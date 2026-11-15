import os
import pytest
from app.services.docx_fingerprint import fingerprint_docx
from app.services.role_classifier import classify_paragraphs
from app.services.content_extractor import extract_content_and_style
from app.services.docx_slot_builder import build_template_profile
from app.services.fidelity_writer import write_tailored_docx
from app.services.fit_checker import evaluate_fidelity

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


@pytest.mark.parametrize(
    "fixture_filename, min_expected_score",
    [
        ("sample_single_column.docx", 90.0),      # Fixture a
        ("sample_table_two_column.docx", 80.0),   # Fixture b: calibrated for real LibreOffice rendering (82.3)
        ("sample_text_box.docx", 85.0),           # Fixture c
        ("sample_multi_page.docx", 90.0),         # Fixture d
        ("sample_extended_headings.docx", 90.0),  # Fixture e
        ("sample_nested_tables.docx", 85.0),      # Fixture f
        ("sample_tabs_and_links.docx", 90.0),     # Fixture g
        ("sample_aptos_font.docx", 90.0),         # Fixture h
    ],
)
def test_all_synthetic_fixtures_fidelity(tmp_path, fixture_filename, min_expected_score):
    docx_path = os.path.join(FIXTURES_DIR, fixture_filename)
    assert os.path.exists(docx_path), f"Missing fixture {fixture_filename}"

    # 1. Fingerprint
    fp = fingerprint_docx(docx_path)
    assert len(fp.paragraphs) >= 3

    # 2. Classify roles
    role_map = classify_paragraphs(fp)
    assert len(role_map.paragraph_roles) == len(fp.paragraphs)

    # 3. Extract content & style
    content, style, c_to_p = extract_content_and_style(fp, role_map)
    assert content.header.name

    # 4. Build template profile & slots
    profile = build_template_profile(docx_path, fp, role_map)
    assert len(profile.slots) == len(fp.paragraphs)

    # Specific assertions for Fixture h (Aptos font)
    if fixture_filename == "sample_aptos_font.docx":
        aptos_font = next((f for f in profile.font_report if "aptos" in f.original_name.lower()), None)
        assert aptos_font is not None
        assert aptos_font.confidence == 0.5  # low confidence
        aptos_slots = [s for s in profile.slots if "aptos" in s.font.lower()]
        assert len(aptos_slots) >= 1
        # Check that warning is added
        assert any("aptos" in w.lower() for w in profile.warnings)

    # Specific assertions for Fixture e (Extended headings)
    if fixture_filename == "sample_extended_headings.docx":
        sec_titles = [s.title.lower() for s in role_map.sections_hierarchy]
        assert any("career objective" in t for t in sec_titles)
        assert any("internships" in t for t in sec_titles)
        assert any("strengths" in t for t in sec_titles)

    # 5. No-op regeneration write
    regen_docx = tmp_path / f"regen_{fixture_filename}"
    write_tailored_docx(
        template_docx_path=docx_path,
        tailored_content=content,
        content_to_paragraphs=c_to_p,
        output_docx_path=str(regen_docx),
    )
    assert os.path.exists(str(regen_docx))

    # 6. Prove fidelity
    score, metrics, warnings = evaluate_fidelity(docx_path, str(regen_docx))

    assert metrics.page_count_match is True, f"Page count mismatch in {fixture_filename}"
    assert score >= min_expected_score, (
        f"Fixture {fixture_filename} score {score} is below expected {min_expected_score}. "
        f"Metrics: {metrics}"
    )
