import re
from typing import List, Dict, Optional, Tuple
from app.schemas.template import (
    DocxFingerprint,
    ParagraphFingerprint,
    RoleMap,
    ParagraphRoleAssignment,
    ParagraphRoleType,
    SectionHierarchy,
    SectionHierarchyItem,
)

# Common Section Heading Keywords
SECTION_KEYWORDS: Dict[str, List[str]] = {
    "summary": ["summary", "professional summary", "profile", "about me", "executive profile", "objective"],
    "experience": ["experience", "work experience", "employment", "work history", "professional experience", "career history"],
    "skills": ["skills", "technical skills", "core competencies", "competencies", "technologies", "tech stack", "tools"],
    "education": ["education", "academic background", "academic qualifications", "degrees", "university"],
    "projects": ["projects", "key projects", "selected projects", "personal projects", "portfolio"],
    "certifications": ["certifications", "certificates", "licenses", "credentials"],
    "custom": ["publications", "patents", "honors", "awards", "volunteer", "activities", "affiliations"],
}

DATE_REGEX = re.compile(
    r"\b(19\d\d|20\d\d|present|current|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b",
    re.IGNORECASE,
)
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_REGEX = re.compile(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}")
URL_REGEX = re.compile(r"(https?://|www\.|linkedin\.com|github\.com|[a-zA-Z0-9-]+\.(com|dev|io|org|net|me))", re.IGNORECASE)


def _detect_section_heading(text: str) -> Optional[Tuple[str, str]]:
    """Checks if text matches any standard section heading keywords."""
    clean = text.strip().lower()
    # Remove leading numbering or trailing punctuation (e.g. "1. EXPERIENCE:" -> "experience")
    clean = re.sub(r"^[\d\.\-\s]+", "", clean)
    clean = re.sub(r"[:\-\s]+$", "", clean)

    if len(clean) > 40:
        return None

    for section_type, keywords in SECTION_KEYWORDS.items():
        for kw in keywords:
            if clean == kw or clean.startswith(f"{kw} ") or clean.endswith(f" {kw}"):
                return section_type, text.strip()
    return None


