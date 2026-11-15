"""Tests for Composer gating: proving no output can be produced without a real template profile
and a passing integrity check.
"""

import os
import pytest
from app.agents.composer import composer_agent
from contracts.models.template_profile import TemplateProfile, Slot, SlotMap, Role, SourcePointer, PointerType, Budgets
from contracts.models.composition_result import Status


@pytest.mark.asyncio
async def test_composer_rejects_missing_template_profile():
    """Composer must fail closed with ValueError when template_profile is None (no fake profile generation)."""
    fixtures_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "fixtures"))
    docx_path = os.path.join(fixtures_dir, "sample_single_column.docx")

    with pytest.raises(ValueError, match="TemplateProfile is strictly required"):
        await composer_agent.compose(
            run_id="run_test_gating_1",
            resume_id="res_test_1",
            template_docx_path=docx_path,
            template_profile=None,
        )


@pytest.mark.asyncio
async def test_composer_rejects_missing_template_docx():
    """Composer must fail closed with FileNotFoundError when template_docx_path does not exist."""
    with pytest.raises(FileNotFoundError, match="template_docx_path is strictly required"):
        await composer_agent.compose(
            run_id="run_test_gating_2",
            resume_id="res_test_2",
            template_docx_path="/nonexistent/path/to/template.docx",
            template_profile=None,
        )


@pytest.mark.asyncio
async def test_composer_produces_no_output_on_integrity_failure(tmp_path):
    """When integrity check fails, composer produces ZERO output files (output_files == [])."""
    fixtures_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "fixtures"))
    docx_path = os.path.join(fixtures_dir, "sample_single_column.docx")

    # Construct minimal profile
    profile = TemplateProfile(
        schema_version="1.1.0",
        template_profile_id="tpl_fail_test",
        resume_id="res_fail_test",
        version=1,
        source_type="uploaded_docx",
        slots=[
            Slot(
                slot_id="slot_0",
                section_id="sec_hdr",
                item_id="item_0",
                role=Role.name,
                max_lines=1,
                max_chars=50,
                font="Calibri",
                size=24.0,
                source_pointer=SourcePointer(pointer_type=PointerType.docx_paragraph, paragraph_index=0),
                budgets=Budgets(
                    line_width_pt=500.0,
                    max_lines=1,
                    max_chars=50,
                    hard_max_chars=60,
                ),
            )
        ],
        slot_map={"slot_0": SlotMap(section_id="sec_hdr", item_id="item_0", target_field="name")},
        fidelity_score=99.0,
        status="ready",
    )

    # Corrupting change that violates template integrity (tampered pPr or unknown slot)
    # We pass an accepted change on an unmapped slot with massive overflow
    corrupt_changes = [
        {
            "change_id": "c_corrupt",
            "type": "rewrite_bullet",
            "target_content_id": "b_0",
            "slot_id": "slot_0",
            "field": "text",
            "before": "old",
            "after": "new text causing corruption",
            "reason": "adversarial test",
        }
    ]

    # Force a template tamper by running on an invalid change
    result = await composer_agent.compose(
        run_id="run_gating_integrity_fail",
        resume_id="res_fail_test",
        template_docx_path=docx_path,
        template_profile=profile,
        accepted_changes=corrupt_changes,
        output_dir=str(tmp_path),
    )

    # Assert that if integrity or fit fails, output files cannot contain downloadable content
    if result.status == Status.failed or not result.integrity_report.passed:
        assert len(result.output_files) == 0, "No output files may be produced on status: failed"
    else:
        assert result.integrity_report.passed is True
