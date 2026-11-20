from typing import Dict, List, Tuple, Any, Optional
from app.schemas.pdf_template import PdfLayout, PdfBlock, PdfLine, PdfSpan
from app.schemas.template import (
    DocxFingerprint,
    ParagraphFingerprint,
    ParagraphLocation,
    SpacingInfo,
    IndentInfo,
    BulletInfo,
    RunFingerprint,
    RunFormatting,
    DocumentMetadata,
    PageSizePt,
    MarginsPt,
    DefaultFont,
    RoleMap,
)
from app.schemas.content import ResumeContent
from app.schemas.style import ResumeStyle
from app.services.role_classifier import classify_paragraphs, _detect_section_heading
from app.services.content_extractor import extract_content_and_style


def pdf_layout_to_fingerprint(
    layout: PdfLayout,
) -> Tuple[DocxFingerprint, Dict[int, PdfBlock], Dict[int, List[List[float]]]]:
    """Converts a PdfLayout into a DocxFingerprint paragraph structure

    so the Phase 2 role classifier and content extractor can be reused without modification.
    Returns:
    - fingerprint: DocxFingerprint
    - block_map: Dict[int, PdfBlock] (indexed by reading_order / paragraph index)
    - para_to_line_boxes: Dict[int, List[List[float]]] (line bounding boxes per paragraph)
    """
    paragraphs: List[ParagraphFingerprint] = []
    block_map: Dict[int, PdfBlock] = {}
    para_to_line_boxes: Dict[int, List[List[float]]] = {}

    # Calculate overall margins from page size and text bounds
    page_w = 595.3
    page_h = 841.9
    if layout.document_metadata.page_sizes:
        page_w = layout.document_metadata.page_sizes[0].get("width_pt", 595.3)
        page_h = layout.document_metadata.page_sizes[0].get("height_pt", 841.9)

    min_x = page_w
    max_x = 0.0
    min_y = page_h
    max_y = 0.0

    run_counter = 0

    for block in layout.blocks:
        idx = block.reading_order
        block_map[idx] = block

        # Update bounding extent
        if len(block.bbox) >= 4:
            min_x = min(min_x, block.bbox[0])
            max_x = max(max_x, block.bbox[2])
            min_y = min(min_y, block.bbox[1])
            max_y = max(max_y, block.bbox[3])

        # Collect line boxes
        l_boxes = [l.bbox for l in block.lines if len(l.bbox) >= 4]
        para_to_line_boxes[idx] = l_boxes

        # Convert spans to runs
        runs: List[RunFingerprint] = []
        for line in block.lines:
            for s in line.spans:
                run_fmt = RunFormatting(
                    font_family=s.font_family,
                    font_size_pt=s.font_size_pt,
                    bold=s.flags.is_bold,
                    italic=s.flags.is_italic,
                    underline=False,
                    color_hex=s.color_hex,
                    highlight=None,
                )
                runs.append(
                    RunFingerprint(
                        index=run_counter,
                        text=s.text,
                        formatting=run_fmt,
                    )
                )
                run_counter += 1

        # Check alignment heuristic
        alignment: Optional[str] = "left"
        if len(block.bbox) >= 4:
            b_center = (block.bbox[0] + block.bbox[2]) / 2
            if abs(b_center - (page_w / 2)) < 30.0 and (block.bbox[2] - block.bbox[0]) < (page_w * 0.6):
                alignment = "center"

        # Determine location type: sidebar blocks map to text_box, main to body
        is_sidebar = "sb" in block.column_id or "sidebar" in block.column_id
        loc = ParagraphLocation(
            type="text_box" if is_sidebar else "body",
            cell_width_pt=block.max_width_pt,
        )

        # Determine style_name & formatting cues for role classification
        style_name = "Normal"
        clean_text = block.text.strip()
        max_font_sz = max((s.font_size_pt for l in block.lines for s in l.spans), default=10.0)
        has_bold_span = any(s.flags.is_bold for l in block.lines for s in l.spans)

        # Check if block is candidate name
        if max_font_sz >= 18.0 and len(clean_text) > 3 and not _detect_section_heading(clean_text):
            style_name = "Title"
            if runs:
                runs[0].formatting.bold = True

        # Check if block is a section heading
        sec_heading_match = _detect_section_heading(clean_text)
        if sec_heading_match and (clean_text.isupper() or max_font_sz >= 11.0 or has_bold_span):
            style_name = "Heading 1"
            if runs:
                runs[0].formatting.bold = True

        # Dampen avatar icon initials (e.g. "MC") so they are not mistaken for name
        if len(clean_text) <= 3 and is_sidebar:
            for r in runs:
                r.formatting.font_size_pt = 9.0
                r.formatting.bold = False

        p_fp = ParagraphFingerprint(
            index=idx,
            location=loc,
            text=block.text,
            style_name=style_name,
            alignment=alignment,
            spacing=SpacingInfo(
                before_pt=block.spacing.before_pt,
                after_pt=block.spacing.after_pt,
                line_spacing_pt=round(block.spacing.line_height * 12.0, 1),
            ),
            indent=IndentInfo(
                left_pt=block.indent.left_pt,
                hanging_pt=block.indent.hanging_pt,
            ),
            bullet_info=BulletInfo(
                is_bullet=block.bullet_info.is_bullet,
                bullet_char=block.bullet_info.glyph,
            ),
            runs=runs,
            character_count=len(block.text),
            estimated_lines=len(block.lines),
        )
        paragraphs.append(p_fp)

    # Detect horizontal divider lines under section headings
    has_dividers = False
    if layout.vector_drawings:
        for d in layout.vector_drawings:
            r = getattr(d, "rect", None) or getattr(d, "bbox", [])
            w = abs(r[2] - r[0]) if len(r) >= 4 else 0
            h = abs(r[3] - r[1]) if len(r) >= 4 else 0
            if w > 150 and h < 8:
                has_dividers = True
                break

    # Detect header alignment from first few blocks (name, headline, contacts)
    detected_header_align = "left"
    for b in layout.blocks[:4]:
        if len(b.bbox) >= 4:
            b_center = (b.bbox[0] + b.bbox[2]) / 2
            if abs(b_center - (page_w / 2)) < 30.0 and (b.bbox[2] - b.bbox[0]) < (page_w * 0.85):
                detected_header_align = "center"
                break

    # Margins fallback
    margin_top = max(18.0, min_y) if min_y < page_h else 36.0
    margin_left = max(24.0, min_x) if min_x < page_w else 36.0
    margin_right = max(24.0, page_w - max_x) if max_x > 0 else 36.0
    margin_bottom = max(18.0, page_h - max_y) if max_y > 0 else 36.0

    metadata = DocumentMetadata(
        page_size=PageSizePt(
            name="A4" if abs(page_w - 595.3) < 10 else "Letter",
            width_pt=round(page_w, 1),
            height_pt=round(page_h, 1),
        ),
        margins=MarginsPt(
            top_pt=round(margin_top, 1),
            bottom_pt=round(margin_bottom, 1),
            left_pt=round(margin_left, 1),
            right_pt=round(margin_right, 1),
        ),
        default_font=DefaultFont(
            family="Helvetica",
            size_pt=10.0,
        ),
        page_count=layout.document_metadata.page_count,
        has_horizontal_dividers=has_dividers,
        header_alignment=detected_header_align,
        total_paragraphs=len(paragraphs),
        total_tables=0,
        has_text_boxes=any(p.location.type == "text_box" for p in paragraphs),
    )

    fingerprint = DocxFingerprint(
        document_metadata=metadata,
        paragraphs=paragraphs,
    )

    return fingerprint, block_map, para_to_line_boxes


