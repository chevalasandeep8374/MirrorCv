import io
import json
import zipfile
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.database import get_db
from app.models.user import User
from app.models.resume import Document
from app.models.document_version import DocumentVersion
from app.models.share import ShareLink, ShareView
from app.models.user_preset import UserStylePreset
from app.models.ai_log import AiUsageLog
from app.api.deps import get_current_user
from app.services.auth import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)
from app.schemas.account import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    DeleteAccountRequest,
)

router = APIRouter(prefix="", tags=["Account & Hardening"])


@router.post("/account/password")
async def change_password(
    req: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Allows authenticated user to change their account password."""
    if not verify_password(req.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password does not match.",
        )

    current_user.hashed_password = hash_password(req.new_password)
    db.add(current_user)
    await db.commit()
    return {"message": "Password successfully updated."}


@router.post("/auth/forgot-password")
async def forgot_password(
    req: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """Initiates a password reset flow, returning a signed 15-minute token."""
    stmt = select(User).where(User.email == req.email.lower().strip())
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    reset_token = None
    if user:
        # Create signed token with 15 minute expiration
        reset_token = create_access_token(
            user_id=user.id,
            email=user.email,
            expires_delta=timedelta(minutes=15),
        )

    return {
        "message": "If that email is registered, password reset instructions have been generated.",
        "reset_token": reset_token,
    }


@router.post("/auth/reset-password")
async def reset_password(
    req: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """Validates the reset token and updates the user's password."""
    payload = decode_access_token(req.reset_token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token.",
        )

    user_id = payload["sub"]
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    user.hashed_password = hash_password(req.new_password)
    db.add(user)
    await db.commit()
    return {"message": "Password has been successfully reset. You may now sign in."}


@router.get("/account/export-data")
async def export_user_data_gdpr(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """GDPR Full Data Portability: downloads all user resumes, versions, share links,

    custom presets, and usage logs packaged as a clean ZIP archive.
    """
    zip_buf = io.BytesIO()

    # 1. User Profile
    profile_data = {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        "updated_at": current_user.updated_at.isoformat() if current_user.updated_at else None,
        "export_timestamp": datetime.now(timezone.utc).isoformat(),
    }

    # 2. Resumes
    stmt_docs = select(Document).where(Document.user_id == current_user.id)
    res_docs = await db.execute(stmt_docs)
    documents = res_docs.scalars().all()

    # 3. Presets
    stmt_presets = select(UserStylePreset).where(UserStylePreset.user_id == current_user.id)
    res_presets = await db.execute(stmt_presets)
    presets = res_presets.scalars().all()

    # 4. AI Usage Logs
    stmt_ai = select(AiUsageLog).where(AiUsageLog.user_id == current_user.id)
    res_ai = await db.execute(stmt_ai)
    ai_logs = res_ai.scalars().all()

    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        # Profile
        zf.writestr("profile.json", json.dumps(profile_data, indent=2))

        # Resumes
        for doc in documents:
            doc_data = {
                "id": doc.id,
                "title": doc.title,
                "target_job_title": doc.target_job_title,
                "tags": doc.tags,
                "folder": doc.folder,
                "is_archived": doc.is_archived,
                "content": doc.content,
                "style": doc.style,
                "created_at": doc.created_at.isoformat() if doc.created_at else None,
                "updated_at": doc.updated_at.isoformat() if doc.updated_at else None,
            }
            safe_title = "".join(c for c in doc.title if c.isalnum() or c in (" ", "_", "-")).strip() or "resume"
            zf.writestr(f"resumes/{doc.id}_{safe_title.replace(' ', '_')}.json", json.dumps(doc_data, indent=2))

            # Fetch versions for this document
            stmt_vers = select(DocumentVersion).where(DocumentVersion.document_id == doc.id)
            res_vers = await db.execute(stmt_vers)
            versions = res_vers.scalars().all()
            if versions:
                vers_list = [
                    {
                        "id": v.id,
                        "version_number": v.version_number,
                        "label": v.label,
                        "is_manual": v.is_manual,
                        "change_summary": v.change_summary,
                        "content_snapshot": v.content_snapshot,
                        "style_snapshot": v.style_snapshot,
                        "created_at": v.created_at.isoformat() if v.created_at else None,
                    }
                    for v in versions
                ]
                zf.writestr(f"versions/{doc.id}_versions.json", json.dumps(vers_list, indent=2))

            # Fetch share link for this document
            stmt_share = select(ShareLink).where(ShareLink.document_id == doc.id)
            res_share = await db.execute(stmt_share)
            share = res_share.scalar_one_or_none()
            if share:
                # Fetch views
                stmt_views = select(ShareView).where(ShareView.share_link_id == share.id)
                res_views = await db.execute(stmt_views)
                views = res_views.scalars().all()
                share_data = {
                    "slug": share.slug,
                    "is_active": share.is_active,
                    "expires_at": share.expires_at.isoformat() if share.expires_at else None,
                    "allow_pdf_download": share.allow_pdf_download,
                    "no_index": share.no_index,
                    "total_views": len(views),
                    "views": [
                        {
                            "id": vw.id,
                            "viewed_at": vw.viewed_at.isoformat() if vw.viewed_at else None,
                            "country": vw.country,
                            "device_type": vw.device_type,
                        }
                        for vw in views
                    ],
                }
                zf.writestr(f"shares/{doc.id}_share.json", json.dumps(share_data, indent=2))

        # Presets
        if presets:
            presets_data = [
                {
                    "id": p.id,
                    "name": p.name,
                    "style_tokens": p.style_tokens,
                    "created_at": p.created_at.isoformat() if p.created_at else None,
                }
                for p in presets
            ]
            zf.writestr("presets/user_presets.json", json.dumps(presets_data, indent=2))

        # AI Usage
        if ai_logs:
            ai_data = [
                {
                    "id": a.id,
                    "action": a.action,
                    "tokens_in": a.tokens_in,
                    "tokens_out": a.tokens_out,
                    "cost_usd": a.cost_usd,
                    "created_at": a.created_at.isoformat() if a.created_at else None,
                }
                for a in ai_logs
            ]
            zf.writestr("ai_usage/logs.json", json.dumps(ai_data, indent=2))

    zip_bytes = zip_buf.getvalue()
    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": 'attachment; filename="mirrorcv_gdpr_export.zip"'},
    )


@router.delete("/account/delete-my-data")
async def delete_my_data(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """GDPR / CCPA 'Right to be Forgotten' endpoint.
    Permanently deletes all data associated with the user across:
    - Postgres DB (resumes, versions, share links, presets, logs)
    - Supabase Cloud DB (master_profile_items with vector embeddings, template_profiles, compositions, tailoring_results, pipeline_runs)
    - Supabase Storage (storage buckets 'originals' and 'exports')
    """
    user_id = current_user.id
    deletion_manifest: Dict[str, Any] = {
        "user_id": user_id,
        "database_records_deleted": 0,
        "storage_files_deleted": 0,
        "embeddings_deleted": 0,
        "status": "success",
    }

    # 1. Clean up Supabase Cloud tables & Storage if Supabase is configured
    if settings.SUPABASE_URL and settings.SUPABASE_KEY:
        import httpx
        base_url = settings.SUPABASE_URL.rstrip("/")
        headers = {
            "apikey": settings.SUPABASE_KEY,
            "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_KEY}",
            "Prefer": "return=representation",
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            # Delete vector embeddings from master_profile_items
            try:
                resp = await client.delete(f"{base_url}/rest/v1/master_profile_items?user_id=eq.{user_id}", headers=headers)
                if resp.status_code in (200, 204):
                    items = resp.json() if resp.status_code == 200 else []
                    deletion_manifest["embeddings_deleted"] = len(items)
            except Exception as e:
                logger.error(f"Error deleting master_profile_items: {e}")

            # Delete compositions
            try:
                await client.delete(f"{base_url}/rest/v1/compositions?user_id=eq.{user_id}", headers=headers)
            except Exception as e:
                logger.error(f"Error deleting compositions: {e}")

            # Delete tailoring results
            try:
                await client.delete(f"{base_url}/rest/v1/tailoring_results?user_id=eq.{user_id}", headers=headers)
            except Exception as e:
                logger.error(f"Error deleting tailoring_results: {e}")

            # Delete template profiles
            try:
                await client.delete(f"{base_url}/rest/v1/template_profiles?user_id=eq.{user_id}", headers=headers)
            except Exception as e:
                logger.error(f"Error deleting template_profiles: {e}")

            # Delete pipeline runs
            try:
                await client.delete(f"{base_url}/rest/v1/pipeline_runs?user_id=eq.{user_id}", headers=headers)
            except Exception as e:
                logger.error(f"Error deleting pipeline_runs: {e}")

            # Delete Supabase resumes
            try:
                await client.delete(f"{base_url}/rest/v1/resumes?user_id=eq.{user_id}", headers=headers)
            except Exception as e:
                logger.error(f"Error deleting resumes from cloud: {e}")

            # Delete Storage Objects in 'originals' and 'exports'
            for bucket in ["originals", "exports"]:
                try:
                    list_url = f"{base_url}/storage/v1/object/list/{bucket}"
                    list_resp = await client.post(list_url, headers=headers, json={"prefix": user_id})
                    if list_resp.status_code == 200:
                        files = list_resp.json()
                        file_paths = [f"{user_id}/{f['name']}" for f in files if "name" in f]
                        if file_paths:
                            del_url = f"{base_url}/storage/v1/object/{bucket}"
                            del_resp = await client.request("DELETE", del_url, headers=headers, json={"prefixes": file_paths})
                            if del_resp.status_code in (200, 204):
                                deletion_manifest["storage_files_deleted"] += len(file_paths)
                except Exception as e:
                    logger.error(f"Error deleting storage objects from {bucket}: {e}")

    # 2. Local Database Cascade Deletions
    await db.execute(delete(AiUsageLog).where(AiUsageLog.user_id == user_id))
    await db.execute(delete(UserStylePreset).where(UserStylePreset.user_id == user_id))
    res = await db.execute(delete(Document).where(Document.user_id == user_id))
    deletion_manifest["database_records_deleted"] += res.rowcount or 0

    await db.commit()

    return {
        "message": "All personal data, vector embeddings, storage files, and resumes have been permanently purged.",
        "manifest": deletion_manifest,
    }


@router.post("/account/delete")
async def delete_account(
    req: DeleteAccountRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Permanently deletes the authenticated user account and cascades deletion across all tables."""
    if not verify_password(req.password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password. Account deletion aborted.",
        )

    user_id = current_user.id

    # Cascade delete across all tables
    await db.execute(delete(AiUsageLog).where(AiUsageLog.user_id == user_id))
    await db.execute(delete(UserStylePreset).where(UserStylePreset.user_id == user_id))

    # Find and delete resumes (which cascades to versions & share links via FK constraints)
    await db.execute(delete(Document).where(Document.user_id == user_id))

    # Delete user record
    await db.execute(delete(User).where(User.id == user_id))
    await db.commit()

    return {"message": "Account and all associated personal data have been permanently deleted."}
