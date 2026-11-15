from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.database import get_db
from app.models.resume import Document
from app.models.document_version import DocumentVersion
from app.models.user import User
from app.api.deps import get_current_user
from app.schemas.version import (
    VersionCreate,
    VersionSummary,
    VersionDetail,
    VersionCompareRequest,
    VersionCompareResponse,
    DiffItem,
)

router = APIRouter(prefix="/resumes/{resume_id}/versions", tags=["versions"])


async def _get_owned_resume(resume_id: str, user: User, db: AsyncSession) -> Document:
    result = await db.execute(select(Document).where(Document.id == resume_id))
    resume = result.scalars().first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found"
        )
    if resume.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this resume"
        )
    return resume


async def _prune_old_auto_versions(resume_id: str, db: AsyncSession, max_auto: int = 50):
    """Retains all manual/labeled versions and keeps only the latest max_auto auto-snapshots."""
    result = await db.execute(
        select(DocumentVersion)
        .where(
            DocumentVersion.document_id == resume_id,
            DocumentVersion.is_manual == False,
        )
        .order_by(desc(DocumentVersion.created_at))
    )
    auto_versions = result.scalars().all()

    if len(auto_versions) > max_auto:
        excess = auto_versions[max_auto:]
        for v in excess:
            await db.delete(v)
        await db.commit()


