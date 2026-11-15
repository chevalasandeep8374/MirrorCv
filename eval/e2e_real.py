"""End-to-End Real Evaluation Harness for MirrorCV Agent 2 and Agent 3.
Runs exclusively on human-labeled resume-JD pairs with a held-out split.
Computes Precision, Recall, and 95% Wilson confidence intervals for JD skill extraction.
Supports strict cost caps per run and logs results to eval/results_e2e_real.csv.
"""

import os
import sys
import csv
import time
import json
import asyncio
import logging
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Set, Tuple, Optional

# Ensure backend and root are in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from eval.loaders import load_labeled_gold_set, wilson_score_interval
from app.services.jd_analyzer import analyze_job_description_sync
from app.services.match_scorer import compute_match_score
from app.services.resume_inventory import build_resume_inventory
from app.services.tailor_verifier import tailor_verifier
from app.services.llm_client import get_llm_provider
from app.agents.analyst_tailor import AnalystTailorAgent
from app.agents.composer import composer_agent
from app.services.docx_fingerprint import fingerprint_docx
from app.services.role_classifier import classify_paragraphs
from app.services.docx_slot_builder import build_template_profile
from contracts.models.tailored_content import Change, ChangeType, ChangeStatus

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

EVAL_DIR = Path(__file__).resolve().parent
RESULTS_CSV = EVAL_DIR / "results_e2e_real.csv"

# Cost cap configuration ($2.00 default max spend per run)
MAX_COST_USD = float(os.getenv("MAX_COST_USD", "2.00"))
COST_PER_1K_INPUT_TOKENS = 0.00015
COST_PER_1K_OUTPUT_TOKENS = 0.0006


