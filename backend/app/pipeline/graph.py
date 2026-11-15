"""LangGraph StateGraph for MirrorCV Three-Agent Pipeline:
Agent 1 (Template Guardian) -> Agent 2 (Analyst & Tailor) -> Agent 3 (Composer).
"""

import time
import logging
import httpx
from langgraph.graph import StateGraph, END, START

from app.config import settings
from contracts.models.template_profile import TemplateProfile
from app.pipeline.state import PipelineRunState
from app.agents.template_guardian import TemplateGuardianAgent
from app.agents.analyst_tailor import AnalystTailorAgent
from app.agents.composer import ComposerAgent

logger = logging.getLogger(__name__)

guardian_agent = TemplateGuardianAgent()
tailor_agent = AnalystTailorAgent()
composer_agent = ComposerAgent()


async def guardian_node(state: PipelineRunState) -> PipelineRunState:
    """Stage 1: Template Guardian extracts slots and geometry rules."""
    t0 = time.time()
    logger.info(f"Pipeline [{state.get('run_id')}]: Executing guardian_node")

    existing_profile = state.get("template_profile")
    resume_id = state.get("resume_id")
    if not existing_profile and resume_id and settings.SUPABASE_URL and settings.SUPABASE_KEY:
        try:
            url = f"{settings.SUPABASE_URL.rstrip('/')}/rest/v1/template_profiles?resume_id=eq.{resume_id}&select=*"
            headers = {"apikey": settings.SUPABASE_KEY}
            if settings.SUPABASE_SERVICE_ROLE_KEY:
                headers["Authorization"] = f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}"
            async with httpx.AsyncClient(timeout=8.0) as client:
                res = await client.get(url, headers=headers)
                if res.status_code == 200 and res.json():
                    rows = res.json()
                    rows.sort(key=lambda r: float(r.get("fidelity_score") or 0.0), reverse=True)
                    p_data = rows[0].get("profile")
                    if p_data:
                        existing_profile = TemplateProfile(**p_data)
                        state["template_profile_exists"] = True
        except Exception as e:
            logger.warning(f"Could not load existing template profile: {e}")

    if existing_profile:
        profile = existing_profile
    else:
        profile = await guardian_agent.generate_profile(
            resume_id=state["resume_id"],
            content=state.get("content") or {},
            style=state.get("style") or {},
        )

    duration_ms = round((time.time() - t0) * 1000, 2)
    state["template_profile"] = profile
    state["current_stage"] = "template_guardian"
    state.setdefault("stage_log", []).append({
        "stage": "template_guardian",
        "duration_ms": duration_ms,
        "slots_count": len(profile.slots),
        "fidelity_score": float(profile.fidelity_score),
        "timestamp": time.time(),
    })
    return state


async def tailor_node(state: PipelineRunState) -> PipelineRunState:
    """Stage 2: Analyst & Tailor generates fact-grounded tailored adjustments."""
    t0 = time.time()
    logger.info(f"Pipeline [{state.get('run_id')}]: Executing tailor_node")

    tailored = await tailor_agent.analyze_and_tailor(
        run_id=state["run_id"],
        resume_id=state["resume_id"],
        content=state.get("content") or {},
        jd_text=state.get("job_description_text") or "",
        template_profile=state.get("template_profile"),
        style=state.get("style"),
        mode=state.get("mode", "full"),
        user_id=state.get("user_id"),
    )

    duration_ms = round((time.time() - t0) * 1000, 2)
    state["tailored_content"] = tailored
    state["current_stage"] = "analyst_tailor"
    if state.get("mode") == "analyze":
        state["status"] = "completed"

    state.setdefault("stage_log", []).append({
        "stage": "analyst_tailor",
        "duration_ms": duration_ms,
        "mode": state.get("mode", "full"),
        "changes_count": len(tailored.changes),
        "score_before": float(tailored.score_before),
        "score_after": float(tailored.score_after),
        "missing_keywords_count": len(tailored.missing_keywords),
        "timestamp": time.time(),
    })
    return state


def route_after_tailor(state: PipelineRunState) -> str:
    """Routes to END if mode is analyze, otherwise continues to composer."""
    if state.get("mode") == "analyze":
        return END
    return "composer"


async def composer_node(state: PipelineRunState) -> PipelineRunState:
    """Stage 3: Composer merges tailored parts into slots with zero overflow."""
    t0 = time.time()
    logger.info(f"Pipeline [{state.get('run_id')}]: Executing composer_node")

    import os
    docx_path = state.get("template_docx_path")
    if not docx_path or not os.path.exists(docx_path):
        fixtures_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "tests", "fixtures"))
        docx_path = os.path.join(fixtures_dir, "sample_single_column.docx")

    comp_result = await composer_agent.compose(
        run_id=state["run_id"],
        resume_id=state["resume_id"],
        user_id=state.get("user_id"),
        template_docx_path=docx_path,
        original_content=state.get("content") or {},
        original_style=state.get("style") or {},
        template_profile=state["template_profile"],
        tailored_content=state["tailored_content"],
        user_token=state.get("user_token"),
    )

    duration_ms = round((time.time() - t0) * 1000, 2)
    state["composition_result"] = comp_result
    state["current_stage"] = "composer"
    state["status"] = "completed"
    state.setdefault("stage_log", []).append({
        "stage": "composer",
        "duration_ms": duration_ms,
        "output_files_count": len(comp_result.output_files),
        "has_overflow": comp_result.overflow_report.has_overflow,
        "final_status": comp_result.status.value,
        "timestamp": time.time(),
    })
    return state


def build_pipeline_graph() -> StateGraph:
    """Builds and compiles the 3-agent StateGraph."""
    builder = StateGraph(PipelineRunState)

    builder.add_node("guardian", guardian_node)
    builder.add_node("tailor", tailor_node)
    builder.add_node("composer", composer_node)

    builder.add_edge(START, "guardian")
    builder.add_edge("guardian", "tailor")
    builder.add_conditional_edges("tailor", route_after_tailor, {END: END, "composer": "composer"})
    builder.add_edge("composer", END)

    return builder.compile()
