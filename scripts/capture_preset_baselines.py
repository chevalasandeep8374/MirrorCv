"""Capture baseline PNG screenshots of all 8 presets on current code before any renderer changes."""

import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

PRESETS = [
    "classic-single-column",
    "modern-sidebar-left",
    "executive-sidebar-right",
    "header-banner",
    "compact-dense",
    "creative-accent",
    "minimal-editorial",
    "academic-cv",
]

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "tests" / "baselines" / "presets"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ARTIFACT_DIR = Path("C:/Users/CH SANDEEP/.gemini/antigravity/brain/3851a65a-681b-4352-8b81-b39225ebec7c/baselines")
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)


def capture_all():
    print(f"Capturing baseline screenshots for {len(PRESETS)} presets...")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        # Standard A4 viewport at 96 DPI: 794 x 1123, deviceScaleFactor 2 for crisp text
        context = browser.new_context(
            viewport={"width": 1200, "height": 1400},
            device_scale_factor=2,
        )
        page = context.new_page()

        for preset_id in PRESETS:
            url = f"http://localhost:3000/render/preset-{preset_id}"
            print(f"Loading {url}...")
            page.goto(url, wait_until="networkidle")
            page.wait_for_selector(".resume-document.resume-ready", timeout=10000)
            page.wait_for_timeout(500)  # Brief delay for font settling

            # Select the resume document container or first page view
            doc_elem = page.query_selector(".resume-document")
            if not doc_elem:
                raise RuntimeError(f"Could not find .resume-document on {url}")

            out_path = OUTPUT_DIR / f"{preset_id}.png"
            artifact_path = ARTIFACT_DIR / f"{preset_id}.png"

            doc_elem.screenshot(path=str(out_path))
            doc_elem.screenshot(path=str(artifact_path))
            print(f"Saved: {out_path} ({out_path.stat().st_size} bytes)")

        browser.close()
    print("All 8 baseline screenshots captured successfully!")


if __name__ == "__main__":
    capture_all()
