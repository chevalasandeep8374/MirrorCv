import os
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
        page.wait_for_timeout(1500)

        # Click on "AI Tools" in the top navigation bar
        print("Clicking AI Tools tab...")
        ai_tab = page.get_by_text("AI Tools", exact=False).first
        ai_tab.click()
        page.wait_for_timeout(800)

        # 1. Capture full AI Tools active state
        screenshot_path = os.path.join(OUTPUT_DIR, "editor_ai_tools_active.png")
        page.screenshot(path=screenshot_path)
        print(f"Captured: {screenshot_path}")

        # 2. Test clicking "+ Inject to Skills"
        inject_btn = page.get_by_text("+ Inject to Skills", exact=False).first
        if inject_btn.is_visible():
            print("Clicking '+ Inject to Skills'...")
            inject_btn.click()
            page.wait_for_timeout(500)

        # 3. Test clicking "Apply to Resume"
        apply_btn = page.get_by_text("Apply to Resume", exact=False).first
        if apply_btn.is_visible():
            print("Clicking 'Apply to Resume'...")
            apply_btn.click()
            page.wait_for_timeout(500)

        applied_screenshot_path = os.path.join(OUTPUT_DIR, "editor_ai_tools_applied.png")
        page.screenshot(path=applied_screenshot_path)
        print(f"Captured: {applied_screenshot_path}")

        browser.close()

if __name__ == "__main__":
    verify()
