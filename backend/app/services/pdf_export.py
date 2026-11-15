import logging
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)


async def generate_resume_pdf(
    resume_id: str,
    page_size: str = "A4",
    render_token: Optional[str] = None,
    auth_token: Optional[str] = None,
) -> bytes:
    """Uses headless Playwright Chromium to open the /render/{resume_id} route
    and return exact 1:1 PDF bytes without browser headers/footers.
    """
    from playwright.async_api import async_playwright

    url = f"{settings.FRONTEND_URL}/render/{resume_id}"
    if render_token:
        url += f"?render_token={render_token}"
    elif auth_token:
        url += f"?token={auth_token}"

    logger.info(f"Generating PDF for resume {resume_id} from {url} (render_token={'present' if render_token else 'none'})")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--font-render-hinting=none",
            ],
        )

        context = await browser.new_context(
            viewport={"width": 1200, "height": 1600},
            device_scale_factor=2,
        )
        page = await context.new_page()

        try:
            # Navigate to print route and wait for fonts and elements to settle
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await page.wait_for_selector(".resume-ready", timeout=15000)

            # Generate exact PDF
            pdf_bytes = await page.pdf(
                format=page_size,
                print_background=True,
                prefer_css_page_size=True,
                margin={"top": "0px", "bottom": "0px", "left": "0px", "right": "0px"},
            )
            return pdf_bytes
        finally:
            await browser.close()
