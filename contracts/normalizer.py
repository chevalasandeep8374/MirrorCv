"""Python normalizer for ResumeContent and StyleTokens (v1.0.0 -> v1.1.0).

Matches the logic and golden fixtures of frontend/src/lib/migration.ts.
"""

from typing import Dict, Any, Tuple
import copy

MONTH_NAMES = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]


def format_structured_date(dates: Dict[str, Any] | None, date_format: str = "MMM YYYY") -> str:
    if not dates:
        return ""

    def format_part(month: int | None, year: int | None) -> str:
        if not year:
            return ""
        if date_format == "YYYY":
            return str(year)
        if month and 1 <= month <= 12:
            if date_format == "MM/YYYY":
                return f"{month:02d}/{year}"
            return f"{MONTH_NAMES[month - 1]} {year}"
        return str(year)

    start_str = format_part(dates.get("startMonth"), dates.get("startYear"))
    end_str = "Present" if dates.get("isCurrent") else format_part(dates.get("endMonth"), dates.get("endYear"))

    if start_str and end_str:
        return f"{start_str} – {end_str}"
    if start_str:
        return start_str
    if end_str:
        return end_str
    return ""


def normalize_resume_tokens(
    raw_content: Dict[str, Any], raw_style: Dict[str, Any]
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Deterministic pure function to normalize ResumeContent and StyleTokens to 1.1.0."""
    content = copy.deepcopy(raw_content)
    style = copy.deepcopy(raw_style)

    # 1. Content normalization
    content["schema_version"] = "1.1.0"
    header = content.setdefault("header", {})
    field_vis = header.setdefault("fieldVisibility", {})
    default_vis = {
        "name": True,
        "title": True,
        "email": True,
        "phone": True,
        "location": True,
        "website": True,
        "photo": True,
    }
    for k, v in default_vis.items():
        field_vis.setdefault(k, v)

    for section in content.get("sections", []):
        section["visible"] = section.get("visible", True) is not False
        for item in section.get("items", []):
            item["visible"] = item.get("visible", True) is not False
            item.setdefault("itemType", "timeline")
            item.setdefault("groupId", None)

            # Date sync rule
            dates = item.get("dates")
            if dates and (dates.get("startYear") or dates.get("isCurrent")):
                item["dateRange"] = format_structured_date(dates, style.get("dateFormat", "MMM YYYY"))

            for bullet in item.get("bullets", []):
                bullet.setdefault("level", 0)
                bullet.setdefault("proficiency", None)

    # 2. Style normalization
    style["schema_version"] = "1.1.0"
    template_id = style.get("templateId", "")
    if "isLocked" not in style:
        style["isLocked"] = isinstance(template_id, str) and template_id.startswith("uploaded:")

    # Length units to pt
    if "margins" in style:
        style["margins"]["unit"] = "pt"
    if "spacing" in style:
        style["spacing"]["unit"] = "pt"

    # Typography font size model migration
    typography = style.setdefault("typography", {})
    legacy_font_sizes = typography.get("fontSizes")
    scale = typography.get("fontSizeScale", 1.0) or 1.0

    if not typography.get("fontSizeOffsets") and legacy_font_sizes:
        base_font_size = round(legacy_font_sizes.get("body", 9.5) * scale, 2)
        typography["baseFontSize"] = base_font_size

        def round_offset(val):
            v = val if val is not None else base_font_size
            return round((v * scale) - base_font_size, 2)

        typography["fontSizeOffsets"] = {
            "name": round_offset(legacy_font_sizes.get("name")),
            "headerTitle": round_offset(legacy_font_sizes.get("headerTitle")),
            "contact": round_offset(legacy_font_sizes.get("contact")),
            "sectionHeading": round_offset(legacy_font_sizes.get("sectionHeading")),
            "itemTitle": round_offset(legacy_font_sizes.get("itemTitle")),
            "itemSubtitle": round_offset(legacy_font_sizes.get("itemSubtitle")),
            "body": 0.0,
            "meta": round_offset(legacy_font_sizes.get("meta")),
        }
    elif not typography.get("fontSizeOffsets"):
        typography.setdefault("baseFontSize", 9.5)
        typography["fontSizeOffsets"] = {
            "name": 12.5,
            "headerTitle": 1.5,
            "contact": -0.5,
            "sectionHeading": 3.0,
            "itemTitle": 1.0,
            "itemSubtitle": 0.0,
            "body": 0.0,
            "meta": -1.0,
        }
    else:
        typography.setdefault("baseFontSize", 9.5)

    typography["fontSizeScale"] = 1.0

    # Colors & Accent toggles
    colors = style.setdefault("colors", {})
    colors.setdefault("area", "full_page")
    colors.setdefault("mode", "single")
    colors.setdefault("backgroundOverlayOpacity", 0.6)
    accent_toggles = colors.setdefault("accentToggles", {})
    default_accents = {
        "name": False,
        "jobTitle": False,
        "headings": True,
        "headingsLine": True,
        "headerIcons": True,
        "bullets": True,
        "dates": False,
        "entryTitle": False,
        "entrySubtitle": False,
        "linkIcons": True,
    }
    for k, v in default_accents.items():
        accent_toggles.setdefault(k, v)

    # Entry Layout
    entry_layout = style.setdefault("entryLayout", {})
    entry_layout.setdefault("structure", "full_width")
    entry_layout.setdefault("dateLocationPosition", "right")
    entry_layout.setdefault("headerSplitRatio", "auto")

    # Heading Config
    heading = style.setdefault("heading", {})
    heading.setdefault("capitalization", "none")
    heading.setdefault("iconStyle", "none")

    # Header Config
    header_cfg = style.setdefault("header", {})
    header_cfg.setdefault("alignment", "left")
    header_cfg.setdefault("arrangement", "bullet")

    # Photo Config
    photo = style.setdefault("photo", {})
    photo.setdefault("shape", "circle")
    photo.setdefault("size", "medium")
    photo.setdefault("border", "none")
    photo.setdefault("position", "right")

    # Link Styling
    link_styling = style.setdefault("linkStyling", {})
    link_styling.setdefault("underline", True)
    link_styling.setdefault("colored", False)
    link_styling.setdefault("showIcon", True)

    # Footer Config
    footer = style.setdefault("footer", {})
    footer.setdefault("showPageNumbers", True)
    footer.setdefault("showEmail", False)
    footer.setdefault("showName", False)

    # Layout Placement
    layout = style.setdefault("layout", {})
    layout.setdefault("sectionPlacement", {})

    # Section Customizations
    sec_cust = style.setdefault("sectionCustomizations", {})
    sec_cust.setdefault("summary", {"inHeader": False, "showHeading": True})
    sec_cust.setdefault("skills", {
        "style": "compact",
        "rowSpacing": "tight",
        "startRowsWithBullets": False,
        "subInfoStyle": "colon",
    })
    sec_cust.setdefault("experience", {
        "titleSubtitleOrder": "title_first",
        "groupPromotions": True,
    })
    sec_cust.setdefault("education", {
        "titleSubtitleOrder": "title_first",
    })
    sec_cust.setdefault("certificates", {
        "style": "compact",
    })
    sec_cust.setdefault("languages", {
        "style": "chips",
    })
    sec_cust.setdefault("interests", {
        "style": "chips",
    })
    sec_cust.setdefault("declaration", {
        "showPlace": True,
        "showDate": True,
    })

    return content, style
