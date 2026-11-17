"""Tests for Python normalizer against the shared golden fixture."""

import json
from pathlib import Path
from contracts.normalizer import normalize_resume_tokens

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"


def test_python_normalizer_matches_golden_fixture():
    with open(FIXTURES_DIR / "legacy_1_0_0_resume.json", "r", encoding="utf-8") as f:
        legacy = json.load(f)
    with open(FIXTURES_DIR / "golden_normalized_1_1_0_resume.json", "r", encoding="utf-8") as f:
        golden = json.load(f)

    norm_c, norm_s = normalize_resume_tokens(legacy["content"], legacy["style"])

    assert norm_c == golden["content"], "Normalized content does not match golden fixture!"
    assert norm_s == golden["style"], "Normalized style does not match golden fixture!"
