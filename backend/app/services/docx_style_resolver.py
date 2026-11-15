"""DOCX Style Inheritance Resolver.
Parses styles.xml, docDefaults, and basedOn chains to resolve effective formatting
for every run and paragraph so values are never 'unknown'.
"""

from xml.etree.ElementTree import Element
import defusedxml.ElementTree as defused_ET
from typing import Dict, Any, Optional, Tuple

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W_NS}


def _pt_from_eighth_pt(val: Optional[str]) -> Optional[float]:
    if not val:
        return None
    try:
        return float(val) / 8.0
    except ValueError:
        return None


def _pt_from_half_pt(val: Optional[str]) -> Optional[float]:
    if not val:
        return None
    try:
        return float(val) / 2.0
    except ValueError:
        return None


def _pt_from_twips(val: Optional[str]) -> Optional[float]:
    if not val:
        return None
    try:
        return float(val) / 20.0
    except ValueError:
        return None


class ResolvedFormatting:
    def __init__(
        self,
        font_family: str = "Calibri",
        font_size_pt: float = 11.0,
        bold: bool = False,
        italic: bool = False,
        underline: bool = False,
        color_hex: str = "#000000",
        caps: bool = False,
        small_caps: bool = False,
        character_spacing_pt: float = 0.0,
        highlight: Optional[str] = None,
    ):
        self.font_family = font_family
        self.font_size_pt = font_size_pt
        self.bold = bold
        self.italic = italic
        self.underline = underline
        self.color_hex = color_hex
        self.caps = caps
        self.small_caps = small_caps
        self.character_spacing_pt = character_spacing_pt
        self.highlight = highlight

    def to_dict(self) -> Dict[str, Any]:
        return {
            "font_family": self.font_family,
            "font_size_pt": self.font_size_pt,
            "bold": self.bold,
            "italic": self.italic,
            "underline": self.underline,
            "color_hex": self.color_hex,
            "caps": self.caps,
            "small_caps": self.small_caps,
            "character_spacing_pt": self.character_spacing_pt,
            "highlight": self.highlight,
        }


