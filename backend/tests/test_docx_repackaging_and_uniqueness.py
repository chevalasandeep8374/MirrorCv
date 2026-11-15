"""Tests for DOCX Zip-Level Repackaging, XML ID Uniqueness Scrubbing,
Namespace Preservation, and Structural Integrity.
"""

import os
import hashlib
import zipfile
import pytest
from lxml import etree
from docx import Document

from contracts.models.template_profile import (
    TemplateProfile,
    Slot,
    SlotMap,
    Role,
    SourcePointer,
    PointerType,
    Budgets,
    SchemaVersion,
    SourceType,
    Status,
)
from app.services.change_planner import Operation, OperationType
from app.services.fidelity_writer import write_tailored_docx_repackaged

FIXTURES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "fixtures"))
TMP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "tmp_output"))
os.makedirs(TMP_DIR, exist_ok=True)

SAMPLE_DOCX = os.path.join(FIXTURES_DIR, "sample_single_column.docx")


@pytest.fixture
def sample_profile_and_doc():
    doc = Document(SAMPLE_DOCX)
    slots = []
    slot_map = {}
    for i, p in enumerate(doc.paragraphs):
        sid = f"slot_{i}"
        slots.append(
            Slot(
                slot_id=sid,
                section_id="sec_exp" if i > 1 else "sec_hdr",
                item_id=f"item_{i}",
                bullet_id=f"b_{i}" if i > 1 else None,
                role=Role.bullet if i > 1 else (Role.name if i == 0 else Role.contact),
                max_lines=2,
                max_chars=200,
                font="Calibri",
                size=11.0,
                source_pointer=SourcePointer(
                    pointer_type=PointerType.docx_paragraph,
                    paragraph_index=i,
                ),
                budgets=Budgets(
                    line_width_pt=500.0,
                    max_lines=2,
                    max_chars=200,
                    hard_max_chars=250,
                ),
            )
        )
        slot_map[sid] = SlotMap(
            section_id="sec_exp" if i > 1 else "sec_hdr",
            item_id=f"item_{i}",
            bullet_id=f"b_{i}" if i > 1 else None,
            target_field="text" if i > 1 else "name",
        )

    profile = TemplateProfile(
        schema_version=SchemaVersion.field_1_1_0,
        template_profile_id="tpl_repkg_test",
        resume_id="res_repkg_test",
        version=1,
        source_type=SourceType.uploaded_docx,
        slots=slots,
        slot_map=slot_map,
        fidelity_score=99.0,
        status=Status.ready,
    )
    return profile


def test_repackaging_byte_identity_on_non_document_parts(sample_profile_and_doc):
    """Proves that every non-document file in the zip is SHA-256 byte-identical by construction."""
    out_docx = os.path.join(TMP_DIR, "test_byte_identity.docx")
    ops = [
        Operation(
            op_id="op_1",
            type=OperationType.set_text,
            slot_id="slot_0",
            text="Alex Mercer, Staff Engineer",
        )
    ]

    write_tailored_docx_repackaged(
        template_docx_path=SAMPLE_DOCX,
        operations=ops,
        template_profile=sample_profile_and_doc,
        output_docx_path=out_docx,
    )

    with zipfile.ZipFile(SAMPLE_DOCX, "r") as z_orig, zipfile.ZipFile(out_docx, "r") as z_tailor:
        orig_names = set(z_orig.namelist())
        tailor_names = set(z_tailor.namelist())
        assert orig_names == tailor_names, "Zip file entries must match exactly"

        for name in orig_names:
            if name != "word/document.xml":
                orig_hash = hashlib.sha256(z_orig.read(name)).hexdigest()
                tailor_hash = hashlib.sha256(z_tailor.read(name)).hexdigest()
                assert orig_hash == tailor_hash, f"Part '{name}' was altered during repackaging!"


