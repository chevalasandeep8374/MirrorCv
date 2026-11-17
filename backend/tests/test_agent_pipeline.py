"""Automated test suite for Step 5: LangGraph Multi-Agent Pipeline & Agents Skeleton.
Tests:
1. Agent 1 (Template Guardian) contract adherence & slot extraction.
2. Agent 2 (Analyst & Tailor) keyword scoring, fact-grounded rules, and safe inline markup.
3. Agent 3 (Composer) slot insertion and overflow budget verification.
4. End-to-end LangGraph StateGraph execution & stage_log privacy guarantee (no resume text).
"""

import os
import pytest

from app.agents.template_guardian import TemplateGuardianAgent
from app.agents.analyst_tailor import AnalystTailorAgent
from app.agents.composer import ComposerAgent
from app.pipeline.graph import build_pipeline_graph
from app.pipeline.state import PipelineRunState

from contracts.models.template_profile import TemplateProfile
from contracts.models.tailored_content import TailoredContent
from contracts.models.composition_result import CompositionResult

SAMPLE_RESUME_CONTENT = {
    "header": {
        "name": "Alex Mercer",
        "title": "Senior Software Engineer",
        "email": "alex@example.com",
    },
    "sections": [
        {
            "id": "sec_exp_01",
            "type": "experience",
            "title": "Work Experience",
            "items": [
                {
                    "id": "item_exp_01",
                    "title": "Lead Backend Developer",
                    "subtitle": "Apex Cloud Systems",
                    "date": "2021 - Present",
                    "bullets": [
                        {
                            "id": "b_01",
                            "text": "Architected distributed RESTful microservices reducing response latency by 35%.",
                        },
                        {
                            "id": "b_02",
                            "text": "Implemented caching layers and database indexing improving query throughput.",
                        },
                    ],
                }
            ],
        }
    ],
}

SAMPLE_STYLE = {
    "typography": {
        "headingFont": "Inter",
        "bodyFont": "Inter",
        "fontSizeScale": 1.0,
    },
    "colors": {
        "primary": "#0f172a",
        "text": "#1e293b",
    },
}

SAMPLE_JD = """
We are looking for a Senior Python Engineer experienced in FastAPI, Docker, and PostgreSQL.
The ideal candidate has hands-on experience building scalable microservices and database optimization.
"""


@pytest.mark.asyncio
async def test_agent_1_template_guardian():
    """Proves Agent 1 produces a valid, schema-compliant TemplateProfile."""
    guardian = TemplateGuardianAgent()
    profile = await guardian.generate_profile(
        resume_id="res_test_001",
        content=SAMPLE_RESUME_CONTENT,
        style=SAMPLE_STYLE,
    )

    assert isinstance(profile, TemplateProfile)
    assert profile.schema_version.value == "1.0.0"
    assert profile.resume_id == "res_test_001"
    assert len(profile.slots) >= 3  # header name, item title, bullets
    assert profile.fidelity_score >= 95.0
    assert profile.status.value == "ready"

    # Verify slot geometry & pointer
    b_slot = next(s for s in profile.slots if s.role.value == "bullet")
    assert b_slot.max_chars > 0
    assert b_slot.font == "Inter"


@pytest.mark.asyncio
async def test_agent_2_analyst_tailor():
    """Proves Agent 2 analyzes JD, computes score, and generates grounded changes with safe markdown."""
    guardian = TemplateGuardianAgent()
    profile = await guardian.generate_profile(
        resume_id="res_test_001",
        content=SAMPLE_RESUME_CONTENT,
        style=SAMPLE_STYLE,
    )

    tailor = AnalystTailorAgent()
    tailored = await tailor.analyze_and_tailor(
        run_id="run_test_001",
        resume_id="res_test_001",
        content=SAMPLE_RESUME_CONTENT,
        jd_text=SAMPLE_JD,
        template_profile=profile,
    )

    assert isinstance(tailored, TailoredContent)
    assert tailored.schema_version.value in ("1.0.0", "1.1.0")
    assert tailored.run_id == "run_test_001"
    assert tailored.score_after >= tailored.score_before

    # Check anti-hallucination rules
    assert tailored.rules.no_new_facts_allowed.value is True

    # Check changes & safe inline markdown
    assert len(tailored.changes) > 0
    for chg in tailored.changes:
        assert chg.source_reference.is_grounded is True
        # Check inline markup: must contain **bold** and NO raw HTML < >
        assert "<script" not in chg.tailored_text
        assert "<div>" not in chg.tailored_text
        assert "**" in chg.tailored_text


@pytest.mark.asyncio
async def test_agent_3_composer():
    """Proves Agent 3 merges tailored content into slots and performs budget verification."""
    guardian = TemplateGuardianAgent()
    profile = await guardian.generate_profile(
        resume_id="res_test_001",
        content=SAMPLE_RESUME_CONTENT,
        style=SAMPLE_STYLE,
    )

    tailor = AnalystTailorAgent()
    tailored = await tailor.analyze_and_tailor(
        run_id="run_test_001",
        resume_id="res_test_001",
        content=SAMPLE_RESUME_CONTENT,
        jd_text=SAMPLE_JD,
        template_profile=profile,
    )

    sample_docx = os.path.join(os.path.dirname(__file__), "fixtures", "sample_single_column.docx")
    composer = ComposerAgent()
    result = await composer.compose(
        run_id="run_test_001",
        resume_id="res_test_001",
        template_docx_path=sample_docx,
        original_content=SAMPLE_RESUME_CONTENT,
        original_style=SAMPLE_STYLE,
        template_profile=profile,
        tailored_content=tailored,
    )

    assert isinstance(result, CompositionResult)
    assert result.schema_version.value in ("1.0.0", "1.1.0")
    assert len(result.output_files) == 2  # pdf and docx
    assert result.overflow_report.has_overflow is False
    assert result.status.value in ("success", "ready")


@pytest.mark.asyncio
async def test_langgraph_pipeline_execution_and_privacy():
    """Proves end-to-end execution through the LangGraph StateGraph,

    verifying that no resume body text is leaked into stage_log (Change #9).
    """
    graph = build_pipeline_graph()

    initial_state: PipelineRunState = {
        "run_id": "run_e2e_001",
        "user_id": "user_e2e_123",
        "resume_id": "res_e2e_456",
        "job_description_text": SAMPLE_JD,
        "content": SAMPLE_RESUME_CONTENT,
        "style": SAMPLE_STYLE,
        "current_stage": "queued",
        "stage_log": [],
        "status": "running",
    }

    final_state = await graph.ainvoke(initial_state)

    # 1. State assertions
    assert final_state["status"] == "completed"
    assert final_state["current_stage"] == "composer"
    assert final_state["template_profile"] is not None
    assert final_state["tailored_content"] is not None
    assert final_state["composition_result"] is not None

    # 2. Stage log assertions
    stage_log = final_state["stage_log"]
    assert len(stage_log) == 3
    stages_called = [entry["stage"] for entry in stage_log]
    assert stages_called == ["template_guardian", "analyst_tailor", "composer"]

    # 3. Privacy guarantee (Change #9: Zero resume text in stage_log)
    for entry in stage_log:
        log_str = str(entry).lower()
        # Ensure Alex Mercer and resume bullet text are NOT in stage_log
        assert "alex mercer" not in log_str
        assert "architected distributed" not in log_str
        assert "apex cloud" not in log_str
        # Verify strictly numerical and stage metadata
        assert "duration_ms" in entry
