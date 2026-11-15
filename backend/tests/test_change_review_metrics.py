"""Unit tests for eval/compute_review_metrics.py."""

import pytest
import csv
import tempfile
from pathlib import Path
from eval.compute_review_metrics import compute_review_metrics, wilson_score_interval


def test_wilson_score_interval_properties():
    # 0 out of 10
    low, high = wilson_score_interval(0, 10)
    assert low == 0.0
    assert high > 0.0 and high < 0.35

    # 10 out of 10
    low, high = wilson_score_interval(10, 10)
    assert low > 0.65
    assert high == 1.0

    # 5 out of 10 (symmetric around 0.5)
    low, high = wilson_score_interval(5, 10)
    assert low < 0.5 < high


def test_compute_review_metrics_calculation():
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["id", "before", "after", "status", "rejection_reason", "gates_tripped", "human_label"],
        )
        writer.writeheader()
        # 10 accepted changes: 9 legitimate, 1 exaggerated
        for i in range(9):
            writer.writerow({
                "id": f"c_acc_{i}",
                "before": "b",
                "after": "a",
                "status": "accepted",
                "rejection_reason": "",
                "gates_tripped": "",
                "human_label": "legitimate",
            })
        writer.writerow({
            "id": "c_acc_9",
            "before": "b",
            "after": "a",
            "status": "accepted",
            "rejection_reason": "",
            "gates_tripped": "",
            "human_label": "exaggerated",
        })

        # 5 rejected changes: 4 fabricated, 1 legitimate (false rejection)
        for i in range(4):
            writer.writerow({
                "id": f"c_rej_{i}",
                "before": "b",
                "after": "a",
                "status": "rejected",
                "rejection_reason": "fabrication",
                "gates_tripped": "fabrication_numbers",
                "human_label": "fabricated",
            })
        writer.writerow({
            "id": "c_rej_4",
            "before": "b",
            "after": "a",
            "status": "rejected",
            "rejection_reason": "budget",
            "gates_tripped": "budget_exceeded",
            "human_label": "legitimate",
        })

        # 2 unlabeled changes
        for i in range(2):
            writer.writerow({
                "id": f"c_un_{i}",
                "before": "b",
                "after": "a",
                "status": "proposed",
                "rejection_reason": "",
                "gates_tripped": "",
                "human_label": "",
            })
        csv_path = Path(f.name)

    try:
        metrics = compute_review_metrics(csv_path)
        assert metrics["total_changes"] == 17
        assert metrics["labeled_changes"] == 15
        assert metrics["unlabeled_changes"] == 2

        # Residual violation rate = 1 / 10 = 0.10
        assert metrics["accepted_changes_labeled"] == 10
        assert metrics["violations_in_accepted"] == 1
        assert metrics["residual_violation_rate"] == 0.1
        low, high = metrics["residual_violation_rate_95ci"]
        assert 0.0 < low < 0.1 < high < 1.0

        # False rejection rate = 1 / 5 = 0.20
        assert metrics["rejected_changes_labeled"] == 5
        assert metrics["false_rejections"] == 1
        assert metrics["false_rejection_rate"] == 0.2
        r_low, r_high = metrics["false_rejection_rate_95ci"]
        assert 0.0 < r_low < 0.2 < r_high < 1.0
    finally:
        csv_path.unlink(missing_ok=True)
