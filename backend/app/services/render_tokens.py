"""Service for short-lived (60s), single-use, resume-scoped render tokens.
Used for headless PDF generation without exposing long-lived user JWTs in URLs or query logs.
"""

import time
import secrets
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# In-memory store: token -> metadata dict
_RENDER_TOKENS: Dict[str, Dict[str, Any]] = {}
DEFAULT_RENDER_TOKEN_TTL = 60  # 60 seconds strict expiry


def _cleanup_expired_tokens() -> None:
    now = time.time()
    expired = [t for t, meta in _RENDER_TOKENS.items() if now > meta["expires_at"]]
    for t in expired:
        _RENDER_TOKENS.pop(t, None)


def create_render_token(resume_id: str, user_id: str, ttl_seconds: int = DEFAULT_RENDER_TOKEN_TTL) -> str:
    """Creates a short-lived, single-use token strictly scoped to a specific resume_id."""
    _cleanup_expired_tokens()
    token = secrets.token_urlsafe(32)
    now = time.time()
    _RENDER_TOKENS[token] = {
        "resume_id": str(resume_id),
        "user_id": str(user_id),
        "expires_at": now + ttl_seconds,
        "used": False,
        "created_at": now,
    }
    logger.info(f"Created single-use render token for resume {resume_id} (valid {ttl_seconds}s)")
    return token


def validate_and_consume_render_token(token: str, resume_id: str) -> Optional[Dict[str, Any]]:
    """Validates and immediately consumes a single-use render token.

    Returns the token metadata if valid, or None if expired, already used, or mismatched resume_id.
    """
    _cleanup_expired_tokens()
    meta = _RENDER_TOKENS.get(token)
    if not meta:
        logger.warning(f"Render token not found or expired for resume {resume_id}")
        return None

    now = time.time()
    if now > meta["expires_at"]:
        _RENDER_TOKENS.pop(token, None)
        logger.warning(f"Render token expired for resume {resume_id}")
        return None

    if meta["used"]:
        logger.warning(f"Render token already used for resume {resume_id}")
        return None

    if meta["resume_id"] != str(resume_id):
        logger.warning(f"Render token resume mismatch: expected {meta['resume_id']}, got {resume_id}")
        return None

    # Mark as used (single-use)
    meta["used"] = True
    _RENDER_TOKENS.pop(token, None)
    logger.info(f"Render token successfully validated and consumed for resume {resume_id}")
    return meta
