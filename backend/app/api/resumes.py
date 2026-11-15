import copy
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, Query
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.resume import Resume
from app.models.template import UploadedTemplate
from app.schemas.resume import (
    ResumeCreate,
    ResumeUpdate,
    ResumePatch,
    ResumeDetail,
    ResumeSummary,
)
from app.schemas.content import ResumeContent
from app.schemas.style import ResumeStyle
from app.schemas.cover_letter import CoverLetterGenerateRequest, CoverLetterGenerateResponse
from app.services.cover_letter_service import generate_cover_letter_draft
from app.services.presets import get_classic_single_column_preset, get_realistic_seed_content
from app.api.deps import get_current_user

router = APIRouter(prefix="/resumes", tags=["Resumes"])


@router.get("", response_model=List[ResumeSummary])
async def list_resumes(
    doc_type: Optional[str] = Query("resume", description="Document type: resume or cover_letter"),
    folder: Optional[str] = Query(None, description="Filter by folder name"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    is_archived: bool = Query(False, description="Filter by archived status"),
    search: Optional[str] = Query(None, description="Search by title or target job title"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List resumes / documents belonging to the authenticated user with filtering."""
    query = select(Resume).where(
        Resume.user_id == current_user.id,
        Resume.is_archived == is_archived,
    )

    if doc_type:
        query = query.where(Resume.doc_type == doc_type)
    if folder:
        query = query.where(Resume.folder == folder)
    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.where(
            or_(
                Resume.title.ilike(term),
                Resume.target_job_title.ilike(term),
            )
        )

    query = query.order_by(Resume.updated_at.desc())
    result = await db.execute(query)
    resumes = result.scalars().all()

    # Filter in-memory for JSON tags if tag requested
    if tag and tag.strip():
        tag_lower = tag.strip().lower()
        resumes = [
            r for r in resumes
            if isinstance(r.tags, list) and any(str(t).lower() == tag_lower for t in r.tags)
        ]

    # Preload parent titles for tailored-from badges
    parent_ids = [r.tailored_from_id for r in resumes if r.tailored_from_id]
    parent_map = {}
    if parent_ids:
        p_stmt = select(Resume.id, Resume.title).where(Resume.id.in_(parent_ids))
        p_res = await db.execute(p_stmt)
        parent_map = {row[0]: row[1] for row in p_res.fetchall()}

    summaries = []
    for r in resumes:
        summary_dict = {
            "id": r.id,
            "user_id": r.user_id,
            "title": r.title,
            "doc_type": r.doc_type,
            "target_job_title": r.target_job_title,
            "tags": r.tags or [],
            "folder": r.folder,
            "is_archived": r.is_archived,
            "tailored_from_id": r.tailored_from_id,
            "tailored_from_title": parent_map.get(r.tailored_from_id),
            "thumbnail_path": r.thumbnail_path,
            "created_at": r.created_at,
            "updated_at": r.updated_at,
        }
        summaries.append(ResumeSummary.model_validate(summary_dict))

    return summaries


@router.post("", response_model=ResumeDetail, status_code=status.HTTP_201_CREATED)
async def create_resume(
    payload: ResumeCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new resume or cover letter."""
    content_obj = payload.content or get_realistic_seed_content()
    style_obj = payload.style or get_classic_single_column_preset()

    resume = Resume(
        user_id=current_user.id,
        title=payload.title or "Untitled Resume",
        doc_type=payload.doc_type or "resume",
        target_job_title=payload.target_job_title,
        tags=payload.tags or [],
        folder=payload.folder,
        content=content_obj.model_dump(),
        style=style_obj.model_dump(),
    )
    db.add(resume)
    await db.commit()
    await db.refresh(resume)
    return resume


@router.get("/meta/folders")
async def list_user_folders(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns unique folder names for the current user."""
    stmt = (
        select(Resume.folder)
        .where(Resume.user_id == current_user.id, Resume.folder.isnot(None))
        .distinct()
    )
    res = await db.execute(stmt)
    folders = [f[0] for f in res.fetchall() if f[0]]
    return {"folders": sorted(folders)}


@router.get("/meta/tags")
async def list_user_tags(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns unique tags for the current user."""
    stmt = select(Resume.tags).where(Resume.user_id == current_user.id)
    res = await db.execute(stmt)
    tag_set = set()
    for row in res.fetchall():
        if isinstance(row[0], list):
            for t in row[0]:
                if t:
                    tag_set.add(str(t).strip())
    return {"tags": sorted(list(tag_set))}


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

    # Fetch parent title if tailored
    tailored_title = None
    if resume.tailored_from_id:
        p_stmt = select(Resume.title).where(Resume.id == resume.tailored_from_id)
        p_res = await db.execute(p_stmt)
        p_val = p_res.scalars().first()
        if p_val:
            tailored_title = p_val

    detail_dict = {
        "id": resume.id,
        "user_id": resume.user_id,
        "title": resume.title,
        "doc_type": resume.doc_type,
        "target_job_title": resume.target_job_title,
        "tags": resume.tags or [],
        "folder": resume.folder,
        "is_archived": resume.is_archived,
        "tailored_from_id": resume.tailored_from_id,
        "tailored_from_title": tailored_title,
        "linked_resume_id": resume.linked_resume_id,
        "thumbnail_path": resume.thumbnail_path,
        "content": resume.content,
        "style": resume.style,
        "created_at": resume.created_at,
        "updated_at": resume.updated_at,
    }
    return ResumeDetail.model_validate(detail_dict)


@router.patch("/{resume_id}", response_model=ResumeDetail)
async def patch_resume(
    resume_id: str,
    payload: ResumePatch,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Partially update resume metadata (title, target_job_title, tags, folder, archive status)."""
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
        resume.title = payload.title.strip()
    if payload.target_job_title is not None:
        resume.target_job_title = payload.target_job_title.strip() or None
    if payload.tags is not None:
        resume.tags = payload.tags
    if payload.folder is not None:
        resume.folder = payload.folder.strip() or None
    if payload.is_archived is not None:
        resume.is_archived = payload.is_archived

    await db.commit()
    await db.refresh(resume)
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
    if payload.target_job_title is not None:
        resume.target_job_title = payload.target_job_title
    if payload.tags is not None:
        resume.tags = payload.tags
    if payload.folder is not None:
        resume.folder = payload.folder
    if payload.is_archived is not None:
        resume.is_archived = payload.is_archived
    if payload.content is not None:
        resume.content = payload.content.model_dump()
    if payload.style is not None:
        resume.style = payload.style.model_dump()

    await db.commit()
    await db.refresh(resume)
    return resume


@router.post("/{resume_id}/duplicate", response_model=ResumeDetail, status_code=status.HTTP_201_CREATED)
async def duplicate_resume(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Duplicates an existing resume with all content and style tokens."""
    stmt = select(Resume).where(
        Resume.id == resume_id, Resume.user_id == current_user.id
    )
    result = await db.execute(stmt)
    source = result.scalars().first()
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume '{resume_id}' not found.",
        )

    new_resume = Resume(
        user_id=current_user.id,
        title=f"{source.title} (Copy)",
        doc_type=source.doc_type,
        target_job_title=source.target_job_title,
        tags=copy.deepcopy(source.tags or []),
        folder=source.folder,
        content=copy.deepcopy(source.content),
        style=copy.deepcopy(source.style),
        tailored_from_id=source.tailored_from_id,
    )
    db.add(new_resume)
    await db.commit()
    await db.refresh(new_resume)
    return new_resume


@router.post("/{resume_id}/archive")
async def archive_resume(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Archives a resume."""
    stmt = select(Resume).where(
        Resume.id == resume_id, Resume.user_id == current_user.id
    )
    result = await db.execute(stmt)
    resume = result.scalars().first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    resume.is_archived = True
    await db.commit()
    return {"status": "archived", "id": resume.id}


@router.post("/{resume_id}/unarchive")
async def unarchive_resume(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Unarchives a resume."""
    stmt = select(Resume).where(
        Resume.id == resume_id, Resume.user_id == current_user.id
    )
    result = await db.execute(stmt)
    resume = result.scalars().first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    resume.is_archived = False
    await db.commit()
    return {"status": "unarchived", "id": resume.id}


@router.post("/{resume_id}/tailor-jump")
async def tailor_jump(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Bridges an editor resume into Phase 2 tailoring as a master template."""
    stmt = select(Resume).where(
        Resume.id == resume_id, Resume.user_id == current_user.id
    )
    result = await db.execute(stmt)
    resume = result.scalars().first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    template = UploadedTemplate(
        user_id=current_user.id,
        original_filename=f"{resume.title}.pdf",
        file_path="",
        pdf_path="",
        fingerprint={"template_type": "editor", "source_resume_id": resume.id},
        role_map={},
        content_to_paragraphs={},
        content=resume.content,
        style=resume.style,
    )
    db.add(template)
    await db.commit()
    await db.refresh(template)

    return {
        "status": "ready",
        "template_id": template.id,
        "resume_id": resume.id,
        "title": resume.title,
    }


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

    import json
    return Response(
        content=json.dumps(resume.content, indent=2),
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


@router.get("/{resume_id}/render-data")
async def get_render_data(
    resume_id: str,
    render_token: str = Query(..., description="Short-lived, single-use render token"),
    db: AsyncSession = Depends(get_db),
):
    """Returns resume content and style for headless Playwright PDF export.
    Protected by short-lived (60s), single-use render token without exposing user credentials.
    """
    import httpx
    from app.config import settings
    from app.services.render_tokens import validate_and_consume_render_token

    token_meta = validate_and_consume_render_token(render_token, resume_id)
    if not token_meta:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid, expired, or already consumed render token",
        )

    user_id = token_meta["user_id"]

    # 1. Check SQLite
    resume = None
    try:
        stmt = select(Resume).where(
            Resume.id == resume_id, Resume.user_id == user_id
        )
        result = await db.execute(stmt)
        resume = result.scalars().first()
        if resume:
            return {
                "id": resume.id,
                "title": resume.title,
                "content": resume.content,
                "style": resume.style,
            }
    except Exception:
        pass

    # 2. Check Supabase
    if settings.SUPABASE_URL and settings.SUPABASE_KEY:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                headers = {"apikey": settings.SUPABASE_KEY}
                if settings.SUPABASE_SERVICE_ROLE_KEY:
                    headers["Authorization"] = f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}"
                resp = await client.get(
                    f"{settings.SUPABASE_URL.rstrip('/')}/rest/v1/resumes?id=eq.{resume_id}&select=*",
                    headers=headers,
                )
                if resp.status_code == 200 and resp.json():
                    row = resp.json()[0]
                    if row.get("user_id") == user_id:
                        return {
                            "id": row["id"],
                            "title": row["title"],
                            "content": row["content"],
                            "style": row["style"],
                        }
        except Exception as e:
            pass

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Resume not found",
    )


@router.get("/{resume_id}/export/pdf")
async def export_pdf(
    resume_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generates and downloads PDF using Playwright headless Chromium with short-lived render token."""
    import httpx
    from app.config import settings
    from app.services.render_tokens import create_render_token

    # 1. Lookup in SQLite
    stmt = select(Resume).where(
        Resume.id == resume_id, Resume.user_id == current_user.id
    )
    result = await db.execute(stmt)
    resume = result.scalars().first()

    # 2. Lookup in Supabase if not in SQLite
    if not resume and settings.SUPABASE_URL and settings.SUPABASE_KEY:
        auth_header = request.headers.get("Authorization", "")
        token = auth_header.replace("Bearer ", "") if "Bearer " in auth_header else ""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                headers = {"apikey": settings.SUPABASE_KEY}
                if token:
                    headers["Authorization"] = f"Bearer {token}"
                elif settings.SUPABASE_SERVICE_ROLE_KEY:
                    headers["Authorization"] = f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}"
                resp = await client.get(
                    f"{settings.SUPABASE_URL.rstrip('/')}/rest/v1/resumes?id=eq.{resume_id}&select=*",
                    headers=headers,
                )
                if resp.status_code == 200 and resp.json():
                    row = resp.json()[0]
                    if row.get("user_id") == current_user.id:
                        class ResumeShim:
                            def __init__(self, d):
                                self.id = d["id"]
                                self.title = d["title"]
                                self.content = d.get("content") or {}
                                self.style = d.get("style") or {}
                                self.user_id = d["user_id"]
                        resume = ResumeShim(row)
        except Exception:
            pass

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found"
        )

    page_size = "A4"
    if isinstance(resume.style, dict):
        page_size = resume.style.get("pageSize", "A4")

    try:
        from app.services.pdf_export import generate_resume_pdf

        # Generate short-lived (60s), single-use render token
        render_token = create_render_token(resume_id=resume.id, user_id=current_user.id, ttl_seconds=60)

        pdf_bytes = await generate_resume_pdf(
            resume_id=resume.id,
            page_size=page_size,
            render_token=render_token,
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


@router.post("/{resume_id}/generate-cover-letter", response_model=CoverLetterGenerateResponse)
async def generate_cover_letter_from_resume(
    resume_id: str,
    payload: CoverLetterGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generates a cover letter strictly grounded in facts from the source resume.
    Creates a new document with doc_type='cover_letter' sharing the resume's exact style tokens and fonts.
    """
    stmt = select(Resume).where(
        Resume.id == resume_id, Resume.user_id == current_user.id
    )
    result = await db.execute(stmt)
    source_resume = result.scalars().first()
    if not source_resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Source resume not found"
        )

    # Validate source content
    raw_content = source_resume.content or {}
    try:
        parsed_content = ResumeContent.model_validate(raw_content)
    except Exception:
        parsed_content = get_realistic_seed_content()

    # Generate draft using fact-verifier
    draft = generate_cover_letter_draft(parsed_content, payload)

    company_label = payload.company_name or "Target Job"
    cl_title = f"Cover Letter – {company_label}"

    # Package as full document content with coverLetter field
    doc_content = {
        "header": parsed_content.header.model_dump(),
        "sections": [],
        "coverLetter": draft.model_dump(),
    }

    # Inherit source resume's style tokens
    doc_style = source_resume.style or get_classic_single_column_preset().model_dump()

    new_cover_letter_doc = Resume(
        user_id=current_user.id,
        title=cl_title,
        doc_type="cover_letter",
        target_job_title=payload.job_title or source_resume.target_job_title or "",
        linked_resume_id=source_resume.id,
        content=doc_content,
        style=doc_style,
    )

    db.add(new_cover_letter_doc)
    await db.commit()
    await db.refresh(new_cover_letter_doc)

    return CoverLetterGenerateResponse(
        document_id=new_cover_letter_doc.id,
        title=new_cover_letter_doc.title,
        cover_letter=draft,
        linked_resume_id=source_resume.id,
    )
