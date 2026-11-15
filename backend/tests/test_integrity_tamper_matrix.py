"""Test Matrix for Template Integrity Checker.
Enforces that every one of the 16 forbidden style tamper variants
plus unknown XML fuzzing fails Tier 1 Integrity and blocks download (status: failed).
"""

import os
import copy
import zipfile
import pytest
from lxml import etree
from docx import Document

from contracts.models.template_profile import (
    TemplateProfile,
    Slot,
    SlotMap,
    Role,
    SourcePointer,
    PointerType,
    Budgets,
    SchemaVersion,
    SourceType,
    Status as ProfileStatus,
)
from contracts.models.composition_result import Status
from app.services.template_integrity_checker import check_template_integrity, W_NS, W14_NS
from app.services.fidelity_writer import write_tailored_docx_repackaged
from app.services.change_planner import Operation, OperationType

FIXTURES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "fixtures"))
TMP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "tmp_output", "tamper_matrix"))
os.makedirs(TMP_DIR, exist_ok=True)

SAMPLE_DOCX = os.path.join(FIXTURES_DIR, "sample_single_column.docx")
TEXTBOX_DOCX = os.path.join(FIXTURES_DIR, "sample_text_box.docx")


@pytest.fixture
def base_profile():
    doc = Document(SAMPLE_DOCX)
    slots = []
    slot_map = {}
    for i, p in enumerate(doc.paragraphs):
        sid = f"slot_{i}"
        font_name = p.runs[0].font.name if (p.runs and p.runs[0].font.name) else "Calibri"
        font_size = p.runs[0].font.size.pt if (p.runs and p.runs[0].font.size) else 11.0
        p_lines = max(2, p.text.count("\n") + 1)
        slots.append(
            Slot(
                slot_id=sid,
                section_id="sec_exp" if i > 1 else "sec_hdr",
                item_id=f"item_{i}",
                bullet_id=f"b_{i}" if i > 1 else None,
                role=Role.bullet if i > 1 else (Role.name if i == 0 else Role.contact),
                max_lines=p_lines,
                max_chars=max(200, len(p.text) + 50),
                font=font_name,
                size=font_size,
                source_pointer=SourcePointer(
                    pointer_type=PointerType.docx_paragraph,
                    paragraph_index=i,
                ),
                budgets=Budgets(
                    line_width_pt=500.0,
                    max_lines=p_lines,
                    max_chars=max(200, len(p.text) + 50),
                    hard_max_chars=max(250, len(p.text) + 100),
                ),
            )
        )
        slot_map[sid] = SlotMap(
            section_id="sec_exp" if i > 1 else "sec_hdr",
            item_id=f"item_{i}",
            bullet_id=f"b_{i}" if i > 1 else None,
            target_field="text" if i > 1 else "name",
        )

    return TemplateProfile(
        schema_version=SchemaVersion.field_1_1_0,
        template_profile_id="tpl_tamper_test",
        resume_id="res_tamper_test",
        version=1,
        source_type=SourceType.uploaded_docx,
        slots=slots,
        slot_map=slot_map,
        fidelity_score=100.0,
        status=ProfileStatus.ready,
    )


def _create_clean_tailored_docx(out_path: str, profile: TemplateProfile) -> str:
    ops = [
        Operation(
            op_id="op_1",
            type=OperationType.set_text,
            slot_id="slot_2",
            text="Legitimate tailored bullet content that fits budget perfectly.",
        )
    ]
    write_tailored_docx_repackaged(
        template_docx_path=SAMPLE_DOCX,
        operations=ops,
        template_profile=profile,
        output_docx_path=out_path,
    )
    return out_path


def _tamper_document_xml(base_docx: str, tampered_docx: str, tamper_func) -> str:
    with zipfile.ZipFile(base_docx, "r") as zin, zipfile.ZipFile(tampered_docx, "w") as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "word/document.xml":
                root = etree.fromstring(data)
                tamper_func(root)
                data = etree.tostring(root, xml_declaration=True, encoding="utf-8")
            zout.writestr(item.filename, data)
    return tampered_docx


