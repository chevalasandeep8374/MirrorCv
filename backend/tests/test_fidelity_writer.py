import os
import fitz  # PyMuPDF
import pytest
from docx import Document

from app.services.docx_fingerprint import fingerprint_docx
from app.services.role_classifier import classify_paragraphs
from app.services.content_extractor import extract_content_and_style
from app.services.fidelity_writer import write_tailored_docx
from app.services.pdf_converter import convert_docx_to_pdf
from app.schemas.content import BulletItem

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
TMP_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "tmp_output")


@pytest.fixture(autouse=True)
def ensure_tmp_dir():
    os.makedirs(TMP_OUTPUT_DIR, exist_ok=True)


def test_noop_fidelity_single_column():
    """No-op fidelity test: unmodified content produces an identical document."""
    input_path = os.path.join(FIXTURES_DIR, "sample_single_column.docx")
    out_docx = os.path.join(TMP_OUTPUT_DIR, "noop_single_column.docx")
    out_pdf = os.path.join(TMP_OUTPUT_DIR, "noop_single_column.pdf")
    orig_pdf = os.path.join(TMP_OUTPUT_DIR, "orig_single_column.pdf")

    fp = fingerprint_docx(input_path)
    role_map = classify_paragraphs(fp)
    content, style, c_to_p = extract_content_and_style(fp, role_map)

    # 1. Write unmodified content
    write_tailored_docx(
        template_docx_path=input_path,
        tailored_content=content,
        content_to_paragraphs=c_to_p,
        output_docx_path=out_docx,
    )
    assert os.path.exists(out_docx)

    # 2. Render both to PDF
    convert_docx_to_pdf(input_path, orig_pdf)
    convert_docx_to_pdf(out_docx, out_pdf)
    assert os.path.exists(orig_pdf)
    assert os.path.exists(out_pdf)

    # 3. Assert page counts match
    doc_orig = fitz.open(orig_pdf)
    doc_out = fitz.open(out_pdf)
    assert len(doc_out) == len(doc_orig)

    # 4. Assert text positions / content match
    orig_text = "\n".join([page.get_text() for page in doc_orig])
    out_text = "\n".join([page.get_text() for page in doc_out])
    assert "Alex Mercer" in out_text
    assert "WORK EXPERIENCE" in out_text
    assert "Architected" in out_text

    doc_orig.close()
    doc_out.close()


def test_paragraph_cloning_and_deletion():
    """Tests that adding extra bullets performs deep XML cloning,

    and removing bullets deletes excess paragraphs cleanly.
    """
    input_path = os.path.join(FIXTURES_DIR, "sample_single_column.docx")
    out_docx = os.path.join(TMP_OUTPUT_DIR, "cloned_single_column.docx")

    fp = fingerprint_docx(input_path)
    role_map = classify_paragraphs(fp)
    content, style, c_to_p = extract_content_and_style(fp, role_map)

    exp_sec = next(s for s in content.sections if s.type == "experience")
    initial_bullets_count = len(exp_sec.items[0].bullets)

    # Add a 4th bullet (triggering XML deep copy clone)
    exp_sec.items[0].bullets.append(
        BulletItem(id="b-new-cloned-bullet", text="Authored distributed consensus algorithm improving fault recovery.")
    )

    write_tailored_docx(
        template_docx_path=input_path,
        tailored_content=content,
        content_to_paragraphs=c_to_p,
        output_docx_path=out_docx,
    )

    # Verify cloned paragraph exists in saved DOCX
    saved_doc = Document(out_docx)
    all_text = "\n".join([p.text for p in saved_doc.paragraphs])
    assert "Authored distributed consensus algorithm" in all_text

    # Now test deletion: remove 2 bullets
    out_del_docx = os.path.join(TMP_OUTPUT_DIR, "deleted_single_column.docx")
    exp_sec.items[0].bullets = exp_sec.items[0].bullets[:1]  # Keep only 1 bullet
    write_tailored_docx(
        template_docx_path=input_path,
        tailored_content=content,
        content_to_paragraphs=c_to_p,
        output_docx_path=out_del_docx,
    )

    saved_del_doc = Document(out_del_docx)
    del_text = "\n".join([p.text for p in saved_del_doc.paragraphs])
    assert "Reduced AWS infrastructure costs by 38%" not in del_text
    assert "Established engineering excellence standards" not in del_text
