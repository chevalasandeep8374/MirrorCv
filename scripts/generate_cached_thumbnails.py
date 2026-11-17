"""Generate pre-rendered, optimized template thumbnails for fast gallery loading."""

from pathlib import Path
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent.parent
POST_DIR = BASE_DIR / "tests" / "post_migration" / "presets"
THUMBNAIL_DIR = BASE_DIR / "frontend" / "public" / "templates" / "thumbnails"
THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)

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


def generate_all():
    print("Generating pre-rendered thumbnails...")
    for preset_id in PRESETS:
        src = POST_DIR / f"{preset_id}.png"
        dst = THUMBNAIL_DIR / f"{preset_id}.png"
        dst_webp = THUMBNAIL_DIR / f"{preset_id}.webp"

        if not src.exists():
            print(f"Skipping {src} (not found)")
            continue

        with Image.open(src) as img:
            # Target gallery thumbnail size: width 350, maintaining A4 aspect ratio (1:1.414) -> 350x495
            img_rgb = img.convert("RGB")
            thumb = img_rgb.resize((350, 495), Image.Resampling.LANCZOS)
            thumb.save(dst, format="PNG", optimize=True)
            thumb.save(dst_webp, format="WEBP", quality=85)
            print(f"Generated: {dst} ({dst.stat().st_size} bytes), {dst_webp} ({dst_webp.stat().st_size} bytes)")


if __name__ == "__main__":
    generate_all()