def classify_paragraphs(fingerprint: DocxFingerprint) -> RoleMap:
    """Labels every paragraph with a role using hierarchical heuristics and structural cues."""
    paragraphs = fingerprint.paragraphs
    assignments: Dict[int, ParagraphRoleAssignment] = {}
    sections_hierarchy: List[SectionHierarchy] = []
    content_to_paragraphs: Dict[str, List[int]] = {}

    if not paragraphs:
        return RoleMap(paragraph_roles={}, sections_hierarchy=[], content_to_paragraph_indices={})

    # 1. Detect Name & Contact in the top region (first 4 paragraphs or text boxes)
    name_found = False
    name_idx = None
    header_indices = set()

    for p in paragraphs[:5]:
        text = p.text.strip()
        if not text:
            continue

        # Contact line
        has_contact = bool(
            EMAIL_REGEX.search(text)
            or PHONE_REGEX.search(text)
            or URL_REGEX.search(text)
            or ("|" in text and "@" in text)
        )
        if has_contact:
            assignments[p.index] = ParagraphRoleAssignment(
                role="contact",
                confidence=0.98,
                rule_matched="contact_regex_email_phone_url",
                section_id="header",
                field="contact",
            )
            header_indices.add(p.index)
            content_to_paragraphs.setdefault("header.contact", []).append(p.index)
            continue

        # Check Name (First non-contact paragraph with bold, large font, or title style)
        if not name_found:
            is_bold = any(r.formatting.bold for r in p.runs)
            max_size = max((r.formatting.font_size_pt or 10.0 for r in p.runs), default=10.0)
            if (p.alignment == "center" or is_bold or max_size >= 14.0 or p.style_name.lower() in ("title", "heading 1")) and len(text) < 50:
                name_found = True
                name_idx = p.index
                assignments[p.index] = ParagraphRoleAssignment(
                    role="name",
                    confidence=0.99,
                    rule_matched="top_large_bold_name",
                    section_id="header",
                    field="name",
                )
                header_indices.add(p.index)
                content_to_paragraphs["header.name"] = [p.index]
                continue

        # Target Title / Headline (under name before first section)
        if name_found and p.index > (name_idx or 0) and not _detect_section_heading(text):
            if len(text) < 60 and (p.runs and p.runs[0].formatting.bold or "engineer" in text.lower() or "developer" in text.lower() or "manager" in text.lower()):
                assignments[p.index] = ParagraphRoleAssignment(
                    role="title",
                    confidence=0.88,
                    rule_matched="headline_under_name",
                    section_id="header",
                    field="title",
                )
                header_indices.add(p.index)
                content_to_paragraphs["header.title"] = [p.index]
                continue

    # 2. Iterate through all paragraphs and track section context
    current_section: Optional[SectionHierarchy] = None
    current_item: Optional[SectionHierarchyItem] = None
    item_counter = 0

    for p in paragraphs:
        if p.index in assignments:
            continue  # Already assigned in header pass

        text = p.text.strip()
        if not text:
            assignments[p.index] = ParagraphRoleAssignment(role="other", confidence=1.0, rule_matched="empty_paragraph")
            continue

        # A. Check Section Heading
        heading_match = _detect_section_heading(text)
        is_bold_or_styled = any(r.formatting.bold for r in p.runs) or p.style_name.lower().startswith("heading")

        if heading_match and is_bold_or_styled:
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
                rule_matched="section_heading_keyword",
                section_id=sec_id,
                field="title",
            )
            content_to_paragraphs[f"{sec_id}.title"] = [p.index]
            continue

        # If not inside a recognized section yet, check if it's text box or body
        if not current_section:
            assignments[p.index] = ParagraphRoleAssignment(
                role="body",
                confidence=0.6,
                rule_matched="pre_section_body",
            )
            continue

        sec_type = current_section.type
        sec_id = current_section.section_id

        # B. Classification within specific section types
        if sec_type == "skills":
            # In skills, lines are typically skill_line
            assignments[p.index] = ParagraphRoleAssignment(
                role="skill_line",
                confidence=0.92,
                rule_matched="skills_section_line",
                section_id=sec_id,
            )
            if not current_item:
                current_item = SectionHierarchyItem(item_id=f"item-{sec_id}-skills")
                current_section.items.append(current_item)
            current_item.body_para_indices.append(p.index)
            content_to_paragraphs.setdefault(f"{sec_id}.skills", []).append(p.index)

        elif sec_type == "summary":
            # Narrative summary body
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
            # Experience, Education, Projects, Certifications
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

            # 2. Item Meta (Dates / Location)
            elif DATE_REGEX.search(text) and len(text) < 70 and not any(r.formatting.bold for r in p.runs[:1]):
                if not current_item:
                    item_counter += 1
                    current_item = SectionHierarchyItem(item_id=f"item-{sec_id}-{item_counter}")
                    current_section.items.append(current_item)

                current_item.meta_para_indices.append(p.index)
                assignments[p.index] = ParagraphRoleAssignment(
                    role="item_meta",
                    confidence=0.94,
                    rule_matched="date_or_location_regex",
                    section_id=sec_id,
                    item_id=current_item.item_id,
                    field="dateRange",
                )
                content_to_paragraphs.setdefault(f"{sec_id}.{current_item.item_id}.meta", []).append(p.index)

            # 3. Item Title / Role Header
            elif any(r.formatting.bold for r in p.runs) or len(text) < 80:
                item_counter += 1
                current_item = SectionHierarchyItem(
                    item_id=f"item-{sec_id}-{item_counter}",
                    title_para_index=p.index,
                )
                current_section.items.append(current_item)

                assignments[p.index] = ParagraphRoleAssignment(
                    role="item_title",
                    confidence=0.91,
                    rule_matched="bold_or_short_item_header",
                    section_id=sec_id,
                    item_id=current_item.item_id,
                    field="title",
                )
                content_to_paragraphs[f"{sec_id}.{current_item.item_id}.title"] = [p.index]

            else:
                # Narrative body under item
                assignments[p.index] = ParagraphRoleAssignment(
                    role="body",
                    confidence=0.8,
                    rule_matched="general_item_body",
                    section_id=sec_id,
                    item_id=current_item.item_id if current_item else None,
                )

    return RoleMap(
        paragraph_roles=assignments,
        sections_hierarchy=sections_hierarchy,
        content_to_paragraph_indices=content_to_paragraphs,
    )
