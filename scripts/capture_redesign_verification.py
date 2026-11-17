import os
import subprocess
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "redesign_reference" / "verified_pages"
ARTIFACT_DIR = Path("C:/Users/CH SANDEEP/.gemini/antigravity/brain/e3539cfe-1379-4d58-868f-a3ad5b4c09bd/redesign_reference/verified_pages")

OUT_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

print("Starting Next.js production server for visual verification...")
server_proc = subprocess.Popen(
    ["npm.cmd", "--prefix", "frontend", "start"],
    cwd=str(ROOT),
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    shell=True,
)

time.sleep(4)

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        pages_to_capture = [
            ("landing_1440", "http://localhost:3000", {"width": 1440, "height": 900}),
            ("landing_1024", "http://localhost:3000", {"width": 1024, "height": 800}),
            ("landing_768", "http://localhost:3000", {"width": 768, "height": 900}),
            ("landing_390", "http://localhost:3000", {"width": 390, "height": 844}),
            ("pricing_1440", "http://localhost:3000/pricing", {"width": 1440, "height": 900}),
            ("changelog_1440", "http://localhost:3000/changelog", {"width": 1440, "height": 900}),
            ("login_1440", "http://localhost:3000/login", {"width": 1440, "height": 900}),
            ("register_1440", "http://localhost:3000/register", {"width": 1440, "height": 900}),
            ("dashboard_1440", "http://localhost:3000/dashboard", {"width": 1440, "height": 900}),
        ]

        for label, url, vp in pages_to_capture:
            page = browser.new_page(viewport=vp)
            print(f"Loading {url} at {vp['width']}x{vp['height']}...")
            try:
                page.goto(url, wait_until="networkidle", timeout=12000)
            except Exception as e:
                print(f"Network idle timeout on {url}, continuing with load...")
                page.wait_for_timeout(1000)

            out_file = f"verified_{label}.png"
            page.screenshot(path=str(OUT_DIR / out_file), full_page=True)
            page.screenshot(path=str(ARTIFACT_DIR / out_file), full_page=True)
            print(f"Captured: {out_file}")
            page.close()

        browser.close()
finally:
    print("Stopping test server...")
    server_proc.terminate()
    try:
        server_proc.wait(timeout=3)
    except:
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(server_proc.pid)], shell=True)

print("Verification screenshots completed successfully!")
