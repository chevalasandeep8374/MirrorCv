"""ECMA-376 Transitional XML Schema Validation Test Suite (Phase E3 Mandate 5).
Validates word/document.xml against official ECMA-376 / ISO-IEC 29500-4 schemas across:
1. Standard template fixtures
2. Composed DOCX with cloned blocks
3. Composed DOCX with reordered paragraphs
4. Deliberately corrupted XML schemas to prove the validator fails closed
"""

import os
import io
import copy
import zipfile
import pytest
from docx import Document

from app.services.docx_schema_validator import validate_docx_document_xml_xsd
from app.services.docx_fingerprint import fingerprint_docx
from app.services.role_classifier import classify_paragraphs
from app.services.docx_slot_builder import build_template_profile
from app.services.fidelity_writer import write_tailored_docx_repackaged

FIXTURES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "fixtures"))


def test_standard_fixtures_ecma376_validity():
    """All standard template fixtures must strictly validate against ECMA-376 schemas."""
    fixture_files = [
        "sample_single_column.docx",
        "sample_table_two_column.docx",
        "sample_multi_page.docx",
        "sample_nested_tables.docx",
    ]
    for fn in fixture_files:
        path = os.path.join(FIXTURES_DIR, fn)
        if os.path.exists(path):
            is_valid, errors = validate_docx_document_xml_xsd(path)
            assert is_valid is True, f"Fixture {fn} failed ECMA-376 XSD validation: {errors}"


def test_composition_with_cloning_ecma376_validity(tmp_path):
    """DOCX output with cloned blocks must strictly validate against ECMA-376 schemas."""
    docx_path = os.path.join(FIXTURES_DIR, "sample_single_column.docx")
    fp = fingerprint_docx(docx_path)
    role_map = classify_paragraphs(fp)
    profile = build_template_profile(docx_path, fp, role_map)

    out_docx = os.path.join(str(tmp_path), "cloned_output.docx")

    bullet_slot = next(s for s in profile.slots if s.role.value == "bullet")
    operations = [
        {
            "type": "clone_slot",
            "prototype_slot_id": bullet_slot.slot_id,
            "anchor_slot_id": bullet_slot.slot_id,
            "text": "Engineered event-driven distributed ingestion pipeline with Kafka and ClickHouse.",
        }
    ]

    write_tailored_docx_repackaged(
        template_docx_path=docx_path,
        template_profile=profile,
        operations=operations,
        output_docx_path=out_docx,
    )

    assert os.path.exists(out_docx)
    is_valid, errors = validate_docx_document_xml_xsd(out_docx)
    assert is_valid is True, f"Cloned DOCX failed ECMA-376 XSD validation: {errors}"


def test_composition_with_reorder_ecma376_validity(tmp_path):
    """DOCX output with reordered paragraphs must strictly validate against ECMA-376 schemas."""
    docx_path = os.path.join(FIXTURES_DIR, "sample_single_column.docx")
    fp = fingerprint_docx(docx_path)
    role_map = classify_paragraphs(fp)
    profile = build_template_profile(docx_path, fp, role_map)

    out_docx = os.path.join(str(tmp_path), "reordered_output.docx")

    bullet_slots = [s for s in profile.slots if s.role.value == "bullet"]
    assert len(bullet_slots) >= 2

    # Swap first two bullets
    reordered_ids = [bullet_slots[1].slot_id, bullet_slots[0].slot_id]
    operations = [
        {
            "type": "reorder",
            "new_order": reordered_ids,
        }
    ]

    write_tailored_docx_repackaged(
        template_docx_path=docx_path,
        template_profile=profile,
        operations=operations,
        output_docx_path=out_docx,
    )

    assert os.path.exists(out_docx)
    is_valid, errors = validate_docx_document_xml_xsd(out_docx)
    assert is_valid is True, f"Reordered DOCX failed ECMA-376 XSD validation: {errors}"


def test_validator_fails_closed_on_schema_violations(tmp_path):
    """Demonstrates that validate_docx_document_xml_xsd strictly detects and flags schema violations."""
    docx_path = os.path.join(FIXTURES_DIR, "sample_single_column.docx")
    corrupted_docx = os.path.join(str(tmp_path), "corrupted_schema.docx")

    with zipfile.ZipFile(docx_path, "r") as zin:
        with zipfile.ZipFile(corrupted_docx, "w") as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename == "word/document.xml":
                    # Inject an illegal XML element not permitted in CT_Body
                    data = data.replace(b"<w:body>", b"<w:body><w:illegalCustomTagNotAllowedInWml>corrupted</w:illegalCustomTagNotAllowedInWml>")
                zout.writestr(item, data)

    assert os.path.exists(corrupted_docx)
    is_valid, errors = validate_docx_document_xml_xsd(corrupted_docx)
    assert is_valid is False, "Validator must fail closed on schema violations"
    assert len(errors) > 0, "Validator must report descriptive schema error messages"
    assert any("illegalCustomTagNotAllowedInWml" in err or "element" in err.lower() for err in errors)
