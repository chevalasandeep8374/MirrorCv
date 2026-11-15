"""Unit tests for change_planner: Validating conversion of content diffs
into slot-level Operations with pre-execution budget and constraint validation.
"""

import pytest
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
    Status,
)
from contracts.models.tailored_content import Change, ChangeType, ChangeStatus, RiskLevel
from app.services.change_planner import build_change_plan, OperationType


@pytest.fixture
def sample_template_profile():
    slots = [
        Slot(
            slot_id="slot_name",
            section_id="sec_header",
            item_id="header",
            role=Role.name,
            max_lines=1,
            max_chars=40,
            font="Calibri",
            size=18.0,
            source_pointer=SourcePointer(
                pointer_type=PointerType.docx_paragraph,
                paragraph_index=0,
            ),
            budgets=Budgets(
                line_width_pt=500.0,
                max_lines=1,
                max_chars=40,
                hard_max_chars=50,
            ),
        ),
        Slot(
            slot_id="slot_b1",
            section_id="sec_exp",
            item_id="exp_1",
            bullet_id="b1",
            role=Role.bullet,
            max_lines=2,
            max_chars=160,
            font="Calibri",
            size=11.0,
            source_pointer=SourcePointer(
                pointer_type=PointerType.docx_paragraph,
                paragraph_index=1,
            ),
            budgets=Budgets(
                line_width_pt=480.0,
                max_lines=2,
                max_chars=160,
                hard_max_chars=200,
            ),
        ),
        Slot(
            slot_id="slot_b2",
            section_id="sec_exp",
            item_id="exp_1",
            bullet_id="b2",
            role=Role.bullet,
            max_lines=2,
            max_chars=160,
            font="Calibri",
            size=11.0,
            source_pointer=SourcePointer(
                pointer_type=PointerType.docx_paragraph,
                paragraph_index=2,
            ),
            budgets=Budgets(
                line_width_pt=480.0,
                max_lines=2,
                max_chars=160,
                hard_max_chars=200,
            ),
        ),
        Slot(
            slot_id="slot_header",
            section_id="sec_hdr",
            item_id="hdr_item",
            role=Role.other,
            max_lines=1,
            max_chars=50,
            font="Calibri",
            size=9.0,
            source_pointer=SourcePointer(
                pointer_type=PointerType.docx_paragraph,
                paragraph_index=99,
            ),
            budgets=Budgets(
                line_width_pt=480.0,
                max_lines=1,
                max_chars=50,
                hard_max_chars=60,
            ),
        ),
    ]

    slot_map = {
        "slot_name": SlotMap(section_id="sec_header", item_id="header", target_field="name"),
        "slot_b1": SlotMap(section_id="sec_exp", item_id="exp_1", bullet_id="b1", target_field="text"),
        "slot_b2": SlotMap(section_id="sec_exp", item_id="exp_1", bullet_id="b2", target_field="text"),
        "slot_header": SlotMap(section_id="sec_hdr", item_id="hdr_item", target_field="text"),
    }

    return TemplateProfile(
        schema_version=SchemaVersion.field_1_1_0,
        template_profile_id="tpl_sample_1",
        resume_id="res_sample_1",
        version=1,
        source_type=SourceType.uploaded_docx,
        slots=slots,
        slot_map=slot_map,
        fidelity_score=99.0,
        status=Status.ready,
    )


