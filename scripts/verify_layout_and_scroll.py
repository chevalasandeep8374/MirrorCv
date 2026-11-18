import sys
import time
from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Using desktop 1440x900 viewport
        context = browser.new_context(viewport={'width': 1440, 'height': 900})
        page = context.new_page()

        print("Navigating to http://localhost:3000/editor/demo%20resume%201...")
        page.goto('http://localhost:3000/editor/demo%20resume%201', wait_until='networkidle')
        page.wait_for_timeout(2000)

        # 1. Full view initial screenshot showing wider left panel
        page.screenshot(path=r'C:\Users\CH SANDEEP\.gemini\antigravity\brain\e3539cfe-1379-4d58-868f-a3ad5b4c09bd\editor_stages_verification\wider_panel_initial.png')
        print("Captured wider_panel_initial.png")

        # 2. Scroll the left stage container down to verify Certifications card is completely clear and + Add Content is below it
        sections_container = page.locator("#resume-sections-scroll-container").first
        if sections_container.count() > 0:
            sections_container.evaluate("el => el.scrollTop = el.scrollHeight")
            page.wait_for_timeout(800)
            page.screenshot(path=r'C:\Users\CH SANDEEP\.gemini\antigravity\brain\e3539cfe-1379-4d58-868f-a3ad5b4c09bd\editor_stages_verification\scroll_bottom_certifications_clear.png')
            print("Captured scroll_bottom_certifications_clear.png")

        # 3. Scroll preview container down to inspect bottom of resume page (ensure no double sheet)
        preview_container = page.locator(".flex-1.bg-\\[\\#ECEEF2\\]").first
        if preview_container.count() > 0:
            # Scroll down to show bottom of page 1
            preview_container.evaluate("el => el.scrollTop = 500")
            page.wait_for_timeout(800)
            page.screenshot(path=r'C:\Users\CH SANDEEP\.gemini\antigravity\brain\e3539cfe-1379-4d58-868f-a3ad5b4c09bd\editor_stages_verification\preview_bottom_single_sheet.png')
            print("Captured preview_bottom_single_sheet.png")

        browser.close()
        print("Verification complete!")

if __name__ == '__main__':
    main()
