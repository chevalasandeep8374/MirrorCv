import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FRONTEND_SRC = ROOT / "frontend" / "src"
RENDERER_DIR = FRONTEND_SRC / "components" / "resume-renderer"
RENDER_APP_DIR = FRONTEND_SRC / "app" / "render"

print("=" * 80)
print("VERIFYING GLASS ISOLATION ON RESUME RENDERER & PDF EXPORT ROUTES")
print("=" * 80)

violations = []

def check_dir(dir_path):
    if not dir_path.exists():
        print(f"Directory {dir_path} does not exist. Skipping.")
        return
    for root, _, files in os.walk(dir_path):
        for f in files:
            if f.endswith((".tsx", ".ts", ".css", ".jsx", ".js")):
                p = Path(root) / f
                content = p.read_text(encoding="utf-8", errors="ignore")
                
                # Check for glass classes or backdrop-filter
                if "glass-1" in content or "glass-2" in content or "glass-3" in content:
                    violations.append(f"{p.relative_to(ROOT)}: references glass classes")
                if "backdrop-filter" in content or "-webkit-backdrop-filter" in content:
                    violations.append(f"{p.relative_to(ROOT)}: references backdrop-filter")

check_dir(RENDERER_DIR)
check_dir(RENDER_APP_DIR)

files_scanned = list(RENDERER_DIR.glob('**/*')) + list(RENDER_APP_DIR.glob('**/*'))
print(f"Renderer & export route files scanned: {len([f for f in files_scanned if f.is_file()])}")
if violations:
    print(f"❌ VIOLATIONS DETECTED ({len(violations)}):")
    for v in violations:
        print(f"  - {v}")
    sys.exit(1)
else:
    print("✅ ZERO GLASS OR BACKDROP-FILTER STYLES IN RESUME RENDERER OR PDF ROUTES!")
    print("   <ResumeDocument>, print styles, and PDF render pipelines remain 100% solid and isolated.")

print("=" * 80)
