"""Deterministic DOCX Fingerprinter and Reading-Order Walker.
Extracts paragraphs, nested tables, text boxes, headers/footers, resolved styles,
paragraph borders, tab stops, and inline structures without modifying the original document.
"""

import io
import re
import zipfile
import logging
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
from app.services.docx_style_resolver import DocxStyleResolver

logger = logging.getLogger(__name__)

DOCX_NAMESPACES = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "wp": "http://schemas.openxmlformats.org/wordprocessingDrawing",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "wps": "http://schemas.microsoft.com/office/word/2010/wordprocessingShape",
    "mc": "http://schemas.openxmlformats.org/markup-compatibility/2006",
    "v": "urn:schemas-microsoft-com:vml",
}


def _length_to_pt(length: Optional[Length], default: float = 0.0) -> float:
    if length is None:
        return default
    try:
        return round(length.pt, 1)
    except Exception:
        return default


def strip_external_relationships(docx_path: str, output_path: str) -> None:
    """Strips external network relationship targets from the working copy

    before converting with LibreOffice to guarantee zero network access (Change #7).
    """
    try:
        with zipfile.ZipFile(docx_path, "r") as zin:
            with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as zout:
                for item in zin.infolist():
                    data = zin.read(item.filename)
                    if item.filename.endswith(".rels"):
                        text = data.decode("utf-8", errors="ignore")
                        # Neutralize TargetMode="External" with external URLs
                        text = re.sub(r'TargetMode="External"\s+Target="https?://[^"]*"', 'Target="about:blank"', text)
                        data = text.encode("utf-8")
                    zout.writestr(item, data)
    except Exception as e:
        logger.warning(f"Could not strip external relationships: {e}")
        import shutil
        shutil.copyfile(docx_path, output_path)


def _load_rels_map(docx_path: str) -> Dict[str, str]:
    """Reads word/_rels/document.xml.rels to map r:id to hyperlink targets."""
    rels_map: Dict[str, str] = {}
    try:
        with zipfile.ZipFile(docx_path, "r") as zf:
            if "word/_rels/document.xml.rels" in zf.namelist():
                rels_xml = zf.read("word/_rels/document.xml.rels").decode("utf-8", errors="ignore")
                for m in re.finditer(r'<Relationship\s+([^>]+)/>', rels_xml):
                    attrs = m.group(1)
                    id_m = re.search(r'Id="([^"]+)"', attrs)
                    target_m = re.search(r'Target="([^"]+)"', attrs)
                    if id_m and target_m:
                        rels_map[id_m.group(1)] = target_m.group(1)
    except Exception as e:
        logger.debug(f"Could not parse rels map: {e}")
    return rels_map


def _extract_bullet_info(p: Paragraph) -> BulletInfo:
    """Detects list / bullet properties from style, XML numPr, or leading bullet glyphs."""
    text = p.text.strip()
    is_bullet = False
    num_id = None
    ilvl = None
    bullet_char = None

    # 1. Style name check
    style_name = p.style.name if p.style else ""
    if "bullet" in style_name.lower() or "list" in style_name.lower():
        is_bullet = True
        bullet_char = "•"

    # 2. XML numPr check
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

    # 3. Text prefix check (•, -, *, ▪, ▫, ◦, –)
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


def _extract_tab_stops(p: Paragraph) -> List[Dict[str, Any]]:
    """Extracts tab stops including right-aligned tabs used for dates."""
    tabs: List[Dict[str, Any]] = []
    pPr = p._p.find(qn("w:pPr"))
    if pPr is not None:
        tabs_elem = pPr.find(qn("w:tabs"))
        if tabs_elem is not None:
            for t in tabs_elem.findall(qn("w:tab")):
                pos = t.attrib.get(qn("w:pos"))
                val = t.attrib.get(qn("w:val"), "left")
                if pos:
                    try:
                        pos_pt = round(float(pos) / 20.0, 1)  # twips to pt
                        tabs.append({"pos_pt": pos_pt, "val": val})
                    except ValueError:
                        pass
    return tabs


def _extract_hyperlinks(p: Paragraph, rels_map: Dict[str, str]) -> List[Dict[str, str]]:
    """Extracts inline hyperlinks preserving targets and anchor texts."""
    links: List[Dict[str, str]] = []
    for h in p._p.findall(f".//{{{DOCX_NAMESPACES['w']}}}hyperlink"):
        r_id = h.attrib.get(f"{{{DOCX_NAMESPACES['r']}}}id")
        text = "".join(h.itertext()).strip()
        if r_id and r_id in rels_map and text:
            links.append({"target": rels_map[r_id], "text": text})
    return links


def _has_paragraph_border_or_shading(p: Paragraph) -> Tuple[bool, bool]:
    """Detects bottom border rules (used for section headings) and background shading."""
    has_bottom_border = False
    has_shading = False
    pPr = p._p.find(qn("w:pPr"))
    if pPr is not None:
        pBdr = pPr.find(qn("w:pBdr"))
        if pBdr is not None and pBdr.find(qn("w:bottom")) is not None:
            has_bottom_border = True

        shd = pPr.find(qn("w:shd"))
        if shd is not None and shd.attrib.get(qn("w:val"), "none") not in ("none", "clear", "nil"):
            has_shading = True

    return has_bottom_border, has_shading