class DocxStyleResolver:
    """Parses styles.xml and resolves inheritance chains."""

    def __init__(self, styles_xml_bytes: Optional[bytes] = None):
        self.doc_defaults_rPr: Dict[str, Any] = {
            "font_family": "Calibri",
            "font_size_pt": 11.0,
            "color_hex": "#000000",
            "bold": False,
            "italic": False,
            "underline": False,
        }
        self.doc_defaults_pPr: Dict[str, Any] = {
            "spacing_before_pt": 0.0,
            "spacing_after_pt": 0.0,
            "line_spacing_pt": 13.2,
            "alignment": "left",
        }
        self.styles: Dict[str, Dict[str, Any]] = {}

        if styles_xml_bytes:
            self._parse_styles(styles_xml_bytes)

    def _parse_styles(self, xml_bytes: bytes):
        try:
            root = defused_ET.fromstring(xml_bytes)
        except Exception:
            return

        # 1. Parse docDefaults
        doc_def = root.find("w:docDefaults", NS)
        if doc_def is not None:
            rpr_def = doc_def.find("w:rPrDefault/w:rPr", NS)
            if rpr_def is not None:
                self.doc_defaults_rPr.update(self._parse_rPr_elements(rpr_def))

            ppr_def = doc_def.find("w:pPrDefault/w:pPr", NS)
            if ppr_def is not None:
                self.doc_defaults_pPr.update(self._parse_pPr_elements(ppr_def))

        # 2. Parse individual styles
        for s_elem in root.findall("w:style", NS):
            style_id = s_elem.attrib.get(f"{{{W_NS}}}styleId")
            if not style_id:
                continue

            style_type = s_elem.attrib.get(f"{{{W_NS}}}type", "paragraph")
            based_on_elem = s_elem.find("w:basedOn", NS)
            based_on = based_on_elem.attrib.get(f"{{{W_NS}}}val") if based_on_elem is not None else None

            rPr_elem = s_elem.find("w:rPr", NS)
            pPr_elem = s_elem.find("w:pPr", NS)

            self.styles[style_id] = {
                "type": style_type,
                "based_on": based_on,
                "rPr": self._parse_rPr_elements(rPr_elem) if rPr_elem is not None else {},
                "pPr": self._parse_pPr_elements(pPr_elem) if pPr_elem is not None else {},
            }

    def _parse_rPr_elements(self, rPr_elem: Element) -> Dict[str, Any]:
        res: Dict[str, Any] = {}
        # Font family: check ascii, hAnsi, eastAsia
        rFonts = rPr_elem.find("w:rFonts", NS)
        if rFonts is not None:
            f = rFonts.attrib.get(f"{{{W_NS}}}ascii") or rFonts.attrib.get(f"{{{W_NS}}}hAnsi")
            if f:
                res["font_family"] = f

        # Font size: w:sz is in half-points
        sz = rPr_elem.find("w:sz", NS)
        if sz is not None:
            val = _pt_from_half_pt(sz.attrib.get(f"{{{W_NS}}}val"))
            if val is not None:
                res["font_size_pt"] = val

        # Bold
        b = rPr_elem.find("w:b", NS)
        if b is not None:
            res["bold"] = b.attrib.get(f"{{{W_NS}}}val", "true").lower() in ("true", "1", "on")

        # Italic
        i = rPr_elem.find("w:i", NS)
        if i is not None:
            res["italic"] = i.attrib.get(f"{{{W_NS}}}val", "true").lower() in ("true", "1", "on")

        # Underline
        u = rPr_elem.find("w:u", NS)
        if u is not None:
            u_val = u.attrib.get(f"{{{W_NS}}}val", "none")
            res["underline"] = u_val not in ("none", "false", "0")

        # Color
        color = rPr_elem.find("w:color", NS)
        if color is not None:
            c_val = color.attrib.get(f"{{{W_NS}}}val")
            if c_val and c_val.lower() != "auto":
                res["color_hex"] = f"#{c_val}"

        # Caps / Small caps
        caps = rPr_elem.find("w:caps", NS)
        if caps is not None:
            res["caps"] = caps.attrib.get(f"{{{W_NS}}}val", "true").lower() in ("true", "1")

        smallCaps = rPr_elem.find("w:smallCaps", NS)
        if smallCaps is not None:
            res["small_caps"] = smallCaps.attrib.get(f"{{{W_NS}}}val", "true").lower() in ("true", "1")

        # Character spacing (twips)
        spacing = rPr_elem.find("w:spacing", NS)
        if spacing is not None:
            res["character_spacing_pt"] = _pt_from_twips(spacing.attrib.get(f"{{{W_NS}}}val")) or 0.0

        return res

    def _parse_pPr_elements(self, pPr_elem: Element) -> Dict[str, Any]:
        res: Dict[str, Any] = {}
        # Alignment
        jc = pPr_elem.find("w:jc", NS)
        if jc is not None:
            res["alignment"] = jc.attrib.get(f"{{{W_NS}}}val", "left")

        # Spacing
        spacing = pPr_elem.find("w:spacing", NS)
        if spacing is not None:
            before = _pt_from_twips(spacing.attrib.get(f"{{{W_NS}}}before"))
            after = _pt_from_twips(spacing.attrib.get(f"{{{W_NS}}}after"))
            if before is not None:
                res["spacing_before_pt"] = before
            if after is not None:
                res["spacing_after_pt"] = after

        # Indents
        ind = pPr_elem.find("w:ind", NS)
        if ind is not None:
            left = _pt_from_twips(ind.attrib.get(f"{{{W_NS}}}left"))
            right = _pt_from_twips(ind.attrib.get(f"{{{W_NS}}}right"))
            first_line = _pt_from_twips(ind.attrib.get(f"{{{W_NS}}}firstLine"))
            hanging = _pt_from_twips(ind.attrib.get(f"{{{W_NS}}}hanging"))
            if left is not None:
                res["indent_left_pt"] = left
            if right is not None:
                res["indent_right_pt"] = right
            if first_line is not None:
                res["indent_first_line_pt"] = first_line
            if hanging is not None:
                res["indent_hanging_pt"] = hanging

        return res

    def resolve_run_formatting(
        self,
        style_id: Optional[str] = None,
        direct_rPr: Optional[Dict[str, Any]] = None,
    ) -> ResolvedFormatting:
        """Resolves formatting by merging: docDefaults -> style inheritance chain -> direct formatting."""
        merged: Dict[str, Any] = dict(self.doc_defaults_rPr)

        # Traverse based_on style chain
        chain = []
        cur = style_id
        visited = set()
        while cur and cur in self.styles and cur not in visited:
            visited.add(cur)
            chain.append(self.styles[cur])
            cur = self.styles[cur].get("based_on")

        for s in reversed(chain):
            merged.update(s.get("rPr", {}))

        if direct_rPr:
            merged.update(direct_rPr)

        return ResolvedFormatting(
            font_family=merged.get("font_family", "Calibri"),
            font_size_pt=merged.get("font_size_pt", 11.0),
            bold=merged.get("bold", False),
            italic=merged.get("italic", False),
            underline=merged.get("underline", False),
            color_hex=merged.get("color_hex", "#000000"),
            caps=merged.get("caps", False),
            small_caps=merged.get("small_caps", False),
            character_spacing_pt=merged.get("character_spacing_pt", 0.0),
            highlight=merged.get("highlight"),
        )
