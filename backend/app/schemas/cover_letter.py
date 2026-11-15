from typing import Optional, List, Literal
from pydantic import BaseModel, ConfigDict
from app.schemas.content import CoverLetterContent, HeaderContent, RecipientContent, CoverLetterParagraph


class CoverLetterGenerateRequest(BaseModel):
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    job_description: Optional[str] = None
    tone: Literal["formal", "friendly", "concise"] = "formal"
    length: Literal["short", "medium", "detailed"] = "medium"


class CoverLetterGenerateResponse(BaseModel):
    document_id: str
    title: str
    cover_letter: CoverLetterContent
    linked_resume_id: str
