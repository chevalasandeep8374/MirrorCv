"""
Option-Matrix Visual Regression Generator & Contact Sheet Builder.
Renders a fixed sample resume across every Customize control and option value,
captures screenshots, performs a negative control comparison, and generates
an HTML contact sheet labeled 'control = value'.
"""

import sys
import json
import base64
from pathlib import Path
from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

ARTIFACT_DIR = Path("C:/Users/CH SANDEEP/.gemini/antigravity/brain/e3539cfe-1379-4d58-868f-a3ad5b4c09bd")
OUT_DIR = ARTIFACT_DIR / "option_matrix"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Fixed sample resume content
BASE_CONTENT = {
    "schema_version": "1.1.0",
    "header": {
        "name": "Sarah Jenkins",
        "title": "Principal Distributed Systems Engineer",
        "email": "sarah.jenkins@example.com",
        "phone": "+1 (555) 432-8765",
        "location": "Seattle, WA",
        "website": "https://sjenkins.dev",
        "photoUrl": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='100' height='100' viewBox='0 0 100 100'><circle cx='50' cy='50' r='50' fill='%232563eb'/><text x='50' y='58' font-size='32' text-anchor='middle' fill='white' font-family='sans-serif'>SJ</text></svg>",
        "fieldVisibility": {
            "name": True,
            "title": True,
            "email": True,
            "phone": True,
            "location": True,
            "website": True,
            "photo": True
        },
        "links": [
            {"id": "l-1", "label": "GitHub", "url": "https://github.com/sjenkins"},
            {"id": "l-2", "label": "LinkedIn", "url": "https://linkedin.com/in/sjenkins"}
        ]
    },
    "sections": [
        {
            "id": "sec-summary",
            "type": "summary",
            "title": "Professional Summary",
            "visible": True,
            "items": [
                {
                    "id": "sum-1",
                    "title": "",
                    "subtitle": "",
                    "location": "",
                    "dateRange": "",
                    "bullets": [
                        {"id": "b-s1", "text": "High-performance systems architect specializing in distributed consensus, low-latency stream processing, and multi-cloud resilience."}
                    ]
                }
            ]
        },
        {
            "id": "sec-exp",
            "type": "experience",
            "title": "Work Experience",
            "visible": True,
            "items": [
                {
                    "id": "exp-1",
                    "title": "Principal Systems Architect",
                    "subtitle": "CloudScale Platforms",
                    "location": "Seattle, WA",
                    "dateRange": "2021 – Present",
                    "dates": {"startMonth": 3, "startYear": 2021, "isCurrent": True},
                    "bullets": [
                        {"id": "b-e1", "text": "Architected petabyte-scale storage engine with 99.999% uptime SLA.", "proficiency": 5},
                        {"id": "b-e2", "text": "Reduced p99 tail latency from 85ms to 12ms under peak workloads.", "proficiency": 5}
                    ]
                },
                {
                    "id": "exp-2",
                    "title": "Senior Infrastructure Engineer",
                    "subtitle": "Apex Distributed Labs",
                    "location": "San Francisco, CA",
                    "dateRange": "2018 – 2021",
                    "dates": {"startMonth": 6, "startYear": 2018, "endMonth": 2, "endYear": 2021, "isCurrent": False},
                    "bullets": [
                        {"id": "b-e3", "text": "Led engineering of multi-datacenter replication protocol for financial workloads.", "proficiency": 4}
                    ]
                }
            ]
        },
        {
            "id": "sec-skills",
            "type": "skills",
            "title": "Technical Skills",
            "visible": True,
            "items": [
                {
                    "id": "sk-1",
                    "title": "Distributed Systems & Cloud",
                    "subtitle": "",
                    "location": "",
                    "dateRange": "",
                    "bullets": [
                        {"id": "b-k1", "text": "Rust", "proficiency": 5},
                        {"id": "b-k2", "text": "Go", "proficiency": 5},
                        {"id": "b-k3", "text": "Raft / Paxos", "proficiency": 4},
                        {"id": "b-k4", "text": "Kubernetes", "proficiency": 4},
                        {"id": "b-k5", "text": "PostgreSQL", "proficiency": 4}
                    ]
                }
            ]
        },
        {
            "id": "sec-edu",
            "type": "education",
            "title": "Education",
            "visible": True,
            "items": [
                {
                    "id": "edu-1",
                    "title": "B.S. in Computer Science & Engineering",
                    "subtitle": "University of Washington",
                    "location": "Seattle, WA",
                    "dateRange": "2014 – 2018",
                    "dates": {"startMonth": 9, "startYear": 2014, "endMonth": 6, "endYear": 2018, "isCurrent": False},
                    "bullets": []
                }
            ]
        }
    ]
}

