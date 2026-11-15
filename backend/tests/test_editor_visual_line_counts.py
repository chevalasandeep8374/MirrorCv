"""Playwright browser test comparing browser visual DOM line counts
with measure_lines font-advance word-wrap simulation for editor resumes.
Tests bold run advances across editor font families (Inter, Roboto, Merriweather, Playfair Display).
"""

import pytest
import asyncio
from playwright.async_api import async_playwright
from app.services.docx_rendering_measurements import measure_lines


TEST_FONTS = [
    {"name": "Inter", "css": "Inter, sans-serif"},
    {"name": "Roboto", "css": "Roboto, sans-serif"},
    {"name": "Merriweather", "css": "Merriweather, serif"},
    {"name": "Playfair Display", "css": "'Playfair Display', serif"},
]

SAMPLE_BULLETS = [
    # 1-line bullet
    "Engineered distributed backend APIs with Python and PostgreSQL.",
    # 2-line bullet with bold runs
    "Architected high-throughput **microservices** using **Python**, **FastAPI**, and **PostgreSQL**, optimizing database queries and cutting p99 latency across distributed clusters.",
    # Multi-line bullet with links and bold
    "Collaborated cross-functionally to drive **cloud infrastructure migration** onto **AWS**, maintaining developer documentation at [Project Docs](https://github.com/acme/docs) with zero downtime.",
]


@pytest.mark.asyncio
async def test_editor_visual_line_counts_against_measure_lines():
    """Renders editor resume bullets in a headless browser and compares
    visual rendered DOM line counts against measure_lines word-wrap simulator.
    """
    # Editor geometry: A4 width 595.28 pt minus 2 * 54 pt margins = 487.28 pt
    line_width_pt = 487.28
    font_size_pt = 10.5
    line_height_multiplier = 1.35

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # Build test harness HTML
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    margin: 0;
                    padding: 20px;
                    background: #fff;
                }}
                .bullet-container {{
                    width: {line_width_pt}pt;
                    font-size: {font_size_pt}pt;
                    line-height: {line_height_multiplier};
                    margin-bottom: 20px;
                    word-wrap: break-word;
                    overflow-wrap: break-word;
                    white-space: normal;
                }}
                b, strong {{
                    font-weight: 700;
                }}
            </style>
        </head>
        <body>
            <div id="test-root"></div>
        </body>
        </html>
        """
        await page.set_content(html_content)

        mismatches = []
        total_evaluations = 0

        for font in TEST_FONTS:
            font_family = font["name"]
            font_css = font["css"]

            for idx, text in enumerate(SAMPLE_BULLETS):
                total_evaluations += 1

                # Convert markdown bold **word** to <b>word</b> and links [label](url) to <a href="url">label</a> for HTML
                import re
                html_text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r'<a href="#">\1</a>', text)
                html_text = re.sub(r"\*\*([^\*]+)\*\*", r"<b>\1</b>", html_text)

                # Set inner HTML of test element in browser
                eval_script = f"""
                (() => {{
                    const root = document.getElementById('test-root');
                    root.innerHTML = '';
                    const div = document.createElement('div');
                    div.className = 'bullet-container';
                    div.style.fontFamily = "{font_css}";
                    div.innerHTML = `{html_text}`;
                    root.appendChild(div);

                    const computed = window.getComputedStyle(div);
                    const lineHeight = parseFloat(computed.lineHeight);
                    const clientHeight = div.clientHeight;
                    const lines = Math.round(clientHeight / lineHeight);
                    return lines;
                }})()
                """
                browser_lines = await page.evaluate(eval_script)

                # Run measure_lines with identical geometry and bold run advances
                slot_params = {
                    "line_width_pt": line_width_pt,
                    "formatting": {
                        "font_family": font_family,
                        "font_size_pt": font_size_pt,
                        "bold": False,
                    },
                }
                simulated_lines = measure_lines(text, slot_params)

                diff = abs(browser_lines - simulated_lines)
                print(
                    f"[{font_family:16}] Bullet {idx+1}: Browser={browser_lines} lines | "
                    f"Simulated={simulated_lines} lines | Diff={diff}"
                )

                # Allow at most 0 or 1 line difference on boundary wraps across system font rasterizers
                if diff > 1:
                    mismatches.append(
                        f"Font '{font_family}' bullet {idx+1}: Browser had {browser_lines} lines, "
                        f"simulated had {simulated_lines} lines (diff {diff} > 1)"
                    )

        await browser.close()

        print(f"\nTotal evaluations: {total_evaluations}")
        print(f"Mismatches (> 1 line diff): {len(mismatches)}")
        assert len(mismatches) == 0, f"Excessive line measurement drift: {mismatches}"
