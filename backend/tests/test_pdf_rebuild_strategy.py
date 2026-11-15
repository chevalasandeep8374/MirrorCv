import os
import pytest
from app.services.pdf_extractor import extract_pdf_spans_and_assets
from app.services.pdf_font_analyzer import analyze_pdf_fonts
from app.services.pdf_layout_analyzer import analyze_pdf_layout
from app.services.pdf_role_adapter import process_pdf_roles_and_content
from app.services.writers.pdf_rebuild_strategy import PdfRebuildWriterStrategy

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures", "pdf")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads", "test_runs")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def test_rebuild_writer_fixture_a():
    a_path = os.path.join(FIXTURES_DIR, "fixture_a_word_single_col.pdf")
    out_path = os.path.join(OUTPUT_DIR, "rebuild_fixture_a.pdf")

    layout = extract_pdf_spans_and_assets(a_path)
    layout = analyze_pdf_layout(layout)
    font_table = analyze_pdf_fonts(a_path, layout)
    role_map, content, style, c_to_p, c_to_boxes = process_pdf_roles_and_content(layout)

    writer = PdfRebuildWriterStrategy()
    template_data = {
        "layout": layout,
        "style": style,
        "content_to_paragraphs": c_to_p,
        "font_table": font_table,
    }

    writer.write(content, a_path, out_path, template_data=template_data)
    assert os.path.exists(out_path)

    score = writer.measure(a_path, out_path, font_table=font_table)
    assert score.page_count_score == 100.0
    assert score.total_score >= 70.0


def test_rebuild_writer_fixture_c_twocol():
    c_path = os.path.join(FIXTURES_DIR, "fixture_c_canva_twocol.pdf")
    out_path = os.path.join(OUTPUT_DIR, "rebuild_fixture_c.pdf")

    layout = extract_pdf_spans_and_assets(c_path)
    layout = analyze_pdf_layout(layout)
    font_table = analyze_pdf_fonts(c_path, layout)
    role_map, content, style, c_to_p, c_to_boxes = process_pdf_roles_and_content(layout)

    writer = PdfRebuildWriterStrategy()
    template_data = {
        "layout": layout,
        "style": style,
        "content_to_paragraphs": c_to_p,
        "font_table": font_table,
    }

    writer.write(content, c_path, out_path, template_data=template_data)
    assert os.path.exists(out_path)

    score = writer.measure(c_path, out_path, font_table=font_table)
    assert score.page_count_score == 100.0
    assert score.total_score >= 70.0
