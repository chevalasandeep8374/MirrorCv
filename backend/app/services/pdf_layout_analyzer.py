import re
from typing import List, Dict, Optional, Tuple
from app.schemas.pdf_template import (
    PdfLayout,
    PdfBlock,
    PdfLine,
    PdfSpan,
    PdfColumn,
    BulletGlyphInfo,
    BlockSpacing,
    BlockIndent,
)
from app.services.role_classifier import _detect_section_heading

BULLET_GLYPHS = ["•", "–", "—", "-", "▪", "➤", "○", "*", "►", "■", "\u2022", "\u25b6", "\u25cf", "\u25aa", "\u25cb"]
BULLET_REGEX = re.compile(r"^([•–—\-▪➤○*►■\u2022\u25b6\u25cf\u25aa\u25cb]|\d+\.)\s*(.*)$")


def detect_bullet_and_indent(text: str, left_x: float, min_col_x: float) -> Tuple[bool, Optional[str], str, float]:
    """Checks if text begins with a bullet glyph and computes hanging indent.

    Returns (is_bullet, glyph, stripped_text, hanging_indent_pt).
    """
    clean = text.strip()
    m = BULLET_REGEX.match(clean)
    if m:
        glyph = m.group(1)
        remaining_text = m.group(2).strip()
        hanging_indent = max(0.0, left_x - min_col_x)
        return True, glyph, remaining_text, round(hanging_indent, 2)

    return False, None, clean, 0.0


def detect_columns(layout: PdfLayout) -> List[PdfColumn]:
    """Identifies single-column vs two-column sidebar layouts on each page

    by analyzing horizontal span clusters and background vector shapes.
    """
    columns: List[PdfColumn] = []

    for page_size in layout.document_metadata.page_sizes:
        page_num = page_size["page_number"]
        page_w = page_size["width_pt"]
        page_h = page_size["height_pt"]

        # Get all text blocks and vector rects on this page
        p_blocks = [b for b in layout.blocks if b.page_number == page_num]
        p_rects = [d for d in layout.vector_drawings if d.page_number == page_num and d.type == "rect"]

        # Check if there is a distinct vertical sidebar background rectangle
        sidebar_rect = None
        for r in p_rects:
            r_box = r.rect
            r_w = r_box[2] - r_box[0]
            r_h = r_box[3] - r_box[1]
            # Sidebar condition: width between 15% and 40% of page, height > 70% of page
            if (0.15 * page_w <= r_w <= 0.40 * page_w) and (r_h >= 0.70 * page_h):
                sidebar_rect = r_box
                break

        if sidebar_rect:
            # We have a clear colored sidebar
            sb_x0, sb_y0, sb_x1, sb_y1 = sidebar_rect
            if sb_x0 < (page_w / 2):  # Left sidebar
                sidebar_col = PdfColumn(
                    column_id=f"col_sb_p{page_num}",
                    page_number=page_num,
                    bbox=[sb_x0, 0.0, sb_x1, page_h],
                    width_pt=round(sb_x1 - sb_x0, 2),
                    type="sidebar",
                )
                main_col = PdfColumn(
                    column_id=f"col_main_p{page_num}",
                    page_number=page_num,
                    bbox=[sb_x1, 0.0, page_w, page_h],
                    width_pt=round(page_w - sb_x1, 2),
                    type="main",
                )
                columns.extend([sidebar_col, main_col])
            else:  # Right sidebar
                main_col = PdfColumn(
                    column_id=f"col_main_p{page_num}",
                    page_number=page_num,
                    bbox=[0.0, 0.0, sb_x0, page_h],
                    width_pt=round(sb_x0, 2),
                    type="main",
                )
                sidebar_col = PdfColumn(
                    column_id=f"col_sb_p{page_num}",
                    page_number=page_num,
                    bbox=[sb_x0, 0.0, page_w, page_h],
                    width_pt=round(page_w - sb_x0, 2),
                    type="sidebar",
                )
                columns.extend([main_col, sidebar_col])
            continue

        # If no colored background rect, cluster horizontal coordinates of text blocks
        if len(p_blocks) >= 4:
            x_lefts = [b.bbox[0] for b in p_blocks if len(b.bbox) >= 4]
            min_x = min(x_lefts)
            max_x = max(b.bbox[2] for b in p_blocks if len(b.bbox) >= 4)

            # Check if there are two separated left margins (gap > 40pt)
            midpoint = (min_x + max_x) / 2
            left_group = [x for x in x_lefts if x < midpoint - 20]
            right_group = [x for x in x_lefts if x > midpoint + 20]

            if len(left_group) >= 3 and len(right_group) >= 3:
                # Two column layout detected
                split_x = (max(left_group) + min(right_group)) / 2
                col1 = PdfColumn(
                    column_id=f"col_1_p{page_num}",
                    page_number=page_num,
                    bbox=[min_x - 10, 0.0, split_x, page_h],
                    width_pt=round(split_x - min_x + 10, 2),
                    type="sidebar" if (split_x - min_x) < (page_w * 0.4) else "main",
                )
                col2 = PdfColumn(
                    column_id=f"col_2_p{page_num}",
                    page_number=page_num,
                    bbox=[split_x, 0.0, max_x + 10, page_h],
                    width_pt=round(max_x + 10 - split_x, 2),
                    type="main",
                )
                columns.extend([col1, col2])
                continue

        # Default: Single column layout
        columns.append(PdfColumn(
            column_id=f"col_main_p{page_num}",
            page_number=page_num,
            bbox=[0.0, 0.0, page_w, page_h],
            width_pt=round(page_w, 2),
            type="main",
        ))

    return columns


