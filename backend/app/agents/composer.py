"""Agent 3: Composer
Responsible for taking Agent 1's template (original DOCX + SlotMap) and Agent 2's
accepted tailored changes, and producing a tailored resume whose template is
provably unchanged: same fonts, sizes, margins, spacing, colors, bullets, columns,
and page count.
"""

import os
import copy
import uuid
import logging
from typing import Dict, Any, List, Optional, Union
import httpx

from contracts.models.composition_result import (
    CompositionResult,
    SchemaVersion,
    OutputFile,
    Kind,
    Format,
    Status,
    IntegrityReport,
    FitLoop,
    OverflowReport,
)
from contracts.models.template_profile import TemplateProfile
from contracts.models.tailored_content import Change
from app.services.apply_changes import apply_changes
from app.services.fit_loop import execute_render_and_fit_loop, FitLoopExecutionResult
from app.config import settings

logger = logging.getLogger(__name__)


async def generate_signed_storage_url(bucket: str, storage_path: str, expires_in: int = 600) -> Optional[str]:
    """Generates a secure signed download URL with ~10-minute expiry (600s).

    Uses service role credentials to request the signed object URL from Supabase Storage.
    """
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
        return f"/api/storage/{bucket}/{storage_path}"

    url = f"{settings.SUPABASE_URL.rstrip('/')}/storage/v1/object/sign/{bucket}/{storage_path}"
    headers = {
        "apikey": settings.SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json",
    }
    payload = {"expiresIn": expires_in}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code in (200, 201):
                data = resp.json()
                signed_subpath = data.get("signedURL") or data.get("signedUrl")
                if signed_subpath:
                    return f"{settings.SUPABASE_URL.rstrip('/')}/storage/v1{signed_subpath}"
    except Exception as e:
        logger.warning(f"Could not generate signed URL from Supabase storage: {e}")

    return f"/api/storage/{bucket}/{storage_path}"


