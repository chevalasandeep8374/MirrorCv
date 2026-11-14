import copy
import re
from typing import Dict, List, Optional
from docx import Document
from docx.text.paragraph import Paragraph
from docx.oxml import OxmlElement

from app.schemas.content import ResumeContent


def _collect_all_paragraphs_in_order(doc: Document) -> List[Paragraph]:
    """Collects all paragraphs across body, table cells, and text boxes

    in the exact same sequence as the fingerprinter.
    """
    paragraphs: List[Paragraph] = []
    body_elem = doc._body._body

    for child in body_elem.iterchildren():
        if child.tag.endswith("}p"):
            p_obj = Paragraph(child, doc)

            # Check text boxes inside child paragraph
            try:
                tx_p_elems = child.xpath(
                    ".//*[local-name()='txBody' or local-name()='textbox' or local-name()='txbx']//*[local-name()='p']"
                )
            except Exception:
                tx_p_elems = []

            for tp in tx_p_elems:
                t_obj = Paragraph(tp, doc)
                if t_obj.text.strip():
                    paragraphs.append(t_obj)

            if p_obj.text.strip():
                paragraphs.append(p_obj)

        elif child.tag.endswith("}tbl"):
            # Table element
            for tbl in doc.tables:
                if tbl._tbl == child:
                    for row in tbl.rows:
                        for cell in row.cells:
                            for cell_p in cell.paragraphs:
                                if cell_p.text.strip():
                                    paragraphs.append(cell_p)
                    break

    return paragraphs


def _replace_paragraph_text_preserving_runs(p: Paragraph, new_text: str):
    """Replaces paragraph text while preserving run-level formatting

    such as bold lead-ins followed by normal text.
    """
    if not p.runs:
        p.add_run(new_text)
        return

    if len(p.runs) == 1:
        p.runs[0].text = new_text
        return

    # Check if first run is a bold lead-in
    first_run_bold = bool(p.runs[0].bold)
    second_run_bold = bool(p.runs[1].bold)

    if first_run_bold and not second_run_bold:
        # Split on colon, dash, or first 3 words
        if ":" in new_text:
            parts = new_text.split(":", 1)
            lead_in = parts[0] + ":"
            rest = parts[1]
        elif "—" in new_text:
            parts = new_text.split("—", 1)
            lead_in = parts[0] + " —"
            rest = parts[1]
        else:
            words = new_text.split()
            if len(words) > 3:
                lead_in = " ".join(words[:3])
                rest = " " + " ".join(words[3:])
            else:
                lead_in = new_text
                rest = ""

        p.runs[0].text = lead_in
        p.runs[1].text = rest
        for r in p.runs[2:]:
            r.text = ""
    else:
        # Distribute into run 0, clear others
        p.runs[0].text = new_text
        for r in p.runs[1:]:
            r.text = ""


def write_tailored_docx(
    template_docx_path: str,
    tailored_content: ResumeContent,
    content_to_paragraphs: Dict[str, List[int]],
    output_docx_path: str,
) -> str:
    """Writes tailored resume content back into the master DOCX template in-place.

    Preserves runs, margins, styles, and fonts. Performs XML deep-copy cloning
    when extra bullets are present and deletes unused bullet paragraphs.
    """
    doc = Document(template_docx_path)
    all_paragraphs = _collect_all_paragraphs_in_order(doc)

    # 1. Update Header (Name & Contact)
    name_indices = content_to_paragraphs.get("header.name", [])
    if name_indices and name_indices[0] < len(all_paragraphs):
        _replace_paragraph_text_preserving_runs(all_paragraphs[name_indices[0]], tailored_content.header.name)

    title_indices = content_to_paragraphs.get("header.title", [])
    if title_indices and title_indices[0] < len(all_paragraphs) and tailored_content.header.title:
        _replace_paragraph_text_preserving_runs(all_paragraphs[title_indices[0]], tailored_content.header.title)

    # 2. Update Sections & Items
    for section in tailored_content.sections:
        sec_id = section.id

        # Update Section Heading Title
        h_indices = content_to_paragraphs.get(f"{sec_id}.title", [])
        if h_indices and h_indices[0] < len(all_paragraphs):
            _replace_paragraph_text_preserving_runs(all_paragraphs[h_indices[0]], section.title)

        if section.type == "summary":
            # Update summary body
            for item in section.items:
                for bullet in item.bullets:
                    b_indices = content_to_paragraphs.get(f"{sec_id}.{item.id}.{bullet.id}", [])
                    if not b_indices:
                        b_indices = content_to_paragraphs.get(f"{sec_id}.summary", [])
                    if b_indices and b_indices[0] < len(all_paragraphs):
                        _replace_paragraph_text_preserving_runs(all_paragraphs[b_indices[0]], bullet.text)

        elif section.type == "skills":
            # Update skills
            for item in section.items:
                for bullet in item.bullets:
                    b_indices = content_to_paragraphs.get(f"{sec_id}.{item.id}.{bullet.id}", [])
                    if b_indices and b_indices[0] < len(all_paragraphs):
                        # Reconstruct "Category: skills" if item has title
                        new_txt = f"{item.title}: {bullet.text}" if item.title and not item.title.startswith("Skill Group") else bullet.text
                        _replace_paragraph_text_preserving_runs(all_paragraphs[b_indices[0]], new_txt)

        else:
            # Experience, Education, Projects, Certifications
            for item in section.items:
                # Update Item Title
                t_indices = content_to_paragraphs.get(f"{sec_id}.{item.id}.title", [])
                if t_indices and t_indices[0] < len(all_paragraphs):
                    full_title = f"{item.title} — {item.subtitle}" if item.subtitle else item.title
                    _replace_paragraph_text_preserving_runs(all_paragraphs[t_indices[0]], full_title)

                # Update or Clone Bullets
                # Find all original bullet paragraph indices for this item
                orig_bullet_indices = []
                for k, indices in content_to_paragraphs.items():
                    if k.startswith(f"{sec_id}.{item.id}.b-"):
                        orig_bullet_indices.extend(indices)

                tailored_bullets = item.bullets or []
                last_bullet_p: Optional[Paragraph] = None

                # Update existing bullets
                for idx, bullet in enumerate(tailored_bullets):
                    if idx < len(orig_bullet_indices):
                        p_idx = orig_bullet_indices[idx]
                        if p_idx < len(all_paragraphs):
                            p_target = all_paragraphs[p_idx]
                            _replace_paragraph_text_preserving_runs(p_target, bullet.text)
                            last_bullet_p = p_target
                    else:
                        # Extra bullet needed -> XML deep-copy clone!
                        if last_bullet_p is not None:
                            cloned_elem = copy.deepcopy(last_bullet_p._p)
                            last_bullet_p._p.addnext(cloned_elem)
                            cloned_p = Paragraph(cloned_elem, doc)
                            _replace_paragraph_text_preserving_runs(cloned_p, bullet.text)
                            last_bullet_p = cloned_p

                # If original had more bullets than tailored, remove unused extra paragraphs
                if len(orig_bullet_indices) > len(tailored_bullets):
                    for excess_idx in range(len(tailored_bullets), len(orig_bullet_indices)):
                        p_idx = orig_bullet_indices[excess_idx]
                        if p_idx < len(all_paragraphs):
                            excess_elem = all_paragraphs[p_idx]._p
                            parent = excess_elem.getparent()
                            if parent is not None:
                                parent.remove(excess_elem)

    doc.save(output_docx_path)
    return output_docx_path
