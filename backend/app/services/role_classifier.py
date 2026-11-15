"""DOCX Paragraph Role Classifier.
Deterministically classifies paragraphs into name, contact, headline, section_heading,
item_title, item_subtitle, item_meta, bullet, skill_line, body, etc.
Adheres to strict name detection rules (largest font size in first three paragraphs),
phone detection via phonenumbers library / digits, and extended heading dictionary.
"""

import re
import logging
from typing import List, Dict, Optional, Tuple, Any
import phonenumbers

from app.schemas.template import (
    DocxFingerprint,
    ParagraphFingerprint,
    RoleMap,
    ParagraphRoleAssignment,
    ParagraphRoleType,
    SectionHierarchy,
    SectionHierarchyItem,
)

logger = logging.getLogger(__name__)

# Extended Section Heading Dictionary (Change #8)
SECTION_KEYWORDS: Dict[str, List[str]] = {
    "summary": [
        "summary", "professional summary", "profile", "about me", "executive profile",
        "objective", "career objective"
    ],
    "experience": [
        "experience", "work experience", "employment", "work history", "professional experience",
        "career history", "internships", "positions of responsibility"
    ],
    "skills": [
        "skills", "technical skills", "core competencies", "competencies", "technologies",
        "tech stack", "tools", "strengths"
    ],
    "education": [
        "education", "academic background", "academic qualifications", "academic qualification",
        "degrees", "university", "training"
    ],
    "projects": [
        "projects", "key projects", "selected projects", "personal projects", "portfolio",
        "academic projects"
    ],
    "certifications": [
        "certifications", "certificates", "licenses", "credentials"
    ],
    "custom": [
        "extracurricular activities", "extracurricular", "declaration", "personal details",
        "hobbies", "interests", "publications", "patents", "honors", "awards", "volunteer",
        "activities", "affiliations"
    ],
}

DATE_REGEX = re.compile(
    r"\b(19\d\d|20\d\d|present|current|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b",
    re.IGNORECASE,
)
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
URL_REGEX = re.compile(r"(https?://|www\.|linkedin\.com|github\.com|[a-zA-Z0-9-]+\.(com|dev|io|org|net|me))", re.IGNORECASE)


def detect_phone_number(text: str) -> bool:
    """Detects phone numbers using the phonenumbers library or >=10 digits after removing separators."""
    if not text:
        return False

    # 1. phonenumbers library
    try:
        for region in ["US", "IN", "GB", "CA", "AU", "DE", "FR"]:
            if any(phonenumbers.PhoneNumberMatcher(text, region)):
                return True
    except Exception:
        pass

    # 2. Strict >= 10 digits after stripping non-digits
    digits_only = re.sub(r"\D", "", text)
    if len(digits_only) >= 10:
        return True

    return False


def _is_contact_line(text: str) -> bool:
    """Checks if paragraph text contains contact info: email, phone, location, or portfolio links."""
    if EMAIL_REGEX.search(text):
        return True
    if detect_phone_number(text):
        return True
    if URL_REGEX.search(text):
        return True
    if "|" in text and ("@" in text or any(c.isdigit() for c in text)):
        return True
    return False


def detect_section_heading(text: str) -> Optional[Tuple[str, str]]:
    """Checks if text matches any standard or extended section heading keywords."""
    clean = text.strip().lower()
    clean = re.sub(r"^[\d\.\-\s]+", "", clean)
    clean = re.sub(r"[:\-\s]+$", "", clean)

    if len(clean) > 45:
        return None

    for section_type, keywords in SECTION_KEYWORDS.items():
        for kw in keywords:
            if clean == kw or clean.startswith(f"{kw} ") or clean.endswith(f" {kw}"):
                return section_type, text.strip()
    return None


# Backward-compatible alias
_detect_section_heading = detect_section_heading


def _get_max_font_size(p: ParagraphFingerprint) -> float:
    """Gets the maximum font size in a paragraph across runs and resolved formatting."""
    sizes = [r.formatting.font_size_pt for r in p.runs if r.formatting.font_size_pt is not None]
    if p.resolved_formatting and "font_size_pt" in p.resolved_formatting:
        sizes.append(p.resolved_formatting["font_size_pt"])
    return max(sizes) if sizes else 11.0


