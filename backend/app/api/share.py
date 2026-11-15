import secrets
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Header, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.database import get_db
from app.models.resume import Document
from app.models.share import ShareLink, ShareView
from app.models.user import User
from app.services.auth import hash_password, verify_password
from app.api.deps import get_current_user
from app.schemas.share import (
    ShareLinkConfig,
    ShareLinkResponse,
    PublicResumeResponse,
)

router = APIRouter(tags=["share"])


async def _get_owned_resume(resume_id: str, user: User, db: AsyncSession) -> Document:
    result = await db.execute(select(Document).where(Document.id == resume_id))
    resume = result.scalars().first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found"
        )
    if resume.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )
    return resume


@router.get("/resumes/{resume_id}/share", response_model=ShareLinkResponse)
async def get_share_settings(
    resume_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves current sharing configuration and analytics for the resume."""
    await _get_owned_resume(resume_id, user, db)

    result = await db.execute(
        select(ShareLink).where(ShareLink.document_id == resume_id)
    )
    link = result.scalars().first()

    if not link:
        # Create initial share link with default settings
        slug = secrets.token_urlsafe(12)
        link = ShareLink(
            document_id=resume_id,
            slug=slug,
            is_active=False,
            allow_pdf_download=True,
            no_index=True,
        )
        db.add(link)
        await db.commit()
        await db.refresh(link)

    # Get view statistics
    v_count_res = await db.execute(
        select(func.count(ShareView.id)).where(ShareView.share_link_id == link.id)
    )
    view_count = v_count_res.scalar() or 0

    last_v_res = await db.execute(
        select(func.max(ShareView.viewed_at)).where(ShareView.share_link_id == link.id)
    )
    last_viewed_at = last_v_res.scalar()

    return ShareLinkResponse(
        id=link.id,
        document_id=link.document_id,
        slug=link.slug,
        is_active=link.is_active,
        has_password=bool(link.password_hash),
        expires_at=link.expires_at,
        allow_pdf_download=link.allow_pdf_download,
        no_index=link.no_index,
        view_count=view_count,
        last_viewed_at=last_viewed_at,
        share_url=f"/p/{link.slug}",
    )


@router.post("/resumes/{resume_id}/share", response_model=ShareLinkResponse)
async def update_share_settings(
    resume_id: str,
    config: ShareLinkConfig,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Configures public sharing (toggle, password, expiry, pdf download, noindex)."""
    await _get_owned_resume(resume_id, user, db)

    result = await db.execute(
        select(ShareLink).where(ShareLink.document_id == resume_id)
    )
    link = result.scalars().first()

    if not link:
        slug = secrets.token_urlsafe(12)
        link = ShareLink(
            document_id=resume_id,
            slug=slug,
        )
        db.add(link)

    link.is_active = config.is_active
    link.allow_pdf_download = config.allow_pdf_download
    link.no_index = config.no_index
    link.expires_at = config.expires_at

    # Password management
    if config.password is not None:
        if config.password.strip():
            link.password_hash = hash_password(config.password.strip())
        else:
            link.password_hash = None

    await db.commit()
    await db.refresh(link)

    # Get stats
    v_count_res = await db.execute(
        select(func.count(ShareView.id)).where(ShareView.share_link_id == link.id)
    )
    view_count = v_count_res.scalar() or 0

    last_v_res = await db.execute(
        select(func.max(ShareView.viewed_at)).where(ShareView.share_link_id == link.id)
    )
    last_viewed_at = last_v_res.scalar()

    return ShareLinkResponse(
        id=link.id,
        document_id=link.document_id,
        slug=link.slug,
        is_active=link.is_active,
        has_password=bool(link.password_hash),
        expires_at=link.expires_at,
        allow_pdf_download=link.allow_pdf_download,
        no_index=link.no_index,
        view_count=view_count,
        last_viewed_at=last_viewed_at,
        share_url=f"/p/{link.slug}",
    )


@router.get("/public/resumes/{slug}", response_model=PublicResumeResponse)
async def get_public_resume(
    slug: str,
    request: Request,
    response: Response,
    x_share_password: Optional[str] = Header(None, alias="X-Share-Password"),
    db: AsyncSession = Depends(get_db),
):
    """
    Public read-only endpoint for viewing shared resumes.
    Sets X-Robots-Tag: noindex if no_index is enabled.
    """
    result = await db.execute(
        select(ShareLink).where(ShareLink.slug == slug)
    )
    link = result.scalars().first()

    if not link or not link.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shared resume not found or link has been disabled.",
        )

    # Check expiration
    if link.expires_at:
        now = datetime.now(timezone.utc)
        exp = link.expires_at if link.expires_at.tzinfo else link.expires_at.replace(tzinfo=timezone.utc)
        if now > exp:
            return PublicResumeResponse(is_expired=True)

    # Check password protection
    if link.password_hash:
        if not x_share_password or not verify_password(x_share_password, link.password_hash):
            return PublicResumeResponse(
                password_required=True,
                allow_pdf_download=link.allow_pdf_download,
                no_index=link.no_index,
            )

    # Set noindex header if enabled
    if link.no_index:
        response.headers["X-Robots-Tag"] = "noindex, nofollow"

    # Fetch document
    doc_res = await db.execute(
        select(Document).where(Document.id == link.document_id)
    )
    doc = doc_res.scalars().first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document content not found.")

    # Record coarse anonymous view analytics
    user_agent = request.headers.get("user-agent", "").lower()
    device = "desktop"
    if "mobile" in user_agent or "android" in user_agent or "iphone" in user_agent:
        device = "mobile"
    elif "tablet" in user_agent or "ipad" in user_agent:
        device = "tablet"

    country = request.headers.get("cf-ipcountry", "Global")

    view_event = ShareView(
        share_link_id=link.id,
        device_type=device,
        coarse_country=country,
    )
    db.add(view_event)
    await db.commit()

    return PublicResumeResponse(
        password_required=False,
        is_expired=False,
        title=doc.title,
        content=doc.content,
        style=doc.style,
        allow_pdf_download=link.allow_pdf_download,
        no_index=link.no_index,
        doc_type=doc.doc_type or "resume",
    )
