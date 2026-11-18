import os
from playwright.sync_api import sync_playwright

OUTPUT_DIR = r"C:\Users\CH SANDEEP\.gemini\antigravity\brain\e3539cfe-1379-4d58-868f-a3ad5b4c09bd\editor_stages_verification"

def verify():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        page.goto("http://localhost:3000/editor/demo-resume-1", wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(2000)

        # Expand Work Experience
        page.locator("h3:has-text('Work Experience')").first.click()
        page.wait_for_timeout(600)

        # Scroll to the bottom of Work Experience
        scrollable = page.locator("div.overflow-y-auto").first
        scrollable.evaluate("el => el.scrollTop = 2400")
        page.wait_for_timeout(600)

        path_toolbar = os.path.join(OUTPUT_DIR, "verified_stage_toolbar_purple_ai.png")
        page.screenshot(path=path_toolbar)
        print(f"Captured: {path_toolbar}", flush=True)

        browser.close()

if __name__ == "__main__":
    verify()
