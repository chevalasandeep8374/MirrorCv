import os
import copy
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, AsyncSessionLocal
from app.models.user import User
from app.models.template import UploadedTemplate
from app.models.tailoring_job import TailoringJob
from app.schemas.content import ResumeContent, BulletItem
from app.schemas.tailoring import ChangeReason
from app.graph.pipeline import tailoring_pipeline_graph
from app.services.fidelity_writer import write_tailored_docx
from app.services.pdf_converter import convert_docx_to_pdf
from app.services.match_scorer import calculate_match_score
from app.schemas.tailoring import JDAnalysis
from app.api.deps import get_current_user

router = APIRouter(prefix="/tailor", tags=["Tailoring"])


class TailorRequest(BaseModel):
    template_id: str
    jd_text: str


class ChangeToggleRequest(BaseModel):
    accepted: bool


async def _execute_pipeline(session: AsyncSession, job_id: str, template_id: str, jd_text: str):
    stmt_t = select(UploadedTemplate).where(UploadedTemplate.id == template_id)
    res_t = await session.execute(stmt_t)
    template = res_t.scalars().first()

    stmt_j = select(TailoringJob).where(TailoringJob.id == job_id)
    res_j = await session.execute(stmt_j)
    job = res_j.scalars().first()

    if not template or not job:
        return

    try:
        job.status = "processing"
        job.progress = 10
        job.current_step = "orchestrating_graph"
        await session.commit()

        initial_state = {
            "job_id": job_id,
            "template_id": template_id,
            "original_docx_path": template.file_path,
            "original_pdf_path": template.pdf_path or "",
            "jd_text": jd_text,
            "fingerprint": template.fingerprint,
            "role_map": template.role_map,
            "content_to_paragraphs": template.content_to_paragraphs,
            "source_content": ResumeContent.model_validate(template.content),
            "source_style": template.style,
        }

        final_state = tailoring_pipeline_graph.invoke(initial_state)

        # Store completed state
        job.status = "completed"
        job.progress = 100
        job.current_step = "completed"
        job.jd_analysis = final_state.get("jd_analysis", {}).model_dump() if hasattr(final_state.get("jd_analysis"), "model_dump") else final_state.get("jd_analysis", {})
        job.tailored_content = final_state.get("tailored_content", {}).model_dump() if hasattr(final_state.get("tailored_content"), "model_dump") else final_state.get("tailored_content", {})
        job.changes = [c.model_dump() if hasattr(c, "model_dump") else c for c in final_state.get("changes", [])]
        job.skills_missing = final_state.get("skills_missing", [])
        job.match_score_before = final_state.get("match_score_before", {}).model_dump() if hasattr(final_state.get("match_score_before"), "model_dump") else final_state.get("match_score_before", {})
        job.match_score_after = final_state.get("match_score_after", {}).model_dump() if hasattr(final_state.get("match_score_after"), "model_dump") else final_state.get("match_score_after", {})
        job.tailored_docx_path = final_state.get("tailored_docx_path")
        job.tailored_pdf_path = final_state.get("tailored_pdf_path")
        job.warnings = final_state.get("warnings", [])

        await session.commit()

    except Exception as exc:
        job.status = "failed"
        job.error = str(exc)
        await session.commit()


async def run_tailoring_pipeline_task(job_id: str, template_id: str, jd_text: str, session: Optional[AsyncSession] = None):
    """Background task executing the LangGraph tailoring pipeline."""
    if session:
        await _execute_pipeline(session, job_id, template_id, jd_text)
    else:
        async with AsyncSessionLocal() as session_ctx:
            await _execute_pipeline(session_ctx, job_id, template_id, jd_text)


