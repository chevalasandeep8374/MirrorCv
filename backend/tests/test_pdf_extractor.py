import os
import pytest
from app.services.pdf_extractor import (
    validate_pdf,
    extract_pdf_spans_and_assets,
    detect_scanned_pdf,
)

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures", "pdf")


def test_validate_pdf():
    a_path = os.path.join(FIXTURES_DIR, "fixture_a_word_single_col.pdf")
    is_valid, err, page_count = validate_pdf(a_path)
    assert is_valid is True
    assert err is None
    assert page_count == 1

    # Non-existent file
    is_valid_fake, err_fake, _ = validate_pdf("non_existent.pdf")
    assert is_valid_fake is False
    assert "does not exist" in err_fake


def test_extract_spans_fixture_a():
    a_path = os.path.join(FIXTURES_DIR, "fixture_a_word_single_col.pdf")
    layout = extract_pdf_spans_and_assets(a_path)

    assert layout.document_metadata.page_count == 1
    assert layout.document_metadata.is_scanned is False
    assert len(layout.blocks) > 0
    assert len(layout.links) > 0
    assert layout.links[0].uri == "https://alexmercer.dev"

    # Check that header block contains ALEX MERCER
    all_text = " ".join(b.text for b in layout.blocks)
    assert "ALEX MERCER" in all_text
    assert "PROFESSIONAL SUMMARY" in all_text
    assert "WORK EXPERIENCE" in all_text


def test_extract_drawings_fixture_c():
    c_path = os.path.join(FIXTURES_DIR, "fixture_c_canva_twocol.pdf")
    layout = extract_pdf_spans_and_assets(c_path)

    assert layout.document_metadata.has_vector_drawings is True
    assert len(layout.vector_drawings) >= 5

    # Check for sidebar background rectangle
    sidebar_drawings = [d for d in layout.vector_drawings if d.type == "rect"]
    assert len(sidebar_drawings) > 0

    all_text = " ".join(b.text for b in layout.blocks)
    assert "MARCUS CHEN" in all_text
    assert "CONTACT" in all_text
    assert "SKILLS" in all_text


def test_detect_scanned_fixture_e():
    e_path = os.path.join(FIXTURES_DIR, "fixture_e_scanned.pdf")
    layout = extract_pdf_spans_and_assets(e_path)

    assert layout.document_metadata.is_scanned is True
    assert layout.document_metadata.image_count >= 1
