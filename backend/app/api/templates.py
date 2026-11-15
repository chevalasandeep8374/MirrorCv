"""Template Management API Endpoints for MirrorCV (Phase B1: DOCX Template Guardian).
Handles secure DOCX template intake, storage in Supabase 'originals' bucket,
deterministic template profiling, slot building, fidelity evaluation,
and slot correction overrides with strict user data isolation.
"""

import os
import shutil
import uuid
import logging
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Body, Query, status, Request
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import httpx

from app.database import get_db
from app.models.user import User
from app.models.template import UploadedTemplate
from app.config import settings
from app.api.deps import get_current_user, CurrentUser
from app.services.docx_validator import validate_docx_bytes
from app.services.docx_fingerprint import fingerprint_docx
from app.services.role_classifier import classify_paragraphs
from app.services.content_extractor import extract_content_and_style
from app.services.docx_slot_builder import build_template_profile
from app.services.fidelity_writer import write_tailored_docx
from app.services.fit_checker import evaluate_fidelity
from app.services.pdf_converter import convert_docx_to_pdf

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/templates", tags=["Templates"])

UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)


async def _save_to_supabase_storage(
    user_id: str,
    resume_id: str,
    file_bytes: bytes,
    file_name: str = "original.docx",
    user_token: Optional[str] = None,
) -> str:
    """Uploads file to Supabase storage bucket 'originals/{user_id}/{resume_id}/{file_name}'."""
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        return f"local://originals/{user_id}/{resume_id}/{file_name}"

    storage_path = f"{user_id}/{resume_id}/{file_name}"
    url = f"{settings.SUPABASE_URL.rstrip('/')}/storage/v1/object/originals/{storage_path}"
    auth_bearer = user_token or settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_KEY
    headers = {
        "apikey": settings.SUPABASE_KEY,
        "Authorization": f"Bearer {auth_bearer}",
        "Content-Type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "x-upsert": "true",
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, headers=headers, content=file_bytes)
            if resp.status_code in (200, 201):
                logger.info(f"Uploaded original DOCX to Supabase storage at {storage_path}")
            else:
                logger.warning(f"Supabase storage upload returned status {resp.status_code}: {resp.text}")
    except Exception as e:
        logger.warning(f"Could not upload to Supabase storage: {e}")

    return storage_path


