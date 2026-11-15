from typing import List, Literal, Optional
from pydantic import BaseModel, Field

PageSize = Literal["A4", "Letter"]
Unit = Literal["pt", "px"]
BulletStyle = Literal["disc", "circle", "square", "dash", "arrow", "none"]
HeadingStyle = Literal["underline", "bar", "plain", "caps", "boxed", "pill"]
ColumnLayoutType = Literal[
    "single",
    "sidebar_left",
    "sidebar_right",
    "header_banner",
    "compact",
    "creative",
    "minimal",
    "academic",
]


class Margins(BaseModel):
    top: float = 36.0
    bottom: float = 36.0
    left: float = 40.0
    right: float = 40.0
    unit: Unit = "pt"


class FontSizes(BaseModel):
    name: float = 22.0
    headerTitle: float = 12.0
    contact: float = 9.0
    sectionHeading: float = 13.0
    itemTitle: float = 11.0
    itemSubtitle: float = 10.0
    body: float = 9.5
    meta: float = 8.5
    unit: Unit = "pt"


class Typography(BaseModel):
    baseFontFamily: str = "Inter"
    headingFontFamily: str = "Inter"
    nameFontFamily: Optional[str] = None
    fontSizeScale: float = 1.0
    fontSizes: FontSizes = Field(default_factory=FontSizes)
    lineHeight: float = 1.45


class Spacing(BaseModel):
    sectionSpacing: float = 14.0
    itemSpacing: float = 8.0
    bulletSpacing: float = 3.0
    headerBottomSpacing: float = 16.0
    unit: Unit = "pt"


class Colors(BaseModel):
    accent: str = "#2563eb"
    text: str = "#111827"
    muted: str = "#4b5563"
    background: str = "#ffffff"
    sidebarBackground: str = "#f8fafc"
    divider: str = "#e5e7eb"
    headerBannerColor: Optional[str] = None
    headerBannerTextColor: Optional[str] = None


class ColumnLayout(BaseModel):
    type: ColumnLayoutType = "single"
    sidebarWidthPercent: float = 32.0
    sidebarSectionIds: List[str] = Field(default_factory=list)
    mainSectionIds: List[str] = Field(default_factory=list)


class Decorations(BaseModel):
    headerBanner: bool = False
    headerBannerColor: str = "#0f172a"
    headerBannerTextColor: str = "#ffffff"
    avatarShape: Literal["circle", "square"] = "circle"
    showAvatar: bool = False
    avatarUrl: Optional[str] = None


class ResumeStyle(BaseModel):
    templateId: str = "classic-single-column"
    pageSize: PageSize = "A4"
    margins: Margins = Field(default_factory=Margins)
    typography: Typography = Field(default_factory=Typography)
    spacing: Spacing = Field(default_factory=Spacing)
    colors: Colors = Field(default_factory=Colors)
    bulletStyle: BulletStyle = "disc"
    headingStyle: HeadingStyle = "bar"
    layout: ColumnLayout = Field(default_factory=ColumnLayout)
    decorations: Decorations = Field(default_factory=Decorations)
    dateFormat: str = "MMM YYYY"
