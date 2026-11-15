import os
import pytest
from app.services.docx_rendering_measurements import (
    evaluate_font_confidence,
    calculate_frequency_weighted_advance,
    measure_lines,
    calculate_paragraph_budget,
    extract_pdf_lines,
)


def test_font_confidence_and_margins():
    # 1. Standard fonts with metric substitutes (Calibri -> Carlito)
    calibri_status = evaluate_font_confidence("Calibri")
    assert calibri_status["budget_margin"] == 0.97
    assert calibri_status["confidence"] in ("exact", "metric_compatible")

    times_status = evaluate_font_confidence("Times New Roman")
    assert times_status["budget_margin"] == 0.97

    # 2. Aptos has no metric-compatible substitute -> low confidence & 8% margin (0.92)
    aptos_status = evaluate_font_confidence("Aptos")
    assert aptos_status["confidence"] == "low_confidence"
    assert aptos_status["budget_margin"] == 0.92
    assert "0.92" in str(aptos_status["budget_margin"])

    # 3. Open source font (Roboto)
    roboto_status = evaluate_font_confidence("Roboto")
    assert roboto_status["confidence"] in ("exact", "metric_compatible")
    assert roboto_status["budget_margin"] == 0.97


def test_frequency_weighted_advance():
    text_narrow = "iiiiii llllll 111111"
    text_wide = "WWWWWW MMMMMM @@@@@@"

    adv_narrow = calculate_frequency_weighted_advance(text_narrow, font_family="Calibri", font_size_pt=11.0)
    adv_wide = calculate_frequency_weighted_advance(text_wide, font_family="Calibri", font_size_pt=11.0)

    # Wide characters must produce significantly larger advance than narrow characters
    assert adv_wide > adv_narrow * 1.8


def test_measure_lines_word_wrap_simulator():
    slot = {
        "line_width_pt": 200.0,
        "resolved_formatting": {
            "font_family": "Calibri",
            "font_size_pt": 11.0,
            "bold": False,
        },
    }

    short_text = "This is a short line."
    lines_short = measure_lines(short_text, slot)
    assert lines_short == 1

    longer_text = (
        "This is a longer paragraph that definitely contains enough words and text "
        "to exceed two hundred points of width and must wrap into multiple lines."
    )
    lines_longer = measure_lines(longer_text, slot)
    assert lines_longer >= 3

    # Hard newlines must force new lines
    two_lines_text = "First line\nSecond line"
    assert measure_lines(two_lines_text, slot) == 2


def test_budget_validation_synthetic_fill():
    """Validates that filling a slot with max_chars (x0.97) does NOT increase line count,

    whereas hard_max_chars * 1.15 DOES wrap into the next line.
    """
    line_width = 400.0
    budget = calculate_paragraph_budget(
        text="Architected distributed event streaming platform handling 250k messages per second.",
        line_width_pt=line_width,
        font_family="Calibri",
        font_size_pt=11.0,
        rendered_lines=1,
    )

    assert budget.max_lines == 1
    assert budget.budget_margin == 0.97
    assert budget.max_chars < budget.hard_max_chars

    slot = {
        "line_width_pt": line_width,
        "resolved_formatting": {
            "font_family": "Calibri",
            "font_size_pt": 11.0,
        },
    }

    # 1. Fill with typical words up to max_chars length
    word = "data "
    repeat_count = budget.max_chars // len(word)
    synthetic_safe_text = (word * repeat_count).strip()
    assert len(synthetic_safe_text) <= budget.max_chars

    simulated_lines = measure_lines(synthetic_safe_text, slot)
    # Line count must NOT increase (must fit in budget.max_lines)
    assert simulated_lines <= budget.max_lines

    # 2. Assert that hard_max_chars * 1.15 DOES wrap into an additional line
    overflow_len = int(budget.hard_max_chars * 1.15)
    overflow_repeats = (overflow_len // len(word)) + 1
    synthetic_overflow_text = (word * overflow_repeats).strip()
    assert len(synthetic_overflow_text) > budget.hard_max_chars

    overflow_lines = measure_lines(synthetic_overflow_text, slot)
    # Must wrap!
    assert overflow_lines > budget.max_lines
