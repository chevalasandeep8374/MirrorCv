import os
import shutil
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.template import UploadedTemplate
from app.services.docx_fingerprint import fingerprint_docx
from app.services.role_classifier import classify_paragraphs
from app.services.content_extractor import extract_content_and_style
from app.services.pdf_converter import convert_docx_to_pdf
from app.api.deps import get_current_user

router = APIRouter(prefix="/templates", tags=["Templates"])

UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_template(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Uploads a DOCX resume, validates max 5MB, extracts fingerprint & roles,

    and stores a parsed template record in PostgreSQL.
    """
    if not file.filename or not file.filename.lower().endswith(".docx"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Only Microsoft Word (.docx) files are supported.",
        )

    # Read and check file size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File exceeds maximum allowed size of 5 MB ({len(contents)} bytes).",
        )

    template_id = str(uuid.uuid4())
    save_filename = f"{template_id}_{file.filename}"
    saved_docx_path = os.path.join(UPLOAD_DIR, save_filename)
    saved_pdf_path = os.path.join(UPLOAD_DIR, f"{template_id}_original.pdf")

    with open(saved_docx_path, "wb") as f:
        f.write(contents)

    # 1. Fingerprint
    try:
        fp = fingerprint_docx(saved_docx_path)
    except Exception as exc:
        if os.path.exists(saved_docx_path):
            os.remove(saved_docx_path)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse DOCX structure (file may be password-protected or corrupt): {str(exc)}",
        )

    # 2. Classify roles
    role_map = classify_paragraphs(fp)

    # Validate that at least one recognizable section exists
    if not role_map.sections_hierarchy:
        if os.path.exists(saved_docx_path):
            os.remove(saved_docx_path)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The uploaded resume has no recognizable sections (Experience, Skills, Education, etc.). Please check formatting.",
        )

    # 3. Extract Phase 1 Content & Style
    content, style, c_to_p = extract_content_and_style(fp, role_map)

    # 4. Render initial original PDF
    try:
        convert_docx_to_pdf(saved_docx_path, saved_pdf_path)
    except Exception as exc:
        saved_pdf_path = None

    template_record = UploadedTemplate(
        id=template_id,
        user_id=current_user.id,
        original_filename=file.filename,
        file_path=saved_docx_path,
        pdf_path=saved_pdf_path,
        fingerprint=fp.model_dump(),
        role_map=role_map.model_dump(),
        content=content.model_dump(),
        style=style.model_dump(),
        content_to_paragraphs=c_to_p,
    )
    db.add(template_record)
    await db.commit()
    await db.refresh(template_record)

    return {
        "id": template_record.id,
        "filename": template_record.original_filename,
        "sections_detected": [s.title for s in role_map.sections_hierarchy],
        "total_paragraphs": fp.document_metadata.total_paragraphs,
        "layout": style.layout.type,
        "has_text_boxes": fp.document_metadata.has_text_boxes,
        "created_at": template_record.created_at,
    }


@router.get("/{template_id}/analysis")
async def get_template_analysis(
    template_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns fingerprint summary, paragraph roles, and extracted Phase 1 content and style."""
    stmt = select(UploadedTemplate).where(
        UploadedTemplate.id == template_id, UploadedTemplate.user_id == current_user.id
    )
    result = await db.execute(stmt)
    template = result.scalars().first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    return {
        "id": template.id,
        "filename": template.original_filename,
        "fingerprint": template.fingerprint,
        "role_map": template.role_map,
        "content": template.content,
        "style": template.style,
        "content_to_paragraphs": template.content_to_paragraphs,
    }
