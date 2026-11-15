"""Integration tests for Phase C Slice 1: Analyze mode, job descriptions intake,

scoring endpoints, and master profile management.
"""

import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.api.deps import CurrentUser, get_current_user

USER_A = CurrentUser(id="fb6cdc4c-a608-4be0-8224-2954b0fce396", email="alpha_tester_1234@gmail.com")
USER_B = CurrentUser(id="874a7eb3-df46-4cb4-890d-2b47dcfdcfbf", email="beta_tester_manual@example.com")


@pytest.fixture
def override_user_a():
    app.dependency_overrides[get_current_user] = lambda: USER_A
    yield
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture
def override_user_b():
    app.dependency_overrides[get_current_user] = lambda: USER_B
    yield
    app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_job_description_intake_and_caching(override_user_a):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Submit fresh JD
        jd_payload = {
            "title": "Senior Backend Engineer",
            "company": "Tech Corp",
            "raw_text": "We are seeking a Senior Backend Engineer proficient in Python, FastAPI, and PostgreSQL to scale microservices.",
        }
        res = await client.post("/api/job-descriptions", json=jd_payload)
        assert res.status_code == 201, res.text
        data = res.json()
        assert data["id"] is not None
        assert data["text_hash"] is not None
        assert "FastAPI" in data["analysis"]["required_skills"] or "Python" in data["analysis"]["required_skills"]

        # Fetch previously submitted JD
        get_res = await client.get(f"/api/job-descriptions/{data['id']}")
        assert get_res.status_code == 200
        assert get_res.json()["id"] == data["id"]


@pytest.mark.asyncio
async def test_pipeline_run_analyze_mode(override_user_a):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        valid_resume_uuid = "c421c70a-b3b6-4f54-bdd6-9993e69be239"
        run_payload = {
            "resume_id": valid_resume_uuid,
            "job_description_text": "We are looking for a Senior Python and FastAPI Engineer with PostgreSQL and Kubernetes experience.",
            "mode": "analyze",
        }
        res = await client.post("/api/pipeline/runs", json=run_payload)
        assert res.status_code == 201, res.text
        run_data = res.json()
        assert run_data["id"] is not None
        assert run_data["status"] == "queued"


@pytest.mark.asyncio
async def test_master_profile_crud(override_user_a):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Add item
        item_payload = {
            "type": "skill",
            "text": "Kubernetes cluster administration",
            "confirmed": True,
            "metadata": {"source": "test"},
        }
        res_add = await client.post("/api/master-profile/items", json=item_payload)
        assert res_add.status_code == 201, res_add.text
        item = res_add.json()
        assert item["text"] == item_payload["text"]
        item_id = item["id"]

        # 2. List items
        res_list = await client.get("/api/master-profile/items")
        assert res_list.status_code == 200
        items = res_list.json()
        assert any(i["id"] == item_id for i in items)

        # 3. Delete item
        res_del = await client.delete(f"/api/master-profile/items/{item_id}")
        assert res_del.status_code == 204

