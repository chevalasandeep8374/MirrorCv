"""Tailoring and JD analysis schemas for Agent 2."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.content import ResumeContent


class JDAnalysis(BaseModel):
    model_config = ConfigDict(extra="ignore")
    job_title: Optional[str] = "Software Engineer"
    company: Optional[str] = None
    seniority: str = "Senior"
    seniority_level: int = 3  # 0=Intern/Fresher, 1=Junior, 2=Mid, 3=Senior, 4=Staff/Lead, 5=Director
    years_required: Optional[float] = 3.0
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    tools_and_tech: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    domain: Optional[str] = "Software Engineering"
    education_requirements: List[str] = Field(default_factory=list)
    soft_skills: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    weighted_keywords: Dict[str, float] = Field(default_factory=dict)
    text_hash: Optional[str] = None


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
