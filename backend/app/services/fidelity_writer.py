"""In-Place High-Fidelity DOCX Slot Writer.
Holds live references to parsed XML elements from a single parse pass, resolves all slots first,
and applies updates, clones, and removals in strict phases without index drift.
"""

import copy
import re
import os
import zipfile
import random
import shutil
import logging
from typing import Dict, List, Optional, Tuple, Any, Set, Union
from docx import Document
from docx.text.paragraph import Paragraph
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from lxml import etree

from app.schemas.content import ResumeContent
from contracts.models.template_profile import TemplateProfile, Slot

logger = logging.getLogger(__name__)

# Standard XML Namespaces in WordprocessingML
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W14_NS = "http://schemas.microsoft.com/office/word/2010/wordml"
WP_NS = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"


def _generate_unique_8hex(used: Set[str]) -> str:
    """Generates an 8-character uppercase hex string unique within used set."""
    while True:
        val = f"{random.randint(0x01000000, 0x7FFFFFFF):08X}"
        if val not in used:
            used.add(val)
            return val


def _collect_existing_ids(root: etree._Element) -> Tuple[Set[str], Set[str], int, int]:
    """Collects all existing w14:paraId, w14:textId, max bookmark id, and max docPr id."""
    used_para_ids: Set[str] = set()
    used_text_ids: Set[str] = set()
    max_bm_id = 0
    max_docpr_id = 0

    for elem in root.iter():
        p_id = elem.attrib.get(f"{{{W14_NS}}}paraId")
        if p_id:
            used_para_ids.add(p_id.upper())
        t_id = elem.attrib.get(f"{{{W14_NS}}}textId")
        if t_id:
            used_text_ids.add(t_id.upper())

        if elem.tag in (f"{{{W_NS}}}bookmarkStart", f"{{{W_NS}}}bookmarkEnd"):
            b_id = elem.attrib.get(f"{{{W_NS}}}id")
            if b_id and b_id.isdigit():
                max_bm_id = max(max_bm_id, int(b_id))

        if elem.tag == f"{{{WP_NS}}}docPr" or elem.tag.endswith("}docPr"):
            d_id = elem.attrib.get("id")
            if d_id and d_id.isdigit():
                max_docpr_id = max(max_docpr_id, int(d_id))

    return used_para_ids, used_text_ids, max_bm_id, max_docpr_id


def _scrub_cloned_element_ids(
    elem: etree._Element,
    used_para_ids: Set[str],
    used_text_ids: Set[str],
    bm_counter: List[int],
    docpr_counter: List[int],
) -> None:
    """Scrubs and replaces all XML IDs (paraId, textId, bookmark IDs, drawing IDs)

    on a cloned element to guarantee strict XML ID uniqueness.
    """
    for el in [elem] + list(elem.iter()):
        if f"{{{W14_NS}}}paraId" in el.attrib:
            el.attrib[f"{{{W14_NS}}}paraId"] = _generate_unique_8hex(used_para_ids)
        if f"{{{W14_NS}}}textId" in el.attrib:
            el.attrib[f"{{{W14_NS}}}textId"] = _generate_unique_8hex(used_text_ids)

        if el.tag == f"{{{WP_NS}}}docPr" or el.tag.endswith("}docPr"):
            docpr_counter[0] += 1
            el.attrib["id"] = str(docpr_counter[0])

    # Re-map bookmarks
    bm_map: Dict[str, str] = {}
    for el in elem.iter():
        if el.tag == f"{{{W_NS}}}bookmarkStart":
            old_id = el.attrib.get(f"{{{W_NS}}}id")
            bm_counter[0] += 1
            new_id = str(bm_counter[0])
            if old_id:
                bm_map[old_id] = new_id
            el.attrib[f"{{{W_NS}}}id"] = new_id
            old_name = el.attrib.get(f"{{{W_NS}}}name", "bm")
            el.attrib[f"{{{W_NS}}}name"] = f"{old_name}_{new_id}"
        elif el.tag == f"{{{W_NS}}}bookmarkEnd":
            old_id = el.attrib.get(f"{{{W_NS}}}id")
            if old_id and old_id in bm_map:
                el.attrib[f"{{{W_NS}}}id"] = bm_map[old_id]
            else:
                bm_counter[0] += 1
                el.attrib[f"{{{W_NS}}}id"] = str(bm_counter[0])


