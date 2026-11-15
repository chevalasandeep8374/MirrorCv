"""Unit tests for template_integrity_checker: Validating the two-tier split
(TEMPLATE INTEGRITY -> failed vs LAYOUT FIT -> layout_changed),
positive conformance, and negative tampering tests.
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
from app.services.template_integrity_checker import check_template_integrity
from app.services.fidelity_writer import write_tailored_docx_repackaged
from app.services.change_planner import Operation, OperationType

FIXTURES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "fixtures"))
TMP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "tmp_output"))
os.makedirs(TMP_DIR, exist_ok=True)

SAMPLE_DOCX = os.path.join(FIXTURES_DIR, "sample_single_column.docx")


@pytest.fixture
def sample_profile():
    doc = Document(SAMPLE_DOCX)
    slots = []
    slot_map = {}
    for i, p in enumerate(doc.paragraphs):
        sid = f"slot_{i}"
        font_name = p.runs[0].font.name if (p.runs and p.runs[0].font.name) else "Calibri"
        font_size = p.runs[0].font.size.pt if (p.runs and p.runs[0].font.size) else 11.0
        p_lines = max(2, p.text.count("\n") + 1)
        if len(p.text) > 120:
            p_lines = max(p_lines, 3)
        if len(p.text) > 200:
            p_lines = max(p_lines, 4)

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
        template_profile_id="tpl_integ_test",
        resume_id="res_integ_test",
        version=1,
        source_type=SourceType.uploaded_docx,
        slots=slots,
        slot_map=slot_map,
        fidelity_score=99.0,
        status=ProfileStatus.ready,
    )


def test_integrity_clean_tailored_docx_passes(sample_profile):
    """Proves that a cleanly repackaged document passes all integrity invariants."""
    out_docx = os.path.join(TMP_DIR, "test_integ_clean.docx")
    ops = [
        Operation(
            op_id="op_1",
            type=OperationType.set_text,
            slot_id="slot_2",
            text="Clean tailored bullet text for testing.",
        )
    ]

    write_tailored_docx_repackaged(
        template_docx_path=SAMPLE_DOCX,
        operations=ops,
        template_profile=sample_profile,
        output_docx_path=out_docx,
    )

    result = check_template_integrity(
        template_docx_path=SAMPLE_DOCX,
        tailored_docx_path=out_docx,
        template_profile=sample_profile,
        accepted_changes=[{"slot_id": "slot_2"}],
        page_count_before=1,
        page_count_after=1,
    )

    assert result.integrity_report.passed is True
    assert result.layout_fit_passed is True
    assert result.status == Status.ready
    assert len(result.integrity_report.violations) == 0


def test_tamper_non_document_zip_part_fails_invariant_1(sample_profile):
    """Negative test: Tampering with a non-document part (styles.xml) fails Invariant 1."""
    out_docx = os.path.join(TMP_DIR, "test_tamper_inv1.docx")
    ops = [
        Operation(
            op_id="op_1",
            type=OperationType.set_text,
            slot_id="slot_2",
            text="Clean bullet.",
        )
    ]

    write_tailored_docx_repackaged(
        template_docx_path=SAMPLE_DOCX,
        operations=ops,
        template_profile=sample_profile,
        output_docx_path=out_docx,
    )

    # Tamper with word/styles.xml inside the zip
    tampered_docx = os.path.join(TMP_DIR, "test_tamper_inv1_corrupted.docx")
    with zipfile.ZipFile(out_docx, "r") as zin, zipfile.ZipFile(tampered_docx, "w") as zout:
        for item in zin.infolist():
            if item.filename == "word/styles.xml":
                zout.writestr(item.filename, zin.read(item.filename) + b"<!-- Tampered Styles -->")
            else:
                zout.writestr(item.filename, zin.read(item.filename))

    result = check_template_integrity(
        template_docx_path=SAMPLE_DOCX,
        tailored_docx_path=tampered_docx,
        template_profile=sample_profile,
        accepted_changes=[{"slot_id": "slot_2"}],
        page_count_before=1,
        page_count_after=1,
    )

    assert result.integrity_report.passed is False
    assert result.status == Status.failed
    assert any("Invariant 1 Failed" in v for v in result.integrity_report.violations)


def test_tamper_margins_fails_invariant_2(sample_profile):
    """Negative test: Tampering with section margins fails Invariant 2."""
    out_docx = os.path.join(TMP_DIR, "test_tamper_inv2.docx")
    ops = [Operation(op_id="op_1", type=OperationType.set_text, slot_id="slot_2", text="Clean bullet.")]
    write_tailored_docx_repackaged(SAMPLE_DOCX, ops, sample_profile, out_docx)

    # Modify sectPr in document.xml
    tampered_docx = os.path.join(TMP_DIR, "test_tamper_inv2_corrupted.docx")
    with zipfile.ZipFile(out_docx, "r") as zin, zipfile.ZipFile(tampered_docx, "w") as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "word/document.xml":
                # Alter top margin from 720 to 1440
                data = data.replace(b'w:top="720"', b'w:top="1440"')
            zout.writestr(item.filename, data)

    result = check_template_integrity(
        template_docx_path=SAMPLE_DOCX,
        tailored_docx_path=tampered_docx,
        template_profile=sample_profile,
        accepted_changes=[{"slot_id": "slot_2"}],
        page_count_before=1,
        page_count_after=1,
    )

    assert result.integrity_report.passed is False
    assert result.status == Status.failed
    assert any("Invariant 2 Failed" in v for v in result.integrity_report.violations)


def test_tamper_font_size_fails_invariant_4(sample_profile):
    """Negative test: Illegally shrinking font size fails Invariant 4."""
    out_docx = os.path.join(TMP_DIR, "test_tamper_inv4.docx")
    ops = [Operation(op_id="op_1", type=OperationType.set_text, slot_id="slot_2", text="Clean bullet.")]
    write_tailored_docx_repackaged(SAMPLE_DOCX, ops, sample_profile, out_docx)

    tampered_docx = os.path.join(TMP_DIR, "test_tamper_inv4_corrupted.docx")
    w_ns = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    with zipfile.ZipFile(out_docx, "r") as zin, zipfile.ZipFile(tampered_docx, "w") as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "word/document.xml":
                root = etree.fromstring(data)
                paras = [p for p in root.iter() if p.tag == f"{{{w_ns}}}p"]
                r = paras[2].find(f".//{{{w_ns}}}r")
                if r is not None:
                    rPr = r.find(f"{{{w_ns}}}rPr")
                    if rPr is None:
                        rPr = etree.SubElement(r, f"{{{w_ns}}}rPr")
                    sz = rPr.find(f"{{{w_ns}}}sz")
                    if sz is None:
                        sz = etree.SubElement(rPr, f"{{{w_ns}}}sz")
                    sz.attrib[f"{{{w_ns}}}val"] = "12"  # 6 pt (down from 11pt)
                data = etree.tostring(root, xml_declaration=True, encoding="UTF-8")
            zout.writestr(item.filename, data)

    result = check_template_integrity(
        template_docx_path=SAMPLE_DOCX,
        tailored_docx_path=tampered_docx,
        template_profile=sample_profile,
        accepted_changes=[{"slot_id": "slot_2"}],
        page_count_before=1,
        page_count_after=1,
    )

    assert result.integrity_report.passed is False
    assert result.status == Status.failed
    assert any("Invariant 4 Failed" in v for v in result.integrity_report.violations)


def test_tamper_duplicate_para_id_fails_invariant_6(sample_profile):
    """Negative test: Duplicate w14:paraId fails Invariant 6."""
    out_docx = os.path.join(TMP_DIR, "test_tamper_inv6.docx")
    ops = [Operation(op_id="op_1", type=OperationType.set_text, slot_id="slot_2", text="Clean bullet.")]
    write_tailored_docx_repackaged(SAMPLE_DOCX, ops, sample_profile, out_docx)

    # Insert duplicate paraIds in document.xml
    tampered_docx = os.path.join(TMP_DIR, "test_tamper_inv6_corrupted.docx")
    w14_ns = "http://schemas.microsoft.com/office/word/2010/wordml"
    with zipfile.ZipFile(out_docx, "r") as zin, zipfile.ZipFile(tampered_docx, "w") as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "word/document.xml":
                root = etree.fromstring(data)
                # Assign identical paraId to two paragraphs
                paras = root.xpath(".//w:p", namespaces={"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"})
                paras[0].attrib[f"{{{w14_ns}}}paraId"] = "DEADBEEF"
                paras[1].attrib[f"{{{w14_ns}}}paraId"] = "DEADBEEF"
                data = etree.tostring(root, xml_declaration=True, encoding="UTF-8")
            zout.writestr(item.filename, data)

    result = check_template_integrity(
        template_docx_path=SAMPLE_DOCX,
        tailored_docx_path=tampered_docx,
        template_profile=sample_profile,
        accepted_changes=[{"slot_id": "slot_2"}],
        page_count_before=1,
        page_count_after=1,
    )

    assert result.integrity_report.passed is False
    assert result.status == Status.failed
    assert any("Invariant 6 Failed" in v for v in result.integrity_report.violations)


def test_layout_fit_overflow_yields_layout_changed(sample_profile):
    """Proves that a page-count overflow passes integrity but yields status 'layout_changed'."""
    out_docx = os.path.join(TMP_DIR, "test_layout_overflow.docx")
    ops = [Operation(op_id="op_1", type=OperationType.set_text, slot_id="slot_2", text="Valid text.")]
    write_tailored_docx_repackaged(SAMPLE_DOCX, ops, sample_profile, out_docx)

    result = check_template_integrity(
        template_docx_path=SAMPLE_DOCX,
        tailored_docx_path=out_docx,
        template_profile=sample_profile,
        accepted_changes=[{"slot_id": "slot_2"}],
        page_count_before=1,
        page_count_after=2,  # Overflow from 1 -> 2 pages
    )

    # Invariants 1-6, 8, container clipping all passed
    assert result.integrity_report.passed is True
    # Layout fit failed due to page count
    assert result.layout_fit_passed is False
    assert any("Page count increased from 1 to 2" in v for v in result.layout_violations)
    # Status is layout_changed, NOT failed!
    assert result.status == Status.layout_changed