def _create_sub_block(parent_block: PdfBlock, lines: List[PdfLine], block_id: str) -> PdfBlock:
    """Creates a new PdfBlock from a subset of lines belonging to a parent block."""
    sub_x0 = min((l.bbox[0] for l in lines if len(l.bbox) >= 4), default=parent_block.bbox[0])
    sub_y0 = min((l.bbox[1] for l in lines if len(l.bbox) >= 4), default=parent_block.bbox[1])
    sub_x1 = max((l.bbox[2] for l in lines if len(l.bbox) >= 4), default=parent_block.bbox[2])
    sub_y1 = max((l.bbox[3] for l in lines if len(l.bbox) >= 4), default=parent_block.bbox[3])
    text = "\n".join(l.text.strip() for l in lines if l.text.strip())

    return PdfBlock(
        block_id=block_id,
        page_number=parent_block.page_number,
        column_id=parent_block.column_id,
        bbox=[round(sub_x0, 2), round(sub_y0, 2), round(sub_x1, 2), round(sub_y1, 2)],
        max_width_pt=parent_block.max_width_pt,
        reading_order=parent_block.reading_order,
        lines=lines,
        text=text,
        spacing=parent_block.spacing,
        indent=parent_block.indent,
        bullet_info=parent_block.bullet_info,
    )


def _split_blocks_at_section_boundaries(raw_blocks: List[PdfBlock]) -> List[PdfBlock]:
    """Splits multi-line blocks whenever an individual line represents a section heading."""
    out_blocks: List[PdfBlock] = []
    blk_counter = 0

    for block in raw_blocks:
        if len(block.lines) <= 1:
            out_blocks.append(block)
            continue

        has_heading = any(_detect_section_heading(line.text.strip()) for line in block.lines)
        if not has_heading:
            out_blocks.append(block)
            continue

        current_lines: List[PdfLine] = []
        for line in block.lines:
            if _detect_section_heading(line.text.strip()):
                if current_lines:
                    out_blocks.append(_create_sub_block(block, current_lines, f"blk_{blk_counter}"))
                    blk_counter += 1
                    current_lines = []
                out_blocks.append(_create_sub_block(block, [line], f"blk_{blk_counter}"))
                blk_counter += 1
            else:
                current_lines.append(line)

        if current_lines:
            out_blocks.append(_create_sub_block(block, current_lines, f"blk_{blk_counter}"))
            blk_counter += 1

    return out_blocks


