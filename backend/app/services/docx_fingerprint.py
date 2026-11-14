import re
from typing import List, Optional, Tuple, Dict, Any
from docx import Document
from docx.shared import Pt, Inches, Length
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph

from app.schemas.template import (
    DocxFingerprint,
    DocumentMetadata,
    PageSizePt,
    MarginsPt,
    DefaultFont,
    ParagraphFingerprint,
    ParagraphLocation,
    SpacingInfo,
    IndentInfo,
    BulletInfo,
    RunFingerprint,
    RunFormatting,
)


def _length_to_pt(length: Optional[Length], default: float = 0.0) -> float:
    if length is None:
        return default
    try:
        return round(length.pt, 1)
    except Exception:
        return default


def _extract_bullet_info(p: Paragraph) -> BulletInfo:
    """Detects list / bullet properties from style, XML numPr, or leading bullet glyphs."""
    text = p.text.strip()
    is_bullet = False
    num_id = None
    ilvl = None
    bullet_char = None

    # 1. Check style name
    style_name = p.style.name if p.style else ""
    if "bullet" in style_name.lower() or "list" in style_name.lower():
        is_bullet = True
        bullet_char = "•"

    # 2. Check XML numPr
    numPr = p._p.find(qn("w:pPr"))
    if numPr is not None:
        numPr_elem = numPr.find(qn("w:numPr"))
        if numPr_elem is not None:
            is_bullet = True
            num_elem = numPr_elem.find(qn("w:numId"))
            if num_elem is not None and "val" in num_elem.attrib:
                try:
                    num_id = int(num_elem.attrib[qn("w:val")])
                except Exception:
                    pass
            ilvl_elem = numPr_elem.find(qn("w:ilvl"))
            if ilvl_elem is not None and "val" in ilvl_elem.attrib:
                try:
                    ilvl = int(ilvl_elem.attrib[qn("w:val")])
                except Exception:
                    pass
            if not bullet_char:
                bullet_char = "•"

    # 3. Check text prefix (•, -, *, ▪, ◦)
    bullet_regex = r"^([\u2022\u25E6\u25AA\u25AB\u2013\u2014\-*])\s+"
    m = re.match(bullet_regex, text)
    if m:
        is_bullet = True
        bullet_char = m.group(1)

    return BulletInfo(
        is_bullet=is_bullet,
        num_id=num_id,
        ilvl=ilvl,
        bullet_char=bullet_char,
    )


def _extract_alignment(p: Paragraph) -> Optional[str]:
    align = p.alignment
    if align == WD_ALIGN_PARAGRAPH.CENTER:
        return "center"
    elif align == WD_ALIGN_PARAGRAPH.RIGHT:
        return "right"
    elif align == WD_ALIGN_PARAGRAPH.JUSTIFY:
        return "justify"
    elif align == WD_ALIGN_PARAGRAPH.LEFT:
        return "left"
    return "left"


def _extract_runs(p: Paragraph, default_font_family: str, default_font_size: float) -> List[RunFingerprint]:
    runs: List[RunFingerprint] = []
    for r_idx, r in enumerate(p.runs):
        if not r.text:
            continue

        font_family = r.font.name or default_font_family
        font_size = _length_to_pt(r.font.size, default_font_size) if r.font.size else default_font_size
        bold = bool(r.bold)
        italic = bool(r.italic)
        underline = bool(r.underline)

        # Color
        color_hex = None
        if r.font.color and r.font.color.rgb:
            color_hex = f"#{r.font.color.rgb}"
        elif r.font.color and r.font.color.theme_color:
            color_hex = "#111827"  # fallback dark theme
        else:
            color_hex = "#111827"

        runs.append(
            RunFingerprint(
                index=r_idx,
                text=r.text,
                formatting=RunFormatting(
                    font_family=font_family,
                    font_size_pt=font_size,
                    bold=bold,
                    italic=italic,
                    underline=underline,
                    color_hex=color_hex,
                    highlight=str(r.font.highlight_color) if r.font.highlight_color else None,
                ),
            )
        )
    return runs


def _extract_paragraph_fingerprint(
    p: Paragraph,
    index: int,
    location: ParagraphLocation,
    default_font_family: str,
    default_font_size: float,
) -> ParagraphFingerprint:
    pf = p.paragraph_format

    spacing = SpacingInfo(
        before_pt=_length_to_pt(pf.space_before, 0.0),
        after_pt=_length_to_pt(pf.space_after, 0.0),
        line_spacing_pt=_length_to_pt(pf.line_spacing, None) if isinstance(pf.line_spacing, Length) else None,
        line_spacing_rule=str(pf.line_spacing_rule) if pf.line_spacing_rule else None,
    )

    indent = IndentInfo(
        left_pt=_length_to_pt(pf.left_indent, 0.0),
        right_pt=_length_to_pt(pf.right_indent, 0.0),
        first_line_pt=_length_to_pt(pf.first_line_indent, 0.0),
        hanging_pt=abs(_length_to_pt(pf.first_line_indent, 0.0)) if pf.first_line_indent and pf.first_line_indent.pt < 0 else 0.0,
    )

    bullet_info = _extract_bullet_info(p)
    alignment = _extract_alignment(p)
    runs = _extract_runs(p, default_font_family, default_font_size)

    full_text = p.text
    char_count = len(full_text)

    # Estimate line count based on character budget: ~85 chars per line in full width, ~45 in sidebar
    chars_per_line = 45 if location.type == "table_cell" and location.cell_width_pt and location.cell_width_pt < 250 else 85
    estimated_lines = max(1, (char_count + chars_per_line - 1) // chars_per_line) if char_count > 0 else 1

    return ParagraphFingerprint(
        index=index,
        location=location,
        text=full_text,
        style_name=p.style.name if p.style else "Normal",
        alignment=alignment,
        spacing=spacing,
        indent=indent,
        bullet_info=bullet_info,
        runs=runs,
        character_count=char_count,
        estimated_lines=estimated_lines,
    )


DOCX_NAMESPACES = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "wps": "http://schemas.microsoft.com/office/word/2010/wordprocessingShape",
    "v": "urn:schemas-microsoft-com:vml",
}