def process_pdf_roles_and_content(
    layout: PdfLayout,
) -> Tuple[RoleMap, ResumeContent, ResumeStyle, Dict[str, List[int]], Dict[str, List[Dict[str, Any]]]]:
    """Runs the Phase 2 role classification and content/style extraction on a PdfLayout.

    Returns:
    - role_map: RoleMap
    - content: ResumeContent
    - style: ResumeStyle
    - content_to_paragraphs: Dict[str, List[int]]
    - content_to_line_boxes: Dict[str, List[Dict[str, Any]]] (maps content paths to line boxes with page info)
    """
    fingerprint, block_map, para_to_line_boxes = pdf_layout_to_fingerprint(layout)

    # 1. Reuse Phase 2 Role Classifier
    role_map = classify_paragraphs(fingerprint)

    # 2. Reuse Phase 2 Content & Style Extractor
    content, style, content_to_paragraphs = extract_content_and_style(fingerprint, role_map)

    # 3. Build content-item -> source line boxes mapping
    content_to_line_boxes: Dict[str, List[Dict[str, Any]]] = {}

    for c_key, p_indices in content_to_paragraphs.items():
        box_list = []
        for p_idx in p_indices:
            block = block_map.get(p_idx)
            if not block:
                continue
            for line in block.lines:
                box_list.append({
                    "line_id": line.line_id,
                    "page_number": block.page_number,
                    "bbox": line.bbox,
                    "baseline_origin": line.baseline_origin,
                    "text": line.text,
                    "max_width_pt": block.max_width_pt,
                })
        content_to_line_boxes[c_key] = box_list

    return role_map, content, style, content_to_paragraphs, content_to_line_boxes
