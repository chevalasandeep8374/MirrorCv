from typing import List, Optional, Literal, Dict, Any, Tuple
from pydantic import BaseModel, Field


class SpanFlags(BaseModel):
    is_bold: bool = False
    is_italic: bool = False
    is_monospace: bool = False
    is_serif: bool = False


class PdfSpan(BaseModel):
    span_id: str
    text: str
    font_name: str
    font_family: str
    font_size_pt: float
    flags: SpanFlags = Field(default_factory=SpanFlags)
    color_rgb: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    color_hex: str = "#000000"
    bbox: List[float] = Field(default_factory=list)  # [x0, y0, x1, y1]
    origin: List[float] = Field(default_factory=list)  # [x, y]
    char_count: int = 0


class PdfLine(BaseModel):
    line_id: str
    bbox: List[float] = Field(default_factory=list)  # [x0, y0, x1, y1]
    baseline_origin: List[float] = Field(default_factory=list)  # [x, y]
    spans: List[PdfSpan] = Field(default_factory=list)
    text: str = ""
    is_right_aligned_meta: bool = False


class BulletGlyphInfo(BaseModel):
    is_bullet: bool = False
    glyph: Optional[str] = None
    hanging_indent_pt: float = 0.0


class BlockSpacing(BaseModel):
    before_pt: float = 0.0
    after_pt: float = 0.0
    line_height: float = 1.2


class BlockIndent(BaseModel):
    left_pt: float = 0.0
    hanging_pt: float = 0.0


class PdfBlock(BaseModel):
    block_id: str
    page_number: int = 1
    column_id: str = "col_main"
    bbox: List[float] = Field(default_factory=list)  # [x0, y0, x1, y1]
    max_width_pt: float = 500.0
    reading_order: int = 0
    lines: List[PdfLine] = Field(default_factory=list)
    text: str = ""
    spacing: BlockSpacing = Field(default_factory=BlockSpacing)
    indent: BlockIndent = Field(default_factory=BlockIndent)
    bullet_info: BulletGlyphInfo = Field(default_factory=BulletGlyphInfo)


class PdfColumn(BaseModel):
    column_id: str
    page_number: int = 1
    bbox: List[float] = Field(default_factory=list)  # [x0, y0, x1, y1]
    width_pt: float = 500.0
    type: Literal["main", "sidebar", "header", "footer"] = "main"


class PdfVectorDrawing(BaseModel):
    page_number: int = 1
    type: Literal["rect", "line", "curve"] = "rect"
    rect: List[float] = Field(default_factory=list)  # [x0, y0, x1, y1]
    fill_color: Optional[str] = None
    stroke_color: Optional[str] = None
    width_pt: float = 1.0


class PdfImage(BaseModel):
    page_number: int = 1
    image_index: int = 0
    bbox: List[float] = Field(default_factory=list)  # [x0, y0, x1, y1]
    width_px: int = 0
    height_px: int = 0
    format: str = "png"


class PdfLink(BaseModel):
    page_number: int = 1
    rect: List[float] = Field(default_factory=list)  # [x0, y0, x1, y1]
    uri: str = ""


class PdfDocumentMetadata(BaseModel):
    page_count: int = 1
    page_sizes: List[Dict[str, float]] = Field(default_factory=list)
    is_encrypted: bool = False
    is_scanned: bool = False
    extractable_char_count: int = 0
    has_vector_drawings: bool = False
    image_count: int = 0
    link_count: int = 0


class PdfLayout(BaseModel):
    document_metadata: PdfDocumentMetadata = Field(default_factory=PdfDocumentMetadata)
    columns: List[PdfColumn] = Field(default_factory=list)
    blocks: List[PdfBlock] = Field(default_factory=list)
    vector_drawings: List[PdfVectorDrawing] = Field(default_factory=list)
    images: List[PdfImage] = Field(default_factory=list)
    links: List[PdfLink] = Field(default_factory=list)


class FontResolutionEntry(BaseModel):
    original_font_name: str
    clean_family: str
    is_embedded: bool = False
    is_subset: bool = False
    style_flags: Dict[str, bool] = Field(default_factory=dict)
    resolved_font_name: str
    resolved_font_path: Optional[str] = None
    source: Literal["exact_match", "metric_compatible", "system_fallback", "user_uploaded"] = "system_fallback"
    match_confidence: float = 1.0
    glyph_width_scale: float = 1.0
    notes: str = ""


class FontSubstitution(BaseModel):
    original: str
    replacement: str
    confidence: float
    notes: str = ""


class FontResolutionTable(BaseModel):
    fonts: List[FontResolutionEntry] = Field(default_factory=list)
    all_matched_well: bool = True
    overall_confidence: float = 1.0
    substitutions: List[FontSubstitution] = Field(default_factory=list)


FidelityTier = Literal["A", "B", "C"]


class FidelityScoreBreakdown(BaseModel):
    total_score: float = 100.0
    page_count_score: float = 100.0
    position_delta_score: float = 100.0
    font_match_score: float = 100.0
    ssim_score: float = 100.0
    tier: FidelityTier = "A"
    selected_strategy: Literal["in_place", "rebuild", "ocr_rebuild"] = "in_place"
    mean_position_delta_pt: float = 0.0
    max_position_delta_pt: float = 0.0
    explanation: str = ""
