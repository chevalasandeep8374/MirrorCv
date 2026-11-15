"""DOCX Upload Validator and Security Guard for MirrorCV.
Enforces:
- File magic bytes (ZIP + word/document.xml)
- Size limits (max 5 MB upload)
- Zip-bomb defense (uncompressed size <= 50 MB, entry count <= 200, ratio <= 100:1)
- Rejection of .docm, VBA macros (vbaProject.bin), and encrypted/password-protected files
- Hardened XML parsing using defusedxml (rejects DTDs and external entities)
"""

import io
import zipfile
import logging
from typing import Tuple, List, Optional
import defusedxml.minidom
from xml.etree import ElementTree as ET

logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
MAX_UNCOMPRESSED_SIZE = 50 * 1024 * 1024  # 50 MB
MAX_ENTRY_COUNT = 200
MAX_COMPRESSION_RATIO = 100

MAGIC_ZIP_HEADER = b"PK\x03\x04"
MAGIC_EMPTY_ZIP = b"PK\x05\x06"
MAGIC_SPANNED_ZIP = b"PK\x07\x08"


class DocxValidationError(Exception):
    """Raised when an uploaded DOCX fails safety or structure checks."""
    pass


def validate_docx_bytes(data: bytes, filename: str = "resume.docx") -> Tuple[bool, Optional[str]]:
    """Validates uploaded raw bytes against all security constraints.

    Returns (is_valid, error_message).
    """
    # 1. Filename & Extension Check
    fn_lower = filename.lower()
    if fn_lower.endswith(".docm"):
        return False, "Macro-enabled Word files (.docm) are not supported for security reasons."
    if not fn_lower.endswith(".docx"):
        return False, "Invalid file format. Only Microsoft Word (.docx) documents are supported."

    # 2. File Size Limit
    if len(data) > MAX_FILE_SIZE:
        return False, f"File exceeds maximum allowed size of 5 MB ({len(data)} bytes)."
    if len(data) < 100:
        return False, "File is too small or corrupted to be a valid DOCX document."

    # 3. Magic Bytes Check
    if not (data.startswith(MAGIC_ZIP_HEADER) or data.startswith(MAGIC_EMPTY_ZIP) or data.startswith(MAGIC_SPANNED_ZIP)):
        # Check if it's an encrypted OLE package
        if data.startswith(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"):
            return False, "Encrypted or password-protected DOCX files are not supported. Please remove password protection and try again."
        return False, "Invalid DOCX file signature. File does not appear to be a valid Office Open XML archive."

    # 4. Zip Archive & Zip-Bomb Guards
    try:
        zip_buffer = io.BytesIO(data)
        with zipfile.ZipFile(zip_buffer, "r") as zf:
            infolist = zf.infolist()

            if len(infolist) > MAX_ENTRY_COUNT:
                return False, f"Zip bomb protection: Archive contains too many entries ({len(infolist)} > {MAX_ENTRY_COUNT})."

            total_uncompressed = 0
            has_document_xml = False

            for info in infolist:
                # Check for password encryption flag (bit 0 of flag_bits)
                if info.flag_bits & 0x1:
                    return False, "Encrypted or password-protected DOCX files are not supported. Please remove password protection and try again."

                # Macro & VBA checks
                name_lower = info.filename.lower()
                if "vbaproject.bin" in name_lower or "vbadata.xml" in name_lower or name_lower.endswith(".vba"):
                    return False, "Document contains macro components (VBA), which are forbidden for security reasons."

                total_uncompressed += info.file_size
                if total_uncompressed > MAX_UNCOMPRESSED_SIZE:
                    return False, f"Zip bomb protection: Uncompressed size exceeds limit ({total_uncompressed} > {MAX_UNCOMPRESSED_SIZE})."

                # Per-entry compression ratio check
                if info.compress_size > 0:
                    ratio = info.file_size / info.compress_size
                    if ratio > MAX_COMPRESSION_RATIO and info.file_size > 500_000:
                        return False, f"Zip bomb protection: Suspicious compression ratio detected on entry '{info.filename}'."

                if info.filename == "word/document.xml":
                    has_document_xml = True

            if not has_document_xml:
                return False, "Invalid DOCX package: missing 'word/document.xml'."

            # 5. Hardened XML Parsing of word/document.xml using defusedxml
            try:
                doc_xml_bytes = zf.read("word/document.xml")
                # Parse with defusedxml to verify no XXE / DTD expansion attacks
                defusedxml.minidom.parseString(doc_xml_bytes)
            except Exception as xml_err:
                logger.warning(f"defusedxml rejected document.xml: {xml_err}")
                return False, f"Security violation or corrupted XML in document: {str(xml_err)}"

            # Also check styles.xml if present
            if "word/styles.xml" in zf.namelist():
                try:
                    styles_bytes = zf.read("word/styles.xml")
                    defusedxml.minidom.parseString(styles_bytes)
                except Exception as xml_err:
                    return False, f"Security violation or corrupted XML in styles: {str(xml_err)}"

    except zipfile.BadZipFile:
        return False, "The uploaded file is not a valid or readable ZIP archive."
    except Exception as exc:
        return False, f"Failed to validate DOCX package: {str(exc)}"

    return True, None