def _parse_inline_markdown(text: str) -> List[Dict[str, Any]]:
    """Parses safe inline markdown (**bold**, *italic*, [link](url)) into run tokens."""
    tokens: List[Dict[str, Any]] = []

    # Combined regex to tokenize markdown structures
    pattern = re.compile(
        r"(\*\*\*(?P<bold_italic>.*?)\*\*\*|"
        r"\*\*(?P<bold>.*?)\*\*|"
        r"\*(?P<italic>.*?)\*|"
        r"\[(?P<link_text>.*?)\]\((?P<link_url>.*?)\)|"
        r"(?P<plain>[^*\[]+|\*|\[))"
    )

    for m in pattern.finditer(text):
        if m.group("bold_italic") is not None:
            tokens.append({"text": m.group("bold_italic"), "bold": True, "italic": True})
        elif m.group("bold") is not None:
            tokens.append({"text": m.group("bold"), "bold": True, "italic": False})
        elif m.group("italic") is not None:
            tokens.append({"text": m.group("italic"), "bold": False, "italic": True})
        elif m.group("link_text") is not None:
            tokens.append({
                "text": m.group("link_text"),
                "url": m.group("link_url"),
                "bold": False,
                "italic": False,
                "is_link": True,
            })
        elif m.group("plain") is not None:
            tokens.append({"text": m.group("plain"), "bold": False, "italic": False})

    if not tokens and text:
        tokens.append({"text": text, "bold": False, "italic": False})

    return tokens


def set_slot_text(p: Paragraph, text_with_markup: str, literal_prefix: Optional[str] = None) -> None:
    """Replaces text in the given paragraph while preserving run-level styling
    (font family, size, color) and applying inline bold/italic/link markup.
    If literal_prefix is provided or detected, re-attaches it to the front of the text.
    """
    if literal_prefix is None and p.text:
        numPr = p._p.find(qn("w:pPr"))
        has_numpr = numPr is not None and numPr.find(qn("w:numPr")) is not None
        if not has_numpr:
            m = re.match(r"^([\u2022\u25E6\u25AA\u25AB\u2013\u2014\-*\uf0b7]\s*)", p.text)
            if m:
                literal_prefix = m.group(1)

    if literal_prefix:
        clean_prefix = literal_prefix.strip()
        if not text_with_markup.startswith(clean_prefix):
            text_with_markup = literal_prefix + text_with_markup.lstrip()

    if p.text == text_with_markup:
        return

    if not text_with_markup:
        for r in p.runs:
            r.text = ""
        return

    tokens = _parse_inline_markdown(text_with_markup)
    has_markup = any(t.get("bold") or t.get("italic") or t.get("is_link") for t in tokens)

    # 1. Pure fast path: single run with no markdown tokens
    if not has_markup and len(p.runs) == 1:
        p.runs[0].text = text_with_markup
        return

    # 2. Pure fast path: bold lead-in followed by normal text without markdown
    if not has_markup and len(p.runs) > 1:
        first_bold = bool(p.runs[0].bold)
        second_bold = bool(p.runs[1].bold)
        if first_bold and not second_bold and (":" in text_with_markup or "—" in text_with_markup):
            sep = ":" if ":" in text_with_markup else "—"
            parts = text_with_markup.split(sep, 1)
            p.runs[0].text = parts[0] + sep
            p.runs[1].text = parts[1]
            for r in p.runs[2:]:
                r.text = ""
            return

    # 3. General path with markdown parsing or multiple runs
    # Collect all available prototype rPr elements from original runs before removal
    proto_rprs: List[etree._Element] = []
    for r in p.runs:
        rpr = r._r.find(qn("w:rPr"))
        if rpr is not None:
            proto_rprs.append(copy.deepcopy(rpr))

    # Clear all existing runs safely from XML
    for r in list(p.runs):
        p._p.remove(r._r)

    for t in tokens:
        txt = t.get("text", "")
        if not txt:
            continue
        new_run = p.add_run(txt)

        is_bold = bool(t.get("bold"))
        is_italic = bool(t.get("italic"))

        # Find matching prototype if available
        matched_proto = None
        for pr in proto_rprs:
            b_tag = pr.find(qn("w:b"))
            has_b = b_tag is not None and b_tag.attrib.get(qn("w:val"), "1") not in ("0", "false", "off")
            i_tag = pr.find(qn("w:i"))
            has_i = i_tag is not None and i_tag.attrib.get(qn("w:val"), "1") not in ("0", "false", "off")
            if has_b == is_bold and has_i == is_italic:
                matched_proto = copy.deepcopy(pr)
                break

        if matched_proto is None and proto_rprs:
            # Copy first prototype and adjust tags directly without adding val="0" pollution
            matched_proto = copy.deepcopy(proto_rprs[0])
            b_tag = matched_proto.find(qn("w:b"))
            if is_bold:
                if b_tag is None:
                    matched_proto.insert(0, etree.Element(qn("w:b")))
            else:
                if b_tag is not None:
                    matched_proto.remove(b_tag)

            i_tag = matched_proto.find(qn("w:i"))
            if is_italic:
                if i_tag is None:
                    matched_proto.append(etree.Element(qn("w:i")))
            else:
                if i_tag is not None:
                    matched_proto.remove(i_tag)

        if matched_proto is not None:
            # WordprocessingML (ECMA-376) strictly requires w:rPr before w:t
            new_run._r.insert(0, matched_proto)
        elif is_bold or is_italic:
            new_rpr = etree.Element(qn("w:rPr"))
            if is_bold:
                new_rpr.append(etree.Element(qn("w:b")))
            if is_italic:
                new_rpr.append(etree.Element(qn("w:i")))
            new_run._r.insert(0, new_rpr)