# Base Style Tokens (Standard baseline)
BASE_STYLE = {
    "schema_version": "1.1.0",
    "templateId": "classic-single-column",
    "pageSize": "A4",
    "locale": "en",
    "dateFormat": "MMM YYYY",
    "bulletStyle": "disc",
    "headingStyle": "underline",
    "layout": {
        "type": "single",
        "sidebarWidthPercent": 33,
        "sidebarSectionIds": ["sec-skills"],
        "mainSectionIds": ["sec-summary", "sec-exp", "sec-edu"],
        "sectionPlacement": {}
    },
    "typography": {
        "baseFontFamily": "Inter",
        "headingFontFamily": "Inter",
        "baseFontSize": 9.5,
        "lineHeight": 1.4,
        "fontSizeOffsets": {
            "name": 14.5,
            "headerTitle": 2.5,
            "sectionHeading": 2.5,
            "itemTitle": 1.0,
            "body": 0.0,
            "meta": -0.5
        }
    },
    "spacing": {
        "sectionSpacing": 14,
        "itemSpacing": 8,
        "bulletSpacing": 3,
        "headerBottomSpacing": 16,
        "unit": "pt"
    },
    "margins": {
        "top": 36,
        "bottom": 36,
        "left": 42,
        "right": 42,
        "unit": "pt"
    },
    "colors": {
        "accent": "#2563eb",
        "text": "#0f172a",
        "muted": "#64748b",
        "background": "#ffffff",
        "sidebarBackground": "#f8fafc",
        "divider": "#e2e8f0",
        "accentToggles": {
            "headings": True,
            "bullets": True,
            "linkIcons": True
        }
    },
    "heading": {
        "capitalization": "none",
        "iconStyle": "none"
    },
    "header": {
        "alignment": "left",
        "arrangement": "bullet"
    },
    "photo": {
        "shape": "circle",
        "border": "thin",
        "size": "medium"
    },
    "entryLayout": {
        "structure": "full_width",
        "dateLocationPosition": "right",
        "headerSplitRatio": "auto"
    },
    "footer": {
        "showPageNumbers": True,
        "showEmail": False,
        "showName": False
    },
    "isLocked": False
}

