"""Automated test suite for Step 4: Supabase JWT Verification & Short-Lived Single-Use Render Tokens.
Tests:
1. Supabase GoTrue JWT verification with TTL in-memory caching.
2. Cryptographic single-use, resume-scoped render token lifecycle (creation, validation, replay rejection, expiry).
3. FastAPI /api/resumes/{resume_id}/render-data endpoint behavior.
"""

import time
import asyncio
import pytest
import httpx
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.config import settings
from app.services.supabase_auth import verify_supabase_jwt, _TOKEN_USER_CACHE
from app.services.render_tokens import create_render_token, validate_and_consume_render_token

SUPABASE_URL = "https://uwomilakkajzzbbnijeh.supabase.co"
ANON_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV3b21pbGFra2FqenpiYm5pamVoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTQ3MjMwOTMsImV4cCI6MjExMDI5OTA5M30."
    "Kxi0-Wt8Yt-hXDRA1doyUKxwwk15Wncp41Zqc9L-UA0"
)
TEST_USER_EMAIL = "alpha_tester_1234@gmail.com"
TEST_USER_PASSWORD = "Password123!"


@pytest.mark.asyncio
async def test_supabase_jwt_verification_and_cache():
    """Proves that valid Supabase JWTs are verified and cached in memory."""
    # Obtain real Supabase JWT
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
            headers={"apikey": ANON_KEY, "Content-Type": "application/json"},
            json={"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
        )
        assert resp.status_code == 200, f"Supabase login failed: {resp.text}"
        data = resp.json()
        token = data["access_token"]
        expected_user_id = data["user"]["id"]

    # 1. Primary verification against Supabase
    _TOKEN_USER_CACHE.pop(token, None)
    user_info = await verify_supabase_jwt(token)
    assert user_info is not None, "Valid Supabase token must verify successfully"
    assert user_info["id"] == expected_user_id
    assert user_info["email"] == TEST_USER_EMAIL

    # 2. Fast cache hit (without network)
    assert token in _TOKEN_USER_CACHE
    cached_hit = await verify_supabase_jwt(token)
    assert cached_hit == user_info

    # 3. Invalid token returns None
    invalid_result = await verify_supabase_jwt("invalid.bogus.jwt")
    assert invalid_result is None


def test_render_token_single_use_and_scoping():
    """Proves that render tokens are single-use, resume-scoped, and expire properly."""
    resume_id = "test-resume-1234"
    user_id = "test-user-5678"

    # 1. Create token with short TTL (2 seconds for testing)
    token = create_render_token(resume_id, user_id, ttl_seconds=2)
    assert isinstance(token, str) and len(token) > 20

    # 2. Rejection on wrong resume_id (scoping)
    mismatched = validate_and_consume_render_token(token, "wrong-resume-9999")
    assert mismatched is None, "Token must be rejected for mismatched resume_id"

    # 3. Success on correct resume_id
    valid_meta = validate_and_consume_render_token(token, resume_id)
    assert valid_meta is not None, "Token must be accepted on first use"
    assert valid_meta["resume_id"] == resume_id
    assert valid_meta["user_id"] == user_id

    # 4. Immediate replay / reuse rejection (single-use)
    replay = validate_and_consume_render_token(token, resume_id)
    assert replay is None, "Token must be rejected on replay (single-use enforced)"

    # 5. Expiration enforcement
    exp_token = create_render_token(resume_id, user_id, ttl_seconds=1)
    time.sleep(1.2)
    expired = validate_and_consume_render_token(exp_token, resume_id)
    assert expired is None, "Token must be rejected after TTL expiration"


@pytest.mark.asyncio
async def test_render_data_api_endpoint():
    """Tests GET /api/resumes/{resume_id}/render-data with render tokens."""
    resume_id = "00000000-0000-0000-0000-000000000001"
    user_id = "fb6cdc4c-a608-4be0-8224-2954b0fce396"

    # Create token
    token = create_render_token(resume_id, user_id, ttl_seconds=60)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Request with invalid token -> 403
        bad_resp = await ac.get(f"/api/resumes/{resume_id}/render-data?render_token=invalid_token")
        assert bad_resp.status_code == 403

        # 2. Request with valid token (resume may be 404 or 200, but token validation succeeds)
        # We test that the token was consumed
        resp = await ac.get(f"/api/resumes/{resume_id}/render-data?render_token={token}")
        # Token validation passed, either found resume or 404 not found (NOT 403 forbidden)
        assert resp.status_code in (200, 404), f"Unexpected status: {resp.status_code}"

        # 3. Repeat request with same consumed token -> 403
        reused_resp = await ac.get(f"/api/resumes/{resume_id}/render-data?render_token={token}")
        assert reused_resp.status_code == 403, "Reused token must return 403 Forbidden"
