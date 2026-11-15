import io
import re
from typing import Dict, Any, Optional
import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from app.schemas.content import ResumeContent
from app.schemas.style import ResumeStyle


def hex_to_rgb(hex_str: str) -> RGBColor:
    """Converts #RRGGBB hex to docx RGBColor."""
    clean = hex_str.lstrip("#")
    if len(clean) == 3:
        clean = "".join(2 * c for c in clean)
    try:
        r = int(clean[0:2], 16)
        g = int(clean[2:4], 16)
        b = int(clean[4:6], 16)
        return RGBColor(r, g, b)
    except Exception:
        return RGBColor(15, 23, 42)


def set_cell_margins(cell, top=0, bottom=0, left=0, right=0):
    """Sets cell padding in dxa."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in (('top', top), ('bottom', bottom), ('left', left), ('right', right)):
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)


def add_formatted_runs(paragraph, text: str, default_font_size: Pt, default_color: RGBColor, is_bold: bool = False):
    """Parses safe inline markup (**bold**, *italic*, [link](url)) into docx runs."""
    if not text:
        return

    tokens = re.split(r"(\*\*[\s\S]+?\*\*|\*[^\s\*][\s\S]*?\*|\[[\s\S]+?\]\([^\s\)]+?\))", text)
    for tok in tokens:
        if not tok:
            continue
        if tok.startswith("**") and tok.endswith("**") and len(tok) >= 4:
            run = paragraph.add_run(tok[2:-2])
            run.font.bold = True
            run.font.size = default_font_size
            run.font.color.rgb = default_color
        elif tok.startswith("*") and tok.endswith("*") and len(tok) >= 2 and not tok.startswith("**"):
            run = paragraph.add_run(tok[1:-1])
            run.font.italic = True
            run.font.size = default_font_size
            run.font.color.rgb = default_color
        elif tok.startswith("[") and "](" in tok and tok.endswith(")"):
            m = re.match(r"^\[([\s\S]+?)\]\(([^\s\)]+?)\)$", tok)
            if m:
                label, url = m.groups()
                run = paragraph.add_run(label)
                run.font.underline = True
                run.font.size = default_font_size
                run.font.color.rgb = RGBColor(37, 99, 235)
            else:
                run = paragraph.add_run(tok)
                run.font.size = default_font_size
                run.font.color.rgb = default_color
        else:
            run = paragraph.add_run(tok)
            run.font.bold = is_bold
            run.font.size = default_font_size
            run.font.color.rgb = default_color


def export_resume_to_docx(content_dict: Dict[str, Any], style_dict: Optional[Dict[str, Any]] = None) -> bytes:
    """Renders ResumeContent and ResumeStyle into an editable Word document (.docx)

    with matching typography, colors, margins, and section structure.
    """
    content = ResumeContent.model_validate(content_dict)
    style = ResumeStyle.model_validate(style_dict) if style_dict else None

    doc = docx.Document()

    # Colors & Fonts setup
    accent_rgb = hex_to_rgb(style.colors.accent if style else "#2563eb")
    text_rgb = hex_to_rgb(style.colors.text if style else "#0f172a")
    muted_rgb = hex_to_rgb(style.colors.muted if style else "#64748b")
    font_name = style.typography.baseFontFamily if style else "Calibri"

    # Set page margins
    sections = doc.sections
    if sections:
        sec = sections[0]
        if style:
            sec.top_margin = Inches(style.margins.top * 0.0138)  # pt to inches or direct inches
            sec.bottom_margin = Inches(style.margins.bottom * 0.0138)
            sec.left_margin = Inches(style.margins.left * 0.0138)
            sec.right_margin = Inches(style.margins.right * 0.0138)
        else:
            sec.top_margin = Inches(0.6)
            sec.bottom_margin = Inches(0.6)
            sec.left_margin = Inches(0.6)
            sec.right_margin = Inches(0.6)

    # 1. Candidate Header
    p_name = doc.add_paragraph()
    p_name.paragraph_format.space_before = Pt(0)
    p_name.paragraph_format.space_after = Pt(2)
    p_name.alignment = WD_ALIGN_PARAGRAPH.CENTER

    name_run = p_name.add_run(content.header.name or "Untitled Resume")
    name_run.font.name = font_name
    name_run.font.size = Pt(22)
    name_run.font.bold = True
    name_run.font.color.rgb = accent_rgb

    if content.header.title:
        p_title = doc.add_paragraph()
        p_title.paragraph_format.space_before = Pt(0)
        p_title.paragraph_format.space_after = Pt(4)
        p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        title_run = p_title.add_run(content.header.title)
        title_run.font.name = font_name
        title_run.font.size = Pt(12)
        title_run.font.color.rgb = muted_rgb

    # Contact Info Line
    contact_parts = []
    if content.header.email:
        contact_parts.append(content.header.email)
    if content.header.phone:
        contact_parts.append(content.header.phone)
    if content.header.location:
        contact_parts.append(content.header.location)
    if content.header.website:
        contact_parts.append(content.header.website)
    if content.header.links:
        for link in content.header.links:
            contact_parts.append(f"{link.label}: {link.url}")

    if contact_parts:
        p_contact = doc.add_paragraph()
        p_contact.paragraph_format.space_before = Pt(0)
        p_contact.paragraph_format.space_after = Pt(12)
        p_contact.alignment = WD_ALIGN_PARAGRAPH.CENTER
        contact_run = p_contact.add_run("  |  ".join(contact_parts))
        contact_run.font.name = font_name
        contact_run.font.size = Pt(9.5)
        contact_run.font.color.rgb = muted_rgb

    # 2. Sections
    for section in content.sections:
        if not section.visible or not section.items:
            continue

        # Section Heading
        p_heading = doc.add_paragraph()
        p_heading.paragraph_format.space_before = Pt(10)
        p_heading.paragraph_format.space_after = Pt(4)
        p_heading.paragraph_format.keep_with_next = True

        h_run = p_heading.add_run(section.title.upper())
        h_run.font.name = font_name
        h_run.font.size = Pt(11.5)
        h_run.font.bold = True
        h_run.font.color.rgb = accent_rgb

        # Horizontal Rule under heading
        p_rule = doc.add_paragraph()
        p_rule.paragraph_format.space_before = Pt(0)
        p_rule.paragraph_format.space_after = Pt(6)
        rule_run = p_rule.add_run("―" * 58)
        rule_run.font.size = Pt(6)
        rule_run.font.color.rgb = muted_rgb

        # Items
        for item in section.items:
            if item.visible is False:
                continue

            # Item title line
            has_title_line = bool(item.title or item.subtitle or item.dateRange or item.location)
            if has_title_line:
                p_item = doc.add_paragraph()
                p_item.paragraph_format.space_before = Pt(4)
                p_item.paragraph_format.space_after = Pt(2)
                p_item.paragraph_format.keep_with_next = True

                if item.title:
                    add_formatted_runs(p_item, item.title, Pt(10.5), text_rgb, is_bold=True)

                if item.subtitle:
                    sub_prefix = "  |  " if item.title else ""
                    add_formatted_runs(p_item, f"{sub_prefix}{item.subtitle}", Pt(10), muted_rgb)

                meta_parts = []
                if item.dateRange:
                    meta_parts.append(item.dateRange)
                if item.location:
                    meta_parts.append(item.location)
                if meta_parts:
                    meta_run = p_item.add_run(f"    ({', '.join(meta_parts)})")
                    meta_run.font.size = Pt(9)
                    meta_run.font.italic = True
                    meta_run.font.color.rgb = muted_rgb

            # Bullets
            if item.bullets:
                for b in item.bullets:
                    if not b.text.strip():
                        continue
                    p_b = doc.add_paragraph(style='List Bullet')
                    p_b.paragraph_format.space_before = Pt(1)
                    p_b.paragraph_format.space_after = Pt(2)
                    p_b.paragraph_format.left_indent = Inches(0.25 * ((b.level or 0) + 1))
                    add_formatted_runs(p_b, b.text.strip(), Pt(9.5), text_rgb)

    # Save to buffer
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()
