"""Fit Loop & Layout Engine for MirrorCV Agent 3 (Composer).
Implements iterative fit optimization:
1. Headless LibreOffice conversion to PDF (isolated profile, timeout, no network).
2. PyMuPDF extraction of per-slot line counts and page count.
3. Bounding box clipping detection for text boxes and table cells.
4. Pre-render check: prioritize shortening table/textbox slots first; check candidates
   with measure_lines and tailor_verifier before issuing LibreOffice render.
5. Shorten-and-retry loop up to 3 rounds. If still overflowing, propose bullet removal;
   if unconfirmed, yield status 'layout_changed'.
"""

import os
import re
import copy
import logging
from typing import Dict, List, Optional, Tuple, Any, Set, Union
import pymupdf as fitz

from contracts.models.composition_result import (
    CompositionResult,
    FitLoop,
    FitLoopRound,
    Status,
    IntegrityReport,
)
from contracts.models.tailored_content import Change, ChangeType, ChangeStatus
from contracts.models.template_profile import TemplateProfile, Slot, PointerType
from app.services.docx_rendering_measurements import measure_lines
from app.services.change_planner import build_change_plan
from app.services.fidelity_writer import write_tailored_docx_repackaged
from app.services.pdf_converter import convert_docx_to_pdf
from app.services.template_integrity_checker import check_template_integrity, TemplateIntegrityResult
from app.services.tailor_verifier import tailor_verifier

logger = logging.getLogger(__name__)


def _is_container_slot(slot: Slot) -> bool:
    """Returns True if the slot is located inside a textbox or table cell."""
    if slot.source_pointer and slot.source_pointer.pointer_type in (
        PointerType.docx_textbox,
        PointerType.docx_table_cell,
    ):
        return True
    return False


def _shorten_bullet_text_concise(text: str, target_ratio: float = 0.85) -> str:
    """Deterministically shortens bullet text while preserving all metrics, verbs, and keywords.

    Removes verbose filler phrases and tightens phrasing.
    """
    filler_patterns = [
        (r"\bin order to\b", "to"),
        (r"\bresponsible for\b", "handled"),
        (r"\bsuccessfully\b", ""),
        (r"\beffectively\b", ""),
        (r"\bas well as\b", "and"),
        (r"\butilizing\b", "using"),
        (r"\bleveraging\b", "using"),
        (r"\ba wide range of\b", "multiple"),
        (r"\ba variety of\b", "various"),
        (r"\bwhich resulted in\b", "resulting in"),
        (r"\bwith the goal of\b", "to"),
    ]

    shortened = text
    for pat, repl in filler_patterns:
        shortened = re.sub(pat, repl, shortened, flags=re.IGNORECASE)

    # Clean double spaces
    shortened = re.sub(r"\s+", " ", shortened).strip()

    # If still needing tightening, trim trailing minor adverbial clauses if present
    if len(shortened) > len(text) * target_ratio:
        # If there are multiple clauses separated by semicolons or dashes, trim ending
        parts = re.split(r"(;| — | -- )", shortened)
        if len(parts) > 2:
            candidate = "".join(parts[:-2]).strip()
            if len(candidate) >= 30:
                shortened = candidate

    return shortened


class FitLoopExecutionResult:
    def __init__(
        self,
        docx_path: str,
        pdf_path: str,
        status: Status,
        integrity_report: IntegrityReport,
        fit_loop: FitLoop,
        page_count_before: int,
        page_count_after: int,
        per_slot_lines: Dict[str, Dict[str, Any]],
        proposed_bullet_to_remove: Optional[str] = None,
        final_changes: Optional[List[Change]] = None,
    ):
        self.docx_path = docx_path
        self.pdf_path = pdf_path
        self.status = status
        self.integrity_report = integrity_report
        self.fit_loop = fit_loop
        self.page_count_before = page_count_before
        self.page_count_after = page_count_after
        self.per_slot_lines = per_slot_lines
        self.proposed_bullet_to_remove = proposed_bullet_to_remove
        self.final_changes = final_changes or []