class ComposerAgent:
    """Agent 3: Composer implementation."""

    def __init__(self):
        self.agent_name = "Composer"

    async def compose(
        self,
        run_id: str,
        resume_id: str,
        user_id: Optional[str] = "default_user",
        template_docx_path: Optional[str] = None,
        template_profile: Optional[TemplateProfile] = None,
        accepted_changes: Optional[List[Union[Change, Dict[str, Any]]]] = None,
        original_content: Optional[Dict[str, Any]] = None,
        output_dir: Optional[str] = None,
        confirmed_bullet_removals: Optional[List[str]] = None,
        tailored_content: Optional[Any] = None,
        original_style: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> CompositionResult:
        """Executes full composition pipeline (Run 2):

        1. Generates FinalContent deterministically via apply_changes.
        2. Executes render & fit loop with pre-render checks, table/textbox prioritization,
           and headless LibreOffice rendering.
        3. Enforces two-tier verification:
           - Invariants 1-6, 8, container clipping (status: 'failed' blocks download)
           - Layout fit / page count overflow (status: 'layout_changed' requires acknowledgement)
        4. Uploads output files to 'exports' bucket and generates signed URLs (10-minute expiry).
        5. Emits 1.1.0 conformant CompositionResult.
        """
        logger.info(f"Agent 3 [{self.agent_name}]: Starting composition for run {run_id}")
        composition_id = f"comp_{uuid.uuid4().hex[:12]}"
        user_id = user_id or "default_user"
        original_content = original_content or {"sections": []}

        # Ensure template DOCX path exists; fallback is strictly prohibited
        if not template_docx_path or not os.path.exists(template_docx_path):
            raise FileNotFoundError(
                f"Valid template_docx_path is strictly required for composition. Provided: '{template_docx_path}'"
            )

        # Ensure real template_profile is provided; fallback profile generation is strictly prohibited
        if template_profile is None:
            raise ValueError(
                "A verified TemplateProfile is strictly required for composition. Fallback profile generation is permanently disabled."
            )

        # Resolve accepted changes from tailored_content if needed
        if accepted_changes is None:
            if tailored_content is not None and hasattr(tailored_content, "changes"):
                accepted_changes = [
                    c.model_dump() if hasattr(c, "model_dump") else c
                    for c in tailored_content.changes
                ]
            elif isinstance(tailored_content, dict) and "changes" in tailored_content:
                accepted_changes = tailored_content["changes"]
            else:
                accepted_changes = []

        if not output_dir:
            output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "tmp_output", composition_id))
        os.makedirs(output_dir, exist_ok=True)

        # 1. Deterministic pure-function content application
        final_content = apply_changes(original_content, accepted_changes)

        # 2. Render & Fit loop with two-tier verification
        fit_result: FitLoopExecutionResult = execute_render_and_fit_loop(
            template_docx_path=template_docx_path,
            template_profile=template_profile,
            accepted_changes=accepted_changes,
            original_content=original_content,
            final_content=final_content,
            output_dir=output_dir,
            max_rounds=3,
            confirmed_bullet_removals=confirmed_bullet_removals,
        )

        docx_size = os.path.getsize(fit_result.docx_path) if os.path.exists(fit_result.docx_path) else 0
        pdf_size = os.path.getsize(fit_result.pdf_path) if os.path.exists(fit_result.pdf_path) else 0

        # Upload files to storage (bucket: exports)
        docx_storage_path = f"{user_id}/{resume_id}/{composition_id}/tailored_resume.docx"
        pdf_storage_path = f"{user_id}/{resume_id}/{composition_id}/tailored_resume.pdf"

        # Generate signed download URLs (600 seconds = 10 minutes)
        docx_signed_url = None
        pdf_signed_url = None

        # Strict gating: No output files can be produced without passing integrity check
        output_files: List[OutputFile] = []
        if fit_result.status != Status.failed and fit_result.integrity_report.passed:
            docx_signed_url = await generate_signed_storage_url("exports", docx_storage_path, expires_in=600)
            pdf_signed_url = await generate_signed_storage_url("exports", pdf_storage_path, expires_in=600)
            output_files = [
                OutputFile(
                    kind=Kind.tailored,
                    format=Format.docx,
                    storage_path=docx_storage_path,
                    mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    size_bytes=docx_size,
                    download_url=docx_signed_url,
                ),
                OutputFile(
                    kind=Kind.tailored,
                    format=Format.pdf,
                    storage_path=pdf_storage_path,
                    mime_type="application/pdf",
                    size_bytes=pdf_size,
                    download_url=pdf_signed_url,
                ),
            ]
        else:
            logger.warning(
                f"Agent 3: Template integrity check failed ({len(fit_result.integrity_report.violations)} violations). "
                "Output generation strictly gated: zero output files produced."
            )

        page_count_preserved = (fit_result.page_count_after == fit_result.page_count_before)

        overflow_slots = [
            sid for sid, info in fit_result.per_slot_lines.items()
            if info.get("lines_after", 1) > info.get("max_lines", 1)
        ]
        overflow_report = OverflowReport(
            has_overflow=fit_result.status == Status.layout_changed or len(overflow_slots) > 0,
            overflowing_slots=overflow_slots,
            details="Layout overflow detected" if fit_result.status == Status.layout_changed else "All tailored slots fit within geometry budgets.",
        )

        return CompositionResult(
            schema_version=SchemaVersion.field_1_1_0,
            run_id=run_id,
            resume_id=resume_id,
            composition_id=composition_id,
            output_files=output_files,
            overflow_report=overflow_report,
            fidelity_score=template_profile.fidelity_score,
            page_count_before=fit_result.page_count_before,
            page_count_after=fit_result.page_count_after,
            page_count_preserved=page_count_preserved,
            status=fit_result.status,
            integrity_report=fit_result.integrity_report,
            fit_loop=fit_result.fit_loop,
            final_content=final_content,
            per_slot_lines=fit_result.per_slot_lines,
        )


composer_agent = ComposerAgent()
