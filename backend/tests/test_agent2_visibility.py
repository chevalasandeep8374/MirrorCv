"""Tests verifying that Agent 2 resume inventory and scoring strictly respect visible=false."""

import pytest
from app.services.resume_inventory import build_resume_inventory
from app.services.match_scorer import compute_match_score
from app.schemas.tailoring import JDAnalysis


@pytest.fixture
def sample_jd():
    return JDAnalysis(
        raw_jd_text="Looking for a Python and Kubernetes engineer with Docker experience.",
        job_title="Senior Infrastructure Engineer",
        company_name="Cloud Corp",
        seniority_level=3,
        required_skills=["Python", "Kubernetes"],
        preferred_skills=["Docker"],
        responsibilities=["Maintain microservices"],
    )


@pytest.fixture
def resume_with_hidden_items():
    return {
        "header": {
            "name": "Jane Doe",
            "title": "Cloud Architect",
            "email": "jane@example.com",
            "phone": "555-1234",
            "location": "Remote",
            "website": "janedoe.dev",
            "fieldVisibility": {
                "name": True,
                "title": False,  # Hidden title
            },
            "links": [],
        },
        "sections": [
            {
                "id": "sec-skills-visible",
                "type": "skills",
                "title": "Visible Skills",
                "visible": True,
                "items": [
                    {
                        "id": "item-py",
                        "title": "Python",
                        "subtitle": "",
                        "location": "",
                        "dateRange": "",
                        "visible": True,
                        "bullets": [],
                    },
                    {
                        "id": "item-k8s-hidden",
                        "title": "Kubernetes",
                        "subtitle": "",
                        "location": "",
                        "dateRange": "",
                        "visible": False,  # Hidden item
                        "bullets": [],
                    },
                ],
            },
            {
                "id": "sec-exp-hidden",
                "type": "experience",
                "title": "Old Experience",
                "visible": False,  # Entire section hidden
                "items": [
                    {
                        "id": "item-docker",
                        "title": "DevOps Lead",
                        "subtitle": "Docker Corp",
                        "location": "",
                        "dateRange": "2018 - 2020",
                        "visible": True,
                        "bullets": [
                            {
                                "id": "b-docker-1",
                                "text": "Architected Docker container infrastructure and managed Kubernetes clusters.",
                            }
                        ],
                    }
                ],
            },
        ],
    }


def test_inventory_excludes_hidden_sections_and_items(resume_with_hidden_items):
    inventory = build_resume_inventory(resume_with_hidden_items)

    # 1. Header field visibility respected
    assert "Jane Doe" in inventory.entities
    assert "Cloud Architect" not in inventory.entities

    # 2. Visible skill included
    assert "Python" in inventory.skills

    # 3. Hidden skill item excluded from inventory
    assert "Kubernetes" not in inventory.skills

    # 4. Hidden section items & bullets excluded
    assert "Docker" not in inventory.skills
    assert "item-docker" not in inventory.item_map
    assert "b-docker-1" not in inventory.bullet_map


def test_match_scoring_respects_visibility(resume_with_hidden_items, sample_jd):
    inventory = build_resume_inventory(resume_with_hidden_items)
    res = compute_match_score(inventory=inventory, jd=sample_jd)

    # Python is matched because it is visible
    matched_canonical = [m.canonical_name for m in res.skills_analysis.matched_skills]
    assert "Python" in matched_canonical

    # Kubernetes was in a hidden item, so it MUST NOT be matched
    assert "Kubernetes" not in matched_canonical

    # Docker was in a hidden section, so it MUST NOT be matched
    assert "Docker" not in matched_canonical

    # Kubernetes and Docker should be missing
    missing_canonical = [m.canonical_name for m in res.skills_analysis.missing_skills]
    assert "Kubernetes" in missing_canonical


def test_toggling_visible_changes_inventory_and_score(sample_jd):
    resume = {
        "header": {"name": "Jane", "title": "Dev"},
        "sections": [
            {
                "id": "sec-1",
                "type": "skills",
                "title": "Skills",
                "visible": True,
                "items": [
                    {"id": "1", "title": "Python", "visible": True, "bullets": []},
                    {"id": "2", "title": "Kubernetes", "visible": True, "bullets": []},
                ],
            }
        ],
    }

    # When visible: true
    inv1 = build_resume_inventory(resume)
    score1 = compute_match_score(inv1, sample_jd)

    # Toggle Kubernetes to visible: false
    resume["sections"][0]["items"][1]["visible"] = False
    inv2 = build_resume_inventory(resume)
    score2 = compute_match_score(inv2, sample_jd)

    assert "Kubernetes" in inv1.skills
    assert "Kubernetes" not in inv2.skills
    assert score1.estimated_match_score > score2.estimated_match_score