@router.get("", response_model=List[VersionSummary])
async def list_versions(
    resume_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lists all versions for the resume in reverse chronological order."""
    await _get_owned_resume(resume_id, user, db)

    result = await db.execute(
        select(DocumentVersion)
        .where(DocumentVersion.document_id == resume_id)
        .order_by(desc(DocumentVersion.version_number))
    )
    return result.scalars().all()


@router.post("", response_model=VersionSummary)
async def create_version(
    resume_id: str,
    payload: VersionCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Creates a new snapshot version.
    Deduplicates if content and style have not changed from the most recent version.
    """
    resume = await _get_owned_resume(resume_id, user, db)

    # Get latest version for deduplication check
    result = await db.execute(
        select(DocumentVersion)
        .where(DocumentVersion.document_id == resume_id)
        .order_by(desc(DocumentVersion.version_number))
    )
    latest_version = result.scalars().first()

    cur_content = resume.content or {}
    cur_style = resume.style or {}

    # Deduplication check for auto-snapshots
    if latest_version and not payload.is_manual:
        if (
            latest_version.content_snapshot == cur_content
            and latest_version.style_snapshot == cur_style
        ):
            return latest_version

    next_num = (latest_version.version_number + 1) if latest_version else 1

    new_version = DocumentVersion(
        document_id=resume_id,
        version_number=next_num,
        label=payload.label,
        is_manual=payload.is_manual,
        change_summary=payload.change_summary,
        content_snapshot=cur_content,
        style_snapshot=cur_style,
    )

    db.add(new_version)
    await db.commit()
    await db.refresh(new_version)

    # Prune auto-snapshots beyond retention limit
    await _prune_old_auto_versions(resume_id, db, max_auto=50)

    return new_version


@router.get("/{version_id}", response_model=VersionDetail)
async def get_version(
    resume_id: str,
    version_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves full snapshot detail for a specific version."""
    await _get_owned_resume(resume_id, user, db)

    result = await db.execute(
        select(DocumentVersion).where(
            DocumentVersion.document_id == resume_id,
            DocumentVersion.id == version_id,
        )
    )
    version = result.scalars().first()
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Version not found"
        )
    return version


@router.post("/{version_id}/restore", response_model=VersionSummary)
async def restore_version(
    resume_id: str,
    version_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Restores the specified version into the active resume document.
    Rule: Restoring creates a NEW version, preserving the full timeline history.
    """
    resume = await _get_owned_resume(resume_id, user, db)

    result = await db.execute(
        select(DocumentVersion).where(
            DocumentVersion.document_id == resume_id,
            DocumentVersion.id == version_id,
        )
    )
    target_version = result.scalars().first()
    if not target_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Target version not found"
        )

    # Apply snapshots to current resume
    resume.content = target_version.content_snapshot
    resume.style = target_version.style_snapshot

    # Find next version number
    num_result = await db.execute(
        select(func.max(DocumentVersion.version_number)).where(
            DocumentVersion.document_id == resume_id
        )
    )
    max_num = num_result.scalar() or 0

    restored_version = DocumentVersion(
        document_id=resume_id,
        version_number=max_num + 1,
        label=f"Restored from v{target_version.version_number}",
        is_manual=True,
        change_summary=f"Reverted to version {target_version.version_number} created on {target_version.created_at.strftime('%Y-%m-%d %H:%M')}",
        content_snapshot=resume.content,
        style_snapshot=resume.style,
    )

    db.add(restored_version)
    await db.commit()
    await db.refresh(restored_version)
    return restored_version


@router.post("/compare", response_model=VersionCompareResponse)
async def compare_versions(
    resume_id: str,
    payload: VersionCompareRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Computes a text-level structured comparison between two versions.
    """
    await _get_owned_resume(resume_id, user, db)

    res_a = await db.execute(
        select(DocumentVersion).where(
            DocumentVersion.document_id == resume_id,
            DocumentVersion.id == payload.version_a_id,
        )
    )
    v_a = res_a.scalars().first()

    res_b = await db.execute(
        select(DocumentVersion).where(
            DocumentVersion.document_id == resume_id,
            DocumentVersion.id == payload.version_b_id,
        )
    )
    v_b = res_b.scalars().first()

    if not v_a or not v_b:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or both versions not found",
        )

    diffs: List[DiffItem] = []

    # Compare Header
    header_a = (v_a.content_snapshot or {}).get("header", {})
    header_b = (v_b.content_snapshot or {}).get("header", {})

    for key in ["name", "title", "email", "phone", "location", "website"]:
        val_a = header_a.get(key, "")
        val_b = header_b.get(key, "")
        if val_a != val_b:
            diffs.append(
                DiffItem(
                    path=f"Header > {key.capitalize()}",
                    type="modified",
                    old_value=val_a,
                    new_value=val_b,
                )
            )

    # Compare Sections
    sections_a = {
        s.get("id"): s for s in (v_a.content_snapshot or {}).get("sections", [])
    }
    sections_b = {
        s.get("id"): s for s in (v_b.content_snapshot or {}).get("sections", [])
    }

    all_sec_ids = set(sections_a.keys()).union(set(sections_b.keys()))

    for sec_id in all_sec_ids:
        if sec_id in sections_a and sec_id not in sections_b:
            diffs.append(
                DiffItem(
                    path=f"Section: {sections_a[sec_id].get('title', 'Untitled')}",
                    type="removed",
                    old_value=sections_a[sec_id].get("title"),
                    new_value=None,
                )
            )
        elif sec_id in sections_b and sec_id not in sections_a:
            diffs.append(
                DiffItem(
                    path=f"Section: {sections_b[sec_id].get('title', 'Untitled')}",
                    type="added",
                    old_value=None,
                    new_value=sections_b[sec_id].get("title"),
                )
            )
        else:
            s_a = sections_a[sec_id]
            s_b = sections_b[sec_id]
            sec_title = s_b.get("title", s_a.get("title", "Section"))

            if s_a.get("title") != s_b.get("title"):
                diffs.append(
                    DiffItem(
                        path=f"{sec_title} > Title",
                        type="modified",
                        old_value=s_a.get("title"),
                        new_value=s_b.get("title"),
                    )
                )

            items_a = s_a.get("items", [])
            items_b = s_b.get("items", [])

            bullets_a_text = [
                f"{b.get('text', '')}"
                for item in items_a
                for b in item.get("bullets", [])
            ]
            bullets_b_text = [
                f"{b.get('text', '')}"
                for item in items_b
                for b in item.get("bullets", [])
            ]

            set_a = set(bullets_a_text)
            set_b = set(bullets_b_text)

            for b_added in set_b - set_a:
                diffs.append(
                    DiffItem(
                        path=f"{sec_title} > Bullet",
                        type="added",
                        old_value=None,
                        new_value=b_added,
                    )
                )

            for b_removed in set_a - set_b:
                diffs.append(
                    DiffItem(
                        path=f"{sec_title} > Bullet",
                        type="removed",
                        old_value=b_removed,
                        new_value=None,
                    )
                )

    return VersionCompareResponse(
        version_a_number=v_a.version_number,
        version_b_number=v_b.version_number,
        diffs=diffs,
    )
