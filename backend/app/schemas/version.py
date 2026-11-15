from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class VersionCreate(BaseModel):
    label: Optional[str] = None
    is_manual: bool = True
    change_summary: Optional[str] = None


class VersionSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    version_number: int
    label: Optional[str] = None
    is_manual: bool = False
    change_summary: Optional[str] = None
    created_at: datetime


class VersionDetail(VersionSummary):
    content_snapshot: Dict[str, Any]
    style_snapshot: Dict[str, Any]


class VersionCompareRequest(BaseModel):
    version_a_id: str
    version_b_id: str


class DiffItem(BaseModel):
    path: str
    type: str  # "added" | "removed" | "modified" | "unchanged"
    old_value: Optional[str] = None
    new_value: Optional[str] = None


class VersionCompareResponse(BaseModel):
    version_a_number: int
    version_b_number: int
    diffs: List[DiffItem]
