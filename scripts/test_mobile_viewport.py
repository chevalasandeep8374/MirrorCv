"""
Mobile Viewport (390x844) Responsiveness Test.
Verifies:
1. No horizontal scrolling (scrollWidth <= innerWidth at 390px).
2. Mobile bottom navigation tab switcher functions correctly.
3. Content and Preview views switch cleanly without layout breakages.
"""

import sys
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.generate_option_matrix import BASE_CONTENT, BASE_STYLE

ARTIFACT_DIR = Path("C:/Users/CH SANDEEP/.gemini/antigravity/brain/e3539cfe-1379-4d58-868f-a3ad5b4c09bd")

def test_mobile_layout():
    print("Starting Mobile (390x844) Viewport Verification...")
    results = {}

    with sync_playwright() as p:
        browser = p.chromium.launch()
        # Exact iPhone 12/13/14/15 standard viewport
        context = browser.new_context(
            viewport={"width": 390, "height": 844},
            is_mobile=True,
            has_touch=True,
            device_scale_factor=3,
        )
        page = context.new_page()

        resume_obj = {
            "id": "mobile-test",
            "userId": "system",
            "title": "Mobile Viewport Test",
            "content": BASE_CONTENT,
            "style": BASE_STYLE,
            "version": 1
        }
        resume_json = json.dumps(resume_obj)
        page.add_init_script(f"""
            localStorage.setItem('resume_mobile-test', JSON.stringify({resume_json}));
            localStorage.setItem('matrix_resume', JSON.stringify({resume_json}));
        """)

        page.goto("http://localhost:3000/editor/mobile-test")
        page.wait_for_selector("header", timeout=10000)
        page.wait_for_timeout(500)

        # 1. Content Tab initial check
        w_width = page.evaluate("() => window.innerWidth")
        s_width = page.evaluate("() => document.documentElement.scrollWidth")
        b_width = page.evaluate("() => document.body.scrollWidth")
        no_h_scroll_content = (s_width <= w_width) and (b_width <= w_width)
        print(f"Content View: innerWidth={w_width}, scrollWidth={s_width} (No H-Scroll: {no_h_scroll_content})")

        # 2. Switch to Preview via mobile bottom bar
        preview_btn = page.query_selector("div.md\\:hidden button:has-text('Preview')")
        assert preview_btn, "Mobile Preview button not found in bottom bar!"
        preview_btn.click()
        page.wait_for_timeout(400)

        s_width_preview = page.evaluate("() => document.documentElement.scrollWidth")
        b_width_preview = page.evaluate("() => document.body.scrollWidth")
        no_h_scroll_preview = (s_width_preview <= w_width) and (b_width_preview <= w_width)
        preview_visible = page.is_visible(".resume-document")
        print(f"Preview View: innerWidth={w_width}, scrollWidth={s_width_preview} (Visible: {preview_visible}, No H-Scroll: {no_h_scroll_preview})")

        # 3. Switch to Design (Customize) via mobile bottom bar
        customize_btn = page.query_selector("div.md\\:hidden button:has-text('Design'), div.md\\:hidden button:has-text('Customize')")
        assert customize_btn, "Mobile Design/Customize button not found in bottom bar!"
        customize_btn.click()
        page.wait_for_timeout(400)

        s_width_custom = page.evaluate("() => document.documentElement.scrollWidth")
        b_width_custom = page.evaluate("() => document.body.scrollWidth")
        no_h_scroll_custom = (s_width_custom <= w_width) and (b_width_custom <= w_width)
        print(f"Design View: innerWidth={w_width}, scrollWidth={s_width_custom} (No H-Scroll: {no_h_scroll_custom})")

        # 4. Switch to Overview via mobile bottom bar
        overview_btn = page.query_selector("div.md\\:hidden button:has-text('Overview')")
        assert overview_btn, "Mobile Overview button not found in bottom bar!"
        overview_btn.click()
        page.wait_for_timeout(400)

        s_width_overview = page.evaluate("() => document.documentElement.scrollWidth")
        b_width_overview = page.evaluate("() => document.body.scrollWidth")
        no_h_scroll_overview = (s_width_overview <= w_width) and (b_width_overview <= w_width)
        print(f"Overview View: innerWidth={w_width}, scrollWidth={s_width_overview} (No H-Scroll: {no_h_scroll_overview})")

        # 5. Switch back to Content (Edit)
        content_btn = page.query_selector("div.md\\:hidden button:has-text('Content')")
        assert content_btn, "Mobile Content button not found in bottom bar!"
        content_btn.click()
        page.wait_for_timeout(400)

        s_width_content_back = page.evaluate("() => document.documentElement.scrollWidth")
        no_h_scroll_content_back = s_width_content_back <= w_width
        print(f"Back to Content View: innerWidth={w_width}, scrollWidth={s_width_content_back} (No H-Scroll: {no_h_scroll_content_back})")

        all_pass = no_h_scroll_content and no_h_scroll_preview and no_h_scroll_custom and no_h_scroll_overview and no_h_scroll_content_back and preview_visible

        results = {
            "viewport": {"width": 390, "height": 844},
            "content_tab": {"scrollWidth": s_width, "innerWidth": w_width, "no_horizontal_scroll": no_h_scroll_content},
            "preview_tab": {"scrollWidth": s_width_preview, "innerWidth": w_width, "no_horizontal_scroll": no_h_scroll_preview, "preview_rendered": preview_visible},
            "customize_tab": {"scrollWidth": s_width_custom, "innerWidth": w_width, "no_horizontal_scroll": no_h_scroll_custom},
            "overview_tab": {"scrollWidth": s_width_overview, "innerWidth": w_width, "no_horizontal_scroll": no_h_scroll_overview},
            "overall_status": "PASS" if all_pass else "FAIL"
        }

        # Take mobile screenshot
        mobile_img = ARTIFACT_DIR / "mobile_preview_390x844.png"
        page.screenshot(path=str(mobile_img))
        print(f"Captured mobile preview screenshot -> {mobile_img.name}")

        browser.close()

    summary_file = ARTIFACT_DIR / "mobile_verification.json"
    summary_file.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nMobile verification summary written to: {summary_file}")
    assert results["overall_status"] == "PASS"

if __name__ == "__main__":
    test_mobile_layout()
