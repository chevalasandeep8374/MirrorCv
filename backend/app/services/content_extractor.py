"""DOCX Resume Content and Style Extractor.
Translates a DocxFingerprint and RoleMap into the frontend editor's ResumeContent
and StyleTokens shapes with stable IDs and safe inline markdown markup.
"""

import re
from typing import Dict, List, Tuple, Optional
from app.schemas.content import (
    ResumeContent,
    HeaderContent,
    ContactLink,
    ResumeSection,
    SectionItem,
    BulletItem,
    SectionType,
)
from app.schemas.style import (
    ResumeStyle,
    PageSize,
    Margins,
    Typography,
    FontSizes,
    Spacing,
    Colors,
    ColumnLayout,
)
from app.schemas.template import DocxFingerprint, RoleMap, ParagraphFingerprint


def _clean_bullet_text(text: str) -> str:
    """Strips leading bullet glyphs from text."""
    return re.sub(r"^[\u2022\u25E6\u25AA\u25AB\u2013\u2014\-*]\s*", "", text).strip()


def convert_runs_to_markdown(p: ParagraphFingerprint) -> str:
    """Converts runs and inline hyperlinks into safe markdown (**bold**, *italic*, [text](url))."""
    if not p.runs:
        return _clean_bullet_text(p.text)

    hyperlink_map = {h["text"].strip(): h["target"] for h in p.hyperlinks if "text" in h and "target" in h}

    parts = []
    for r in p.runs:
        txt = r.text
        if not txt:
            continue

        stripped = txt.strip()
        if stripped in hyperlink_map:
            # Inline link
            target = hyperlink_map[stripped]
            txt = f"[{txt}]({target})"
        else:
            # Check bold & italic
            is_b = bool(r.formatting.bold)
            is_i = bool(r.formatting.italic)

            if is_b and is_i:
                # Keep leading/trailing whitespace outside markdown delimiters
                l_space = " " if txt.startswith(" ") else ""
                r_space = " " if txt.endswith(" ") else ""
                txt = f"{l_space}***{stripped}***{r_space}" if stripped else txt
            elif is_b:
                l_space = " " if txt.startswith(" ") else ""
                r_space = " " if txt.endswith(" ") else ""
                txt = f"{l_space}**{stripped}**{r_space}" if stripped else txt
            elif is_i:
                l_space = " " if txt.startswith(" ") else ""
                r_space = " " if txt.endswith(" ") else ""
                txt = f"{l_space}*{stripped}*{r_space}" if stripped else txt

        parts.append(txt)

    combined = "".join(parts)
    return _clean_bullet_text(combined)


