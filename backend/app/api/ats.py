from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.models.resume import Document
from app.api.deps import get_current_user
from app.schemas.ats import AtsAnalysisRequest, AtsAnalysisResponse
from app.services.ats_checker import evaluate_resume_ats

router = APIRouter(prefix="/ats", tags=["ATS Checker"])


@router.post("/analyze", response_model=AtsAnalysisResponse)
async def analyze_ats(
    req: AtsAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Analyzes a resume against ATS formatting, verb strength, metrics, and JD keyword alignment."""
    content_dict = req.content
    style_dict = req.style

    if req.resume_id:
        stmt = select(Document).where(Document.id == req.resume_id)
        result = await db.execute(stmt)
        doc = result.scalar_one_or_none()
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found",
            )
        if doc.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found",
            )
        content_dict = doc.content
        style_dict = doc.style

    if not content_dict:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Either resume_id or content must be provided.",
        )

    return evaluate_resume_ats(
        content_dict=content_dict,
        style_dict=style_dict,
        job_description=req.job_description,
    )