def clone_slot(prototype_p: Paragraph, insert_after_p: Paragraph, text_with_markup: str) -> Paragraph:
    """Deep-copies prototype paragraph XML element and inserts it directly after insert_after_p,
    scrubbing IDs to guarantee XML ID uniqueness.
    """
    root = prototype_p._p.getroottree().getroot()
    used_para_ids, used_text_ids, max_bm_id, max_docpr_id = _collect_existing_ids(root)
    cloned_elem = copy.deepcopy(prototype_p._p)
    _scrub_cloned_element_ids(cloned_elem, used_para_ids, used_text_ids, [max_bm_id], [max_docpr_id])
    insert_after_p._p.addnext(cloned_elem)
    cloned_p = Paragraph(cloned_elem, insert_after_p._parent)
    set_slot_text(cloned_p, text_with_markup)
    return cloned_p


def clone_slot_with_unique_ids(
    prototype_p: Paragraph,
    insert_after_p: Paragraph,
    text_with_markup: str,
    used_para_ids: Set[str],
    used_text_ids: Set[str],
    bm_counter: List[int],
    docpr_counter: List[int],
) -> Paragraph:
    """Deep-copies prototype paragraph XML element, scrubs all internal IDs, and inserts after target."""
    cloned_elem = copy.deepcopy(prototype_p._p)
    _scrub_cloned_element_ids(cloned_elem, used_para_ids, used_text_ids, bm_counter, docpr_counter)
    insert_after_p._p.addnext(cloned_elem)
    cloned_p = Paragraph(cloned_elem, insert_after_p._parent)
    set_slot_text(cloned_p, text_with_markup)
    return cloned_p


def remove_slot(p: Paragraph) -> None:
    """Removes paragraph XML element safely from its parent container."""
    elem = p._p
    parent = elem.getparent()
    if parent is not None:
        parent.remove(elem)


