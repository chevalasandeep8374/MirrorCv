from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.content import ResumeContent
from app.schemas.style import ResumeStyle


class ResumeCreate(BaseModel):
    title: str = "Untitled Resume"
    content: Optional[ResumeContent] = None
    style: Optional[ResumeStyle] = None


class ResumeUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[ResumeContent] = None
    style: Optional[ResumeStyle] = None


class ResumeSummary(BaseModel):
    id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResumeDetail(BaseModel):
    id: str
    user_id: str
    title: str
    content: ResumeContent
    style: ResumeStyle
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
