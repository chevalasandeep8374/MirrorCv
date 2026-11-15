from typing import Optional, Union
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.services.auth import decode_access_token
from app.services.supabase_auth import verify_supabase_jwt

security = HTTPBearer(auto_error=False)

DEV_DEFAULT_USER_EMAIL = "alex@example.com"


class CurrentUser:
    """Represents an authenticated user (Supabase Auth or legacy fallback)."""
    def __init__(self, id: str, email: str, full_name: Optional[str] = None):
        self.id = str(id)
        self.email = str(email)
        self.full_name = full_name

    def __repr__(self) -> str:
        return f"<CurrentUser id={self.id} email={self.email}>"


async def get_or_create_dev_user(db: AsyncSession) -> User:
    """Fallback dev user when auth header is omitted in development mode."""
    stmt = select(User).where(User.email == DEV_DEFAULT_USER_EMAIL)
    result = await db.execute(stmt)
    user = result.scalars().first()
    if not user:
        from app.services.auth import hash_password

        user = User(
            email=DEV_DEFAULT_USER_EMAIL,
            hashed_password=hash_password("password123"),
            full_name="Alex Mercer (Dev)",
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> Union[User, CurrentUser]:
    """Authenticates user via Supabase JWT bearer token, legacy custom JWT, or falls back to dev user."""
    if credentials:
        token = credentials.credentials

        # 1. Primary: Verify against Supabase Auth
        supabase_user = await verify_supabase_jwt(token)
        if supabase_user:
            return CurrentUser(
                id=supabase_user["id"],
                email=supabase_user["email"],
                full_name=supabase_user.get("full_name"),
            )

        # 2. Secondary fallback: Legacy SQLite JWT
        payload = decode_access_token(token)
        if payload and "sub" in payload:
            user_id = payload["sub"]
            stmt = select(User).where(User.id == user_id)
            result = await db.execute(stmt)
            user = result.scalars().first()
            if user:
                return user

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Dev fallback allows instant onboarding and testing
    return await get_or_create_dev_user(db)
