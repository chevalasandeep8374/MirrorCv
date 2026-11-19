import os
import json
import uuid
import tempfile
import logging
from typing import Optional, Dict, Any, List
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

# PDF extraction
from app.services.pdf_extractor import extract_pdf_spans_and_assets, validate_pdf
from app.services.pdf_layout_analyzer import analyze_pdf_layout
from app.services.pdf_role_adapter import process_pdf_roles_and_content

# DOCX extraction
from app.services.docx_validator import validate_docx_bytes
from app.services.docx_fingerprint import fingerprint_docx
from app.services.role_classifier import classify_paragraphs
from app.services.content_extractor import extract_content_and_style

logger = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["Import & Export"])


@router.post("/import/resume")
async def import_universal_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Universal resume intake endpoint.

    Supports PDF (.pdf), Word (.docx), JSON Resume (.json), LinkedIn Archive (.zip), or Text (.txt).
    Automatically detects file type, runs deterministic extraction into MirrorCV schema,
    stores document in database, and returns the parsed resume.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded.")

    filename_lower = file.filename.lower()
    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    detected_format = ""
    content_dict: Dict[str, Any] = {}
    style_dict: Dict[str, Any] = {}
    mapping_report: Dict[str, Any] = {}

    default_preset = get_classic_single_column_preset().model_dump()

    # 1. PDF Resume
    if filename_lower.endswith(".pdf"):
        detected_format = "pdf"
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        try:
            is_valid, err, page_count = validate_pdf(tmp_path)
            if not is_valid:
                raise HTTPException(status_code=400, detail=f"Invalid PDF: {err}")

            raw_layout = extract_pdf_spans_and_assets(tmp_path)
            if raw_layout.document_metadata.is_scanned and raw_layout.document_metadata.extractable_char_count < 50:
                raise HTTPException(
                    status_code=422,
                    detail="This PDF appears to be a scanned image without selectable text. Please upload a PDF with selectable text, DOCX, or JSON.",
                )

            layout = analyze_pdf_layout(raw_layout)
            role_map, content_model, style_model, c_to_p, _ = process_pdf_roles_and_content(layout)

            content_dict = content_model.model_dump()
            style_dict = style_model.model_dump() if style_model else default_preset

            mapping_report = {
                "source": "pdf",
                "page_count": page_count,
                "sections_detected": [s.title for s in content_model.sections],
                "char_count": raw_layout.document_metadata.extractable_char_count,
            }
        except HTTPException:
            raise
        except Exception as exc:
            logger.error(f"Failed to parse PDF resume: {exc}", exc_info=True)
            raise HTTPException(status_code=422, detail=f"Failed to parse PDF resume: {str(exc)}")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    # 2. DOCX Resume
    elif filename_lower.endswith(".docx") or filename_lower.endswith(".doc"):
        detected_format = "docx"
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        try:
            validate_docx_bytes(file_bytes, file.filename)
            fp = fingerprint_docx(tmp_path)
            role_map = classify_paragraphs(fp)
            content_model, style_model, c_to_p = extract_content_and_style(fp, role_map)

            content_dict = content_model.model_dump() if hasattr(content_model, "model_dump") else content_model
            style_dict = style_model.model_dump() if hasattr(style_model, "model_dump") else default_preset

            mapping_report = {
                "source": "docx",
                "sections_detected": [s.get("title") if isinstance(s, dict) else s.title for s in content_dict.get("sections", [])],
                "paragraphs_count": len(fp.paragraphs),
            }
        except HTTPException:
            raise
        except Exception as exc:
            logger.error(f"Failed to parse DOCX resume: {exc}", exc_info=True)
            raise HTTPException(status_code=422, detail=f"Failed to parse DOCX resume: {str(exc)}")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    # 3. JSON Resume
    elif filename_lower.endswith(".json"):
        detected_format = "json"
        try:
            json_data = json.loads(file_bytes.decode("utf-8"))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON file: {str(e)}")

        if "basics" in json_data:
            content_dict, report = import_json_resume(json_data)
            mapping_report = report
            style_dict = default_preset
        elif "header" in json_data and "sections" in json_data:
            content_dict = json_data
            style_dict = default_preset
            mapping_report = {
                "source": "mirrorcv_json",
                "sections_detected": [s.get("title") for s in json_data.get("sections", [])],
            }
        else:
            content_dict, report = import_json_resume(json_data)
            mapping_report = report
            style_dict = default_preset

    # 4. LinkedIn ZIP Archive
    elif filename_lower.endswith(".zip"):
        detected_format = "linkedin_zip"
        try:
            content_dict, report = import_linkedin_zip(file_bytes)
            style_dict = default_preset
            mapping_report = report
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Failed to parse LinkedIn ZIP archive: {str(exc)}")

    # 5. Plain Text (.txt)
    elif filename_lower.endswith(".txt"):
        detected_format = "text"
        try:
            text_content = file_bytes.decode("utf-8", errors="replace")
            lines = [l.strip() for l in text_content.splitlines() if l.strip()]
            header_name = lines[0] if lines else "Candidate"
            content_dict = {
                "header": {
                    "name": header_name,
                    "title": lines[1] if len(lines) > 1 else "",
                    "email": "",
                    "phone": "",
                    "location": "",
                    "website": "",
                    "links": [],
                },
                "sections": [
                    {
                        "id": f"sec-{uuid.uuid4().hex[:6]}",
                        "type": "summary",
                        "title": "Summary",
                        "visible": True,
                        "items": [
                            {
                                "id": f"item-{uuid.uuid4().hex[:6]}",
                                "title": "",
                                "subtitle": "",
                                "bullets": [{"id": f"b-{uuid.uuid4().hex[:6]}", "text": "\n".join(lines[2:10])}],
                            }
                        ],
                    }
                ],
            }
            style_dict = default_preset
            mapping_report = {"source": "text", "lines_count": len(lines)}
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Failed to parse text resume: {str(exc)}")

    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Please upload a PDF (.pdf), Word (.docx), JSON Resume (.json), or LinkedIn Archive (.zip).",
        )

    # Determine title
    candidate_name = (content_dict.get("header", {}).get("name") or "").strip()
    if candidate_name:
        resume_title = f"{candidate_name} - Resume"
    else:
        base_name = os.path.splitext(file.filename)[0]
        resume_title = f"{base_name} (Imported)"

    if not style_dict or not style_dict.get("templateId"):
        style_dict = default_preset

    # Save to database
    new_doc = Document(
        user_id=current_user.id,
        title=resume_title,
        content=content_dict,
        style=style_dict,
        tags=["imported", detected_format],
    )
    db.add(new_doc)
    await db.commit()
    await db.refresh(new_doc)

    detected_sections = [
        s.get("title") if isinstance(s, dict) else s.title
        for s in content_dict.get("sections", [])
    ]

    return {
        "resume_id": new_doc.id,
        "title": new_doc.title,
        "format": detected_format,
        "content": content_dict,
        "style": style_dict,
        "mapping_report": mapping_report,
        "detected_sections": detected_sections,
        "total_sections": len(detected_sections),
        "message": f"Successfully imported {detected_format.upper()} resume!",
    }


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
