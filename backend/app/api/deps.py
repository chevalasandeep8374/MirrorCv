from typing import Optional, Union
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.services.supabase_auth import verify_supabase_jwt

security = HTTPBearer(auto_error=False)


class CurrentUser:
    """Represents an authenticated Supabase user."""

    def __init__(self, id: str, email: str, full_name: Optional[str] = None):
        self.id = str(id)
        self.email = str(email)
        self.full_name = full_name

    def __repr__(self) -> str:
        return f"<CurrentUser id={self.id} email={self.email}>"


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> CurrentUser:
    """Authenticates the caller strictly via a valid Supabase Auth JWT bearer token.

    Missing credentials return 401 Unauthorized.
    Invalid or expired tokens return 401 Unauthorized.
    No mock fallbacks.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    # Primary: Verify cryptographically against Supabase GoTrue Auth
    supabase_user = await verify_supabase_jwt(token)
    if supabase_user:
        return CurrentUser(
            id=supabase_user["id"],
            email=supabase_user["email"],
            full_name=supabase_user.get("full_name"),
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )
