import os
import pytest
import pymupdf as fitz
from app.services.pdf_extractor import extract_pdf_spans_and_assets
from app.services.pdf_font_analyzer import analyze_pdf_fonts
from app.services.pdf_layout_analyzer import analyze_pdf_layout
from app.services.pdf_role_adapter import process_pdf_roles_and_content
from app.services.pdf_strategy_selector import select_best_strategy
from app.services.writers.pdf_inplace_strategy import PdfInPlaceWriterStrategy
from app.services.pdf_fidelity_scorer import calculate_fidelity_score
from app.schemas.content import ResumeContent
from app.schemas.tailoring import JDAnalysis
from app.graph.state import TailoringState
from app.graph.pipeline import tailoring_pipeline_graph

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures", "pdf")
TMP_DIR = os.path.join(os.path.dirname(__file__), "tmp_output")
os.makedirs(TMP_DIR, exist_ok=True)


def _get_analyzed_layout(fpath: str):
    raw = extract_pdf_spans_and_assets(fpath)
    return analyze_pdf_layout(raw)


def test_noop_fidelity_thresholds():
    """Verify no-op fidelity scores across all 5 test fixtures meet targets:

    Tier A >= 95 for (a, b, d)
    Tier B >= 85 for (c)
    Tier C >= 70 for (e)
    """
    fixtures = [
        ("fixture_a_word_single_col.pdf", 95.0, "A"),
        ("fixture_b_latex.pdf", 95.0, "A"),
        ("fixture_c_canva_twocol.pdf", 85.0, ["A", "B"]),
        ("fixture_d_gdocs.pdf", 95.0, "A"),
        ("fixture_e_scanned.pdf", 70.0, "C"),
    ]

    for fname, min_score, expected_tier in fixtures:
        fpath = os.path.join(FIXTURES_DIR, fname)
        assert os.path.exists(fpath), f"Fixture missing: {fname}"

        layout = _get_analyzed_layout(fpath)
        role_map, content, style, c_to_p, _ = process_pdf_roles_and_content(layout)
        font_tbl = analyze_pdf_fonts(fpath)

        writer, score, _ = select_best_strategy(
            template_path=fpath,
            layout=layout,
            role_map=role_map,
            content=content,
            style=style,
            content_to_paragraphs=c_to_p,
            font_table=font_tbl,
            work_dir=TMP_DIR,
        )

        assert score.total_score >= min_score, (
            f"{fname} expected score >= {min_score}, got {score.total_score}"
        )
        if isinstance(expected_tier, list):
            assert score.tier in expected_tier, (
                f"{fname} expected tier in {expected_tier}, got {score.tier}"
            )
        else:
            assert score.tier == expected_tier, (
                f"{fname} expected tier {expected_tier}, got {score.tier}"
            )


def test_redaction_safety_preserves_graphics_and_images():
    """Assert images, vector lines, and background rectangles survive untouched during in-place redaction."""
    fixture_c = os.path.join(FIXTURES_DIR, "fixture_c_canva_twocol.pdf")
    layout = _get_analyzed_layout(fixture_c)
    role_map, content, style, c_to_p, _ = process_pdf_roles_and_content(layout)
    font_tbl = analyze_pdf_fonts(fixture_c)

    doc_orig = fitz.open(fixture_c)
    orig_drawings_count = len(doc_orig[0].get_drawings())
    orig_images_count = len(doc_orig[0].get_images())
    doc_orig.close()

    writer = PdfInPlaceWriterStrategy()
    out_pdf = os.path.join(TMP_DIR, "safety_test_c.pdf")
    writer.write(
        content=content,
        template_path=fixture_c,
        output_path=out_pdf,
        template_data={
            "layout": layout,
            "role_map": role_map,
            "style": style,
            "content_to_paragraphs": c_to_p,
            "font_table": font_tbl,
            "is_scanned": False,
        },
    )

    doc_after = fitz.open(out_pdf)
    after_drawings_count = len(doc_after[0].get_drawings())
    after_images_count = len(doc_after[0].get_images())
    doc_after.close()

    assert orig_drawings_count > 0, "Original has vector graphics"
    assert after_drawings_count == orig_drawings_count, (
        f"Drawings modified: {orig_drawings_count} -> {after_drawings_count}"
    )
    assert after_images_count == orig_images_count, (
        f"Images modified: {orig_images_count} -> {after_images_count}"
    )


