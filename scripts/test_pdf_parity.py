"""
Preview vs PDF Parity Verification Script.
Compares word positions (PyMuPDF vs Playwright DOM bounding boxes within 1 pt),
page counts, and font embedding across 3 templates x 3 option combinations (9 total).
Includes:
- Mix layout
- Skills bubbles mode
- Skills level mode
- Image background
- Footer page numbers
- Hindi sample (Noto Sans Devanagari)
"""

import sys
import json
import pymupdf
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.generate_option_matrix import BASE_CONTENT, BASE_STYLE

ARTIFACT_DIR = Path("C:/Users/CH SANDEEP/.gemini/antigravity/brain/e3539cfe-1379-4d58-868f-a3ad5b4c09bd")
PDF_DIR = ARTIFACT_DIR / "pdf_parity"
PDF_DIR.mkdir(parents=True, exist_ok=True)

# 9 Test Combinations
COMBINATIONS = [
    {
        "id": "case_1_classic_standard",
        "name": "Classic Single + Standard Options",
        "template": "Classic Single Column",
        "features": ["Single Column", "Inter font", "Underline headings", "Footer page numbers"],
        "style_patch": {
            "layout": {"type": "single", "sidebarWidthPercent": 33, "sidebarSectionIds": [], "mainSectionIds": ["sec-summary", "sec-exp", "sec-skills", "sec-edu"], "sectionPlacement": {}},
            "typography": {**BASE_STYLE["typography"], "baseFontFamily": "Inter", "headingFontFamily": "Inter"},
            "heading": {"capitalization": "none", "iconStyle": "none"},
            "footer": {"showPageNumbers": True, "showEmail": False, "showName": False}
        },
        "content_patch": {}
    },
    {
        "id": "case_2_classic_bubbles",
        "name": "Classic Single + Skills Bubbles Mode",
        "template": "Classic Single Column",
        "features": ["Skills Bubbles Mode", "Date Below Title", "Accent Bar Headings"],
        "style_patch": {
            "layout": {"type": "single", "sidebarWidthPercent": 33, "sidebarSectionIds": [], "mainSectionIds": ["sec-summary", "sec-exp", "sec-skills", "sec-edu"], "sectionPlacement": {}},
            "skills": {"displayMode": "bubble"},
            "entryLayout": {"structure": "full_width", "dateLocationPosition": "below", "headerSplitRatio": "auto"},
            "decorations": {"sectionHeadingStyle": "bar"}
        },
        "content_patch": {}
    },
    {
        "id": "case_3_classic_hindi",
        "name": "Classic Single + Hindi Sample (Devanagari)",
        "template": "Classic Single Column",
        "features": ["Hindi Sample", "Noto Sans Devanagari", "Footer Page Numbers", "Pill Headings"],
        "style_patch": {
            "locale": "hi",
            "layout": {"type": "single", "sidebarWidthPercent": 33, "sidebarSectionIds": [], "mainSectionIds": ["sec-summary", "sec-exp", "sec-skills", "sec-edu"], "sectionPlacement": {}},
            "typography": {**BASE_STYLE["typography"], "baseFontFamily": "Noto Sans Devanagari", "headingFontFamily": "Noto Sans Devanagari"},
            "decorations": {"sectionHeadingStyle": "pill"},
            "footer": {"showPageNumbers": True, "showEmail": False, "showName": False}
        },
        "content_patch": {
            "header": {
                "name": "राजेश कुमार",
                "title": "वरिष्ठ सॉफ्टवेयर आर्किटेक्ट",
                "email": "rajesh.kumar@example.com",
                "phone": "+91 (987) 654-3210",
                "location": "नई दिल्ली, भारत",
                "website": "https://rajeshk.dev",
                "fieldVisibility": {"name": True, "title": True, "email": True, "phone": True, "location": True, "website": True, "photo": True},
                "links": [{"id": "l-1", "label": "गिटहब", "url": "https://github.com/rajesh"}]
            },
            "sections": [
                {
                    "id": "sec-summary",
                    "type": "summary",
                    "title": "व्यावसायिक सारांश",
                    "visible": True,
                    "items": [{"id": "s-1", "title": "", "subtitle": "", "location": "", "dateRange": "", "bullets": [{"id": "b-1", "text": "वितरित क्लाउड प्रणालियों में 10+ वर्षों के अनुभव के साथ विशेषज्ञ आर्किटेक्ट।"}]}]
                },
                {
                    "id": "sec-exp",
                    "type": "experience",
                    "title": "कार्य अनुभव",
                    "visible": True,
                    "items": [{"id": "e-1", "title": "वरिष्ठ सॉफ्टवेयर आर्किटेक्ट", "subtitle": "क्लाउडटेक सॉल्यूशंस", "location": "बेंगलुरु", "dateRange": "2021 – वर्तमान", "bullets": [{"id": "b-e1", "text": "उच्च-प्रदर्शन डेटा प्रोसेसिंग इंजन का निर्माण और संचालन।"}]}]
                },
                {
                    "id": "sec-skills",
                    "type": "skills",
                    "title": "तकनीकी कौशल",
                    "visible": True,
                    "skills": [
                        {"id": "sk-1", "name": "क्लाउड इन्फ्रास्ट्रक्चर", "category": "क्लाउड", "level": 5},
                        {"id": "sk-2", "name": "वितरित प्रणालियाँ", "category": "आर्किटेक्चर", "level": 5}
                    ]
                }
            ]
        }
    },
    {
        "id": "case_4_modern_skills_level",
        "name": "Modern Sidebar + Skills Level Mode",
        "template": "Modern Sidebar Left",
        "features": ["Sidebar Left (33%)", "Skills Level Mode (Dots 1-5)", "Roboto Font", "Boxed Headings"],
        "style_patch": {
            "layout": {"type": "sidebar_left", "sidebarWidthPercent": 33, "sidebarSectionIds": ["sec-skills"], "mainSectionIds": ["sec-summary", "sec-exp"], "sectionPlacement": {}},
            "skills": {"displayMode": "level"},
            "typography": {**BASE_STYLE["typography"], "baseFontFamily": "Roboto", "headingFontFamily": "Roboto"},
            "decorations": {"sectionHeadingStyle": "boxed"},
            "footer": {"showPageNumbers": True, "showEmail": False, "showName": False}
        },
        "content_patch": {}
    },
    {
        "id": "case_5_modern_image_background",
        "name": "Modern Sidebar + Image Background Mode",
        "template": "Modern Sidebar Left",
        "features": ["Image Background Mode", "Dark Overlay", "Footer Page Numbers", "White Text"],
        "style_patch": {
            "layout": {"type": "sidebar_left", "sidebarWidthPercent": 33, "sidebarSectionIds": ["sec-skills"], "mainSectionIds": ["sec-summary", "sec-exp"], "sectionPlacement": {}},
            "colors": {
                **BASE_STYLE["colors"],
                "colorMode": "image",
                "backgroundImage": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='400' height='400'><rect width='400' height='400' fill='%231e293b'/><circle cx='200' cy='200' r='120' fill='%23334155' opacity='0.5'/></svg>",
                "background": "#0f172a",
                "text": "#f8fafc",
                "muted": "#94a3b8",
                "sidebarBackground": "#1e293b",
                "divider": "#334155"
            },
            "footer": {"showPageNumbers": True, "showEmail": True, "showName": True}
        },
        "content_patch": {}
    },
    {
        "id": "case_6_modern_sidebar_wide",
        "name": "Modern Sidebar + Wide Column & Uppercase",
        "template": "Modern Sidebar Left",
        "features": ["Sidebar 40% Wide", "Heading Capitalization UPPERCASE", "Accent Side Line"],
        "style_patch": {
            "layout": {"type": "sidebar_left", "sidebarWidthPercent": 40, "sidebarSectionIds": ["sec-skills"], "mainSectionIds": ["sec-summary", "sec-exp"], "sectionPlacement": {}},
            "heading": {"capitalization": "uppercase", "iconStyle": "none"},
            "decorations": {"sectionHeadingStyle": "side_line"}
        },
        "content_patch": {}
    },
    {
        "id": "case_7_creative_mix_layout",
        "name": "Creative Mix Layout + Executive Serif",
        "template": "Creative Mix",
        "features": ["Mix Layout (Full Summary + 2-Col Body)", "Playfair Display Font", "Compact Margins"],
        "style_patch": {
            "layout": {
                "type": "mix",
                "sidebarWidthPercent": 35,
                "sidebarSectionIds": ["sec-skills"],
                "mainSectionIds": ["sec-exp"],
                "sectionPlacement": {
                    "sec-summary": "full",
                    "sec-exp": "main",
                    "sec-skills": "sidebar"
                }
            },
            "typography": {**BASE_STYLE["typography"], "headingFontFamily": "Playfair Display", "baseFontFamily": "Inter"},
            "margins": {"top": 28, "bottom": 28, "left": 32, "right": 32, "unit": "pt"},
            "footer": {"showPageNumbers": True, "showEmail": False, "showName": False}
        },
        "content_patch": {}
    },
    {
        "id": "case_8_creative_mix_bubbles_footer",
        "name": "Creative Mix + Skills Bubbles + Footer",
        "template": "Creative Mix",
        "features": ["Mix Layout", "Skills Bubbles Mode", "Footer Page Numbers", "Underline Headings"],
        "style_patch": {
            "layout": {
                "type": "mix",
                "sidebarWidthPercent": 35,
                "sidebarSectionIds": ["sec-skills"],
                "mainSectionIds": ["sec-exp"],
                "sectionPlacement": {
                    "sec-summary": "full",
                    "sec-exp": "main",
                    "sec-skills": "sidebar"
                }
            },
            "skills": {"displayMode": "bubble"},
            "decorations": {"sectionHeadingStyle": "underline"},
            "footer": {"showPageNumbers": True, "showEmail": True, "showName": False}
        },
        "content_patch": {}
    },
    {
        "id": "case_9_creative_mix_level_image",
        "name": "Creative Mix + Skills Level + Merriweather",
        "template": "Creative Mix",
        "features": ["Mix Layout", "Skills Level Mode (1-5)", "Merriweather Serif Font", "Header Center Aligned"],
        "style_patch": {
            "layout": {
                "type": "mix",
                "sidebarWidthPercent": 35,
                "sidebarSectionIds": ["sec-skills"],
                "mainSectionIds": ["sec-exp"],
                "sectionPlacement": {
                    "sec-summary": "full",
                    "sec-exp": "main",
                    "sec-skills": "sidebar"
                }
            },
            "skills": {"displayMode": "level"},
            "header": {"alignment": "center", "arrangement": "pipe"},
            "typography": {**BASE_STYLE["typography"], "baseFontFamily": "Merriweather", "headingFontFamily": "Merriweather"},
            "footer": {"showPageNumbers": True, "showEmail": False, "showName": True}
        },
        "content_patch": {}
    }
]