# ---------------------------------------------------------------------------
# Tamper Variant 1: Margin (sectPr/pgMar)
# ---------------------------------------------------------------------------
def test_tamper_1_margin(base_profile):
    clean_docx = _create_clean_tailored_docx(os.path.join(TMP_DIR, "clean_1.docx"), base_profile)
    tampered = os.path.join(TMP_DIR, "tamper_1_margin.docx")

    def tamper(root):
        pgMar = root.find(f".//{{{W_NS}}}pgMar")
        assert pgMar is not None
        pgMar.attrib[f"{{{W_NS}}}left"] = "1440"

    _tamper_document_xml(clean_docx, tampered, tamper)
    res = check_template_integrity(SAMPLE_DOCX, tampered, base_profile, accepted_changes=[{"slot_id": "slot_2"}])
    assert res.integrity_report.passed is False
    assert res.status == Status.failed
    assert any("Invariant 2 Failed" in v for v in res.integrity_report.violations)


# ---------------------------------------------------------------------------
# Tamper Variant 2: Page size (sectPr/pgSz)
# ---------------------------------------------------------------------------
def test_tamper_2_page_size(base_profile):
    clean_docx = _create_clean_tailored_docx(os.path.join(TMP_DIR, "clean_2.docx"), base_profile)
    tampered = os.path.join(TMP_DIR, "tamper_2_page_size.docx")

    def tamper(root):
        pgSz = root.find(f".//{{{W_NS}}}pgSz")
        assert pgSz is not None
        pgSz.attrib[f"{{{W_NS}}}w"] = "14000"

    _tamper_document_xml(clean_docx, tampered, tamper)
    res = check_template_integrity(SAMPLE_DOCX, tampered, base_profile, accepted_changes=[{"slot_id": "slot_2"}])
    assert res.integrity_report.passed is False
    assert res.status == Status.failed
    assert any("Invariant 2 Failed" in v for v in res.integrity_report.violations)


# ---------------------------------------------------------------------------
# Tamper Variant 3: Spacing Before/After (pPr/spacing)
# ---------------------------------------------------------------------------
def test_tamper_3_spacing_before_after(base_profile):
    clean_docx = _create_clean_tailored_docx(os.path.join(TMP_DIR, "clean_3.docx"), base_profile)
    tampered = os.path.join(TMP_DIR, "tamper_3_spacing.docx")

    def tamper(root):
        p = root.findall(f".//{{{W_NS}}}p")[2]
        pPr = p.find(f"{{{W_NS}}}pPr")
        if pPr is None:
            pPr = etree.SubElement(p, f"{{{W_NS}}}pPr")
        spacing = pPr.find(f"{{{W_NS}}}spacing")
        if spacing is None:
            spacing = etree.SubElement(pPr, f"{{{W_NS}}}spacing")
        spacing.attrib[f"{{{W_NS}}}before"] = "360"

    _tamper_document_xml(clean_docx, tampered, tamper)
    res = check_template_integrity(SAMPLE_DOCX, tampered, base_profile, accepted_changes=[{"slot_id": "slot_2"}])
    assert res.integrity_report.passed is False
    assert res.status == Status.failed
    assert any("Invariant 3 Failed" in v for v in res.integrity_report.violations)


# ---------------------------------------------------------------------------
# Tamper Variant 4: Line Spacing (pPr/spacing@line)
# ---------------------------------------------------------------------------
def test_tamper_4_line_spacing(base_profile):
    clean_docx = _create_clean_tailored_docx(os.path.join(TMP_DIR, "clean_4.docx"), base_profile)
    tampered = os.path.join(TMP_DIR, "tamper_4_line_spacing.docx")

    def tamper(root):
        p = root.findall(f".//{{{W_NS}}}p")[2]
        pPr = p.find(f"{{{W_NS}}}pPr")
        if pPr is None:
            pPr = etree.SubElement(p, f"{{{W_NS}}}pPr")
        spacing = pPr.find(f"{{{W_NS}}}spacing")
        if spacing is None:
            spacing = etree.SubElement(pPr, f"{{{W_NS}}}spacing")
        spacing.attrib[f"{{{W_NS}}}line"] = "480"
        spacing.attrib[f"{{{W_NS}}}lineRule"] = "exact"

    _tamper_document_xml(clean_docx, tampered, tamper)
    res = check_template_integrity(SAMPLE_DOCX, tampered, base_profile, accepted_changes=[{"slot_id": "slot_2"}])
    assert res.integrity_report.passed is False
    assert res.status == Status.failed
    assert any("Invariant 3 Failed" in v for v in res.integrity_report.violations)