def test_plan_set_text_and_reorder(sample_template_profile):
    """Proves set_text and reorder operations are emitted cleanly."""
    original = {"sections": []}
    final = {"sections": []}
    changes = [
        Change(
            change_id="c1",
            type=ChangeType.rewrite_bullet,
            target_content_id="b1",
            field="text",
            before="Original bullet 1.",
            after="Engineered Python microservices with PostgreSQL.",
            reason="Skill alignment",
            status=ChangeStatus.accepted,
        ),
        Change(
            change_id="c2",
            type=ChangeType.reorder_bullets,
            target_content_id="exp_1",
            field="bullets",
            before=["b1", "b2"],
            after=["b2", "b1"],
            reason="Reorder",
            status=ChangeStatus.accepted,
        ),
    ]

    plan = build_change_plan(original, final, sample_template_profile, changes)
    assert plan.is_valid is True
    assert len(plan.operations) == 2

    # Check set_text op
    op1 = plan.operations[0]
    assert op1.type == OperationType.set_text
    assert op1.slot_id == "slot_b1"
    assert op1.text == "Engineered Python microservices with PostgreSQL."

    # Check reorder op
    op2 = plan.operations[1]
    assert op2.type == OperationType.reorder
    assert op2.new_order == ["slot_b2", "slot_b1"]


def test_plan_rejects_header_footer_targets(sample_template_profile):
    """Proves operations targeting protected header slots are rejected during validation."""
    changes = [
        Change(
            change_id="c_bad_hdr",
            type=ChangeType.rewrite_bullet,
            target_content_id="slot_header",
            field="text",
            before="Confidential Resume",
            after="Hacked Header",
            reason="Malicious edit",
            status=ChangeStatus.accepted,
        )
    ]

    plan = build_change_plan({}, {}, sample_template_profile, changes)
    assert plan.is_valid is False
    assert any("targets protected header slot" in err for err in plan.validation_errors)


def test_plan_rejects_budget_overflow(sample_template_profile):
    """Proves text exceeding slot max_lines budget is flagged as invalid."""
    changes = [
        Change(
            change_id="c_overflow",
            type=ChangeType.rewrite_bullet,
            target_content_id="b1",
            field="text",
            before="Original bullet 1.",
            after="This is an extremely long paragraph intended to wrap onto three or four lines, which clearly exceeds the 2 line budget allocated for this bullet in the template geometry specification, triggering a deterministic validation error before any XML is modified. It adds many more words to ensure it comfortably exceeds the budget for testing.",
            reason="Details",
            status=ChangeStatus.accepted,
        )
    ]

    plan = build_change_plan({}, {}, sample_template_profile, changes)
    assert plan.is_valid is False
    assert any("would exceed budget" in err for err in plan.validation_errors)


def test_plan_reports_unmappable_items(sample_template_profile):
    """Proves changes with unmappable content IDs are captured rather than silently dropped."""
    changes = [
        Change(
            change_id="c_ghost",
            type=ChangeType.rewrite_bullet,
            target_content_id="ghost_bullet_999",
            field="text",
            before="Ghost",
            after="Ghost after",
            reason="Ghost",
            status=ChangeStatus.accepted,
        )
    ]

    plan = build_change_plan({}, {}, sample_template_profile, changes)
    assert len(plan.unmappable_items) == 1
    assert "ghost_bullet_999" in plan.unmappable_items[0]


def test_plan_cloning_and_removal(sample_template_profile):
    """Proves clone_block and remove_slot operations are generated for additions and hidden items."""
    changes = [
        Change(
            change_id="c_add",
            type=ChangeType.add_item_from_master_profile,
            target_content_id="sec_exp",
            field="items",
            after="Kafka streaming event pipeline.",
            evidence_ids=["mp_kafka"],
            reason="Add project",
            status=ChangeStatus.accepted,
        ),
        Change(
            change_id="c_hide",
            type=ChangeType.hide_item,
            target_content_id="exp_1",
            field="items",
            reason="Hide role",
            status=ChangeStatus.accepted,
        ),
    ]

    plan = build_change_plan({}, {}, sample_template_profile, changes)
    assert plan.is_valid is True

    clone_ops = [op for op in plan.operations if op.type == OperationType.clone_block]
    assert len(clone_ops) == 1
    assert clone_ops[0].prototype_slot_id == "slot_b1"
    assert clone_ops[0].text == "Kafka streaming event pipeline."

    remove_ops = [op for op in plan.operations if op.type == OperationType.remove_slot]
    assert len(remove_ops) == 2  # exp_1 had slot_b1 and slot_b2