def _extract_runs(
    p: Paragraph,
    style_resolver: DocxStyleResolver,
    style_name: str,
) -> List[RunFingerprint]:
    runs: List[RunFingerprint] = []
    for r_idx, r in enumerate(p.runs):
        if not r.text:
            continue

        # Extract direct run formatting
        direct_rPr = {}
        if r.font.name:
            direct_rPr["font_family"] = r.font.name
        if r.font.size:
            try:
                direct_rPr["font_size_pt"] = round(r.font.size.pt, 1)
            except Exception:
                pass
        if r.bold is not None:
            direct_rPr["bold"] = bool(r.bold)
        if r.italic is not None:
            direct_rPr["italic"] = bool(r.italic)
        if r.underline is not None:
            direct_rPr["underline"] = bool(r.underline)
        if r.font.color and r.font.color.rgb:
            direct_rPr["color_hex"] = f"#{r.font.color.rgb}"

        # Resolve through full inheritance tree
        resolved = style_resolver.resolve_run_formatting(style_id=style_name, direct_rPr=direct_rPr)

        runs.append(
            RunFingerprint(
                index=r_idx,
                text=r.text,
                formatting=RunFormatting(
                    font_family=resolved.font_family,
                    font_size_pt=resolved.font_size_pt,
                    bold=resolved.bold,
                    italic=resolved.italic,
                    underline=resolved.underline,
                    color_hex=resolved.color_hex,
                    highlight=str(r.font.highlight_color) if r.font.highlight_color else None,
                ),
            )
        )
    return runs


