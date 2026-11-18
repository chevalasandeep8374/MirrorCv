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

        # 1. Click on "Collapse All" to collapse everything
        collapse_btn = page.locator("button:has-text('Collapse All')").first
        if collapse_btn.is_visible():
            collapse_btn.click()
            page.wait_for_timeout(600)
            path_collapsed = os.path.join(OUTPUT_DIR, "stitch_content_all_collapsed.png")
            page.screenshot(path=path_collapsed)
            print(f"Captured all collapsed view: {path_collapsed}")

        # 2. Click on "Technical Skills" stage to expand it
        skills_stage = page.locator("text='Technical Skills'").first
        if skills_stage.is_visible():
            skills_stage.click()
            page.wait_for_timeout(800)
            path_skills = os.path.join(OUTPUT_DIR, "stitch_content_skills_expanded_clean.png")
            page.screenshot(path=path_skills)
            print(f"Captured clean skills expanded view: {path_skills}")

        # 3. Click on "Work Experience" stage to expand it
        exp_stage = page.locator("text='Work Experience'").first
        if exp_stage.is_visible():
            exp_stage.click()
            page.wait_for_timeout(800)
            path_exp = os.path.join(OUTPUT_DIR, "stitch_content_experience_expanded.png")
            page.screenshot(path=path_exp)
            print(f"Captured experience expanded view: {path_exp}")

        # 4. Click on "Professional Summary" stage to expand it
        sum_stage = page.locator("text='Professional Summary'").first
        if sum_stage.is_visible():
            sum_stage.click()
            page.wait_for_timeout(800)
            path_sum = os.path.join(OUTPUT_DIR, "stitch_content_summary_expanded.png")
            page.screenshot(path=path_sum)
            print(f"Captured summary expanded view: {path_sum}")

        browser.close()

if __name__ == "__main__":
    verify()
