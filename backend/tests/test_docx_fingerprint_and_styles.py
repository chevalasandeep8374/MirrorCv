import os
import io
import zipfile
import pytest
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from app.services.docx_style_resolver import DocxStyleResolver
from app.services.docx_fingerprint import (
    fingerprint_docx,
    strip_external_relationships,
    _load_rels_map,
)


def test_style_inheritance_resolution():
    styles_xml = b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
        <w:docDefaults>
            <w:rPrDefault>
                <w:rPr>
                    <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>
                    <w:sz w:val="22"/>
                    <w:color w:val="333333"/>
                </w:rPr>
            </w:rPrDefault>
        </w:docDefaults>
        <w:style w:type="paragraph" w:styleId="BaseHeading">
            <w:name w:val="Base Heading"/>
            <w:rPr>
                <w:rFonts w:ascii="Arial"/>
                <w:b/>
            </w:rPr>
        </w:style>
        <w:style w:type="paragraph" w:styleId="Heading1">
            <w:name w:val="heading 1"/>
            <w:basedOn w:val="BaseHeading"/>
            <w:rPr>
                <w:sz w:val="28"/>
                <w:color w:val="0055AA"/>
            </w:rPr>
        </w:style>
    </w:styles>"""

    resolver = DocxStyleResolver(styles_xml)

    # 1. Default formatting
    default_fmt = resolver.resolve_run_formatting()
    assert default_fmt.font_family == "Calibri"
    assert default_fmt.font_size_pt == 11.0
    assert default_fmt.color_hex == "#333333"
    assert default_fmt.bold is False

    # 2. Inherited style: Heading1 inherits font Arial and bold from BaseHeading, overrides size to 14pt (28/2) and color
    h1_fmt = resolver.resolve_run_formatting(style_id="Heading1")
    assert h1_fmt.font_family == "Arial"
    assert h1_fmt.font_size_pt == 14.0
    assert h1_fmt.bold is True
    assert h1_fmt.color_hex == "#0055AA"

    # 3. Direct run override on top of Heading1
    direct_override = {"italic": True, "font_size_pt": 16.0}
    resolved_direct = resolver.resolve_run_formatting(style_id="Heading1", direct_rPr=direct_override)
    assert resolved_direct.font_family == "Arial"
    assert resolved_direct.font_size_pt == 16.0
    assert resolved_direct.bold is True
    assert resolved_direct.italic is True
    assert resolved_direct.color_hex == "#0055AA"


def test_strip_external_relationships(tmp_path):
    docx_file = tmp_path / "test_rels.docx"
    doc = Document()
    doc.add_paragraph("Testing rels")
    doc.save(str(docx_file))

    # Inject an external relationship into document.xml.rels
    rels_content = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
        <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink"
            TargetMode="External" Target="https://evil-server.com/malicious.png"/>
        <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles"
            Target="styles.xml"/>
    </Relationships>"""

    # Modify zip
    buf = io.BytesIO()
    with zipfile.ZipFile(str(docx_file), "r") as zin:
        with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if item.filename == "word/_rels/document.xml.rels":
                    continue
                zout.writestr(item, zin.read(item.filename))
            zout.writestr("word/_rels/document.xml.rels", rels_content.encode("utf-8"))

    with open(str(docx_file), "wb") as f:
        f.write(buf.getvalue())

    # Strip external rels
    sanitized_file = tmp_path / "sanitized.docx"
    strip_external_relationships(str(docx_file), str(sanitized_file))

    # Verify that external URL is neutralized
    with zipfile.ZipFile(str(sanitized_file), "r") as z:
        rels_after = z.read("word/_rels/document.xml.rels").decode("utf-8")
        assert "evil-server.com" not in rels_after
        assert "about:blank" in rels_after
        assert "styles.xml" in rels_after


def test_fingerprint_tab_stops_and_borders(tmp_path):
    doc_path = tmp_path / "tabs_borders.docx"
    doc = Document()

    # Paragraph with bottom border (typical for section heading)
    p_bdr = doc.add_paragraph("WORK EXPERIENCE")
    pPr = p_bdr._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "12")
    bottom.set(qn("w:space"), "4")
    bottom.set(qn("w:color"), "003366")
    pBdr.append(bottom)
    pPr.append(pBdr)

    # Paragraph with right tab stop for date
    p_tab = doc.add_paragraph("Senior Engineer\t2020 - Present")
    pPr2 = p_tab._p.get_or_add_pPr()
    tabs_elem = OxmlElement("w:tabs")
    tab_elem = OxmlElement("w:tab")
    tab_elem.set(qn("w:val"), "right")
    tab_elem.set(qn("w:pos"), "9360")  # 468 pt
    tabs_elem.append(tab_elem)
    pPr2.append(tabs_elem)

    doc.save(str(doc_path))

    fp = fingerprint_docx(str(doc_path))
    assert len(fp.paragraphs) == 2

    # Verify heading border detection
    p0 = fp.paragraphs[0]
    assert p0.text == "WORK EXPERIENCE"
    assert p0.has_bottom_border is True

    # Verify tab stop detection
    p1 = fp.paragraphs[1]
    assert len(p1.tab_stops) == 1
    assert p1.tab_stops[0]["val"] == "right"
    assert p1.tab_stops[0]["pos_pt"] == 468.0


def test_fingerprint_nested_tables(tmp_path):
    doc_path = tmp_path / "nested_tables.docx"
    doc = Document()

    # Outer table: 1 row, 2 columns
    outer_table = doc.add_table(rows=1, cols=2)
    c0 = outer_table.cell(0, 0)
    c1 = outer_table.cell(0, 1)

    c0.paragraphs[0].text = "Left sidebar content"

    # Inner table nested in c1
    inner_table = c1.add_table(rows=1, cols=1)
    inner_table.cell(0, 0).paragraphs[0].text = "Nested inner cell text"

    doc.save(str(doc_path))

    fp = fingerprint_docx(str(doc_path))
    texts = [p.text for p in fp.paragraphs]

    assert "Left sidebar content" in texts
    assert "Nested inner cell text" in texts

    # Check that location table_path records hierarchy
    nested_p = next(p for p in fp.paragraphs if "Nested inner cell text" in p.text)
    assert nested_p.location.type == "table_cell"
    assert len(nested_p.location.table_path) >= 4
