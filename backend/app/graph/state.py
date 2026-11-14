from typing import TypedDict, List, Dict, Any, Optional
from app.schemas.content import ResumeContent
from app.schemas.style import ResumeStyle
from app.schemas.tailoring import JDAnalysis, ChangeReason, MatchScore


class TailoringState(TypedDict, total=False):
    job_id: str
    template_id: str
    original_docx_path: str
    original_pdf_path: str
    jd_text: str

    fingerprint: Dict[str, Any]
    role_map: Dict[str, Any]
    content_to_paragraphs: Dict[str, List[int]]
    source_content: ResumeContent
    source_style: ResumeStyle

    jd_analysis: JDAnalysis

    tailored_content: ResumeContent
    changes: List[ChangeReason]
    skills_missing: List[str]

    tailored_docx_path: str
    tailored_pdf_path: str

    fit_attempt: int
    fit_passed: bool
    original_page_count: int
    tailored_page_count: int
    offending_bullet_ids: List[str]
    stricter_budgets: Dict[str, int]
    warnings: List[str]

    match_score_before: MatchScore
    match_score_after: MatchScore

    current_step: str
    error: Optional[str]
