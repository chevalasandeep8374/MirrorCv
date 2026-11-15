"""Pipeline API endpoints for orchestrating and polling SaaS AI Agent runs."""

import uuid
import asyncio
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, Field
import httpx

from app.config import settings
from app.api.deps import get_current_user, CurrentUser
from app.pipeline.runner import execute_pipeline_run

router = APIRouter(prefix="/pipeline", tags=["Pipeline"])


class PipelineRunCreateRequest(BaseModel):
    resume_id: str
    job_description_text: str = Field(..., min_length=20)
    job_title: Optional[str] = None
    mode: str = Field("full", pattern="^(analyze|full)$")


class PipelineRunResponse(BaseModel):
    id: str
    user_id: str
    resume_id: str
    status: str
    current_stage: str
    stage_log: List[Dict[str, Any]] = []
    error: Optional[str] = None
    result: Optional[Dict[str, Any]] = None


@router.post("/runs", response_model=PipelineRunResponse, status_code=status.HTTP_201_CREATED)
async def create_pipeline_run(
    payload: PipelineRunCreateRequest,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Initiates a multi-agent tailoring pipeline run.
    Validates user ownership, creates the queued run in Supabase,
    and launches background agent execution.
    """
    run_id = str(uuid.uuid4())
    user_id = current_user.id

    auth_header = request.headers.get("Authorization", "")
    user_token = auth_header.replace("Bearer ", "") if "Bearer " in auth_header else None

    # 1. Fetch resume content & style from Supabase or fallback
    resume_data = None
    if settings.SUPABASE_URL and settings.SUPABASE_KEY:
        headers = {"apikey": settings.SUPABASE_KEY}
        if user_token:
            headers["Authorization"] = f"Bearer {user_token}"
        elif settings.SUPABASE_SERVICE_ROLE_KEY:
            headers["Authorization"] = f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}"

        url = f"{settings.SUPABASE_URL.rstrip('/')}/rest/v1/resumes?id=eq.{payload.resume_id}&select=*"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, headers=headers)
                if resp.status_code == 200 and resp.json():
                    resume_data = resp.json()[0]
        except Exception as e:
            pass

    content = resume_data.get("content") or {} if resume_data else {}
    style = resume_data.get("style") or {} if resume_data else {}

    # 2. Insert queued record into pipeline_runs
    initial_log = [{
        "stage": "queued",
        "timestamp": asyncio.get_event_loop().time(),
    }]

    if settings.SUPABASE_URL and settings.SUPABASE_KEY:
        insert_headers = {
            "apikey": settings.SUPABASE_KEY,
            "Content-Type": "application/json",
        }
        if settings.SUPABASE_SERVICE_ROLE_KEY:
            insert_headers["Authorization"] = f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}"
        elif user_token:
            insert_headers["Authorization"] = f"Bearer {user_token}"

        insert_url = f"{settings.SUPABASE_URL.rstrip('/')}/rest/v1/pipeline_runs"
        insert_payload = {
            "id": run_id,
            "user_id": user_id,
            "resume_id": payload.resume_id,
            "status": "queued",
            "current_stage": "initialized",
            "stage_log": initial_log,
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(insert_url, headers=insert_headers, json=insert_payload)
                if resp.status_code not in (200, 201):
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Failed to queue pipeline run: {resp.text}",
                    )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error queuing run: {e}",
            )

    # 3. Launch background execution
    asyncio.create_task(
        execute_pipeline_run(
            run_id=run_id,
            user_id=user_id,
            resume_id=payload.resume_id,
            content=content,
            style=style,
            jd_text=payload.job_description_text,
            mode=payload.mode,
            user_token=user_token,
        )
    )

    return PipelineRunResponse(
        id=run_id,
        user_id=user_id,
        resume_id=payload.resume_id,
        status="queued",
        current_stage="initialized",
        stage_log=initial_log,
    )


@router.get("/runs/{run_id}", response_model=PipelineRunResponse)
async def get_pipeline_run(
    run_id: str,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Polls pipeline progress. Row-Level Security ensures users can only read their own runs."""
    auth_header = request.headers.get("Authorization", "")
    user_token = auth_header.replace("Bearer ", "") if "Bearer " in auth_header else None

    if settings.SUPABASE_URL and settings.SUPABASE_KEY:
        headers = {"apikey": settings.SUPABASE_KEY}
        if user_token:
            headers["Authorization"] = f"Bearer {user_token}"
        elif settings.SUPABASE_SERVICE_ROLE_KEY:
            headers["Authorization"] = f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}"

        url = f"{settings.SUPABASE_URL.rstrip('/')}/rest/v1/pipeline_runs?id=eq.{run_id}&select=*"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, headers=headers)
                if resp.status_code == 200 and resp.json():
                    row = resp.json()[0]
                    # Verify user isolation
                    if row.get("user_id") != current_user.id:
                        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
                    return PipelineRunResponse(
                        id=row["id"],
                        user_id=row["user_id"],
                        resume_id=row["resume_id"],
                        status=row["status"],
                        current_stage=row["current_stage"],
                        stage_log=row.get("stage_log") or [],
                        error=row.get("error"),
                        result=row.get("result"),
                    )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to query pipeline run: {e}",
            )

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
