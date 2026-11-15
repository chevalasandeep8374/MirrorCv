import os
import pytest
from PIL import Image
from app.services.pdf_ocr_service import process_scanned_pdf, BaseOcrEngine
from app.services.pdf_font_analyzer import analyze_pdf_fonts
from app.services.pdf_layout_analyzer import analyze_pdf_layout
from app.services.pdf_role_adapter import process_pdf_roles_and_content
from app.services.pdf_strategy_selector import select_best_strategy
from app.services.writers.pdf_rebuild_strategy import PdfRebuildWriterStrategy

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures", "pdf")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads", "test_runs")
os.makedirs(OUTPUT_DIR, exist_ok=True)


class MockLowConfidenceEngine(BaseOcrEngine):
    def extract_page_data(self, image: Image.Image, page_num: int, dpi: int = 300):
        # Returns low confidence < 0.6
        return [], 0.45


def test_process_scanned_pdf_fixture_e():
    e_path = os.path.join(FIXTURES_DIR, "fixture_e_scanned.pdf")
    layout = process_scanned_pdf(e_path)

    assert layout.document_metadata.is_scanned is True
    assert len(layout.blocks) >= 5

    # Run through layout and role adapter
    analyzed_layout = analyze_pdf_layout(layout)
    font_table = analyze_pdf_fonts(e_path, analyzed_layout)
    role_map, content, style, c_to_p, c_to_boxes = process_pdf_roles_and_content(analyzed_layout)

    assert "ALEX MERCER" in content.header.name
    assert len(content.sections) >= 2

    # Auto-strategy selection: scanned document selects rebuild / Tier C
    writer, score, preview_path = select_best_strategy(
        template_path=e_path,
        layout=analyzed_layout,
        role_map=role_map,
        content=content,
        style=style,
        content_to_paragraphs=c_to_p,
        font_table=font_table,
        work_dir=OUTPUT_DIR,
    )

    assert isinstance(writer, PdfRebuildWriterStrategy)
    assert score.tier == "C"
    assert score.selected_strategy == "ocr_rebuild"
    assert score.total_score >= 70.0


def test_low_confidence_ocr_rejection():
    e_path = os.path.join(FIXTURES_DIR, "fixture_e_scanned.pdf")
    with pytest.raises(ValueError) as excinfo:
        process_scanned_pdf(e_path, ocr_engine=MockLowConfidenceEngine())

    assert "poor OCR confidence" in str(excinfo.value)
