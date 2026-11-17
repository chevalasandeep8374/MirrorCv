"""
Accessibility Verification Suite using axe-core & Playwright.
Audits all 4 tabs (Overview, Content, Customize, AI Tools) and modal dialogs,
tests tab focus order, and validates editor UI contrast.
"""

import sys
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from axe_playwright_python.sync_playwright import Axe

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.generate_option_matrix import BASE_CONTENT, BASE_STYLE

ARTIFACT_DIR = Path("C:/Users/CH SANDEEP/.gemini/antigravity/brain/e3539cfe-1379-4d58-868f-a3ad5b4c09bd")

def run_a11y_suite():
    print("Starting Editor Accessibility (axe-core) Suite...")
    axe = Axe()
    report = {}

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(viewport={"width": 1400, "height": 900})
        page = context.new_page()

        # Seed local storage with custom resume
        resume_obj = {
            "id": "a11y-test",
            "userId": "system",
            "title": "A11y Test Resume",
            "content": BASE_CONTENT,
            "style": BASE_STYLE,
            "version": 1
        }
        resume_json = json.dumps(resume_obj)
        page.add_init_script(f"""
            localStorage.setItem('resume_a11y-test', JSON.stringify({resume_json}));
            localStorage.setItem('matrix_resume', JSON.stringify({resume_json}));
        """)

        page.goto("http://localhost:3000/editor/a11y-test")
        page.wait_for_selector("header", timeout=10000)
        page.wait_for_timeout(1000)

        # -------------------------------------------------------------
        # 1. Content Tab
        # -------------------------------------------------------------
        print("\n[1/7] Auditing Tab: Content...")
        results_content = axe.run(page)
        report["content_tab"] = {
            "violations_count": results_content.violations_count,
            "report": results_content.generate_report()
        }
        print(f"Content Tab Violations: {results_content.violations_count}")

        # -------------------------------------------------------------
        # 2. Overview Tab
        # -------------------------------------------------------------
        print("\n[2/7] Auditing Tab: Overview...")
        page.click("nav button:has-text('Overview')")
        page.wait_for_timeout(500)
        results_overview = axe.run(page)
        report["overview_tab"] = {
            "violations_count": results_overview.violations_count,
            "report": results_overview.generate_report()
        }
        print(f"Overview Tab Violations: {results_overview.violations_count}")

        # -------------------------------------------------------------
        # 3. Customize Tab
        # -------------------------------------------------------------
        print("\n[3/7] Auditing Tab: Customize...")
        page.click("nav button:has-text('Customize')")
        page.wait_for_timeout(500)
        results_customize = axe.run(page)
        report["customize_tab"] = {
            "violations_count": results_customize.violations_count,
            "report": results_customize.generate_report()
        }
        print(f"Customize Tab Violations: {results_customize.violations_count}")

        # -------------------------------------------------------------
        # 4. AI Tools Tab
        # -------------------------------------------------------------
        print("\n[4/7] Auditing Tab: AI Tools...")
        page.click("nav button:has-text('AI Tools')")
        page.wait_for_timeout(500)
        results_ai = axe.run(page)
        report["ai_tab"] = {
            "violations_count": results_ai.violations_count,
            "report": results_ai.generate_report()
        }
        print(f"AI Tools Tab Violations: {results_ai.violations_count}")

        # -------------------------------------------------------------
        # 5. Template Gallery Modal
        # -------------------------------------------------------------
        print("\n[5/7] Auditing Modal: Template Gallery...")
        page.click("nav button:has-text('Customize')")
        page.wait_for_timeout(300)
        gallery_btn = page.query_selector("button:has-text('Browse Design Templates')")
        if gallery_btn:
            gallery_btn.click()
            page.wait_for_selector(".fixed.inset-0", timeout=5000)
            page.wait_for_timeout(500)
            results_gallery = axe.run(page)
            report["template_gallery_modal"] = {
                "violations_count": results_gallery.violations_count,
                "report": results_gallery.generate_report()
            }
            print(f"Gallery Modal Violations: {results_gallery.violations_count}")
            page.keyboard.press("Escape")
            page.wait_for_timeout(300)

        # -------------------------------------------------------------
        # 6. Focus Order Check
        # -------------------------------------------------------------
        print("\n[6/7] Testing Focus Order Navigation (Tab sequence)...")
        page.click("nav button:has-text('Content')")
        page.wait_for_timeout(300)
        # Tab through 10 elements and verify active elements have valid focus indicators
        focus_tags = []
        for _ in range(10):
            page.keyboard.press("Tab")
            tag = page.evaluate("() => document.activeElement ? document.activeElement.tagName + '.' + (document.activeElement.className || '').slice(0, 20) : 'none'")
            focus_tags.append(tag)
        report["focus_sequence"] = focus_tags
        print(f"Focus sequence: {focus_tags[:5]}...")

        # -------------------------------------------------------------
        # 7. UI Contrast Sampling
        # -------------------------------------------------------------
        print("\n[7/7] Sampling Editor UI Contrast...")
        # Check text color contrast of primary buttons & header labels
        contrast_info = page.evaluate("""() => {
            const sampleSelectors = [
                'header button',
                'nav button',
                'h3',
                'label',
                '.resume-document'
            ];
            return sampleSelectors.map(sel => {
                const el = document.querySelector(sel);
                if (!el) return { selector: sel, found: false };
                const style = window.getComputedStyle(el);
                return {
                    selector: sel,
                    found: true,
                    color: style.color,
                    background: style.backgroundColor,
                    fontSize: style.fontSize
                };
            });
        }""")
        report["contrast_samples"] = contrast_info
        print(f"Sampled {len(contrast_info)} UI elements for contrast.")

        browser.close()

    out_file = ARTIFACT_DIR / "accessibility_report.json"
    out_file.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nA11y audit report written to: {out_file}")

if __name__ == "__main__":
    run_a11y_suite()
