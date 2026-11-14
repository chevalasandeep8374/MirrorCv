from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.resume import Resume
from app.schemas.resume import ResumeCreate, ResumeUpdate, ResumeDetail, ResumeSummary
from app.schemas.content import ResumeContent
from app.schemas.style import ResumeStyle
from app.services.presets import get_classic_single_column_preset, get_realistic_seed_content
from app.api.deps import get_current_user

router = APIRouter(prefix="/resumes", tags=["Resumes"])


@router.get("", response_model=List[ResumeSummary])
async def list_resumes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all resumes belonging to the authenticated user."""
    stmt = (
        select(Resume)
        .where(Resume.user_id == current_user.id)
        .order_by(Resume.updated_at.desc())
    )
    result = await db.execute(stmt)
    resumes = result.scalars().all()
    return resumes


@router.post("", response_model=ResumeDetail, status_code=status.HTTP_201_CREATED)
async def create_resume(
    payload: ResumeCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new resume, populating default content/style if omitted."""
    content_obj = payload.content or get_realistic_seed_content()
    style_obj = payload.style or get_classic_single_column_preset()

    resume = Resume(
        user_id=current_user.id,
        title=payload.title or "Untitled Resume",
        content=content_obj.model_dump(),
        style=style_obj.model_dump(),
    )
    db.add(resume)
    await db.commit()
    await db.refresh(resume)
    return resume


@router.get("/{resume_id}", response_model=ResumeDetail)
async def get_resume(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Fetch a single resume by ID."""
    stmt = select(Resume).where(
        Resume.id == resume_id, Resume.user_id == current_user.id
    )
    result = await db.execute(stmt)
    resume = result.scalars().first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume '{resume_id}' not found.",
        )
    return resume


@router.put("/{resume_id}", response_model=ResumeDetail)
async def update_resume(
    resume_id: str,
    payload: ResumeUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update resume content, style tokens, and/or title (used by debounced autosave)."""
    stmt = select(Resume).where(
        Resume.id == resume_id, Resume.user_id == current_user.id
    )
    result = await db.execute(stmt)
    resume = result.scalars().first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume '{resume_id}' not found.",
        )

    if payload.title is not None:
        resume.title = payload.title
    if payload.content is not None:
        resume.content = payload.content.model_dump()
    if payload.style is not None:
        resume.style = payload.style.model_dump()

    await db.commit()
    await db.refresh(resume)
    return resume


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a resume."""
    stmt = select(Resume).where(
        Resume.id == resume_id, Resume.user_id == current_user.id
    )
    result = await db.execute(stmt)
    resume = result.scalars().first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume '{resume_id}' not found.",
        )

    await db.delete(resume)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# -----------------------------------------------------------------------------
# JSON Export / Import Endpoints
# -----------------------------------------------------------------------------

@router.get("/{resume_id}/export/content")
async def export_content_json(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Export Content JSON as a downloadable file."""
    stmt = select(Resume).where(
        Resume.id == resume_id, Resume.user_id == current_user.id
    )
    result = await db.execute(stmt)
    resume = result.scalars().first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found"
        )

    content_data = resume.content
    import json
    return Response(
        content=json.dumps(content_data, indent=2),
        media_type="application/json",
        headers={
            "Content-Disposition": f'attachment; filename="resume_{resume_id}_content.json"'
        },
    )


@router.post("/{resume_id}/import/content", response_model=ResumeDetail)
async def import_content_json(
    resume_id: str,
    payload: ResumeContent,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Import and replace Content JSON."""
    stmt = select(Resume).where(
        Resume.id == resume_id, Resume.user_id == current_user.id
    )
    result = await db.execute(stmt)
    resume = result.scalars().first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found"
        )

    resume.content = payload.model_dump()
    await db.commit()
    await db.refresh(resume)
    return resume


@router.get("/{resume_id}/export/style")
async def export_style_json(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Export Style JSON as a downloadable file."""
    stmt = select(Resume).where(
        Resume.id == resume_id, Resume.user_id == current_user.id
    )
    result = await db.execute(stmt)
    resume = result.scalars().first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found"
        )

    import json
    return Response(
        content=json.dumps(resume.style, indent=2),
        media_type="application/json",
        headers={
            "Content-Disposition": f'attachment; filename="resume_{resume_id}_style.json"'
        },
    )


@router.post("/{resume_id}/import/style", response_model=ResumeDetail)
async def import_style_json(
    resume_id: str,
    payload: ResumeStyle,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Import and replace Style JSON."""
    stmt = select(Resume).where(
        Resume.id == resume_id, Resume.user_id == current_user.id
    )
    result = await db.execute(stmt)
    resume = result.scalars().first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found"
        )

    resume.style = payload.model_dump()
    await db.commit()
    await db.refresh(resume)
    return resume


@router.get("/{resume_id}/export/pdf")
async def export_pdf(
    resume_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generates and downloads PDF using Playwright headless Chromium."""
    stmt = select(Resume).where(
        Resume.id == resume_id, Resume.user_id == current_user.id
    )
    result = await db.execute(stmt)
    resume = result.scalars().first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found"
        )

    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "") if "Bearer " in auth_header else ""

    page_size = "A4"
    if isinstance(resume.style, dict):
        page_size = resume.style.get("pageSize", "A4")

    try:
        from app.services.pdf_export import generate_resume_pdf

        pdf_bytes = await generate_resume_pdf(
            resume_id=resume.id,
            page_size=page_size,
            auth_token=token,
        )

        clean_title = "".join(c for c in resume.title.lower() if c.isalnum() or c in (" ", "_", "-")).strip().replace(" ", "_")
        filename = f"{clean_title or 'resume'}_{resume.id[:8]}.pdf"
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF rendering failed: {str(exc)}",
        )

