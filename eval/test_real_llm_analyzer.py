"""Evaluation test for JD analyzer measuring skill extraction Precision and Recall against ground truth labels.
Marked with @pytest.mark.slow.
"""

import sys
import pytest
import asyncio
from pathlib import Path
from typing import Set

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "backend"))

from eval.loaders import load_labeled_gold_set
from app.services.jd_analyzer import analyze_job_description
from app.services.llm_client import get_llm_provider
from app.services.skill_taxonomy import skill_taxonomy_service


@pytest.mark.slow
@pytest.mark.asyncio
async def test_real_llm_jd_analyzer_precision_recall():
    """Runs JD analyzer on held-out test set and evaluates skill extraction against human gold labels.

    Reports:
    - Extraction Precision (TP / (TP + FP))
    - Extraction Recall (TP / (TP + FN))
    - F1 Score
    """
    provider = get_llm_provider()
    train_set, held_out_set = load_labeled_gold_set(seed=42)

    total_tp = 0
    total_fp = 0
    total_fn = 0

    print(f"\n--- Real LLM JD Analyzer Evaluation (Provider: {provider}) ---")

    for pair in held_out_set:
        jd_text = pair["jd_text"]
        all_skills = pair.get("expected_matched_skills", []) + pair.get("expected_missing_skills", [])
        # Ground truth skills actually mentioned in the job description text
        ground_truth: Set[str] = {
            s for s in all_skills if s.lower() in jd_text.lower()
        }

        if not ground_truth:
            continue

        # Run analyzer
        jd_analysis = await analyze_job_description(jd_text)
        extracted: Set[str] = set()
        for s in jd_analysis.required_skills + jd_analysis.preferred_skills + jd_analysis.tools_and_tech:
            norm = skill_taxonomy_service.normalize_term(s)
            extracted.add(norm.canonical_name if norm.status == "approved" else s)

        # Normalize ground truth for fair comparison
        norm_gt: Set[str] = set()
        for g in ground_truth:
            norm = skill_taxonomy_service.normalize_term(g)
            norm_gt.add(norm.canonical_name if norm.status == "approved" else g)

        tp = len(extracted.intersection(norm_gt))
        fp = len(extracted - norm_gt)
        fn = len(norm_gt - extracted)

        total_tp += tp
        total_fp += fp
        total_fn += fn

    precision = total_tp / max(1, total_tp + total_fp)
    recall = total_tp / max(1, total_tp + total_fn)
    f1 = 2 * (precision * recall) / max(0.001, (precision + recall))

    print(f"Total True Positives (TP):  {total_tp}")
    print(f"Total False Positives (FP): {total_fp}")
    print(f"Total False Negatives (FN): {total_fn}")
    print(f"Extraction Precision:       {precision * 100:.1f}%")
    print(f"Extraction Recall:          {recall * 100:.1f}%")
    print(f"F1 Score:                   {f1:.3f}")
    print(f"------------------------------------------------------------------\n")

    assert precision >= 0.75, f"Extraction precision too low: {precision:.2f} < 0.75"
    assert recall >= 0.75, f"Extraction recall too low: {recall:.2f} < 0.75"