async def _save_template_profile_to_supabase(
    template_profile_id: str,
    user_id: str,
    resume_id: str,
    profile_data: Dict[str, Any],
    slot_map_data: Dict[str, Any],
    fidelity_score: float,
    user_token: Optional[str] = None,
) -> None:
    """Saves template profile directly to public.template_profiles using user JWT or backend credentials."""
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        return

    url = f"{settings.SUPABASE_URL.rstrip('/')}/rest/v1/template_profiles"
    auth_bearer = user_token or settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_KEY
    headers = {
        "apikey": settings.SUPABASE_KEY,
        "Authorization": f"Bearer {auth_bearer}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates",
    }
    payload = {
        "id": template_profile_id,
        "user_id": user_id,
        "resume_id": resume_id,
        "version": 1,
        "profile": profile_data,
        "slot_map": slot_map_data,
        "fidelity_score": fidelity_score,
        "status": "ready",
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code not in (200, 201):
                logger.warning(f"Failed to save template profile in Supabase: {resp.text}")
    except Exception as e:
        logger.warning(f"Error saving template profile: {e}")


async def _save_resume_row_to_supabase(
    resume_id: str,
    user_id: str,
    title: str,
    content: Dict[str, Any],
    style: Dict[str, Any],
    template_profile_id: str,
    user_token: Optional[str] = None,
) -> None:
    """Inserts a row into public.resumes with source_type='uploaded_docx'."""
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        return

    url = f"{settings.SUPABASE_URL.rstrip('/')}/rest/v1/resumes"
    auth_bearer = user_token or settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_KEY
    headers = {
        "apikey": settings.SUPABASE_KEY,
        "Authorization": f"Bearer {auth_bearer}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }
    payload = {
        "id": resume_id,
        "user_id": user_id,
        "title": title,
        "content": content,
        "style": style,
        "template_id": f"uploaded:{template_profile_id}",
        "source_type": "uploaded_docx",
        "version": 1,
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code not in (200, 201):
                logger.warning(f"Failed to insert resume row in Supabase: {resp.text}")
    except Exception as e:
        logger.warning(f"Error inserting resume in Supabase: {e}")


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_template(
    file: UploadFile = File(...),
    request: Request = None,
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Securely uploads and validates a DOCX resume, runs Agent 1 (Template Guardian)

    deterministic analysis, evaluates fidelity, and stores template profile and resume.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided in upload.",
        )

    # 1. Enforce DOCX-only validation with safety checks (Change #6: hardened parser, zip-bomb, macros)
    contents = await file.read()
    validate_docx_bytes(contents, file.filename)

    user_id = str(current_user.id)
    auth_header = request.headers.get("Authorization", "") if request else ""
    user_token = auth_header.replace("Bearer ", "") if "Bearer " in auth_header else None

    resume_id = str(uuid.uuid4())
    template_profile_id = str(uuid.uuid4())

    # 2. Save working copy to local cache
    work_dir = os.path.join(UPLOAD_DIR, template_profile_id)
    os.makedirs(work_dir, exist_ok=True)
    orig_docx_path = os.path.join(work_dir, "original.docx")
    regen_docx_path = os.path.join(work_dir, "regenerated.docx")
    orig_pdf_path = os.path.join(work_dir, "original.pdf")
    regen_pdf_path = os.path.join(work_dir, "regenerated.pdf")

    with open(orig_docx_path, "wb") as f:
        f.write(contents)

    # 3. Store untouched original in Supabase storage: originals/{user_id}/{resume_id}/original.docx
    storage_path = await _save_to_supabase_storage(user_id, resume_id, contents, "original.docx", user_token=user_token)

    # 4. Deterministic Analysis Pipeline (Agent 1: Template Guardian)
    try:
        fp = fingerprint_docx(orig_docx_path)
    except Exception as exc:
        shutil.rmtree(work_dir, ignore_errors=True)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse DOCX structure: {str(exc)}",
        )

    role_map = classify_paragraphs(fp)
    if not role_map.sections_hierarchy:
        shutil.rmtree(work_dir, ignore_errors=True)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The uploaded resume has no recognizable sections (Experience, Skills, Education, etc.). Please check formatting.",
        )

    content, style, c_to_p = extract_content_and_style(
        fingerprint=fp,
        role_map=role_map,
        template_profile_id=template_profile_id,
    )

    # 5. Build Template Profile & Slot Map (Schema 1.1.0)
    profile = build_template_profile(
        docx_path=orig_docx_path,
        fingerprint=fp,
        role_map=role_map,
        template_profile_id=template_profile_id,
        resume_id=resume_id,
        page_count=1,
    )

    # 6. Prove Fidelity: No-Op Regeneration Test
    write_tailored_docx(
        template_docx_path=orig_docx_path,
        tailored_content=content,
        content_to_paragraphs=c_to_p,
        output_docx_path=regen_docx_path,
    )

    fidelity_score, fidelity_metrics, fidelity_warnings = evaluate_fidelity(orig_docx_path, regen_docx_path)

    profile.fidelity_score = fidelity_score
    profile.fidelity_metrics = fidelity_metrics
    if fidelity_warnings:
        profile.warnings.extend(fidelity_warnings)

    profile_dict = profile.model_dump(mode="json")
    slot_map_dict = {k: v.model_dump(mode="json") for k, v in profile.slot_map.items()}

    # 7. Persist to Supabase: save resume row first (satisfies foreign key constraint), then template profile
    title = f"{content.header.name or 'Imported'} Resume"
    await _save_resume_row_to_supabase(
        resume_id=resume_id,
        user_id=user_id,
        title=title,
        content=content.model_dump(),
        style=style.model_dump(),
        template_profile_id=template_profile_id,
        user_token=user_token,
    )

    await _save_template_profile_to_supabase(
        template_profile_id=template_profile_id,
        user_id=user_id,
        resume_id=resume_id,
        profile_data=profile_dict,
        slot_map_data=slot_map_dict,
        fidelity_score=fidelity_score,
        user_token=user_token,
    )

    # 8. Local SQLite fallback persistence for development
    fp_dict = fp.model_dump()
    fp_dict["template_type"] = "docx"
    fp_dict["template_profile_id"] = template_profile_id
    fp_dict["fidelity_score"] = fidelity_score
    fp_dict["fidelity_metrics"] = fidelity_metrics.model_dump()
    fp_dict["font_report"] = [f.model_dump() for f in profile.font_report]

    template_record = UploadedTemplate(
        id=template_profile_id,
        user_id=user_id,
        original_filename=file.filename,
        file_path=orig_docx_path,
        pdf_path=orig_pdf_path,
        fingerprint=fp_dict,
        role_map=role_map.model_dump(),
        content=content.model_dump(),
        style=style.model_dump(),
        content_to_paragraphs=c_to_p,
    )
    db.add(template_record)
    try:
        await db.commit()
    except Exception as e:
        logger.debug(f"SQLite template persistence notice: {e}")

    return {
        "id": template_profile_id,
        "resume_id": resume_id,
        "filename": file.filename,
        "template_type": "docx",
        "fidelity_score": fidelity_score,
        "fidelity_metrics": fidelity_metrics.model_dump(),
        "page_count_match": fidelity_metrics.page_count_match,
        "font_report": [f.model_dump() for f in profile.font_report],
        "sections_detected": [s.title for s in role_map.sections_hierarchy],
        "slots_count": len(profile.slots),
        "warnings": profile.warnings,
        "storage_path": storage_path,
    }


@router.get("/{template_id}/analysis")
async def get_template_analysis(
    template_id: str,
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns the TemplateProfile analysis including slots, font report, and fidelity metrics."""
    user_id = str(current_user.id)

    # 1. Check Supabase template_profiles first
    if settings.SUPABASE_URL and settings.SUPABASE_KEY:
        url = f"{settings.SUPABASE_URL.rstrip('/')}/rest/v1/template_profiles?id=eq.{template_id}&select=*"
        headers = {
            "apikey": settings.SUPABASE_KEY,
            "Authorization": f"Bearer {settings.SUPABASE_KEY}",
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, headers=headers)
                if resp.status_code == 200:
                    rows = resp.json()
                    if rows:
                        row = rows[0]
                        # Verify ownership
                        if str(row.get("user_id")) != user_id:
                            raise HTTPException(status_code=403, detail="Access denied: unauthorized template access")
                        return {
                            "id": row.get("id"),
                            "resume_id": row.get("resume_id"),
                            "profile": row.get("profile"),
                            "slot_map": row.get("slot_map"),
                            "fidelity_score": float(row.get("fidelity_score") or 100.0),
                            "status": row.get("status"),
                        }
        except HTTPException:
            raise
        except Exception as e:
            logger.debug(f"Supabase lookup notice: {e}")

    # 2. SQLite fallback
    stmt = select(UploadedTemplate).where(UploadedTemplate.id == template_id)
    result = await db.execute(stmt)
    template = result.scalars().first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    if str(template.user_id) != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    fp = template.fingerprint or {}
    return {
        "id": template.id,
        "filename": template.original_filename,
        "template_type": fp.get("template_type", "docx"),
        "fingerprint": fp,
        "role_map": template.role_map,
        "content": template.content,
        "style": template.style,
        "fidelity_score": fp.get("fidelity_score", 100.0),
        "fidelity_metrics": fp.get("fidelity_metrics"),
        "font_report": fp.get("font_report", []),
    }


@router.get("/{template_id}/preview")
async def get_template_preview_pdf(
    template_id: str,
    preview_type: str = Query("regenerated", alias="type"),
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Serves the original or regenerated PDF preview for side-by-side comparison."""
    user_id = str(current_user.id)
    work_dir = os.path.join(UPLOAD_DIR, template_id)

    pdf_filename = "original.pdf" if preview_type == "original" else "regenerated.pdf"
    docx_filename = "original.docx" if preview_type == "original" else "regenerated.docx"

    pdf_path = os.path.join(work_dir, pdf_filename)
    docx_path = os.path.join(work_dir, docx_filename)

    if not os.path.exists(pdf_path) and os.path.exists(docx_path):
        convert_docx_to_pdf(docx_path, pdf_path)

    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail=f"Preview PDF ({preview_type}) not found")

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=f"{template_id}_{preview_type}.pdf",
    )