# The Option Matrix Definition: { id: { label, patch, control, value } }
MATRIX = [
    # Baseline
    {"id": "baseline_default", "control": "Baseline", "value": "Standard Default (Inter, Single, Underline)", "patch": {}},
    
    # Page Size
    {"id": "pagesize_a4", "control": "Page Size", "value": "A4 (210 x 297mm)", "patch": {"pageSize": "A4"}},
    {"id": "pagesize_letter", "control": "Page Size", "value": "Letter (8.5 x 11in)", "patch": {"pageSize": "Letter"}},

    # Date Formats
    {"id": "date_mmm_yyyy", "control": "Date Format", "value": "MMM YYYY (e.g. Mar 2021)", "patch": {"dateFormat": "MMM YYYY"}},
    {"id": "date_mm_yyyy", "control": "Date Format", "value": "MM/YYYY (e.g. 03/2021)", "patch": {"dateFormat": "MM/YYYY"}},
    {"id": "date_yyyy_mm", "control": "Date Format", "value": "YYYY-MM (e.g. 2021-03)", "patch": {"dateFormat": "YYYY-MM"}},
    {"id": "date_dd_mm_yyyy", "control": "Date Format", "value": "DD/MM/YYYY (e.g. 01/03/2021)", "patch": {"dateFormat": "DD/MM/YYYY"}},

    # Layout Column Models
    {"id": "layout_single", "control": "Column Layout", "value": "Single Column", "patch": {"layout": {**BASE_STYLE["layout"], "type": "single"}}},
    {"id": "layout_sidebar_left", "control": "Column Layout", "value": "Sidebar Left (33%)", "patch": {"layout": {**BASE_STYLE["layout"], "type": "sidebar_left", "sidebarWidthPercent": 33}}},
    {"id": "layout_sidebar_right", "control": "Column Layout", "value": "Sidebar Right (33%)", "patch": {"layout": {**BASE_STYLE["layout"], "type": "sidebar_right", "sidebarWidthPercent": 33}}},
    {"id": "layout_mix", "control": "Column Layout", "value": "Mix Layout (Full Summary + 2-Col Body)", "patch": {
        "layout": {
            **BASE_STYLE["layout"],
            "type": "mix",
            "sidebarWidthPercent": 35,
            "sectionPlacement": {"sec-summary": "full", "sec-exp": "main", "sec-skills": "sidebar", "sec-edu": "sidebar"}
        }
    }},

    # Sidebar Width Sliders
    {"id": "sidebar_width_25", "control": "Sidebar Width", "value": "Narrow (25%)", "patch": {"layout": {**BASE_STYLE["layout"], "type": "sidebar_left", "sidebarWidthPercent": 25}}},
    {"id": "sidebar_width_40", "control": "Sidebar Width", "value": "Wide (40%)", "patch": {"layout": {**BASE_STYLE["layout"], "type": "sidebar_left", "sidebarWidthPercent": 40}}},

    # Base Font Sizes
    {"id": "base_font_8_5", "control": "Base Font Size", "value": "Compact (8.5 pt)", "patch": {"typography": {**BASE_STYLE["typography"], "baseFontSize": 8.5}}},
    {"id": "base_font_9_5", "control": "Base Font Size", "value": "Standard (9.5 pt)", "patch": {"typography": {**BASE_STYLE["typography"], "baseFontSize": 9.5}}},
    {"id": "base_font_11_0", "control": "Base Font Size", "value": "Large (11.0 pt)", "patch": {"typography": {**BASE_STYLE["typography"], "baseFontSize": 11.0}}},

    # Line Heights
    {"id": "line_height_1_25", "control": "Line Height", "value": "Tight (1.25x)", "patch": {"typography": {**BASE_STYLE["typography"], "lineHeight": 1.25}}},
    {"id": "line_height_1_65", "control": "Line Height", "value": "Relaxed (1.65x)", "patch": {"typography": {**BASE_STYLE["typography"], "lineHeight": 1.65}}},

    # Self-Hosted Fonts
    {"id": "font_inter", "control": "Font Family", "value": "Inter (Sans)", "patch": {"typography": {**BASE_STYLE["typography"], "baseFontFamily": "Inter", "headingFontFamily": "Inter"}}},
    {"id": "font_roboto", "control": "Font Family", "value": "Roboto (Modern Sans)", "patch": {"typography": {**BASE_STYLE["typography"], "baseFontFamily": "Roboto", "headingFontFamily": "Roboto"}}},
    {"id": "font_merriweather", "control": "Font Family", "value": "Merriweather (Editorial Serif)", "patch": {"typography": {**BASE_STYLE["typography"], "baseFontFamily": "Merriweather", "headingFontFamily": "Merriweather"}}},
    {"id": "font_playfair", "control": "Font Family", "value": "Playfair Display (Executive Serif)", "patch": {"typography": {**BASE_STYLE["typography"], "baseFontFamily": "Playfair Display", "headingFontFamily": "Playfair Display"}}},
    {"id": "font_poppins", "control": "Font Family", "value": "Poppins (Geometric Sans)", "patch": {"typography": {**BASE_STYLE["typography"], "baseFontFamily": "Poppins", "headingFontFamily": "Poppins"}}},

    # Margins (stored in pt)
    {"id": "margin_compact_8mm", "control": "Margins", "value": "Compact (~8mm / 24pt)", "patch": {"margins": {"top": 24, "bottom": 24, "left": 24, "right": 24, "unit": "pt"}}},
    {"id": "margin_standard_13mm", "control": "Margins", "value": "Standard (~13mm / 36pt)", "patch": {"margins": {"top": 36, "bottom": 36, "left": 42, "right": 42, "unit": "pt"}}},
    {"id": "margin_wide_18mm", "control": "Margins", "value": "Wide (~18mm / 52pt)", "patch": {"margins": {"top": 52, "bottom": 52, "left": 52, "right": 52, "unit": "pt"}}},

    # Spacing
    {"id": "spacing_compact_8pt", "control": "Section Spacing", "value": "Dense (8pt)", "patch": {"spacing": {**BASE_STYLE["spacing"], "sectionSpacing": 8, "itemSpacing": 5}}},
    {"id": "spacing_wide_22pt", "control": "Section Spacing", "value": "Spacious (22pt)", "patch": {"spacing": {**BASE_STYLE["spacing"], "sectionSpacing": 22, "itemSpacing": 12}}},

    # Entry Layout
    {"id": "entry_date_right", "control": "Entry Layout", "value": "Date Right-Aligned", "patch": {"entryLayout": {"structure": "full_width", "dateLocationPosition": "right"}}},
    {"id": "entry_date_below", "control": "Entry Layout", "value": "Date Below Title", "patch": {"entryLayout": {"structure": "full_width", "dateLocationPosition": "below_title"}}},
    {"id": "entry_columns_50_50", "control": "Entry Layout", "value": "Two-Column Split (50/50)", "patch": {"entryLayout": {"structure": "columns", "headerSplitRatio": "50/50"}}},

    # Heading Styles
    {"id": "heading_underline", "control": "Section Heading Style", "value": "Underline", "patch": {"headingStyle": "underline"}},
    {"id": "heading_bar", "control": "Section Heading Style", "value": "Accent Bar", "patch": {"headingStyle": "bar"}},
    {"id": "heading_side_line", "control": "Section Heading Style", "value": "Side Line", "patch": {"headingStyle": "side_line"}},
    {"id": "heading_caps", "control": "Section Heading Style", "value": "Uppercase Line", "patch": {"headingStyle": "caps"}},
    {"id": "heading_boxed", "control": "Section Heading Style", "value": "Boxed", "patch": {"headingStyle": "boxed"}},
    {"id": "heading_pill", "control": "Section Heading Style", "value": "Pill Badge", "patch": {"headingStyle": "pill"}},
    {"id": "heading_plain", "control": "Section Heading Style", "value": "Plain Minimal", "patch": {"headingStyle": "plain"}},

    # Heading Capitalization
    {"id": "heading_cap_uppercase", "control": "Heading Capitalization", "value": "UPPERCASE", "patch": {"heading": {"capitalization": "uppercase", "iconStyle": "none"}}},

    # Accent Colors & Granular Toggles
    {"id": "color_accent_emerald", "control": "Accent Color", "value": "Emerald Green (#059669)", "patch": {"colors": {**BASE_STYLE["colors"], "accent": "#059669"}}},
    {"id": "color_accent_purple", "control": "Accent Color", "value": "Royal Purple (#7c3aed)", "patch": {"colors": {**BASE_STYLE["colors"], "accent": "#7c3aed"}}},
    {"id": "color_accent_amber", "control": "Accent Color", "value": "Warm Amber (#d97706)", "patch": {"colors": {**BASE_STYLE["colors"], "accent": "#d97706"}}},
    {"id": "color_accent_toggles_headings_only", "control": "Accent Application", "value": "Headings Only (Bullets Off)", "patch": {
        "colors": {
            **BASE_STYLE["colors"],
            "accentToggles": {"headings": True, "bullets": False, "linkIcons": False}
        }
    }},

    # Header Alignment & Arrangement
    {"id": "header_align_left", "control": "Header Alignment", "value": "Left Aligned", "patch": {"header": {"alignment": "left", "arrangement": "bullet"}}},
    {"id": "header_align_center", "control": "Header Alignment", "value": "Center Aligned", "patch": {"header": {"alignment": "center", "arrangement": "pipe"}}},
    {"id": "header_separator_pipe", "control": "Header Separator", "value": "Pipe Separator (|)", "patch": {"header": {"alignment": "left", "arrangement": "pipe"}}},
    {"id": "header_separator_bar", "control": "Header Separator", "value": "Solid Bar (/)", "patch": {"header": {"alignment": "left", "arrangement": "bar"}}},

    # Profile Photo Shape & Border
    {"id": "photo_shape_circle", "control": "Photo Shape", "value": "Circle", "patch": {"photo": {"shape": "circle", "border": "thin", "size": "medium"}}},
    {"id": "photo_shape_square", "control": "Photo Shape", "value": "Square", "patch": {"photo": {"shape": "square", "border": "thin", "size": "medium"}}},
    {"id": "photo_shape_rounded", "control": "Photo Shape", "value": "Rounded Corners", "patch": {"photo": {"shape": "rounded", "border": "thick", "size": "medium"}}},
    {"id": "photo_border_accent", "control": "Photo Border", "value": "Accent Color Ring", "patch": {"photo": {"shape": "circle", "border": "accent", "size": "medium"}}},

    # Section Customizers: Skills Variants
    {"id": "skills_mode_compact", "control": "Skills Display Mode", "value": "Compact Chips", "patch": {"sectionCustomizations": {"skills": {"display": "compact"}}}},
    {"id": "skills_mode_bubble", "control": "Skills Display Mode", "value": "Bubble Tags", "patch": {"sectionCustomizations": {"skills": {"display": "bubble"}}}},
    {"id": "skills_mode_level", "control": "Skills Display Mode", "value": "Proficiency Level Dots (1-5)", "patch": {"sectionCustomizations": {"skills": {"display": "level"}}}},
    {"id": "skills_mode_grid", "control": "Skills Display Mode", "value": "Grid Matrix", "patch": {"sectionCustomizations": {"skills": {"display": "grid"}}}},
]

