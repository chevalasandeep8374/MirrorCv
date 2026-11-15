"""Computes Residual Violation Rate and False-Rejection Rate from human review labels.
Loads eval/change_review.csv with human labels (legitimate | fabricated | exaggerated),
and calculates empirical rates with 95% Wilson score confidence intervals.
"""

import os
import sys
import csv
import math
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

EVAL_DIR = Path(__file__).resolve().parent
DEFAULT_CSV = EVAL_DIR / "change_review.csv"


def wilson_score_interval(successes: int, total: int, z: float = 1.96) -> Tuple[float, float]:
    """Calculates 95% Wilson score confidence interval for a proportion."""
    if total <= 0:
        return (0.0, 1.0)
    p = successes / float(total)
    denom = 1.0 + (z**2) / total
    center = (p + (z**2) / (2.0 * total)) / denom
    margin = (z / denom) * math.sqrt((p * (1.0 - p) / total) + (z**2) / (4.0 * (total**2)))
    low = max(0.0, round(center - margin, 4))
    high = min(1.0, round(center + margin, 4))
    return (low, high)


def compute_review_metrics(csv_path: Optional[Path] = None) -> Dict[str, Any]:
    """Parses labeled change_review.csv and computes residual violation and false-rejection metrics."""
    target_path = Path(csv_path) if csv_path else DEFAULT_CSV
    if not target_path.exists():
        raise FileNotFoundError(f"Change review file not found: {target_path}")

    total_rows = 0
    unlabeled_count = 0
    labeled_count = 0

    labeled_accepted = 0
    violations_in_accepted = 0  # fabricated or exaggerated among accepted

    labeled_rejected = 0
    false_rejections = 0  # legitimate among rejected

    breakdown_by_label: Dict[str, int] = {
        "legitimate": 0,
        "fabricated": 0,
        "exaggerated": 0,
        "unlabeled": 0,
    }

    with open(target_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total_rows += 1
            status = (row.get("status") or "").strip().lower()
            label = (row.get("human_label") or "").strip().lower()

            if not label:
                unlabeled_count += 1
                breakdown_by_label["unlabeled"] += 1
                continue

            if label not in ("legitimate", "fabricated", "exaggerated"):
                raise ValueError(
                    f"Row {row.get('id')}: Invalid human_label '{label}'. "
                    f"Allowed values are: 'legitimate', 'fabricated', 'exaggerated'."
                )

            labeled_count += 1
            breakdown_by_label[label] += 1

            if status in ("accepted", "proposed"):
                labeled_accepted += 1
                if label in ("fabricated", "exaggerated"):
                    violations_in_accepted += 1
            elif status in ("rejected", "auto_rejected"):
                labeled_rejected += 1
                if label == "legitimate":
                    false_rejections += 1

    # Compute rates and 95% Wilson confidence intervals
    if labeled_accepted > 0:
        residual_violation_rate = round(violations_in_accepted / float(labeled_accepted), 4)
        residual_ci = wilson_score_interval(violations_in_accepted, labeled_accepted)
    else:
        residual_violation_rate = None
        residual_ci = (0.0, 0.0)

    if labeled_rejected > 0:
        false_rejection_rate = round(false_rejections / float(labeled_rejected), 4)
        false_rejection_ci = wilson_score_interval(false_rejections, labeled_rejected)
    else:
        false_rejection_rate = None
        false_rejection_ci = (0.0, 0.0)

    summary = {
        "csv_path": str(target_path),
        "total_changes": total_rows,
        "labeled_changes": labeled_count,
        "unlabeled_changes": unlabeled_count,
        "label_breakdown": breakdown_by_label,
        "accepted_changes_labeled": labeled_accepted,
        "violations_in_accepted": violations_in_accepted,
        "residual_violation_rate": residual_violation_rate,
        "residual_violation_rate_95ci": list(residual_ci),
        "rejected_changes_labeled": labeled_rejected,
        "false_rejections": false_rejections,
        "false_rejection_rate": false_rejection_rate,
        "false_rejection_rate_95ci": list(false_rejection_ci),
    }

    return summary


def main():
    parser = argparse.ArgumentParser(description="Compute MirrorCV change review metrics from human labels.")
    parser.add_argument("--csv", type=str, default=str(DEFAULT_CSV), help="Path to change_review.csv")
    args = parser.parse_args()

    metrics = compute_review_metrics(Path(args.csv))

    print("\n=======================================================")
    print("        MirrorCV Change Review Evaluation Report        ")
    print("=======================================================")
    print(f"File:                {metrics['csv_path']}")
    print(f"Total Changes:       {metrics['total_changes']}")
    print(f"Labeled Changes:     {metrics['labeled_changes']}")
    print(f"Unlabeled Changes:   {metrics['unlabeled_changes']}")
    print("Label Breakdown:")
    for k, v in metrics["label_breakdown"].items():
        print(f"  - {k:<12}: {v}")
    print("-------------------------------------------------------")

    if metrics["residual_violation_rate"] is not None:
        r_rate = metrics["residual_violation_rate"] * 100
        r_ci = [x * 100 for x in metrics["residual_violation_rate_95ci"]]
        print(f"Residual Violation Rate: {r_rate:.2f}% (95% CI: [{r_ci[0]:.2f}%, {r_ci[1]:.2f}%])")
        print(f"  (Fabricated/Exaggerated among Accepted: {metrics['violations_in_accepted']} / {metrics['accepted_changes_labeled']})")
    else:
        print("Residual Violation Rate: [No labeled accepted changes yet]")

    if metrics["false_rejection_rate"] is not None:
        fr_rate = metrics["false_rejection_rate"] * 100
        fr_ci = [x * 100 for x in metrics["false_rejection_rate_95ci"]]
        print(f"False-Rejection Rate:    {fr_rate:.2f}% (95% CI: [{fr_ci[0]:.2f}%, {fr_ci[1]:.2f}%])")
        print(f"  (Legitimate among Rejected: {metrics['false_rejections']} / {metrics['rejected_changes_labeled']})")
    else:
        print("False-Rejection Rate:    [No labeled rejected changes yet]")
    print("=======================================================\n")


if __name__ == "__main__":
    main()
