import os
import pytest
import fitz
from app.services.pdf_extractor import extract_pdf_spans_and_assets
from app.services.pdf_font_analyzer import analyze_pdf_fonts
from app.services.pdf_layout_analyzer import analyze_pdf_layout
from app.services.pdf_role_adapter import process_pdf_roles_and_content
from app.services.writers.pdf_inplace_strategy import PdfInPlaceWriterStrategy

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures", "pdf")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads", "test_runs")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def test_noop_fidelity_fixture_a():
    a_path = os.path.join(FIXTURES_DIR, "fixture_a_word_single_col.pdf")
    out_path = os.path.join(OUTPUT_DIR, "noop_fixture_a.pdf")

    layout = extract_pdf_spans_and_assets(a_path)
    layout = analyze_pdf_layout(layout)
    font_table = analyze_pdf_fonts(a_path, layout)
    role_map, content, style, c_to_p, c_to_boxes = process_pdf_roles_and_content(layout)

    writer = PdfInPlaceWriterStrategy()
    template_data = {
        "layout": layout,
        "role_map": role_map,
        "content_to_paragraphs": c_to_p,
        "font_table": font_table,
    }

    # Run no-op write
    writer.write(content, a_path, out_path, template_data=template_data)
    assert os.path.exists(out_path)

    # Measure fidelity score
    score = writer.measure(a_path, out_path, font_table=font_table)
    assert score.page_count_score == 100.0
    assert score.tier == "A"
    assert score.total_score >= 95.0


def test_redaction_safety_fixture_c_drawings_preserved():
    """Safety test: backgrounds, circles, and divider lines survive untouched after editing."""
    c_path = os.path.join(FIXTURES_DIR, "fixture_c_canva_twocol.pdf")
    out_path = os.path.join(OUTPUT_DIR, "edited_fixture_c.pdf")

    layout = extract_pdf_spans_and_assets(c_path)
    layout = analyze_pdf_layout(layout)
    font_table = analyze_pdf_fonts(c_path, layout)
    role_map, content, style, c_to_p, c_to_boxes = process_pdf_roles_and_content(layout)

    # Count drawings in original
    doc_orig = fitz.open(c_path)
    orig_drawings_count = len(doc_orig[0].get_drawings())
    doc_orig.close()

    writer = PdfInPlaceWriterStrategy()
    template_data = {
        "layout": layout,
        "role_map": role_map,
        "content_to_paragraphs": c_to_p,
        "font_table": font_table,
    }

    # Write
    writer.write(content, c_path, out_path, template_data=template_data)

    # Count drawings in generated
    doc_gen = fitz.open(out_path)
    gen_drawings_count = len(doc_gen[0].get_drawings())
    doc_gen.close()

    assert gen_drawings_count == orig_drawings_count


def test_noop_fidelity_fixture_b_latex():
    b_path = os.path.join(FIXTURES_DIR, "fixture_b_latex.pdf")
    out_path = os.path.join(OUTPUT_DIR, "noop_fixture_b.pdf")

    layout = extract_pdf_spans_and_assets(b_path)
    layout = analyze_pdf_layout(layout)
    font_table = analyze_pdf_fonts(b_path, layout)
    role_map, content, style, c_to_p, c_to_boxes = process_pdf_roles_and_content(layout)

    writer = PdfInPlaceWriterStrategy()
    template_data = {
        "layout": layout,
        "role_map": role_map,
        "content_to_paragraphs": c_to_p,
        "font_table": font_table,
    }

    writer.write(content, b_path, out_path, template_data=template_data)
    score = writer.measure(b_path, out_path, font_table=font_table)

    assert score.page_count_score == 100.0
    assert score.tier == "A"
    assert score.total_score >= 95.0
