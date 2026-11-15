import os
import pytest
from app.services.pdf_extractor import extract_pdf_spans_and_assets
from app.services.pdf_layout_analyzer import analyze_pdf_layout, detect_bullet_and_indent

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures", "pdf")


def test_detect_bullet_and_indent():
    # Bullet with hanging indent
    is_b, glyph, text, indent = detect_bullet_and_indent("• Developed microservices", 50.0, 40.0)
    assert is_b is True
    assert glyph == "•"
    assert "Developed microservices" in text
    assert indent == 10.0

    # Dash bullet
    is_b2, glyph2, text2, indent2 = detect_bullet_and_indent("- Reduced cloud costs by 38%", 52.0, 40.0)
    assert is_b2 is True
    assert glyph2 == "-"
    assert indent2 == 12.0

    # Plain text
    is_b3, glyph3, text3, indent3 = detect_bullet_and_indent("Alex Mercer", 40.0, 40.0)
    assert is_b3 is False
    assert glyph3 is None


def test_analyze_layout_fixture_a_single_col():
    a_path = os.path.join(FIXTURES_DIR, "fixture_a_word_single_col.pdf")
    layout = extract_pdf_spans_and_assets(a_path)
    analyzed = analyze_pdf_layout(layout)

    # Columns
    assert len(analyzed.columns) >= 1
    assert analyzed.columns[0].type == "main"

    # Blocks have max_width_pt, reading_order
    assert len(analyzed.blocks) > 0
    for idx, b in enumerate(analyzed.blocks):
        assert b.reading_order == idx
        assert b.max_width_pt > 100.0

    # Bullets detected
    bullet_blocks = [b for b in analyzed.blocks if b.bullet_info.is_bullet]
    assert len(bullet_blocks) >= 3
    for bb in bullet_blocks:
        assert bb.bullet_info.glyph in ("•", "-", "▪")


def test_analyze_layout_fixture_c_two_column_sidebar():
    c_path = os.path.join(FIXTURES_DIR, "fixture_c_canva_twocol.pdf")
    layout = extract_pdf_spans_and_assets(c_path)
    analyzed = analyze_pdf_layout(layout)

    # Sidebar detected
    sidebar_cols = [c for c in analyzed.columns if c.type == "sidebar"]
    main_cols = [c for c in analyzed.columns if c.type == "main"]
    assert len(sidebar_cols) >= 1
    assert len(main_cols) >= 1

    # Blocks assigned to sidebar and main
    sb_blocks = [b for b in analyzed.blocks if "sb" in b.column_id or "sidebar" in b.column_id]
    main_blocks = [b for b in analyzed.blocks if "main" in b.column_id]
    assert len(sb_blocks) > 0
    assert len(main_blocks) > 0

    # Reading order places sidebar blocks first
    assert sb_blocks[0].reading_order < main_blocks[-1].reading_order
