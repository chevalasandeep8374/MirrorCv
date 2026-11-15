import os
import re
import fitz
from typing import Dict, List, Tuple, Optional, Any
from app.schemas.pdf_template import (
    PdfLayout,
    FontResolutionEntry,
    FontResolutionTable,
    FontSubstitution,
)

# Open / Metric-compatible font substitutions
METRIC_COMPATIBLE_MAP: Dict[str, Dict[str, Any]] = {
    "calibri": {
        "replacement": "Carlito",
        "family": "Carlito",
        "confidence": 0.96,
        "base14": "helv",
        "notes": "Metric-compatible open font Carlito matches Calibri character widths exactly.",
    },
    "arial": {
        "replacement": "Liberation Sans",
        "family": "Liberation Sans",
        "confidence": 0.98,
        "base14": "helv",
        "notes": "Liberation Sans is metric-compatible with Arial.",
    },
    "helvetica": {
        "replacement": "Liberation Sans",
        "family": "Helvetica",
        "confidence": 0.99,
        "base14": "helv",
        "notes": "Standard Helvetica Base-14 font.",
    },
    "helv": {
        "replacement": "Helvetica",
        "family": "Helvetica",
        "confidence": 1.0,
        "base14": "helv",
        "notes": "Native PDF Base-14 Helvetica.",
    },
    "times": {
        "replacement": "Liberation Serif",
        "family": "Times-Roman",
        "confidence": 0.98,
        "base14": "times-roman",
        "notes": "Liberation Serif / Times-Roman is metric-compatible with Times New Roman.",
    },
    "times new roman": {
        "replacement": "Liberation Serif",
        "family": "Times-Roman",
        "confidence": 0.98,
        "base14": "times-roman",
        "notes": "Liberation Serif matches Times New Roman glyph metrics.",
    },
    "cambria": {
        "replacement": "Caladea",
        "family": "Caladea",
        "confidence": 0.95,
        "base14": "times-roman",
        "notes": "Caladea is metric-compatible with Cambria.",
    },
    "georgia": {
        "replacement": "Noto Serif",
        "family": "Georgia",
        "confidence": 0.88,
        "base14": "times-roman",
        "notes": "Noto Serif provides close serif proportion match for Georgia.",
    },
    "courier": {
        "replacement": "Liberation Mono",
        "family": "Courier",
        "confidence": 1.0,
        "base14": "courier",
        "notes": "Standard Monospace Base-14 Courier.",
    },
    "courier new": {
        "replacement": "Liberation Mono",
        "family": "Courier",
        "confidence": 0.99,
        "base14": "courier",
        "notes": "Liberation Mono is metric-compatible with Courier New.",
    },
}

SUBSET_REGEX = re.compile(r"^[A-Z]{6}\+(.+)$")


def parse_font_name(raw_name: str) -> Tuple[str, bool, bool, bool]:
    """Parses a PDF font name to extract clean name, subset flag, bold, and italic."""
    clean = raw_name
    is_subset = False

    # Check for subset prefix e.g. "ABCDEF+Calibri-Bold"
    m = SUBSET_REGEX.match(clean)
    if m:
        is_subset = True
        clean = m.group(1)

    lower = clean.lower()
    is_bold = bool("bold" in lower or "bd" in lower or "black" in lower or "heavy" in lower)
    is_italic = bool("italic" in lower or "it" in lower or "oblique" in lower)

    # Clean family name by removing weight suffix
    family = re.split(r"[,\-_]", clean)[0].strip()
    return family, is_subset, is_bold, is_italic


