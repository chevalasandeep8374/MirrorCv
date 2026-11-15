import os
import io
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.api.deps import CurrentUser, get_current_user

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")

USER_A = CurrentUser(id="11111111-1111-1111-1111-111111111111", email="user_a@example.com")
USER_B = CurrentUser(id="22222222-2222-2222-2222-222222222222", email="user_b@example.com")


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
async def test_upload_docx_and_ownership_isolation(override_user_a):
    docx_path = os.path.join(FIXTURES_DIR, "sample_single_column.docx")
    assert os.path.exists(docx_path)

    with open(docx_path, "rb") as f:
        file_bytes = f.read()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. User A uploads DOCX
        resp = await ac.post(
            "/api/templates/upload",
            files={"file": ("sample_single_column.docx", file_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
        )
        assert resp.status_code == 201, resp.text
        data = resp.json()
        template_id = data["id"]
        assert "resume_id" in data
        assert data["fidelity_score"] >= 90.0
        assert data["page_count_match"] is True

        # 2. User A can view analysis
        resp_a = await ac.get(f"/api/templates/{template_id}/analysis")
        assert resp_a.status_code == 200

        # 3. User A can update slot
        resp_patch = await ac.patch(
            f"/api/templates/{template_id}/slots/slot_0",
            json={"role": "name", "binds": "header.name"},
        )
        assert resp_patch.status_code == 200

    # 4. Switch to User B -> Must be blocked by ownership check (403 Forbidden or 404)
    app.dependency_overrides[get_current_user] = lambda: USER_B
    async with AsyncClient(transport=transport, base_url="http://test") as ac_b:
        resp_b = await ac_b.get(f"/api/templates/{template_id}/analysis")
        assert resp_b.status_code in (403, 404), f"Expected 403 or 404 for User B, got {resp_b.status_code}"


@pytest.mark.asyncio
async def test_upload_invalid_file_rejected(override_user_a):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Rejects fake docx (not zip, no PK magic bytes)
        fake_bytes = b"This is not a zip docx file"
        resp = await ac.post(
            "/api/templates/upload",
            files={"file": ("fake.docx", fake_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
        )
        assert resp.status_code in (400, 422)
