from playwright.sync_api import sync_playwright

def inspect_hero_stage():
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1440, "height": 900})
        pg.goto("https://taskflow-marketing-612994.hostingersite.com/", wait_until="domcontentloaded")
        
        stage = pg.query_selector(".hero-stage")
        if stage:
            print("Hero Stage HTML structure:")
            print(stage.inner_html()[:2500])
        else:
            print("Hero stage not found!")
            
        b.close()

if __name__ == "__main__":
    inspect_hero_stage()