def test_root_element_namespaces_and_mc_ignorable_preservation(sample_profile_and_doc):
    """Proves that root element namespace declarations and mc:Ignorable attributes are preserved."""
    out_docx = os.path.join(TMP_DIR, "test_namespaces.docx")
    ops = [
        Operation(
            op_id="op_1",
            type=OperationType.set_text,
            slot_id="slot_0",
            text="Alex Mercer, Lead Architect",
        )
    ]

    write_tailored_docx_repackaged(
        template_docx_path=SAMPLE_DOCX,
        operations=ops,
        template_profile=sample_profile_and_doc,
        output_docx_path=out_docx,
    )

    with zipfile.ZipFile(out_docx, "r") as z:
        xml_bytes = z.read("word/document.xml")
        root = etree.fromstring(xml_bytes)

        # Assert root namespaces
        assert "w" in root.nsmap
        assert "mc" in root.nsmap

        # Assert mc:Ignorable attribute
        mc_ns = "http://schemas.openxmlformats.org/markup-compatibility/2006"
        ignorable_val = root.attrib.get(f"{{{mc_ns}}}Ignorable")
        assert ignorable_val is not None, "mc:Ignorable attribute must be preserved on w:document root"
        assert "w14" in ignorable_val


def test_id_uniqueness_on_cloning(sample_profile_and_doc):
    """Proves that cloned slots receive unique w14:paraId, w14:textId, and no collisions exist."""
    out_docx = os.path.join(TMP_DIR, "test_id_uniqueness.docx")
    ops = [
        Operation(
            op_id="op_clone_1",
            type=OperationType.clone_slot,
            prototype_slot_id="slot_2",
            insert_after_slot_id="slot_2",
            text="Cloned Bullet 1: Built real-time analytics engine.",
        ),
        Operation(
            op_id="op_clone_2",
            type=OperationType.clone_slot,
            prototype_slot_id="slot_2",
            insert_after_slot_id="slot_2",
            text="Cloned Bullet 2: Designed distributed consensus cluster.",
        ),
    ]

    write_tailored_docx_repackaged(
        template_docx_path=SAMPLE_DOCX,
        operations=ops,
        template_profile=sample_profile_and_doc,
        output_docx_path=out_docx,
    )

    with zipfile.ZipFile(out_docx, "r") as z:
        xml_bytes = z.read("word/document.xml")
        root = etree.fromstring(xml_bytes)

        w14_ns = "http://schemas.microsoft.com/office/word/2010/wordml"
        w_ns = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

        # Check all paraIds
        para_id_nodes = root.xpath("//*[@w14:paraId]", namespaces={"w14": w14_ns})
        para_ids = [n.attrib[f"{{{w14_ns}}}paraId"] for n in para_id_nodes]
        assert len(para_ids) == len(set(para_ids)), "Duplicate w14:paraId found!"

        # Check all textIds
        text_id_nodes = root.xpath("//*[@w14:textId]", namespaces={"w14": w14_ns})
        text_ids = [n.attrib[f"{{{w14_ns}}}textId"] for n in text_id_nodes]
        assert len(text_ids) == len(set(text_ids)), "Duplicate w14:textId found!"

        # Check all bookmark IDs
        bm_nodes = root.xpath("//*[@w:id]", namespaces={"w": w_ns})
        bm_ids = [n.attrib[f"{{{w_ns}}}id"] for n in bm_nodes]
        assert len(bm_ids) == len(set(bm_ids)), "Duplicate bookmark ID found!"


def test_reorder_and_remove_operations(sample_profile_and_doc):
    """Proves reorder swaps XML element order and remove_slot purges elements cleanly."""
    out_docx = os.path.join(TMP_DIR, "test_reorder_remove.docx")

    # Read original text of slot_2 and slot_3
    orig_doc = Document(SAMPLE_DOCX)
    t2 = orig_doc.paragraphs[2].text
    t3 = orig_doc.paragraphs[3].text
    orig_count = len(orig_doc.paragraphs)

    ops = [
        Operation(
            op_id="op_reorder",
            type=OperationType.reorder,
            new_order=["slot_3", "slot_2"],
        ),
        Operation(
            op_id="op_remove",
            type=OperationType.remove_slot,
            slot_id="slot_4",
        ),
    ]

    write_tailored_docx_repackaged(
        template_docx_path=SAMPLE_DOCX,
        operations=ops,
        template_profile=sample_profile_and_doc,
        output_docx_path=out_docx,
    )

    tailor_doc = Document(out_docx)
    # Total paragraphs should be orig_count - 1
    assert len(tailor_doc.paragraphs) == orig_count - 1

    # In tailor_doc, position 2 should now have t3 and position 3 should have t2
    assert tailor_doc.paragraphs[2].text == t3
    assert tailor_doc.paragraphs[3].text == t2
