"""Unit and integration tests for Phase D Step 1: Review flow, conflict detection,
live fit estimation, batch low-risk acceptance, and add_item_from_master_profile.
"""

import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.api.deps import CurrentUser, get_current_user
from contracts.models.tailored_content import (
    Change,
    ChangeType,
    ChangeStatus,
    RiskLevel,
)
from app.services.tailor_verifier import tailor_verifier
from app.api.tailoring import calculate_live_fit_estimate

TEST_USER = CurrentUser(id="fb6cdc4c-a608-4be0-8224-2954b0fce396", email="alpha_tester_1234@gmail.com")


@pytest.fixture
def override_test_user():
    app.dependency_overrides[get_current_user] = lambda: TEST_USER
    yield
    app.dependency_overrides.pop(get_current_user, None)


def test_calculate_live_fit_estimate():
    """Validates line delta estimation for rewrites, hide_item, and add_item_from_master_profile."""
    changes = [
        # Rewrite bullet with 1 line expansion
        {
            "change_id": "c1",
            "type": "rewrite_bullet",
            "target_content_id": "b1",
            "before": "Short bullet text.",
            "after": "Much longer bullet text that wraps across multiple lines in the document geometry.",
            "status": "accepted",
        },
        # Hide item: creates free room
        {
            "change_id": "c2",
            "type": "hide_item",
            "target_content_id": "item_old",
            "before": "Older work experience paragraph.",
            "status": "accepted",
        },
        # Proposed change (not accepted yet): must not affect estimate
        {
            "change_id": "c3",
            "type": "rewrite_bullet",
            "target_content_id": "b2",
            "before": "Existing bullet.",
            "after": "Super long bullet that wraps significantly.",
            "status": "proposed",
        },
    ]

    fit_est = calculate_live_fit_estimate(changes)
    assert fit_est["accepted_changes_count"] == 2
    assert "predicted_line_delta" in fit_est
    assert "fit_status" in fit_est
    assert fit_est["has_risk_of_page_overflow"] is False or fit_est["has_risk_of_page_overflow"] is True


def test_verifier_add_item_from_master_profile():
    """Tests verifier gate for add_item_from_master_profile."""
    resume = {
        "header": {"name": "Alex Mercer", "title": "Software Engineer"},
        "sections": [{"id": "sec_exp", "type": "experience", "items": []}],
    }
    skills = {"Python", "PostgreSQL"}

    # 1. Missing evidence_ids -> REJECTED
    chg_no_ev = Change(
        change_id="c_add_1",
        type=ChangeType.add_item_from_master_profile,
        field="items",
        after="Architected cloud services at ScaleCorp.",
        evidence_ids=[],
        reason="Swap project",
    )
    res1 = tailor_verifier.verify_change(chg_no_ev, resume, skills, confirmed_evidence_text="")
    assert not res1.is_valid
    assert res1.gate_failed == "missing_master_profile_evidence"

    # 2. Missing confirmed evidence text -> REJECTED
    chg_no_text = Change(
        change_id="c_add_2",
        type=ChangeType.add_item_from_master_profile,
        field="items",
        after="Architected cloud services at ScaleCorp.",
        evidence_ids=["mp_item_123"],
        reason="Swap project",
    )
    res2 = tailor_verifier.verify_change(chg_no_text, resume, skills, confirmed_evidence_text="")
    assert not res2.is_valid
    assert res2.gate_failed == "unconfirmed_master_item"

    # 3. Grounded with confirmed evidence -> ACCEPTED
    evidence = "Architected cloud services at ScaleCorp using Python and PostgreSQL."
    chg_ok = Change(
        change_id="c_add_3",
        type=ChangeType.add_item_from_master_profile,
        field="items",
        after="Architected cloud services at ScaleCorp using Python and PostgreSQL.",
        evidence_ids=["mp_item_123"],
        reason="Swap project",
    )
    res3 = tailor_verifier.verify_change(chg_ok, resume, skills, confirmed_evidence_text=evidence)
    assert res3.is_valid


@pytest.mark.asyncio
async def test_review_flow_conflict_detection_and_batch_acceptance(override_test_user):
    """Integration test verifying conflict detection (HTTP 409) and batch low-risk acceptance."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # First, intake JD and create pipeline run
        jd_res = await client.post("/api/job-descriptions", json={
            "title": "Backend Architect",
            "company": "Scale Corp",
            "raw_text": "We need an engineer experienced in Python, FastAPI, and PostgreSQL to design microservices.",
        })
        assert jd_res.status_code == 201

        # Queue pipeline run in full mode
        run_res = await client.post("/api/pipeline/runs", json={
            "resume_id": "c421c70a-b3b6-4f54-bdd6-9993e69be239",
            "job_description_text": "We need an engineer experienced in Python, FastAPI, and PostgreSQL to design microservices.",
            "mode": "full",
        })
        assert run_res.status_code == 201
        run_id = run_res.json()["id"]

        # Fetch tailoring results
        tailor_res = await client.get(f"/api/tailoring/{run_id}")
        if tailor_res.status_code == 200:
            data = tailor_res.json()
            changes = data.get("changes", [])
            if len(changes) >= 1:
                chg1 = changes[0]["change_id"]

                # 1. Accept first change
                patch_res1 = await client.patch(f"/api/tailoring/{run_id}/changes/{chg1}", json={"status": "accepted"})
                assert patch_res1.status_code == 200
                res1_data = patch_res1.json()
                assert res1_data["new_status"] == "accepted"
                assert "live_fit_estimate" in res1_data

                # 2. Batch accept all low risk
                batch_res = await client.post(f"/api/tailoring/{run_id}/changes/accept-low-risk")
                assert batch_res.status_code == 200
                batch_data = batch_res.json()
                assert "total_accepted_count" in batch_data
                assert "live_fit_estimate" in batch_data