# ---------------------------------------------------------------------------
# Tamper Variant 5: Indent (pPr/ind)
# ---------------------------------------------------------------------------
def test_tamper_5_indent(base_profile):
    clean_docx = _create_clean_tailored_docx(os.path.join(TMP_DIR, "clean_5.docx"), base_profile)
    tampered = os.path.join(TMP_DIR, "tamper_5_indent.docx")

    def tamper(root):
        p = root.findall(f".//{{{W_NS}}}p")[2]
        pPr = p.find(f"{{{W_NS}}}pPr")
        if pPr is None:
            pPr = etree.SubElement(p, f"{{{W_NS}}}pPr")
        ind = pPr.find(f"{{{W_NS}}}ind")
        if ind is None:
            ind = etree.SubElement(pPr, f"{{{W_NS}}}ind")
        ind.attrib[f"{{{W_NS}}}left"] = "720"

    _tamper_document_xml(clean_docx, tampered, tamper)
    res = check_template_integrity(SAMPLE_DOCX, tampered, base_profile, accepted_changes=[{"slot_id": "slot_2"}])
    assert res.integrity_report.passed is False
    assert res.status == Status.failed
    assert any("Invariant 3 Failed" in v for v in res.integrity_report.violations)


# ---------------------------------------------------------------------------
# Tamper Variant 6: Tab Stop (pPr/tabs)
# ---------------------------------------------------------------------------
def test_tamper_6_tab_stop(base_profile):
    clean_docx = _create_clean_tailored_docx(os.path.join(TMP_DIR, "clean_6.docx"), base_profile)
    tampered = os.path.join(TMP_DIR, "tamper_6_tabs.docx")

    def tamper(root):
        p = root.findall(f".//{{{W_NS}}}p")[2]
        pPr = p.find(f"{{{W_NS}}}pPr")
        if pPr is None:
            pPr = etree.SubElement(p, f"{{{W_NS}}}pPr")
        tabs = pPr.find(f"{{{W_NS}}}tabs")
        if tabs is None:
            tabs = etree.SubElement(pPr, f"{{{W_NS}}}tabs")
        tab = etree.SubElement(tabs, f"{{{W_NS}}}tab")
        tab.attrib[f"{{{W_NS}}}val"] = "left"
        tab.attrib[f"{{{W_NS}}}pos"] = "1440"

    _tamper_document_xml(clean_docx, tampered, tamper)
    res = check_template_integrity(SAMPLE_DOCX, tampered, base_profile, accepted_changes=[{"slot_id": "slot_2"}])
    assert res.integrity_report.passed is False
    assert res.status == Status.failed
    assert any("Invariant 3 Failed" in v for v in res.integrity_report.violations)


# ---------------------------------------------------------------------------
# Tamper Variant 7: Alignment (pPr/jc)
# ---------------------------------------------------------------------------
def test_tamper_7_alignment(base_profile):
    clean_docx = _create_clean_tailored_docx(os.path.join(TMP_DIR, "clean_7.docx"), base_profile)
    tampered = os.path.join(TMP_DIR, "tamper_7_jc.docx")

    def tamper(root):
        p = root.findall(f".//{{{W_NS}}}p")[2]
        pPr = p.find(f"{{{W_NS}}}pPr")
        if pPr is None:
            pPr = etree.SubElement(p, f"{{{W_NS}}}pPr")
        jc = pPr.find(f"{{{W_NS}}}jc")
        if jc is None:
            jc = etree.SubElement(pPr, f"{{{W_NS}}}jc")
        jc.attrib[f"{{{W_NS}}}val"] = "center"

    _tamper_document_xml(clean_docx, tampered, tamper)
    res = check_template_integrity(SAMPLE_DOCX, tampered, base_profile, accepted_changes=[{"slot_id": "slot_2"}])
    assert res.integrity_report.passed is False
    assert res.status == Status.failed
    assert any("Invariant 3 Failed" in v for v in res.integrity_report.violations)


