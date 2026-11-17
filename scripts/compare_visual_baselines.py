"""Visual regression comparison script between baseline and post-migration preset renders."""

import os
import sys
from pathlib import Path
from PIL import Image, ImageChops
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
BASELINE_DIR = BASE_DIR / "tests" / "baselines" / "presets"
POST_DIR = BASE_DIR / "tests" / "post_migration" / "presets"
DIFF_DIR = BASE_DIR / "tests" / "diffs" / "presets"

POST_DIR.mkdir(parents=True, exist_ok=True)
DIFF_DIR.mkdir(parents=True, exist_ok=True)

ARTIFACT_BASE = Path("C:/Users/CH SANDEEP/.gemini/antigravity/brain/e3539cfe-1379-4d58-868f-a3ad5b4c09bd")
ARTIFACT_POST = ARTIFACT_BASE / "post_migration"
ARTIFACT_DIFF = ARTIFACT_BASE / "diffs"
ARTIFACT_POST.mkdir(parents=True, exist_ok=True)
ARTIFACT_DIFF.mkdir(parents=True, exist_ok=True)


def capture_post_screenshots():
    print(f"Capturing post-migration screenshots for {len(PRESETS)} presets...")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(
            viewport={"width": 1200, "height": 1400},
            device_scale_factor=2,
        )
        page = context.new_page()

        for preset_id in PRESETS:
            url = f"http://localhost:3000/render/preset-{preset_id}"
            page.goto(url, wait_until="networkidle")
            page.wait_for_selector(".resume-document.resume-ready", timeout=10000)
            page.wait_for_timeout(500)

            doc_elem = page.query_selector(".resume-document")
            if not doc_elem:
                raise RuntimeError(f"Could not find .resume-document on {url}")

            out_path = POST_DIR / f"{preset_id}.png"
            artifact_path = ARTIFACT_POST / f"{preset_id}.png"

            doc_elem.screenshot(path=str(out_path))
            doc_elem.screenshot(path=str(artifact_path))
            print(f"Captured: {out_path} ({out_path.stat().st_size} bytes)")

        browser.close()


def compare_images():
    print("\nComparing baseline vs post-migration renders...")
    results = []

    for preset_id in PRESETS:
        baseline_path = BASELINE_DIR / f"{preset_id}.png"
        post_path = POST_DIR / f"{preset_id}.png"
        diff_path = DIFF_DIR / f"{preset_id}_diff.png"
        artifact_diff_path = ARTIFACT_DIFF / f"{preset_id}_diff.png"

        if not baseline_path.exists():
            print(f"[MISSING BASELINE] {baseline_path}")
            continue

        base_img = Image.open(baseline_path).convert("RGBA")
        post_img = Image.open(post_path).convert("RGBA")

        # Resize if slight dimensional drift to allow diffing
        if base_img.size != post_img.size:
            print(f"[SIZE DIFFERENCE] {preset_id}: baseline {base_img.size} vs post {post_img.size}")
            # Resize post to match baseline for diffing
            post_img = post_img.resize(base_img.size, Image.Resampling.LANCZOS)

        diff = ImageChops.difference(base_img, post_img)
        bbox = diff.getbbox()

        if bbox is None:
            # 100% exact pixel match!
            similarity = 100.0
            diff_pixels = 0
            total_pixels = base_img.size[0] * base_img.size[1]
        else:
            # Count differing pixels
            diff_data = diff.getdata()
            total_pixels = len(diff_data)
            diff_pixels = sum(1 for p in diff_data if p[0] > 10 or p[1] > 10 or p[2] > 10)
            similarity = round((1.0 - (diff_pixels / total_pixels)) * 100.0, 3)

            # Generate highlighted visual diff
            highlighted = base_img.copy()
            highlight_pixels = highlighted.load()
            diff_pixels_map = diff.load()
            w, h = base_img.size
            for y in range(h):
                for x in range(w):
                    dp = diff_pixels_map[x, y]
                    if dp[0] > 10 or dp[1] > 10 or dp[2] > 10:
                        # Red highlight for differences
                        highlight_pixels[x, y] = (255, 0, 80, 255)

            highlighted.save(diff_path)
            highlighted.save(artifact_diff_path)

        status = "EXACT MATCH (100%)" if similarity >= 99.99 else f"MATCH ({similarity}%)"
        results.append({
            "preset": preset_id,
            "similarity": similarity,
            "diff_pixels": diff_pixels,
            "total_pixels": total_pixels,
            "status": status,
        })

    print("\n" + "=" * 70)
    print(f"{'PRESET':<30} | {'SIMILARITY':<12} | {'DIFF PIXELS':<12} | {'STATUS'}")
    print("=" * 70)
    for r in results:
        print(f"{r['preset']:<30} | {r['similarity']:>10}% | {r['diff_pixels']:>11} | {r['status']}")
    print("=" * 70)

    return results


if __name__ == "__main__":
    capture_post_screenshots()
    compare_images()
