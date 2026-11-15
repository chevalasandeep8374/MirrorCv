from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.user_preset import UserStylePreset
from app.schemas.style import ResumeStyle
from app.services.presets import get_all_system_presets
from app.api.deps import get_current_user

router = APIRouter(prefix="/templates", tags=["Templates & Presets"])


class SaveUserPresetRequest(BaseModel):
    name: str
    style_tokens: ResumeStyle
    source_template_id: Optional[str] = None


@router.get("/presets")
async def list_system_presets():
    """Returns metadata and style token configurations for the 8 system templates."""
    return get_all_system_presets()


@router.get("/presets/{preset_id}")
async def get_system_preset(preset_id: str):
    """Fetch style tokens for a single system preset."""
    all_presets = get_all_system_presets()
    for p in all_presets:
        if p["id"] == preset_id:
            return p
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Template preset '{preset_id}' not found.",
    )


@router.post("/user-presets", status_code=status.HTTP_201_CREATED)
async def create_user_preset(
    payload: SaveUserPresetRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Save the current style tokens as a reusable custom user template."""
    preset = UserStylePreset(
        user_id=current_user.id,
        name=payload.name.strip(),
        style_tokens=payload.style_tokens.model_dump(),
        source_template_id=payload.source_template_id,
    )
    db.add(preset)
    await db.commit()
    await db.refresh(preset)

    return {
        "id": preset.id,
        "name": preset.name,
        "style_tokens": preset.style_tokens,
        "source_template_id": preset.source_template_id,
        "created_at": preset.created_at,
    }


@router.get("/user-presets")
async def list_user_presets(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all custom style presets saved by the user."""
    stmt = (
        select(UserStylePreset)
        .where(UserStylePreset.user_id == current_user.id)
        .order_by(UserStylePreset.created_at.desc())
    )
    res = await db.execute(stmt)
    presets = res.scalars().all()

    return [
        {
            "id": p.id,
            "name": p.name,
            "style_tokens": p.style_tokens,
            "source_template_id": p.source_template_id,
            "created_at": p.created_at,
        }
        for p in presets
    ]


@router.delete("/user-presets/{preset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_preset(
    preset_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Deletes a saved user custom style preset."""
    stmt = select(UserStylePreset).where(
        UserStylePreset.id == preset_id, UserStylePreset.user_id == current_user.id
    )
    res = await db.execute(stmt)
    preset = res.scalars().first()
    if not preset:
        raise HTTPException(status_code=404, detail="User preset not found")

    await db.delete(preset)
    await db.commit()
    return None
