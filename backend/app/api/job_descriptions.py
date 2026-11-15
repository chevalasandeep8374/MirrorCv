"""API Endpoints for Job Description intake, structured parsing, and cached retrieval."""

import uuid
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, Field
import httpx

from app.config import settings
from app.api.deps import get_current_user, CurrentUser
from app.schemas.tailoring import JDAnalysis
from app.services.jd_analyzer import analyze_job_description, compute_jd_hash

router = APIRouter(prefix="/job-descriptions", tags=["Job Descriptions"])

# Local store fallback for testing and dev environments
_LOCAL_JD_STORE: Dict[str, Dict[str, Any]] = {}


class JobDescriptionCreateRequest(BaseModel):
    raw_text: str = Field(..., min_length=20, max_length=20000, description="Pasted job description text")
    title: Optional[str] = Field(None, max_length=150)
    company: Optional[str] = Field(None, max_length=150)


class JobDescriptionResponse(BaseModel):
    id: str
    user_id: str
    title: Optional[str]
    company: Optional[str]
    raw_text: str
    text_hash: Optional[str]
    analysis: JDAnalysis
    created_at: Optional[str] = None


@router.post("", response_model=JobDescriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_job_description(
    payload: JobDescriptionCreateRequest,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Submits a job description text (max 20k chars), performs structured analysis,

    normalizes skills through taxonomy, and caches by text_hash.
    """
    user_id = current_user.id
    auth_header = request.headers.get("Authorization", "")
    user_token = auth_header.replace("Bearer ", "") if "Bearer " in auth_header else None

    text_hash = compute_jd_hash(payload.raw_text)

    # 1. Check existing cached JD for this user
    if settings.SUPABASE_URL and settings.SUPABASE_KEY:
        check_url = f"{settings.SUPABASE_URL.rstrip('/')}/rest/v1/job_descriptions?user_id=eq.{user_id}&text_hash=eq.{text_hash}&select=*"
        headers = {"apikey": settings.SUPABASE_KEY}
        if settings.SUPABASE_SERVICE_ROLE_KEY:
            headers["Authorization"] = f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}"
        elif user_token:
            headers["Authorization"] = f"Bearer {user_token}"

        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                res = await client.get(check_url, headers=headers)
                if res.status_code == 200:
                    rows = res.json()
                    if rows:
                        row = rows[0]
                        return JobDescriptionResponse(
                            id=row["id"],
                            user_id=row["user_id"],
                            title=row.get("title"),
                            company=row.get("company"),
                            raw_text=row["raw_text"],
                            text_hash=row.get("text_hash"),
                            analysis=JDAnalysis.model_validate(row.get("analysis", {})),
                            created_at=row.get("created_at"),
                        )
        except Exception:
            pass

    # 2. Perform fresh analysis
    analysis = await analyze_job_description(
        jd_text=payload.raw_text,
        title=payload.title,
        company=payload.company,
        user_id=user_id,
        user_token=user_token,
    )

    jd_id = str(uuid.uuid4())
    stored_row = {
        "id": jd_id,
        "user_id": user_id,
        "title": payload.title or analysis.job_title,
        "company": payload.company or analysis.company,
        "raw_text": payload.raw_text,
        "text_hash": text_hash,
        "analysis": analysis.model_dump(mode="json"),
    }

    # 3. Persist in Supabase with user RLS isolation
    _LOCAL_JD_STORE[jd_id] = stored_row

    if settings.SUPABASE_URL and settings.SUPABASE_KEY:
        insert_url = f"{settings.SUPABASE_URL.rstrip('/')}/rest/v1/job_descriptions"
        headers = {
            "apikey": settings.SUPABASE_KEY,
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }
        if settings.SUPABASE_SERVICE_ROLE_KEY:
            headers["Authorization"] = f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}"
        elif user_token:
            headers["Authorization"] = f"Bearer {user_token}"

        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                insert_res = await client.post(insert_url, headers=headers, json=stored_row)
                if insert_res.status_code in (200, 201):
                    rows = insert_res.json()
                    if rows:
                        stored_row["created_at"] = rows[0].get("created_at")
        except Exception:
            pass

    return JobDescriptionResponse(
        id=jd_id,
        user_id=user_id,
        title=stored_row["title"],
        company=stored_row["company"],
        raw_text=payload.raw_text,
        text_hash=text_hash,
        analysis=analysis,
        created_at=stored_row.get("created_at"),
    )


@router.get("/{jd_id}", response_model=JobDescriptionResponse)
async def get_job_description(
    jd_id: str,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Retrieves a previously analyzed job description by ID."""
    user_id = current_user.id
    auth_header = request.headers.get("Authorization", "")
    user_token = auth_header.replace("Bearer ", "") if "Bearer " in auth_header else None

    if settings.SUPABASE_URL and settings.SUPABASE_KEY:
        url = f"{settings.SUPABASE_URL.rstrip('/')}/rest/v1/job_descriptions?id=eq.{jd_id}&user_id=eq.{user_id}&select=*"
        headers = {"apikey": settings.SUPABASE_KEY}
        if settings.SUPABASE_SERVICE_ROLE_KEY:
            headers["Authorization"] = f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}"
        elif user_token:
            headers["Authorization"] = f"Bearer {user_token}"

        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                res = await client.get(url, headers=headers)
                if res.status_code == 200:
                    rows = res.json()
                    if rows:
                        row = rows[0]
                        return JobDescriptionResponse(
                            id=row["id"],
                            user_id=row["user_id"],
                            title=row.get("title"),
                            company=row.get("company"),
                            raw_text=row["raw_text"],
                            text_hash=row.get("text_hash"),
                            analysis=JDAnalysis.model_validate(row.get("analysis", {})),
                            created_at=row.get("created_at"),
                        )
        except Exception:
            pass

    # Check local fallback store
    if jd_id in _LOCAL_JD_STORE:
        row = _LOCAL_JD_STORE[jd_id]
        if row.get("user_id") == user_id:
            return JobDescriptionResponse(
                id=row["id"],
                user_id=row["user_id"],
                title=row.get("title"),
                company=row.get("company"),
                raw_text=row["raw_text"],
                text_hash=row.get("text_hash"),
                analysis=JDAnalysis.model_validate(row.get("analysis", {})),
                created_at=row.get("created_at"),
            )
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job description not found")