@router.post("", status_code=status.HTTP_202_ACCEPTED)
async def create_tailoring_job(
    payload: TailorRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submits a tailoring job with template_id and job description text.

    Runs in the background via LangGraph pipeline.
    """
    if not payload.jd_text or not payload.jd_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job description text cannot be empty.",
        )

    stmt = select(UploadedTemplate).where(
        UploadedTemplate.id == payload.template_id,
        UploadedTemplate.user_id == current_user.id,
    )
    result = await db.execute(stmt)
    template = result.scalars().first()
    if not template:
        raise HTTPException(status_code=404, detail="Uploaded template not found.")

    job = TailoringJob(
        user_id=current_user.id,
        template_id=template.id,
        jd_text=payload.jd_text.strip(),
        status="pending",
        progress=0,
        current_step="queued",
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    # Launch background LangGraph pipeline
    background_tasks.add_task(
        run_tailoring_pipeline_task,
        job_id=job.id,
        template_id=template.id,
        jd_text=job.jd_text,
    )

    return {
        "job_id": job.id,
        "template_id": template.id,
        "status": "pending",
        "message": "Tailoring job started in background.",
    }


@router.get("/{job_id}")
async def get_tailoring_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Polls tailoring job status, tailored content JSON, change list with reasons, and scores."""
    stmt = select(TailoringJob).where(
        TailoringJob.id == job_id, TailoringJob.user_id == current_user.id
    )
    result = await db.execute(stmt)
    job = result.scalars().first()
    if not job:
        raise HTTPException(status_code=404, detail="Tailoring job not found.")

    return {
        "job_id": job.id,
        "template_id": job.template_id,
        "status": job.status,
        "progress": job.progress,
        "current_step": job.current_step,
        "tailored_content": job.tailored_content,
        "changes": job.changes,
        "skills_missing": job.skills_missing,
        "match_score_before": job.match_score_before,
        "match_score_after": job.match_score_after,
        "warnings": job.warnings,
        "error": job.error,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
    }


@router.post("/{job_id}/change/{change_id}")
async def toggle_change(
    job_id: str,
    change_id: str,
    payload: ChangeToggleRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Accepts or rejects an individual change.

    Regenerates the tailored content and updates fidelity DOCX & PDF outputs.
    """
    stmt = select(TailoringJob).where(
        TailoringJob.id == job_id, TailoringJob.user_id == current_user.id
    )
    result = await db.execute(stmt)
    job = result.scalars().first()
    if not job or job.status != "completed":
        raise HTTPException(status_code=404, detail="Completed tailoring job not found.")

    # Find and toggle change
    change_found = False
    for chg in job.changes:
        if chg.get("id") == change_id:
            chg["accepted"] = payload.accepted
            change_found = True
            break

    if not change_found:
        raise HTTPException(status_code=404, detail=f"Change '{change_id}' not found.")

    # Fetch original template to get base content and mappings
    stmt_t = select(UploadedTemplate).where(UploadedTemplate.id == job.template_id)
    res_t = await db.execute(stmt_t)
    template = res_t.scalars().first()

    base_content = ResumeContent.model_validate(template.content)
    new_content = copy.deepcopy(base_content)

    # Re-apply all currently accepted changes onto base content
    for chg in job.changes:
        if chg.get("accepted", True):
            sec_id = chg.get("section_id")
            b_id = chg.get("bullet_id")
            new_text = chg.get("new_text")

            for s in new_content.sections:
                if s.id == sec_id:
                    for item in s.items:
                        for b in item.bullets:
                            if b.id == b_id or (s.type == "summary" and not b_id):
                                b.text = new_text

    job.tailored_content = new_content.model_dump()

    # Regenerate Fidelity DOCX & PDF
    if job.tailored_docx_path and os.path.exists(template.file_path):
        write_tailored_docx(
            template_docx_path=template.file_path,
            tailored_content=new_content,
            content_to_paragraphs=template.content_to_paragraphs,
            output_docx_path=job.tailored_docx_path,
        )
        if job.tailored_pdf_path:
            convert_docx_to_pdf(job.tailored_docx_path, job.tailored_pdf_path)

    # Recompute score
    if job.jd_analysis:
        jd_model = JDAnalysis.model_validate(job.jd_analysis)
        new_score = calculate_match_score(new_content, jd_model)
        job.match_score_after = new_score.model_dump()

    await db.commit()
    return {
        "status": "updated",
        "change_id": change_id,
        "accepted": payload.accepted,
        "match_score_after": job.match_score_after,
    }


@router.get("/{job_id}/docx")
async def download_tailored_docx(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Downloads the fidelity output DOCX."""
    stmt = select(TailoringJob).where(
        TailoringJob.id == job_id, TailoringJob.user_id == current_user.id
    )
    result = await db.execute(stmt)
    job = result.scalars().first()
    if not job or not job.tailored_docx_path or not os.path.exists(job.tailored_docx_path):
        raise HTTPException(status_code=404, detail="Tailored DOCX not found.")

    return FileResponse(
        path=job.tailored_docx_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=f"tailored_resume_{job_id[:8]}.docx",
    )


@router.get("/{job_id}/pdf")
async def download_tailored_pdf(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Downloads the fidelity output PDF."""
    stmt = select(TailoringJob).where(
        TailoringJob.id == job_id, TailoringJob.user_id == current_user.id
    )
    result = await db.execute(stmt)
    job = result.scalars().first()
    if not job or not job.tailored_pdf_path or not os.path.exists(job.tailored_pdf_path):
        raise HTTPException(status_code=404, detail="Tailored PDF not found.")

    return FileResponse(
        path=job.tailored_pdf_path,
        media_type="application/pdf",
        filename=f"tailored_resume_{job_id[:8]}.pdf",
    )


@router.get("/{job_id}/original-pdf")
async def download_original_pdf(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Serves the original uploaded PDF for side-by-side comparison."""
    stmt = select(TailoringJob).where(
        TailoringJob.id == job_id, TailoringJob.user_id == current_user.id
    )
    result = await db.execute(stmt)
    job = result.scalars().first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    stmt_t = select(UploadedTemplate).where(UploadedTemplate.id == job.template_id)
    res_t = await db.execute(stmt_t)
    template = res_t.scalars().first()
    if not template or not template.pdf_path or not os.path.exists(template.pdf_path):
        raise HTTPException(status_code=404, detail="Original PDF not found.")

    return FileResponse(
        path=template.pdf_path,
        media_type="application/pdf",
        filename="original_resume.pdf",
    )