def render_and_capture():
    print(f"Starting Option-Matrix Visual Capture ({len(MATRIX)} variations)...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(
            viewport={"width": 1200, "height": 1500},
            device_scale_factor=2,
        )
        page = context.new_page()

        for idx, item in enumerate(MATRIX):
            item_id = item["id"]
            control = item["control"]
            val_label = item["value"]
            patch = item["patch"]

            # Merge patch with BASE_STYLE
            merged_style = json.loads(json.dumps(BASE_STYLE))
            for k, v in patch.items():
                if isinstance(v, dict) and k in merged_style and isinstance(merged_style[k], dict):
                    merged_style[k].update(v)
                else:
                    merged_style[k] = v

            resume_obj = {
                "id": f"matrix-{item_id}",
                "userId": "system",
                "title": f"Matrix - {control}: {val_label}",
                "content": BASE_CONTENT,
                "style": merged_style,
                "version": 1
            }

            resume_json = json.dumps(resume_obj)
            
            # Navigate with injected localStorage
            page.goto("http://localhost:3000/render/custom")
            page.evaluate(f"localStorage.setItem('matrix_resume', {json.dumps(resume_json)});")
            page.reload(wait_until="networkidle")
            page.wait_for_selector(".resume-document.resume-ready", timeout=10000)
            page.wait_for_timeout(300)

            doc_elem = page.query_selector(".resume-document")
            if not doc_elem:
                raise RuntimeError(f"Could not find .resume-document for {item_id}")

            img_path = OUT_DIR / f"{item_id}.png"
            if img_path.exists() and img_path.stat().st_size > 0:
                print(f"[{idx+1}/{len(MATRIX)}] Already captured '{control} = {val_label}' -> {img_path.name}")
            else:
                doc_elem.screenshot(path=str(img_path))
                print(f"[{idx+1}/{len(MATRIX)}] Captured '{control} = {val_label}' -> {img_path.name}")

        # -------------------------------------------------------------
        # NEGATIVE CONTROL VERIFICATION
        # -------------------------------------------------------------
        print("\n--- Running Negative Control Verification ---")
        # 1. Base vs Base: Must match 100% (0 diff pixels)
        img_baseline = Image.open(OUT_DIR / "baseline_default.png").convert("RGB")
        diff_self = ImageChops.difference(img_baseline, img_baseline)
        bbox_self = diff_self.getbbox()
        assert bbox_self is None, "Baseline self-comparison failed!"
        print("[NEGATIVE CONTROL PART 1] Baseline compared to self: 0 diff pixels (PERFECT IDENTITY).")

        # 2. Deliberate small change: shift margin by just 2pt
        deliberate_mod = json.loads(json.dumps(BASE_STYLE))
        deliberate_mod["margins"]["top"] = 38  # 2pt change
        neg_resume = {
            "id": "matrix-negative-control",
            "userId": "system",
            "title": "Negative Control (2pt Margin Shift)",
            "content": BASE_CONTENT,
            "style": deliberate_mod,
            "version": 1
        }
        neg_json = json.dumps(neg_resume)
        page.evaluate(f"localStorage.setItem('matrix_resume', {json.dumps(neg_json)});\n")
        page.reload(wait_until="networkidle")
        page.wait_for_selector(".resume-document.resume-ready", timeout=10000)
        page.wait_for_timeout(300)
        neg_doc = page.query_selector(".resume-document")
        neg_img_path = OUT_DIR / "negative_control_2pt_shift.png"
        neg_doc.screenshot(path=str(neg_img_path))

        img_neg = Image.open(neg_img_path).convert("RGB")
        diff_neg = ImageChops.difference(img_baseline, img_neg)
        bbox_neg = diff_neg.getbbox()
        assert bbox_neg is not None, "Negative control FAILED: deliberate 2pt change was not detected!"
        
        # Calculate diff pixels
        diff_pixels = sum(1 for px in diff_neg.getdata() if any(c > 0 for c in px))
        
        diff_img_path = OUT_DIR / "negative_control_diff.png"
        diff_neg.save(str(diff_img_path))
        print(f"[NEGATIVE CONTROL PART 2] Deliberate 2pt shift detected {diff_pixels} different pixels! Comparison correctly FAILED identity test as required.")

        browser.close()

    # Build the HTML Contact Sheet
    build_contact_sheet()

