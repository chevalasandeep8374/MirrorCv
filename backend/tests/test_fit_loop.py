import os
import fitz
import pytest

from app.services.docx_fingerprint import fingerprint_docx
from app.services.role_classifier import classify_paragraphs
from app.services.content_extractor import extract_content_and_style
from app.services.fit_checker import check_pdf_fit_overflow
from app.services.pdf_converter import convert_docx_to_pdf
from app.services.tailor_agent import tailor_resume_content
from app.schemas.tailoring import JDAnalysis

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
TMP_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "tmp_output")


def test_fit_check_matching_pages():
    orig_path = os.path.join(FIXTURES_DIR, "sample_single_column.docx")
    orig_pdf = os.path.join(TMP_OUTPUT_DIR, "fit_orig.pdf")
    convert_docx_to_pdf(orig_path, orig_pdf)

    fp = fingerprint_docx(orig_path)
    role_map = classify_paragraphs(fp)
    content, _, _ = extract_content_and_style(fp, role_map)

    # Identical PDF should pass fit check
    passed, orig_p, tail_p, offending, budgets = check_pdf_fit_overflow(
        original_pdf_path=orig_pdf,
        tailored_pdf_path=orig_pdf,
        tailored_content=content,
        original_content=content,
    )

    assert passed is True
    assert orig_p == tail_p
    assert len(offending) == 0


def test_fit_check_detects_overflow_and_shrinks():
    orig_path = os.path.join(FIXTURES_DIR, "sample_single_column.docx")
    orig_pdf = os.path.join(TMP_OUTPUT_DIR, "fit_orig2.pdf")
    convert_docx_to_pdf(orig_path, orig_pdf)

    fp = fingerprint_docx(orig_path)
    role_map = classify_paragraphs(fp)
    content, _, _ = extract_content_and_style(fp, role_map)

    # Create artificial 2-page PDF
    overflow_pdf_path = os.path.join(TMP_OUTPUT_DIR, "fit_overflow.pdf")
    pdf = fitz.open()
    pdf.new_page(width=595, height=842)
    pdf.new_page(width=595, height=842)  # Extra second page
    pdf.save(overflow_pdf_path)
    pdf.close()

    # Modify a bullet so it grew
    tailored_content = content.model_copy(deep=True)
    target_bullet = tailored_content.sections[1].items[0].bullets[0]
    target_bullet.text += " Expanded extra detail to trigger overflow analysis."

    passed, orig_p, tail_p, offending, stricter_budgets = check_pdf_fit_overflow(
        original_pdf_path=orig_pdf,
        tailored_pdf_path=overflow_pdf_path,
        tailored_content=tailored_content,
        original_content=content,
    )

    assert passed is False
    assert tail_p > orig_p
    assert target_bullet.id in offending
    assert target_bullet.id in stricter_budgets
    assert stricter_budgets[target_bullet.id] < len(target_bullet.text)

    # Verify tailor agent respects the stricter budget
    jd = JDAnalysis(job_title="Staff Engineer", required_skills=["Python", "FastAPI"])
    compressed = tailor_resume_content(
        source_content=content,
        jd_analysis=jd,
        stricter_budgets=stricter_budgets,
    )
    compressed_bullet = compressed.tailored_content.sections[1].items[0].bullets[0]
    assert len(compressed_bullet.text) <= stricter_budgets[target_bullet.id]
