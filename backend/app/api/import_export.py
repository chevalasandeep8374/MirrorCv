import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.models.resume import Document
from app.api.deps import get_current_user
from app.services.docx_exporter import export_resume_to_docx
from app.services.json_resume_importer import import_json_resume
from app.services.linkedin_importer import import_linkedin_zip
from app.services.presets import get_classic_single_column_preset

router = APIRouter(prefix="", tags=["Import & Export"])


@router.get("/resumes/{id}/export/docx")
async def export_resume_docx(
    id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generates an editable Word (.docx) document matching content and style tokens."""
    stmt = select(Document).where(Document.id == id)
    result = await db.execute(stmt)
    doc = result.scalar_one_or_none()

    if not doc or doc.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")

    docx_bytes = export_resume_to_docx(doc.content, doc.style)
    safe_title = "".join(c for c in doc.title if c.isalnum() or c in (" ", "_", "-")).rstrip() or "resume"
    filename = f"{safe_title.replace(' ', '_')}.docx"

    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/import/json-resume")
async def import_json_resume_endpoint(
    file: UploadFile = File(None),
    raw_data: Optional[dict] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Imports JSON Resume schema file into MirrorCV content schema and creates a new resume."""
    data = {}
    if file:
        content_bytes = await file.read()
        try:
            data = json.loads(content_bytes.decode("utf-8"))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON file: {str(e)}")
    elif raw_data:
        data = raw_data
    else:
        raise HTTPException(status_code=422, detail="Provide either a JSON file or raw_data.")

    content_dict, report = import_json_resume(data)

    # Create new document with standard preset
    default_preset = get_classic_single_column_preset()
    title = f"{content_dict['header']['name']} - Resume (Imported)"
    new_doc = Document(
        user_id=current_user.id,
        title=title,
        content=content_dict,
        style=default_preset.model_dump(),
        tags=["imported", "json_resume"],
    )
    db.add(new_doc)
    await db.commit()
    await db.refresh(new_doc)

    return {
        "resume_id": new_doc.id,
        "title": new_doc.title,
        "content": content_dict,
        "mapping_report": report,
    }


@router.post("/import/linkedin-zip")
async def import_linkedin_zip_endpoint(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Imports LinkedIn Data Export ZIP archive (Profile, Positions, Education, Skills CSVs)."""
    if not file.filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="Uploaded file must be a .zip archive.")

    zip_bytes = await file.read()
    try:
        content_dict, report = import_linkedin_zip(zip_bytes)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read LinkedIn ZIP: {str(e)}")

    default_preset = get_classic_single_column_preset()
    title = f"{content_dict['header']['name']} - LinkedIn Import"
    new_doc = Document(
        user_id=current_user.id,
        title=title,
        content=content_dict,
        style=default_preset.model_dump(),
        tags=["imported", "linkedin"],
    )
    db.add(new_doc)
    await db.commit()
    await db.refresh(new_doc)

    return {
        "resume_id": new_doc.id,
        "title": new_doc.title,
        "content": content_dict,
        "mapping_report": report,
    }
