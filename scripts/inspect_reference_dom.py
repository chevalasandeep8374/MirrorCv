from playwright.sync_api import sync_playwright

def inspect():
    with sync_playwright() as p:
        b = p.chromium.launch()
        
        # 1. Landing
        pg = b.new_page(viewport={"width": 1440, "height": 900})
        pg.goto("https://taskflow-marketing-612994.hostingersite.com/", wait_until="domcontentloaded")
        print("=== LANDING SECTIONS ===")
        sections = pg.query_selector_all("header, section, footer")
        for idx, s in enumerate(sections):
            cls = s.get_attribute("class") or ""
            id_attr = s.get_attribute("id") or ""
            text = s.inner_text().strip().replace("\n", "   ")[:150]
            print(f"[{idx}] <{s.evaluate('el => el.tagName')}> class='{cls}' id='{id_attr}':\n    {text}\n")
        
        # 2. Pricing
        print("=== PRICING PAGE ===")
        pg.goto("https://taskflow-marketing-612994.hostingersite.com/pricing", wait_until="domcontentloaded")
        pricing_cards = pg.query_selector_all(".pricing-card, [class*='pricing'], [class*='plan']")
        for idx, c in enumerate(pricing_cards[:10]):
            cls = c.get_attribute("class") or ""
            text = c.inner_text().strip().replace("\n", "   ")[:120]
            print(f"Card [{idx}] class='{cls}': {text}")
            
        # 3. Workspace mockup
        print("=== WORKSPACE PAGE ===")
        pg.goto("https://taskflow-marketing-612994.hostingersite.com/workspace", wait_until="domcontentloaded")
        sidebar = pg.query_selector(".workspace-sidebar, [class*='sidebar'], aside")
        if sidebar:
            print("Sidebar found:", sidebar.inner_text().strip().replace("\n", "   ")[:200])
        main_content = pg.query_selector(".workspace-main, [class*='content'], main")
        if main_content:
            print("Workspace main found:", main_content.inner_text().strip().replace("\n", "   ")[:200])

        b.close()

if __name__ == "__main__":
    inspect()
