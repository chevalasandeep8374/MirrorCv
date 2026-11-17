#!/usr/bin/env python3
"""Contract Code Generation and CI Freshness Check Script.

Usage:
    py scripts/codegen.py          # Regenerates Python models and TS interfaces from schemas
    py scripts/codegen.py --check  # Verifies files on disk match generated output (CI freshness check)
"""

import sys
import shutil
import tempfile
import filecmp
from pathlib import Path
import subprocess

BASE_DIR = Path(__file__).resolve().parent.parent
SCHEMAS_DIR = BASE_DIR / "contracts" / "schemas"
PYTHON_MODELS_DIR = BASE_DIR / "contracts" / "models"
CONTRACT_TYPES_DIR = BASE_DIR / "contracts" / "types"
FRONTEND_TYPES_DIR = BASE_DIR / "frontend" / "src" / "types"
BACKEND_SCHEMAS_DIR = BASE_DIR / "backend" / "app" / "schemas"


def run_datamodel_codegen(schema_path: Path, output_path: Path):
    cmd = [
        sys.executable,
        "-m",
        "datamodel_code_generator",
        "--input",
        str(schema_path),
        "--output",
        str(output_path),
        "--output-model-type",
        "pydantic_v2.BaseModel",
        "--disable-timestamp",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error generating {output_path}:\n{res.stderr}")
        sys.exit(res.returncode)


def sync_files(src: Path, dst: Path, check_only: bool = False) -> bool:
    """Sync src to dst, or if check_only, return True if they are identical."""
    if not dst.exists():
        if check_only:
            print(f"[CI CHECK FAILED] Missing file: {dst}")
            return False
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return True

    # Compare ignoring line endings (CRLF vs LF)
    src_text = src.read_text(encoding="utf-8").replace("\r\n", "\n")
    dst_text = dst.read_text(encoding="utf-8").replace("\r\n", "\n")

    if src_text != dst_text:
        if check_only:
            print(f"[CI CHECK FAILED] Freshness mismatch in: {dst}")
            return False
        dst.write_text(src_text, encoding="utf-8")
        print(f"Updated: {dst}")
        return True
    return True


def main():
    check_mode = "--check" in sys.argv
    all_fresh = True

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # 1. Generate Python models
        gen_resume_py = tmp_path / "resume_content.py"
        gen_style_py = tmp_path / "style_tokens.py"

        run_datamodel_codegen(SCHEMAS_DIR / "resume_content.schema.json", gen_resume_py)
        run_datamodel_codegen(SCHEMAS_DIR / "style_tokens.schema.json", gen_style_py)

        # 2. Check/sync Python models
        if not sync_files(gen_resume_py, PYTHON_MODELS_DIR / "resume_content.py", check_only=check_mode):
            all_fresh = False
        if not sync_files(gen_style_py, PYTHON_MODELS_DIR / "style_tokens.py", check_only=check_mode):
            all_fresh = False

        # 3. Check/sync backend copies of schemas
        if not sync_files(SCHEMAS_DIR / "resume_content.schema.json", BACKEND_SCHEMAS_DIR / "content_schema.json", check_only=check_mode):
            all_fresh = False
        if not sync_files(SCHEMAS_DIR / "style_tokens.schema.json", BACKEND_SCHEMAS_DIR / "style_schema.json", check_only=check_mode):
            all_fresh = False

        # 4. Check/sync TypeScript interfaces between contracts and frontend
        if not sync_files(CONTRACT_TYPES_DIR / "resume_content.ts", FRONTEND_TYPES_DIR / "content.ts", check_only=check_mode):
            all_fresh = False
        if not sync_files(CONTRACT_TYPES_DIR / "style_tokens.ts", FRONTEND_TYPES_DIR / "style.ts", check_only=check_mode):
            all_fresh = False

    if check_mode:
        if all_fresh:
            print("[CI CHECK PASSED] All generated models and schemas are completely up-to-date and fresh.")
            sys.exit(0)
        else:
            print("[CI CHECK FAILED] Generated contracts are stale. Run `py scripts/codegen.py` to regenerate.")
            sys.exit(1)
    else:
        print("[SUCCESS] All contract models, types, and schema mirrors regenerated successfully.")


if __name__ == "__main__":
    main()