def extract_content_and_style(
    fingerprint: DocxFingerprint,
    role_map: RoleMap,
    template_profile_id: Optional[str] = None,
) -> Tuple[ResumeContent, ResumeStyle, Dict[str, List[int]]]:
    """Builds ResumeContent and ResumeStyle tokens with templateId = 'uploaded:{template_profile_id}'."""
    para_dict = {p.index: p for p in fingerprint.paragraphs}
    roles = role_map.paragraph_roles

    # 1. Build Header Content
    header = HeaderContent()
    name_paras = [idx for idx, r in roles.items() if r.role == "name"]
    if name_paras:
        header.name = para_dict[name_paras[0]].text.strip()

    title_paras = [idx for idx, r in roles.items() if r.role in ("headline", "title")]
    if title_paras:
        header.title = para_dict[title_paras[0]].text.strip()

    contact_paras = [idx for idx, r in roles.items() if r.role == "contact"]
    for c_idx in contact_paras:
        c_text = para_dict[c_idx].text.strip()

        # Extract Email
        email_m = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", c_text)
        if email_m and not header.email:
            header.email = email_m.group(0)

        # Extract Phone
        phone_m = re.search(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", c_text)
        if phone_m and not header.phone:
            header.phone = phone_m.group(0)

        # Extract Location
        loc_m = re.search(r"([A-Z][a-zA-Z\s]+,\s*[A-Z]{2})", c_text)
        if loc_m and not header.location:
            header.location = loc_m.group(1).strip()

        # Extract URLs / Links
        urls = re.findall(r"(https?://\S+|www\.\S+|[a-zA-Z0-9-]+\.(?:com|dev|io|org|net|me)\S*)", c_text)
        for u in urls:
            clean_url = u.strip().rstrip("|,;")
            if not clean_url.startswith("http"):
                clean_url = "https://" + clean_url
            label = "Website"
            if "linkedin" in clean_url:
                label = "LinkedIn"
            elif "github" in clean_url:
                label = "GitHub"

            if not any(l.url == clean_url for l in header.links):
                header.links.append(
                    ContactLink(
                        id=f"link-{len(header.links) + 1}",
                        label=label,
                        url=clean_url,
                    )
                )

    # 2. Build Sections & Items
    sections: List[ResumeSection] = []
    content_to_paragraphs: Dict[str, List[int]] = dict(role_map.content_to_paragraph_indices)

    for sec_h in role_map.sections_hierarchy:
        valid_type: SectionType = (
            sec_h.type if sec_h.type in [
                "summary", "experience", "skills", "education", "projects", "certifications", "custom"
            ] else "custom"
        )
        items_list: List[SectionItem] = []

        if valid_type == "summary":
            sum_texts = []
            for item in sec_h.items:
                for b_idx in item.body_para_indices:
                    sum_texts.append(convert_runs_to_markdown(para_dict[b_idx]))

            full_sum = " ".join(sum_texts)
            item_id = f"item-{sec_h.section_id}-1"
            bullet_id = f"b-{sec_h.section_id}-1"
            items_list.append(
                SectionItem(
                    id=item_id,
                    bullets=[BulletItem(id=bullet_id, text=full_sum)],
                )
            )
            content_to_paragraphs[f"{sec_h.section_id}.{item_id}.{bullet_id}"] = [
                idx for item in sec_h.items for idx in item.body_para_indices
            ]

        elif valid_type == "skills":
            for idx, item in enumerate(sec_h.items):
                for p_idx in item.body_para_indices:
                    raw_text = para_dict[p_idx].text.strip()
                    parts = raw_text.split(":", 1)
                    if len(parts) == 2:
                        cat_title = parts[0].strip()
                        cat_skills = parts[1].strip()
                    else:
                        cat_title = f"Skill Group {idx + 1}"
                        cat_skills = raw_text

                    sk_item_id = f"item-{sec_h.section_id}-{p_idx}"
                    b_id = f"b-{sec_h.section_id}-{p_idx}"
                    items_list.append(
                        SectionItem(
                            id=sk_item_id,
                            title=cat_title,
                            bullets=[BulletItem(id=b_id, text=_clean_bullet_text(cat_skills))],
                        )
                    )
                    content_to_paragraphs[f"{sec_h.section_id}.{sk_item_id}.{b_id}"] = [p_idx]

        else:
            # Experience, Education, Projects, Custom, Certifications
            for item_h in sec_h.items:
                title = ""
                subtitle = ""
                date_range = ""
                location = ""

                if item_h.title_para_index is not None and item_h.title_para_index in para_dict:
                    raw_title = para_dict[item_h.title_para_index].text.strip()
                    if "—" in raw_title:
                        t_parts = raw_title.split("—", 1)
                        title = t_parts[0].strip()
                        subtitle = t_parts[1].strip()
                    elif "|" in raw_title:
                        t_parts = raw_title.split("|", 1)
                        title = t_parts[0].strip()
                        subtitle = t_parts[1].strip()
                    else:
                        title = raw_title

                if item_h.subtitle_para_index is not None and item_h.subtitle_para_index in para_dict:
                    subtitle = para_dict[item_h.subtitle_para_index].text.strip()

                if item_h.meta_para_indices:
                    for m_idx in item_h.meta_para_indices:
                        m_txt = para_dict[m_idx].text.strip()
                        if "|" in m_txt:
                            m_parts = m_txt.split("|", 1)
                            date_range = m_parts[0].strip()
                            location = m_parts[1].strip()
                        else:
                            date_range = m_txt

                # Bullets with safe markdown conversion
                bullets = []
                for b_idx in item_h.bullet_para_indices:
                    b_md = convert_runs_to_markdown(para_dict[b_idx])
                    b_id = f"b-{sec_h.section_id}-{b_idx}"
                    bullets.append(BulletItem(id=b_id, text=b_md))
                    content_to_paragraphs[f"{sec_h.section_id}.{item_h.item_id}.{b_id}"] = [b_idx]

                items_list.append(
                    SectionItem(
                        id=item_h.item_id,
                        title=title,
                        subtitle=subtitle,
                        dateRange=date_range,
                        location=location,
                        bullets=bullets,
                    )
                )

        sections.append(
            ResumeSection(
                id=sec_h.section_id,
                type=valid_type,
                title=sec_h.title,
                visible=True,
                items=items_list,
            )
        )

    content = ResumeContent(header=header, sections=sections)

    # 3. Build Style Tokens
    meta = fingerprint.document_metadata
    page_size: PageSize = "A4" if meta.page_size.name == "A4" else "Letter"

    margins = Margins(
        top=round(meta.margins.top_pt, 1),
        bottom=round(meta.margins.bottom_pt, 1),
        left=round(meta.margins.left_pt, 1),
        right=round(meta.margins.right_pt, 1),
        unit="pt",
    )

    body_fonts: Dict[str, int] = {}
    heading_fonts: Dict[str, int] = {}
    accent_colors: Dict[str, int] = {}

    for p in fingerprint.paragraphs:
        r_role = roles.get(p.index)
        for run in p.runs:
            f_fam = run.formatting.font_family or "Calibri"
            f_col = run.formatting.color_hex

            if r_role and r_role.role == "section_heading":
                heading_fonts[f_fam] = heading_fonts.get(f_fam, 0) + 1
                if f_col and f_col not in ("#000000", "#111827", "#1f2937"):
                    accent_colors[f_col] = accent_colors.get(f_col, 0) + 2
            else:
                body_fonts[f_fam] = body_fonts.get(f_fam, 0) + 1

    base_font = max(body_fonts, key=body_fonts.get) if body_fonts else "Calibri"
    heading_font = max(heading_fonts, key=heading_fonts.get) if heading_fonts else base_font
    accent_color = max(accent_colors, key=accent_colors.get) if accent_colors else "#2563eb"

    name_size = 22.0
    for idx, r in roles.items():
        if r.role == "name":
            sizes = [run.formatting.font_size_pt for run in para_dict[idx].runs if run.formatting.font_size_pt]
            if sizes:
                name_size = round(max(sizes), 1)

    heading_size = 12.5
    for idx, r in roles.items():
        if r.role == "section_heading":
            sizes = [run.formatting.font_size_pt for run in para_dict[idx].runs if run.formatting.font_size_pt]
            if sizes:
                heading_size = round(max(sizes), 1)
                break

    layout_type = "single"
    sidebar_ids: List[str] = []
    main_ids: List[str] = []
    sidebar_width = 32.0

    if meta.total_tables > 0:
        table_cells = [p for p in fingerprint.paragraphs if p.location.type == "table_cell"]
        if table_cells:
            layout_type = "sidebar_left"
            col_0_secs = {
                roles[p.index].section_id
                for p in table_cells
                if p.location.col_index == 0 and p.index in roles and roles[p.index].section_id
            }
            col_1_secs = {
                roles[p.index].section_id
                for p in table_cells
                if p.location.col_index == 1 and p.index in roles and roles[p.index].section_id
            }
            sidebar_ids = list(col_0_secs)
            main_ids = list(col_1_secs)

    if not main_ids:
        main_ids = [s.id for s in sections]

    template_id_str = f"uploaded:{template_profile_id}" if template_profile_id else "extracted-template"

    style = ResumeStyle(
        templateId=template_id_str,
        pageSize=page_size,
        margins=margins,
        typography=Typography(
            baseFontFamily=base_font,
            headingFontFamily=heading_font,
            fontSizes=FontSizes(
                name=name_size,
                headerTitle=11.0,
                contact=9.0,
                sectionHeading=heading_size,
                itemTitle=10.5,
                itemSubtitle=9.5,
                body=9.5,
                meta=8.5,
                unit="pt",
            ),
            lineHeight=1.4,
        ),
        spacing=Spacing(
            sectionSpacing=14.0,
            itemSpacing=8.0,
            bulletSpacing=3.0,
            headerBottomSpacing=16.0,
            unit="pt",
        ),
        colors=Colors(
            accent=accent_color,
            text="#111827",
            muted="#4b5563",
            background="#ffffff",
            sidebarBackground="#f8fafc",
            divider="#e5e7eb",
        ),
        bulletStyle="disc",
        headingStyle="bar" if layout_type == "single" else "plain",
        layout=ColumnLayout(
            type=layout_type,
            sidebarWidthPercent=sidebar_width,
            sidebarSectionIds=sidebar_ids,
            mainSectionIds=main_ids,
        ),
    )

    return content, style, content_to_paragraphs
