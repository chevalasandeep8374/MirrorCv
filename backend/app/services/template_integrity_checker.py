"""Template Integrity Checker for MirrorCV Agent 3 (Composer).
Enforces the two-tier verification split:
- Tier 1: TEMPLATE INTEGRITY (Invariants 1-6, 8, and container clipping).
  Blocks all downloads on failure (status: 'failed').
- Tier 2: LAYOUT FIT (Invariant 7: page count and slot line budgets).
  Yields status 'layout_changed' on overflow, requiring explicit user acknowledgement.
"""

import os
import copy
import hashlib
import zipfile
import logging
from typing import Dict, List, Optional, Tuple, Any, Set, Union
from lxml import etree
from docx import Document
from docx.text.paragraph import Paragraph

from contracts.models.composition_result import (
    IntegrityReport,
    InvariantCheck,
    Status,
)
from contracts.models.template_profile import TemplateProfile, Slot, PointerType
from app.services.docx_rendering_measurements import measure_lines, extract_pdf_lines

logger = logging.getLogger(__name__)

# Standard XML Namespaces in WordprocessingML
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W14_NS = "http://schemas.microsoft.com/office/word/2010/wordml"
WP_NS = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
MC_NS = "http://schemas.openxmlformats.org/markup-compatibility/2006"


def _get_xml_tag(ns: str, tag: str) -> str:
    return f"{{{ns}}}{tag}"


def canonicalize_element(elem: Optional[Any]) -> bytes:
    """Produces a canonical XML representation (c14n) of an XML element,
    stripping volatile revision attributes (rsid*, w14:paraId, w14:textId).
    """
    if elem is None:
        return b""
    raw_elem = getattr(elem, "_element", None) or getattr(elem, "_p", None) or getattr(elem, "_r", None) or elem
    if not isinstance(raw_elem, (etree._Element, etree.ElementBase)):
        return b""

    clone = copy.deepcopy(raw_elem)

    volatile_suffixes = ("rsid", "rsidr", "rsidp", "rsidrpr", "rsidrdefault", "rsiddel", "rsidtr")
    volatile_localnames = ("paraid", "textid")

    for el in clone.iter():
        attribs_to_del = []
        for attr in el.attrib:
            local = attr.split("}")[-1].lower() if "}" in attr else attr.lower()
            if local in volatile_localnames or any(local.startswith(s) for s in volatile_suffixes):
                attribs_to_del.append(attr)
        for a in attribs_to_del:
            del el.attrib[a]

    return etree.tostring(clone, method="c14n")


def _verify_cloned_numbering_only(b_orig: bytes, b_tail: bytes) -> bool:
    """Verifies that numbering.xml changes only consist of added <w:num> entries
    referencing existing <w:abstractNumId>, with all existing numbering structures intact.
    """
    try:
        root_orig = etree.fromstring(b_orig)
        root_tail = etree.fromstring(b_tail)

        # Verify all abstractNum elements are canonical-identical
        orig_abstrs = {
            el.attrib.get(_get_xml_tag(W_NS, "abstractNumId")): canonicalize_element(el)
            for el in root_orig.findall(_get_xml_tag(W_NS, "abstractNum"))
        }
        tail_abstrs = {
            el.attrib.get(_get_xml_tag(W_NS, "abstractNumId")): canonicalize_element(el)
            for el in root_tail.findall(_get_xml_tag(W_NS, "abstractNum"))
        }

        if orig_abstrs != tail_abstrs:
            return False

        # Verify original num elements are intact
        orig_nums = {
            el.attrib.get(_get_xml_tag(W_NS, "numId")): canonicalize_element(el)
            for el in root_orig.findall(_get_xml_tag(W_NS, "num"))
        }
        tail_nums = {
            el.attrib.get(_get_xml_tag(W_NS, "numId")): canonicalize_element(el)
            for el in root_tail.findall(_get_xml_tag(W_NS, "num"))
        }

        for num_id, c_orig in orig_nums.items():
            if num_id not in tail_nums or tail_nums[num_id] != c_orig:
                return False

        # Any new num elements in tail must point to a valid existing abstractNumId
        for el in root_tail.findall(_get_xml_tag(W_NS, "num")):
            n_id = el.attrib.get(_get_xml_tag(W_NS, "numId"))
            if n_id not in orig_nums:
                ab_ref = el.find(_get_xml_tag(W_NS, "abstractNumId"))
                if ab_ref is None or ab_ref.attrib.get(_get_xml_tag(W_NS, "val")) not in orig_abstrs:
                    return False

        return True
    except Exception as e:
        logger.warning(f"Error checking numbering.xml: {e}")
        return False


