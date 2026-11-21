"""Cross-Resume Ownership and Security Isolation Tests (Addition 4).
Verifies:
- User A cannot access or export User B's resume via /api/resumes/{id}
- User A cannot export User B's resume to DOCX via /api/resumes/{id}/export/docx
- User A cannot export User B's resume to PDF via /api/resumes/{id}/export/pdf
- Render token issued for User A and Resume A cannot be consumed for Resume B
"""

import uuid
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.api.deps import get_current_user, CurrentUser
from app.services.render_tokens import create_render_token


@pytest.mark.asyncio
async def test_cross_user_isolation_on_resume_endpoints():
    """Verify that User B cannot access or export User A's resume."""
    user_a = CurrentUser(id="user_a_" + uuid.uuid4().hex[:6], email="usera@example.com")
    user_b = CurrentUser(id="user_b_" + uuid.uuid4().hex[:6], email="userb@example.com")

    transport = ASGITransport(app=app)

    # 1. User A creates a resume
    app.dependency_overrides[get_current_user] = lambda: user_a
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create_resp = await client.post(
            "/api/resumes",
            json={
                "title": "User A Private Confidential Resume",
                "target_job_title": "Security Architect",
            },
        )
        assert create_resp.status_code == 201, f"Failed to create resume: {create_resp.text}"
        resume_a_id = create_resp.json()["id"]

    # 2. Switch to User B and attempt cross-user access
    app.dependency_overrides[get_current_user] = lambda: user_b
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # A) Direct GET
        get_resp = await client.get(f"/api/resumes/{resume_a_id}")
        assert get_resp.status_code == 404, f"Expected 404 for cross-user get, got {get_resp.status_code}"

        # B) DOCX Export
        docx_resp = await client.get(f"/api/resumes/{resume_a_id}/export/docx")
        assert docx_resp.status_code == 404, f"Expected 404 for cross-user docx export, got {docx_resp.status_code}"

        # C) PDF Export
        pdf_resp = await client.get(f"/api/resumes/{resume_a_id}/export/pdf")
        assert pdf_resp.status_code == 404, f"Expected 404 for cross-user pdf export, got {pdf_resp.status_code}"

    # Cleanup
    app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_render_token_cross_resume_tampering_rejected():
    """Verify that a render token created for Resume A cannot be consumed for Resume B."""
    user_id = "user_" + uuid.uuid4().hex[:6]
    resume_a_id = str(uuid.uuid4())
    resume_b_id = str(uuid.uuid4())

    # Create render token bound strictly to resume_a_id
    token_for_a = create_render_token(resume_id=resume_a_id, user_id=user_id, ttl_seconds=60)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Attacker tries to use token_for_a to access resume_b_id
        tampered_resp = await client.get(
            f"/api/resumes/{resume_b_id}/render-data?render_token={token_for_a}"
        )
        assert tampered_resp.status_code == 403, (
            f"Expected 403 Forbidden for mismatched render token, got {tampered_resp.status_code}"
        )
        assert "Invalid, expired, or already consumed" in tampered_resp.json()["detail"]
