"""Pipeline execution state definition for LangGraph orchestrator."""

from typing import TypedDict, List, Dict, Any, Optional

from contracts.models.template_profile import TemplateProfile
from contracts.models.tailored_content import TailoredContent
from contracts.models.composition_result import CompositionResult


class PipelineRunState(TypedDict, total=False):
    run_id: str
    user_id: str
    user_token: Optional[str]
    resume_id: str
    job_description_id: Optional[str]
    job_description_text: str
    mode: str  # "analyze" or "full"

    # Source resume state
    content: Dict[str, Any]
    style: Dict[str, Any]

    # Agent outputs (strictly typed to contracts)
    template_profile: Optional[TemplateProfile]
    tailored_content: Optional[TailoredContent]
    composition_result: Optional[CompositionResult]

    # Progress tracking (Zero resume text or personal data in stage_log)
    current_stage: str
    stage_log: List[Dict[str, Any]]
    status: str
    error: Optional[str]
