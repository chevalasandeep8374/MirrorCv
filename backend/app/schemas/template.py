from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field


class PageSizePt(BaseModel):
    name: str = "A4"
    width_pt: float = 595.3
    height_pt: float = 841.9


class MarginsPt(BaseModel):
    top_pt: float = 36.0
    bottom_pt: float = 36.0
    left_pt: float = 40.0
    right_pt: float = 40.0


class DefaultFont(BaseModel):
    family: str = "Calibri"
    size_pt: float = 11.0


class DocumentMetadata(BaseModel):
    page_size: PageSizePt = Field(default_factory=PageSizePt)
    margins: MarginsPt = Field(default_factory=MarginsPt)
    default_font: DefaultFont = Field(default_factory=DefaultFont)
    total_paragraphs: int = 0
    total_tables: int = 0
    has_text_boxes: bool = False
    headers_text: List[str] = Field(default_factory=list)
    footers_text: List[str] = Field(default_factory=list)


class ParagraphLocation(BaseModel):
    type: Literal["body", "table_cell", "text_box"] = "body"
    table_index: Optional[int] = None
    row_index: Optional[int] = None
    col_index: Optional[int] = None
    cell_width_pt: Optional[float] = None


class SpacingInfo(BaseModel):
    before_pt: float = 0.0
    after_pt: float = 0.0
    line_spacing_pt: Optional[float] = None
    line_spacing_rule: Optional[str] = None


class IndentInfo(BaseModel):
    left_pt: float = 0.0
    right_pt: float = 0.0
    first_line_pt: float = 0.0
    hanging_pt: float = 0.0


class BulletInfo(BaseModel):
    is_bullet: bool = False
    num_id: Optional[int] = None
    ilvl: Optional[int] = None
    bullet_char: Optional[str] = None


class RunFormatting(BaseModel):
    font_family: Optional[str] = None
    font_size_pt: Optional[float] = None
    bold: bool = False
    italic: bool = False
    underline: bool = False
    color_hex: Optional[str] = None
    highlight: Optional[str] = None


class RunFingerprint(BaseModel):
    index: int
    text: str
    formatting: RunFormatting = Field(default_factory=RunFormatting)


class ParagraphFingerprint(BaseModel):
    index: int
    location: ParagraphLocation = Field(default_factory=ParagraphLocation)
    text: str
    style_name: str = "Normal"
    alignment: Optional[str] = None
    spacing: SpacingInfo = Field(default_factory=SpacingInfo)
    indent: IndentInfo = Field(default_factory=IndentInfo)
    bullet_info: BulletInfo = Field(default_factory=BulletInfo)
    runs: List[RunFingerprint] = Field(default_factory=list)
    character_count: int = 0
    estimated_lines: int = 1


class DocxFingerprint(BaseModel):
    document_metadata: DocumentMetadata = Field(default_factory=DocumentMetadata)
    paragraphs: List[ParagraphFingerprint] = Field(default_factory=list)
