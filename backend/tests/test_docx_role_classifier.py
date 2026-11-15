import pytest
from docx import Document
from docx.shared import Pt

from app.services.docx_fingerprint import fingerprint_docx
from app.services.role_classifier import (
    classify_paragraphs,
    detect_phone_number,
    detect_section_heading,
)


def test_phone_detection():
    # Various phone formats
    assert detect_phone_number("+1 (555) 234-5678") is True
    assert detect_phone_number("+91 98765 43210") is True
    assert detect_phone_number("123-456-7890") is True
    assert detect_phone_number("(800) 555-0199") is True
    assert detect_phone_number("442071838750") is True  # 12 digits

    # Not phone numbers
    assert detect_phone_number("alex.mercer@gmail.com") is False
    assert detect_phone_number("San Francisco, CA") is False
    assert detect_phone_number("123 Main Street") is False
    assert detect_phone_number("2020 - 2024") is False


def test_extended_heading_dictionary():
    extended_headings = [
        "Career Objective",
        "Objective",
        "Internships",
        "Academic Projects",
        "Academic Qualification",
        "Training",
        "Strengths",
        "Extracurricular Activities",
        "Positions of Responsibility",
        "Declaration",
        "Personal Details",
        "Hobbies",
    ]

    for heading in extended_headings:
        match = detect_section_heading(heading)
        assert match is not None, f"Failed to detect heading: {heading}"
        assert match[1] == heading


def test_name_rule_requires_largest_font_size(tmp_path):
    """Verifies that name detection requires the largest font size in the first 3 paragraphs,

    even if another paragraph in the first 3 is bold.
    """
    doc_path = tmp_path / "name_font_size.docx"
    doc = Document()

    # Para 0: Bold but small title (e.g. 12pt)
    p0 = doc.add_paragraph()
    r0 = p0.add_run("CURRICULUM VITAE")
    r0.bold = True
    r0.font.size = Pt(12)

    # Para 1: Candidate Name with LARGEST font size (20pt), normal weight
    p1 = doc.add_paragraph()
    r1 = p1.add_run("Jane Doe")
    r1.bold = False
    r1.font.size = Pt(20)

    # Para 2: Contact line (10pt)
    p2 = doc.add_paragraph()
    r2 = p2.add_run("jane@example.com | +1 555-019-2834")
    r2.font.size = Pt(10)

    # Section heading
    p3 = doc.add_paragraph()
    r3 = p3.add_run("CAREER OBJECTIVE")
    r3.bold = True
    r3.font.size = Pt(14)

    p4 = doc.add_paragraph("Seeking a senior software engineering role.")

    doc.save(str(doc_path))

    fp = fingerprint_docx(str(doc_path))
    role_map = classify_paragraphs(fp)

    # Jane Doe (p1) must be classified as 'name' because it has the largest font size in first 3
    assert role_map.paragraph_roles[p1._p].role == "name" if p1._p in role_map.paragraph_roles else role_map.paragraph_roles[1].role == "name"
    assert role_map.paragraph_roles[1].field == "name"

    # p2 must be contact
    assert role_map.paragraph_roles[2].role == "contact"

    # p3 must be section_heading for career objective
    assert role_map.paragraph_roles[3].role == "section_heading"
    assert role_map.sections_hierarchy[0].type == "summary"
