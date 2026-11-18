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

        # 1. Capture default initial view with Personal Details expanded
        path_initial = os.path.join(OUTPUT_DIR, "verified_stage_personal_expanded.png")
        page.screenshot(path=path_initial)
        print(f"Captured: {path_initial}", flush=True)

        # 2. Click "Professional Summary" header to expand Summary stage
        print("Expanding Professional Summary...", flush=True)
        page.locator("h3:has-text('Professional Summary')").first.click()
        page.wait_for_timeout(800)
        path_sum = os.path.join(OUTPUT_DIR, "verified_stage_summary_expanded.png")
        page.screenshot(path=path_sum)
        print(f"Captured: {path_sum}", flush=True)

        # 3. Click "Work Experience" header to expand Experience stage
        print("Expanding Work Experience...", flush=True)
        page.locator("h3:has-text('Work Experience')").first.click()
        page.wait_for_timeout(800)
        path_exp = os.path.join(OUTPUT_DIR, "verified_stage_experience_expanded.png")
        page.screenshot(path=path_exp)
        print(f"Captured: {path_exp}", flush=True)

        # 4. Click "Technical Skills" header to expand Skills stage
        print("Expanding Technical Skills...", flush=True)
        page.locator("h3:has-text('Technical Skills')").first.click()
        page.wait_for_timeout(800)
        path_skills = os.path.join(OUTPUT_DIR, "verified_stage_skills_expanded.png")
        page.screenshot(path=path_skills)
        print(f"Captured: {path_skills}", flush=True)

        browser.close()
        print("Verification complete!", flush=True)

if __name__ == "__main__":
    verify()
