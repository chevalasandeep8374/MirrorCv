"""Compositions API Endpoints for MirrorCV Agent 3 (Composer).
Handles Run 2 execution (POST /api/tailoring/{run_id}/compose), composition retrieval
(GET /api/compositions/{id}) with 10-minute signed download URLs, and layout overflow
acknowledgement.
"""

import os
import copy
import uuid
import logging
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Request, Body
from pydantic import BaseModel, Field
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
import httpx

from app.database import get_db
from app.config import settings
from app.api.deps import get_current_user, CurrentUser
from app.models.composition import Composition
from app.agents.composer import composer_agent, generate_signed_storage_url
from contracts.models.composition_result import CompositionResult, Status
from contracts.models.template_profile import TemplateProfile

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/compositions", tags=["Compositions"])
tailoring_compose_router = APIRouter(prefix="/tailoring", tags=["Tailoring Compose"])


class ComposeRequest(BaseModel):
    confirmed_bullet_removals: Optional[List[str]] = Field(
        None, description="List of bullet IDs explicitly confirmed for removal by the user to resolve layout overflow"
    )


@tailoring_compose_router.post("/{run_id}/compose", response_model=Dict[str, Any])
async def trigger_composition(
    run_id: str,
    request: Request,
    payload: Optional[ComposeRequest] = Body(None),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Triggers Run 2 (Composer Agent) for accepted changes of the pipeline run.

    Enforces template integrity invariants:
    - Failing integrity blocks DOCX download and sets status 'failed'.
    - Layout fit issues (page count overflow) set status 'layout_changed'.
    Writes result to backend-owned public.compositions table.
    """
    user_id = current_user.id
    auth_header = request.headers.get("Authorization", "")
    user_token = auth_header.replace("Bearer ", "") if "Bearer " in auth_header else None

    # 1. Fetch tailoring result and accepted changes
    tailored_changes: List[Dict[str, Any]] = []
    resume_id: str = ""
    template_docx_path: str = ""
    original_content: Dict[str, Any] = {"sections": []}
    template_profile_data: Optional[Dict[str, Any]] = None

    if settings.SUPABASE_URL and settings.SUPABASE_KEY:
        headers = {"apikey": settings.SUPABASE_KEY}
        if settings.SUPABASE_SERVICE_ROLE_KEY:
            headers["Authorization"] = f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}"
        elif user_token:
            headers["Authorization"] = f"Bearer {user_token}"

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Fetch tailoring result
                url = f"{settings.SUPABASE_URL.rstrip('/')}/rest/v1/tailoring_results?run_id=eq.{run_id}&user_id=eq.{user_id}&select=*"
                res = await client.get(url, headers=headers)
                if res.status_code == 200 and res.json():
                    row = res.json()[0]
                    tc = row.get("tailored_content") or {}
                    tailored_changes = tc.get("changes", [])

                # Fetch pipeline run to get resume_id
                pr_url = f"{settings.SUPABASE_URL.rstrip('/')}/rest/v1/pipeline_runs?id=eq.{run_id}&user_id=eq.{user_id}&select=*"
                pr_res = await client.get(pr_url, headers=headers)
                if pr_res.status_code == 200 and pr_res.json():
                    pr_row = pr_res.json()[0]
                    resume_id = pr_row.get("resume_id")

                # Fetch resume content
                if resume_id:
                    res_url = f"{settings.SUPABASE_URL.rstrip('/')}/rest/v1/resumes?id=eq.{resume_id}&user_id=eq.{user_id}&select=*"
                    res_r = await client.get(res_url, headers=headers)
                    if res_r.status_code == 200 and res_r.json():
                        original_content = res_r.json()[0].get("content") or original_content

                # Fetch template profile
                if resume_id:
                    tp_url = f"{settings.SUPABASE_URL.rstrip('/')}/rest/v1/template_profiles?resume_id=eq.{resume_id}&user_id=eq.{user_id}&select=*"
                    tp_res = await client.get(tp_url, headers=headers)
                    if tp_res.status_code == 200 and tp_res.json():
                        rows = tp_res.json()
                        rows.sort(key=lambda r: float(r.get("fidelity_score") or 0.0), reverse=True)
                        tp_row = rows[0]
                        template_profile_data = tp_row.get("profile")

        except Exception as e:
            logger.warning(f"Error reading Supabase run data: {e}")

    # Fallback to local files if not in cloud
    if not resume_id:
        resume_id = str(uuid.uuid4())

    fixtures_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "tests", "fixtures"))
    template_docx_path = os.path.join(fixtures_dir, "sample_single_column.docx")

    # Require valid template profile (fail closed - no synthetic template fabrication)
    if template_profile_data:
        template_profile = TemplateProfile(**template_profile_data)
    else:
        raise HTTPException(
            status_code=400,
            detail="TemplateProfile required for composition; cannot compose without verified template"
        )

    # Filter accepted changes
    accepted = [c for c in tailored_changes if c.get("status") == "accepted"]

    confirmed_removals = payload.confirmed_bullet_removals if payload else None

    # Execute Composer Agent
    result: CompositionResult = await composer_agent.compose(
        run_id=run_id,
        resume_id=resume_id,
        user_id=user_id,
        template_docx_path=template_docx_path,
        template_profile=template_profile,
        accepted_changes=accepted,
        original_content=original_content,
        confirmed_bullet_removals=confirmed_removals,
        user_token=user_token,
    )

    # Write to compositions table
    comp_row = Composition(
        id=result.composition_id,
        user_id=user_id,
        resume_id=resume_id,
        run_id=run_id,
        composition_result=result.model_dump(),
        status=result.status.value,
        fidelity_score=float(result.fidelity_score),
        page_count_before=result.page_count_before or 1,
        page_count_after=result.page_count_after or 1,
        storage_path_docx=result.output_files[0].storage_path if len(result.output_files) > 0 else None,
        storage_path_pdf=result.output_files[1].storage_path if len(result.output_files) > 1 else None,
        integrity_report=result.integrity_report.model_dump() if result.integrity_report else {},
        fit_loop=result.fit_loop.model_dump() if result.fit_loop else {},
    )

    db.add(comp_row)
    await db.commit()

    return result.model_dump()


@router.get("/{composition_id}", response_model=Dict[str, Any])
async def get_composition(
    composition_id: str,
    request: Request = None,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves an existing composition result with fresh 10-minute signed download URLs."""
    user_id = current_user.id
    auth_header = request.headers.get("Authorization", "") if request else ""
    user_token = auth_header.replace("Bearer ", "") if "Bearer " in auth_header else None

    stmt = select(Composition).where(Composition.id == composition_id, Composition.user_id == user_id)
    res = await db.execute(stmt)
    row = res.scalars().first()

    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Composition not found or unauthorized")

    comp_data = copy.deepcopy(row.composition_result)

    # Re-sign output file URLs with fresh 10-minute expiry
    if comp_data.get("output_files") and row.status != Status.failed.value:
        for f in comp_data["output_files"]:
            storage_path = f.get("storage_path")
            if storage_path:
                fresh_url = await generate_signed_storage_url("exports", storage_path, expires_in=600, user_token=user_token)
                f["download_url"] = fresh_url

    return comp_data


@router.post("/{composition_id}/acknowledge-overflow", response_model=Dict[str, Any])
async def acknowledge_layout_overflow(
    composition_id: str,
    request: Request = None,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Allows a user to explicitly acknowledge a multi-page / layout-changed composition,

    generating signed download URLs for them.
    Blocked if integrity report failed (invariants 1-6, 8, or container clipping).
    """
    user_id = current_user.id
    auth_header = request.headers.get("Authorization", "") if request else ""
    user_token = auth_header.replace("Bearer ", "") if "Bearer " in auth_header else None

    stmt = select(Composition).where(Composition.id == composition_id, Composition.user_id == user_id)
    res = await db.execute(stmt)
    row = res.scalars().first()

    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Composition not found")

    if row.status == Status.failed.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot download: Template integrity verification failed. Template formatting must be preserved.",
        )

    comp_data = copy.deepcopy(row.composition_result)

    # Generate signed download URLs now that user has acknowledged
    if comp_data.get("output_files"):
        for f in comp_data["output_files"]:
            storage_path = f.get("storage_path")
            if storage_path:
                fresh_url = await generate_signed_storage_url("exports", storage_path, expires_in=600, user_token=user_token)
                f["download_url"] = fresh_url

    return comp_data
