import sys
import time
from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1440, 'height': 900})
        page = context.new_page()

        print("Navigating to http://localhost:3000/editor/demo%20resume%201...")
        page.goto('http://localhost:3000/editor/demo%20resume%201', wait_until='networkidle')
        page.wait_for_timeout(2000)

        # Click 1-Page Fit button
        one_page_btn = page.locator("button:has-text('1-Page Fit')").first
        if one_page_btn.count() > 0:
            one_page_btn.click()
            page.wait_for_timeout(1000)

        # Scroll preview down to bottom
        preview_container = page.locator(".flex-1.bg-\\[\\#ECEEF2\\]").first
        if preview_container.count() > 0:
            preview_container.evaluate("el => el.scrollTop = 400")
            page.wait_for_timeout(500)
            page.screenshot(path=r'C:\Users\CH SANDEEP\.gemini\antigravity\brain\e3539cfe-1379-4d58-868f-a3ad5b4c09bd\editor_stages_verification\one_page_fit_bottom_clean.png')
            print("Captured one_page_fit_bottom_clean.png")

        browser.close()

if __name__ == '__main__':
    main()
