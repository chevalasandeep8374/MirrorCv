import os
import pytest
from app.services.docx_fingerprint import fingerprint_docx
from app.services.role_classifier import classify_paragraphs
from app.services.docx_slot_builder import build_template_profile
from app.services.content_extractor import extract_content_and_style
from contracts.models.template_profile import TemplateProfile

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


def test_build_template_profile_single_column():
    docx_path = os.path.join(FIXTURES_DIR, "sample_single_column.docx")
    assert os.path.exists(docx_path)

    fp = fingerprint_docx(docx_path)
    role_map = classify_paragraphs(fp)

    profile_id = "test-prof-123"
    profile = build_template_profile(
        docx_path=docx_path,
        fingerprint=fp,
        role_map=role_map,
        template_profile_id=profile_id,
        resume_id="res-456",
        page_count=1,
    )

    # 1. Check top-level contract compliance
    assert isinstance(profile, TemplateProfile)
    assert profile.template_profile_id == profile_id
    assert profile.resume_id == "res-456"
    assert profile.schema_version.value in ("1.1.0", "1.0.0")
    assert profile.source_type.value == "uploaded_docx"
    assert profile.page_count == 1
    assert profile.fidelity_score == 100.0

    # 2. Check slots
    assert len(profile.slots) == len(fp.paragraphs)
    name_slot = next(s for s in profile.slots if s.role.value == "name")
    assert "header.name" in name_slot.binds
    assert name_slot.font in ("Calibri", "Arial", "Carlito", "Liberation Sans")
    assert name_slot.budgets.max_chars > 0
    assert name_slot.budgets.line_width_pt > 0

    # Check bullet slot
    bullet_slot = next(s for s in profile.slots if s.role.value == "bullet")
    assert bullet_slot.is_clonable is True
    assert bullet_slot.bullet_id is not None
    assert bullet_slot.section_id is not None

    # 3. Check item blocks
    assert len(profile.item_blocks) >= 1
    first_block = profile.item_blocks[0]
    assert first_block.item_block_id.startswith("block_")
    exp_block = next(b for b in profile.item_blocks if b.bullet_slot_ids)
    assert len(exp_block.bullet_slot_ids) >= 1

    # 4. Check slot map
    assert len(profile.slot_map) == len(profile.slots)
    assert "slot_0" in profile.slot_map

    # 5. Check font report
    assert len(profile.font_report) >= 1
    assert all(0.0 <= f.confidence <= 1.0 for f in profile.font_report)
    assert all(f.original_name for f in profile.font_report)


def test_extract_content_and_style_with_template_id():
    docx_path = os.path.join(FIXTURES_DIR, "sample_single_column.docx")
    fp = fingerprint_docx(docx_path)
    role_map = classify_paragraphs(fp)

    profile_id = "test-prof-789"
    content, style, content_to_paras = extract_content_and_style(
        fingerprint=fp,
        role_map=role_map,
        template_profile_id=profile_id,
    )

    # Verify templateId format
    assert style.templateId == f"uploaded:{profile_id}"

    # Verify content extraction
    assert content.header.name == "Alex Mercer"
    assert "alex.mercer" in content.header.email
    assert len(content.sections) >= 3

    # Verify bullets are extracted
    exp_sec = next(s for s in content.sections if s.type == "experience")
    assert len(exp_sec.items) >= 1
    assert len(exp_sec.items[0].bullets) >= 3
