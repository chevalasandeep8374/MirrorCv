"""SaaS Tailoring API Endpoints.
Provides run retrieval, change accept/reject with conflict detection,
live fit estimation, batch low-risk acceptance, and non-destructive application.
"""

import copy
import uuid
import logging
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, Field
import httpx

from app.config import settings
from app.api.deps import get_current_user, CurrentUser
from contracts.models.tailored_content import TailoredContent, ChangeStatus, ChangeType, RiskLevel
from app.services.resume_inventory import build_resume_inventory
from app.services.match_scorer import compute_match_score
from app.services.docx_rendering_measurements import measure_lines
from app.schemas.tailoring import JDAnalysis

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tailoring", tags=["Tailoring"])


class ChangeStatusUpdateRequest(BaseModel):
    status: ChangeStatus = Field(..., description="New status for the change: accepted, rejected, or proposed")


def calculate_live_fit_estimate(changes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Computes predicted visual line delta vs free room based on accepted changes."""
    accepted = [c for c in changes if c.get("status") == "accepted"]
    total_delta = 0
    lines_per_target: Dict[str, int] = {}
    default_slot_params = {
        "line_width_pt": 487.2,
        "formatting": {"font_family": "Calibri", "font_size_pt": 11.0, "bold": False},
    }

    for c in accepted:
        chg_type = c.get("type", "rewrite_bullet")
        before_txt = str(c.get("before") or "")
        after_txt = str(c.get("after") or "")
        target_id = c.get("target_content_id") or c.get("slot_id") or "slot"

        if chg_type in ("rewrite_bullet", "rewrite_summary", "normalize_term"):
            before_lines = measure_lines(before_txt, default_slot_params)
            after_lines = measure_lines(after_txt, default_slot_params)
            delta = after_lines - before_lines
            total_delta += delta
            lines_per_target[target_id] = delta
        elif chg_type == "hide_item":
            before_lines = measure_lines(before_txt, default_slot_params) if before_txt else 2
            total_delta -= before_lines
            lines_per_target[target_id] = -before_lines
        elif chg_type == "add_item_from_master_profile":
            after_lines = measure_lines(after_txt, default_slot_params) if after_txt else 2
            total_delta += after_lines
            lines_per_target[target_id] = after_lines

    fit_status = "fits_cleanly" if total_delta <= 0 else ("tight" if total_delta <= 2 else "overflow_warning")
    return {
        "predicted_line_delta": total_delta,
        "lines_per_target": lines_per_target,
        "has_risk_of_page_overflow": total_delta > 1,
        "free_lines_remaining": max(0, 3 - total_delta),
        "fit_status": fit_status,
        "accepted_changes_count": len(accepted),
    }


@router.get("/{run_id}", response_model=Dict[str, Any])
async def get_tailoring_result(
    run_id: str,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Retrieves full tailoring results (scores, breakdown, matched/missing skills,
    changes, rejected changes, suggestions, live fit estimate) for a pipeline run.
    """
    user_id = current_user.id
    auth_header = request.headers.get("Authorization", "")
    user_token = auth_header.replace("Bearer ", "") if "Bearer " in auth_header else None

    if settings.SUPABASE_URL and settings.SUPABASE_KEY:
        url = f"{settings.SUPABASE_URL.rstrip('/')}/rest/v1/tailoring_results?run_id=eq.{run_id}&user_id=eq.{user_id}&select=*"
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
                        tailored_content = row.get("tailored_content") or {}
                        changes = tailored_content.get("changes", [])
                        return {
                            "id": row["id"],
                            "run_id": row["run_id"],
                            "user_id": row["user_id"],
                            "score_before": row.get("score_before"),
                            "score_after": row.get("score_after"),
                            "score_breakdown": tailored_content.get("score_breakdown"),
                            "skills_analysis": tailored_content.get("skills_analysis"),
                            "changes": changes,
                            "rejected_changes": tailored_content.get("rejected_changes", []),
                            "suggestions": tailored_content.get("suggestions", []),
                            "matched_keywords": tailored_content.get("matched_keywords", []),
                            "missing_keywords": row.get("missing_skills", []),
                            "live_fit_estimate": calculate_live_fit_estimate(changes),
                            "created_at": row.get("created_at"),
                        }
        except Exception as e:
            logger.error(f"Error fetching tailoring results: {e}")

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tailoring results not found")


@router.patch("/{run_id}/changes/{change_id}")
async def update_change_status(
    run_id: str,
    change_id: str,
    payload: ChangeStatusUpdateRequest,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Accepts or rejects an individual tailored change.
    Enforces target conflict detection: blocking the second change if another accepted
    change already touches the same target bullet or slot.
    Dynamically recomputes score_after and live fit estimate on accepted changes only.
    """
    user_id = current_user.id
    auth_header = request.headers.get("Authorization", "")
    user_token = auth_header.replace("Bearer ", "") if "Bearer " in auth_header else None

    if not (settings.SUPABASE_URL and settings.SUPABASE_KEY):
        raise HTTPException(status_code=500, detail="Database not configured")

    headers = {"apikey": settings.SUPABASE_KEY}
    if settings.SUPABASE_SERVICE_ROLE_KEY:
        headers["Authorization"] = f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}"
    elif user_token:
        headers["Authorization"] = f"Bearer {user_token}"

    # 1. Fetch current tailoring_results row
    url = f"{settings.SUPABASE_URL.rstrip('/')}/rest/v1/tailoring_results?run_id=eq.{run_id}&user_id=eq.{user_id}&select=*"
    async with httpx.AsyncClient(timeout=8.0) as client:
        res = await client.get(url, headers=headers)
        if res.status_code != 200 or not res.json():
            raise HTTPException(status_code=404, detail="Tailoring results not found")
        row = res.json()[0]

    tailored_content = row.get("tailored_content") or {}
    changes = tailored_content.get("changes", [])

    target_chg = None
    for chg in changes:
        if chg.get("change_id") == change_id:
            target_chg = chg
            break

    if not target_chg:
        raise HTTPException(status_code=404, detail=f"Change {change_id} not found")

    # 2. Conflict Detection: If attempting to accept, ensure no other accepted change touches the same target
    if payload.status == ChangeStatus.accepted:
        target_id = target_chg.get("target_content_id")
        slot_id = target_chg.get("slot_id")

        for other in changes:
            if other.get("change_id") != change_id and other.get("status") == "accepted":
                other_target = other.get("target_content_id")
                other_slot = other.get("slot_id")
                if (target_id and other_target and target_id == other_target) or (slot_id and other_slot and slot_id == other_slot):
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=(
                            f"Conflict detected: Target '{target_id or slot_id}' already has an accepted change "
                            f"'{other.get('change_id')}'. Reject or unaccept it before accepting this one."
                        ),
                    )

    # Apply new status
    target_chg["status"] = payload.status.value

    # 3. Recompute score_after from accepted changes only
    accepted = [c for c in changes if c.get("status") == "accepted"]

    run_url = f"{settings.SUPABASE_URL.rstrip('/')}/rest/v1/pipeline_runs?id=eq.{run_id}&select=resume_id,job_description_id"
    async with httpx.AsyncClient(timeout=8.0) as client:
        r_run = await client.get(run_url, headers=headers)
        resume_id = r_run.json()[0]["resume_id"] if (r_run.status_code == 200 and r_run.json()) else None

    resume_content = {}
    if resume_id:
        res_url = f"{settings.SUPABASE_URL.rstrip('/')}/rest/v1/resumes?id=eq.{resume_id}&select=content"
        async with httpx.AsyncClient(timeout=8.0) as client:
            r_res = await client.get(res_url, headers=headers)
            if r_res.status_code == 200 and r_res.json():
                resume_content = r_res.json()[0].get("content") or {}

    inventory = build_resume_inventory(resume_content)
    scoring_result = compute_match_score(
        inventory=inventory,
        jd=JDAnalysis(
            required_skills=tailored_content.get("matched_keywords", []) + tailored_content.get("missing_keywords", []),
            keywords=tailored_content.get("matched_keywords", []),
        ),
        accepted_changes=accepted,
    )

    new_score_after = scoring_result.estimated_match_score
    tailored_content["score_after"] = new_score_after
    tailored_content["changes"] = changes
    fit_estimate = calculate_live_fit_estimate(changes)

    # 4. Update Supabase
    patch_url = f"{settings.SUPABASE_URL.rstrip('/')}/rest/v1/tailoring_results?id=eq.{row['id']}"
    patch_headers = dict(headers)
    patch_headers["Prefer"] = "return=representation"
    patch_payload = {
        "score_after": new_score_after,
        "tailored_content": tailored_content,
        "updated_at": "now()",
    }

    async with httpx.AsyncClient(timeout=8.0) as client:
        r_patch = await client.patch(patch_url, headers=patch_headers, json=patch_payload)
        if r_patch.status_code not in (200, 204):
            raise HTTPException(status_code=500, detail=f"Failed to update tailoring status: {r_patch.text}")

    return {
        "status": "updated",
        "change_id": change_id,
        "new_status": payload.status.value,
        "score_before": row.get("score_before"),
        "score_after": new_score_after,
        "accepted_changes_count": len(accepted),
        "live_fit_estimate": fit_estimate,
    }


@router.post("/{run_id}/changes/accept-low-risk")
async def accept_all_low_risk_changes(
    run_id: str,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
):
    """User-initiated batch acceptance of all low-risk proposed changes.
    Never automatically triggered. Excludes hide_item and add_item_from_master_profile.
    Resolves conflicts by accepting the first non-conflicting low-risk change per target.
    Recomputes score_after and returns updated live fit estimate.
    """
    user_id = current_user.id
    auth_header = request.headers.get("Authorization", "")
    user_token = auth_header.replace("Bearer ", "") if "Bearer " in auth_header else None

    if not (settings.SUPABASE_URL and settings.SUPABASE_KEY):
        raise HTTPException(status_code=500, detail="Database not configured")

    headers = {"apikey": settings.SUPABASE_KEY}
    if settings.SUPABASE_SERVICE_ROLE_KEY:
        headers["Authorization"] = f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}"
    elif user_token:
        headers["Authorization"] = f"Bearer {user_token}"

    url = f"{settings.SUPABASE_URL.rstrip('/')}/rest/v1/tailoring_results?run_id=eq.{run_id}&user_id=eq.{user_id}&select=*"
    async with httpx.AsyncClient(timeout=8.0) as client:
        res = await client.get(url, headers=headers)
        if res.status_code != 200 or not res.json():
            raise HTTPException(status_code=404, detail="Tailoring results not found")
        row = res.json()[0]

    tailored_content = row.get("tailored_content") or {}
    changes = tailored_content.get("changes", [])

    # Collect already accepted targets
    accepted_targets = set()
    for chg in changes:
        if chg.get("status") == "accepted":
            t_id = chg.get("target_content_id") or chg.get("slot_id")
            if t_id:
                accepted_targets.add(t_id)

    accepted_count = 0
    for chg in changes:
        if chg.get("status") == "proposed":
            # Strict rule: hide_item and add_item_from_master_profile require explicit individual acceptance
            if chg.get("type") in ("hide_item", "add_item_from_master_profile"):
                continue
            if chg.get("risk_level") == "low":
                t_id = chg.get("target_content_id") or chg.get("slot_id")
                if t_id and t_id in accepted_targets:
                    # Conflict: skip second change on same target
                    continue
                chg["status"] = "accepted"
                accepted_count += 1
                if t_id:
                    accepted_targets.add(t_id)

    accepted = [c for c in changes if c.get("status") == "accepted"]

    # Recompute score_after
    run_url = f"{settings.SUPABASE_URL.rstrip('/')}/rest/v1/pipeline_runs?id=eq.{run_id}&select=resume_id,job_description_id"
    async with httpx.AsyncClient(timeout=8.0) as client:
        r_run = await client.get(run_url, headers=headers)
        resume_id = r_run.json()[0]["resume_id"] if (r_run.status_code == 200 and r_run.json()) else None

    resume_content = {}
    if resume_id:
        res_url = f"{settings.SUPABASE_URL.rstrip('/')}/rest/v1/resumes?id=eq.{resume_id}&select=content"
        async with httpx.AsyncClient(timeout=8.0) as client:
            r_res = await client.get(res_url, headers=headers)
            if r_res.status_code == 200 and r_res.json():
                resume_content = r_res.json()[0].get("content") or {}

    inventory = build_resume_inventory(resume_content)
    scoring_result = compute_match_score(
        inventory=inventory,
        jd=JDAnalysis(
            required_skills=tailored_content.get("matched_keywords", []) + tailored_content.get("missing_keywords", []),
            keywords=tailored_content.get("matched_keywords", []),
        ),
        accepted_changes=accepted,
    )

    new_score_after = scoring_result.estimated_match_score
    tailored_content["score_after"] = new_score_after
    tailored_content["changes"] = changes
    fit_estimate = calculate_live_fit_estimate(changes)

    patch_url = f"{settings.SUPABASE_URL.rstrip('/')}/rest/v1/tailoring_results?id=eq.{row['id']}"
    patch_headers = dict(headers)
    patch_headers["Prefer"] = "return=representation"
    patch_payload = {
        "score_after": new_score_after,
        "tailored_content": tailored_content,
        "updated_at": "now()",
    }

    async with httpx.AsyncClient(timeout=8.0) as client:
        r_patch = await client.patch(patch_url, headers=patch_headers, json=patch_payload)
        if r_patch.status_code not in (200, 204):
            raise HTTPException(status_code=500, detail=f"Failed to update batch tailoring status: {r_patch.text}")

    return {
        "status": "batch_accepted",
        "newly_accepted_count": accepted_count,
        "total_accepted_count": len(accepted),
        "score_before": row.get("score_before"),
        "score_after": new_score_after,
        "live_fit_estimate": fit_estimate,
    }


@router.post("/{run_id}/apply")
async def apply_tailored_changes(
    run_id: str,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Creates a NEW tailored copy of the resume with accepted changes applied.
    The original resume is NEVER modified.
    """
    user_id = current_user.id
    auth_header = request.headers.get("Authorization", "")
    user_token = auth_header.replace("Bearer ", "") if "Bearer " in auth_header else None

    if not (settings.SUPABASE_URL and settings.SUPABASE_KEY):
        raise HTTPException(status_code=500, detail="Database not configured")

    headers = {"apikey": settings.SUPABASE_KEY}
    if settings.SUPABASE_SERVICE_ROLE_KEY:
        headers["Authorization"] = f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}"
    elif user_token:
        headers["Authorization"] = f"Bearer {user_token}"

    url = f"{settings.SUPABASE_URL.rstrip('/')}/rest/v1/tailoring_results?run_id=eq.{run_id}&user_id=eq.{user_id}&select=*"
    async with httpx.AsyncClient(timeout=8.0) as client:
        res = await client.get(url, headers=headers)
        if res.status_code != 200 or not res.json():
            raise HTTPException(status_code=404, detail="Tailoring results not found")
        tailoring_row = res.json()[0]

    run_url = f"{settings.SUPABASE_URL.rstrip('/')}/rest/v1/pipeline_runs?id=eq.{run_id}&select=resume_id"
    async with httpx.AsyncClient(timeout=8.0) as client:
        r_run = await client.get(run_url, headers=headers)
        if r_run.status_code != 200 or not r_run.json():
            raise HTTPException(status_code=404, detail="Pipeline run not found")
        resume_id = r_run.json()[0]["resume_id"]

    res_url = f"{settings.SUPABASE_URL.rstrip('/')}/rest/v1/resumes?id=eq.{resume_id}&select=*"
    async with httpx.AsyncClient(timeout=8.0) as client:
        r_res = await client.get(res_url, headers=headers)
        if r_res.status_code != 200 or not r_res.json():
            raise HTTPException(status_code=404, detail="Original resume not found")
        orig_resume = r_res.json()[0]

    tailored_content_obj = tailoring_row.get("tailored_content") or {}
    changes = tailored_content_obj.get("changes", [])
    accepted = [c for c in changes if c.get("status") == "accepted"]

    new_content = copy.deepcopy(orig_resume.get("content") or {})
    for chg in accepted:
        t_id = chg.get("target_content_id") or chg.get("target_id")
        after_val = chg.get("after") or chg.get("tailored_text")
        if not t_id or after_val is None:
            continue

        for sec in new_content.get("sections", []):
            for item in sec.get("items", []):
                for b in item.get("bullets", []):
                    if isinstance(b, dict) and b.get("id") == t_id:
                        b["text"] = str(after_val)

    new_resume_id = str(uuid.uuid4())
    new_title = f"{orig_resume.get('title', 'Resume')} (Tailored)"
    insert_payload = {
        "id": new_resume_id,
        "user_id": user_id,
        "title": new_title,
        "content": new_content,
        "style": orig_resume.get("style") or {},
        "version": 1,
        "source_type": orig_resume.get("source_type", "editor"),
        "created_at": "now()",
        "updated_at": "now()",
    }

    insert_url = f"{settings.SUPABASE_URL.rstrip('/')}/rest/v1/resumes"
    insert_headers = dict(headers)
    insert_headers["Prefer"] = "return=representation"

    async with httpx.AsyncClient(timeout=8.0) as client:
        r_ins = await client.post(insert_url, headers=insert_headers, json=insert_payload)
        if r_ins.status_code not in (200, 201):
            raise HTTPException(status_code=500, detail=f"Failed to create tailored resume: {r_ins.text}")

    return {
        "status": "applied",
        "original_resume_id": resume_id,
        "new_resume_id": new_resume_id,
        "new_title": new_title,
        "applied_changes_count": len(accepted),
    }
