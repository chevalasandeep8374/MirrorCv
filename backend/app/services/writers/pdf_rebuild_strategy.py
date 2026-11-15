import os
import base64
import fitz
from typing import Dict, Any, Optional, List
from playwright.sync_api import sync_playwright
from app.schemas.content import ResumeContent
from app.schemas.style import ResumeStyle
from app.schemas.pdf_template import (
    PdfLayout,
    FontResolutionTable,
    FidelityScoreBreakdown,
)
from app.services.writers.base_strategy import WriterStrategy
from app.services.pdf_fidelity_scorer import calculate_fidelity_score


def _generate_rebuild_html(
    content: ResumeContent,
    style: Optional[ResumeStyle] = None,
    layout: Optional[PdfLayout] = None,
    embedded_images: Optional[List[str]] = None,
) -> str:
    """Constructs a self-contained HTML document styled identically to MirrorCV's <ResumeDocument> component."""
    # Margins and dimensions in pt (A4: 595.3 x 841.9 pt)
    page_w = 595.3
    page_h = 841.9
    margin_top = 28.0
    margin_bottom = 28.0
    margin_left = 36.0
    margin_right = 36.0

    if style and style.margins:
        margin_top = min(36.0, style.margins.top)
        margin_bottom = min(36.0, style.margins.bottom)
        margin_left = min(40.0, style.margins.left)
        margin_right = min(40.0, style.margins.right)

    # Layout type (single-column vs sidebar)
    is_two_col = False
    sidebar_w_percent = 32
    is_sidebar_left = True
    sidebar_bg = "#1e2e47"

    if layout:
        sb_cols = [c for c in layout.columns if c.type == "sidebar"]
        if sb_cols:
            is_two_col = True
            sb = sb_cols[0]
            sidebar_w_percent = int(round((sb.width_pt / max(1, page_w)) * 100))
            if sb.bbox[0] > (page_w / 2):
                is_sidebar_left = False

            # Check vector background color
            for draw in layout.vector_drawings:
                if draw.type == "rect" and draw.fill_color:
                    sidebar_bg = draw.fill_color
                    break

    # Build Header HTML
    header = content.header
    contact_parts = []
    if header.email:
        contact_parts.append(f'<span>{header.email}</span>')
    if header.phone:
        contact_parts.append(f'<span>{header.phone}</span>')
    if header.location:
        contact_parts.append(f'<span>{header.location}</span>')
    for link in header.links:
        contact_parts.append(f'<a href="{link.url}" style="color: inherit; text-decoration: none;">{link.url}</a>')

    contact_html = '  |  '.join(contact_parts)

    avatar_html = ""
    if embedded_images and len(embedded_images) > 0:
        avatar_html = f'<img src="{embedded_images[0]}" style="width: 56px; height: 56px; border-radius: 50%; object-fit: cover; margin-bottom: 8px;" />'

    # Build Section HTML generator
    def render_section(sec, in_sidebar=False):
        txt_color = "#f1f5f9" if in_sidebar else "#0f172a"
        heading_color = "#93c5fd" if in_sidebar else "#1e293b"
        line_color = "#334155" if in_sidebar else "#cbd5e1"
        sub_color = "#94a3b8" if in_sidebar else "#64748b"

        items_html = []
        for item in sec.items:
            # Title & Date line
            t_line = ""
            if item.title:
                t_parts = [f'<span style="font-weight: 600; color: {txt_color};">{item.title}</span>']
                if item.dateRange:
                    t_parts.append(f'<span style="color: {sub_color}; font-size: 8.5pt;">{item.dateRange}</span>')
                t_line = f'<div style="display: flex; justify-content: space-between; align-items: baseline; margin-top: 3px;">{"".join(t_parts)}</div>'

            # Subtitle line
            sub_line = ""
            if item.subtitle or item.location:
                sub_parts = []
                if item.subtitle:
                    sub_parts.append(item.subtitle)
                if item.location:
                    sub_parts.append(item.location)
                sub_line = f'<div style="color: {sub_color}; font-size: 8.5pt; margin-bottom: 2px;">{"  |  ".join(sub_parts)}</div>'

            # Bullets
            bullets_html = []
            for b in item.bullets:
                clean_b = b.text.strip().lstrip("•-▪➤* ")
                bullets_html.append(
                    f'<li style="margin-bottom: 2px; padding-left: 2px; color: {txt_color}; font-size: 9pt; line-height: 1.25;">{clean_b}</li>'
                )

            b_list_html = f'<ul style="margin: 2px 0 4px 14px; padding: 0; list-style-type: disc;">{"".join(bullets_html)}</ul>' if bullets_html else ""
            items_html.append(f'<div>{t_line}{sub_line}{b_list_html}</div>')

        return f'''
        <div style="margin-bottom: 8px;">
            <div style="font-size: 10.5pt; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: {heading_color}; border-bottom: 1px solid {line_color}; padding-bottom: 2px; margin-bottom: 4px;">
                {sec.title}
            </div>
            {"".join(items_html)}
        </div>
        '''

    # Split sections for two-column if needed
    if is_two_col:
        sb_types = ["contact", "skills", "certifications", "education"]
        sidebar_secs = [s for s in content.sections if s.type in sb_types]
        main_secs = [s for s in content.sections if s.type not in sb_types]
        if not sidebar_secs:
            sidebar_secs = content.sections[:1]
            main_secs = content.sections[1:]

        contact_sidebar_html = f'''
        <div style="margin-bottom: 14px;">
            <div style="font-size: 10.5pt; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #93c5fd; border-bottom: 1px solid #334155; padding-bottom: 2px; margin-bottom: 6px;">
                Contact
            </div>
            <div style="font-size: 8.5pt; color: #f1f5f9; display: flex; flex-direction: column; gap: 4px;">
                {"".join(f'<div>{p}</div>' for p in contact_parts)}
            </div>
        </div>
        ''' if contact_parts else ""

        sidebar_html = f'''
        <aside style="width: {sidebar_w_percent}%; background-color: {sidebar_bg}; padding: 24px 18px; box-sizing: border-box; display: flex; flex-direction: column;">
            {avatar_html}
            {contact_sidebar_html}
            {"".join(render_section(s, in_sidebar=True) for s in sidebar_secs)}
        </aside>
        '''
        main_html = f'''
        <main style="flex: 1; padding: 28px 24px; box-sizing: border-box; display: flex; flex-direction: column;">
            <div style="margin-bottom: 16px;">
                <h1 style="font-size: 22pt; font-weight: 800; color: #0f172a; margin: 0 0 4px 0;">{header.name}</h1>
                <div style="font-size: 11pt; font-weight: 600; color: #3b82f6; margin-bottom: 6px;">{header.title}</div>
            </div>
            {"".join(render_section(s, in_sidebar=False) for s in main_secs)}
        </main>
        '''
        body_content = f'''
        <div style="display: flex; min-height: 100%; width: 100%; box-sizing: border-box;">
            {sidebar_html if is_sidebar_left else main_html}
            {main_html if is_sidebar_left else sidebar_html}
        </div>
        '''
    else:
        # Single column layout
        sections_html = "".join(render_section(s, in_sidebar=False) for s in content.sections)
        body_content = f'''
        <div style="padding: 20pt 30pt; box-sizing: border-box;">
            <div style="margin-bottom: 10px; border-bottom: 1px solid #e2e8f0; padding-bottom: 6px;">
                <h1 style="font-size: 18pt; font-weight: 800; color: #0f172a; margin: 0 0 2px 0;">{header.name}</h1>
                <div style="font-size: 10pt; font-weight: 500; color: #475569; margin-bottom: 4px;">{header.title}</div>
                <div style="font-size: 8.5pt; color: #64748b;">{contact_html}</div>
            </div>
            {sections_html}
        </div>
        '''

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Resume Document</title>
    <style>
        @page {{
            size: A4;
            margin: 0;
        }}
        html, body {{
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
        }}
    </style>
