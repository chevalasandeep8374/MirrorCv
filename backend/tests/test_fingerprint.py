import os
import pytest
from app.services.docx_fingerprint import fingerprint_docx

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


def test_fingerprint_single_column():
    path = os.path.join(FIXTURES_DIR, "sample_single_column.docx")
    assert os.path.exists(path), f"Fixture {path} not found"

    fp = fingerprint_docx(path)
    meta = fp.document_metadata
    assert meta.page_size.name == "A4"
    assert meta.margins.top_pt == 36.0
    assert meta.margins.left_pt == 40.0
    assert len(fp.paragraphs) >= 10

    # First paragraph is name
    p0 = fp.paragraphs[0]
    assert "Alex Mercer" in p0.text
    assert p0.alignment == "center"
    assert p0.runs[0].formatting.bold is True
    assert p0.runs[0].formatting.font_size_pt == 22.0

    # Verify bullet detection
    bullet_paras = [p for p in fp.paragraphs if p.bullet_info.is_bullet]
    assert len(bullet_paras) >= 3
    assert any("Architected" in b.text for b in bullet_paras)


def test_fingerprint_table_two_column():
    path = os.path.join(FIXTURES_DIR, "sample_table_two_column.docx")
    assert os.path.exists(path)

    fp = fingerprint_docx(path)
    assert fp.document_metadata.total_tables >= 1

    # Check table cells are detected
    cell_paras = [p for p in fp.paragraphs if p.location.type == "table_cell"]
    assert len(cell_paras) >= 6

    # Verify sidebar and main columns are captured
    col_0_paras = [p for p in cell_paras if p.location.col_index == 0]
    col_1_paras = [p for p in cell_paras if p.location.col_index == 1]
    assert len(col_0_paras) >= 2
    assert len(col_1_paras) >= 2

    # Check sidebar contains CONTACT or SKILLS
    assert any("CONTACT" in p.text or "SKILLS" in p.text for p in col_0_paras)
    # Check main column contains SUMMARY or WORK EXPERIENCE
    assert any("SUMMARY" in p.text or "WORK EXPERIENCE" in p.text for p in col_1_paras)


def test_fingerprint_text_box():
    path = os.path.join(FIXTURES_DIR, "sample_text_box.docx")
    assert os.path.exists(path)

    fp = fingerprint_docx(path)
    assert fp.document_metadata.has_text_boxes is True

    # Find the textbox paragraph
    tx_paras = [p for p in fp.paragraphs if p.location.type == "text_box"]
    assert len(tx_paras) >= 1
    assert any("TEXT BOX HEADER" in p.text for p in tx_paras)
