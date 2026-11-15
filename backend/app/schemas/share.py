from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ShareLinkConfig(BaseModel):
    is_active: bool = True
    password: Optional[str] = None
    expires_at: Optional[datetime] = None
    allow_pdf_download: bool = True
    no_index: bool = True


class ShareLinkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    slug: str
    is_active: bool
    has_password: bool
    expires_at: Optional[datetime] = None
    allow_pdf_download: bool
    no_index: bool
    view_count: int = 0
    last_viewed_at: Optional[datetime] = None
    share_url: str = ""


class PublicResumeResponse(BaseModel):
    password_required: bool = False
    is_expired: bool = False
    title: Optional[str] = None
    content: Optional[dict] = None
    style: Optional[dict] = None
    allow_pdf_download: bool = True
    no_index: bool = True
    doc_type: str = "resume"
