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
        page.wait_for_timeout(1000)

        # Click on "Overview" in top navigation
        print("Clicking Overview tab...")
        overview_tab = page.get_by_text("Overview", exact=False).first
        overview_tab.click()
        page.wait_for_timeout(1000)

        # 1. Capture Overview (Documents Grid)
        doc_path = os.path.join(OUTPUT_DIR, "editor_overview_documents.png")
        page.screenshot(path=doc_path)
        print(f"Captured: {doc_path}")

        # 2. Click "Readiness & Health" toggle
        health_btn = page.get_by_text("Readiness & Health", exact=False).first
        if health_btn.is_visible():
            print("Clicking 'Readiness & Health' toggle...")
            health_btn.click()
            page.wait_for_timeout(600)
            health_path = os.path.join(OUTPUT_DIR, "editor_overview_health.png")
            page.screenshot(path=health_path)
            print(f"Captured: {health_path}")

        browser.close()

if __name__ == "__main__":
    verify()