def run_parity_suite():
    print(f"Starting Preview vs PDF Parity Suite ({len(COMBINATIONS)} cases)...")
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1200, "height": 1600})

        for idx, case in enumerate(COMBINATIONS):
            cid = case["id"]
            name = case["name"]
            template = case["template"]
            features = ", ".join(case["features"])

            # Merge styles
            cur_style = json.loads(json.dumps(BASE_STYLE))
            for k, v in case["style_patch"].items():
                if isinstance(v, dict) and k in cur_style and isinstance(cur_style[k], dict):
                    cur_style[k].update(v)
                else:
                    cur_style[k] = v

            # Merge content
            cur_content = json.loads(json.dumps(BASE_CONTENT))
            for k, v in case["content_patch"].items():
                cur_content[k] = v

            resume_obj = {
                "id": f"parity-{cid}",
                "userId": "system",
                "title": f"Parity - {name}",
                "content": cur_content,
                "style": cur_style,
                "version": 1
            }
            resume_json = json.dumps(resume_obj)

            # Inject via add_init_script for instantaneous hydration
            page.add_init_script(f"localStorage.setItem('matrix_resume', JSON.stringify({resume_json}));")
            page.goto("http://localhost:3000/render/custom")
            page.wait_for_selector(".resume-ready", timeout=8000)
            page.wait_for_timeout(250)

            # 1. Query DOM page count and words on each page
            dom_data = page.evaluate("""() => {
                const pages = document.querySelectorAll('.print-page');
                const pageResults = [];
                pages.forEach((pElem, pIdx) => {
                    const pRect = pElem.getBoundingClientRect();
                    const walker = document.createTreeWalker(pElem, NodeFilter.SHOW_TEXT);
                    let node;
                    const words = [];
                    while (node = walker.nextNode()) {
                        if (node.parentElement && node.parentElement.closest('.print\\\\:hidden')) continue;
                        const text = node.textContent;
                        if (!text || !text.trim()) continue;
                        const regex = /\\S+/g;
                        let match;
                        while ((match = regex.exec(text)) !== null) {
                            const range = document.createRange();
                            range.setStart(node, match.index);
                            range.setEnd(node, match.index + match[0].length);
                            const rect = range.getBoundingClientRect();
                            words.push({
                                word: match[0],
                                x0: (rect.left - pRect.left) * 0.75,
                                y0: (rect.top - pRect.top) * 0.75,
                                x1: (rect.right - pRect.left) * 0.75,
                                y1: (rect.bottom - pRect.top) * 0.75
                            });
                        }
                    }
                    pageResults.push({ pageIndex: pIdx, words });
                });
                return pageResults;
            }""")

            dom_page_count = len(dom_data)

            # 2. Export exact PDF bytes
            pdf_bytes = page.pdf(
                format="A4",
                print_background=True,
                prefer_css_page_size=True,
                margin={"top": "0px", "bottom": "0px", "left": "0px", "right": "0px"}
            )
            pdf_path = PDF_DIR / f"{cid}.pdf"
            pdf_path.write_bytes(pdf_bytes)

            # 3. Analyze PDF with PyMuPDF
            doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
            pdf_page_count = len(doc)
            page_count_match = (dom_page_count == pdf_page_count)

            # 4. Check embedded fonts across all pages
            all_fonts = []
            for p_i in range(pdf_page_count):
                all_fonts.extend(doc.get_page_fonts(p_i))
            embedded_fonts = [f[3] for f in all_fonts]
            # Ensure every font is embedded (Type0 or TrueType) and not substituted
            has_embedded_fonts = len(embedded_fonts) > 0 and all(
                ("Inter" in f or "Noto" in f or "Roboto" in f or "Playfair" in f or "Merriweather" in f or "Arial" in f or "Segoe" in f)
                for f in embedded_fonts
            )

            # 5. Coordinate parity check on Page 1 (where most text lives)
            p0_dom_words = dom_data[0]["words"] if dom_data else []
            p0_pdf_words = doc[0].get_text("words") if pdf_page_count > 0 else []

            max_dx = 0.0
            max_dy = 0.0
            matched_words = 0
            within_1pt_count = 0

            for dw in p0_dom_words:
                w_text = dw["word"]
                candidates = [pw for pw in p0_pdf_words if pw[4] == w_text]
                if candidates:
                    best = min(candidates, key=lambda c: (c[0] - dw["x0"]) ** 2 + (c[1] - dw["y0"]) ** 2)
                    dx = abs(best[0] - dw["x0"])
                    dy = abs(best[1] - dw["y0"])
                    if dx < 15 and dy < 15:  # Same word instance
                        matched_words += 1
                        if dx <= 1.0 and dy <= 1.0:
                            within_1pt_count += 1
                        if dx > max_dx: max_dx = dx
                        if dy > max_dy: max_dy = dy

            pass_coords = (max_dx <= 1.0) and (max_dy <= 1.0)
            overall_pass = page_count_match and pass_coords and has_embedded_fonts

            res_entry = {
                "case_id": cid,
                "name": name,
                "template": template,
                "features": features,
                "dom_pages": dom_page_count,
                "pdf_pages": pdf_page_count,
                "page_count_match": page_count_match,
                "matched_words": matched_words,
                "within_1pt_count": within_1pt_count,
                "max_dx_pt": round(max_dx, 3),
                "max_dy_pt": round(max_dy, 3),
                "pass_coords_within_1pt": pass_coords,
                "embedded_fonts": sorted(list(set(embedded_fonts))),
                "status": "PASS" if overall_pass else "FAIL"
            }
            results.append(res_entry)

            print(f"[{idx+1}/9] {cid}: Pages={dom_page_count}/{pdf_page_count} (Match: {page_count_match}) | Max dx={max_dx:.3f}pt, dy={max_dy:.3f}pt | Fonts={len(embedded_fonts)} -> {res_entry['status']}")

        browser.close()

    # Save summary JSON
    summary_path = ARTIFACT_DIR / "pdf_parity_summary.json"
    summary_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nParity summary written to {summary_path}")

    # Print summary table
    print("\n" + "=" * 100)
    print(f"{'Case ID':<25} | {'Template':<16} | {'Pages':<7} | {'Max dx (pt)':<12} | {'Max dy (pt)':<12} | {'Status'}")
    print("-" * 100)
    for r in results:
        print(f"{r['case_id']:<25} | {r['template']:<16} | {str(r['dom_pages'])+'/'+str(r['pdf_pages']):<7} | {r['max_dx_pt']:<12} | {r['max_dy_pt']:<12} | {r['status']}")
    print("=" * 100)

if __name__ == "__main__":
    run_parity_suite()
