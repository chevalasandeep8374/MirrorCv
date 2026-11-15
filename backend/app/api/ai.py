from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.user import User
from app.models.ai_log import AiUsageLog
from app.api.deps import get_current_user
from app.schemas.ai import (
    BulletActionRequest,
    BulletActionResponse,
    SummaryGenerateRequest,
    SummaryGenerateResponse,
    SkillsSuggestRequest,
    SkillsSuggestResponse,
    AiUsageResponse,
)
from app.services.ai_assistant import (
    run_bullet_action,
    run_generate_summary,
    run_suggest_skills,
)

router = APIRouter(prefix="/ai", tags=["AI Assistant"])

DAILY_REQUEST_LIMIT = 50


async def check_and_log_usage(
    db: AsyncSession,
    user_id: str,
    action: str,
    tokens_in: int,
    tokens_out: int,
    cost_usd: float,
) -> None:
    """Enforces daily request limit and logs usage."""
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    
    count_stmt = select(func.count(AiUsageLog.id)).where(
        AiUsageLog.user_id == user_id,
        AiUsageLog.created_at >= today_start,
    )
    result = await db.execute(count_stmt)
    today_count = result.scalar() or 0

    if today_count >= DAILY_REQUEST_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Daily AI request limit reached ({DAILY_REQUEST_LIMIT} requests/day). Resets at midnight UTC.",
        )

    log_entry = AiUsageLog(
        user_id=user_id,
        action=action,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        cost_usd=cost_usd,
    )
    db.add(log_entry)
    await db.commit()


@router.get("/usage", response_model=AiUsageResponse)
async def get_ai_usage(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns today's AI usage and total spend for the authenticated user."""
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    count_stmt = select(func.count(AiUsageLog.id)).where(
        AiUsageLog.user_id == current_user.id,
        AiUsageLog.created_at >= today_start,
    )
    res_count = await db.execute(count_stmt)
    used = res_count.scalar() or 0

    cost_stmt = select(func.sum(AiUsageLog.cost_usd)).where(
        AiUsageLog.user_id == current_user.id
    )
    res_cost = await db.execute(cost_stmt)
    total_cost = res_cost.scalar() or 0.0

    return AiUsageResponse(
        daily_requests_used=used,
        daily_limit=DAILY_REQUEST_LIMIT,
        requests_remaining=max(0, DAILY_REQUEST_LIMIT - used),
        total_cost_usd=round(float(total_cost), 4),
    )


@router.post("/bullet-action", response_model=BulletActionResponse)
async def bullet_action(
    req: BulletActionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Executes AI bullet actions: improve, shorten, add_impact, fix_grammar, change_tone."""
    resp = run_bullet_action(req)
    await check_and_log_usage(
        db=db,
        user_id=current_user.id,
        action=f"bullet_{req.action}",
        tokens_in=30,
        tokens_out=resp.tokens_used,
        cost_usd=resp.estimated_cost,
    )
    return resp


@router.post("/generate-summary", response_model=SummaryGenerateResponse)
async def generate_summary(
    req: SummaryGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generates a professional summary grounded strictly in provided experience."""
    resp = run_generate_summary(req)
    await check_and_log_usage(
        db=db,
        user_id=current_user.id,
        action="generate_summary",
        tokens_in=80,
        tokens_out=resp.tokens_used,
        cost_usd=resp.estimated_cost,
    )
    return resp


@router.post("/suggest-skills", response_model=SkillsSuggestResponse)
async def suggest_skills(
    req: SkillsSuggestRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Extracts grounded skills from experience text for user approval."""
    resp = run_suggest_skills(req)
    await check_and_log_usage(
        db=db,
        user_id=current_user.id,
        action="suggest_skills",
        tokens_in=60,
        tokens_out=resp.tokens_used,
        cost_usd=resp.estimated_cost,
    )
    return resp