@router.patch("/{template_id}/slots/{slot_id}")
async def update_template_slot(
    template_id: str,
    slot_id: str,
    payload: Dict[str, Any] = Body(...),
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Allows user override of a slot's role or binds target with ownership check."""
    user_id = str(current_user.id)
    new_role = payload.get("role")
    new_binds = payload.get("binds")

    if not new_role and not new_binds:
        raise HTTPException(status_code=400, detail="Nothing to update: provide 'role' or 'binds'")

    supabase_updated = False
    if settings.SUPABASE_URL and settings.SUPABASE_KEY:
        get_url = f"{settings.SUPABASE_URL.rstrip('/')}/rest/v1/template_profiles?id=eq.{template_id}&user_id=eq.{user_id}&select=*"
        headers = {
            "apikey": settings.SUPABASE_KEY,
            "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_KEY}",
            "Content-Type": "application/json",
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(get_url, headers=headers)
                if res.status_code == 200 and res.json():
                    row = res.json()[0]
                    profile = row.get("profile") or {}
                    slot_map = row.get("slot_map") or {}
                    slots = profile.get("slots") or []
                    found = False
                    for s in slots:
                        if s.get("slot_id") == slot_id:
                            if new_role:
                                s["role"] = new_role
                            if new_binds:
                                s["binds"] = [new_binds]
                            found = True
                            break
                    if new_binds and slot_id in slot_map:
                        slot_map[slot_id]["target_field"] = new_binds

                    patch_url = f"{settings.SUPABASE_URL.rstrip('/')}/rest/v1/template_profiles?id=eq.{template_id}&user_id=eq.{user_id}"
                    patch_headers = dict(headers)
                    patch_headers["Prefer"] = "return=representation"
                    patch_res = await client.patch(patch_url, headers=patch_headers, json={"profile": profile, "slot_map": slot_map})
                    if patch_res.status_code in (200, 204):
                        supabase_updated = True
        except Exception as e:
            logger.warning(f"Error updating template profile in Supabase: {e}")

    # Also update in local database if present
    stmt = select(UploadedTemplate).where(UploadedTemplate.id == template_id)
    result = await db.execute(stmt)
    template = result.scalars().first()
    if template:
        if str(template.user_id) != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        fp = template.fingerprint or {}
        # update role map in template
        if template.role_map and "paragraph_roles" in template.role_map:
            # find slot paragraph index
            p_idx_str = slot_id.replace("slot_", "")
            if p_idx_str in template.role_map["paragraph_roles"]:
                if new_role:
                    template.role_map["paragraph_roles"][p_idx_str]["role"] = new_role
                if new_binds:
                    template.role_map["paragraph_roles"][p_idx_str]["field"] = new_binds
        await db.commit()

    if not supabase_updated and not template:
        raise HTTPException(status_code=404, detail="Template or slot not found")

    return {
        "message": f"Slot {slot_id} updated successfully",
        "slot_id": slot_id,
        "role": new_role,
        "binds": new_binds,
    }


@router.post("/{template_id}/reanalyze")
async def reanalyze_template(
    template_id: str,
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Re-analyzes the template and re-computes fidelity metrics."""
    user_id = str(current_user.id)
    work_dir = os.path.join(UPLOAD_DIR, template_id)
    orig_docx = os.path.join(work_dir, "original.docx")
    regen_docx = os.path.join(work_dir, "regenerated.docx")

    if not os.path.exists(orig_docx):
        raise HTTPException(status_code=404, detail="Template files not found")

    fp = fingerprint_docx(orig_docx)
    role_map = classify_paragraphs(fp)
    content, style, c_to_p = extract_content_and_style(fp, role_map, template_id)

    profile = build_template_profile(
        docx_path=orig_docx,
        fingerprint=fp,
        role_map=role_map,
        template_profile_id=template_id,
    )

    write_tailored_docx(orig_docx, content, c_to_p, regen_docx)
    fidelity_score, metrics, warnings = evaluate_fidelity(orig_docx, regen_docx)

    profile.fidelity_score = fidelity_score
    profile.fidelity_metrics = metrics

    return {
        "id": template_id,
        "fidelity_score": fidelity_score,
        "fidelity_metrics": metrics.model_dump(),
        "slots_count": len(profile.slots),
        "warnings": warnings,
    }


@router.post("/{template_id}/fonts")
async def upload_font_file(
    template_id: str,
    file: UploadFile = File(...),
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Accepts a custom TTF or OTF font file to resolve a substituted font (Change #9)."""
    if not file.filename or not file.filename.lower().endswith((".ttf", ".otf")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only TrueType (.ttf) or OpenType (.otf) font files are supported.",
        )

    fonts_dir = os.path.join(UPLOAD_DIR, f"{template_id}_fonts")
    os.makedirs(fonts_dir, exist_ok=True)
    saved_font_path = os.path.join(fonts_dir, file.filename)

    contents = await file.read()
    with open(saved_font_path, "wb") as f:
        f.write(contents)

    return {
        "message": f"Font '{file.filename}' uploaded successfully.",
        "font_path": saved_font_path,
    }
