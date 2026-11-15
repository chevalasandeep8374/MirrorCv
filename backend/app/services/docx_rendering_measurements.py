"""DOCX Rendering Measurements and Character Budgets.
Computes frequency-weighted per-paragraph font advances, line wrapping simulation,
and character/line budgets adhering to strict margins (0.97 shrink for standard fonts,
0.92 for low-confidence fonts like Aptos).
"""

import os
import re
import glob
import logging
from typing import Dict, Any, List, Optional, Tuple, Union
import pymupdf as fitz

from app.schemas.template import (
    ParagraphFingerprint,
    BudgetInfo,
)

logger = logging.getLogger(__name__)

# Metric-compatible font substitutions
METRIC_SUBSTITUTES = {
    "calibri": "Carlito",
    "cambria": "Caladea",
    "arial": "Liberation Sans",
    "times new roman": "Liberation Serif",
    "courier new": "Liberation Mono",
    "helvetica": "Liberation Sans",
}

# Fonts with no metric-compatible substitute that require low confidence and 8% margin (0.92)
LOW_CONFIDENCE_FONTS = {
    "aptos",
    "aptos display",
    "aptos narrow",
}

# Standard English fallback text for short or empty paragraphs to compute frequency-weighted advance
FALLBACK_PROSE = "The quick brown fox jumps over the lazy dog. In addition, experience and education 1234567890."

# Cache for fitz.Font objects
_FONT_CACHE: Dict[Tuple[str, bool, bool], fitz.Font] = {}


def _find_system_font_file(family: str, is_bold: bool, is_italic: bool) -> Optional[str]:
    """Search common Windows and Linux font directories for a matching TTF/OTF font file."""
    search_dirs = [
        "C:\\Windows\\Fonts",
        "/usr/share/fonts",
        "/usr/local/share/fonts",
        os.path.expanduser("~/.fonts"),
        os.path.expanduser("~/.local/share/fonts"),
    ]

    clean_family = family.lower().replace(" ", "").replace("-", "")

    for s_dir in search_dirs:
        if not os.path.exists(s_dir):
            continue
        try:
            for root, _, files in os.walk(s_dir):
                for f in files:
                    f_lower = f.lower()
                    if not (f_lower.endswith(".ttf") or f_lower.endswith(".otf")):
                        continue

                    # Simple name matching heuristic
                    f_name = f_lower.replace(" ", "").replace("-", "").replace("_", "")
                    if clean_family in f_name:
                        # Check bold / italic matches if requested
                        if is_bold and is_italic:
                            if any(k in f_name for k in ["bi", "bolditalic", "z"]):
                                return os.path.join(root, f)
                        elif is_bold:
                            if any(k in f_name for k in ["b", "bold", "bd"]) and not any(k in f_name for k in ["i", "italic"]):
                                return os.path.join(root, f)
                        elif is_italic:
                            if any(k in f_name for k in ["i", "italic", "it"]) and not any(k in f_name for k in ["b", "bold"]):
                                return os.path.join(root, f)
                        else:
                            if any(k in f_name for k in ["regular", "r"]) or (clean_family in f_name and not any(k in f_name for k in ["bold", "italic", "b", "i"])):
                                return os.path.join(root, f)
        except Exception:
            continue

    return None


def get_font_instance(font_family: str, is_bold: bool = False, is_italic: bool = False) -> fitz.Font:
    """Gets or creates a fitz.Font instance, falling back to base 14 fonts if needed."""
    cache_key = (font_family.lower().strip(), bool(is_bold), bool(is_italic))
    if cache_key in _FONT_CACHE:
        return _FONT_CACHE[cache_key]

    fam = font_family.lower().strip()

    # 1. Try to find actual TTF file on system
    font_file = _find_system_font_file(fam, is_bold, is_italic)
    if font_file:
        try:
            font = fitz.Font(fontfile=font_file)
            _FONT_CACHE[cache_key] = font
            return font
        except Exception as e:
            logger.debug(f"Failed loading font file {font_file}: {e}")

    # 2. Base 14 built-in font fallback
    base_name = "helv"
    if "times" in fam or "roman" in fam or "serif" in fam or "cambria" in fam:
        base_name = "times"
    elif "courier" in fam or "mono" in fam or "consolas" in fam:
        base_name = "couri"

    if is_bold and is_italic:
        code = f"{base_name}bi" if base_name != "couri" else "cobi"
    elif is_bold:
        code = f"{base_name}b" if base_name != "couri" else "cobo"
    elif is_italic:
        code = f"{base_name}i" if base_name != "couri" else "coi"
    else:
        code = base_name

    try:
        font = fitz.Font(code)
    except Exception:
        font = fitz.Font("helv")

    _FONT_CACHE[cache_key] = font
    return font


