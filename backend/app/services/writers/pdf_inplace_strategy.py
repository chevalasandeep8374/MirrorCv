import os
import copy
import fitz
from typing import Dict, List, Any, Optional, Tuple
from app.schemas.content import ResumeContent
from app.schemas.pdf_template import (
    PdfLayout,
    PdfBlock,
    PdfLine,
    FontResolutionTable,
    FidelityScoreBreakdown,
)
from app.services.writers.base_strategy import WriterStrategy
from app.services.pdf_font_analyzer import measure_text_width_pt
from app.services.pdf_fidelity_scorer import calculate_fidelity_score


def _map_to_fitz_font(font_name: str, is_bold: bool = False, is_italic: bool = False) -> str:
    """Maps a resolved font family to PyMuPDF's built-in standard base-14 font identifier."""
    lower = font_name.lower()
    if any(k in lower for k in ["times", "serif", "caladea", "georgia", "roman"]):
        if is_bold and is_italic:
            return "tibi"
        elif is_bold:
            return "tibo"
        elif is_italic:
            return "tiit"
        return "tiro"
    elif any(k in lower for k in ["mono", "courier", "console", "code"]):
        if is_bold and is_italic:
            return "cobi"
        elif is_bold:
            return "cobo"
        elif is_italic:
            return "coit"
        return "cour"
    else:  # Sans-serif default (Helvetica, Arial, Carlito, Liberation Sans)
        if is_bold and is_italic:
            return "hebi"
        elif is_bold:
            return "hebo"
        elif is_italic:
            return "heit"
        return "helv"


def _normalize_bullet_str(s: str) -> str:
    return s.replace("\x95", "•").replace("\u2022", "•").strip()


