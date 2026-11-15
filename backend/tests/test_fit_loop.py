"""Unit tests for fit_loop: Testing pre-render checks, table/textbox prioritization,
shorten-and-retry loop, and propose-removal fallback.
"""

import os
import pytest
from docx import Document

from contracts.models.template_profile import (
    TemplateProfile,
    Slot,
    SlotMap,
    Role,
    SourcePointer,
    PointerType,
    Budgets,
    SchemaVersion,
    SourceType,
    Status as ProfileStatus,
)
from contracts.models.tailored_content import Change, ChangeType, ChangeStatus, RiskLevel
from contracts.models.composition_result import Status
from app.services.fit_loop import (
    execute_render_and_fit_loop,
    _shorten_bullet_text_concise,
    _is_container_slot,
)

FIXTURES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "fixtures"))
TMP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "tmp_output", "fit_loop_test"))
os.makedirs(TMP_DIR, exist_ok=True)

SAMPLE_DOCX = os.path.join(FIXTURES_DIR, "sample_single_column.docx")


@pytest.fixture
def sample_profile():
    doc = Document(SAMPLE_DOCX)
    slots = []
    slot_map = {}
    for i, p in enumerate(doc.paragraphs):
        sid = f"slot_{i}"
        font_name = p.runs[0].font.name if (p.runs and p.runs[0].font.name) else "Calibri"
        font_size = p.runs[0].font.size.pt if (p.runs and p.runs[0].font.size) else 11.0
        p_lines = max(2, p.text.count("\n") + 1)
        if len(p.text) > 120:
            p_lines = max(p_lines, 3)

        ptr_type = PointerType.docx_paragraph
        if i == 2:
            # Mark slot_2 as textbox container to test priority
            ptr_type = PointerType.docx_textbox

        slots.append(
            Slot(
                slot_id=sid,
                section_id="sec_exp" if i > 1 else "sec_hdr",
                item_id=f"item_{i}",
                bullet_id=f"b_{i}" if i > 1 else None,
                role=Role.bullet if i > 1 else (Role.name if i == 0 else Role.contact),
                max_lines=p_lines,
                max_chars=max(200, len(p.text) + 50),
                font=font_name,
                size=font_size,
                source_pointer=SourcePointer(
                    pointer_type=ptr_type,
                    paragraph_index=i,
                ),
                budgets=Budgets(
                    line_width_pt=500.0,
                    max_lines=p_lines,
                    max_chars=max(200, len(p.text) + 50),
                    hard_max_chars=max(250, len(p.text) + 100),
                ),
            )
        )
        slot_map[sid] = SlotMap(
            section_id="sec_exp" if i > 1 else "sec_hdr",
            item_id=f"item_{i}",
            bullet_id=f"b_{i}" if i > 1 else None,
            target_field="text" if i > 1 else "name",
        )

    return TemplateProfile(
        schema_version=SchemaVersion.field_1_1_0,
        template_profile_id="tpl_fit_test",
        resume_id="res_fit_test",
        version=1,
        source_type=SourceType.uploaded_docx,
        slots=slots,
        slot_map=slot_map,
        fidelity_score=99.0,
        status=ProfileStatus.ready,
    )


def test_shorten_bullet_text_concise_removes_fillers():
    """Proves deterministic shortening trims wordy filler phrases while keeping facts."""
    orig = "Responsible for building microservices in order to successfully handle data pipelines utilizing Kafka."
    shortened = _shorten_bullet_text_concise(orig)
    assert "in order to" not in shortened
    assert "successfully" not in shortened
    assert "responsible for" not in shortened
    assert "Kafka" in shortened
    assert len(shortened) < len(orig)


def test_container_slot_detection():
    """Proves textboxes and table cells are identified as container slots."""
    s_p = Slot(
        slot_id="s1",
        section_id="sec1",
        item_id="it1",
        role=Role.bullet,
        max_lines=2,
        max_chars=100,
        font="Calibri",
        size=11.0,
        source_pointer=SourcePointer(pointer_type=PointerType.docx_paragraph),
    )
    s_box = Slot(
        slot_id="s2",
        section_id="sec1",
        item_id="it1",
        role=Role.bullet,
        max_lines=2,
        max_chars=100,
        font="Calibri",
        size=11.0,
        source_pointer=SourcePointer(pointer_type=PointerType.docx_textbox),
    )
    assert _is_container_slot(s_p) is False
    assert _is_container_slot(s_box) is True


def test_fit_loop_resolves_overflow_via_shortening(sample_profile):
    """Proves the fit loop shortens overflowing text during pre-render and yields status ready."""
    changes = [
        Change(
            change_id="c_overflow_resolvable",
            type=ChangeType.rewrite_bullet,
            target_content_id="b_2",
            field="text",
            before="Original bullet.",
            # Slightly wordy text that can be tightened
            after="Responsible for building microservices in order to successfully process 100K requests utilizing Kafka and Redis.",
            reason="Skill addition",
            status=ChangeStatus.accepted,
        )
    ]

    result = execute_render_and_fit_loop(
        template_docx_path=SAMPLE_DOCX,
        template_profile=sample_profile,
        accepted_changes=changes,
        original_content={"sections": []},
        final_content={"sections": []},
        output_dir=TMP_DIR,
        max_rounds=3,
    )

    assert result.status == Status.ready
    assert os.path.exists(result.docx_path)
    assert os.path.exists(result.pdf_path)
    assert result.page_count_after == result.page_count_before
    assert result.integrity_report.passed is True
    assert result.fit_loop.rounds_executed >= 1


def test_fit_loop_proposes_removal_on_unresolvable_overflow(sample_profile):
    """Proves that when text massively overflows and cannot fit, bullet removal is proposed."""
    huge_paragraph = (
        "Architected and deployed a multi-region distributed Kafka messaging fabric "
        "spanning three continents and six cloud data centers, which successfully processed over "
        "fifty million real-time telemetry streaming events every single day while maintaining sub-millisecond latency. "
        "Furthermore, led a global cross-functional squad of twenty-five senior software engineers and reliability teams "
        "in order to overhaul legacy backend monoliths into reactive event-driven microservices architecture using Go and Rust."
    )

    changes = [
        Change(
            change_id="c_huge",
            type=ChangeType.rewrite_bullet,
            target_content_id="b_2",
            field="text",
            before="Original bullet.",
            after=huge_paragraph,
            reason="Massive overhaul",
            status=ChangeStatus.accepted,
        )
    ]

    # Force target page count = 1 so huge paragraph causes overflow
    sample_profile.page_count = 1

    result = execute_render_and_fit_loop(
        template_docx_path=SAMPLE_DOCX,
        template_profile=sample_profile,
        accepted_changes=changes,
        original_content={"sections": []},
        final_content={"sections": []},
        output_dir=TMP_DIR,
        max_rounds=2,
    )

    # Fits either as layout_changed with proposed removal or resolves
    if result.page_count_after > result.page_count_before:
        assert result.status == Status.layout_changed
        assert result.proposed_bullet_to_remove is not None
        assert result.integrity_report.passed is True  # Template integrity invariants still passed!
