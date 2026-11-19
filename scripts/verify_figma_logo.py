import sys
import time
from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1440, 'height': 900})
        page = context.new_page()

        # 1. Editor Header
        print("Navigating to http://localhost:3000/editor/demo%20resume%201...")
        page.goto('http://localhost:3000/editor/demo%20resume%201', wait_until='networkidle')
        page.wait_for_timeout(2000)
        page.screenshot(path=r'C:\Users\CH SANDEEP\.gemini\antigravity\brain\e3539cfe-1379-4d58-868f-a3ad5b4c09bd\editor_stages_verification\logo_editor_header.png')
        print("Captured logo_editor_header.png")

        # 2. Dashboard Header
        print("Navigating to http://localhost:3000/dashboard...")
        page.goto('http://localhost:3000/dashboard', wait_until='networkidle')
        page.wait_for_timeout(1500)
        page.screenshot(path=r'C:\Users\CH SANDEEP\.gemini\antigravity\brain\e3539cfe-1379-4d58-868f-a3ad5b4c09bd\editor_stages_verification\logo_dashboard_header.png')
        print("Captured logo_dashboard_header.png")

        # 3. Landing Page Header
        print("Navigating to http://localhost:3000...")
        page.goto('http://localhost:3000', wait_until='networkidle')
        page.wait_for_timeout(1500)
        page.screenshot(path=r'C:\Users\CH SANDEEP\.gemini\antigravity\brain\e3539cfe-1379-4d58-868f-a3ad5b4c09bd\editor_stages_verification\logo_landing_header.png')
        print("Captured logo_landing_header.png")

        browser.close()
        print("All Figma logo verification screenshots captured successfully!")

if __name__ == '__main__':
    main()
