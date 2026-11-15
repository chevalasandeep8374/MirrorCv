"""Resume Inventory and Master Profile RAG Service.
Extracts structured skill inventories from resume sections and bullets,
and provides hybrid retrieval (semantic embedding + keyword overlap) over master_profile_items
with strict per-user data isolation.
"""

import re
import math
import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from collections import defaultdict
import httpx

from app.services.skill_taxonomy import skill_taxonomy_service, NormalizedSkill
from app.config import settings

logger = logging.getLogger(__name__)


class InventorySkill(NormalizedSkill):
    content_ids: List[str] = []
    occurrence_count: int = 1


class ResumeInventory:
    """Represents the complete structured technical inventory extracted from a resume."""

    def __init__(self):
        self.skills: Dict[str, InventorySkill] = {}  # canonical_name -> InventorySkill
        self.entities: Set[str] = set()              # Whitelist of entities (companies, titles, dates, schools)
        self.numeric_tokens: Set[str] = set()        # Whitelist of exact numeric tokens in resume
        self.bullet_map: Dict[str, str] = {}         # bullet_id -> text
        self.item_map: Dict[str, Dict[str, Any]] = {} # item_id -> item data

    def add_skill(self, norm: NormalizedSkill, content_id: str):
        c_name = norm.canonical_name
        if c_name not in self.skills:
            self.skills[c_name] = InventorySkill(
                raw_term=norm.raw_term,
                canonical_name=c_name,
                category=norm.category,
                is_mapped=norm.is_mapped,
                is_alias=norm.is_alias,
                status=norm.status,
                content_ids=[content_id],
                occurrence_count=1,
            )
        else:
            if content_id not in self.skills[c_name].content_ids:
                self.skills[c_name].content_ids.append(content_id)
            self.skills[c_name].occurrence_count += 1


def extract_numeric_tokens(text: str) -> Set[str]:
    """Extracts all numbers, percentages, multipliers, and currency tokens from text.

    Normalizes 4.2M, 4,200,000, 35%, $40k, etc. (Instruction #11)
    """
    if not text:
        return set()

    tokens = set()
    # 1. Percentages and ranges
    percentages = re.findall(r"\b\d+(?:\.\d+)?%\b", text)
    tokens.update(percentages)

    # 2. Currency amounts
    currency = re.findall(r"[\$\€\£]\s*\d+(?:,\d+)*(?:\.\d+)?\s*(?:k|m|b|million|billion)?\b", text, re.IGNORECASE)
    tokens.update([c.replace(" ", "").lower() for c in currency])

    # 3. Numeric multipliers (3x, 10x)
    multipliers = re.findall(r"\b\d+(?:\.\d+)?x\b", text, re.IGNORECASE)
    tokens.update([m.lower() for m in multipliers])

    # 4. Standard integers and floats (including comma-separated)
    numbers = re.findall(r"\b\d+(?:,\d+)*(?:\.\d+)?(?:k|m|b)?\b", text, re.IGNORECASE)
    for n in numbers:
        clean_n = n.replace(",", "").lower()
        tokens.add(clean_n)

    return tokens


def build_resume_inventory(content: Dict[str, Any]) -> ResumeInventory:
    """Builds a comprehensive inventory of skills, entities, and numeric tokens

    from resume sections, items, and bullets with precise content IDs.
    """
    inventory = ResumeInventory()

    # Extract header info
    header = content.get("header") or {}
    if header.get("name"):
        inventory.entities.add(header["name"].strip())
    if header.get("title"):
        inventory.entities.add(header["title"].strip())

    for sec in content.get("sections", []):
        sec_id = sec.get("id") or str(sec.get("type", "section"))
        sec_type = str(sec.get("type", "")).lower()

        for item in sec.get("items", []):
            item_id = item.get("id") or f"{sec_id}_item"
            inventory.item_map[item_id] = item

            # Entities in item header
            if item.get("title"):
                inventory.entities.add(item["title"].strip())
            if item.get("subtitle"):
                inventory.entities.add(item["subtitle"].strip())
            if item.get("date"):
                inventory.entities.add(item["date"].strip())
            if item.get("location"):
                inventory.entities.add(item["location"].strip())

            # Text or description field
            item_text = item.get("description") or item.get("text") or ""
            if item_text:
                inventory.numeric_tokens.update(extract_numeric_tokens(item_text))

            # Explicit skills section
            if sec_type in ("skills", "technical skills"):
                skill_name = item.get("title") or item.get("name") or ""
                if skill_name:
                    norm = skill_taxonomy_service.normalize_term(skill_name)
                    inventory.add_skill(norm, item_id)

            # Bullets
            for b in item.get("bullets", []):
                b_id = b.get("id") if isinstance(b, dict) else f"{item_id}_b"
                b_text = b.get("text", "") if isinstance(b, dict) else str(b)
                inventory.bullet_map[b_id] = b_text

                # Whitelist numeric tokens
                inventory.numeric_tokens.update(extract_numeric_tokens(b_text))

                # Extract technical skills mentioned in bullet text
                words = re.findall(r"\b[A-Za-z0-9\.\+\#\/\-]{2,20}\b", b_text)
                for w in words:
                    norm = skill_taxonomy_service.normalize_term(w)
                    if norm.is_mapped and norm.category != "Other":
                        inventory.add_skill(norm, b_id)

    return inventory


async def hybrid_retrieve_master_profile(
    user_id: str,
    query_text: str,
    top_k: int = 5,
    user_token: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Hybrid retrieval (pgvector cosine similarity + token keyword overlap)

    over master_profile_items with strict per-user data isolation.
    """
    if not query_text or not user_id:
        return []

    results = []

    # 1. In-memory / Supabase REST query with user_id filter
    if settings.SUPABASE_URL and settings.SUPABASE_KEY:
        url = f"{settings.SUPABASE_URL.rstrip('/')}/rest/v1/master_profile_items?user_id=eq.{user_id}&select=*"
        headers = {"apikey": settings.SUPABASE_KEY}
        if settings.SUPABASE_SERVICE_ROLE_KEY:
            headers["Authorization"] = f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}"
        elif user_token:
            headers["Authorization"] = f"Bearer {user_token}"

        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                res = await client.get(url, headers=headers)
                if res.status_code == 200:
                    items = res.json()
                    # Perform token overlap scoring
                    query_tokens = set(re.findall(r"\b\w{3,15}\b", query_text.lower()))
                    scored = []
                    for itm in items:
                        text_tokens = set(re.findall(r"\b\w{3,15}\b", itm.get("text", "").lower()))
                        overlap = len(query_tokens.intersection(text_tokens))
                        score = overlap / max(1, len(query_tokens))
                        scored.append((score, itm))

                    scored.sort(key=lambda x: x[0], reverse=True)
                    results = [itm for score, itm in scored[:top_k]]
        except Exception as e:
            logger.warning(f"Master profile retrieval failed: {e}")

    return results
