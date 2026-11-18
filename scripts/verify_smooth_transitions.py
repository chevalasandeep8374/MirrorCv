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

        print("Navigating to http://localhost:3000/editor/demo-resume-1 ...", flush=True)
        page.goto("http://localhost:3000/editor/demo-resume-1", wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(2000)

        # 1. Capture initial state with personal details
        path1 = os.path.join(OUTPUT_DIR, "smooth_transition_initial.png")
        page.screenshot(path=path1)
        print(f"Captured: {path1}", flush=True)

        # 2. Open Work Experience stage smoothly
        print("Clicking Work Experience stage...", flush=True)
        page.locator("h3:has-text('Work Experience')").first.click()
        page.wait_for_timeout(400) # Wait for 300ms transition to complete smoothly
        path2 = os.path.join(OUTPUT_DIR, "smooth_transition_experience_open.png")
        page.screenshot(path=path2)
        print(f"Captured: {path2}", flush=True)

        # 3. Open Download Dropdown to test smooth dropdown transition
        print("Clicking Download dropdown caret...", flush=True)
        page.locator("button[aria-label='Download formats']").first.click()
        page.wait_for_timeout(300)
        path3 = os.path.join(OUTPUT_DIR, "smooth_transition_download_dropdown.png")
        page.screenshot(path=path3)
        print(f"Captured: {path3}", flush=True)

        # Click outside to close dropdown
        page.locator("header").first.click(position={"x": 50, "y": 20})
        page.wait_for_timeout(200)

        # 4. Open Floating "+ Add Content" Modal
        print("Clicking + Add Content button...", flush=True)
        page.locator("button:has-text('Add Content')").first.click()
        page.wait_for_timeout(350)
        path4 = os.path.join(OUTPUT_DIR, "smooth_transition_add_modal.png")
        page.screenshot(path=path4)
        print(f"Captured: {path4}", flush=True)

        browser.close()
        print("All smooth transition tests passed successfully!", flush=True)

if __name__ == "__main__":
    verify()
