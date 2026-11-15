import os
import pytest
from app.services.pdf_extractor import extract_pdf_spans_and_assets
from app.services.pdf_layout_analyzer import analyze_pdf_layout
from app.services.pdf_role_adapter import (
    pdf_layout_to_fingerprint,
    process_pdf_roles_and_content,
)

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures", "pdf")


def test_pdf_role_adapter_fixture_a():
    a_path = os.path.join(FIXTURES_DIR, "fixture_a_word_single_col.pdf")
    layout = extract_pdf_spans_and_assets(a_path)
    layout = analyze_pdf_layout(layout)

    role_map, content, style, c_to_p, c_to_boxes = process_pdf_roles_and_content(layout)

    # 1. Check Role Map
    assert len(role_map.sections_hierarchy) >= 3
    section_types = [s.type for s in role_map.sections_hierarchy]
    assert "summary" in section_types or "experience" in section_types

    # 2. Check Content extraction
    assert "ALEX MERCER" in content.header.name
    assert "alex.mercer@example.com" in (content.header.email or "")

    # Check Experience items and bullets
    exp_sections = [s for s in content.sections if s.type == "experience"]
    assert len(exp_sections) >= 1
    assert len(exp_sections[0].items) >= 1
    assert len(exp_sections[0].items[0].bullets) >= 1

    # 3. Check content_to_line_boxes mapping
    assert len(c_to_boxes) > 0
    # Every bullet should map to at least one source line box with bounding coordinates
    bullet_box_found = False
    for key, boxes in c_to_boxes.items():
        if "b-" in key and len(boxes) > 0:
            bullet_box_found = True
            first_box = boxes[0]
            assert "bbox" in first_box
            assert len(first_box["bbox"]) == 4
            assert first_box["page_number"] == 1
            break
    assert bullet_box_found is True


def test_pdf_role_adapter_fixture_c_twocol():
    c_path = os.path.join(FIXTURES_DIR, "fixture_c_canva_twocol.pdf")
    layout = extract_pdf_spans_and_assets(c_path)
    layout = analyze_pdf_layout(layout)

    role_map, content, style, c_to_p, c_to_boxes = process_pdf_roles_and_content(layout)

    assert "MARCUS CHEN" in content.header.name
    assert len(content.sections) >= 2


def test_pdf_role_adapter_fixture_b_latex():
    b_path = os.path.join(FIXTURES_DIR, "fixture_b_latex.pdf")
    layout = extract_pdf_spans_and_assets(b_path)
    layout = analyze_pdf_layout(layout)

    role_map, content, style, c_to_p, c_to_boxes = process_pdf_roles_and_content(layout)
    assert "ROSTOVA" in content.header.name
    assert len(content.sections) >= 2


def test_pdf_role_adapter_fixture_d_gdocs():
    d_path = os.path.join(FIXTURES_DIR, "fixture_d_gdocs.pdf")
    layout = extract_pdf_spans_and_assets(d_path)
    layout = analyze_pdf_layout(layout)

    role_map, content, style, c_to_p, c_to_boxes = process_pdf_roles_and_content(layout)
    assert "Sarah Jenkins" in content.header.name
    assert len(content.sections) >= 2

