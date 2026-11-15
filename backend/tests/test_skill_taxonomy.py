"""Unit tests for Skill Taxonomy and Normalization Service."""

import pytest
from app.services.skill_taxonomy import skill_taxonomy_service, NormalizedSkill


def test_exact_canonical_match():
    res = skill_taxonomy_service.normalize_term("FastAPI")
    assert res.is_mapped is True
    assert res.canonical_name == "FastAPI"
    assert res.category in ("Frameworks", "Backend Frameworks")
    assert res.is_alias is False
    assert res.status == "approved"


def test_alias_normalization():
    # Postgres -> PostgreSQL
    res_pg = skill_taxonomy_service.normalize_term("postgres")
    assert res_pg.is_mapped is True
    assert res_pg.canonical_name == "PostgreSQL"
    assert res_pg.is_alias is True
    assert res_pg.status == "approved"

    # K8s -> Kubernetes
    res_k8s = skill_taxonomy_service.normalize_term("k8s")
    assert res_k8s.is_mapped is True
    assert res_k8s.canonical_name == "Kubernetes"
    assert res_k8s.is_alias is True

    # ts -> TypeScript
    res_ts = skill_taxonomy_service.normalize_term("ts")
    assert res_ts.is_mapped is True
    assert res_ts.canonical_name == "TypeScript"
    assert res_ts.is_alias is True


def test_fuzzy_matching():
    # py.test -> Pytest
    res = skill_taxonomy_service.normalize_term("py.test")
    assert res.is_mapped is True
    assert res.canonical_name == "Pytest"


def test_unmapped_terms_flagged_as_candidate():
    # Unknown proprietary tool
    res = skill_taxonomy_service.normalize_term("SuperCustomInternalTool123")
    assert res.is_mapped is False
    assert res.status == "candidate"
    assert res.category == "Other"


def test_rule_9_never_substitute_adjacent_skills():
    """Rule 9: normalize_term only for taxonomy-marked aliases; never substitute adjacent skills.

    GCP and AWS are adjacent cloud platforms, but GCP must NOT be normalized to AWS.
    """
    res_gcp = skill_taxonomy_service.normalize_term("GCP")
    assert res_gcp.canonical_name == "GCP"
    assert res_gcp.canonical_name != "AWS"

    res_aws = skill_taxonomy_service.normalize_term("AWS")
    assert res_aws.canonical_name == "AWS"

    # Verify adjacency reporting
    adj = skill_taxonomy_service.get_adjacent_skills("AWS")
    adj_names = [a[0] for a in adj]
    assert "GCP" in adj_names
    assert "Azure" in adj_names