def analyze_pdf_layout(layout: PdfLayout) -> PdfLayout:
    """Refines raw extracted blocks: assigns columns, detects baseline meta lines,

    identifies bullet glyphs with hanging indents, and establishes reading order.
    """
    layout.blocks = _split_blocks_at_section_boundaries(layout.blocks)
    columns = detect_columns(layout)
    layout.columns = columns

    # Build quick column lookup per page
    cols_by_page: Dict[int, List[PdfColumn]] = {}
    for col in columns:
        cols_by_page.setdefault(col.page_number, []).append(col)

    refined_blocks: List[PdfBlock] = []

    for block in layout.blocks:
        page_cols = cols_by_page.get(block.page_number, [])
        bx0, by0, bx1, by1 = block.bbox if len(block.bbox) >= 4 else (0, 0, 0, 0)
        b_mid_x = (bx0 + bx1) / 2

        # Assign block to best matching column
        matched_col = None
        for col in page_cols:
            cx0, cy0, cx1, cy1 = col.bbox
            if cx0 <= b_mid_x <= cx1 or (cx0 <= bx0 and bx1 <= cx1):
                matched_col = col
                break
        if not matched_col and page_cols:
            matched_col = page_cols[0]

        col_id = matched_col.column_id if matched_col else "col_main"
        col_x0 = matched_col.bbox[0] if matched_col else 0.0
        col_x1 = matched_col.bbox[2] if matched_col else block.max_width_pt

        # Calculate max available width for text wrapping inside this column
        max_available_w = max(50.0, col_x1 - bx0 - 15.0)

        # Detect bullet glyphs and hanging indents in the block
        is_bullet = False
        glyph = None
        hanging_indent = 0.0

        for line in block.lines:
            line_text = line.text.strip()
            lx0 = line.bbox[0] if len(line.bbox) >= 4 else bx0
            b_flag, b_glyph, b_clean, b_indent = detect_bullet_and_indent(line_text, lx0, col_x0)
            if b_flag:
                is_bullet = True
                glyph = b_glyph
                hanging_indent = b_indent
                break

        # Check for right-aligned dates / metadata within lines sharing same baseline
        for line in block.lines:
            if len(line.spans) >= 2:
                first_span = line.spans[0]
                last_span = line.spans[-1]
                gap = last_span.bbox[0] - first_span.bbox[2]
                # If there is a wide gap (>40pt) between first and last span on the line
                if gap > 40.0:
                    last_span_text = last_span.text.lower()
                    if any(term in last_span_text for term in ["present", "current", "20", "19", "jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]):
                        line.is_right_aligned_meta = True

        block.column_id = col_id
        block.max_width_pt = round(max_available_w, 2)
        block.bullet_info = BulletGlyphInfo(
            is_bullet=is_bullet,
            glyph=glyph,
            hanging_indent_pt=hanging_indent,
        )
        block.indent = BlockIndent(
            left_pt=round(max(0.0, bx0 - col_x0), 2),
            hanging_pt=hanging_indent,
        )
        block.spacing = BlockSpacing(
            before_pt=2.0,
            after_pt=4.0,
            line_height=1.25,
        )
        refined_blocks.append(block)

    # Establish natural reading order: top header (Name) first, then by column type, then by vertical y position
    def block_sort_key(b: PdfBlock):
        max_sz = max((s.font_size_pt for l in b.lines for s in l.spans), default=10.0)
        is_name_header = max_sz >= 18.0 and len(b.text.strip()) > 3 and (b.bbox[1] if len(b.bbox) >= 4 else 0.0) < 150.0
        header_priority = 0 if is_name_header else 1
        col_priority = 0 if "sb" in b.column_id or "sidebar" in b.column_id else 1
        y_pos = b.bbox[1] if len(b.bbox) >= 4 else 0.0
        return (b.page_number, header_priority, col_priority, y_pos)

    refined_blocks.sort(key=block_sort_key)
    for idx, b in enumerate(refined_blocks):
        b.reading_order = idx

    layout.blocks = refined_blocks
    return layout
