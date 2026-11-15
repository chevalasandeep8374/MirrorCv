"""Skill Taxonomy Service for MirrorCV.
Maintains curated approved technical skills (300+ entries), aliases, and category taxonomy.
Implements multi-stage normalization (exact -> alias -> fuzzy) and strictly uses approved entries
for scoring, with candidate rows reserved in a review queue.
Per Rule #9: normalize_term operates ONLY on taxonomy-marked aliases, never substituting adjacent skills.
"""

import os
import re
import difflib
import logging
from typing import Dict, List, Optional, Tuple, Set, Any
from pydantic import BaseModel, ConfigDict

from app.config import settings
from app.services.taxonomy_data import APPROVED_TECHNICAL_TAXONOMY

logger = logging.getLogger(__name__)

# Curated Approved Technical Taxonomy (300+ approved entries)
CURATED_APPROVED_TAXONOMY: List[Dict[str, Any]] = list(APPROVED_TECHNICAL_TAXONOMY)

# Adjacent Skill Families for reporting present_not_visible & adjacent matches
ADJACENT_SKILL_RELATIONS: Dict[str, Dict[str, str]] = {
    "AWS": {"GCP": "cloud_infrastructure", "Azure": "cloud_infrastructure"},
    "GCP": {"AWS": "cloud_infrastructure", "Azure": "cloud_infrastructure"},
    "Azure": {"AWS": "cloud_infrastructure", "GCP": "cloud_infrastructure"},
    "React": {"Vue.js": "frontend_framework", "Angular": "frontend_framework"},
    "Vue.js": {"React": "frontend_framework", "Angular": "frontend_framework"},
    "FastAPI": {"Django": "python_backend", "Flask": "python_backend"},
    "Django": {"FastAPI": "python_backend", "Flask": "python_backend"},
    "Flask": {"FastAPI": "python_backend", "Django": "python_backend"},
    "PostgreSQL": {"MySQL": "relational_db"},
    "MySQL": {"PostgreSQL": "relational_db"},
    "Playwright": {"Cypress": "e2e_testing", "Selenium": "e2e_testing"},
}


class NormalizedSkill(BaseModel):
    model_config = ConfigDict(extra="forbid")
    raw_term: str
    canonical_name: str
    category: str
    is_mapped: bool
    is_alias: bool
    status: str = "approved"


