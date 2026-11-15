import os
import fitz
from typing import Tuple, Optional, List, Dict, Any
from app.schemas.pdf_template import (
    PdfLayout,
    PdfDocumentMetadata,
    PdfBlock,
    PdfLine,
    PdfSpan,
    SpanFlags,
    PdfVectorDrawing,
    PdfImage,
    PdfLink,
)


def validate_pdf(pdf_path: str) -> Tuple[bool, Optional[str], Optional[int]]:
    """Validates that a PDF exists, is uncorrupted, is not password encrypted,

    and has 3 or fewer pages. Returns (is_valid, error_message, page_count).
    """
    if not os.path.exists(pdf_path):
        return False, "File does not exist.", None

    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        return False, f"Corrupted or invalid PDF file: {str(e)}", None

    if doc.is_encrypted:
        doc.close()
        return False, "PDF is password-protected or encrypted. Please upload an unlocked PDF.", None

    page_count = len(doc)
    if page_count == 0:
        doc.close()
        return False, "PDF file contains zero pages.", 0

    if page_count > 3:
        doc.close()
        return False, f"PDF exceeds maximum page limit (found {page_count} pages, limit is 3).", page_count

    doc.close()
    return True, None, page_count


def _srgb_int_to_hex(color_int: int) -> str:
    """Converts PyMuPDF sRGB integer color to #RRGGBB string."""
    r = (color_int >> 16) & 255
    g = (color_int >> 8) & 255
    b = color_int & 255
    return f"#{r:02x}{g:02x}{b:02x}"


def _srgb_int_to_rgb(color_int: int) -> Tuple[float, float, float]:
    """Converts PyMuPDF sRGB integer color to (r, g, b) floats in range [0, 1]."""
    r = ((color_int >> 16) & 255) / 255.0
    g = ((color_int >> 8) & 255) / 255.0
    b = (color_int & 255) / 255.0
    return (round(r, 3), round(g, 3), round(b, 3))


def _rgb_tuple_to_hex(rgb: Optional[Tuple[float, float, float]]) -> Optional[str]:
    """Converts an (r, g, b) float tuple in [0, 1] to #RRGGBB."""
    if not rgb or len(rgb) < 3:
        return None
    r = int(round(rgb[0] * 255))
    g = int(round(rgb[1] * 255))
    b = int(round(rgb[2] * 255))
    return f"#{r:02x}{g:02x}{b:02x}"


def detect_scanned_pdf(doc: fitz.Document) -> Tuple[bool, int, float]:
    """Determines whether a PDF is scanned/image-based by comparing

    total extractable characters against total image coverage area.
    Returns (is_scanned, total_chars, max_image_coverage_ratio).
    """
    total_chars = 0
    max_coverage = 0.0

    for page in doc:
        page_area = page.rect.width * page.rect.height
        text = page.get_text()
        total_chars += len(text.strip())

        # Measure image area
        image_area = 0.0
        for img_info in page.get_images():
            try:
                rects = page.get_image_rects(img_info[0])
                for r in rects:
                    image_area += r.width * r.height
            except Exception:
                pass

        if page_area > 0:
            coverage = image_area / page_area
            if coverage > max_coverage:
                max_coverage = coverage

    # A scanned PDF has low text density (<150 characters per page) and high image coverage (>60%)
    avg_chars_per_page = total_chars / max(1, len(doc))
    is_scanned = avg_chars_per_page < 150 and max_coverage > 0.6
    return is_scanned, total_chars, round(max_coverage, 3)