def _extract_text_boxes(p_elem: OxmlElement, current_index: int, doc: Document, default_font: DefaultFont) -> List[ParagraphFingerprint]:
    """Finds drawingML (w:txBody) or VML (v:textbox) paragraphs inside a paragraph."""
    results: List[ParagraphFingerprint] = []

    try:
        txbx_p_elems = p_elem.xpath(
            ".//*[local-name()='txBody' or local-name()='textbox' or local-name()='txbx']//*[local-name()='p']"
        )
    except Exception:
        txbx_p_elems = []

    for t_idx, tp_elem in enumerate(txbx_p_elems):
        para_obj = Paragraph(tp_elem, doc)
        if not para_obj.text.strip():
            continue
        fp = _extract_paragraph_fingerprint(
            p=para_obj,
            index=current_index + len(results),
            location=ParagraphLocation(type="text_box"),
            default_font_family=default_font.family,
            default_font_size=default_font.size_pt,
        )
        results.append(fp)

    return results


def fingerprint_docx(docx_path: str) -> DocxFingerprint:
    """Walks the DOCX body paragraphs, tables, and text boxes without modifying the file

    and generates a complete fingerprint JSON.
    """
    doc = Document(docx_path)

    # 1. Document Metadata
    section = doc.sections[0] if doc.sections else None
    if section:
        page_width = _length_to_pt(section.page_width, 595.3)
        page_height = _length_to_pt(section.page_height, 841.9)
        name = "A4" if abs(page_width - 595.3) < 20 else "Letter"

        margins = MarginsPt(
            top_pt=_length_to_pt(section.top_margin, 36.0),
            bottom_pt=_length_to_pt(section.bottom_margin, 36.0),
            left_pt=_length_to_pt(section.left_margin, 40.0),
            right_pt=_length_to_pt(section.right_margin, 40.0),
        )
    else:
        page_width, page_height, name = 595.3, 841.9, "A4"
        margins = MarginsPt()

    # Headers & Footers (read-only)
    headers_text = []
    footers_text = []
    for s in doc.sections:
        if s.header:
            h_txt = "\n".join([p.text.strip() for p in s.header.paragraphs if p.text.strip()])
            if h_txt:
                headers_text.append(h_txt)
        if s.footer:
            f_txt = "\n".join([p.text.strip() for p in s.footer.paragraphs if p.text.strip()])
            if f_txt:
                footers_text.append(f_txt)

    default_font = DefaultFont(family="Calibri", size_pt=10.5)

    paragraphs_fingerprints: List[ParagraphFingerprint] = []
    para_counter = 0
    total_tables = len(doc.tables)
    has_text_boxes = False

    # 2. Iterate in Document Order through the body elements
    body_elem = doc._body._body
    for child in body_elem.iterchildren():
        if child.tag == qn("w:p"):
            p_obj = Paragraph(child, doc)

            # Check for embedded text boxes
            tx_fps = _extract_text_boxes(child, para_counter, doc, default_font)
            if tx_fps:
                has_text_boxes = True
                for tx_fp in tx_fps:
                    paragraphs_fingerprints.append(tx_fp)
                    para_counter += 1

            # Main paragraph (if it has text or is meaningful)
            if p_obj.text.strip():
                fp = _extract_paragraph_fingerprint(
                    p=p_obj,
                    index=para_counter,
                    location=ParagraphLocation(type="body"),
                    default_font_family=default_font.family,
                    default_font_size=default_font.size_pt,
                )
                paragraphs_fingerprints.append(fp)
                para_counter += 1

        elif child.tag == qn("w:tbl"):
            # Table element
            table_idx = 0
            for idx, tbl in enumerate(doc.tables):
                if tbl._tbl == child:
                    table_idx = idx
                    break

            tbl_obj = doc.tables[table_idx]
            for row_idx, row in enumerate(tbl_obj.rows):
                for col_idx, cell in enumerate(row.cells):
                    cell_width = _length_to_pt(cell.width, 250.0)
                    for cell_p in cell.paragraphs:
                        if cell_p.text.strip():
                            fp = _extract_paragraph_fingerprint(
                                p=cell_p,
                                index=para_counter,
                                location=ParagraphLocation(
                                    type="table_cell",
                                    table_index=table_idx,
                                    row_index=row_idx,
                                    col_index=col_idx,
                                    cell_width_pt=cell_width,
                                ),
                                default_font_family=default_font.family,
                                default_font_size=default_font.size_pt,
                            )
                            paragraphs_fingerprints.append(fp)
                            para_counter += 1

    metadata = DocumentMetadata(
        page_size=PageSizePt(name=name, width_pt=page_width, height_pt=page_height),
        margins=margins,
        default_font=default_font,
        total_paragraphs=len(paragraphs_fingerprints),
        total_tables=total_tables,
        has_text_boxes=has_text_boxes,
        headers_text=headers_text,
        footers_text=footers_text,
    )

    return DocxFingerprint(
        document_metadata=metadata,
        paragraphs=paragraphs_fingerprints,
    )
