import os
import tempfile
from typing import Tuple, Optional, Dict, Any, List
from app.schemas.content import ResumeContent
from app.schemas.style import ResumeStyle
from app.schemas.template import RoleMap
from app.schemas.pdf_template import (
    PdfLayout,
    FontResolutionTable,
    FidelityScoreBreakdown,
)
from app.services.writers.base_strategy import WriterStrategy
from app.services.writers.pdf_inplace_strategy import PdfInPlaceWriterStrategy
from app.services.writers.pdf_rebuild_strategy import PdfRebuildWriterStrategy


def select_best_strategy(
    template_path: str,
    layout: PdfLayout,
    role_map: RoleMap,
    content: ResumeContent,
    style: ResumeStyle,
    content_to_paragraphs: Dict[str, List[int]],
    font_table: Optional[FontResolutionTable] = None,
    work_dir: Optional[str] = None,
) -> Tuple[WriterStrategy, FidelityScoreBreakdown, str]:
    """Auto-picks the optimal writer strategy for a given PDF:

    1. If document is scanned / image-only: select Rebuild / OCR (Tier C).
    2. Try In-Place strategy with a no-op write:
       - Measure fidelity score.
       - If score >= 90.0: select In-Place (Tier A).
    3. If In-Place score < 90.0:
       - Try Rebuild strategy with a no-op write.
       - Compare both scores and select whichever scores higher.
    Returns:
    - selected_strategy: WriterStrategy
    - score_breakdown: FidelityScoreBreakdown
    - noop_preview_pdf_path: str
    """
    if not work_dir:
        work_dir = os.path.dirname(os.path.abspath(template_path))
    os.makedirs(work_dir, exist_ok=True)

    base_name = os.path.splitext(os.path.basename(template_path))[0]
    inplace_noop_path = os.path.join(work_dir, f"{base_name}_noop_inplace.pdf")
    rebuild_noop_path = os.path.join(work_dir, f"{base_name}_noop_rebuild.pdf")

    template_data = {
        "layout": layout,
        "role_map": role_map,
        "style": style,
        "content_to_paragraphs": content_to_paragraphs,
        "font_table": font_table,
        "is_scanned": layout.document_metadata.is_scanned,
    }

    # 1. Scanned Document Path -> Direct to Rebuild / OCR (Tier C)
    if layout.document_metadata.is_scanned:
        rebuild_writer = PdfRebuildWriterStrategy()
        rebuild_writer.write(content, template_path, rebuild_noop_path, template_data=template_data)
        rebuild_score = rebuild_writer.measure(
            template_path, rebuild_noop_path, font_table=font_table, is_scanned=True
        )
        rebuild_score.tier = "C"
        rebuild_score.selected_strategy = "ocr_rebuild"
        return rebuild_writer, rebuild_score, rebuild_noop_path

    # 2. Try In-Place Strategy First
    inplace_writer = PdfInPlaceWriterStrategy()
    try:
        inplace_writer.write(content, template_path, inplace_noop_path, template_data=template_data)
        inplace_score = inplace_writer.measure(template_path, inplace_noop_path, font_table=font_table)
    except Exception as exc:
        inplace_score = FidelityScoreBreakdown(
            total_score=0.0,
            tier="C",
            selected_strategy="rebuild",
            explanation=f"In-place writing failed: {str(exc)}",
        )

    # If in-place achieves >= 90.0, select Tier A
    if inplace_score.total_score >= 90.0:
        inplace_score.tier = "A"
        inplace_score.selected_strategy = "in_place"
        return inplace_writer, inplace_score, inplace_noop_path

    # 3. Fallback to Rebuild and Compare
    rebuild_writer = PdfRebuildWriterStrategy()
    try:
        rebuild_writer.write(content, template_path, rebuild_noop_path, template_data=template_data)
        rebuild_score = rebuild_writer.measure(template_path, rebuild_noop_path, font_table=font_table)
    except Exception as exc:
        rebuild_score = FidelityScoreBreakdown(
            total_score=0.0,
            tier="C",
            selected_strategy="in_place",
            explanation=f"Rebuild writing failed: {str(exc)}",
        )

    # Return whichever strategy achieved the higher fidelity score
    if inplace_score.total_score >= rebuild_score.total_score:
        return inplace_writer, inplace_score, inplace_noop_path
    else:
        return rebuild_writer, rebuild_score, rebuild_noop_path
