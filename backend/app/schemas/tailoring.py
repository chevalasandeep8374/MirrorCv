from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.content import ResumeContent


class JDAnalysis(BaseModel):
    job_title: Optional[str] = None
    seniority: str = "Senior"
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    tools_and_tech: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    domain: Optional[str] = None


class ChangeReason(BaseModel):
    id: str
    section_id: str
    item_id: Optional[str] = None
    bullet_id: Optional[str] = None
    original_text: str
    new_text: str
    reason: str
    accepted: bool = True


class MatchScore(BaseModel):
    total_score: int = 0
    matched_keywords: List[str] = Field(default_factory=list)
    missing_keywords: List[str] = Field(default_factory=list)
    coverage_ratio: float = 0.0
    explanation: str = ""


class TailoredOutput(BaseModel):
    tailored_content: ResumeContent
    changes: List[ChangeReason] = Field(default_factory=list)
    skills_missing: List[str] = Field(default_factory=list)
    character_budget_report: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