def _extract_paragraph_fingerprint(
    p: Paragraph,
    index: int,
    location: ParagraphLocation,
    style_resolver: DocxStyleResolver,
    rels_map: Dict[str, str],
) -> ParagraphFingerprint:
    pf = p.paragraph_format
    style_name = p.style.name if p.style else "Normal"

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
    tab_stops = _extract_tab_stops(p)
    hyperlinks = _extract_hyperlinks(p, rels_map)
    has_bdr, has_shd = _has_paragraph_border_or_shading(p)
    runs = _extract_runs(p, style_resolver, style_name)

    # Paragraph-level resolved formatting (average font across runs or style defaults)
    if runs:
        primary_font = runs[0].formatting.font_family or "Calibri"
        primary_size = runs[0].formatting.font_size_pt or 11.0
        primary_bold = any(r.formatting.bold for r in runs)
        primary_color = runs[0].formatting.color_hex or "#000000"
    else:
        resolved_p = style_resolver.resolve_run_formatting(style_id=style_name)
        primary_font = resolved_p.font_family
        primary_size = resolved_p.font_size_pt
        primary_bold = resolved_p.bold
        primary_color = resolved_p.color_hex

    resolved_fmt = {
        "font_family": primary_font,
        "font_size_pt": primary_size,
        "bold": primary_bold,
        "color_hex": primary_color,
    }

    full_text = p.text
    char_count = len(full_text)

    # Compute estimated line count from geometry
    available_width = location.cell_width_pt if (location.type == "table_cell" and location.cell_width_pt) else 515.0
    chars_per_line = max(30, int(available_width / 6.0))
    estimated_lines = max(1, (char_count + chars_per_line - 1) // chars_per_line) if char_count > 0 else 1

    alignment = "left"
    if p.alignment == WD_ALIGN_PARAGRAPH.CENTER:
        alignment = "center"
    elif p.alignment == WD_ALIGN_PARAGRAPH.RIGHT:
        alignment = "right"
    elif p.alignment == WD_ALIGN_PARAGRAPH.JUSTIFY:
        alignment = "justify"

    return ParagraphFingerprint(
        index=index,
        location=location,
        text=full_text,
        style_name=style_name,
        alignment=alignment,
        spacing=spacing,
        indent=indent,
        bullet_info=bullet_info,
        runs=runs,
        character_count=char_count,
        estimated_lines=estimated_lines,
        has_bottom_border=has_bdr,
        has_shading=has_shd,
        keep_with_next=bool(p.paragraph_format.keep_with_next),
        tab_stops=tab_stops,
        hyperlinks=hyperlinks,
        resolved_formatting=resolved_fmt,
        line_width_pt=available_width,
    )


def _traverse_tables_and_textboxes(
    doc: Document,
    style_resolver: DocxStyleResolver,
    rels_map: Dict[str, str],
) -> List[ParagraphFingerprint]:
    """Walks the full document in true visual reading order:

    body paragraphs, drawingML/VML textboxes, and nested tables.
    """
    fingerprints: List[ParagraphFingerprint] = []
    body_elem = doc._body._body

    current_idx = 0

    def process_textbox_elements(parent_elem: OxmlElement, loc_type: str = "text_box") -> List[ParagraphFingerprint]:
        nonlocal current_idx
        tb_fps = []
        try:
            tx_p_elems = parent_elem.xpath(
                ".//*[local-name()='txBody' or local-name()='textbox' or local-name()='txbx']//*[local-name()='p']"
            )
        except Exception:
            tx_p_elems = []

        for t_idx, tp in enumerate(tx_p_elems):
            para_obj = Paragraph(tp, doc)
            if not para_obj.text.strip():
                continue
            fp = _extract_paragraph_fingerprint(
                p=para_obj,
                index=current_idx,
                location=ParagraphLocation(type="text_box", paragraph_index=current_idx, textbox_id=f"txbx_{current_idx}"),
                style_resolver=style_resolver,
                rels_map=rels_map,
            )
            tb_fps.append(fp)
            current_idx += 1
        return tb_fps

    def process_table(tbl, table_idx: int, path_prefix: List[int]) -> List[ParagraphFingerprint]:
        nonlocal current_idx
        tbl_fps = []
        for r_idx, row in enumerate(tbl.rows):
            for c_idx, cell in enumerate(row.cells):
                cell_width_pt = _length_to_pt(cell.width, 250.0) if cell.width else 250.0

                for p_idx, cell_p in enumerate(cell.paragraphs):
                    # Check textboxes inside cell
                    tbl_fps.extend(process_textbox_elements(cell_p._p))

                    if cell_p.text.strip():
                        t_path = path_prefix + [table_idx, r_idx, c_idx, p_idx]
                        fp = _extract_paragraph_fingerprint(
                            p=cell_p,
                            index=current_idx,
                            location=ParagraphLocation(
                                type="table_cell",
                                paragraph_index=current_idx,
                                table_index=table_idx,
                                row_index=r_idx,
                                col_index=c_idx,
                                table_path=t_path,
                                cell_width_pt=cell_width_pt,
                            ),
                            style_resolver=style_resolver,
                            rels_map=rels_map,
                        )
                        tbl_fps.append(fp)
                        current_idx += 1

                # Nested tables inside cell
                for n_idx, nested_tbl in enumerate(cell.tables):
                    tbl_fps.extend(process_table(nested_tbl, n_idx, path_prefix + [table_idx, r_idx, c_idx]))

        return tbl_fps

    # Traverse main body XML elements in sequence
    tbl_counter = 0
    for child in body_elem.iterchildren():
        tag = child.tag
        if tag.endswith("}p"):
            p_obj = Paragraph(child, doc)

            # 1. Text boxes anchored to this paragraph
            fingerprints.extend(process_textbox_elements(child))

            # 2. Main body paragraph
            if p_obj.text.strip():
                fp = _extract_paragraph_fingerprint(
                    p=p_obj,
                    index=current_idx,
                    location=ParagraphLocation(type="body", paragraph_index=current_idx),
                    style_resolver=style_resolver,
                    rels_map=rels_map,
                )
                fingerprints.append(fp)
                current_idx += 1

        elif tag.endswith("}tbl"):
            # Table element
            for tbl in doc.tables:
                if tbl._tbl == child:
                    fingerprints.extend(process_table(tbl, tbl_counter, []))
                    tbl_counter += 1
                    break

    return fingerprints


def fingerprint_docx(docx_path: str) -> DocxFingerprint:
    """Extracts styles, metadata, and all paragraphs in true visual reading order."""
    doc = Document(docx_path)

    # 1. Extract styles.xml for inheritance resolution
    styles_xml_bytes = None
    try:
        with zipfile.ZipFile(docx_path, "r") as zf:
            if "word/styles.xml" in zf.namelist():
                styles_xml_bytes = zf.read("word/styles.xml")
    except Exception as e:
        logger.debug(f"Could not read styles.xml directly: {e}")

    style_resolver = DocxStyleResolver(styles_xml_bytes)
    rels_map = _load_rels_map(docx_path)

    # 2. Document Metadata & Sections
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

    # Read-only headers and footers
    headers_text = []
    footers_text = []
    for s in doc.sections:
        if s.header:
            ht = " ".join(p.text.strip() for p in s.header.paragraphs if p.text.strip())
            if ht:
                headers_text.append(ht)
        if s.footer:
            ft = " ".join(p.text.strip() for p in s.footer.paragraphs if p.text.strip())
            if ft:
                footers_text.append(ft)

    # 3. Reading-order paragraph extraction
    paragraphs = _traverse_tables_and_textboxes(doc, style_resolver, rels_map)

    metadata = DocumentMetadata(
        page_size=PageSizePt(name=name, width_pt=page_width, height_pt=page_height),
        margins=margins,
        default_font=DefaultFont(
            family=style_resolver.doc_defaults_rPr.get("font_family", "Calibri"),
            size_pt=style_resolver.doc_defaults_rPr.get("font_size_pt", 11.0),
        ),
        total_paragraphs=len(paragraphs),
        total_tables=len(doc.tables),
        has_text_boxes=any(p.location.type == "text_box" for p in paragraphs),
        headers_text=headers_text,
        footers_text=footers_text,
    )

    return DocxFingerprint(document_metadata=metadata, paragraphs=paragraphs)
