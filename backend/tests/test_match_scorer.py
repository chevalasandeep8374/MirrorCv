"""Unit tests for Match Scoring Engine: determinism, weights, stuffing penalty, and missing skill classes."""

import pytest
from app.schemas.tailoring import JDAnalysis
from app.services.resume_inventory import build_resume_inventory
from app.services.match_scorer import compute_match_score


@pytest.fixture
def sample_resume_content():
    return {
        "header": {"name": "Alex Mercer", "title": "Senior Backend Engineer"},
        "sections": [
            {
                "id": "sec_skills",
                "type": "skills",
                "items": [
                    {"id": "item_s1", "title": "Python"},
                    {"id": "item_s2", "title": "FastAPI"},
                    {"id": "item_s3", "title": "PostgreSQL"},
                    {"id": "item_s4", "title": "AWS"},
                ],
            },
            {
                "id": "sec_exp",
                "type": "experience",
                "items": [
                    {
                        "id": "item_exp_1",
                        "title": "Senior Engineer",
                        "subtitle": "Tech Corp",
                        "bullets": [
                            {
                                "id": "b1",
                                "text": "Architected high-throughput document processing pipelines with FastAPI and PostgreSQL.",
                            },
                            {
                                "id": "b2",
                                "text": "Scaled cloud infrastructure on AWS managing ECS clusters with 99.99% uptime.",
                            },
                        ],
                    }
                ],
            },
        ],
    }


@pytest.fixture
def sample_jd():
    return JDAnalysis(
        job_title="Senior Software Engineer",
        seniority="Senior",
        seniority_level=3,
        required_skills=["Python", "FastAPI", "PostgreSQL", "Kubernetes"],
        preferred_skills=["AWS", "GCP", "GraphQL"],
        tools_and_tech=["Python", "FastAPI", "PostgreSQL", "AWS", "Kubernetes", "GCP"],
        responsibilities=[
            "Architect and scale distributed document processing microservices.",
            "Deploy and monitor cloud infrastructure.",
        ],
        keywords=["fastapi", "postgresql", "aws", "kubernetes", "python"],
        domain="Backend Systems",
    )


def test_scoring_determinism(sample_resume_content, sample_jd):
    inv1 = build_resume_inventory(sample_resume_content)
    res1 = compute_match_score(inv1, sample_jd)

    inv2 = build_resume_inventory(sample_resume_content)
    res2 = compute_match_score(inv2, sample_jd)

    assert res1.estimated_match_score == res2.estimated_match_score
    assert res1.score_breakdown.required_skill_coverage == res2.score_breakdown.required_skill_coverage
    assert res1.score_breakdown.semantic_relevance == res2.score_breakdown.semantic_relevance


def test_missing_skill_three_classes(sample_resume_content, sample_jd):
    """Verifies that missing skills are classified into:

    1. missing (not found anywhere)
    2. present_not_visible (in master profile but not on resume)
    3. adjacent (related skill present, e.g. AWS present for GCP requirement)
    """
    inv = build_resume_inventory(sample_resume_content)

    # Master profile has Kubernetes
    master_items = [
        {"id": "mpi_k8s_01", "type": "skill", "text": "Kubernetes cluster administration"}
    ]

    res = compute_match_score(inv, sample_jd, master_items=master_items)

    # 1. Kubernetes is in master profile -> present_not_visible
    present_not_visible_names = [p.canonical_name for p in res.skills_analysis.present_not_visible]
    assert "Kubernetes" in present_not_visible_names

    # 2. GraphQL is in preferred JD skills and neither on resume nor in master -> missing
    missing_names = [m.canonical_name for m in res.skills_analysis.missing_skills]
    assert "GraphQL" in missing_names

    # 3. GCP is requested in JD preferred skills, user has AWS -> adjacent
    adjacent_pairs = [(a.jd_skill, a.resume_skill) for a in res.skills_analysis.adjacent_skills]
    assert ("GCP", "AWS") in adjacent_pairs


def test_stuffing_penalty_and_repetition_cap(sample_resume_content, sample_jd):
    """Tests resume-wide keyword repetition cap (Instruction #12)."""
    inv = build_resume_inventory(sample_resume_content)

    # Inject repeated keyword 'fastapi' 10 times in bullets
    for i in range(10):
        inv.bullet_map[f"extra_b_{i}"] = "FastAPI microservice implementation for FastAPI endpoints."

    res = compute_match_score(inv, sample_jd)
    # Excess repetitions should trigger stuffing penalty
    assert res.score_breakdown.stuffing_penalty > 0.0
    assert res.estimated_match_score < 100.0