def evaluate_font_confidence(font_family: str) -> Dict[str, Any]:
    """Evaluates font confidence, metric compatibility, and budget margin (0.97 vs 0.92)."""
    clean_fam = font_family.lower().strip()

    # Check if exact font is found on disk
    is_installed = _find_system_font_file(clean_fam, False, False) is not None

    if clean_fam in LOW_CONFIDENCE_FONTS:
        return {
            "family": font_family,
            "installed": is_installed,
            "substitute": None,
            "confidence": "low_confidence",
            "budget_margin": 0.92,  # 8% shrink margin for Aptos / unknown
            "notes": "No metric-compatible substitute available (e.g. Aptos). Using 8% budget margin.",
        }

    substitute = METRIC_SUBSTITUTES.get(clean_fam)
    if is_installed:
        confidence = "exact"
    elif substitute is not None:
        confidence = "metric_compatible"
    else:
        # Check if it's a known open source font
        known_oss = ["roboto", "open sans", "lato", "source sans pro", "montserrat", "raleway"]
        if any(k in clean_fam for k in known_oss):
            confidence = "exact" if is_installed else "metric_compatible"
            substitute = font_family
        else:
            confidence = "low_confidence"

    margin = 0.92 if confidence == "low_confidence" else 0.97

    return {
        "family": font_family,
        "installed": is_installed,
        "substitute": substitute,
        "confidence": confidence,
        "budget_margin": margin,
        "notes": f"Font resolved with confidence: {confidence}",
    }


def calculate_frequency_weighted_advance(
    text: str,
    font_family: str = "Calibri",
    font_size_pt: float = 11.0,
    is_bold: bool = False,
    is_italic: bool = False,
) -> float:
    """Computes the frequency-weighted average advance in points per character for the paragraph.

    Uses the paragraph's actual characters if >= 5 chars, otherwise standard English prose.
    """
    cleaned = text.strip()
    sample_text = cleaned if len(cleaned) >= 5 else FALLBACK_PROSE

    font = get_font_instance(font_family, is_bold, is_italic)

    try:
        total_length_pt = font.text_length(sample_text, fontsize=font_size_pt)
        w_avg = total_length_pt / float(len(sample_text))
        return max(3.0, round(w_avg, 3))
    except Exception:
        # Fallback approximation: 1 pt of font size ~= 0.5 pt width for average glyph
        return max(3.0, round(font_size_pt * 0.52, 3))


def measure_lines(text: str, slot_or_params: Any) -> int:
    """Word-wrap simulator using real font advances for Agent 2, the fit loop, and editor resumes.

    Accepts text (with markdown bold/italic/links) and either a slot object/dict or parameters
    with line_width_pt, font_family, font_size_pt.
    Accounts for bold font advances on bold runs and link labels.
    Returns the simulated line count.
    """
    if not text or not text.strip():
        return 1

    # Extract geometry and formatting parameters
    line_width_pt = 515.0
    font_family = "Calibri"
    font_size_pt = 11.0
    slot_is_bold = False
    slot_is_italic = False

    if isinstance(slot_or_params, dict):
        line_width_pt = slot_or_params.get("line_width_pt") or slot_or_params.get("width_pt")
        budgets = slot_or_params.get("budgets")
        if not line_width_pt and isinstance(budgets, dict):
            line_width_pt = budgets.get("line_width_pt")
        line_width_pt = line_width_pt or 515.0
        fmt = slot_or_params.get("resolved_formatting") or slot_or_params.get("formatting") or slot_or_params
        font_family = fmt.get("font_family") or slot_or_params.get("font") or font_family
        font_size_pt = fmt.get("font_size_pt") or slot_or_params.get("size") or font_size_pt
        slot_is_bold = fmt.get("bold") or False
        slot_is_italic = fmt.get("italic") or False
    else:
        if hasattr(slot_or_params, "budgets") and getattr(slot_or_params, "budgets"):
            b = getattr(slot_or_params, "budgets")
            if getattr(b, "line_width_pt", None):
                line_width_pt = b.line_width_pt
        elif hasattr(slot_or_params, "line_width_pt") and getattr(slot_or_params, "line_width_pt"):
            line_width_pt = getattr(slot_or_params, "line_width_pt")

        if hasattr(slot_or_params, "font") and getattr(slot_or_params, "font"):
            font_family = getattr(slot_or_params, "font")
        if hasattr(slot_or_params, "size") and getattr(slot_or_params, "size"):
            font_size_pt = getattr(slot_or_params, "size")

        fmt = getattr(slot_or_params, "resolved_formatting", None) or getattr(slot_or_params, "formatting", None)
        if fmt:
            font_family = getattr(fmt, "font_family", font_family)
            font_size_pt = getattr(fmt, "font_size_pt", font_size_pt)
            slot_is_bold = getattr(fmt, "bold", False)
            slot_is_italic = getattr(fmt, "italic", False)

        rs = getattr(slot_or_params, "run_structure", None)
        if rs and getattr(rs, "normal_rPr", None):
            nr = rs.normal_rPr
            if getattr(nr, "font_family", None):
                font_family = nr.font_family
            if getattr(nr, "font_size_pt", None):
                font_size_pt = nr.font_size_pt
            if getattr(nr, "bold", None) is not None:
                slot_is_bold = bool(nr.bold)
            if getattr(nr, "italic", None) is not None:
                slot_is_italic = bool(nr.italic)

    regular_font = get_font_instance(font_family, slot_is_bold, slot_is_italic)
    bold_font = get_font_instance(font_family, True, slot_is_italic)
    space_width = regular_font.text_length(" ", fontsize=font_size_pt)

    total_lines = 0

    # Split by explicit hard newlines
    paragraphs = text.split("\n")
    for para in paragraphs:
        # Pre-process markdown links [label](url) -> label
        clean_para = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", para)

        tokens = clean_para.split()
        if not tokens:
            total_lines += 1
            continue

        curr_line_width = 0.0
        lines_in_para = 1

        for token in tokens:
            # Check if token is styled bold via markdown **word** or <b>word</b>
            is_token_bold = slot_is_bold
            clean_token = token
            if (token.startswith("**") and token.endswith("**")) or (token.startswith("<b>") and token.endswith("</b>")):
                clean_token = token.replace("**", "").replace("<b>", "").replace("</b>", "")
                is_token_bold = True
            elif token.startswith("**"):
                clean_token = token.replace("**", "")
                is_token_bold = True
            elif token.endswith("**"):
                clean_token = token.replace("**", "")
                is_token_bold = True

            font = bold_font if is_token_bold else regular_font
            token_width = font.text_length(clean_token, fontsize=font_size_pt)

            if curr_line_width == 0.0:
                curr_line_width = token_width
            else:
                if (curr_line_width + space_width + token_width) <= line_width_pt:
                    curr_line_width += space_width + token_width
                else:
                    lines_in_para += 1
                    curr_line_width = token_width

        total_lines += lines_in_para

    return max(1, total_lines)


