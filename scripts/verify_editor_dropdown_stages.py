import os
import sys
from playwright.sync_api import sync_playwright

OUTPUT_DIR = r"C:\Users\CH SANDEEP\.gemini\antigravity\brain\e3539cfe-1379-4d58-868f-a3ad5b4c09bd\editor_stages_verification"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def verify():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        print("Navigating to http://localhost:3000/editor/demo-resume-1 ...")
        page.goto("http://localhost:3000/editor/demo-resume-1", wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(2000)

        # 1. Capture full editor in collapsed state
        screenshot_path = os.path.join(OUTPUT_DIR, "editor_stages_collapsed.png")
        page.screenshot(path=screenshot_path)
        print(f"Captured: {screenshot_path}")

        # 2. Click on the first stage (e.g. Personal Details or Summary) to test expansion
        # Find all dropdown stage headers
        stage_triggers = page.locator("div[class*='cursor-pointer']").all()
        print(f"Found {len(stage_triggers)} potential clickable stage triggers.")

        # Click on "Summary" or the first section
        summary_trigger = page.get_by_text("Professional Summary", exact=False).first
        if summary_trigger.is_visible():
            summary_trigger.click()
            page.wait_for_timeout(500)
            expanded_path = os.path.join(OUTPUT_DIR, "editor_stages_summary_expanded.png")
            page.screenshot(path=expanded_path)
            print(f"Captured: {expanded_path}")

        browser.close()

if __name__ == "__main__":
    verify()
