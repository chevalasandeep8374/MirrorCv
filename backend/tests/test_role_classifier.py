import os
import pytest
from app.services.docx_fingerprint import fingerprint_docx
from app.services.role_classifier import classify_paragraphs

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


def test_classify_single_column():
    path = os.path.join(FIXTURES_DIR, "sample_single_column.docx")
    fp = fingerprint_docx(path)
    role_map = classify_paragraphs(fp)

    roles = role_map.paragraph_roles

    # Check Name
    assert roles[0].role == "name"
    assert roles[0].field == "name"

    # Check Contact
    assert roles[1].role == "contact"

    # Check Section Headings
    headings = [r for idx, r in roles.items() if r.role == "section_heading"]
    assert len(headings) >= 4  # Summary, Experience, Skills, Education

    # Check Bullets
    bullets = [r for idx, r in roles.items() if r.role == "bullet"]
    assert len(bullets) >= 3

    # Check Sections Hierarchy
    assert len(role_map.sections_hierarchy) >= 4
    exp_sec = next((s for s in role_map.sections_hierarchy if s.type == "experience"), None)
    assert exp_sec is not None
    assert len(exp_sec.items) >= 1
    assert len(exp_sec.items[0].bullet_para_indices) >= 3

    # Check Content-to-Paragraph Mapping
    assert "header.name" in role_map.content_to_paragraph_indices
    assert "header.contact" in role_map.content_to_paragraph_indices


def test_classify_table_two_column():
    path = os.path.join(FIXTURES_DIR, "sample_table_two_column.docx")
    fp = fingerprint_docx(path)
    role_map = classify_paragraphs(fp)

    roles = role_map.paragraph_roles

    # Header Name & Title
    assert roles[0].role == "name"
    assert roles[1].role == "title"

    # Verify section headings across both sidebar and main columns
    sec_types = {s.type for s in role_map.sections_hierarchy}
    assert "skills" in sec_types or "education" in sec_types
    assert "summary" in sec_types or "experience" in sec_types

    # Verify bullet roles inside table
    bullets = [r for idx, r in roles.items() if r.role == "bullet"]
    assert len(bullets) >= 2
