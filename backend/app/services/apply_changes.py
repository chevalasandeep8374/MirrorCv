"""Pure, side-effect free, deterministic function for applying accepted tailored changes
onto ResumeContent to produce FinalContent.
Never mutates original content; strictly preserves IDs and valid permutations.
"""

import copy
import logging
from typing import Dict, Any, List, Union
from contracts.models.tailored_content import Change, ChangeType

logger = logging.getLogger(__name__)


def apply_changes(
    original_content: Dict[str, Any],
    accepted_changes: List[Union[Change, Dict[str, Any]]],
) -> Dict[str, Any]:
    """Applies accepted tailored changes to a copy of original_content in strict phases:
    1. add_item_from_master_profile (inserts confirmed project/experience items)
    2. text rewrites (rewrite_bullet, rewrite_summary, normalize_term)
    3. visibility toggles (hide_item, show_item)
    4. reordering (reorder_bullets, reorder_items, reorder_skills)

    Returns a new, fully populated FinalContent dictionary.
    """
    final_content = copy.deepcopy(original_content)
    if not accepted_changes:
        return final_content

    # Normalize change objects to dictionaries if necessary
    norm_changes: List[Dict[str, Any]] = []
    for c in accepted_changes:
        if isinstance(c, Change):
            norm_changes.append(c.model_dump())
        elif isinstance(c, dict):
            norm_changes.append(c)

    # ----------------------------------------------------
    # Phase 1: Add Items from Master Profile
    # ----------------------------------------------------
    for c in norm_changes:
        c_type = c.get("type")
        if c_type in (ChangeType.add_item_from_master_profile.value, "add_item_from_master_profile"):
            target_sec_id = c.get("target_content_id") or "sec_projects"
            after_val = c.get("after")
            evidence_ids = c.get("evidence_ids", [])
            new_item_id = evidence_ids[0] if evidence_ids else f"item_added_{len(final_content.get('sections', []))}"

            # Create item dict if after_val is string or dict
            if isinstance(after_val, str):
                new_item = {
                    "id": new_item_id,
                    "title": after_val.split(".")[0][:40],
                    "subtitle": "Master Profile Project",
                    "description": after_val,
                    "bullets": [{"id": f"{new_item_id}_b1", "text": after_val}],
                }
            elif isinstance(after_val, dict):
                new_item = dict(after_val)
                new_item.setdefault("id", new_item_id)
            else:
                continue

            # Insert into target section
            sec_found = False
            for sec in final_content.get("sections", []):
                if sec.get("id") == target_sec_id or sec.get("type") in ("projects", "experience"):
                    sec.setdefault("items", []).insert(0, new_item)
                    sec_found = True
                    break

            if not sec_found and final_content.get("sections"):
                final_content["sections"][0].setdefault("items", []).insert(0, new_item)

    # ----------------------------------------------------
    # Phase 2: Text Rewrites & Term Normalizations
    # ----------------------------------------------------
    for c in norm_changes:
        c_type = c.get("type")
        if c_type in (
            ChangeType.rewrite_bullet.value,
            "rewrite_bullet",
            ChangeType.rewrite_summary.value,
            "rewrite_summary",
            ChangeType.normalize_term.value,
            "normalize_term",
        ):
            target_id = c.get("target_content_id") or c.get("slot_id") or c.get("target_id")
            after_text = c.get("after") or c.get("tailored_text")
            field = c.get("field", "text")

            if not target_id or after_text is None:
                continue

            after_str = str(after_text)

            # Check if summary change
            if c_type in (ChangeType.rewrite_summary.value, "rewrite_summary") or field == "summary":
                # Find summary/profile section
                summary_updated = False
                for sec in final_content.get("sections", []):
                    if sec.get("type") in ("summary", "profile", "about") or sec.get("id") == target_id:
                        for itm in sec.get("items", []):
                            if "description" in itm:
                                itm["description"] = after_str
                            else:
                                itm["text"] = after_str
                            summary_updated = True
                            break
                        if summary_updated:
                            break
                if not summary_updated:
                    # Update or add summary in header or section
                    for sec in final_content.get("sections", []):
                        if sec.get("id") == target_id:
                            sec["summary"] = after_str
                            summary_updated = True
                            break

            # Bullet changes
            for sec in final_content.get("sections", []):
                for item in sec.get("items", []):
                    bullets = item.get("bullets", [])
                    for b in bullets:
                        if isinstance(b, dict) and (b.get("id") == target_id or target_id in (b.get("id"),)):
                            b["text"] = after_str
                            break

    # ----------------------------------------------------
    # Phase 3: Item Visibility (Hide / Show)
    # ----------------------------------------------------
    for c in norm_changes:
        c_type = c.get("type")
        target_id = c.get("target_content_id") or c.get("item_id")
        if not target_id:
            continue

        if c_type in (ChangeType.hide_item.value, "hide_item"):
            for sec in final_content.get("sections", []):
                for item in sec.get("items", []):
                    if item.get("id") == target_id:
                        item["hidden"] = True

        elif c_type in (ChangeType.show_item.value, "show_item"):
            for sec in final_content.get("sections", []):
                for item in sec.get("items", []):
                    if item.get("id") == target_id:
                        item["hidden"] = False

    # ----------------------------------------------------
    # Phase 4: Reordering (Bullets, Items, Skills)
    # ----------------------------------------------------
    for c in norm_changes:
        c_type = c.get("type")
        new_order = c.get("after")

        if not isinstance(new_order, list):
            continue

        # Reorder bullets inside an item
        if c_type in (ChangeType.reorder_bullets.value, "reorder_bullets"):
            target_item_id = c.get("target_content_id") or c.get("item_id")
            for sec in final_content.get("sections", []):
                for item in sec.get("items", []):
                    if not target_item_id or item.get("id") == target_item_id:
                        bullets = item.get("bullets", [])
                        if bullets and all(isinstance(b, dict) for b in bullets):
                            b_lookup = {b.get("id"): b for b in bullets if b.get("id")}
                            # Check if new_order contains these bullets
                            matching_ids = [bid for bid in new_order if bid in b_lookup]
                            if len(matching_ids) == len(bullets):
                                item["bullets"] = [b_lookup[bid] for bid in matching_ids]

        # Reorder items inside a section
        elif c_type in (ChangeType.reorder_items.value, "reorder_items", ChangeType.reorder_skills.value, "reorder_skills"):
            target_sec_id = c.get("target_content_id")
            for sec in final_content.get("sections", []):
                if not target_sec_id or sec.get("id") == target_sec_id:
                    items = sec.get("items", [])
                    if items:
                        item_lookup = {itm.get("id"): itm for itm in items if itm.get("id")}
                        matching_item_ids = [iid for iid in new_order if iid in item_lookup]
                        if len(matching_item_ids) == len(items):
                            sec["items"] = [item_lookup[iid] for iid in matching_item_ids]

    return final_content
