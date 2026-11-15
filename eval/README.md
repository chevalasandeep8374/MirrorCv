# MirrorCV Evaluation Harness (`/eval`)

This module provides empirical benchmarks and evaluation datasets for Agent 2 (Analyst & Tailor).

## 1. Datasets & Licenses
- **Kaggle Resume Dataset**: Staged in `eval/data/` (gitignored). License: CC0: Public Domain / Open Database License (ODbL). All personal identifiers (names, emails, phone numbers, addresses) are scrubbed and anonymized using synthetic placeholders prior to metric evaluation in `eval/loaders.py`.
- **Kaggle Job Descriptions Dataset**: Staged in `eval/data/` (gitignored). License: CC BY-SA 4.0.
- **Curated Gold Set (30 Pairs)**: `eval/fixtures/gold_30_pairs.json`. Curated resume-JD pairs across technical roles (Backend, Frontend, Fullstack, DevOps/Cloud, Data/ML, and Cross-Domain Out-of-Family controls) with hand-labeled ground-truth skill annotations.

## 2. Core Benchmark Metrics
1. **Score Separation**: Compares same-family pairs (e.g. Backend Resume vs Backend JD) against cross-family pairs (e.g. Backend Resume vs Nursing/Marketing JD). Reports mean score gap and AUC (Area Under ROC Curve).
2. **Determinism**: Proves that given identical inputs, the scoring engine produces 100% deterministic output.
3. **Missing Skills Detection**: Evaluates Precision and Recall against hand-labeled missing skill annotations.
4. **Fabrication Rate (Slice 2)**: Counts verifier rejections per 100 proposed changes to guarantee zero fabricated metrics, entities, or unconfirmed technologies.
5. **Slot Budget Compliance (Slice 2)**: Percentage of changes where `measure_lines(after, slot) <= slot.max_lines` (Target: 100%).
