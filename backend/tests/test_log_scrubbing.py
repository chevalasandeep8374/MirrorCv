"""Test Suite for Log Scrubbing & Privacy Guarantees.
Proves that no candidate names, emails, phone numbers, bullet prose,
or JD text ever leak into application operational logs.
"""

import io
import logging
import pytest
from app.agents.analyst_tailor import AnalystTailorAgent
from app.services.resume_inventory import build_resume_inventory
from app.services.match_scorer import compute_match_score
from app.services.jd_analyzer import analyze_job_description_sync

CANARY_NAME = "CanaryCandidateSecretName99"
CANARY_EMAIL = "canary_pii_99@confidential-corp.test"
CANARY_PHONE = "+1-555-987-6543"
CANARY_BULLET = "SuperSecretProprietaryBulletPayloadAlphaOmega"
CANARY_JD = "TopSecretUnreleasedJobDescriptionRequirements"


@pytest.fixture
def log_capture():
    """Captures all log output from root and app loggers during test execution."""
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setLevel(logging.DEBUG)

    root_logger = logging.getLogger()
    app_logger = logging.getLogger("app")

    old_root_level = root_logger.level
    root_logger.setLevel(logging.DEBUG)
    app_logger.setLevel(logging.DEBUG)

    root_logger.addHandler(handler)
    app_logger.addHandler(handler)

    try:
        yield stream
    finally:
        root_logger.removeHandler(handler)
        app_logger.removeHandler(handler)
        root_logger.setLevel(old_root_level)


@pytest.mark.asyncio
async def test_zero_pii_and_text_leakage_in_logs(log_capture):
    """Executes full Agent 2 workflow and asserts canary strings do not appear in any log."""
    canary_resume = {
        "header": {
            "name": CANARY_NAME,
            "email": CANARY_EMAIL,
            "phone": CANARY_PHONE,
            "title": "Principal Security Engineer",
        },
        "sections": [
            {
                "id": "sec_exp",
                "type": "experience",
                "items": [
                    {
                        "id": "exp_1",
                        "title": "Staff Engineer",
                        "subtitle": "Confidential Corp",
                        "bullets": [
                            {"id": "b1", "text": f"Engineered system with {CANARY_BULLET} using Python and FastAPI."},
                        ],
                    }
                ],
            }
        ],
    }

    canary_jd = f"Looking for Python FastAPI engineer. Requirements: {CANARY_JD}."

    # 1. Run JD Analysis
    jd_analysis = analyze_job_description_sync(canary_jd)

    # 2. Run Resume Inventory
    inventory = build_resume_inventory(canary_resume)

    # 3. Run Match Scorer
    compute_match_score(inventory=inventory, jd=jd_analysis)

    # 4. Run AnalystTailorAgent
    agent = AnalystTailorAgent()
    await agent.analyze_and_tailor(
        run_id="scrubbing_test_run",
        resume_id="scrubbing_test_res",
        content=canary_resume,
        jd_text=canary_jd,
        mode="full",
    )

    all_logs = log_capture.getvalue()

    # Assert zero canary leakage
    assert CANARY_NAME not in all_logs, f"Candidate name '{CANARY_NAME}' leaked into logs!"
    assert CANARY_EMAIL not in all_logs, f"Candidate email '{CANARY_EMAIL}' leaked into logs!"
    assert CANARY_PHONE not in all_logs, f"Candidate phone '{CANARY_PHONE}' leaked into logs!"
    assert CANARY_BULLET not in all_logs, f"Bullet text '{CANARY_BULLET}' leaked into logs!"
    assert CANARY_JD not in all_logs, f"JD text '{CANARY_JD}' leaked into logs!"
