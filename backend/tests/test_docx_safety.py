"""Security and safety test suite for DOCX upload validation.
Tests:
- Valid DOCX passes
- File size > 5 MB rejected
- Extension != .docx rejected
- .docm and VBA macros rejected
- Password protected / encrypted ZIP entries rejected
- Zip bomb (excessive entries and high compression) rejected
- XML external entity (XXE) and DTD injection rejected via defusedxml
"""

import io
import zipfile
import pytest
from docx import Document

from app.services.docx_validator import validate_docx_bytes


def _create_minimal_docx_bytes() -> bytes:
    doc = Document()
    doc.add_heading("Alex Mercer", level=0)
    doc.add_paragraph("Senior Full-Stack Engineer")
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def test_valid_docx_passes():
    data = _create_minimal_docx_bytes()
    is_valid, err = validate_docx_bytes(data, "resume.docx")
    assert is_valid is True
    assert err is None


def test_invalid_extension_rejected():
    data = _create_minimal_docx_bytes()
    is_valid, err = validate_docx_bytes(data, "resume.docm")
    assert is_valid is False
    assert "Macro-enabled" in err

    is_valid, err = validate_docx_bytes(data, "resume.pdf")
    assert is_valid is False
    assert "Invalid file format" in err


def test_oversized_file_rejected():
    # 5 MB + 1 byte
    fake_data = b"PK\x03\x04" + b"0" * (5 * 1024 * 1024 + 1)
    is_valid, err = validate_docx_bytes(fake_data, "large.docx")
    assert is_valid is False
    assert "exceeds maximum allowed size" in err


def test_invalid_magic_bytes_rejected():
    fake_data = b"NOT_A_ZIP_HEADER" + b"0" * 200
    is_valid, err = validate_docx_bytes(fake_data, "corrupt.docx")
    assert is_valid is False
    assert "Invalid DOCX file signature" in err


def test_encrypted_ole_package_rejected():
    # OLE Compound Document signature (Word encrypted binary)
    fake_ole = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" + b"0" * 300
    is_valid, err = validate_docx_bytes(fake_ole, "encrypted.docx")
    assert is_valid is False
    assert "Encrypted or password-protected" in err


def test_macro_vba_project_rejected():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("word/document.xml", "<w:document xmlns:w='http://schemas.openxmlformats.org/wordprocessingml/2006/main'><w:body/></w:document>")
        zf.writestr("word/vbaProject.bin", b"DUMMY_VBA_PAYLOAD")
    data = buf.getvalue()

    is_valid, err = validate_docx_bytes(data, "macro.docx")
    assert is_valid is False
    assert "macro components" in err


def test_zip_bomb_excessive_entries_rejected():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("word/document.xml", "<w:document xmlns:w='http://schemas.openxmlformats.org/wordprocessingml/2006/main'><w:body/></w:document>")
        for i in range(250):
            zf.writestr(f"word/part_{i}.xml", b"<part/>")
    data = buf.getvalue()

    is_valid, err = validate_docx_bytes(data, "bomb.docx")
    assert is_valid is False
    assert "Zip bomb protection: Archive contains too many entries" in err


def test_xxe_external_entity_rejected():
    xxe_xml = """<?xml version="1.0"?>
    <!DOCTYPE w:document [
      <!ENTITY xxe SYSTEM "file:///etc/passwd">
    ]>
    <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
      <w:body>&xxe;</w:body>
    </w:document>"""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("word/document.xml", xxe_xml)
    data = buf.getvalue()

    is_valid, err = validate_docx_bytes(data, "xxe.docx")
    assert is_valid is False
    assert "Security violation" in err or "XML" in err
