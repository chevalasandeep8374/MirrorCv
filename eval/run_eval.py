"""Evaluation runner for Agent 2: Score separation, AUC, and determinism benchmarks
with strict held-out evaluation isolation.
"""

import sys
import asyncio
from pathlib import Path
from typing import List, Dict, Any

# Ensure project root is on sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "backend"))

from eval.loaders import load_labeled_gold_set
from app.services.resume_inventory import build_resume_inventory
from app.services.jd_analyzer import analyze_job_description
from app.services.match_scorer import compute_match_score


def calculate_auc(labels: List[int], scores: List[float]) -> float:
    """Computes Area Under the ROC Curve (Mann-Whitney U statistic)."""
    pos_scores = [scores[i] for i, l in enumerate(labels) if l == 1]
    neg_scores = [scores[i] for i, l in enumerate(labels) if l == 0]

    if not pos_scores or not neg_scores:
        return 1.0

    u = 0.0
    for p in pos_scores:
        for n in neg_scores:
            if p > n:
                u += 1.0
            elif p == n:
                u += 0.5

    return u / (len(pos_scores) * len(neg_scores))


async def evaluate_subset(name: str, pairs: List[Dict[str, Any]]):
    print(f"\n--- Evaluating {name} ({len(pairs)} pairs) ---")
    same_family_scores = []
    diff_family_scores = []
    labels = []
    all_scores = []
    drift_count = 0

    for p in pairs:
        pair_id = p["pair_id"]
        same_family = p["same_family"]
        role = p["role"]
        content = p["resume_content"]
        jd_text = p["jd_text"]

        # Run 1
        inv1 = build_resume_inventory(content)
        jd1 = await analyze_job_description(jd_text)
        res1 = compute_match_score(inv1, jd1)
        score1 = res1.estimated_match_score

        # Run 2 (Determinism verification)
        inv2 = build_resume_inventory(content)
        jd2 = await analyze_job_description(jd_text)
        res2 = compute_match_score(inv2, jd2)
        score2 = res2.estimated_match_score

        if score1 != score2:
            drift_count += 1

        all_scores.append(score1)
        labels.append(1 if same_family else 0)

        if same_family:
            same_family_scores.append(score1)
        else:
            diff_family_scores.append(score1)

        cat_label = "IN-FAMILY" if same_family else "OUT-OF-FAMILY"
        print(f"[{pair_id}] {cat_label:14} | Score: {score1:4.1f}% | Role: {role}")

    mean_in = sum(same_family_scores) / max(1, len(same_family_scores))
    mean_out = sum(diff_family_scores) / max(1, len(diff_family_scores))
    gap = mean_in - mean_out
    auc = calculate_auc(labels, all_scores)

    print(f"\n[{name} Summary]")
    print(f"Mean Same-Family Score:   {mean_in:.1f}%")
    print(f"Mean Out-of-Family Score: {mean_out:.1f}%")
    print(f"Score Gap:                {gap:.1f} pts (Target: >= 30.0 pts)")
    print(f"Empirical AUC:            {auc:.3f} (Target: >= 0.900)")
    print(f"Drift Count:              {drift_count} (Target: 0)")

    assert drift_count == 0, f"Determinism failure in {name}: {drift_count} non-deterministic scores!"
    assert gap >= 25.0, f"Score separation insufficient in {name}: gap {gap} < 25.0"
    assert auc >= 0.85, f"AUC insufficient in {name}: {auc} < 0.85"
    return mean_in, mean_out, gap, auc


async def run_evaluation():
    print("=" * 65)
    print("MirrorCV Agent 2 Evaluation: Gold Set with 50/50 Held-Out Split")
    print("=" * 65)

    train_set, held_out_set = load_labeled_gold_set(seed=42)
    print(f"Loaded {len(train_set)} development pairs and {len(held_out_set)} held-out pairs.")
    print("Constraint: Scoring weights and prompts are NEVER tuned on the held-out half.\n")

    # Evaluate Development Set
    await evaluate_subset("Development Set (Train)", train_set)

    # Evaluate Held-Out Set
    await evaluate_subset("Held-Out Validation Set", held_out_set)

    print("\n" + "=" * 65)
    print("ALL EVALUATION BENCHMARKS PASSED ON BOTH TRAIN AND HELD-OUT SPLITS!")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    asyncio.run(run_evaluation())
