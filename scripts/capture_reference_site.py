import os
import sys
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

REFERENCE_URL = "https://taskflow-marketing-612994.hostingersite.com/"

ARTIFACT_DIR = Path("C:/Users/CH SANDEEP/.gemini/antigravity/brain/e3539cfe-1379-4d58-868f-a3ad5b4c09bd/redesign_reference")
LOCAL_DIR = Path(__file__).resolve().parent.parent / "redesign_reference"

ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
LOCAL_DIR.mkdir(parents=True, exist_ok=True)

VIEWPORTS = [
    {"name": "desktop_1440", "width": 1440, "height": 900},
    {"name": "tablet_landscape_1024", "width": 1024, "height": 768},
    {"name": "tablet_portrait_768", "width": 768, "height": 1024},
    {"name": "mobile_390", "width": 390, "height": 844, "is_mobile": True},
]

def capture_reference():
    print(f"Connecting to reference URL: {REFERENCE_URL}...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # 1. Capture at all requested viewports
        for vp in VIEWPORTS:
            ctx_args = {"viewport": {"width": vp["width"], "height": vp["height"]}}
            if vp.get("is_mobile"):
                ctx_args["is_mobile"] = True
                ctx_args["has_touch"] = True
                ctx_args["device_scale_factor"] = 2
            
            context = browser.new_context(**ctx_args)
            page = context.new_page()
            
            print(f"Loading {REFERENCE_URL} at {vp['width']}x{vp['height']}...")
            try:
                page.goto(REFERENCE_URL, wait_until="networkidle", timeout=30000)
            except Exception as e:
                print(f"Warning: networkidle timed out or failed: {e}. Falling back to domcontentloaded.")
                page.goto(REFERENCE_URL, wait_until="domcontentloaded", timeout=30000)
            
            page.wait_for_timeout(2000)

            # Scroll through the page to trigger any lazy-loaded elements or animations
            page.evaluate("""async () => {
                await new Promise((resolve) => {
                    let totalHeight = 0;
                    const distance = 400;
                    const timer = setInterval(() => {
                        const scrollHeight = document.body.scrollHeight;
                        window.scrollBy(0, distance);
                        totalHeight += distance;
                        if(totalHeight >= scrollHeight){
                            clearInterval(timer);
                            window.scrollTo(0, 0);
                            resolve();
                        }
                    }, 100);
                });
            }""")
            page.wait_for_timeout(1000)

            # Full page screenshot
            local_shot = LOCAL_DIR / f"reference_{vp['name']}.png"
            artifact_shot = ARTIFACT_DIR / f"reference_{vp['name']}.png"
            page.screenshot(path=str(local_shot), full_page=True)
            page.screenshot(path=str(artifact_shot), full_page=True)
            print(f"Saved screenshot: {local_shot}")

            # Also check if there are subpages/navigation links in the header
            if vp["name"] == "desktop_1440":
                print("Extracting navigation links and sub-pages...")
                links = page.evaluate("""() => {
                    return Array.from(document.querySelectorAll('header a, nav a')).map(a => ({
                        text: a.innerText.trim(),
                        href: a.href
                    })).filter(l => l.href && l.href.startsWith(window.location.origin));
                }""")
                print(f"Found internal links: {links}")

                # Capture subpages if any exist
                seen_hrefs = set()
                for l in links:
                    href = l['href']
                    if href not in seen_hrefs and href != REFERENCE_URL and not href.endswith('#'):
                        seen_hrefs.add(href)
                        sub_name = href.rstrip('/').split('/')[-1] or "home"
                        try:
                            print(f"Loading subpage: {href}...")
                            sub_page = context.new_page()
                            sub_page.goto(href, wait_until="domcontentloaded", timeout=15000)
                            sub_page.wait_for_timeout(1500)
                            sub_local = LOCAL_DIR / f"reference_sub_{sub_name}_1440.png"
                            sub_artifact = ARTIFACT_DIR / f"reference_sub_{sub_name}_1440.png"
                            sub_page.screenshot(path=str(sub_local), full_page=True)
                            sub_page.screenshot(path=str(sub_artifact), full_page=True)
                            print(f"Saved subpage screenshot: {sub_local}")
                            sub_page.close()
                        except Exception as err:
                            print(f"Could not capture {href}: {err}")

            context.close()

        # 2. Extract in-depth computed styles from desktop 1440
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()
        page.goto(REFERENCE_URL, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(2000)

        print("\nExtracting computed styles across all DOM elements...")
        computed_data = page.evaluate("""() => {
            const allElements = Array.from(document.querySelectorAll('*'));
            
            const colors = new Set();
            const backgrounds = new Set();
            const borders = new Set();
            const fontFamilies = new Set();
            const fontSizes = new Set();
            const fontWeights = new Set();
            const lineHeights = new Set();
            const letterSpacings = new Set();
            const radii = new Set();
            const shadows = new Set();
            const transitions = new Set();
            
            const elementsSummary = [];

            allElements.forEach(el => {
                const style = window.getComputedStyle(el);
                if (style.color && style.color !== 'rgba(0, 0, 0, 0)') colors.add(style.color);
                if (style.backgroundColor && style.backgroundColor !== 'rgba(0, 0, 0, 0)') backgrounds.add(style.backgroundColor);
                if (style.borderColor && style.borderWidth !== '0px') borders.add(`${style.borderWidth} ${style.borderStyle} ${style.borderColor}`);
                if (style.fontFamily) fontFamilies.add(style.fontFamily);
                if (style.fontSize) fontSizes.add(style.fontSize);
                if (style.fontWeight) fontWeights.add(style.fontWeight);
                if (style.lineHeight) lineHeights.add(style.lineHeight);
                if (style.letterSpacing) letterSpacings.add(style.letterSpacing);
                if (style.borderRadius && style.borderRadius !== '0px') radii.add(style.borderRadius);
                if (style.boxShadow && style.boxShadow !== 'none') shadows.add(style.boxShadow);
                if (style.transition && style.transition !== 'none' && !style.transition.startsWith('all 0s')) transitions.add(style.transition);
            });

            // Specific key component inspection
            const inspectSelectors = [
                { role: 'body', selector: 'body' },
                { role: 'header', selector: 'header' },
                { role: 'hero_h1', selector: 'h1' },
                { role: 'h2', selector: 'h2' },
                { role: 'h3', selector: 'h3' },
                { role: 'p', selector: 'p' },
                { role: 'primary_button', selector: 'a[class*=\"primary\"], button[class*=\"primary\"], .btn-primary, header a:last-child, main button, main a.bg-' },
                { role: 'secondary_button', selector: 'a[class*=\"secondary\"], button[class*=\"secondary\"], .btn-secondary' },
                { role: 'pill_badge', selector: '[class*=\"pill\"], [class*=\"badge\"], [class*=\"tag\"], [class*=\"rounded-full\"]' },
                { role: 'cards', selector: '[class*=\"card\"], [class*=\"rounded-2xl\"], [class*=\"rounded-xl\"], [class*=\"rounded-lg\"], [class*=\"shadow\"]' },
                { role: 'container', selector: '[class*=\"container\"], [class*=\"max-w-\"], main > div, section > div' },
                { role: 'footer', selector: 'footer' }
            ];

            const components = [];
            inspectSelectors.forEach(({ role, selector }) => {
                const els = Array.from(document.querySelectorAll(selector));
                els.slice(0, 5).forEach((el, idx) => {
                    const cs = window.getComputedStyle(el);
                    components.push({
                        role: `${role}_${idx}`,
                        tagName: el.tagName,
                        className: el.className,
                        textSnippet: el.innerText ? el.innerText.slice(0, 80).replace(/\\n/g, ' ') : '',
                        color: cs.color,
                        backgroundColor: cs.backgroundColor,
                        borderColor: cs.borderColor,
                        borderWidth: cs.borderWidth,
                        borderRadius: cs.borderRadius,
                        boxShadow: cs.boxShadow,
                        fontFamily: cs.fontFamily,
                        fontSize: cs.fontSize,
                        fontWeight: cs.fontWeight,
                        lineHeight: cs.lineHeight,
                        letterSpacing: cs.letterSpacing,
                        padding: `${cs.paddingTop} ${cs.paddingRight} ${cs.paddingBottom} ${cs.paddingLeft}`,
                        margin: `${cs.marginTop} ${cs.marginRight} ${cs.marginBottom} ${cs.marginLeft}`,
                        width: cs.width,
                        maxWidth: cs.maxWidth,
                        gap: cs.gap,
                        display: cs.display
                    });
                });
            });

            return {
                title: document.title,
                colors: Array.from(colors),
                backgrounds: Array.from(backgrounds),
                borders: Array.from(borders),
                fontFamilies: Array.from(fontFamilies),
                fontSizes: Array.from(fontSizes).sort((a,b) => parseFloat(a) - parseFloat(b)),
                fontWeights: Array.from(fontWeights).sort((a,b) => parseInt(a) - parseInt(b)),
                lineHeights: Array.from(lineHeights),
                letterSpacings: Array.from(letterSpacings),
                radii: Array.from(radii),
                shadows: Array.from(shadows),
                transitions: Array.from(transitions),
                components
            };
        }""")

        browser.close()

        # Save computed data
        out_local = LOCAL_DIR / "reference_styles.json"
        out_artifact = ARTIFACT_DIR / "reference_styles.json"
        out_local.write_text(json.dumps(computed_data, indent=2), encoding="utf-8")
        out_artifact.write_text(json.dumps(computed_data, indent=2), encoding="utf-8")
        print(f"\nExtracted computed styles saved to {out_local} and {out_artifact}")

if __name__ == "__main__":
    capture_reference()