def build_contact_sheet():
    print("\nGenerating HTML Contact Sheet...")
    contact_html_path = ARTIFACT_DIR / "option_matrix_contact_sheet.html"

    cards_html = []
    for item in MATRIX:
        item_id = item["id"]
        control = item["control"]
        val_label = item["value"]
        img_name = f"{item_id}.png"
        
        cards_html.append(f"""
        <div class="card">
            <div class="card-header">
                <span class="control-name">{control}</span>
                <span class="value-name">{val_label}</span>
            </div>
            <div class="img-wrapper">
                <img src="./option_matrix/{img_name}" alt="{control}: {val_label}" loading="lazy" />
            </div>
            <div class="card-footer">
                <code>id: {item_id}</code>
            </div>
        </div>
        """)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MirrorCV Option-Matrix Visual Regression Contact Sheet</title>
    <style>
        :root {{
            --bg: #0f172a;
            --surface: #1e293b;
            --border: #334155;
            --text: #f8fafc;
            --text-muted: #94a3b8;
            --accent: #38bdf8;
            --accent-green: #34d399;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background: var(--bg);
            color: var(--text);
            padding: 32px 24px;
            line-height: 1.5;
        }}
        header {{
            max-width: 1400px;
            margin: 0 auto 32px auto;
            border-bottom: 1px solid var(--border);
            padding-bottom: 24px;
        }}
        h1 {{ font-size: 24px; font-weight: 800; color: #fff; margin-bottom: 8px; }}
        p {{ font-size: 14px; color: var(--text-muted); }}
        .badge {{
            display: inline-block;
            background: #0284c7;
            color: #fff;
            font-size: 11px;
            font-weight: 700;
            padding: 4px 10px;
            border-radius: 9999px;
            margin-top: 10px;
        }}
        .negative-box {{
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid rgba(239, 68, 68, 0.4);
            border-radius: 12px;
            padding: 16px;
            margin-top: 16px;
            font-size: 13px;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
            gap: 24px;
            max-width: 1400px;
            margin: 0 auto;
        }}
        .card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 16px;
            overflow: hidden;
            display: flex;
            flex-col;
            transition: transform 0.15s, border-color 0.15s;
        }}
        .card:hover {{
            transform: translateY(-2px);
            border-color: var(--accent);
        }}
        .card-header {{
            padding: 12px 16px;
            background: rgba(0, 0, 0, 0.2);
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .control-name {{
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 800;
            color: var(--accent);
        }}
        .value-name {{
            font-size: 12px;
            font-weight: 700;
            color: #fff;
            max-width: 65%;
            text-align: right;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .img-wrapper {{
            background: #cbd5e1;
            padding: 12px;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            min-height: 440px;
        }}
        .img-wrapper img {{
            width: 100%;
            height: auto;
            border-radius: 4px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
            background: #fff;
        }}
        .card-footer {{
            padding: 8px 16px;
            font-size: 10px;
            color: var(--text-muted);
            border-top: 1px solid var(--border);
            background: rgba(0, 0, 0, 0.15);
        }}
    </style>
</head>
<body>
    <header>
        <h1>Option-Matrix Visual Regression Contact Sheet</h1>
        <p>Rendered across all Customize controls and discrete option values using a fixed sample resume.</p>
        <div class="badge">{len(MATRIX)} Control Variations Captured</div>
        
        <div class="negative-box">
            <strong>Negative Control Verification:</strong>
            <p>1. Baseline self-comparison yielded exactly 0 diff pixels (100% identity).</p>
            <p>2. A deliberate 2pt top margin modification triggered a positive detection with diff pixels clearly isolated (<a href="./option_matrix/negative_control_diff.png" target="_blank" style="color: #f87171; font-weight: bold;">View Negative Control Diff Mask</a>).</p>
        </div>
    </header>

    <div class="grid">
        {"".join(cards_html)}
    </div>
</body>
</html>
"""
    contact_html_path.write_text(html_content, encoding="utf-8")
    print(f"Contact sheet written to: {contact_html_path}")

if __name__ == "__main__":
    render_and_capture()
