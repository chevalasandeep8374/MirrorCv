"""Supabase Auth verification service for FastAPI backend.
Verifies Supabase GoTrue JWT tokens with in-memory TTL caching for optimal performance.
"""

import time
import logging
from typing import Optional, Dict, Any, Tuple
import httpx
import jwt

from app.config import settings

logger = logging.getLogger(__name__)

# In-memory cache for verified tokens: token -> (cache_expiry_timestamp, user_dict)
_TOKEN_USER_CACHE: Dict[str, Tuple[float, Dict[str, Any]]] = {}
CACHE_TTL_SECONDS = 300.0  # 5 minutes max cache


async def verify_supabase_jwt(token: str) -> Optional[Dict[str, Any]]:
    """Verifies a Supabase Bearer JWT token against Supabase Auth service.

    Returns the user dictionary with 'id', 'email', and 'full_name' if valid,
    or None if invalid/expired.
    """
    if not token or not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        return None

    now = time.time()

    # 1. Check in-memory cache
    if token in _TOKEN_USER_CACHE:
        cache_exp, cached_user = _TOKEN_USER_CACHE[token]
        if now < cache_exp:
            return cached_user
        else:
            _TOKEN_USER_CACHE.pop(token, None)

    # 2. Fast check of unverified JWT payload for expiration
    try:
        unverified_payload = jwt.decode(token, options={"verify_signature": False})
        token_exp = unverified_payload.get("exp")
        if token_exp and now > token_exp:
            logger.debug("Token has expired based on exp claim.")
            return None
    except Exception as e:
        logger.debug(f"Failed to parse unverified JWT claims: {e}")
        return None

    # 3. Cryptographically verify with Supabase GoTrue /auth/v1/user
    url = f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1/user"
    headers = {
        "apikey": settings.SUPABASE_KEY,
        "Authorization": f"Bearer {token}",
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code != 200:
                logger.warning(f"Supabase auth verification failed ({resp.status_code}): {resp.text}")
                return None

            user_data = resp.json()
            user_id = user_data.get("id")
            email = user_data.get("email", "")
            meta = user_data.get("user_metadata") or {}
            full_name = meta.get("full_name") or meta.get("name") or email.split("@")[0]

            user_info = {
                "id": user_id,
                "email": email,
                "full_name": full_name,
                "role": user_data.get("role", "authenticated"),
                "aud": user_data.get("aud", "authenticated"),
            }

            # Cache with TTL bounded by token expiration
            remaining_ttl = CACHE_TTL_SECONDS
            if token_exp:
                remaining_ttl = min(CACHE_TTL_SECONDS, max(5.0, token_exp - now))

            _TOKEN_USER_CACHE[token] = (now + remaining_ttl, user_info)
            return user_info
    except Exception as exc:
        logger.error(f"Error connecting to Supabase Auth service: {exc}")
        return None