def extract_pdf_spans_and_assets(pdf_path: str) -> PdfLayout:
    """Extracts raw text spans, lines, blocks, vector drawings, images, and links

    from all pages of a PDF document using PyMuPDF.
    """
    is_valid, err, page_count = validate_pdf(pdf_path)
    if not is_valid:
        raise ValueError(err or "Invalid PDF")

    doc = fitz.open(pdf_path)
    is_scanned, total_chars, image_coverage = detect_scanned_pdf(doc)

    page_sizes: List[Dict[str, float]] = []
    blocks_out: List[PdfBlock] = []
    drawings_out: List[PdfVectorDrawing] = []
    images_out: List[PdfImage] = []
    links_out: List[PdfLink] = []

    block_counter = 0
    line_counter = 0
    span_counter = 0

    for p_idx, page in enumerate(doc):
        page_num = p_idx + 1
        page_rect = page.rect
        page_sizes.append({
            "page_number": page_num,
            "width_pt": round(page_rect.width, 2),
            "height_pt": round(page_rect.height, 2),
        })

        # 1. Extract Links
        for link in page.get_links():
            if link.get("uri"):
                r = link.get("from")
                if r:
                    links_out.append(PdfLink(
                        page_number=page_num,
                        rect=[round(r.x0, 2), round(r.y0, 2), round(r.x1, 2), round(r.y1, 2)],
                        uri=link["uri"],
                    ))

        # 2. Extract Vector Drawings (paths, rects, lines)
        for draw in page.get_drawings():
            rect = draw.get("rect")
            if not rect:
                continue
            d_type = "rect"
            items = draw.get("items", [])
            if any(item[0] == "l" for item in items):
                d_type = "line"
            elif any(item[0] == "c" for item in items):
                d_type = "curve"

            fill_hex = _rgb_tuple_to_hex(draw.get("fill"))
            stroke_hex = _rgb_tuple_to_hex(draw.get("color"))
            width_pt = draw.get("width") or 1.0

            drawings_out.append(PdfVectorDrawing(
                page_number=page_num,
                type=d_type,
                rect=[round(rect.x0, 2), round(rect.y0, 2), round(rect.x1, 2), round(rect.y1, 2)],
                fill_color=fill_hex,
                stroke_color=stroke_hex,
                width_pt=round(width_pt, 2),
            ))

        # 3. Extract Images
        for img_idx, img_info in enumerate(page.get_images()):
            xref = img_info[0]
            try:
                rects = page.get_image_rects(xref)
                r = rects[0] if rects else None
            except Exception:
                r = None

            bbox = [round(r.x0, 2), round(r.y0, 2), round(r.x1, 2), round(r.y1, 2)] if r else [0.0, 0.0, 0.0, 0.0]
            images_out.append(PdfImage(
                page_number=page_num,
                image_index=img_idx,
                bbox=bbox,
                width_px=img_info[2],
                height_px=img_info[3],
                format=img_info[8] if len(img_info) > 8 else "png",
            ))

        # 4. Extract Text Blocks, Lines, and Spans
        text_dict = page.get_text("dict", flags=fitz.TEXT_DEHYPHENATE)
        raw_blocks = text_dict.get("blocks", [])

        for b in raw_blocks:
            # Block type 0 is text, type 1 is image
            if b.get("type") != 0:
                continue

            b_rect = b.get("bbox", [0, 0, 0, 0])
            b_lines: List[PdfLine] = []
            block_full_text: List[str] = []

            for l in b.get("lines", []):
                l_rect = l.get("bbox", [0, 0, 0, 0])
                line_spans: List[PdfSpan] = []
                line_full_text: List[str] = []
                baseline_origin = [round(l_rect[0], 2), round(l_rect[3], 2)]

                for s in l.get("spans", []):
                    text = s.get("text", "")
                    if not text:
                        continue

                    span_flags_int = s.get("flags", 0)
                    is_bold = bool(span_flags_int & 2 or span_flags_int & 16 or "bold" in s.get("font", "").lower() or "bd" in s.get("font", "").lower())
                    is_italic = bool(span_flags_int & 1 or "italic" in s.get("font", "").lower() or "it" in s.get("font", "").lower() or "oblique" in s.get("font", "").lower())
                    is_monospace = bool(span_flags_int & 8 or "mono" in s.get("font", "").lower() or "courier" in s.get("font", "").lower())
                    is_serif = bool(span_flags_int & 4 or "times" in s.get("font", "").lower() or "serif" in s.get("font", "").lower())

                    color_int = s.get("color", 0)
                    color_hex = _srgb_int_to_hex(color_int)
                    color_rgb = _srgb_int_to_rgb(color_int)

                    origin = s.get("origin")
                    if origin and len(origin) >= 2:
                        s_origin = [round(origin[0], 2), round(origin[1], 2)]
                        baseline_origin = s_origin
                    else:
                        s_origin = [round(s["bbox"][0], 2), round(s["bbox"][3], 2)]

                    clean_font = s.get("font", "Helvetica")
                    # Clean font family: strip subset tag e.g. "ABCDEF+Calibri-Bold" -> "Calibri"
                    family_part = clean_font.split("+")[-1].split("-")[0]

                    pdf_span = PdfSpan(
                        span_id=f"span_{span_counter}",
                        text=text,
                        font_name=clean_font,
                        font_family=family_part,
                        font_size_pt=round(s.get("size", 10.0), 2),
                        flags=SpanFlags(
                            is_bold=is_bold,
                            is_italic=is_italic,
                            is_monospace=is_monospace,
                            is_serif=is_serif,
                        ),
                        color_rgb=color_rgb,
                        color_hex=color_hex,
                        bbox=[round(coord, 2) for coord in s.get("bbox", [0, 0, 0, 0])],
                        origin=s_origin,
                        char_count=len(text),
                    )
                    span_counter += 1
                    line_spans.append(pdf_span)
                    line_full_text.append(text)

                if line_spans:
                    full_l_text = " ".join(t.strip() for t in line_full_text if t.strip())
                    pdf_line = PdfLine(
                        line_id=f"line_{line_counter}",
                        bbox=[round(coord, 2) for coord in l_rect],
                        baseline_origin=baseline_origin,
                        spans=line_spans,
                        text=full_l_text,
                    )
                    line_counter += 1
                    b_lines.append(pdf_line)
                    block_full_text.append(full_l_text)

            if b_lines:
                full_b_text = "\n".join(block_full_text)
                pdf_block = PdfBlock(
                    block_id=f"blk_{block_counter}",
                    page_number=page_num,
                    column_id="col_main",
                    bbox=[round(coord, 2) for coord in b_rect],
                    max_width_pt=round(b_rect[2] - b_rect[0], 2),
                    reading_order=block_counter,
                    lines=b_lines,
                    text=full_b_text,
                )
                block_counter += 1
                blocks_out.append(pdf_block)

    metadata = PdfDocumentMetadata(
        page_count=len(page_sizes),
        page_sizes=page_sizes,
        is_encrypted=False,
        is_scanned=is_scanned,
        extractable_char_count=total_chars,
        has_vector_drawings=len(drawings_out) > 0,
        image_count=len(images_out),
        link_count=len(links_out),
    )

    doc.close()
    return PdfLayout(
        document_metadata=metadata,
        blocks=blocks_out,
        vector_drawings=drawings_out,
        images=images_out,
        links=links_out,
    )
