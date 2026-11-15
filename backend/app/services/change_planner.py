"""Change Planner for Agent 3.
Diffs original ResumeContent vs FinalContent into an ordered list of concrete slot Operations
(set_text, reorder, clone_slot/block, remove_slot/block) using TemplateProfile SlotMap.
Validates the entire plan before any XML manipulation occurs.
"""

import logging
from enum import Enum
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field

from contracts.models.template_profile import TemplateProfile, Slot
from contracts.models.tailored_content import Change, ChangeType
from app.services.docx_rendering_measurements import measure_lines

logger = logging.getLogger(__name__)


class OperationType(str, Enum):
    set_text = "set_text"
    reorder = "reorder"
    clone_slot = "clone_slot"
    clone_block = "clone_block"
    remove_slot = "remove_slot"
    remove_block = "remove_block"


class Operation(BaseModel):
    op_id: str
    type: OperationType
    slot_id: Optional[str] = None
    target_content_id: Optional[str] = None
    prototype_slot_id: Optional[str] = None
    insert_after_slot_id: Optional[str] = None
    text: Optional[str] = None
    new_order: Optional[List[str]] = None
    formatting: Optional[Dict[str, Any]] = None
    budget_lines: int = 2
    estimated_lines: int = 1


class ChangePlan(BaseModel):
    operations: List[Operation] = Field(default_factory=list)
    is_valid: bool = True
    validation_errors: List[str] = Field(default_factory=list)
    unmappable_items: List[str] = Field(default_factory=list)
    total_operations: int = 0


