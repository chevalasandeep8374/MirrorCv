import os
import pytest
from app.services.pdf_extractor import extract_pdf_spans_and_assets
from app.services.pdf_font_analyzer import analyze_pdf_fonts
from app.services.pdf_layout_analyzer import analyze_pdf_layout
from app.services.pdf_role_adapter import process_pdf_roles_and_content
from app.services.pdf_strategy_selector import select_best_strategy
from app.services.writers.pdf_inplace_strategy import PdfInPlaceWriterStrategy
from app.services.writers.pdf_rebuild_strategy import PdfRebuildWriterStrategy

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures", "pdf")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads", "test_runs")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def test_auto_strategy_selection_fixture_a():
    a_path = os.path.join(FIXTURES_DIR, "fixture_a_word_single_col.pdf")
    layout = extract_pdf_spans_and_assets(a_path)
    layout = analyze_pdf_layout(layout)
    font_table = analyze_pdf_fonts(a_path, layout)
    role_map, content, style, c_to_p, c_to_boxes = process_pdf_roles_and_content(layout)

    writer, score, preview_path = select_best_strategy(
        template_path=a_path,
        layout=layout,
        role_map=role_map,
        content=content,
        style=style,
        content_to_paragraphs=c_to_p,
        font_table=font_table,
        work_dir=OUTPUT_DIR,
    )

    assert isinstance(writer, PdfInPlaceWriterStrategy)
    assert score.tier == "A"
    assert score.selected_strategy == "in_place"
    assert score.total_score >= 95.0
    assert os.path.exists(preview_path)