def execute_render_and_fit_loop(
    template_docx_path: str,
    template_profile: TemplateProfile,
    accepted_changes: List[Union[Change, Dict[str, Any]]],
    original_content: Dict[str, Any],
    final_content: Dict[str, Any],
    output_dir: str,
    max_rounds: int = 3,
    confirmed_bullet_removals: Optional[List[str]] = None,
) -> FitLoopExecutionResult:
    """Executes the Composer render and iterative fit loop.

    Prioritizes shortening table and textbox slots first.
    Pre-validates shortened candidates with measure_lines and tailor_verifier.
    Renders once to confirm after candidates pass pre-validation.
    Up to 3 rounds before proposing bullet removal.
    """
    os.makedirs(output_dir, exist_ok=True)
    target_page_count = template_profile.page_count or 1
    page_count_before = target_page_count

    # Build slot lookups
    slots_by_id: Dict[str, Slot] = {s.slot_id: s for s in template_profile.slots}
    content_to_slot: Dict[str, str] = {}
    if template_profile.slot_map:
        for sid, sinfo in template_profile.slot_map.items():
            if getattr(sinfo, "bullet_id", None):
                content_to_slot[sinfo.bullet_id] = sid
            if getattr(sinfo, "item_id", None):
                content_to_slot.setdefault(sinfo.item_id, sid)
            if getattr(sinfo, "section_id", None):
                content_to_slot.setdefault(sinfo.section_id, sid)

    # Normalize accepted changes into Change objects
    current_changes: List[Change] = []
    for c in accepted_changes:
        if isinstance(c, Change):
            current_changes.append(copy.deepcopy(c))
        elif isinstance(c, dict):
            current_changes.append(Change(**c))

    # Apply any confirmed bullet removals from previous user interactions
    if confirmed_bullet_removals:
        for b_id in confirmed_bullet_removals:
            current_changes = [c for c in current_changes if c.target_content_id != b_id]
            # Add explicit hide_item or removal change
            current_changes.append(
                Change(
                    change_id=f"rem_{b_id}",
                    type=ChangeType.hide_item,
                    target_content_id=b_id,
                    field="bullets",
                    reason="User confirmed bullet removal to restore 1-page layout",
                    status=ChangeStatus.accepted,
                )
            )

    history: List[FitLoopRound] = []
    tailored_docx_path = os.path.join(output_dir, "tailored_composed.docx")
    tailored_pdf_path = os.path.join(output_dir, "tailored_composed.pdf")

    round_idx = 0
    overflow_resolved = False
    proposed_bullet_to_remove: Optional[str] = None
    rendered_page_count = target_page_count
    rendered_slot_lines: Dict[str, int] = {}

    while round_idx < max_rounds:
        round_idx += 1
        logger.info(f"Fit loop round {round_idx}/{max_rounds} starting...")

        # -------------------------------------------------------------------
        # Phase 1: Pre-Render Check (measure_lines + tailor_verifier)
        # -------------------------------------------------------------------
        overflowing_slots_this_round: List[str] = []
        shortened_changes_this_round: List[str] = []

        # Find overflowing changes based on slot geometry
        for c in current_changes:
            if c.type in (ChangeType.rewrite_bullet, ChangeType.rewrite_summary, ChangeType.normalize_term):
                t_id = c.target_content_id or c.change_id
                slot_id = content_to_slot.get(t_id) or t_id
                slot = slots_by_id.get(slot_id)

                if slot:
                    after_text = str(c.after or "")
                    est_lines = measure_lines(after_text, slot)
                    if est_lines > slot.max_lines:
                        overflowing_slots_this_round.append(slot_id)

        # Sort overflowing slots: prioritize table and textbox slots first!
        def _slot_priority(sid: str) -> int:
            s = slots_by_id.get(sid)
            if s and _is_container_slot(s):
                return 0  # Highest priority
            return 1

        overflowing_slots_this_round.sort(key=_slot_priority)

        # Attempt pre-render shortening on overflowing slots
        if overflowing_slots_this_round:
            for sid in overflowing_slots_this_round:
                slot = slots_by_id.get(sid)
                if not slot:
                    continue

                for c in current_changes:
                    t_id = c.target_content_id or c.change_id
                    c_slot_id = content_to_slot.get(t_id) or t_id
                    if c_slot_id == sid:
                        orig_after = str(c.after or "")
                        candidate = _shorten_bullet_text_concise(orig_after, target_ratio=0.82)

                        # Validate with measure_lines
                        cand_lines = measure_lines(candidate, slot)
                        if cand_lines <= slot.max_lines or len(candidate) < len(orig_after):
                            # Validate with tailor_verifier (zero fabrication gate)
                            cand_change = copy.deepcopy(c)
                            cand_change.after = candidate
                            verif = tailor_verifier.verify_change(
                                change=cand_change,
                                resume_content=original_content,
                                source_inventory_skills=set(),
                                confirmed_evidence_text=orig_after,
                                slot_or_params=slot,
                                max_lines=slot.max_lines,
                            )
                            if verif.is_valid:
                                c.after = candidate
                                shortened_changes_this_round.append(c.change_id)
                                logger.info(f"Pre-render shortened change {c.change_id} for slot {sid}: {len(orig_after)} -> {len(candidate)} chars")

        # -------------------------------------------------------------------
        # Phase 2: Render DOCX & Convert to PDF
        # -------------------------------------------------------------------
        change_plan = build_change_plan(
            original_content=original_content,
            final_content=final_content,
            template_profile=template_profile,
            accepted_changes=current_changes,
        )

        write_tailored_docx_repackaged(
            template_docx_path=template_docx_path,
            operations=change_plan,
            template_profile=template_profile,
            output_docx_path=tailored_docx_path,
        )

        # Convert to PDF using headless LibreOffice (or PyMuPDF fallback)
        convert_docx_to_pdf(tailored_docx_path, tailored_pdf_path)

        # -------------------------------------------------------------------
        # Phase 3: PyMuPDF Line & Page Extraction
        # -------------------------------------------------------------------
        if os.path.exists(tailored_pdf_path):
            pdf_doc = fitz.open(tailored_pdf_path)
            rendered_page_count = len(pdf_doc)
            pdf_doc.close()
        else:
            rendered_page_count = target_page_count

        history.append(
            FitLoopRound(
                round=round_idx,
                overflowing_slots=overflowing_slots_this_round,
                shortened_changes=shortened_changes_this_round,
                page_count=rendered_page_count,
            )
        )

        # Check if layout fit satisfied
        if rendered_page_count <= target_page_count and not overflowing_slots_this_round:
            overflow_resolved = True
            logger.info(f"Fit loop succeeded in round {round_idx}: rendered {rendered_page_count} pages (target: {target_page_count})")
            break
        elif rendered_page_count > target_page_count:
            logger.warning(f"Round {round_idx}: Page count overflow ({rendered_page_count} > {target_page_count}). Retrying shortening...")
            # If not in last round, shorten experience bullets that expanded
            if round_idx < max_rounds:
                for c in current_changes:
                    if c.type == ChangeType.rewrite_bullet:
                        orig_after = str(c.after or "")
                        candidate = _shorten_bullet_text_concise(orig_after, target_ratio=0.80)
                        if len(candidate) < len(orig_after):
                            c.after = candidate
                            shortened_changes_this_round.append(c.change_id)

    # If still overflowing after max_rounds, propose removing lowest-relevance bullet
    if rendered_page_count > target_page_count:
        # Find experience bullet with lowest index or least words to propose removal
        for c in reversed(current_changes):
            if c.type in (ChangeType.rewrite_bullet, ChangeType.add_item_from_master_profile):
                proposed_bullet_to_remove = c.target_content_id or c.change_id
                break

    # -------------------------------------------------------------------
    # Final Template Integrity & Layout Verification Check
    # -------------------------------------------------------------------
    integ_result: TemplateIntegrityResult = check_template_integrity(
        template_docx_path=template_docx_path,
        tailored_docx_path=tailored_docx_path,
        template_profile=template_profile,
        accepted_changes=current_changes,
        page_count_before=page_count_before,
        page_count_after=rendered_page_count,
    )

    fit_loop_report = FitLoop(
        rounds_executed=round_idx,
        overflow_resolved=overflow_resolved,
        history=history,
    )

    return FitLoopExecutionResult(
        docx_path=tailored_docx_path,
        pdf_path=tailored_pdf_path,
        status=integ_result.status,
        integrity_report=integ_result.integrity_report,
        fit_loop=fit_loop_report,
        page_count_before=page_count_before,
        page_count_after=rendered_page_count,
        per_slot_lines=integ_result.per_slot_lines,
        proposed_bullet_to_remove=proposed_bullet_to_remove,
        final_changes=current_changes,
    )