def _collect_paragraph_elements(doc: Document) -> List[Paragraph]:
    """Single-pass collector that walks the document in true reading order

    and returns live Paragraph objects referencing the underlying XML elements.
    """
    paragraphs: List[Paragraph] = []
    body_elem = doc._body._body

    def process_textboxes(parent_elem: OxmlElement):
        try:
            tx_p_elems = parent_elem.xpath(
                ".//*[local-name()='txBody' or local-name()='textbox' or local-name()='txbx']//*[local-name()='p']"
            )
        except Exception:
            tx_p_elems = []
        for tp in tx_p_elems:
            t_obj = Paragraph(tp, doc)
            if t_obj.text.strip():
                paragraphs.append(t_obj)

    def process_table(tbl):
        for row in tbl.rows:
            for cell in row.cells:
                for cell_p in cell.paragraphs:
                    process_textboxes(cell_p._p)
                    if cell_p.text.strip():
                        paragraphs.append(cell_p)
                for nested_tbl in cell.tables:
                    process_table(nested_tbl)

    for child in body_elem.iterchildren():
        tag = child.tag
        if tag.endswith("}p"):
            process_textboxes(child)
            p_obj = Paragraph(child, doc)
            if p_obj.text.strip():
                paragraphs.append(p_obj)
        elif tag.endswith("}tbl"):
            for tbl in doc.tables:
                if tbl._tbl == child:
                    process_table(tbl)
                    break

    return paragraphs


def write_tailored_docx(
    template_docx_path: str,
    tailored_content: ResumeContent,
    content_to_paragraphs: Dict[str, List[int]],
    output_docx_path: str,
) -> str:
    """Writes tailored resume content back into the master DOCX template in-place.

    Holds live element references from one initial parse pass, resolves all slots first,
    and applies text updates, clones, and deletions in strict phases without index drift.
    """
    doc = Document(template_docx_path)

    # 1. Single Parse Pass: build live paragraph element reference map
    all_elements = _collect_paragraph_elements(doc)
    element_map: Dict[int, Paragraph] = {i: p for i, p in enumerate(all_elements)}

    # Phase A: Text Updates (in-place on existing resolved XML elements)
    # 1. Name & Header Title
    name_indices = content_to_paragraphs.get("header.name", [])
    if name_indices and name_indices[0] in element_map:
        set_slot_text(element_map[name_indices[0]], tailored_content.header.name)

    title_indices = content_to_paragraphs.get("header.title", [])
    if title_indices and title_indices[0] in element_map and tailored_content.header.title:
        set_slot_text(element_map[title_indices[0]], tailored_content.header.title)

    # 2. Sections, Items, and Bullets
    elements_to_remove: List[Paragraph] = []
    clones_to_execute: List[Tuple[Paragraph, Paragraph, str]] = []

    for section in tailored_content.sections:
        sec_id = section.id

        # Section Heading
        h_indices = content_to_paragraphs.get(f"{sec_id}.title", [])
        if h_indices and h_indices[0] in element_map:
            set_slot_text(element_map[h_indices[0]], section.title)

        if section.type == "summary":
            for item in section.items:
                for bullet in item.bullets:
                    b_indices = content_to_paragraphs.get(f"{sec_id}.{item.id}.{bullet.id}", [])
                    if not b_indices:
                        b_indices = content_to_paragraphs.get(f"{sec_id}.summary", [])
                    if b_indices and b_indices[0] in element_map:
                        set_slot_text(element_map[b_indices[0]], bullet.text)

        elif section.type == "skills":
            for item in section.items:
                for bullet in item.bullets:
                    b_indices = content_to_paragraphs.get(f"{sec_id}.{item.id}.{bullet.id}", [])
                    if b_indices and b_indices[0] in element_map:
                        new_txt = f"{item.title}: {bullet.text}" if item.title and not item.title.startswith("Skill Group") else bullet.text
                        set_slot_text(element_map[b_indices[0]], new_txt)

        else:
            # Experience, Education, Projects, Custom, Certifications
            for item in section.items:
                t_indices = content_to_paragraphs.get(f"{sec_id}.{item.id}.title", [])
                if t_indices and t_indices[0] in element_map:
                    full_title = f"{item.title} — {item.subtitle}" if item.subtitle else item.title
                    set_slot_text(element_map[t_indices[0]], full_title)

                # Bullets for this item
                orig_bullet_indices = []
                for k, indices in content_to_paragraphs.items():
                    if k.startswith(f"{sec_id}.{item.id}.b-"):
                        orig_bullet_indices.extend(indices)

                tailored_bullets = item.bullets or []
                last_p: Optional[Paragraph] = None

                for idx, bullet in enumerate(tailored_bullets):
                    if idx < len(orig_bullet_indices):
                        p_idx = orig_bullet_indices[idx]
                        if p_idx in element_map:
                            target_p = element_map[p_idx]
                            set_slot_text(target_p, bullet.text)
                            last_p = target_p
                    else:
                        # Extra bullet needed -> clone
                        if last_p is not None:
                            clones_to_execute.append((last_p, last_p, bullet.text))

                # Extra bullets in template to delete
                if len(orig_bullet_indices) > len(tailored_bullets):
                    for excess_idx in range(len(tailored_bullets), len(orig_bullet_indices)):
                        p_idx = orig_bullet_indices[excess_idx]
                        if p_idx in element_map:
                            elements_to_remove.append(element_map[p_idx])

    # Phase B: Clone slots
    for proto_p, after_p, txt in clones_to_execute:
        clone_slot(proto_p, after_p, txt)

    # Phase C: Remove elements last
    for elem_p in elements_to_remove:
        remove_slot(elem_p)

    doc.save(output_docx_path)
    return output_docx_path


