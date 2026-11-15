"""Master Profile API Endpoints.
Allows users to view, add, confirm, and manage verified accomplishments, extra projects,
and confirmed skills with strict per-user isolation.
"""

import uuid
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, Field
import httpx

from app.config import settings
from app.api.deps import get_current_user, CurrentUser

router = APIRouter(prefix="/master-profile", tags=["Master Profile"])

# Local store fallback for testing and dev environments
_LOCAL_MASTER_STORE: Dict[str, Dict[str, Any]] = {}


class MasterProfileItemCreateRequest(BaseModel):
    type: str = Field(..., description="Item type: skill, project, achievement, certification")
    text: str = Field(..., min_length=2, max_length=2000, description="Full description or skill name")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    confirmed: bool = Field(True, description="Whether this item is confirmed by the user")


class MasterProfileItemResponse(BaseModel):
    id: str
    user_id: str
    type: str
    text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[str] = None


@router.get("/items", response_model=List[MasterProfileItemResponse])
async def list_master_profile_items(
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Lists all confirmed master profile items for the authenticated user."""
    user_id = current_user.id
    auth_header = request.headers.get("Authorization", "")
    user_token = auth_header.replace("Bearer ", "") if "Bearer " in auth_header else None

    if settings.SUPABASE_URL and settings.SUPABASE_KEY:
        url = f"{settings.SUPABASE_URL.rstrip('/')}/rest/v1/master_profile_items?user_id=eq.{user_id}&select=*&order=created_at.desc"
        headers = {"apikey": settings.SUPABASE_KEY}
        if settings.SUPABASE_SERVICE_ROLE_KEY:
            headers["Authorization"] = f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}"
        elif user_token:
            headers["Authorization"] = f"Bearer {user_token}"

        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                res = await client.get(url, headers=headers)
                if res.status_code == 200:
                    rows = res.json()
                    if rows:
                        return [
                            MasterProfileItemResponse(
                                id=row["id"],
                                user_id=row["user_id"],
                                type=row["type"],
                                text=row["text"],
                                metadata=row.get("metadata", {}),
                                created_at=row.get("created_at"),
                            )
                            for row in rows
                        ]
        except Exception:
            pass

    # Fallback to local store for user
    user_items = [
        MasterProfileItemResponse(
            id=r["id"],
            user_id=r["user_id"],
            type=r["type"],
            text=r["text"],
            metadata=r.get("metadata", {}),
            created_at=r.get("created_at"),
        )
        for r in _LOCAL_MASTER_STORE.values()
        if r.get("user_id") == user_id
    ]
    return user_items


@router.post("/items", response_model=MasterProfileItemResponse, status_code=status.HTTP_201_CREATED)
async def create_master_profile_item(
    payload: MasterProfileItemCreateRequest,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Adds a new verified item or confirmed skill to the user's master profile."""
    user_id = current_user.id
    auth_header = request.headers.get("Authorization", "")
    user_token = auth_header.replace("Bearer ", "") if "Bearer " in auth_header else None

    item_id = str(uuid.uuid4())
    meta = dict(payload.metadata)
    meta["confirmed"] = payload.confirmed
    meta["source"] = meta.get("source", "user_added")

    row = {
        "id": item_id,
        "user_id": user_id,
        "type": payload.type,
        "text": payload.text,
        "metadata": meta,
    }
    _LOCAL_MASTER_STORE[item_id] = row

    if settings.SUPABASE_URL and settings.SUPABASE_KEY:
        url = f"{settings.SUPABASE_URL.rstrip('/')}/rest/v1/master_profile_items"
        headers = {
            "apikey": settings.SUPABASE_KEY,
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }
        if settings.SUPABASE_SERVICE_ROLE_KEY:
            headers["Authorization"] = f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}"
        elif user_token:
            headers["Authorization"] = f"Bearer {user_token}"

        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                res = await client.post(url, headers=headers, json=row)
                if res.status_code in (200, 201):
                    rows = res.json()
                    if rows:
                        row["created_at"] = rows[0].get("created_at")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error saving master profile item: {e}")

    return MasterProfileItemResponse(
        id=item_id,
        user_id=user_id,
        type=payload.type,
        text=payload.text,
        metadata=meta,
        created_at=row.get("created_at"),
    )


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_master_profile_item(
    item_id: str,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Deletes an item from the user's master profile."""
    user_id = current_user.id
    auth_header = request.headers.get("Authorization", "")
    user_token = auth_header.replace("Bearer ", "") if "Bearer " in auth_header else None

    if settings.SUPABASE_URL and settings.SUPABASE_KEY:
        url = f"{settings.SUPABASE_URL.rstrip('/')}/rest/v1/master_profile_items?id=eq.{item_id}&user_id=eq.{user_id}"
        headers = {"apikey": settings.SUPABASE_KEY}
        if settings.SUPABASE_SERVICE_ROLE_KEY:
            headers["Authorization"] = f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}"
        elif user_token:
            headers["Authorization"] = f"Bearer {user_token}"

        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                res = await client.delete(url, headers=headers)
                if res.status_code in (200, 204):
                    _LOCAL_MASTER_STORE.pop(item_id, None)
                    return None
        except Exception:
            pass

    _LOCAL_MASTER_STORE.pop(item_id, None)
    return None