def resolve_font(
    font_name: str,
    is_embedded: bool = False,
    user_fonts_dir: Optional[str] = None,
) -> FontResolutionEntry:
    """Resolves an original PDF font to an open, usable font for new text insertion.

    Never reuses embedded subset fonts for new text.
    """
    family, is_subset, is_bold, is_italic = parse_font_name(font_name)
    fam_lower = family.lower()

    # 1. Check if user provided an uploaded font file matching this family
    if user_fonts_dir and os.path.exists(user_fonts_dir):
        for f in os.listdir(user_fonts_dir):
            if f.lower().endswith((".ttf", ".otf")) and fam_lower in f.lower():
                user_path = os.path.join(user_fonts_dir, f)
                return FontResolutionEntry(
                    original_font_name=font_name,
                    clean_family=family,
                    is_embedded=is_embedded,
                    is_subset=is_subset,
                    style_flags={"bold": is_bold, "italic": is_italic},
                    resolved_font_name=f.rsplit(".", 1)[0],
                    resolved_font_path=user_path,
                    source="user_uploaded",
                    match_confidence=1.0,
                    glyph_width_scale=1.0,
                    notes=f"Using exact user-uploaded font file '{f}'.",
                )

    # 2. Check metric-compatible table
    for key, info in METRIC_COMPATIBLE_MAP.items():
        if key in fam_lower:
            resolved_name = info["replacement"]
            if is_bold and is_italic:
                resolved_name += "-BoldItalic"
            elif is_bold:
                resolved_name += "-Bold"
            elif is_italic:
                resolved_name += "-Italic"

            return FontResolutionEntry(
                original_font_name=font_name,
                clean_family=family,
                is_embedded=is_embedded,
                is_subset=is_subset,
                style_flags={"bold": is_bold, "italic": is_italic},
                resolved_font_name=resolved_name,
                resolved_font_path=None,
                source="metric_compatible",
                match_confidence=info["confidence"],
                glyph_width_scale=1.0,
                notes=info["notes"],
            )

    # 3. Default system fallback based on serif/sans heuristic
    is_serif = any(term in fam_lower for term in ["serif", "times", "roman", "georgia", "cambria", "garamond"])
    is_mono = any(term in fam_lower for term in ["mono", "courier", "console", "code"])

    if is_mono:
        fallback_name = "Courier"
        conf = 0.90
    elif is_serif:
        fallback_name = "Times-Roman"
        conf = 0.82
    else:
        fallback_name = "Helvetica"
        conf = 0.85

    if is_bold:
        fallback_name += "-Bold"

    return FontResolutionEntry(
        original_font_name=font_name,
        clean_family=family,
        is_embedded=is_embedded,
        is_subset=is_subset,
        style_flags={"bold": is_bold, "italic": is_italic},
        resolved_font_name=fallback_name,
        resolved_font_path=None,
        source="system_fallback",
        match_confidence=conf,
        glyph_width_scale=1.0,
        notes=f"Original font '{font_name}' substituted with standard '{fallback_name}'.",
    )


def analyze_pdf_fonts(
    pdf_path: str,
    layout: Optional[PdfLayout] = None,
    user_fonts_dir: Optional[str] = None,
) -> FontResolutionTable:
    """Inspects all fonts in the PDF and generates the complete FontResolutionTable

    including subset status, metric-compatible alternatives, and match confidence.
    """
    doc = fitz.open(pdf_path)
    embedded_font_names: Dict[str, bool] = {}

    for page in doc:
        for f_tuple in page.get_fonts():
            # tuple format: (xref, ext, type, basefont, name, encoding)
            basefont = f_tuple[3] if len(f_tuple) > 3 else ""
            if basefont:
                embedded_font_names[basefont] = bool(f_tuple[1])

    # Also collect all font names found in spans
    span_font_names = set()
    if layout:
        for b in layout.blocks:
            for l in b.lines:
                for s in l.spans:
                    if s.font_name:
                        span_font_names.add(s.font_name)

    all_fonts = set(list(embedded_font_names.keys()) + list(span_font_names))
    if not all_fonts:
        all_fonts.add("Helvetica")

    entries: List[FontResolutionEntry] = []
    substitutions: List[FontSubstitution] = []
    conf_scores: List[float] = []

    for fn in sorted(all_fonts):
        is_embedded = embedded_font_names.get(fn, False)
        entry = resolve_font(fn, is_embedded=is_embedded, user_fonts_dir=user_fonts_dir)
        entries.append(entry)
        conf_scores.append(entry.match_confidence)

        if entry.source in ("metric_compatible", "system_fallback"):
            substitutions.append(FontSubstitution(
                original=entry.original_font_name,
                replacement=entry.resolved_font_name,
                confidence=entry.match_confidence,
                notes=entry.notes,
            ))

    overall_conf = round(sum(conf_scores) / max(1, len(conf_scores)), 3)
    all_matched_well = overall_conf >= 0.85

    doc.close()
    return FontResolutionTable(
        fonts=entries,
        all_matched_well=all_matched_well,
        overall_confidence=overall_conf,
        substitutions=substitutions,
    )


def measure_text_width_pt(
    text: str,
    font_name: str = "helv",
    font_size_pt: float = 10.0,
) -> float:
    """Accurately calculates the advance width in points for text in a given font and size

    using PyMuPDF's font metric engine.
    """
    try:
        f = fitz.Font(fontname=font_name)
        width = f.text_length(text, fontsize=font_size_pt)
        return round(width, 2)
    except Exception:
        # Fallback approximation: 0.52 em per character for sans, 0.48 for serif
        return round(len(text) * font_size_pt * 0.52, 2)
