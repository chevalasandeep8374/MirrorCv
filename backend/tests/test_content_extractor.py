import os
import pytest
from app.services.docx_fingerprint import fingerprint_docx
from app.services.role_classifier import classify_paragraphs
from app.services.content_extractor import extract_content_and_style
from app.schemas.content import ResumeContent
from app.schemas.style import ResumeStyle

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


def test_extract_single_column():
    path = os.path.join(FIXTURES_DIR, "sample_single_column.docx")
    fp = fingerprint_docx(path)
    role_map = classify_paragraphs(fp)
    content, style, c_to_p = extract_content_and_style(fp, role_map)

    # Validate Types
    assert isinstance(content, ResumeContent)
    assert isinstance(style, ResumeStyle)

    # Validate Header
    assert content.header.name == "Alex Mercer"
    assert "alex.mercer@example.com" in content.header.email
    assert content.header.phone != ""
    assert "San Francisco" in content.header.location

    # Validate Sections
    sec_types = [s.type for s in content.sections]
    assert "summary" in sec_types
    assert "experience" in sec_types
    assert "skills" in sec_types
    assert "education" in sec_types

    # Validate Bullets
    exp_sec = next(s for s in content.sections if s.type == "experience")
    assert len(exp_sec.items) >= 1
    assert len(exp_sec.items[0].bullets) >= 3
    assert any("Architected" in b.text for b in exp_sec.items[0].bullets)

    # Validate Style Tokens
    assert style.pageSize == "A4"
    assert style.margins.top == 36.0
    assert style.typography.baseFontFamily == "Calibri"
    assert style.typography.fontSizes.name == 22.0
    assert style.layout.type == "single"

    # Validate Mapping
    assert len(c_to_p) > 5


def test_extract_table_two_column():
    path = os.path.join(FIXTURES_DIR, "sample_table_two_column.docx")
    fp = fingerprint_docx(path)
    role_map = classify_paragraphs(fp)
    content, style, c_to_p = extract_content_and_style(fp, role_map)

    assert content.header.name == "ALEX MERCER"
    # Should detect two-column sidebar layout
    assert style.layout.type == "sidebar_left"
    assert len(style.layout.sidebarSectionIds) > 0
    assert len(style.layout.mainSectionIds) > 0
