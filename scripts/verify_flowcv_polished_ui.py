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

        # 1. Capture clean initial state
        page.screenshot(path=r'C:\Users\CH SANDEEP\.gemini\antigravity\brain\e3539cfe-1379-4d58-868f-a3ad5b4c09bd\editor_stages_verification\flowcv_clean_initial.png')
        print("Captured flowcv_clean_initial.png")

        # 2. Hover over "Work Experience" card to verify hover actions appear
        work_exp = page.locator("text='Work Experience'").first
        if work_exp.count() > 0:
            work_exp.hover()
            page.wait_for_timeout(500)
            page.screenshot(path=r'C:\Users\CH SANDEEP\.gemini\antigravity\brain\e3539cfe-1379-4d58-868f-a3ad5b4c09bd\editor_stages_verification\flowcv_hover_work_experience.png')
            print("Captured flowcv_hover_work_experience.png")

        # 3. Click "Work Experience" card to toggle expansion
        work_exp.click()
        page.wait_for_timeout(800)
        page.screenshot(path=r'C:\Users\CH SANDEEP\.gemini\antigravity\brain\e3539cfe-1379-4d58-868f-a3ad5b4c09bd\editor_stages_verification\flowcv_work_experience_expanded.png')
        print("Captured flowcv_work_experience_expanded.png")

        # 4. Click "+ Add Content" button to show modal
        add_btn = page.locator("button:has-text('Add Content')").first
        if add_btn.count() > 0:
            add_btn.click()
            page.wait_for_timeout(600)
            page.screenshot(path=r'C:\Users\CH SANDEEP\.gemini\antigravity\brain\e3539cfe-1379-4d58-868f-a3ad5b4c09bd\editor_stages_verification\flowcv_add_content_modal.png')
            print("Captured flowcv_add_content_modal.png")

        browser.close()
        print("All verification screenshots captured successfully!")

if __name__ == '__main__':
    main()
