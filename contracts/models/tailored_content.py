"""Pydantic v2 models generated for TailoredContent schema (supporting 1.0.0 and 1.1.0)."""

from __future__ import annotations
from enum import Enum
from typing import List, Optional, Union, Any, Dict
from pydantic import BaseModel, ConfigDict, Field, confloat


class SchemaVersion(str, Enum):
    field_1_0_0 = "1.0.0"
    field_1_1_0 = "1.1.0"


class NoNewFactsAllowed(Enum):
    boolean_True = True


class AllowedInlineMarkupEnum(str, Enum):
    bold = "bold"
    italic = "italic"
    link = "link"


class SyntaxGuide(BaseModel):
    model_config = ConfigDict(extra="forbid")
    bold: str = "**text**"
    italic: str = "*text*"
    link: str = "[label](url)"


class Rules(BaseModel):
    model_config = ConfigDict(extra="forbid")
    no_new_facts_allowed: NoNewFactsAllowed = Field(
        ...,
        description="Enforces strict anti-hallucination: every claim must be grounded in the original resume or confirmed master profile.",
    )
    allowed_inline_markup: List[AllowedInlineMarkupEnum] = Field(
        ...,
        description="List of allowed inline markup types. Raw HTML tags and block elements are forbidden.",
    )
    syntax_guide: SyntaxGuide


class SourceReference(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source_item_id: str
    source_bullet_id: Optional[str] = None
    verified_fact: str = ""
    is_grounded: bool = True


class ChangeType(str, Enum):
    rewrite_bullet = "rewrite_bullet"
    reorder_bullets = "reorder_bullets"
    reorder_items = "reorder_items"
    show_item = "show_item"
    hide_item = "hide_item"
    reorder_skills = "reorder_skills"
    regroup_skills = "regroup_skills"
    rewrite_summary = "rewrite_summary"
    normalize_term = "normalize_term"
    add_item_from_master_profile = "add_item_from_master_profile"


class RiskLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class ChangeStatus(str, Enum):
    proposed = "proposed"
    accepted = "accepted"
    rejected = "rejected"
    auto_rejected = "auto_rejected"


class GeneratorMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")
    model: str = "gpt-4o"
    prompt_version: str = "1.1.0"
    weights_version: str = "1.0.0"
    taxonomy_version: str = "1.0.0"


class Change(BaseModel):
    model_config = ConfigDict(extra="forbid")
    change_id: str
    type: ChangeType = ChangeType.rewrite_bullet
    target_content_id: Optional[str] = None
    slot_id: Optional[str] = None
    item_id: Optional[str] = None
    field: str
    before: Optional[Union[str, List[str]]] = None
    after: Optional[Union[str, List[str]]] = None
    reason: str
    evidence_ids: List[str] = Field(default_factory=list)
    keywords_touched: List[str] = Field(default_factory=list)
    risk_level: RiskLevel = RiskLevel.low
    status: ChangeStatus = ChangeStatus.proposed
    rejection_reason: Optional[str] = None
    gates_tripped: List[str] = Field(default_factory=list)
    generator: Optional[GeneratorMetadata] = None

    # Backward-compatibility fields for 1.0.0 fixtures
    target_id: Optional[str] = None
    original_text: Optional[str] = None
    tailored_text: Optional[str] = None
    source_reference: Optional[SourceReference] = None


class ScoreBreakdown(BaseModel):
    model_config = ConfigDict(extra="forbid")
    required_skill_coverage: confloat(ge=0.0, le=40.0) = 0.0
    preferred_skill_coverage: confloat(ge=0.0, le=15.0) = 0.0
    semantic_relevance: confloat(ge=0.0, le=25.0) = 0.0
    seniority_fit: confloat(ge=0.0, le=10.0) = 0.0
    ats_readability: confloat(ge=0.0, le=10.0) = 0.0
    stuffing_penalty: confloat(ge=0.0, le=20.0) = 0.0
    confidence_note: Optional[str] = None


class MatchedSkill(BaseModel):
    model_config = ConfigDict(extra="forbid")
    skill: str
    canonical_name: str
    category: str
    content_ids: List[str] = Field(default_factory=list)


class MissingSkill(BaseModel):
    model_config = ConfigDict(extra="forbid")
    skill: str
    canonical_name: str
    category: str
    importance: str = "required"


class PresentNotVisibleSkill(BaseModel):
    model_config = ConfigDict(extra="forbid")
    skill: str
    canonical_name: str
    master_item_id: str


class AdjacentSkill(BaseModel):
    model_config = ConfigDict(extra="forbid")
    jd_skill: str
    resume_skill: str
    relation: str


class SkillsAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")
    matched_skills: List[MatchedSkill] = Field(default_factory=list)
    missing_skills: List[MissingSkill] = Field(default_factory=list)
    present_not_visible: List[PresentNotVisibleSkill] = Field(default_factory=list)
    adjacent_skills: List[AdjacentSkill] = Field(default_factory=list)


class Suggestion(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    suggestion_id: str
    skill: str
    canonical_name: str
    category: str
    class_: str = Field(..., alias="class")
    prompt_text: str
    target_section_id: Optional[str] = None
    confirmed: bool = False


class TailoredContent(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: SchemaVersion = SchemaVersion.field_1_1_0
    run_id: str
    resume_id: str
    job_description_id: Optional[str] = None
    mode: str = "full"
    rules: Rules
    score_before: confloat(ge=0.0, le=100.0)
    score_after: confloat(ge=0.0, le=100.0)
    score_breakdown: Optional[ScoreBreakdown] = None
    skills_analysis: Optional[SkillsAnalysis] = None
    generator: Optional[GeneratorMetadata] = None
    changes: List[Change] = Field(default_factory=list)
    rejected_changes: List[Change] = Field(default_factory=list)
    suggestions: List[Suggestion] = Field(default_factory=list)
    matched_keywords: List[str] = Field(default_factory=list)
    missing_keywords: List[str] = Field(default_factory=list)