# ---------------------------------------------------------------------------
# Tamper Variant 8: Font Name (rPr/rFonts)
# ---------------------------------------------------------------------------
def test_tamper_8_font_name(base_profile):
    clean_docx = _create_clean_tailored_docx(os.path.join(TMP_DIR, "clean_8.docx"), base_profile)
    tampered = os.path.join(TMP_DIR, "tamper_8_font_name.docx")

    def tamper(root):
        r = root.findall(f".//{{{W_NS}}}r")[2]
        rPr = r.find(f"{{{W_NS}}}rPr")
        if rPr is None:
            rPr = etree.SubElement(r, f"{{{W_NS}}}rPr")
        rFonts = rPr.find(f"{{{W_NS}}}rFonts")
        if rFonts is None:
            rFonts = etree.SubElement(rPr, f"{{{W_NS}}}rFonts")
        rFonts.attrib[f"{{{W_NS}}}ascii"] = "Comic Sans MS"
        rFonts.attrib[f"{{{W_NS}}}hAnsi"] = "Comic Sans MS"

    _tamper_document_xml(clean_docx, tampered, tamper)
    res = check_template_integrity(SAMPLE_DOCX, tampered, base_profile, accepted_changes=[{"slot_id": "slot_2"}])
    assert res.integrity_report.passed is False
    assert res.status == Status.failed
    assert any("Invariant 4 Failed" in v for v in res.integrity_report.violations)


# ---------------------------------------------------------------------------
# Tamper Variant 9: Font Size (rPr/sz)
# ---------------------------------------------------------------------------
def test_tamper_9_font_size(base_profile):
    clean_docx = _create_clean_tailored_docx(os.path.join(TMP_DIR, "clean_9.docx"), base_profile)
    tampered = os.path.join(TMP_DIR, "tamper_9_font_size.docx")

    def tamper(root):
        r = root.findall(f".//{{{W_NS}}}r")[2]
        rPr = r.find(f"{{{W_NS}}}rPr")
        if rPr is None:
            rPr = etree.SubElement(r, f"{{{W_NS}}}rPr")
        sz = rPr.find(f"{{{W_NS}}}sz")
        if sz is None:
            sz = etree.SubElement(rPr, f"{{{W_NS}}}sz")
        sz.attrib[f"{{{W_NS}}}val"] = "32"

    _tamper_document_xml(clean_docx, tampered, tamper)
    res = check_template_integrity(SAMPLE_DOCX, tampered, base_profile, accepted_changes=[{"slot_id": "slot_2"}])
    assert res.integrity_report.passed is False
    assert res.status == Status.failed
    assert any("Invariant 4 Failed" in v for v in res.integrity_report.violations)


# ---------------------------------------------------------------------------
# Tamper Variant 10: Color (rPr/color)
# ---------------------------------------------------------------------------
def test_tamper_10_color(base_profile):
    clean_docx = _create_clean_tailored_docx(os.path.join(TMP_DIR, "clean_10.docx"), base_profile)
    tampered = os.path.join(TMP_DIR, "tamper_10_color.docx")

    def tamper(root):
        r = root.findall(f".//{{{W_NS}}}r")[2]
        rPr = r.find(f"{{{W_NS}}}rPr")
        if rPr is None:
            rPr = etree.SubElement(r, f"{{{W_NS}}}rPr")
        color = rPr.find(f"{{{W_NS}}}color")
        if color is None:
            color = etree.SubElement(rPr, f"{{{W_NS}}}color")
        color.attrib[f"{{{W_NS}}}val"] = "FF0000"

    _tamper_document_xml(clean_docx, tampered, tamper)
    res = check_template_integrity(SAMPLE_DOCX, tampered, base_profile, accepted_changes=[{"slot_id": "slot_2"}])
    assert res.integrity_report.passed is False
    assert res.status == Status.failed
    assert any("Invariant 4 Failed" in v for v in res.integrity_report.violations)


