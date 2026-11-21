"""Real Authentication and Security Hardening Tests (Addition 1 & 5).
Validates:
- Missing credentials return 401 Unauthorized (no mock/dev fallbacks).
- Invalid or expired JWT tokens return 401 Unauthorized.
- /health endpoint reports service_key_configured (bool) without leaking key.
- Production environment validation fails if SUPABASE_SERVICE_ROLE_KEY or secure JWT_SECRET is missing.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import HTTPException

from app.main import app
from app.config import Settings, DEV_JWT_DEFAULT
from app.api.deps import get_current_user


@pytest.mark.asyncio
async def test_missing_credentials_returns_401():
    """Verify that omitting the Authorization header returns HTTP 401 without alex@example.com fallback."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Testing on a protected route
        resp = await client.get("/api/resumes")
        assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
        assert resp.json().get("detail") == "Not authenticated"


@pytest.mark.asyncio
async def test_invalid_token_returns_401():
    """Verify that invalid or forged bearer tokens return HTTP 401."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = {"Authorization": "Bearer invalid_fake_jwt_token_12345"}
        resp = await client.get("/api/resumes", headers=headers)
        assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"


@pytest.mark.asyncio
async def test_health_reports_service_key_configured():
    """Verify that /health reports service_key_configured as a boolean and does not reveal the secret."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert "service_key_configured" in data
        assert isinstance(data["service_key_configured"], bool)
        assert "status" in data
        assert data["status"] == "ok"
        # Ensure no key leak
        for val in data.values():
            assert not str(val).startswith("eyJ")


def test_production_fails_without_service_role_key():
    """Verify that startup check fails if running in production without SUPABASE_SERVICE_ROLE_KEY."""
    cfg = Settings(
        ENVIRONMENT="production",
        SUPABASE_SERVICE_ROLE_KEY="",
        JWT_SECRET="custom_production_secret_998877",
    )
    with pytest.raises(RuntimeError, match="SUPABASE_SERVICE_ROLE_KEY is required in production"):
        cfg.validate_production_settings()


def test_production_fails_with_default_jwt_secret():
    """Verify that startup check fails if running in production with dev default JWT_SECRET."""
    cfg = Settings(
        ENVIRONMENT="production",
        SUPABASE_SERVICE_ROLE_KEY="valid_test_service_key_xyz",
        JWT_SECRET=DEV_JWT_DEFAULT,
    )
    with pytest.raises(RuntimeError, match="Secure JWT_SECRET must be set in production"):
        cfg.validate_production_settings()


def test_production_passes_with_proper_secrets():
    """Verify that startup check passes in production when all secrets are configured."""
    cfg = Settings(
        ENVIRONMENT="production",
        SUPABASE_SERVICE_ROLE_KEY="valid_test_service_key_xyz",
        JWT_SECRET="very_secure_unique_production_secret_1234567890",
    )
    # Should not raise any error
    cfg.validate_production_settings()
