import os
import pytest
from app.services.pdf_font_analyzer import (
    parse_font_name,
    resolve_font,
    analyze_pdf_fonts,
    measure_text_width_pt,
)

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures", "pdf")


def test_parse_font_name():
    family, is_subset, is_bold, is_italic = parse_font_name("ABCDEF+Calibri-Bold")
    assert is_subset is True
    assert is_bold is True
    assert is_italic is False
    assert family == "Calibri"

    family2, is_subset2, is_bold2, is_italic2 = parse_font_name("TimesNewRoman-Italic")
    assert is_subset2 is False
    assert is_bold2 is False
    assert is_italic2 is True


def test_resolve_metric_compatible():
    # Calibri -> Carlito (metric compatible)
    calibri_res = resolve_font("ABCDEF+Calibri-Bold")
    assert "Carlito" in calibri_res.resolved_font_name
    assert calibri_res.source == "metric_compatible"
    assert calibri_res.match_confidence >= 0.95
    assert calibri_res.is_subset is True

    # Arial -> Liberation Sans
    arial_res = resolve_font("Arial-Bold")
    assert "Liberation Sans" in calibri_res.resolved_font_name or "Carlito" in calibri_res.resolved_font_name
    assert arial_res.source == "metric_compatible"
    assert arial_res.match_confidence >= 0.95


def test_measure_text_width_pt():
    w1 = measure_text_width_pt("Senior Full Stack Systems Engineer", "helv", 11.0)
    w2 = measure_text_width_pt("Senior Full Stack Systems Engineer", "helv", 22.0)
    assert w1 > 0
    # Double font size should roughly double width
    assert abs(w2 - (w1 * 2)) < 5.0


def test_analyze_pdf_fonts():
    a_path = os.path.join(FIXTURES_DIR, "fixture_a_word_single_col.pdf")
    font_table = analyze_pdf_fonts(a_path)

    assert len(font_table.fonts) > 0
    assert font_table.overall_confidence >= 0.85
