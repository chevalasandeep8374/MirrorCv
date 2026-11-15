import os
import pytest
from app.services.docx_fingerprint import fingerprint_docx
from app.services.role_classifier import classify_paragraphs
from app.services.content_extractor import extract_content_and_style
from app.services.fidelity_writer import write_tailored_docx, set_slot_text, clone_slot, remove_slot
from app.services.fit_checker import evaluate_fidelity
from docx import Document

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


def test_hard_failure_on_page_count_mismatch(tmp_path):
    """Verifies Change #3: Page-count mismatch is a hard failure capping fidelity score at 50."""
    import pymupdf as fitz

    # Create 1-page original PDF
    orig_pdf = tmp_path / "orig.pdf"
    doc_orig = fitz.open()
    doc_orig.new_page(width=595.0, height=842.0)
    doc_orig.save(str(orig_pdf))
    doc_orig.close()

    # Create 2-page regenerated PDF (page overflow!)
    regen_pdf = tmp_path / "regen_overflow.pdf"
    doc_regen = fitz.open()
    doc_regen.new_page(width=595.0, height=842.0)
    doc_regen.new_page(width=595.0, height=842.0)
    doc_regen.save(str(regen_pdf))
    doc_regen.close()

    score, metrics, warnings = evaluate_fidelity(str(orig_pdf), str(regen_pdf))

    # Assert hard failure constraints
    assert metrics.page_count_match is False
    assert score <= 50.0, f"Expected fidelity score <= 50 on page mismatch, got {score}"
    assert len(warnings) >= 1
    assert any("Page count mismatch" in w for w in warnings)
    assert any("capped at 50" in w for w in warnings)


def test_noop_regeneration_fidelity(tmp_path):
    """Proves fidelity: extracted content rewritten to original DOCX matches with high fidelity (>=95)."""
    orig_docx = os.path.join(FIXTURES_DIR, "sample_single_column.docx")
    assert os.path.exists(orig_docx)

    fp = fingerprint_docx(orig_docx)
    role_map = classify_paragraphs(fp)
    content, style, content_to_paras = extract_content_and_style(fp, role_map)

    regen_docx = tmp_path / "noop_regenerated.docx"
    write_tailored_docx(
        template_docx_path=orig_docx,
        tailored_content=content,
        content_to_paragraphs=content_to_paras,
        output_docx_path=str(regen_docx),
    )

    assert os.path.exists(str(regen_docx))

    score, metrics, warnings = evaluate_fidelity(orig_docx, str(regen_docx))

    assert metrics.page_count_match is True
    assert score >= 90.0, f"No-op fidelity score below 90: {score}"
    assert metrics.mean_line_delta_pt <= 4.0


def test_inline_markup_set_slot_text(tmp_path):
    """Tests inline markdown parsing in set_slot_text (**bold**, *italic*)."""
    doc_path = tmp_path / "markup.docx"
    doc = Document()
    p = doc.add_paragraph("Original run")
    doc.save(str(doc_path))

    # Apply inline markup
    set_slot_text(p, "**Architected** high-performance *cloud* streaming platform.")

    runs = p.runs
    assert len(runs) >= 3
    # First run: bold
    assert runs[0].text == "Architected"
    assert runs[0].bold is True

    # Cloud run: italic
    italic_run = next((r for r in runs if "cloud" in r.text), None)
    assert italic_run is not None
    assert italic_run.italic is True