</head>
<body>
    {body_content}
</body>
</html>
'''
    return html


class PdfRebuildWriterStrategy(WriterStrategy):
    """Strategy 2: Tier B/C 'Close / Approximate'.

    Converts layout JSON and content to MirrorCV style tokens,
    embedding original images as assets and rendering via Playwright Chromium.
    """

    def plan(self, content: ResumeContent, template_data: Any) -> Dict[str, Any]:
        """Calculates page allocation and layout parameters for rebuild."""
        layout: Optional[PdfLayout] = template_data.get("layout")
        style: Optional[ResumeStyle] = template_data.get("style")
        return {
            "strategy": "rebuild",
            "is_two_col": bool(layout and any(c.type == "sidebar" for c in layout.columns)),
        }

    def write(self, content: ResumeContent, template_path: str, output_path: str, **kwargs) -> str:
        """Renders the resume via HTML rebuild with Playwright."""
        template_data = kwargs.get("template_data", {})
        layout: Optional[PdfLayout] = template_data.get("layout")
        style: Optional[ResumeStyle] = template_data.get("style")

        # Extract images from original PDF as base64 data URIs
        embedded_images: List[str] = []
        if os.path.exists(template_path):
            try:
                doc = fitz.open(template_path)
                for page in doc:
                    for img_info in page.get_images():
                        xref = img_info[0]
                        base_img = doc.extract_image(xref)
                        if base_img:
                            b64 = base64.b64encode(base_img["image"]).decode("ascii")
                            fmt = base_img["ext"]
                            embedded_images.append(f"data:image/{fmt};base64,{b64}")
                doc.close()
            except Exception:
                pass

        html_str = _generate_rebuild_html(
            content=content,
            style=style,
            layout=layout,
            embedded_images=embedded_images,
        )

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--font-render-hinting=none",
                ],
            )
            page = browser.new_page(viewport={"width": 1200, "height": 1600})
            page.set_content(html_str, wait_until="networkidle")
            page.pdf(
                path=output_path,
                format="A4",
                print_background=True,
                margin={"top": "0px", "bottom": "0px", "left": "0px", "right": "0px"},
            )
            browser.close()

        return output_path

    def measure(self, original_path: str, generated_path: str, **kwargs) -> FidelityScoreBreakdown:
        """Measures fidelity against original PDF."""
        return calculate_fidelity_score(
            original_pdf_path=original_path,
            generated_pdf_path=generated_path,
            font_table=kwargs.get("font_table"),
            is_scanned=kwargs.get("is_scanned", False),
        )
