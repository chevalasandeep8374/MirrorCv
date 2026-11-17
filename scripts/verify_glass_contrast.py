import math

def srgb_to_lin(c):
    c = c / 255.0
    if c <= 0.04045:
        return c / 12.92
    return ((c + 0.055) / 1.055) ** 2.4

def relative_luminance(r, g, b):
    return 0.2126 * srgb_to_lin(r) + 0.7152 * srgb_to_lin(g) + 0.0722 * srgb_to_lin(b)

def contrast_ratio(l1, l2):
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)

def blend(fg_rgb, fg_alpha, bg_rgb):
    return tuple(round(fg_alpha * fg + (1 - fg_alpha) * bg) for fg, bg in zip(fg_rgb, bg_rgb))

# Backdrops in the system
BACKDROPS = {
    "pure_white": (255, 255, 255),
    "faint_warm": (253, 248, 243),
    "light_blue": (219, 234, 254), # #DBEAFE
    "lavender_stage": (233, 227, 250), # #E9E3FA
    "dark_band": (22, 23, 24), # #161718
}

# Proposed Glass Tiers
# 1. Glass-1 (Chrome): 70% white, text #0F172A (slate-900) or #1E293B
# 2. Glass-2 (Floating): 80% white, text #0F172A
# 3. Glass-3 (Overlay): 85% white, text #0F172A
# 4. Glass-Card: 75% white, text #0F172A
# 5. Glass-Dark (Chips on dark): 8% white (0.08), text #F8FAFC (slate-50) over dark_band
# 6. Frosted-Solid (Editor cards): 92% white, text #1E293B, muted #475569

TIERS = [
    {
        "name": "Glass-1 (Chrome - Header, Tabs, Toolbar)",
        "fg_rgb": (255, 255, 255),
        "alpha": 0.70,
        "text_color": (15, 23, 42), # #0F172A deep slate
        "text_muted": (71, 85, 105), # #475569 slate-600
        "applicable_backdrops": ["pure_white", "faint_warm", "light_blue", "lavender_stage"]
    },
    {
        "name": "Glass-2 (Floating - Dropdowns, Popovers, Toasts)",
        "fg_rgb": (255, 255, 255),
        "alpha": 0.82,
        "text_color": (15, 23, 42),
        "text_muted": (71, 85, 105),
        "applicable_backdrops": ["pure_white", "faint_warm", "light_blue", "lavender_stage", "dark_band"]
    },
    {
        "name": "Glass-3 (Overlay - Modals, Dialogs, Side Sheets)",
        "fg_rgb": (255, 255, 255),
        "alpha": 0.88,
        "text_color": (15, 23, 42),
        "text_muted": (71, 85, 105),
        "applicable_backdrops": ["pure_white", "faint_warm", "light_blue", "lavender_stage", "dark_band"]
    },
    {
        "name": "Glass-Card (Stage Cards & Announcement Pill)",
        "fg_rgb": (255, 255, 255),
        "alpha": 0.75,
        "text_color": (15, 23, 42),
        "text_muted": (71, 85, 105),
        "applicable_backdrops": ["lavender_stage", "light_blue", "pure_white"]
    },
    {
        "name": "Glass-Dark (Chips on dark footer/band)",
        "fg_rgb": (255, 255, 255),
        "alpha": 0.08,
        "text_color": (248, 250, 252), # #F8FAFC
        "text_muted": (203, 213, 225), # #CBD5E1
        "applicable_backdrops": ["dark_band"]
    },
    {
        "name": "Frosted-Solid (Editor Content & Customize Cards)",
        "fg_rgb": (255, 255, 255),
        "alpha": 0.92,
        "text_color": (15, 23, 42),
        "text_muted": (71, 85, 105),
        "applicable_backdrops": ["pure_white", "faint_warm", "light_blue", "lavender_stage"]
    }
]

print("=" * 80)
print("GLASS SYSTEM WCAG 2.1 CONTRAST VERIFICATION REPORT")
print("Thresholds: Normal text >= 4.5:1, Large text / UI icons >= 3.0:1")
print("=" * 80)

failures = []
results = []

for tier in TIERS:
    print(f"\n--- {tier['name']} (Alpha={tier['alpha']}) ---")
    tier_results = []
    
    for bg_name in tier["applicable_backdrops"]:
        bg_rgb = BACKDROPS[bg_name]
        blended = blend(tier["fg_rgb"], tier["alpha"], bg_rgb)
        blended_lum = relative_luminance(*blended)
        
        # Primary text
        text_lum = relative_luminance(*tier["text_color"])
        cr_primary = contrast_ratio(text_lum, blended_lum)
        
        # Muted text
        muted_lum = relative_luminance(*tier["text_muted"])
        cr_muted = contrast_ratio(muted_lum, blended_lum)
        
        status_primary = "PASS (AAA)" if cr_primary >= 7.0 else ("PASS (AA)" if cr_primary >= 4.5 else "FAIL")
        status_muted = "PASS (AAA)" if cr_muted >= 7.0 else ("PASS (AA)" if cr_muted >= 4.5 else "FAIL")
        
        if cr_primary < 4.5:
            failures.append(f"{tier['name']} on {bg_name}: primary text CR {cr_primary:.2f}:1 < 4.5:1")
        if cr_muted < 4.5:
            failures.append(f"{tier['name']} on {bg_name}: muted text CR {cr_muted:.2f}:1 < 4.5:1")
            
        print(f"  Over {bg_name:15}: Blended {blended} | Primary {cr_primary:5.2f}:1 [{status_primary}] | Muted {cr_muted:5.2f}:1 [{status_muted}]")
        tier_results.append({
            "backdrop": bg_name,
            "blended": blended,
            "cr_primary": cr_primary,
            "cr_muted": cr_muted,
            "status_primary": status_primary,
            "status_muted": status_muted
        })
    results.append({"tier": tier["name"], "results": tier_results})

print("\n" + "=" * 80)
if failures:
    print(f"FAILURES DETECTED ({len(failures)}):")
    for f in failures:
        print(f"  ❌ {f}")
else:
    print("ALL TIERS PASS WCAG AA / AAA CONTRAST REQUIREMENTS AGAINST WORST CASE BACKDROPS! ✅")
print("=" * 80)
