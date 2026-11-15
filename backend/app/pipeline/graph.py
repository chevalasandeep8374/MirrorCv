"""LangGraph StateGraph for MirrorCV Three-Agent Pipeline:
Agent 1 (Template Guardian) -> Agent 2 (Analyst & Tailor) -> Agent 3 (Composer).
"""

import time
import logging
from langgraph.graph import StateGraph, END, START

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

    profile = await guardian_agent.generate_profile(
        resume_id=state["resume_id"],
        content=state.get("content") or {},
        style=state.get("style") or {},
    )

    duration_ms = round((time.time() - t0) * 1000, 2)
    state["template_profile"] = profile
    state["current_stage"] = "guardian"
    state.setdefault("stage_log", []).append({
        "stage": "guardian",
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
    state["current_stage"] = "tailor"
    if state.get("mode") == "analyze":
        state["status"] = "completed"

    state.setdefault("stage_log", []).append({
        "stage": "tailor",
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

    comp_result = await composer_agent.compose(
        run_id=state["run_id"],
        resume_id=state["resume_id"],
        original_content=state.get("content") or {},
        original_style=state.get("style") or {},
        template_profile=state["template_profile"],
        tailored_content=state["tailored_content"],
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