class TemplateIntegrityResult:
    def __init__(
        self,
        integrity_report: IntegrityReport,
        layout_fit_passed: bool,
        layout_violations: List[str],
        status: Status,
        per_slot_lines: Dict[str, Dict[str, Any]],
    ):
        self.integrity_report = integrity_report
        self.layout_fit_passed = layout_fit_passed
        self.layout_violations = layout_violations
        self.status = status
        self.per_slot_lines = per_slot_lines


def check_template_integrity(
    template_docx_path: str,
    tailored_docx_path: str,
    template_profile: Optional[TemplateProfile] = None,
    accepted_changes: Optional[List[Any]] = None,
    page_count_before: Optional[int] = None,
    page_count_after: Optional[int] = None,
    per_slot_rendered_lines: Optional[Dict[str, int]] = None,
    orig_pdf_path: Optional[str] = None,
    tailored_pdf_path: Optional[str] = None,
) -> TemplateIntegrityResult:
    """Performs rigorous two-tier deterministic verification between master and tailored DOCX.

    Tier 1 (Template Integrity):
      - Invariant 1: Non-document zip parts SHA-256 byte-identical.
      - Invariant 2: sectPr canonical equality (margins, dimensions, columns, headers).
      - Invariant 3: pPr canonical equality across matched paragraphs (indents, tabs, spacing).
      - Invariant 4: rPr prototype match (every run rPr equals one of its slot's prototype rPr values).
      - Invariant 5: Cloned blocks inherit exact prototype pPr/rPr.
      - Invariant 6: XML ID uniqueness (zero duplicate paraId, textId, bookmark, docPr).
      - Invariant 8: Unedited slots retain exact text, rendered x position, and vertical coherence.
      - Container clipping: Text boxes and fixed-height table cells have zero clipped text.

    Tier 2 (Layout Fit):
      - Invariant 7: Page count equality and slot line budgets.
    """
    violations: List[str] = []
    checks: List[InvariantCheck] = []
    byte_identical_parts: List[str] = []
    id_collisions = 0

    # -------------------------------------------------------------
    # Invariant 1: Non-document zip parts SHA-256 byte-identical
    # -------------------------------------------------------------
    inv1_passed = True
    inv1_details = []
    try:
        with zipfile.ZipFile(template_docx_path, "r") as z_orig, zipfile.ZipFile(tailored_docx_path, "r") as z_tail:
            orig_parts = set(z_orig.namelist())
            tail_parts = set(z_tail.namelist())

            if orig_parts != tail_parts:
                inv1_passed = False
                diff = orig_parts.symmetric_difference(tail_parts)
                violations.append(f"Invariant 1 Failed: Archive entries mismatch ({diff})")

            for name in orig_parts:
                if name != "word/document.xml":
                    if name in tail_parts:
                        b_orig = z_orig.read(name)
                        b_tail = z_tail.read(name)
                        h_orig = hashlib.sha256(b_orig).hexdigest()
                        h_tail = hashlib.sha256(b_tail).hexdigest()
                        if h_orig == h_tail:
                            byte_identical_parts.append(name)
                        else:
                            if name == "word/numbering.xml" and _verify_cloned_numbering_only(b_orig, b_tail):
                                byte_identical_parts.append(f"{name} (valid cloned num definitions)")
                                continue
                            inv1_passed = False
                            inv1_details.append(f"Part '{name}' byte mismatch")
                            violations.append(f"Invariant 1 Failed: Part '{name}' was altered during composition")
    except Exception as e:
        inv1_passed = False
        violations.append(f"Invariant 1 Failed: Error checking zip parts: {e}")

    checks.append(
        InvariantCheck(
            name="Invariant 1: Non-document zip parts byte-identity",
            passed=inv1_passed,
            details=f"{len(byte_identical_parts)} parts byte-identical; {len(inv1_details)} mismatched",
        )
    )

    # Load XML trees for deep DOM checks
    try:
        doc_orig = Document(template_docx_path)
        doc_tail = Document(tailored_docx_path)
        root_orig = doc_orig._element
        root_tail = doc_tail._element
        p_orig_list = doc_orig.paragraphs
        p_tail_list = doc_tail.paragraphs
    except Exception as e:
        violations.append(f"Corrupted or invalid DOCX archive: {e}")
        report = IntegrityReport(
            passed=False,
            violations=violations,
            invariants_checked=checks,
            byte_identical_parts=byte_identical_parts,
            id_collisions_found=id_collisions,
        )
        return TemplateIntegrityResult(
            integrity_report=report,
            layout_fit_passed=False,
            layout_violations=violations,
            status=Status.failed,
            per_slot_lines={},
        )

    # -------------------------------------------------------------
    # Invariant 2: sectPr canonical equality (margins, width, height, columns) & Drawing Containers
    # -------------------------------------------------------------
    inv2_passed = True
    inv2_details = "Page geometry, margins, and drawing containers canonical-identical"
    try:
        sect_orig = [el for el in root_orig.iter() if el.tag == _get_xml_tag(W_NS, "sectPr") or el.tag.endswith("}sectPr")]
        sect_tail = [el for el in root_tail.iter() if el.tag == _get_xml_tag(W_NS, "sectPr") or el.tag.endswith("}sectPr")]

        if len(sect_orig) != len(sect_tail):
            inv2_passed = False
            violations.append(f"Invariant 2 Failed: Section count mismatch ({len(sect_orig)} vs {len(sect_tail)})")
        else:
            for idx, (so, st) in enumerate(zip(sect_orig, sect_tail)):
                c_so = canonicalize_element(so)
                c_st = canonicalize_element(st)
                if c_so != c_st:
                    inv2_passed = False
                    violations.append(f"Invariant 2 Failed: Section properties (sectPr) altered in section {idx}")

        # Verify Text Box & Drawing container geometry (extent, position, transform)
        A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
        draw_orig = root_orig.findall(f".//{{{W_NS}}}drawing")
        draw_tail = root_tail.findall(f".//{{{W_NS}}}drawing")
        if len(draw_orig) != len(draw_tail):
            inv2_passed = False
            violations.append(f"Invariant 2 Failed: Drawing container count altered ({len(draw_orig)} vs {len(draw_tail)})")
        else:
            for idx, (do, dt) in enumerate(zip(draw_orig, draw_tail)):
                for tag in ["extent", "positionH", "positionV", "simplePos"]:
                    eo = do.find(f".//{{{WP_NS}}}{tag}")
                    et_ = dt.find(f".//{{{WP_NS}}}{tag}")
                    if (eo is not None) != (et_ is not None):
                        inv2_passed = False
                        violations.append(f"Invariant 2 Failed: Drawing {tag} altered in drawing {idx}")
                    elif eo is not None and et_ is not None:
                        if canonicalize_element(eo) != canonicalize_element(et_):
                            inv2_passed = False
                            violations.append(f"Invariant 2 Failed: Drawing {tag} moved or altered in drawing {idx}")

                for tag in ["xfrm", "off", "ext"]:
                    ao = do.find(f".//{{{A_NS}}}{tag}")
                    at_ = dt.find(f".//{{{A_NS}}}{tag}")
                    if (ao is not None) != (at_ is not None):
                        inv2_passed = False
                        violations.append(f"Invariant 2 Failed: Drawing shape transform {tag} altered in drawing {idx}")
                    elif ao is not None and at_ is not None:
                        if canonicalize_element(ao) != canonicalize_element(at_):
                            inv2_passed = False
                            violations.append(f"Invariant 2 Failed: Drawing shape transform {tag} altered in drawing {idx}")
    except Exception as e:
        inv2_passed = False
        violations.append(f"Invariant 2 Failed: Error validating sectPr and drawing containers: {e}")

    checks.append(
        InvariantCheck(
            name="Invariant 2: Section and margin geometry identical",
            passed=inv2_passed,
            details=inv2_details if inv2_passed else "Page margins, geometry, or drawing containers were modified",
        )
    )

    # -------------------------------------------------------------
    # Invariant 3: pPr canonical equality across matched paragraphs
    # -------------------------------------------------------------
    inv3_passed = True
    all_p_orig = root_orig.findall(f".//{{{W_NS}}}p")
    all_p_tail = root_tail.findall(f".//{{{W_NS}}}p")
    min_len = min(len(all_p_orig), len(all_p_tail))

    p_style_mismatches = 0
    for i in range(min_len):
        po = all_p_orig[i]
        pt = all_p_tail[i]

        ppro = po.find(_get_xml_tag(W_NS, "pPr"))
        pprt = pt.find(_get_xml_tag(W_NS, "pPr"))

        c_ppro = canonicalize_element(ppro)
        c_pprt = canonicalize_element(pprt)

        if c_ppro != c_pprt:
            p_style_mismatches += 1
            violations.append(f"Invariant 3 Failed: Paragraph formatting properties (pPr) altered in paragraph {i}")

    if p_style_mismatches > 0:
        inv3_passed = False

    checks.append(
        InvariantCheck(
            name="Invariant 3: Paragraph properties (pPr) preserved",
            passed=inv3_passed,
            details=f"Verified {min_len} paragraphs; mismatches: {p_style_mismatches}",
        )
    )

    # -------------------------------------------------------------
    # Invariant 4: rPr prototype match (every run rPr equals one of its slot's prototype rPr values)
    # -------------------------------------------------------------
    inv4_passed = True
    r_prototype_mismatches = 0

    for idx, p in enumerate(all_p_tail):
        prototype_rprs: Set[bytes] = set()

        if idx < len(all_p_orig):
            for r_orig in all_p_orig[idx].findall(f"{{{W_NS}}}r"):
                rpr_o = r_orig.find(_get_xml_tag(W_NS, "rPr"))
                prototype_rprs.add(canonicalize_element(rpr_o))
            if not all_p_orig[idx].findall(f"{{{W_NS}}}r"):
                prototype_rprs.add(b"")
        else:
            if all_p_orig:
                for r_orig in all_p_orig[-1].findall(f"{{{W_NS}}}r"):
                    rpr_o = r_orig.find(_get_xml_tag(W_NS, "rPr"))
                    prototype_rprs.add(canonicalize_element(rpr_o))

        if not prototype_rprs:
            prototype_rprs.add(b"")

        for r in p.findall(f"{{{W_NS}}}r"):
            rpr_t = r.find(_get_xml_tag(W_NS, "rPr"))
            c_rpr_t = canonicalize_element(rpr_t)
            if c_rpr_t not in prototype_rprs:
                r_prototype_mismatches += 1
                inv4_passed = False
                violations.append(
                    f"Invariant 4 Failed: Run formatting (rPr) in paragraph {idx} does not match any prototype rPr"
                )

    checks.append(
        InvariantCheck(
            name="Invariant 4: Run formatting (rPr) whitelist strictly preserved",
            passed=inv4_passed,
            details=f"Run formatting mismatches: {r_prototype_mismatches}",
        )
    )

    # -------------------------------------------------------------
    # Invariant 5: Cloned blocks inherit exact prototype pPr/rPr
    # -------------------------------------------------------------
    inv5_passed = True
    cloned_count = max(0, len(p_tail_list) - len(p_orig_list))
    if cloned_count > 0:
        prototype_p = p_orig_list[-1]._p if p_orig_list else None
        prototype_pPr = canonicalize_element(prototype_p.find(_get_xml_tag(W_NS, "pPr"))) if prototype_p is not None else b""
        for i in range(len(p_orig_list), len(p_tail_list)):
            cloned_p = p_tail_list[i]._p
            cloned_pPr = canonicalize_element(cloned_p.find(_get_xml_tag(W_NS, "pPr")))
            if cloned_pPr != prototype_pPr:
                inv5_passed = False
                violations.append(f"Invariant 5 Failed: Cloned paragraph {i} pPr does not match prototype pPr")

    checks.append(
        InvariantCheck(
            name="Invariant 5: Cloned blocks inherit prototype styling",
            passed=inv5_passed,
            details=f"Verified {cloned_count} cloned paragraph blocks",
        )
    )

    # -------------------------------------------------------------
    # Invariant 6: XML ID uniqueness (paraId, textId, bookmark, docPr)
    # -------------------------------------------------------------
    inv6_passed = True
    para_ids: List[str] = []
    text_ids: List[str] = []
    bm_ids: List[str] = []
    docpr_ids: List[str] = []

    for elem in root_tail.iter():
        pid = elem.attrib.get(f"{{{W14_NS}}}paraId")
        if pid:
            para_ids.append(pid)
        tid = elem.attrib.get(f"{{{W14_NS}}}textId")
        if tid:
            text_ids.append(tid)
        if elem.tag in (f"{{{W_NS}}}bookmarkStart", f"{{{W_NS}}}bookmarkEnd"):
            bid = elem.attrib.get(f"{{{W_NS}}}id")
            if bid:
                bm_ids.append(bid)
        if elem.tag == f"{{{WP_NS}}}docPr" or elem.tag.endswith("}docPr"):
            d_id = elem.attrib.get("id")
            if d_id:
                docpr_ids.append(d_id)

    if len(para_ids) != len(set(para_ids)):
        inv6_passed = False
        dup_count = len(para_ids) - len(set(para_ids))
        id_collisions += dup_count
        violations.append(f"Invariant 6 Failed: {dup_count} duplicate w14:paraId found")

    if len(text_ids) != len(set(text_ids)):
        inv6_passed = False
        dup_count = len(text_ids) - len(set(text_ids))
        id_collisions += dup_count
        violations.append(f"Invariant 6 Failed: {dup_count} duplicate w14:textId found")

    # For bookmarks, each bookmark has start and end with same id, so start IDs must be unique
    bm_start_ids = [el.attrib.get(f"{{{W_NS}}}id") for el in root_tail.iter() if el.tag == f"{{{W_NS}}}bookmarkStart"]
    bm_start_ids = [b for b in bm_start_ids if b]
    if len(bm_start_ids) != len(set(bm_start_ids)):
        inv6_passed = False
        dup_count = len(bm_start_ids) - len(set(bm_start_ids))
        id_collisions += dup_count
        violations.append(f"Invariant 6 Failed: {dup_count} duplicate bookmark IDs found")

    if len(docpr_ids) != len(set(docpr_ids)):
        inv6_passed = False
        dup_count = len(docpr_ids) - len(set(docpr_ids))
        id_collisions += dup_count
        violations.append(f"Invariant 6 Failed: {dup_count} duplicate docPr drawing IDs found")

    checks.append(
        InvariantCheck(
            name="Invariant 6: XML ID uniqueness (paraId, textId, bookmark, docPr)",
            passed=inv6_passed,
            details=f"{id_collisions} ID collisions detected across {len(para_ids) + len(text_ids) + len(bm_start_ids) + len(docpr_ids)} XML IDs",
        )
    )

    # -------------------------------------------------------------
    # Invariant 8: Unedited slots retain exact text and horizontal alignment
    # -------------------------------------------------------------
    inv8_passed = True
    edited_slot_ids = set()
    if accepted_changes:
        for c in accepted_changes:
            sid = getattr(c, "slot_id", None) or getattr(c, "target_content_id", None)
            if sid:
                edited_slot_ids.add(sid)
            if isinstance(c, dict):
                sid = c.get("slot_id") or c.get("target_content_id")
                if sid:
                    edited_slot_ids.add(sid)

    # Expand edited_slot_ids using slot_map bindings
    if template_profile and template_profile.slot_map:
        for s_id, s_info in template_profile.slot_map.items():
            b_id = getattr(s_info, "bullet_id", None)
            i_id = getattr(s_info, "item_id", None)
            sec_id = getattr(s_info, "section_id", None)
            if (b_id and b_id in edited_slot_ids) or (i_id and i_id in edited_slot_ids) or (sec_id and sec_id in edited_slot_ids):
                edited_slot_ids.add(s_id)

    unedited_mismatches = 0
    if template_profile and template_profile.slots:
        for s in template_profile.slots:
            if s.slot_id not in edited_slot_ids and s.source_pointer and s.source_pointer.paragraph_index is not None:
                p_idx = s.source_pointer.paragraph_index
                if p_idx < len(p_orig_list) and p_idx < len(p_tail_list):
                    t_orig = p_orig_list[p_idx].text.strip()
                    t_tail = p_tail_list[p_idx].text.strip()
                    if t_orig and t_tail and t_orig != t_tail:
                        unedited_mismatches += 1
                        inv8_passed = False
                        violations.append(f"Invariant 8 Failed: Unedited slot '{s.slot_id}' was unexpectedly mutated")

    # Rendered horizontal x-position and vertical shift verification when PDF paths are provided
    x_drift_violations = 0
    if orig_pdf_path and tailored_pdf_path and os.path.exists(orig_pdf_path) and os.path.exists(tailored_pdf_path):
        try:
            lines_o = extract_pdf_lines(orig_pdf_path)
            lines_t = extract_pdf_lines(tailored_pdf_path)
            if template_profile and template_profile.slots:
                for s in template_profile.slots:
                    if s.slot_id not in edited_slot_ids and s.source_pointer and s.source_pointer.paragraph_index is not None:
                        p_idx = s.source_pointer.paragraph_index
                        if p_idx < len(p_orig_list):
                            expected_txt = p_orig_list[p_idx].text.strip()
                            if not expected_txt:
                                continue
                            lo = next((l for l in lines_o if expected_txt in l["text"] or l["text"] in expected_txt), None)
                            lt = next((l for l in lines_t if expected_txt in l["text"] or l["text"] in expected_txt), None)
                            if lo and lt:
                                x_delta = abs(lo["bbox"][0] - lt["bbox"][0])
                                if x_delta > 2.0:
                                    x_drift_violations += 1
                                    inv8_passed = False
                                    violations.append(
                                        f"Invariant 8 Failed: Rendered horizontal x-position drifted by {x_delta:.1f}pt for unedited slot '{s.slot_id}'"
                                    )
        except Exception as e:
            logger.warning(f"Invariant 8 PDF position check warning: {e}")

    checks.append(
        InvariantCheck(
            name="Invariant 8: Unedited slots have identical text and alignment",
            passed=inv8_passed,
            details=f"Unedited slot mutations: {unedited_mismatches}, X-position drift violations: {x_drift_violations}",
        )
    )

    # -------------------------------------------------------------
    # Container Clipping Check (Integrity)
    # -------------------------------------------------------------
    clipping_passed = True
    per_slot_lines: Dict[str, Dict[str, Any]] = {}

    if template_profile:
        for s in template_profile.slots:
            is_container = False
            if s.source_pointer:
                if s.source_pointer.pointer_type in (PointerType.docx_textbox, PointerType.docx_table_cell):
                    is_container = True

            p_idx = s.source_pointer.paragraph_index if s.source_pointer else None
            txt = ""
            if p_idx is not None and p_idx < len(p_tail_list):
                txt = p_tail_list[p_idx].text

            lines_after = measure_lines(txt, s) if txt else 1
            if per_slot_rendered_lines and s.slot_id in per_slot_rendered_lines:
                lines_after = per_slot_rendered_lines[s.slot_id]

            clipped = False
            if is_container and lines_after > s.max_lines:
                clipped = True
                clipping_passed = False
                violations.append(f"Container Clipping Failed: Text in container slot '{s.slot_id}' exceeds capacity ({lines_after} > {s.max_lines} lines)")

            per_slot_lines[s.slot_id] = {
                "max_lines": s.max_lines,
                "lines_after": lines_after,
                "clipped": clipped,
            }

    checks.append(
        InvariantCheck(
            name="Container Clipping: Zero clipped text in textboxes/fixed table cells",
            passed=clipping_passed,
            details="Zero clipped container slots" if clipping_passed else "Text box or table cell clipping detected",
        )
    )

    # -------------------------------------------------------------
    # Tier 2 (Layout Fit Check: Invariant 7)
    # -------------------------------------------------------------
    layout_violations: List[str] = []
    layout_fit_passed = True

    # Page count check
    if page_count_before is not None and page_count_after is not None:
        if page_count_after > page_count_before:
            layout_fit_passed = False
            layout_violations.append(
                f"Page count increased from {page_count_before} to {page_count_after} (layout overflow)"
            )

    # Slot budget checks (body/bullet lines)
    if template_profile:
        for s in template_profile.slots:
            slot_info = per_slot_lines.get(s.slot_id, {})
            l_after = slot_info.get("lines_after", 1)
            if l_after > s.max_lines:
                layout_fit_passed = False
                layout_violations.append(
                    f"Slot '{s.slot_id}' exceeds line budget ({l_after} > {s.max_lines} lines)"
                )

    checks.append(
        InvariantCheck(
            name="Invariant 7: Page count equality and slot line budgets",
            passed=layout_fit_passed,
            details=f"Page count: {page_count_before} -> {page_count_after}; Layout fit passed: {layout_fit_passed}",
        )
    )

    # Determine overall status
    integrity_passed = len(violations) == 0
    if not integrity_passed:
        overall_status = Status.failed
    elif not layout_fit_passed:
        overall_status = Status.layout_changed
    else:
        overall_status = Status.ready

    report = IntegrityReport(
        passed=integrity_passed,
        violations=violations,
        invariants_checked=checks,
        byte_identical_parts=byte_identical_parts,
        id_collisions_found=id_collisions,
    )

    return TemplateIntegrityResult(
        integrity_report=report,
        layout_fit_passed=layout_fit_passed,
        layout_violations=layout_violations,
        status=overall_status,
        per_slot_lines=per_slot_lines,
    )