def build_change_plan(
    original_content: Dict[str, Any],
    final_content: Dict[str, Any],
    template_profile: TemplateProfile,
    accepted_changes: List[Union[Change, Dict[str, Any]]],
) -> ChangePlan:
    """Constructs and validates an ordered execution plan of slot-level operations.
    Validates:
    - Every referenced slot exists in the template.
    - No operation targets a header or footer slot.
    - Slot budgets are checked via measure_lines.
    - Unmappable items are surfaced explicitly.
    """
    operations: List[Operation] = []
    validation_errors: List[str] = []
    unmappable: List[str] = []
    op_counter = 1

    # Build slot lookups
    slots_by_id: Dict[str, Slot] = {s.slot_id: s for s in template_profile.slots}
    content_to_slot: Dict[str, str] = {}
    item_to_bullet_slots: Dict[str, List[str]] = {}

    if template_profile.slot_map:
        for slot_id, s_info in template_profile.slot_map.items():
            if s_info.bullet_id:
                content_to_slot[s_info.bullet_id] = slot_id
                if s_info.item_id:
                    item_to_bullet_slots.setdefault(s_info.item_id, []).append(slot_id)
            if s_info.item_id:
                content_to_slot.setdefault(s_info.item_id, slot_id)
            if s_info.section_id:
                content_to_slot.setdefault(s_info.section_id, slot_id)

    # Helper to find nearest prototype slot
    def find_prototype_bullet_slot(sec_id: Optional[str] = None) -> Optional[Slot]:
        for s in template_profile.slots:
            if s.role.value == "bullet":
                if sec_id and template_profile.slot_map:
                    s_info = template_profile.slot_map.get(s.slot_id)
                    if s_info and s_info.section_id == sec_id:
                        return s
                return s
        return template_profile.slots[0] if template_profile.slots else None

    # Process normalized accepted changes
    norm_changes: List[Dict[str, Any]] = []
    for c in accepted_changes:
        if isinstance(c, Change):
            norm_changes.append(c.model_dump())
        elif isinstance(c, dict):
            norm_changes.append(c)

    # 1. Text updates & Summary rewrites
    for c in norm_changes:
        c_type = c.get("type", "rewrite_bullet")
        if c_type in (
            ChangeType.rewrite_bullet.value,
            "rewrite_bullet",
            ChangeType.rewrite_summary.value,
            "rewrite_summary",
            ChangeType.normalize_term.value,
            "normalize_term",
        ):
            t_id = c.get("target_content_id") or c.get("slot_id") or c.get("target_id")
            after_text = c.get("after") or c.get("tailored_text")

            if not t_id or after_text is None:
                continue

            slot_id = content_to_slot.get(t_id) or t_id
            slot = slots_by_id.get(slot_id)

            if not slot:
                # Check if it maps to any known slot
                unmappable.append(f"Content ID '{t_id}' has no matching slot in template.")
                continue

            # Validate not header/footer
            role_val = getattr(slot.role, "value", str(slot.role))
            is_protected = (
                role_val in ("header", "footer", "page_number")
                or getattr(slot, "section_id", "") in ("header_part", "footer_part", "page_header", "page_footer", "sec_header_part", "sec_hdr")
                or (template_profile.slot_map and template_profile.slot_map.get(slot_id) and template_profile.slot_map[slot_id].section_id in ("header_part", "footer_part", "page_header", "page_footer", "sec_header_part", "sec_hdr"))
            )
            if is_protected:
                validation_errors.append(f"Operation targets protected header slot '{slot_id}'.")
                continue

            after_str = str(after_text)
            est_lines = measure_lines(after_str, slot)
            budget = slot.max_lines

            if est_lines > budget:
                validation_errors.append(
                    f"Slot '{slot_id}' would exceed budget: requires {est_lines} lines (max: {budget})."
                )

            operations.append(
                Operation(
                    op_id=f"op_{op_counter:03d}",
                    type=OperationType.set_text,
                    slot_id=slot_id,
                    target_content_id=t_id,
                    text=after_str,
                    budget_lines=budget,
                    estimated_lines=est_lines,
                )
            )
            op_counter += 1

    # 2. Reorders (Bullets, Items, Skills)
    for c in norm_changes:
        c_type = c.get("type")
        if c_type in (
            ChangeType.reorder_bullets.value,
            "reorder_bullets",
            ChangeType.reorder_items.value,
            "reorder_items",
            ChangeType.reorder_skills.value,
            "reorder_skills",
        ):
            new_order = c.get("after")
            t_id = c.get("target_content_id") or c.get("item_id")
            if isinstance(new_order, list):
                # Map content IDs to slot IDs
                slot_order = [content_to_slot.get(cid, cid) for cid in new_order]
                operations.append(
                    Operation(
                        op_id=f"op_{op_counter:03d}",
                        type=OperationType.reorder,
                        target_content_id=t_id,
                        new_order=slot_order,
                    )
                )
                op_counter += 1

    # 3. Additions (add_item_from_master_profile or extra bullets)
    for c in norm_changes:
        c_type = c.get("type")
        if c_type in (ChangeType.add_item_from_master_profile.value, "add_item_from_master_profile"):
            t_sec_id = c.get("target_content_id") or "sec_projects"
            after_text = str(c.get("after") or "")
            proto = find_prototype_bullet_slot(t_sec_id)

            if proto:
                est_lines = measure_lines(after_text, proto)
                operations.append(
                    Operation(
                        op_id=f"op_{op_counter:03d}",
                        type=OperationType.clone_block,
                        target_content_id=t_sec_id,
                        prototype_slot_id=proto.slot_id,
                        insert_after_slot_id=proto.slot_id,
                        text=after_text,
                        budget_lines=proto.max_lines,
                        estimated_lines=est_lines,
                    )
                )
                op_counter += 1
            else:
                unmappable.append(f"No prototype slot available to clone for addition in '{t_sec_id}'.")

    # 4. Hidden items (remove_block / remove_slot)
    for c in norm_changes:
        c_type = c.get("type")
        if c_type in (ChangeType.hide_item.value, "hide_item"):
            t_item_id = c.get("target_content_id") or c.get("item_id")
            bullet_slots = item_to_bullet_slots.get(t_item_id, [])
            if bullet_slots:
                for b_slot in bullet_slots:
                    operations.append(
                        Operation(
                            op_id=f"op_{op_counter:03d}",
                            type=OperationType.remove_slot,
                            slot_id=b_slot,
                            target_content_id=t_item_id,
                        )
                    )
                    op_counter += 1
            else:
                item_slot = content_to_slot.get(t_item_id)
                if item_slot:
                    operations.append(
                        Operation(
                            op_id=f"op_{op_counter:03d}",
                            type=OperationType.remove_block,
                            slot_id=item_slot,
                            target_content_id=t_item_id,
                        )
                    )
                    op_counter += 1

    is_valid = len(validation_errors) == 0

    return ChangePlan(
        operations=operations,
        is_valid=is_valid,
        validation_errors=validation_errors,
        unmappable_items=unmappable,
        total_operations=len(operations),
    )