def classify_paragraphs(fingerprint: DocxFingerprint) -> RoleMap:
    """Classifies paragraphs into structural roles and hierarchy.

    Requires largest font size in first three paragraphs for candidate name.
    """
    paragraphs = fingerprint.paragraphs
    assignments: Dict[int, ParagraphRoleAssignment] = {}
    sections_hierarchy: List[SectionHierarchy] = []
    content_to_paragraphs: Dict[str, List[int]] = {}

    if not paragraphs:
        return RoleMap(paragraph_roles={}, sections_hierarchy=[], content_to_paragraph_indices={})

    # 1. Identify Candidate Name using the strict rule:
    # "The name rule must require the largest font size in the first three paragraphs (not merely bold)."
    first_three_non_empty = [p for p in paragraphs if p.text.strip()][:3]

    name_para_idx: Optional[int] = None
    if first_three_non_empty:
        # Find maximum font size among the first three paragraphs
        max_size_found = -1.0
        best_candidate: Optional[ParagraphFingerprint] = None

        for p in first_three_non_empty:
            text = p.text.strip()
            # Skip pure contact or URL lines
            if EMAIL_REGEX.search(text) or detect_phone_number(text) or URL_REGEX.search(text):
                continue
            if len(text) > 60:
                continue

            sz = _get_max_font_size(p)
            if sz > max_size_found:
                max_size_found = sz
                best_candidate = p

        # If best candidate is found and its size is >= other candidates in the first 3
        if best_candidate is not None:
            name_para_idx = best_candidate.index
            assignments[best_candidate.index] = ParagraphRoleAssignment(
                role="name",
                confidence=0.99,
                rule_matched="largest_font_size_in_first_three_paragraphs",
                section_id="header",
                field="name",
            )
            content_to_paragraphs["header.name"] = [best_candidate.index]

    # 2. Identify Contact and Headline in top region
    for p in first_three_non_empty + paragraphs[3:6]:
        if p.index in assignments:
            continue
        text = p.text.strip()
        if not text:
            continue

        if _is_contact_line(text):
            assignments[p.index] = ParagraphRoleAssignment(
                role="contact",
                confidence=0.98,
                rule_matched="contact_regex_or_phone",
                section_id="header",
                field="contact",
            )
            content_to_paragraphs.setdefault("header.contact", []).append(p.index)
        elif name_para_idx is not None and p.index > name_para_idx and not detect_section_heading(text):
            # Candidate headline
            if len(text) < 70 and not any(p.bullet_info.is_bullet for _ in [1]):
                assignments[p.index] = ParagraphRoleAssignment(
                    role="headline",
                    confidence=0.90,
                    rule_matched="headline_under_name",
                    section_id="header",
                    field="title",
                )
                content_to_paragraphs["header.title"] = [p.index]

    # 3. Main Document Reading-Order Parsing
    current_section: Optional[SectionHierarchy] = None
    current_item: Optional[SectionHierarchyItem] = None
    item_counter = 0

    for p in paragraphs:
        if p.index in assignments:
            continue

        text = p.text.strip()
        if not text:
            assignments[p.index] = ParagraphRoleAssignment(
                role="other",
                confidence=1.0,
                rule_matched="empty_paragraph",
            )
            continue

        # A. Section Heading Check
        heading_match = detect_section_heading(text)
        is_heading_styled = (
            p.has_bottom_border
            or p.has_shading
            or any(r.formatting.bold for r in p.runs)
            or p.style_name.lower().startswith("heading")
            or text.isupper()
        )

        if heading_match and (is_heading_styled or len(text) < 35):
            sec_type, sec_title = heading_match
            sec_id = f"sec-{sec_type}-{len(sections_hierarchy) + 1}"
            current_section = SectionHierarchy(
                section_id=sec_id,
                heading_para_index=p.index,
                type=sec_type,
                title=sec_title,
                items=[],
            )
            sections_hierarchy.append(current_section)
            current_item = None

            assignments[p.index] = ParagraphRoleAssignment(
                role="section_heading",
                confidence=0.98,
                rule_matched="section_heading_extended_dict",
                section_id=sec_id,
                field="title",
            )
            content_to_paragraphs[f"{sec_id}.title"] = [p.index]
            continue

        # If not inside a recognized section yet
        if not current_section:
            assignments[p.index] = ParagraphRoleAssignment(
                role="body",
                confidence=0.6,
                rule_matched="pre_section_body",
            )
            continue

        sec_type = current_section.type
        sec_id = current_section.section_id

        # B. Classification within specific sections
        if sec_type == "skills":
            assignments[p.index] = ParagraphRoleAssignment(
                role="skill_line",
                confidence=0.95,
                rule_matched="skills_section_line",
                section_id=sec_id,
            )
            if not current_item:
                current_item = SectionHierarchyItem(item_id=f"item-{sec_id}-skills")
                current_section.items.append(current_item)
            current_item.body_para_indices.append(p.index)
            content_to_paragraphs.setdefault(f"{sec_id}.skills", []).append(p.index)

        elif sec_type == "summary":
            assignments[p.index] = ParagraphRoleAssignment(
                role="body",
                confidence=0.95,
                rule_matched="summary_section_body",
                section_id=sec_id,
            )
            if not current_item:
                current_item = SectionHierarchyItem(item_id=f"item-{sec_id}-sum")
                current_section.items.append(current_item)
            current_item.body_para_indices.append(p.index)
            content_to_paragraphs.setdefault(f"{sec_id}.summary", []).append(p.index)

        else:
            # Experience, Education, Projects, Custom, Certifications
            # 1. Bullets
            if p.bullet_info.is_bullet or text.startswith(("•", "-", "*", "▪", "◦")):
                bullet_id = f"b-{sec_id}-{p.index}"
                if not current_item:
                    item_counter += 1
                    current_item = SectionHierarchyItem(item_id=f"item-{sec_id}-{item_counter}")
                    current_section.items.append(current_item)

                current_item.bullet_para_indices.append(p.index)
                assignments[p.index] = ParagraphRoleAssignment(
                    role="bullet",
                    confidence=0.96,
                    rule_matched="bullet_property_or_glyph",
                    section_id=sec_id,
                    item_id=current_item.item_id,
                    bullet_id=bullet_id,
                    field="text",
                )
                content_to_paragraphs[f"{sec_id}.{current_item.item_id}.{bullet_id}"] = [p.index]

            # 2. Dates / Meta
            elif (DATE_REGEX.search(text) or len(p.tab_stops) > 0) and len(text) < 70 and not any(r.formatting.bold for r in p.runs[:1]):
                if not current_item:
                    item_counter += 1
                    current_item = SectionHierarchyItem(item_id=f"item-{sec_id}-{item_counter}")
                    current_section.items.append(current_item)

                current_item.meta_para_indices.append(p.index)
                assignments[p.index] = ParagraphRoleAssignment(
                    role="item_meta",
                    confidence=0.94,
                    rule_matched="date_or_tab_meta",
                    section_id=sec_id,
                    item_id=current_item.item_id,
                    field="dateRange",
                )
                content_to_paragraphs.setdefault(f"{sec_id}.{current_item.item_id}.meta", []).append(p.index)

            # 3. Item Title / Subtitle
            elif any(r.formatting.bold for r in p.runs) or len(text) < 80:
                item_counter += 1
                current_item = SectionHierarchyItem(
                    item_id=f"item-{sec_id}-{item_counter}",
                    title_para_index=p.index,
                )
                current_section.items.append(current_item)

                assignments[p.index] = ParagraphRoleAssignment(
                    role="item_title",
                    confidence=0.92,
                    rule_matched="bold_or_short_item_title",
                    section_id=sec_id,
                    item_id=current_item.item_id,
                    field="title",
                )
                content_to_paragraphs[f"{sec_id}.{current_item.item_id}.title"] = [p.index]

            else:
                assignments[p.index] = ParagraphRoleAssignment(
                    role="body",
                    confidence=0.82,
                    rule_matched="general_item_body",
                    section_id=sec_id,
                    item_id=current_item.item_id if current_item else None,
                )

    return RoleMap(
        paragraph_roles=assignments,
        sections_hierarchy=sections_hierarchy,
        content_to_paragraph_indices=content_to_paragraphs,
    )
