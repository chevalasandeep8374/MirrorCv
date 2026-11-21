"""Fresh Account Isolation Tests (Part 2 & Addition 7).
Verifies:
- A new account starts with zero resumes (empty dashboard state).
- No demo, seed, or hardcoded resumes appear in the user-facing resume list.
"""

import uuid
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.api.deps import get_current_user, CurrentUser


@pytest.mark.asyncio
async def test_fresh_account_has_no_seeded_resumes():
    """Verify that a brand new account receives an empty list [] from GET /api/resumes."""
    fresh_user = CurrentUser(id="fresh_user_" + uuid.uuid4().hex[:8], email="fresh@example.com")

    app.dependency_overrides[get_current_user] = lambda: fresh_user
    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/resumes")
            assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
            resumes = resp.json()
            assert isinstance(resumes, list)
            assert len(resumes) == 0, f"Expected fresh account to have 0 resumes, but found {len(resumes)}"
    finally:
        app.dependency_overrides.pop(get_current_user, None)