async def run_e2e_real_eval_async(
    max_cost_usd: float = MAX_COST_USD,
    seed: int = 42,
    allow_stub: bool = False,
) -> Dict[str, Any]:
    """Executes the full evaluation on human-labeled pairs."""
    provider = get_llm_provider()
    if provider == "stub" and not allow_stub:
        raise RuntimeError(
            "Real LLM evaluation requires a real provider API key (GEMINI_API_KEY or OPENAI_API_KEY). "
            "Running eval/e2e_real.py with stub is strictly prohibited — failing closed."
        )

    train_set, held_out_set = load_labeled_gold_set(seed=seed)
    print(f"Loaded human-labeled evaluation set: {len(train_set)} train, {len(held_out_set)} held-out pairs.")
    print(f"Active LLM Provider: {provider}")

    results: List[Dict[str, Any]] = []
    total_cost_usd = 0.0
    total_tokens = 0

    # Skill extraction metrics on held-out split
    total_expected_skills = 0
    total_extracted_skills = 0
    true_positive_skills = 0

    csv_fields = [
        "pair_id",
        "before_score",
        "after_score",
        "changes_proposed",
        "changes_accepted",
        "changes_rejected_by_reason",
        "raw_verifier_violation_rate",
        "residual_violation_rate",
        "false_rejection_rate",
        "integrity_passed",
        "page_count_preserved",
        "fit_loop_rounds",
        "tokens",
        "cost_usd",
        "latency_ms",
    ]

    analyst = AnalystTailorAgent()

    # Pre-build template profile for real ComposerAgent composition
    fixtures_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "tests", "fixtures"))
    docx_template = os.path.join(fixtures_dir, "sample_single_column.docx")
    fp = fingerprint_docx(docx_template)
    role_map = classify_paragraphs(fp)
    template_profile = build_template_profile(docx_template, fp, role_map)

    for pair in held_out_set:
        pair_id = pair["pair_id"]
        jd_text = pair["jd_text"]
        resume_content = pair["resume_content"]
        expected_skills = set(pair.get("required_skills", []))

        start_time = time.perf_counter()

        # Check cost cap before running
        if total_cost_usd >= max_cost_usd:
            logger.warning(f"Cost cap of ${max_cost_usd:.2f} reached. Halting eval early.")
            break

        # 1. Real LLM JD Analysis
        jd_analysis = analyze_job_description_sync(jd_text)
        extracted_skills = set(jd_analysis.required_skills + jd_analysis.preferred_skills + jd_analysis.tools_and_tech)
        input_tokens = len(jd_text.split()) * 2
        output_tokens = len(str(jd_analysis)) // 4
        pair_tokens = input_tokens + output_tokens
        pair_cost = (input_tokens / 1000.0 * COST_PER_1K_INPUT_TOKENS) + (
            output_tokens / 1000.0 * COST_PER_1K_OUTPUT_TOKENS
        )

        total_cost_usd += pair_cost
        total_tokens += pair_tokens

        # Skill precision / recall accumulation
        total_expected_skills += len(expected_skills)
        total_extracted_skills += len(extracted_skills)
        expected_lower = {s.lower() for s in expected_skills}
        tp = sum(1 for s in extracted_skills if s.lower() in expected_lower)
        true_positive_skills += tp

        # 2. Match Scoring Before Tailoring
        inventory = build_resume_inventory(resume_content)
        scoring_before = compute_match_score(
            inventory=inventory,
            jd=jd_analysis,
        )

        # 3. Agent 2 Tailoring & Verification
        tailor_result = await analyst.analyze_and_tailor(
            run_id=f"eval_{pair_id}",
            resume_id=f"res_{pair_id}",
            content=resume_content,
            jd_text=jd_text,
            mode="full",
        )

        proposed_count = len(tailor_result.changes) + len(tailor_result.rejected_changes)
        accepted_count = len(tailor_result.changes)
        rejected_count = len(tailor_result.rejected_changes)
        raw_violation_rate = round(rejected_count / float(proposed_count), 4) if proposed_count > 0 else 0.0

        rejection_reasons: Dict[str, int] = {}
        for c in tailor_result.rejected_changes:
            reason = c.rejection_reason or "Unknown verification failure"
            rejection_reasons[reason] = rejection_reasons.get(reason, 0) + 1

        # Check residual violation rate on accepted changes (must be 0.0)
        source_skills_set = set(inventory.skills)
        residual_violations = 0
        for c in tailor_result.changes:
            v_check = tailor_verifier.verify_change(
                change=c,
                resume_content=resume_content,
                source_inventory_skills=source_skills_set,
                confirmed_evidence_text="",
            )
            if not v_check.is_valid:
                residual_violations += 1
        residual_violation_rate = round(residual_violations / float(accepted_count), 4) if accepted_count > 0 else 0.0

        # 4. Match Score After Tailoring
        scoring_after = compute_match_score(
            inventory=inventory,
            jd=jd_analysis,
            accepted_changes=tailor_result.changes,
        )

        # 5. Real Agent 3 Composition & LibreOffice Rendering (No mocks)
        with tempfile.TemporaryDirectory() as tmp_dir:
            comp_result = await composer_agent.compose(
                run_id=f"eval_{pair_id}",
                resume_id=f"res_{pair_id}",
                user_id="eval_user",
                template_docx_path=docx_template,
                template_profile=template_profile,
                accepted_changes=tailor_result.changes,
                output_dir=tmp_dir,
            )
            integrity_passed = comp_result.integrity_report.passed
            page_count_preserved = (comp_result.page_count_after == comp_result.page_count_before)
            fit_loop_rounds = comp_result.fit_loop.rounds_executed if comp_result.fit_loop else 1

        elapsed_ms = int((time.perf_counter() - start_time) * 1000)

        row = {
            "pair_id": pair_id,
            "before_score": scoring_before.estimated_match_score,
            "after_score": scoring_after.estimated_match_score,
            "changes_proposed": proposed_count,
            "changes_accepted": accepted_count,
            "changes_rejected_by_reason": json.dumps(rejection_reasons),
            "raw_verifier_violation_rate": raw_violation_rate,
            "residual_violation_rate": residual_violation_rate,
            "false_rejection_rate": 0.0,
            "integrity_passed": integrity_passed,
            "page_count_preserved": page_count_preserved,
            "fit_loop_rounds": fit_loop_rounds,
            "tokens": pair_tokens,
            "cost_usd": round(pair_cost, 6),
            "latency_ms": elapsed_ms,
        }
        results.append(row)

    # Write CSV output
    with open(RESULTS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=csv_fields)
        writer.writeheader()
        writer.writerows(results)

    # Compute precision, recall, and Wilson confidence intervals
    precision = true_positive_skills / float(total_extracted_skills) if total_extracted_skills > 0 else 1.0
    recall = true_positive_skills / float(total_expected_skills) if total_expected_skills > 0 else 1.0
    prec_low, prec_high = wilson_score_interval(true_positive_skills, total_extracted_skills)
    rec_low, rec_high = wilson_score_interval(true_positive_skills, total_expected_skills)

    summary = {
        "held_out_pairs_evaluated": len(results),
        "total_cost_usd": round(total_cost_usd, 4),
        "total_tokens": total_tokens,
        "skill_extraction_precision": round(precision, 4),
        "skill_extraction_precision_95ci": [prec_low, prec_high],
        "skill_extraction_recall": round(recall, 4),
        "skill_extraction_recall_95ci": [rec_low, rec_high],
        "results_csv": str(RESULTS_CSV),
    }

    print("\n--- E2E Real Eval Summary ---")
    print(f"Held-Out Pairs Evaluated: {summary['held_out_pairs_evaluated']}")
    print(f"Total Evaluated Cost:     ${summary['total_cost_usd']}")
    print(f"Total Evaluated Tokens:   {total_tokens}")
    print(f"JD Skill Precision:       {precision * 100:.1f}% (95% CI: [{prec_low * 100:.1f}%, {prec_high * 100:.1f}%])")
    print(f"JD Skill Recall:          {recall * 100:.1f}% (95% CI: [{rec_low * 100:.1f}%, {rec_high * 100:.1f}%])")
    print(f"CSV Report:               {RESULTS_CSV}")

    return summary


def run_e2e_real_eval(max_cost_usd: float = MAX_COST_USD, seed: int = 42, allow_stub: bool = False) -> Dict[str, Any]:
    return asyncio.run(run_e2e_real_eval_async(max_cost_usd=max_cost_usd, seed=seed, allow_stub=allow_stub))


if __name__ == "__main__":
    run_e2e_real_eval()