class PdfInPlaceWriterStrategy(WriterStrategy):
    """Strategy 1: Tier A 'Exact'.

    Preserves vector graphics and images via PyMuPDF redaction,
    re-inserts tailored text at exact block coordinates with reflow propagation.
    """

    def plan(self, content: ResumeContent, template_data: Any) -> Dict[str, Any]:
        """Calculates line and coordinate delta shifts for all text blocks."""
        layout: PdfLayout = template_data.get("layout")
        content_to_paragraphs: Dict[str, List[int]] = template_data.get("content_to_paragraphs", {})
        font_table: Optional[FontResolutionTable] = template_data.get("font_table")

        if not layout:
            return {"will_overflow": False, "replaced_blocks": {}, "column_shifts": {}}

        # Map each paragraph index to candidate content text
        para_to_new_text: Dict[int, str] = {}
        for sec in content.sections:
            for item in sec.items:
                if sec.type == "skills" and item.title and not item.title.startswith("Skill Group"):
                    for b in item.bullets:
                        for key, p_indices in content_to_paragraphs.items():
                            if b.id in key or f".{b.id}" in key:
                                for p_idx in p_indices:
                                    para_to_new_text[p_idx] = f"{item.title}: {b.text}"
                else:
                    for b in item.bullets:
                        for key, p_indices in content_to_paragraphs.items():
                            if b.id in key or f".{b.id}" in key:
                                for p_idx in p_indices:
                                    para_to_new_text[p_idx] = b.text

        # Track reflow deltas per column on each page
        # key: (page_number, column_id) -> cumulative vertical displacement in points
        col_shifts: Dict[Tuple[int, str], float] = {}
        replaced_blocks: Dict[str, Dict[str, Any]] = {}
        will_overflow = False

        for block in layout.blocks:
            p_idx = block.reading_order
            col_key = (block.page_number, block.column_id)
            current_col_shift = col_shifts.get(col_key, 0.0)

            orig_text = block.text.strip()
            new_text = para_to_new_text.get(p_idx, orig_text).strip()

            # Format bullet glyph if block originally had one
            if block.bullet_info.is_bullet and block.bullet_info.glyph:
                glyph = block.bullet_info.glyph
                if not new_text.startswith(glyph):
                    bullet_prefix = "\x95 " if glyph == "•" else f"{glyph} "
                    formatted_new_text = bullet_prefix + new_text.lstrip("•-▪➤* ")
                else:
                    formatted_new_text = new_text
            else:
                formatted_new_text = new_text

            avg_font_sz = 10.0
            if block.lines and block.lines[0].spans:
                avg_font_sz = block.lines[0].spans[0].font_size_pt

            # Check if text is genuinely modified after normalizing whitespace & bullets
            is_changed = (_normalize_bullet_str(formatted_new_text) != _normalize_bullet_str(orig_text))
            if not is_changed:
                formatted_new_text = orig_text
                line_delta = 0
                height_delta = 0.0
            else:
                orig_lines = max(1, len(block.lines))
                line_height_pt = avg_font_sz * block.spacing.line_height

                # Approximate line wrapping for new text
                est_width = max(50.0, block.max_width_pt)
                text_w = measure_text_width_pt(formatted_new_text, "helv", avg_font_sz)
                est_new_lines = max(1, int(round(text_w / est_width + 0.45)))
                line_delta = est_new_lines - orig_lines
                height_delta = line_delta * line_height_pt

            replaced_blocks[block.block_id] = {
                "block": block,
                "is_changed": is_changed,
                "orig_text": orig_text,
                "new_text": formatted_new_text,
                "y_shift": current_col_shift,
                "height_delta": height_delta,
                "font_size": avg_font_sz,
            }

            # If block height changed, update cumulative vertical displacement for this column
            if height_delta != 0:
                col_shifts[col_key] = current_col_shift + height_delta

            # Check overflow against bottom margin
            if len(block.bbox) >= 4:
                predicted_bottom = block.bbox[3] + current_col_shift + height_delta
                # A4 height is ~842pt; overflow threshold is 800pt
                if predicted_bottom > 800.0:
                    will_overflow = True

        return {
            "will_overflow": will_overflow,
            "replaced_blocks": replaced_blocks,
            "column_shifts": col_shifts,
        }

    def write(self, content: ResumeContent, template_path: str, output_path: str, **kwargs) -> str:
        """Executes in-place redaction and re-insertion into the PDF."""
        template_data = kwargs.get("template_data", {})
        layout: PdfLayout = template_data.get("layout")
        font_table: Optional[FontResolutionTable] = template_data.get("font_table")

        plan_res = self.plan(content, template_data)
        replaced_map = plan_res["replaced_blocks"]

        doc = fitz.open(template_path)

        # 1. Save original link annotations per page
        links_by_page: Dict[int, List[Dict[str, Any]]] = {}
        for p_idx, page in enumerate(doc):
            links_by_page[p_idx + 1] = page.get_links()

        # 2. Process each page
        for p_idx, page in enumerate(doc):
            page_num = p_idx + 1
            page_blocks = [b for b in layout.blocks if b.page_number == page_num] if layout else []

            # Check which blocks have changed text or non-zero shift
            blocks_to_rewrite = []
            for b in page_blocks:
                p_info = replaced_map.get(b.block_id)
                if p_info and (p_info["is_changed"] or abs(p_info["y_shift"]) > 0.1):
                    blocks_to_rewrite.append((b, p_info))

            if not blocks_to_rewrite:
                continue

            # Redact ONLY the blocks being replaced
            for b, p_info in blocks_to_rewrite:
                if len(b.bbox) >= 4:
                    page.add_redact_annot(fitz.Rect(b.bbox), fill=False)

            # Apply redactions preserving images and vector graphics
            page.apply_redactions(
                images=fitz.PDF_REDACT_IMAGE_NONE,
                graphics=fitz.PDF_REDACT_LINE_ART_NONE,
            )

            # Re-insert new text at origin + shift
            for b, p_info in blocks_to_rewrite:
                new_text = p_info["new_text"]
                y_shift = p_info["y_shift"]
                bx0, by0, bx1, by1 = b.bbox

                # Find dominant font, style and color from original spans
                font_name = "Helvetica"
                is_bold = False
                is_italic = False
                color_rgb = (0.15, 0.15, 0.15)
                fontsize = p_info["font_size"]

                if b.lines and b.lines[0].spans:
                    first_s = b.lines[0].spans[0]
                    font_name = first_s.font_family
                    is_bold = first_s.flags.is_bold
                    is_italic = first_s.flags.is_italic
                    color_rgb = first_s.color_rgb

                fitz_font = _map_to_fitz_font(font_name, is_bold=is_bold, is_italic=is_italic)

                # Target rect for text insertion
                max_w = b.max_width_pt
                insert_rect = fitz.Rect(
                    bx0,
                    by0 + y_shift,
                    bx0 + max_w,
                    by1 + y_shift + p_info["height_delta"] + 10.0,
                )

                # For single-line without wrapping, use insert_text for exact baseline fidelity
                if len(b.lines) == 1 and "\n" not in new_text and len(new_text) < 60:
                    orig_pt = fitz.Point(b.lines[0].baseline_origin[0], b.lines[0].baseline_origin[1] + y_shift)
                    page.insert_text(
                        orig_pt,
                        new_text,
                        fontname=fitz_font,
                        fontsize=fontsize,
                        color=color_rgb,
                    )
                else:
                    page.insert_textbox(
                        insert_rect,
                        new_text,
                        fontname=fitz_font,
                        fontsize=fontsize,
                        color=color_rgb,
                        lineheight=b.spacing.line_height,
                    )

            # Re-attach unchanged links
            for link in links_by_page.get(page_num, []):
                if link.get("uri") and link.get("from"):
                    page.insert_link(link)

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        doc.save(output_path, garbage=3, deflate=True)
        doc.close()
        return output_path

    def measure(self, original_path: str, generated_path: str, **kwargs) -> FidelityScoreBreakdown:
        """Measures fidelity score against the original document."""
        return calculate_fidelity_score(
            original_pdf_path=original_path,
            generated_pdf_path=generated_path,
            font_table=kwargs.get("font_table"),
            is_scanned=False,
        )
