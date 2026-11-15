from typing import List, Optional, Literal
from pydantic import BaseModel, Field


BulletActionType = Literal[
    "improve", "shorten", "add_impact", "fix_grammar", "change_tone"
]
ToneType = Literal["formal", "casual", "technical", "executive"]


class BulletActionRequest(BaseModel):
    text: str = Field(..., min_length=3, description="Original bullet text")
    action: BulletActionType = Field(..., description="Action to perform on bullet")
    tone: Optional[ToneType] = Field("formal", description="Target tone")
    metric_answer: Optional[str] = Field(
        None, description="User-supplied metric/number for add_impact"
    )
    context: Optional[str] = Field(
        None, description="Context such as job title or section name"
    )


class BulletActionResponse(BaseModel):
    original_text: str
    suggested_text: str
    diff_summary: str
    clarification_needed: Optional[str] = None
    action: str
    tokens_used: int = 0
    estimated_cost: float = 0.0


class SummaryGenerateRequest(BaseModel):
    job_title: Optional[str] = Field(None, description="Target job title")
    experience_bullets: List[str] = Field(
        default_factory=list, description="List of experience highlights"
    )
    skills: List[str] = Field(
        default_factory=list, description="Key skills to highlight"
    )
    tone: Optional[str] = Field("formal", description="Tone of summary")


class SummaryGenerateResponse(BaseModel):
    suggested_summary: str
    key_themes: List[str] = Field(default_factory=list)
    tokens_used: int = 0
    estimated_cost: float = 0.0


class SkillsSuggestRequest(BaseModel):
    experience_texts: List[str] = Field(
        ..., description="Experience and project descriptions to extract from"
    )
    existing_skills: List[str] = Field(
        default_factory=list, description="Already listed skills to avoid duplicates"
    )


class SkillSuggestionItem(BaseModel):
    skill: str
    category: str = "Technical"
    source_context: str = ""


class SkillsSuggestResponse(BaseModel):
    suggestions: List[SkillSuggestionItem] = Field(default_factory=list)
    tokens_used: int = 0
    estimated_cost: float = 0.0


class AiUsageResponse(BaseModel):
    daily_requests_used: int
    daily_limit: int = 50
    requests_remaining: int
    total_cost_usd: float