# ---------------------------------------------------------------------------
# Tamper Variant 11: Bold/Italic (rPr/b, rPr/i)
# ---------------------------------------------------------------------------
def test_tamper_11_bold_italic(base_profile):
    clean_docx = _create_clean_tailored_docx(os.path.join(TMP_DIR, "clean_11.docx"), base_profile)
    tampered = os.path.join(TMP_DIR, "tamper_11_bold.docx")

    def tamper(root):
        r = root.findall(f".//{{{W_NS}}}r")[2]
        rPr = r.find(f"{{{W_NS}}}rPr")
        if rPr is None:
            rPr = etree.SubElement(r, f"{{{W_NS}}}rPr")
        etree.SubElement(rPr, f"{{{W_NS}}}b")

    _tamper_document_xml(clean_docx, tampered, tamper)
    res = check_template_integrity(SAMPLE_DOCX, tampered, base_profile, accepted_changes=[{"slot_id": "slot_2"}])
    assert res.integrity_report.passed is False
    assert res.status == Status.failed
    assert any("Invariant 4 Failed" in v for v in res.integrity_report.violations)


# ---------------------------------------------------------------------------
# Tamper Variant 12: Highlight (rPr/highlight)
# ---------------------------------------------------------------------------
def test_tamper_12_highlight(base_profile):
    clean_docx = _create_clean_tailored_docx(os.path.join(TMP_DIR, "clean_12.docx"), base_profile)
    tampered = os.path.join(TMP_DIR, "tamper_12_highlight.docx")

    def tamper(root):
        r = root.findall(f".//{{{W_NS}}}r")[2]
        rPr = r.find(f"{{{W_NS}}}rPr")
        if rPr is None:
            rPr = etree.SubElement(r, f"{{{W_NS}}}rPr")
        hl = etree.SubElement(rPr, f"{{{W_NS}}}highlight")
        hl.attrib[f"{{{W_NS}}}val"] = "yellow"

    _tamper_document_xml(clean_docx, tampered, tamper)
    res = check_template_integrity(SAMPLE_DOCX, tampered, base_profile, accepted_changes=[{"slot_id": "slot_2"}])
    assert res.integrity_report.passed is False
    assert res.status == Status.failed
    assert any("Invariant 4 Failed" in v for v in res.integrity_report.violations)


# ---------------------------------------------------------------------------
# Tamper Variant 13: Character Spacing (rPr/spacing)
# ---------------------------------------------------------------------------
def test_tamper_13_character_spacing(base_profile):
    clean_docx = _create_clean_tailored_docx(os.path.join(TMP_DIR, "clean_13.docx"), base_profile)
    tampered = os.path.join(TMP_DIR, "tamper_13_spacing.docx")

    def tamper(root):
        r = root.findall(f".//{{{W_NS}}}r")[2]
        rPr = r.find(f"{{{W_NS}}}rPr")
        if rPr is None:
            rPr = etree.SubElement(r, f"{{{W_NS}}}rPr")
        sp = etree.SubElement(rPr, f"{{{W_NS}}}spacing")
        sp.attrib[f"{{{W_NS}}}val"] = "40"

    _tamper_document_xml(clean_docx, tampered, tamper)
    res = check_template_integrity(SAMPLE_DOCX, tampered, base_profile, accepted_changes=[{"slot_id": "slot_2"}])
    assert res.integrity_report.passed is False
    assert res.status == Status.failed
    assert any("Invariant 4 Failed" in v for v in res.integrity_report.violations)