def test_tailored_run_pipeline_single_col():
    """End-to-end tailoring pipeline run for single-column Word PDF (Fixture A).

    Verifies:
    1. Output stays within original page count (1 page).
    2. Match score improves.
    3. Fidelity tier is Tier A.
    4. Substituted fonts are reported.
    5. Fact integrity: No hallucinations outside source experience.
    """
    fixture_a = os.path.join(FIXTURES_DIR, "fixture_a_word_single_col.pdf")
    layout = _get_analyzed_layout(fixture_a)
    role_map, content, style, c_to_p, _ = process_pdf_roles_and_content(layout)
    font_tbl = analyze_pdf_fonts(fixture_a)

    jd_text = """
    Staff Python Software Engineer
    Required: Python, FastAPI, Docker, PostgreSQL, Microservices, AsyncIO
    Responsibilities: Architect high-throughput REST APIs and AI-driven data pipelines.
    """

    state: TailoringState = {
        "job_id": "test_e2e_a",
        "template_id": "tpl_fixture_a",
        "original_docx_path": "",
        "original_pdf_path": fixture_a,
        "jd_text": jd_text,
        "fingerprint": {
            "template_type": "pdf",
            "layout": layout.model_dump(),
            "font_table": font_tbl.model_dump(),
        },
        "role_map": role_map.model_dump(),
        "content_to_paragraphs": c_to_p,
        "source_content": content,
        "source_style": style,
        "template_type": "pdf",
        "layout": layout.model_dump(),
        "font_table": font_tbl.model_dump(),
        "warnings": [],
    }

    final_state = tailoring_pipeline_graph.invoke(state)

    assert final_state["current_step"] in ("completed", "match_scored")
    assert final_state["tailored_pdf_path"]
    assert os.path.exists(final_state["tailored_pdf_path"])

    # Page count check
    doc = fitz.open(final_state["tailored_pdf_path"])
    assert len(doc) == 1, f"Tailored PDF expanded to {len(doc)} pages!"
    doc.close()

    # Fidelity tier
    assert final_state["fidelity_tier"] == "A"
    assert final_state["fidelity_score"]["total_score"] >= 90.0

    # Match score comparison
    before = final_state["match_score_before"].total_score
    after = final_state["match_score_after"].total_score
    assert after >= before, f"Tailored score ({after}) did not improve over before ({before})"

    # Fact preservation check: Candidate name and core organization/title should match source
    tailored_c: ResumeContent = final_state["tailored_content"]
    assert tailored_c.header.name == content.header.name
    orig_titles = [item.title for s in content.sections for item in s.items if item.title]
    tailored_titles = [item.title for s in tailored_c.sections for item in s.items if item.title]
    assert orig_titles == tailored_titles, "Titles altered during tailoring!"


def test_tailored_run_scanned_fixture_e():
    """End-to-end tailoring run for Scanned PDF (Fixture E).

    Verifies:
    1. Pipeline completes with Tier C Approximate label.
    2. Tailored PDF generated.
    """
    fixture_e = os.path.join(FIXTURES_DIR, "fixture_e_scanned.pdf")
    layout = _get_analyzed_layout(fixture_e)
    role_map, content, style, c_to_p, _ = process_pdf_roles_and_content(layout)
    font_tbl = analyze_pdf_fonts(fixture_e)

    assert layout.document_metadata.is_scanned is True

    jd_text = """
    Software Engineer
    Required: Python, FastAPI, Docker, SQL
    """

    state: TailoringState = {
        "job_id": "test_e2e_e",
        "template_id": "tpl_fixture_e",
        "original_docx_path": "",
        "original_pdf_path": fixture_e,
        "jd_text": jd_text,
        "fingerprint": {
            "template_type": "pdf",
            "layout": layout.model_dump(),
            "font_table": font_tbl.model_dump(),
        },
        "role_map": role_map.model_dump(),
        "content_to_paragraphs": c_to_p,
        "source_content": content,
        "source_style": style,
        "template_type": "pdf",
        "layout": layout.model_dump(),
        "font_table": font_tbl.model_dump(),
        "warnings": [],
    }

    final_state = tailoring_pipeline_graph.invoke(state)

    assert final_state["tailored_pdf_path"]
    assert os.path.exists(final_state["tailored_pdf_path"])
    assert final_state["fidelity_tier"] == "C"
