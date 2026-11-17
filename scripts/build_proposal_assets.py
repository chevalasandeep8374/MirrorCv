import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
REF_DIR = ROOT / "redesign_reference"
MOCKUP_DIR = REF_DIR / "mockups"
COMP_DIR = REF_DIR / "comparisons"
ARTIFACT_DIR = Path("C:/Users/CH SANDEEP/.gemini/antigravity/brain/e3539cfe-1379-4d58-868f-a3ad5b4c09bd/redesign_reference/comparisons")

COMP_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

# 1. Load images
desktop_img = Image.open(REF_DIR / "reference_desktop_1440.png")
pricing_ref_img = Image.open(REF_DIR / "reference_sub_pricing_1440.png")

mockup_hero_img = Image.open(MOCKUP_DIR / "mockup_landing_hero.png")
mockup_editor_img = Image.open(MOCKUP_DIR / "mockup_resume_editor.png")
mockup_pricing_img = Image.open(MOCKUP_DIR / "mockup_pricing.png")

# Crop reference hero (header + hero + stage)
ref_hero = desktop_img.crop((0, 0, 1440, 1250))
ref_hero.save(COMP_DIR / "cropped_ref_hero.png")

# Crop reference stage app (the workspace app inside the purple stage)
ref_stage = desktop_img.crop((120, 480, 1320, 1200))
ref_stage.save(COMP_DIR / "cropped_ref_stage.png")

# Crop reference pricing (header + pricing cards)
ref_pricing = pricing_ref_img.crop((0, 64, 1440, 980))
ref_pricing.save(COMP_DIR / "cropped_ref_pricing.png")

print("Cropped reference components successfully.")

def create_side_by_side(img_left, img_right, title_left, title_right, out_filename):
    # Resize both to same target width (e.g. 1000px wide each)
    target_w = 900
    
    w1, h1 = img_left.size
    new_h1 = int(h1 * (target_w / w1))
    resized_left = img_left.resize((target_w, new_h1), Image.Resampling.LANCZOS)
    
    w2, h2 = img_right.size
    new_h2 = int(h2 * (target_w / w2))
    resized_right = img_right.resize((target_w, new_h2), Image.Resampling.LANCZOS)
    
    content_h = max(new_h1, new_h2)
    header_h = 70
    canvas_w = target_w * 2 + 60
    canvas_h = content_h + header_h + 30
    
    canvas = Image.new("RGB", (canvas_w, canvas_h), color=(244, 246, 250))
    draw = ImageDraw.Draw(canvas)
    
    # Try loading a system sans font
    try:
        font_header = ImageFont.truetype("arialbd.ttf", 22)
        font_badge = ImageFont.truetype("arial.ttf", 15)
    except:
        font_header = ImageFont.load_default()
        font_badge = ImageFont.load_default()
        
    # Draw left header badge
    draw.rectangle([(20, 15), (target_w + 10, 55)], fill=(255, 255, 255), outline=(218, 222, 233), width=1)
    draw.text((35, 22), title_left, fill=(30, 41, 59), font=font_header)
    
    # Draw right header badge
    draw.rectangle([(target_w + 40, 15), (canvas_w - 20, 55)], fill=(37, 99, 235), outline=(29, 79, 186), width=1)
    draw.text((target_w + 55, 22), title_right, fill=(255, 255, 255), font=font_header)
    
    # Paste images
    canvas.paste(resized_left, (20, header_h))
    canvas.paste(resized_right, (target_w + 40, header_h))
    
    # Save local and artifact
    out_path = COMP_DIR / out_filename
    art_path = ARTIFACT_DIR / out_filename
    canvas.save(out_path, quality=92)
    canvas.save(art_path, quality=92)
    print(f"Saved side-by-side: {out_filename}")

create_side_by_side(
    ref_hero,
    mockup_hero_img,
    "REFERENCE (TaskFlow Marketing Hero)",
    "PROPOSED MIRRORCV (Landing Hero & Interactive Stage)",
    "comparison_1_hero.png"
)

create_side_by_side(
    ref_stage,
    mockup_editor_img,
    "REFERENCE (TaskFlow Workspace App Stage)",
    "PROPOSED MIRRORCV (FlowCV-Class Editor UI & Parity Preview)",
    "comparison_2_editor.png"
)

create_side_by_side(
    ref_pricing,
    mockup_pricing_img,
    "REFERENCE (TaskFlow Pricing 3-Tier Grid)",
    "PROPOSED MIRRORCV (MirrorCV True Entitlements Pricing Grid)",
    "comparison_3_pricing.png"
)

print("All side-by-side comparison images successfully created.")