class SkillTaxonomyService:
    """Service providing skill lookup, exact alias matching, fuzzy matching, and adjacency checking."""

    def __init__(self):
        self._canonical_lookup: Dict[str, Dict[str, Any]] = {}
        self._alias_lookup: Dict[str, Dict[str, Any]] = {}
        self._candidate_queue: Dict[str, Dict[str, Any]] = {}
        self._load_curated_into_memory()

    def _load_curated_into_memory(self):
        self._canonical_lookup.clear()
        self._alias_lookup.clear()
        for entry in CURATED_APPROVED_TAXONOMY:
            if entry.get("status") != "approved":
                continue  # Scoring & normalization uses approved rows only
            c_name = entry["canonical_name"]
            c_lower = c_name.lower()
            self._canonical_lookup[c_lower] = entry

            for alias in entry.get("aliases", []):
                self._alias_lookup[alias.lower().strip()] = entry

    def get_approved_count(self) -> int:
        """Returns the total number of approved taxonomy rows."""
        return len(self._canonical_lookup)

    def add_candidate_skill(
        self,
        canonical_name: str,
        aliases: Optional[List[str]] = None,
        category: str = "Other",
        role_families: Optional[List[str]] = None,
        source: str = "external_corpus",
    ) -> Dict[str, Any]:
        """Adds a newly discovered skill to the candidate review queue with status: 'candidate'."""
        name_clean = canonical_name.strip()
        c_lower = name_clean.lower()

        # If already approved, return existing
        if c_lower in self._canonical_lookup:
            return self._canonical_lookup[c_lower]

        entry = {
            "canonical_name": name_clean,
            "aliases": aliases or [c_lower],
            "category": category,
            "role_families": role_families or ["general"],
            "status": "candidate",
            "source": source,
        }
        self._candidate_queue[c_lower] = entry
        logger.info(f"Skill '{name_clean}' added to candidate review queue from {source}.")
        return entry

    def approve_candidate_skill(self, canonical_name: str) -> bool:
        """Promotes a candidate skill from the review queue into the approved taxonomy."""
        c_lower = canonical_name.lower().strip()
        if c_lower not in self._candidate_queue:
            return False

        candidate = self._candidate_queue.pop(c_lower)
        candidate["status"] = "approved"
        CURATED_APPROVED_TAXONOMY.append(candidate)
        self._load_curated_into_memory()
        logger.info(f"Candidate skill '{canonical_name}' approved and added to active taxonomy.")
        return True

    def get_review_queue(self) -> List[Dict[str, Any]]:
        """Returns all unapproved candidate skills currently in the review queue."""
        return list(self._candidate_queue.values())

    def normalize_term(self, term: str) -> NormalizedSkill:
        """Normalizes a raw term to canonical name using approved entries only.

        Adheres strictly to Rule #9:
        - normalize_term only transforms taxonomy-marked aliases to their canonical term.
        - Never substitutes adjacent skills (e.g. GCP is NOT transformed to AWS).
        """
        if not term or not term.strip():
            return NormalizedSkill(
                raw_term="",
                canonical_name="",
                category="General",
                is_mapped=False,
                is_alias=False,
                status="unmapped",
            )

        raw = term.strip()
        cleaned = re.sub(r"[^\w\+\#\.\/\-\s]", "", raw.lower()).strip()

        # 1. Exact Canonical Match (case-insensitive)
        if cleaned in self._canonical_lookup:
            entry = self._canonical_lookup[cleaned]
            return NormalizedSkill(
                raw_term=raw,
                canonical_name=entry["canonical_name"],
                category=entry["category"],
                is_mapped=True,
                is_alias=False,
                status=entry["status"],
            )

        # 2. Exact Alias Match (taxonomy-marked aliases)
        if cleaned in self._alias_lookup:
            entry = self._alias_lookup[cleaned]
            return NormalizedSkill(
                raw_term=raw,
                canonical_name=entry["canonical_name"],
                category=entry["category"],
                is_mapped=True,
                is_alias=True,
                status=entry["status"],
            )

        # 3. High-Confidence Fuzzy Match on Aliases and Canonical Names
        all_targets = list(self._canonical_lookup.keys()) + list(self._alias_lookup.keys())
        matches = difflib.get_close_matches(cleaned, all_targets, n=1, cutoff=0.88)
        if matches and len(cleaned) >= 4:
            matched_key = matches[0]
            entry = self._canonical_lookup.get(matched_key) or self._alias_lookup.get(matched_key)
            if entry and entry.get("status") == "approved":
                return NormalizedSkill(
                    raw_term=raw,
                    canonical_name=entry["canonical_name"],
                    category=entry["category"],
                    is_mapped=True,
                    is_alias=True,
                    status=entry["status"],
                )

        # 4. Unmapped term: keep raw name flagged as candidate
        return NormalizedSkill(
            raw_term=raw,
            canonical_name=raw.title() if not raw.isupper() else raw,
            category="Other",
            is_mapped=False,
            is_alias=False,
            status="candidate",
        )

    def get_adjacent_skills(self, canonical_name: str) -> List[Tuple[str, str]]:
        """Returns list of (adjacent_skill, relation) for a canonical skill.

        Rule #9: These are kept distinct and reported in adjacent_skills, NEVER substituted.
        """
        if canonical_name in ADJACENT_SKILL_RELATIONS:
            return list(ADJACENT_SKILL_RELATIONS[canonical_name].items())
        return []


# Global singleton
skill_taxonomy_service = SkillTaxonomyService()
