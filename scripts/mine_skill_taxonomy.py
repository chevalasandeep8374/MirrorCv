"""Taxonomy Mining & Review Queue Management Script for MirrorCV.
Mines technical skill candidates from licensed open data corpuses
(e.g., European Commission ESCO dataset under CC-BY 4.0, Stack Overflow Open Data),
verifies open licenses, deposits novel terms into the candidate review queue,
and measures taxonomy mapping coverage on the gold evaluation dataset.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Set, Tuple

# Set up backend paths
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "backend"))
sys.path.insert(0, str(REPO_ROOT / "contracts" / "python"))
sys.path.insert(0, str(REPO_ROOT))

from app.services.skill_taxonomy import skill_taxonomy_service
from eval.loaders import load_gold_set

# Approved Open Licenses for External Mining Corpuses
LICENSED_OPEN_CORPUSES = {
    "ESCO": {
        "name": "European Skills, Competences, Qualifications and Occupations",
        "license": "Creative Commons Attribution 4.0 International (CC-BY 4.0)",
        "commercial_use_permitted": True,
        "attribution_required": True,
    },
    "StackOverflow_OpenData": {
        "name": "Stack Overflow Annual Developer Survey Open Dataset",
        "license": "Open Data Commons Open Database License (ODbL / CC-BY-SA 4.0)",
        "commercial_use_permitted": True,
        "attribution_required": True,
    },
}


def verify_corpus_license(corpus_id: str) -> bool:
    """Verifies that an external corpus license is approved and allows commercial use."""
    if corpus_id not in LICENSED_OPEN_CORPUSES:
        print(f"ERROR: Corpus '{corpus_id}' is not in the approved open license registry.")
        return False
    info = LICENSED_OPEN_CORPUSES[corpus_id]
    print(f"Verified Corpus: {info['name']}")
    print(f"License:         {info['license']}")
    print(f"Commercial Use:  {'PERMITTED' if info['commercial_use_permitted'] else 'PROHIBITED'}")
    return info["commercial_use_permitted"]


def mine_candidate_skills(
    corpus_id: str,
    raw_skills_batch: List[Dict[str, Any]],
) -> Tuple[int, int]:
    """Mines candidate skills from a licensed corpus into the review queue."""
    if not verify_corpus_license(corpus_id):
        raise ValueError(f"Corpus {corpus_id} license check failed.")

    added_candidates = 0
    already_approved = 0

    for item in raw_skills_batch:
        raw_name = item.get("name") or item.get("term", "")
        if not raw_name:
            continue

        norm = skill_taxonomy_service.normalize_term(raw_name)
        if norm.is_mapped and norm.status == "approved":
            already_approved += 1
        else:
            skill_taxonomy_service.add_candidate_skill(
                canonical_name=raw_name,
                aliases=item.get("aliases", [raw_name.lower()]),
                category=item.get("category", "Other"),
                role_families=item.get("role_families", ["general"]),
                source=corpus_id,
            )
            added_candidates += 1

    return added_candidates, already_approved


def evaluate_taxonomy_coverage() -> Dict[str, Any]:
    """Evaluates mapping coverage % of JD skills across the gold evaluation set."""
    gold_pairs = load_gold_set()
    total_skills = 0
    mapped_skills = 0

    for pair in gold_pairs:
        skills = pair.get("required_skills") or pair.get("expected_matched_skills", [])
        for s in skills:
            total_skills += 1
            norm = skill_taxonomy_service.normalize_term(s)
            if norm.is_mapped and norm.status == "approved":
                mapped_skills += 1

    coverage_pct = (mapped_skills / total_skills * 100.0) if total_skills > 0 else 100.0

    return {
        "approved_taxonomy_rows": skill_taxonomy_service.get_approved_count(),
        "total_gold_skills_checked": total_skills,
        "mapped_gold_skills": mapped_skills,
        "mapping_coverage_pct": round(coverage_pct, 1),
    }


def main():
    print("=== MirrorCV Skill Taxonomy Mining & Audit ===")
    approved_count = skill_taxonomy_service.get_approved_count()
    print(f"Current Approved Taxonomy Count: {approved_count} rows\n")

    # Sample batch from licensed ESCO corpus
    sample_corpus_batch = [
        {"name": "Solidity", "category": "Languages", "role_families": ["blockchain", "backend"], "aliases": ["solidity"]},
        {"name": "Hardhat", "category": "Developer Tools", "role_families": ["blockchain"], "aliases": ["hardhat"]},
        {"name": "Python", "category": "Languages", "role_families": ["backend"]},  # Already approved
        {"name": "React", "category": "Frontend Frameworks", "role_families": ["frontend"]},  # Already approved
    ]

    added, approved = mine_candidate_skills("ESCO", sample_corpus_batch)
    print(f"\nMined Batch Results:")
    print(f"- Added to Candidate Review Queue: {added}")
    print(f"- Already Approved in Taxonomy:   {approved}")

    # Check review queue
    review_queue = skill_taxonomy_service.get_review_queue()
    print(f"- Total In Review Queue:          {len(review_queue)}")

    # Demonstrate promotion of candidate to approved
    if review_queue:
        to_promote = review_queue[0]["canonical_name"]
        promoted = skill_taxonomy_service.approve_candidate_skill(to_promote)
        print(f"Promoted Candidate '{to_promote}' to Approved: {promoted}")
        print(f"Updated Approved Taxonomy Count: {skill_taxonomy_service.get_approved_count()}")

    # Measure gold set coverage
    print("\n--- Measuring Gold Evaluation Set Coverage ---")
    cov = evaluate_taxonomy_coverage()
    print(f"Approved Taxonomy Rows:    {cov['approved_taxonomy_rows']}")
    print(f"Gold Skills Checked:       {cov['total_gold_skills_checked']}")
    print(f"Gold Skills Mapped:        {cov['mapped_gold_skills']}")
    print(f"Mapping Coverage Rate:     {cov['mapping_coverage_pct']}%")


if __name__ == "__main__":
    main()
