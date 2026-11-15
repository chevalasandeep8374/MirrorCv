"""Pipeline Runner: Orchestrates agent execution, reports stage progress,
and persists versioned artifacts to Supabase database.
Zero resume text is ever logged in operational logs or stage_logs.
"""

import time
import json
import logging
from typing import Dict, Any, Optional
import httpx

from app.config import settings
from app.pipeline.state import PipelineRunState
from app.pipeline.graph import build_pipeline_graph

logger = logging.getLogger(__name__)


def _get_backend_headers(user_token: Optional[str] = None) -> Dict[str, str]:
    headers = {
        "apikey": settings.SUPABASE_KEY,
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }
    if settings.SUPABASE_SERVICE_ROLE_KEY:
        headers["Authorization"] = f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}"
    elif user_token:
        headers["Authorization"] = f"Bearer {user_token}"
    return headers


async def _update_run_in_supabase(
    run_id: str,
    payload: Dict[str, Any],
    user_token: Optional[str] = None,
) -> None:
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        return
    url = f"{settings.SUPABASE_URL.rstrip('/')}/rest/v1/pipeline_runs?id=eq.{run_id}"
    headers = _get_backend_headers(user_token)
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.patch(url, headers=headers, json=payload)
            if resp.status_code not in (200, 204):
                logger.warning(f"Failed to update pipeline_run {run_id} in Supabase ({resp.status_code}): {resp.text}")
    except Exception as e:
        logger.error(f"Error updating pipeline_run in Supabase: {e}")


async def _insert_template_profile_in_supabase(
    user_id: str,
    resume_id: str,
    profile_data: Dict[str, Any],
    user_token: Optional[str] = None,
) -> Optional[str]:
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        return None
    url = f"{settings.SUPABASE_URL.rstrip('/')}/rest/v1/template_profiles"
    headers = _get_backend_headers(user_token)
    headers["Prefer"] = "return=representation"
    payload = {
        "user_id": user_id,
        "resume_id": resume_id,
        "version": profile_data.get("version", 1),
        "profile": profile_data,
        "slot_map": profile_data.get("slot_map", {}),
        "fidelity_score": profile_data.get("fidelity_score", 95.0),
        "status": profile_data.get("status", "ready"),
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code in (200, 201):
                rows = resp.json()
                return rows[0]["id"] if rows else None
    except Exception as e:
        logger.error(f"Error persisting template_profile: {e}")
    return None


async def _insert_tailoring_results_in_supabase(
    run_id: str,
    user_id: str,
    tailored_data: Dict[str, Any],
    user_token: Optional[str] = None,
) -> None:
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        return
    url = f"{settings.SUPABASE_URL.rstrip('/')}/rest/v1/tailoring_results"
    headers = _get_backend_headers(user_token)
    payload = {
        "run_id": run_id,
        "user_id": user_id,
        "tailored_content": tailored_data,
        "change_list": tailored_data.get("changes", []),
        "score_before": tailored_data.get("score_before", 0.0),
        "score_after": tailored_data.get("score_after", 0.0),
        "missing_skills": tailored_data.get("missing_keywords", []),
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            await client.post(url, headers=headers, json=payload)
    except Exception as e:
        logger.error(f"Error persisting tailoring_results: {e}")


async def execute_pipeline_run(
    run_id: str,
    user_id: str,
    resume_id: str,
    content: Dict[str, Any],
    style: Dict[str, Any],
    jd_text: str,
    mode: str = "full",
    user_token: Optional[str] = None,
) -> Dict[str, Any]:
    """Asynchronous pipeline runner executing the 3-agent LangGraph workflow."""
    logger.info(f"Starting pipeline execution for run {run_id} (resume: {resume_id}, mode: {mode})")

    # 1. Transition to 'running'
    await _update_run_in_supabase(
        run_id,
        {"status": "running", "current_stage": "starting", "updated_at": "now()"},
        user_token,
    )

    initial_state: PipelineRunState = {
        "run_id": run_id,
        "user_id": user_id,
        "resume_id": resume_id,
        "job_description_text": jd_text,
        "mode": mode,
        "content": content,
        "style": style,
        "current_stage": "queued",
        "stage_log": [],
        "status": "running",
        "error": None,
    }

    max_retries = 3
    last_err: Optional[Exception] = None

    for attempt in range(1, max_retries + 1):
        try:
            # Build and invoke LangGraph StateGraph
            graph = build_pipeline_graph()
            final_state: PipelineRunState = await graph.ainvoke(initial_state)

            # 2. Persist Agent 1 TemplateProfile
            template_profile_id = None
            if final_state.get("template_profile"):
                template_profile_id = await _insert_template_profile_in_supabase(
                    user_id=user_id,
                    resume_id=resume_id,
                    profile_data=final_state["template_profile"].model_dump(mode="json"),
                    user_token=user_token,
                )

            # 3. Persist Agent 2 TailoringResults
            if final_state.get("tailored_content"):
                await _insert_tailoring_results_in_supabase(
                    run_id=run_id,
                    user_id=user_id,
                    tailored_data=final_state["tailored_content"].model_dump(mode="json"),
                    user_token=user_token,
                )

            # 4. Finalize pipeline run status in Supabase
            comp_dump = (
                final_state["composition_result"].model_dump(mode="json")
                if final_state.get("composition_result")
                else None
            )

            update_payload = {
                "status": "completed",
                "current_stage": "completed",
                "stage_log": final_state.get("stage_log", []),
                "result": comp_dump,
                "template_profile_id": template_profile_id,
                "updated_at": "now()",
            }
            await _update_run_in_supabase(run_id, update_payload, user_token)

            logger.info(f"Pipeline run {run_id} completed successfully (attempt {attempt}/{max_retries})")
            return {
                "status": "completed",
                "run_id": run_id,
                "stage_log": final_state.get("stage_log", []),
                "result": comp_dump,
            }

        except Exception as exc:
            last_err = exc
            logger.warning(f"Pipeline run {run_id} failed on attempt {attempt}/{max_retries}: {exc}")
            if attempt < max_retries:
                import asyncio
                await asyncio.sleep(2 ** (attempt - 1))

    # All retries exhausted -> Route to Dead-Letter Queue / state
    logger.error(f"Pipeline run {run_id} sent to DEAD-LETTER queue after {max_retries} failed attempts. Error: {last_err}", exc_info=True)
    dead_letter_msg = f"Dead-letter: pipeline run failed after {max_retries} attempts: {last_err}"
    await _update_run_in_supabase(
        run_id,
        {
            "status": "failed",
            "current_stage": "dead_letter",
            "error": dead_letter_msg,
            "updated_at": "now()",
        },
        user_token,
    )
    return {
        "status": "failed",
        "run_id": run_id,
        "error": dead_letter_msg,
        "dead_letter": True,
    }
