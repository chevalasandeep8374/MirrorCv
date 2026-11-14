from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.services.auth import decode_access_token

security = HTTPBearer(auto_error=False)

DEV_DEFAULT_USER_EMAIL = "alex@example.com"


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
) -> User:
    """Authenticates user via JWT bearer token, or falls back to dev user in dev mode."""
    if credentials:
        token = credentials.credentials
        payload = decode_access_token(token)
        if not payload or "sub" not in payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user_id = payload["sub"]
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalars().first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        return user

    # Dev fallback allows instant onboarding and testing
    return await get_or_create_dev_user(db)
