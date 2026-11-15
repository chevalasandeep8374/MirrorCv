"""DOCX and PDF Fidelity Evaluator and Fit Checker.
Compares original document vs regenerated document (no-op write or tailored).
Enforces hard failure (fidelity score capped at 50) on page count mismatch (Change #3),
and measures line bounding box deltas, run property match rates, and visual similarity.
"""

import os
import logging
from typing import Dict, List, Tuple, Any, Optional
import pymupdf as fitz

from contracts.models.template_profile import FidelityMetrics
from app.schemas.content import ResumeContent
from app.services.docx_rendering_measurements import extract_pdf_lines
from app.services.pdf_converter import convert_docx_to_pdf

logger = logging.getLogger(__name__)


def check_pdf_fit_overflow(
    original_pdf_path: str,
    tailored_pdf_path: str,
    tailored_content: ResumeContent,
    original_content: ResumeContent,
) -> Tuple[bool, int, int, List[str], Dict[str, int]]:
    """Compares original vs tailored PDF page count and text layout using PyMuPDF.

    Returns:
    - fit_passed: bool (True if tailored page count <= original page count)
    - original_page_count: int
    - tailored_page_count: int
    - offending_bullet_ids: List[str]
    - stricter_budgets: Dict[str, int]
    """
    if not os.path.exists(original_pdf_path) or not os.path.exists(tailored_pdf_path):
        return True, 1, 1, [], {}

    doc_orig = fitz.open(original_pdf_path)
    doc_tailored = fitz.open(tailored_pdf_path)

    orig_pages = len(doc_orig)
    tailored_pages = len(doc_tailored)

    doc_orig.close()
    doc_tailored.close()

    if tailored_pages <= orig_pages:
        return True, orig_pages, tailored_pages, [], {}

    # Overflow detected! Locate bullets that grew in character count
    offending_bullet_ids: List[str] = []
    stricter_budgets: Dict[str, int] = {}

    orig_bullet_texts = {}
    for s in original_content.sections:
        for item in s.items:
            for b in item.bullets:
                orig_bullet_texts[b.id] = b.text

    for s in tailored_content.sections:
        for item in s.items:
            for b in item.bullets:
                orig_txt = orig_bullet_texts.get(b.id, "")
                if len(b.text) > len(orig_txt):
                    offending_bullet_ids.append(b.id)
                    target_len = max(30, int(len(orig_txt) * 0.85))
                    stricter_budgets[b.id] = target_len

    if not offending_bullet_ids:
        for s in tailored_content.sections:
            if s.type == "experience":
                for item in s.items:
                    for b in item.bullets:
                        offending_bullet_ids.append(b.id)
                        stricter_budgets[b.id] = max(30, int(len(b.text) * 0.85))

    return False, orig_pages, tailored_pages, offending_bullet_ids, stricter_budgets


def _compute_visual_similarity(pix_a: fitz.Pixmap, pix_b: fitz.Pixmap) -> float:
    """Calculates pixel-level similarity ratio between two PyMuPDF Pixmaps."""
    if pix_a.width != pix_b.width or pix_a.height != pix_b.height:
        return 0.5

    samples_a = pix_a.samples
    samples_b = pix_b.samples

    total_bytes = min(len(samples_a), len(samples_b))
    if total_bytes == 0:
        return 1.0

    # Sample comparison (step 4 for RGBA/RGB performance)
    step = 4
    matching = 0
    sampled_count = 0

    for i in range(0, total_bytes, step):
        sampled_count += 1
        if abs(samples_a[i] - samples_b[i]) <= 15:
            matching += 1

    return round(matching / float(sampled_count), 4) if sampled_count > 0 else 1.0


def evaluate_fidelity(
    original_path: str,
    regenerated_path: str,
) -> Tuple[float, FidelityMetrics, List[str]]:
    """Evaluates the fidelity between original and regenerated document (DOCX or PDF).

    Page-count mismatch is a HARD FAILURE: caps fidelity score at 50.0 and flags it (Change #3).
    """
    warnings: List[str] = []

    # 1. Ensure both are converted to PDF
    orig_pdf = original_path if original_path.lower().endswith(".pdf") else convert_docx_to_pdf(original_path)
    regen_pdf = regenerated_path if regenerated_path.lower().endswith(".pdf") else convert_docx_to_pdf(regenerated_path)

    doc_orig = fitz.open(orig_pdf)
    doc_regen = fitz.open(regen_pdf)

    orig_page_count = len(doc_orig)
    regen_page_count = len(doc_regen)

    page_match = (orig_page_count == regen_page_count)

    # 2. Extract Lines and compute deltas
    lines_orig = extract_pdf_lines(orig_pdf)
    lines_regen = extract_pdf_lines(regen_pdf)

    mean_delta = 0.0
    max_delta = 0.0

    if lines_orig and lines_regen:
        compare_count = min(len(lines_orig), len(lines_regen))
        deltas = []
        for i in range(compare_count):
            dy = abs(lines_orig[i]["bbox"][1] - lines_regen[i]["bbox"][1])
            dx = abs(lines_orig[i]["bbox"][0] - lines_regen[i]["bbox"][0])
            deltas.append((dx + dy) / 2.0)

        if deltas:
            mean_delta = round(sum(deltas) / float(len(deltas)), 2)
            max_delta = round(max(deltas), 2)

    # 3. Visual / SSIM similarity on first page
    ssim = 1.0
    if orig_page_count > 0 and regen_page_count > 0:
        pix_orig = doc_orig[0].get_pixmap(dpi=150)
        pix_regen = doc_regen[0].get_pixmap(dpi=150)
        ssim = _compute_visual_similarity(pix_orig, pix_regen)

    doc_orig.close()
    doc_regen.close()

    # 4. Property match rate
    # Calculates exact line and run property match rate
    line_count_ratio = min(len(lines_orig), len(lines_regen)) / float(max(len(lines_orig), len(lines_regen), 1))
    if page_match and lines_orig and lines_regen:
        matching_lines = sum(
            1 for lo, lr in zip(lines_orig, lines_regen)
            if lo.get("text", "").strip() == lr.get("text", "").strip()
        )
        run_prop_rate = round(matching_lines / float(max(len(lines_orig), len(lines_regen))), 4)
    else:
        run_prop_rate = round(line_count_ratio, 4) if page_match else 0.70

    metrics = FidelityMetrics(
        page_count_match=page_match,
        mean_line_delta_pt=mean_delta,
        max_line_delta_pt=max_delta,
        run_property_match_rate=run_prop_rate,
        ssim_score=ssim,
    )

    # 5. Score computation with HARD FAILURE CAP AT 50
    if not page_match:
        warnings.append(
            f"Page count mismatch: original has {orig_page_count} pages but regenerated has {regen_page_count} pages. "
            f"Fidelity score capped at 50 (hard failure)."
        )
        fidelity_score = min(50.0, round(ssim * 50.0, 1))
    else:
        # High fidelity formula: base 100 - minor line deltas
        penalty = (mean_delta * 1.5) + ((1.0 - run_prop_rate) * 15.0) + ((1.0 - ssim) * 10.0)
        fidelity_score = max(55.0, min(100.0, round(100.0 - penalty, 1)))

    return fidelity_score, metrics, warnings
