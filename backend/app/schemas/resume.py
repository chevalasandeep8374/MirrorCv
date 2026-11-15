from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.content import ResumeContent
from app.schemas.style import ResumeStyle


class ResumeCreate(BaseModel):
    title: str = "Untitled Resume"
    doc_type: str = "resume"  # "resume" or "cover_letter"
    target_job_title: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    folder: Optional[str] = None
    content: Optional[ResumeContent] = None
    style: Optional[ResumeStyle] = None


class ResumePatch(BaseModel):
    title: Optional[str] = None
    target_job_title: Optional[str] = None
    tags: Optional[List[str]] = None
    folder: Optional[str] = None
    is_archived: Optional[bool] = None


class ResumeUpdate(BaseModel):
    title: Optional[str] = None
    doc_type: Optional[str] = None
    target_job_title: Optional[str] = None
    tags: Optional[List[str]] = None
    folder: Optional[str] = None
    is_archived: Optional[bool] = None
    content: Optional[ResumeContent] = None
    style: Optional[ResumeStyle] = None


class ResumeSummary(BaseModel):
    id: str
    user_id: str
    title: str
    doc_type: str = "resume"
    target_job_title: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    folder: Optional[str] = None
    is_archived: bool = False
    tailored_from_id: Optional[str] = None
    tailored_from_title: Optional[str] = None
    thumbnail_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResumeDetail(BaseModel):
    id: str
    user_id: str
    title: str
    doc_type: str = "resume"
    target_job_title: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    folder: Optional[str] = None
    is_archived: bool = False
    tailored_from_id: Optional[str] = None
    tailored_from_title: Optional[str] = None
    linked_resume_id: Optional[str] = None
    thumbnail_path: Optional[str] = None
    content: ResumeContent
    style: ResumeStyle
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Document aliases
DocumentCreate = ResumeCreate
DocumentPatch = ResumePatch
DocumentUpdate = ResumeUpdate
DocumentSummary = ResumeSummary
DocumentDetail = ResumeDetail