def write_tailored_docx_repackaged(
    template_docx_path: str,
    operations: Union[List[Any], Any],
    template_profile: Optional[TemplateProfile] = None,
    output_docx_path: str = "",
) -> str:
    """Writes tailored changes into the master DOCX template via zip-level repackaging.

    Guarantees:
    - Only word/document.xml is modified in the zip archive.
    - Non-document parts (styles.xml, settings.xml, theme, etc.) are copied verbatim
      and remain SHA-256 byte-identical to the original archive.
    - Preserves root namespace declarations (xmlns:w, xmlns:w14, xmlns:mc) and mc:Ignorable.
    - Resolves all slots in a single parse pass BEFORE structural modifications.
    - Applies operations in strict order:
        Phase 1: set_text updates
        Phase 2: reorder paragraphs
        Phase 3: clone slots / blocks with unique IDs
        Phase 4: remove slots / blocks
    """
    if not output_docx_path:
        base, ext = os.path.splitext(template_docx_path)
        output_docx_path = f"{base}_tailored{ext}"

    os.makedirs(os.path.dirname(os.path.abspath(output_docx_path)), exist_ok=True)

    doc = Document(template_docx_path)
    all_elements = _collect_paragraph_elements(doc)

    used_para_ids, used_text_ids, max_bm_id, max_docpr_id = _collect_existing_ids(doc._element)
    bm_counter = [max_bm_id]
    docpr_counter = [max_docpr_id]

    # Map slot_id to live Paragraph element reference
    slot_to_elem: Dict[str, Paragraph] = {}
    content_to_slot: Dict[str, str] = {}

    # Initialize index-based mapping
    for i, p in enumerate(all_elements):
        slot_to_elem[f"slot_{i}"] = p

    # If TemplateProfile provided, map explicitly via source_pointer
    if template_profile:
        for s in template_profile.slots:
            if s.source_pointer and s.source_pointer.paragraph_index is not None:
                p_idx = s.source_pointer.paragraph_index
                if 0 <= p_idx < len(all_elements):
                    slot_to_elem[s.slot_id] = all_elements[p_idx]
            elif s.slot_id not in slot_to_elem and s.slot_id.startswith("slot_"):
                try:
                    p_idx = int(s.slot_id.replace("slot_", ""))
                    if 0 <= p_idx < len(all_elements):
                        slot_to_elem[s.slot_id] = all_elements[p_idx]
                except ValueError:
                    pass

        if template_profile.slot_map:
            for sid, sinfo in template_profile.slot_map.items():
                if getattr(sinfo, "bullet_id", None):
                    content_to_slot[sinfo.bullet_id] = sid
                if getattr(sinfo, "item_id", None):
                    content_to_slot.setdefault(sinfo.item_id, sid)
                if getattr(sinfo, "section_id", None):
                    content_to_slot.setdefault(sinfo.section_id, sid)

    slot_objs: Dict[str, Any] = {}
    if template_profile and getattr(template_profile, "slots", None):
        slot_objs = {s.slot_id: s for s in template_profile.slots}

    # Normalize operations list
    raw_ops = operations.operations if hasattr(operations, "operations") else operations
    norm_ops: List[Dict[str, Any]] = []
    for op in raw_ops:
        if hasattr(op, "model_dump"):
            norm_ops.append(op.model_dump())
        elif isinstance(op, dict):
            norm_ops.append(op)
        elif hasattr(op, "__dict__"):
            norm_ops.append(dict(op.__dict__))

    # Phase 1: Text updates (set_text)
    for op in norm_ops:
        op_type = op.get("type")
        if op_type in ("set_text", "set_slot_text"):
            sid = op.get("slot_id") or content_to_slot.get(op.get("target_content_id"))
            text = op.get("text")
            if sid and sid in slot_to_elem and text is not None:
                prefix = getattr(slot_objs.get(sid), "literal_prefix", None) if slot_objs else None
                set_slot_text(slot_to_elem[sid], text, literal_prefix=prefix)

    # Phase 2: Paragraph reordering
    for op in norm_ops:
        op_type = op.get("type")
        if op_type in ("reorder", "reorder_paragraphs"):
            new_order = op.get("new_order", [])
            elems_to_reorder: List[Paragraph] = []
            for item in new_order:
                sid = item if item in slot_to_elem else content_to_slot.get(item)
                if sid and sid in slot_to_elem:
                    elems_to_reorder.append(slot_to_elem[sid])

            if len(elems_to_reorder) >= 2:
                parent = elems_to_reorder[0]._p.getparent()
                if parent is not None and all(p._p.getparent() == parent for p in elems_to_reorder):
                    indices = [parent.index(p._p) for p in elems_to_reorder]
                    anchor = min(indices)
                    for p in elems_to_reorder:
                        parent.remove(p._p)
                    for i, p in enumerate(elems_to_reorder):
                        parent.insert(anchor + i, p._p)

    # Phase 3: Cloning
    for op in norm_ops:
        op_type = op.get("type")
        if op_type in ("clone_slot", "clone_block"):
            proto_sid = op.get("prototype_slot_id") or op.get("slot_id")
            after_sid = op.get("insert_after_slot_id") or proto_sid
            text = op.get("text", "")

            proto_p = slot_to_elem.get(proto_sid)
            after_p = slot_to_elem.get(after_sid) or proto_p

            if proto_p and after_p:
                new_p = clone_slot_with_unique_ids(
                    proto_p,
                    after_p,
                    text,
                    used_para_ids,
                    used_text_ids,
                    bm_counter,
                    docpr_counter,
                )
                target_sid = op.get("slot_id")
                if target_sid:
                    slot_to_elem[target_sid] = new_p

    # Phase 4: Removals (last)
    for op in norm_ops:
        op_type = op.get("type")
        if op_type in ("remove_slot", "remove_block"):
            sid = op.get("slot_id") or content_to_slot.get(op.get("target_content_id"))
            if sid and sid in slot_to_elem:
                remove_slot(slot_to_elem[sid])

    # Phase 5: Serialize and Zip-Level Repackaging
    new_doc_xml = etree.tostring(doc._element, xml_declaration=True, encoding="UTF-8", standalone=True)

    tmp_out = f"{output_docx_path}.tmp_{random.randint(1000, 9999)}"
    with zipfile.ZipFile(template_docx_path, "r") as zin, zipfile.ZipFile(tmp_out, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            if item.filename == "word/document.xml":
                zout.writestr(item.filename, new_doc_xml)
            else:
                zout.writestr(item.filename, zin.read(item.filename))

    shutil.move(tmp_out, output_docx_path)
    logger.info(f"Successfully generated repackaged DOCX at {output_docx_path}")
    return output_docx_path
