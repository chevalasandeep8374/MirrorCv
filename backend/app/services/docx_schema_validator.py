"""ECMA-376 Transitional XML Schema Validator for DOCX word/document.xml.
Validates word/document.xml against the official ECMA-376 / ISO-IEC 29500-4
Transitional WordprocessingML XML schemas.
"""

import os
import io
import zipfile
import logging
from typing import Tuple, List, Union, Optional
import lxml.etree

logger = logging.getLogger(__name__)

SCHEMA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "schemas", "ecma376"))
WML_XSD_PATH = os.path.join(SCHEMA_DIR, "wml.xsd")

_COMPILED_SCHEMA: Optional[lxml.etree.XMLSchema] = None


def get_ecma376_schema() -> lxml.etree.XMLSchema:
    """Returns singleton instance of compiled ECMA-376 XMLSchema."""
    global _COMPILED_SCHEMA
    if _COMPILED_SCHEMA is None:
        if not os.path.exists(WML_XSD_PATH):
            raise FileNotFoundError(f"ECMA-376 schema not found at {WML_XSD_PATH}")
        schema_doc = lxml.etree.parse(WML_XSD_PATH)
        _COMPILED_SCHEMA = lxml.etree.XMLSchema(schema_doc)
        logger.info("Compiled ECMA-376 transitional XMLSchema successfully.")
    return _COMPILED_SCHEMA


def validate_docx_document_xml_xsd(docx_path_or_bytes: Union[str, bytes]) -> Tuple[bool, List[str]]:
    """Validates word/document.xml inside a DOCX file against ECMA-376 schemas.

    Args:
        docx_path_or_bytes: Filepath to DOCX or raw byte content of DOCX archive.

    Returns:
        (is_valid, list_of_error_messages)
    """
    schema = get_ecma376_schema()
    errors: List[str] = []

    try:
        if isinstance(docx_path_or_bytes, bytes):
            zip_file = zipfile.ZipFile(io.BytesIO(docx_path_or_bytes))
        else:
            if not os.path.exists(docx_path_or_bytes):
                return False, [f"File not found: {docx_path_or_bytes}"]
            zip_file = zipfile.ZipFile(docx_path_or_bytes)

        with zip_file as z:
            if "word/document.xml" not in z.namelist():
                return False, ["word/document.xml not found inside DOCX package."]
            doc_xml = z.read("word/document.xml")

        doc_tree = lxml.etree.fromstring(doc_xml)
        is_valid = schema.validate(doc_tree)
        if not is_valid:
            for err in schema.error_log:
                errors.append(f"Line {err.line}: {err.message}")

        return is_valid, errors

    except Exception as exc:
        msg = f"XSD Validation execution error: {exc}"
        logger.error(msg)
        return False, [msg]