# ---------------------------------------------------------------------------
# Tamper Variant 14: Bullet Style (pPr/numPr)
# ---------------------------------------------------------------------------
def test_tamper_14_bullet_style(base_profile):
    clean_docx = _create_clean_tailored_docx(os.path.join(TMP_DIR, "clean_14.docx"), base_profile)
    tampered = os.path.join(TMP_DIR, "tamper_14_bullet.docx")

    def tamper(root):
        p = root.findall(f".//{{{W_NS}}}p")[2]
        pPr = p.find(f"{{{W_NS}}}pPr")
        if pPr is None:
            pPr = etree.SubElement(p, f"{{{W_NS}}}pPr")
        numPr = etree.SubElement(pPr, f"{{{W_NS}}}numPr")
        ilvl = etree.SubElement(numPr, f"{{{W_NS}}}ilvl")
        ilvl.attrib[f"{{{W_NS}}}val"] = "2"
        numId = etree.SubElement(numPr, f"{{{W_NS}}}numId")
        numId.attrib[f"{{{W_NS}}}val"] = "99"

    _tamper_document_xml(clean_docx, tampered, tamper)
    res = check_template_integrity(SAMPLE_DOCX, tampered, base_profile, accepted_changes=[{"slot_id": "slot_2"}])
    assert res.integrity_report.passed is False
    assert res.status == Status.failed
    assert any("Invariant 3 Failed" in v for v in res.integrity_report.violations)


# ---------------------------------------------------------------------------
# Tamper Variant 15: Header/Footer Non-Document Part
# ---------------------------------------------------------------------------
def test_tamper_15_header_footer_text(base_profile):
    clean_docx = _create_clean_tailored_docx(os.path.join(TMP_DIR, "clean_15.docx"), base_profile)
    tampered = os.path.join(TMP_DIR, "tamper_15_header.docx")

    # Tamper styles.xml or add header
    with zipfile.ZipFile(clean_docx, "r") as zin, zipfile.ZipFile(tampered, "w") as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "word/styles.xml":
                data = data.replace(b"</w:styles>", b"<!-- Tampered Stylesheet -->\n</w:styles>")
            zout.writestr(item.filename, data)

    res = check_template_integrity(SAMPLE_DOCX, tampered, base_profile, accepted_changes=[{"slot_id": "slot_2"}])
    assert res.integrity_report.passed is False
    assert res.status == Status.failed
    assert any("Invariant 1 Failed" in v for v in res.integrity_report.violations)


# ---------------------------------------------------------------------------
# Tamper Variant 16: Moved Text Box
# ---------------------------------------------------------------------------
def test_tamper_16_moved_text_box():
    tampered = os.path.join(TMP_DIR, "tamper_16_textbox.docx")
    with zipfile.ZipFile(TEXTBOX_DOCX, "r") as zin, zipfile.ZipFile(tampered, "w") as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "word/document.xml":
                # Alter text box drawing extent or anchor
                assert b'cx="5000000"' in data
                data = data.replace(b'cx="5000000"', b'cx="7000000"')
            zout.writestr(item.filename, data)

    res = check_template_integrity(TEXTBOX_DOCX, tampered)
    assert res.integrity_report.passed is False
    assert res.status == Status.failed
    assert any("Invariant 2 Failed" in v for v in res.integrity_report.violations)


# ---------------------------------------------------------------------------
# Fuzz Test: Injected Random Unknown XML Elements
# ---------------------------------------------------------------------------
def test_fuzz_random_unknown_xml_element(base_profile):
    clean_docx = _create_clean_tailored_docx(os.path.join(TMP_DIR, "clean_fuzz.docx"), base_profile)
    tampered = os.path.join(TMP_DIR, "tamper_fuzz.docx")

    def tamper(root):
        p = root.findall(f".//{{{W_NS}}}p")[2]
        pPr = p.find(f"{{{W_NS}}}pPr")
        if pPr is not None:
            fuzz_el = etree.SubElement(pPr, f"{{{W_NS}}}unrecognizedFuzzElement")
            fuzz_el.attrib["randomParam"] = "adversarial_payload_xyz"

    _tamper_document_xml(clean_docx, tampered, tamper)
    res = check_template_integrity(SAMPLE_DOCX, tampered, base_profile, accepted_changes=[{"slot_id": "slot_2"}])
    assert res.integrity_report.passed is False
    assert res.status == Status.failed
    assert any("Invariant 3 Failed" in v for v in res.integrity_report.violations)
