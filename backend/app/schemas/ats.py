from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from app.schemas.tailoring import MatchScore


class AtsCheckItem(BaseModel):
    category: Literal["contact", "sections", "bullets", "verbs", "metrics", "dates", "typography"]
    name: str
    passed: bool
    severity: Literal["critical", "warning", "info"]
    message: str
    suggestion: Optional[str] = None


class AtsStats(BaseModel):
    total_bullets: int = 0
    bullets_with_metrics: int = 0
    metrics_percentage: float = 0.0
    strong_verbs_count: int = 0
    weak_verbs_count: int = 0
    average_bullet_chars: float = 0.0


class AtsAnalysisRequest(BaseModel):
    resume_id: Optional[str] = None
    content: Optional[dict] = None
    style: Optional[dict] = None
    job_description: Optional[str] = None


class AtsAnalysisResponse(BaseModel):
    overall_score: int = Field(..., ge=0, le=100)
    grade: str
    summary: str
    checks: List[AtsCheckItem]
    stats: AtsStats
    jd_match: Optional[MatchScore] = None