def calculate_paragraph_budget(
    text: str,
    line_width_pt: float,
    font_family: str = "Calibri",
    font_size_pt: float = 11.0,
    is_bold: bool = False,
    is_italic: bool = False,
    rendered_lines: Optional[int] = None,
) -> BudgetInfo:
    """Calculates max_lines, max_chars, hard_max_chars, and last_line_fill_ratio."""
    # 1. Font status and margin
    font_status = evaluate_font_confidence(font_family)
    margin = font_status["budget_margin"]  # 0.97 or 0.92

    # 2. Frequency-weighted average advance
    w_avg = calculate_frequency_weighted_advance(
        text=text,
        font_family=font_family,
        font_size_pt=font_size_pt,
        is_bold=is_bold,
        is_italic=is_italic,
    )

    # 3. Determine rendered lines (from PDF measurement or word-wrap simulation)
    if rendered_lines is None or rendered_lines < 1:
        simulated_slot = {
            "line_width_pt": line_width_pt,
            "font_family": font_family,
            "font_size_pt": font_size_pt,
            "bold": is_bold,
            "italic": is_italic,
        }
        rendered_lines = measure_lines(text, simulated_slot)

    # 4. Characters per line capacity
    chars_per_line = line_width_pt / w_avg

    # 5. Budgets
    max_lines = rendered_lines
    max_chars = int(round(rendered_lines * chars_per_line * margin))
    hard_max_chars = int(round(rendered_lines * chars_per_line))

    # 6. Last line fill ratio
    font = get_font_instance(font_family, is_bold, is_italic)
    text_len_pt = font.text_length(text.strip(), fontsize=font_size_pt)
    if max_lines <= 1:
        last_line_fill_ratio = min(1.0, round(text_len_pt / line_width_pt, 2)) if line_width_pt > 0 else 1.0
    else:
        # Remainder width on last line
        full_lines_width = (max_lines - 1) * line_width_pt
        last_line_width = max(0.0, text_len_pt - full_lines_width)
        last_line_fill_ratio = min(1.0, round(last_line_width / line_width_pt, 2)) if line_width_pt > 0 else 0.5

    return BudgetInfo(
        max_lines=max_lines,
        max_chars=max_chars,
        hard_max_chars=hard_max_chars,
        last_line_fill_ratio=last_line_fill_ratio,
        budget_margin=margin,
    )


def extract_pdf_lines(pdf_path: str) -> List[Dict[str, Any]]:
    """Extracts rendered lines with bounding boxes from a converted PDF using PyMuPDF."""
    lines: List[Dict[str, Any]] = []
    if not os.path.exists(pdf_path):
        return lines

    doc = fitz.open(pdf_path)
    try:
        for page_idx, page in enumerate(doc):
            p_dict = page.get_text("dict")
            for block in p_dict.get("blocks", []):
                if block.get("type") != 0:  # Text block
                    continue
                for l in block.get("lines", []):
                    bbox = l.get("bbox", (0, 0, 0, 0))
                    text = "".join(s.get("text", "") for s in l.get("spans", [])).strip()
                    if text:
                        lines.append({
                            "page": page_idx + 1,
                            "bbox": bbox,
                            "width_pt": round(bbox[2] - bbox[0], 1),
                            "height_pt": round(bbox[3] - bbox[1], 1),
                            "text": text,
                        })
    finally:
        doc.close()

    return lines
