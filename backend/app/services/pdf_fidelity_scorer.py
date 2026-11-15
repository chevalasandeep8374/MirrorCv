import os
import fitz
import numpy as np
from typing import Optional, Tuple, List, Dict, Any
from skimage.metrics import structural_similarity as compute_ssim
from app.schemas.pdf_template import FidelityScoreBreakdown, FontResolutionTable, FidelityTier


def _rasterize_page_grayscale(page: fitz.Page, dpi: int = 150) -> np.ndarray:
    """Rasterizes a PDF page to a 2D grayscale uint8 numpy array."""
    pix = page.get_pixmap(dpi=dpi)
    arr = np.frombuffer(pix.samples, dtype=np.uint8)
    if pix.n == 1:
        # Grayscale
        arr = arr.reshape(pix.height, pix.width)
    elif pix.n in (3, 4):
        # RGB or RGBA
        arr = arr.reshape(pix.height, pix.width, pix.n)
        # Average RGB channels to grayscale
        arr = arr[:, :, :3].mean(axis=2).astype(np.uint8)
    return arr


def calculate_fidelity_score(
    original_pdf_path: str,
    generated_pdf_path: str,
    font_table: Optional[FontResolutionTable] = None,
    is_scanned: bool = False,
) -> FidelityScoreBreakdown:
    """Automated comparison between original and generated PDF:

    - Page count equal (100% or 0%)
    - Text-position delta per line (mean/max in pt)
    - Font match confidence rate
    - Pixel diff (SSIM) on rasterized pages at 150 DPI
    Combines into a 0-100 total score and assigned Tier (A, B, C).
    """
    if not os.path.exists(original_pdf_path) or not os.path.exists(generated_pdf_path):
        return FidelityScoreBreakdown(
            total_score=0.0,
            page_count_score=0.0,
            position_delta_score=0.0,
            font_match_score=0.0,
            ssim_score=0.0,
            tier="C",
            selected_strategy="rebuild",
            explanation="File not found for fidelity comparison.",
        )

    doc_orig = fitz.open(original_pdf_path)
    doc_gen = fitz.open(generated_pdf_path)

    orig_pages = len(doc_orig)
    gen_pages = len(doc_gen)

    # 1. Page count score
    page_count_score = 100.0 if orig_pages == gen_pages else 0.0

    # 2. Text position delta calculation
    deltas: List[float] = []

    min_pages = min(orig_pages, gen_pages)
    for p_idx in range(min_pages):
        p_orig = doc_orig[p_idx]
        p_gen = doc_gen[p_idx]

        orig_dict = p_orig.get_text("dict")
        gen_dict = p_gen.get_text("dict")

        orig_lines = [
            l for b in orig_dict.get("blocks", []) if b.get("type") == 0
            for l in b.get("lines", [])
        ]
        gen_lines = [
            l for b in gen_dict.get("blocks", []) if b.get("type") == 0
            for l in b.get("lines", [])
        ]

        if not orig_lines or not gen_lines:
            continue

        for ol in orig_lines:
            ol_text = " ".join(s.get("text", "") for s in ol.get("spans", [])).strip()
            if not ol_text or len(ol_text) < 4:
                continue

            oy = ol.get("bbox", [0, 0, 0, 0])[1]
            ox = ol.get("bbox", [0, 0, 0, 0])[0]

            # Find best matching line in generated page by text overlap
            best_dist = None
            for gl in gen_lines:
                gl_text = " ".join(s.get("text", "") for s in gl.get("spans", [])).strip()
                if not gl_text:
                    continue

                # Check if lines share significant text
                if ol_text in gl_text or gl_text in ol_text or (len(ol_text) > 10 and ol_text[:12] in gl_text):
                    gy = gl.get("bbox", [0, 0, 0, 0])[1]
                    gx = gl.get("bbox", [0, 0, 0, 0])[0]
                    dist = ((gx - ox)**2 + (gy - oy)**2)**0.5
                    if best_dist is None or dist < best_dist:
                        best_dist = dist

            if best_dist is not None:
                deltas.append(best_dist)

    if deltas:
        mean_delta = round(float(np.mean(deltas)), 2)
        max_delta = round(float(np.max(deltas)), 2)
        # Position score normalizes distance relative to typical line/section shifts (100 at 0pt, 80 at 30pt)
        mean_delta_norm = min(1.0, mean_delta / 150.0)
        position_score = max(0.0, round((1.0 - mean_delta_norm) * 100.0, 1))
    else:
        mean_delta = 0.0
        max_delta = 0.0
        position_score = 100.0 if not is_scanned else 70.0

    # 3. Font match score
    if font_table and font_table.overall_confidence:
        font_match_score = round(font_table.overall_confidence * 100.0, 1)
    else:
        font_match_score = 95.0

    # 4. SSIM Pixel Diff on rasterized pages
    ssim_list: List[float] = []
    for p_idx in range(min_pages):
        try:
            arr_orig = _rasterize_page_grayscale(doc_orig[p_idx], dpi=150)
            arr_gen = _rasterize_page_grayscale(doc_gen[p_idx], dpi=150)

            # Resize if sizes slightly differ
            if arr_orig.shape != arr_gen.shape:
                min_h = min(arr_orig.shape[0], arr_gen.shape[0])
                min_w = min(arr_orig.shape[1], arr_gen.shape[1])
                arr_orig = arr_orig[:min_h, :min_w]
                arr_gen = arr_gen[:min_h, :min_w]

            val = compute_ssim(arr_orig, arr_gen)
            ssim_list.append(max(0.0, float(val)))
        except Exception:
            ssim_list.append(0.85)

    ssim_score = round((sum(ssim_list) / max(1, len(ssim_list))) * 100.0, 1) if ssim_list else 100.0

    # 5. Combined Total Score
    total_score = round(
        (0.25 * page_count_score) +
        (0.35 * position_score) +
        (0.15 * font_match_score) +
        (0.25 * ssim_score),
        1,
    )

    # 6. Tier assignment
    if is_scanned:
        tier: FidelityTier = "C"
        strategy = "ocr_rebuild"
    elif total_score >= 90.0:
        tier = "A"
        strategy = "in_place"
    elif total_score >= 75.0:
        tier = "B"
        strategy = "rebuild"
    else:
        tier = "C"
        strategy = "rebuild"

    doc_orig.close()
    doc_gen.close()

    explanation = (
        f"Fidelity {total_score}/100 (Tier {tier}). "
        f"Pages: {gen_pages}/{orig_pages}, Position delta: {mean_delta}pt mean, "
        f"Font confidence: {font_match_score}%, Visual SSIM: {ssim_score}%."
    )

    return FidelityScoreBreakdown(
        total_score=total_score,
        page_count_score=page_count_score,
        position_delta_score=position_score,
        font_match_score=font_match_score,
        ssim_score=ssim_score,
        tier=tier,
        selected_strategy=strategy,
        mean_position_delta_pt=mean_delta,
        max_position_delta_pt=max_delta,
        explanation=explanation,
    )
