"""Unit tests for pure deterministic function apply_changes.
Proves order of application, immutability, reorder permutations, hidden items,
and ID preservation.
"""

import copy
import pytest
from app.services.apply_changes import apply_changes
from contracts.models.tailored_content import Change, ChangeType, ChangeStatus, RiskLevel

SAMPLE_ORIGINAL = {
    "header": {
        "name": "Alex Mercer",
        "title": "Senior Systems Engineer",
    },
    "sections": [
        {
            "id": "sec_summary",
            "type": "summary",
            "items": [
                {"id": "sum_1", "description": "Original summary text."}
            ],
        },
        {
            "id": "sec_exp",
            "type": "experience",
            "items": [
                {
                    "id": "exp_1",
                    "title": "Senior Engineer",
                    "subtitle": "Acme Corp",
                    "bullets": [
                        {"id": "b1", "text": "Original bullet 1."},
                        {"id": "b2", "text": "Original bullet 2."},
                        {"id": "b3", "text": "Original bullet 3."},
                    ],
                },
                {
                    "id": "exp_2",
                    "title": "Junior Developer",
                    "subtitle": "Old Corp",
                    "bullets": [
                        {"id": "b4", "text": "Older bullet text."},
                    ],
                },
            ],
        },
        {
            "id": "sec_skills",
            "type": "skills",
            "items": [
                {"id": "sk_1", "title": "Python"},
                {"id": "sk_2", "title": "PostgreSQL"},
                {"id": "sk_3", "title": "AWS"},
            ],
        },
    ],
}


def test_apply_changes_immutability():
    """Proves original_content is NEVER mutated."""
    orig_copy = copy.deepcopy(SAMPLE_ORIGINAL)
    changes = [
        Change(
            change_id="c1",
            type=ChangeType.rewrite_bullet,
            target_content_id="b1",
            field="text",
            before="Original bullet 1.",
            after="Tailored bullet 1 with **Python**.",
            reason="Skill emphasis",
            status=ChangeStatus.accepted,
        )
    ]

    final = apply_changes(SAMPLE_ORIGINAL, changes)

    # Assert original untouched
    assert SAMPLE_ORIGINAL == orig_copy
    # Assert final has change
    assert final["sections"][1]["items"][0]["bullets"][0]["text"] == "Tailored bullet 1 with **Python**."


def test_apply_changes_text_rewrites_and_summary():
    """Proves bullet rewrites and summary updates are applied cleanly."""
    changes = [
        Change(
            change_id="c_sum",
            type=ChangeType.rewrite_summary,
            target_content_id="sec_summary",
            field="summary",
            before="Original summary text.",
            after="Accomplished Systems Engineer with distributed systems expertise.",
            reason="Summary polish",
            status=ChangeStatus.accepted,
        ),
        Change(
            change_id="c_b2",
            type=ChangeType.rewrite_bullet,
            target_content_id="b2",
            field="text",
            before="Original bullet 2.",
            after="Optimized PostgreSQL queries reducing latency by 20%.",
            reason="Impact phrasing",
            status=ChangeStatus.accepted,
        ),
    ]

    final = apply_changes(SAMPLE_ORIGINAL, changes)

    # Summary updated
    assert final["sections"][0]["items"][0]["description"] == "Accomplished Systems Engineer with distributed systems expertise."
    # Bullet updated
    assert final["sections"][1]["items"][0]["bullets"][1]["text"] == "Optimized PostgreSQL queries reducing latency by 20%."
    # Unchanged bullet preserved
    assert final["sections"][1]["items"][0]["bullets"][2]["text"] == "Original bullet 3."


def test_apply_changes_hide_item():
    """Proves hide_item sets hidden: True on target item without dropping ID."""
    changes = [
        Change(
            change_id="c_hide",
            type=ChangeType.hide_item,
            target_content_id="exp_2",
            field="items",
            reason="Hide outdated junior role",
            risk_level=RiskLevel.medium,
            status=ChangeStatus.accepted,
        )
    ]

    final = apply_changes(SAMPLE_ORIGINAL, changes)
    exp_2 = next(itm for itm in final["sections"][1]["items"] if itm["id"] == "exp_2")
    assert exp_2.get("hidden") is True
    assert exp_2["id"] == "exp_2"


def test_apply_changes_reorder_bullets_and_skills():
    """Proves reordering preserves exact items while changing sequence."""
    changes = [
        # Reorder bullets: b3, b1, b2
        Change(
            change_id="c_reorder_b",
            type=ChangeType.reorder_bullets,
            target_content_id="exp_1",
            field="bullets",
            before=["b1", "b2", "b3"],
            after=["b3", "b1", "b2"],
            reason="Prioritize AWS bullet",
            status=ChangeStatus.accepted,
        ),
        # Reorder skills: sk_3, sk_1, sk_2
        Change(
            change_id="c_reorder_sk",
            type=ChangeType.reorder_skills,
            target_content_id="sec_skills",
            field="items",
            before=["sk_1", "sk_2", "sk_3"],
            after=["sk_3", "sk_1", "sk_2"],
            reason="Prioritize cloud skills",
            status=ChangeStatus.accepted,
        ),
    ]

    final = apply_changes(SAMPLE_ORIGINAL, changes)

    # Bullets reordered
    bullets = final["sections"][1]["items"][0]["bullets"]
    assert [b["id"] for b in bullets] == ["b3", "b1", "b2"]

    # Skills reordered
    skills = final["sections"][2]["items"]
    assert [s["id"] for s in skills] == ["sk_3", "sk_1", "sk_2"]


def test_apply_changes_add_item_from_master_profile():
    """Proves add_item_from_master_profile prepends new confirmed project item."""
    changes = [
        Change(
            change_id="c_add_proj",
            type=ChangeType.add_item_from_master_profile,
            target_content_id="sec_exp",
            field="items",
            after="Distributed Event Bus: Engineered Kafka messaging architecture.",
            evidence_ids=["mp_proj_kafka_99"],
            reason="Swap in high-relevance Kafka project",
            risk_level=RiskLevel.medium,
            status=ChangeStatus.accepted,
        )
    ]

    final = apply_changes(SAMPLE_ORIGINAL, changes)
    items = final["sections"][1]["items"]
    assert len(items) == 3
    added_item = items[0]
    assert added_item["id"] == "mp_proj_kafka_99"
    assert "Distributed Event Bus" in added_item["title"]


def test_apply_changes_determinism():
    """Proves multiple executions with same inputs return byte-for-byte identical output."""
    changes = [
        Change(
            change_id="c1",
            type=ChangeType.rewrite_bullet,
            target_content_id="b1",
            field="text",
            after="New bullet text.",
            reason="Rewrite",
            status=ChangeStatus.accepted,
        ),
        Change(
            change_id="c2",
            type=ChangeType.reorder_bullets,
            target_content_id="exp_1",
            field="bullets",
            after=["b2", "b1", "b3"],
            reason="Reorder",
            status=ChangeStatus.accepted,
        ),
    ]

    res1 = apply_changes(SAMPLE_ORIGINAL, changes)
    res2 = apply_changes(SAMPLE_ORIGINAL, changes)
    assert res1 == res2
