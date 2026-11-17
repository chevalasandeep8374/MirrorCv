import json
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page()
    sample = {
        "id": "custom-1",
        "title": "Custom Test Resume",
        "content": {
            "schema_version": "1.1.0",
            "header": {
                "name": "TEST CANDIDATE",
                "title": "Software Engineer",
                "email": "test@test.com",
                "phone": "123",
                "location": "NY",
                "website": "test.com",
                "links": []
            },
            "sections": []
        },
        "style": {
            "schema_version": "1.1.0",
            "templateId": "classic-single-column",
            "pageSize": "A4",
            "locale": "en",
            "bulletStyle": "disc",
            "headingStyle": "underline",
            "layout": {
                "type": "single",
                "sidebarWidthPercent": 33,
                "sidebarSectionIds": [],
                "mainSectionIds": []
            },
            "typography": {
                "baseFontFamily": "Inter",
                "headingFontFamily": "Inter",
                "baseFontSize": 9.5,
                "lineHeight": 1.4
            },
            "spacing": {
                "sectionSpacing": 14,
                "itemSpacing": 8,
                "bulletSpacing": 3,
                "headerBottomSpacing": 16,
                "unit": "pt"
            },
            "margins": {
                "top": 36,
                "bottom": 36,
                "left": 42,
                "right": 42,
                "unit": "pt"
            },
            "colors": {
                "accent": "#2563eb",
                "text": "#0f172a",
                "muted": "#64748b",
                "background": "#ffffff",
                "sidebarBackground": "#f8fafc",
                "divider": "#e2e8f0"
            }
        }
    }
    pg.goto("http://localhost:3000/render/custom")
    pg.evaluate(f"localStorage.setItem('matrix_resume', {json.dumps(json.dumps(sample))});")
    pg.reload(wait_until="networkidle")
    print("Full body content:", pg.evaluate("document.body.innerText"))
    print("Full HTML snippet:", pg.evaluate("document.body.innerHTML.substring(0, 300)"))
    b.close()
