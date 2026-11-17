"""Tests verifying schema equality between contracts and backend schemas, ensuring single source of truth."""

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONTRACTS_SCHEMAS = BASE_DIR / "contracts" / "schemas"
BACKEND_SCHEMAS = BASE_DIR / "backend" / "app" / "schemas"


def load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_resume_content_schema_equality():
    contract_schema = load_json(CONTRACTS_SCHEMAS / "resume_content.schema.json")
    backend_schema = load_json(BACKEND_SCHEMAS / "content_schema.json")
    assert contract_schema == backend_schema, (
        "backend/app/schemas/content_schema.json does not match contracts/schemas/resume_content.schema.json! "
        "Keep contracts/schemas as the single source of truth."
    )


def test_style_tokens_schema_equality():
    contract_schema = load_json(CONTRACTS_SCHEMAS / "style_tokens.schema.json")
    backend_schema = load_json(BACKEND_SCHEMAS / "style_schema.json")
    assert contract_schema == backend_schema, (
        "backend/app/schemas/style_schema.json does not match contracts/schemas/style_tokens.schema.json! "
        "Keep contracts/schemas as the single source of truth."
    )
