"""Pydantic v2 models for CompositionResult schema (supporting 1.0.0 and 1.1.0)."""

from __future__ import annotations
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, confloat, Field


class SchemaVersion(str, Enum):
    field_1_0_0 = '1.0.0'
    field_1_1_0 = '1.1.0'


class Kind(str, Enum):
    original = 'original'
    tailored = 'tailored'
    export = 'export'


class Format(str, Enum):
    pdf = 'pdf'
    docx = 'docx'


class OutputFile(BaseModel):
    model_config = ConfigDict(extra='forbid')
    kind: Kind
    format: Optional[Format] = None
    storage_path: str
    mime_type: str
    size_bytes: int
    download_url: Optional[str] = None


class OverflowReport(BaseModel):
    model_config = ConfigDict(extra='forbid')
    has_overflow: bool
    overflowing_slots: List[str]
    details: str


class InvariantCheck(BaseModel):
    model_config = ConfigDict(extra='forbid')
    name: str
    passed: bool
    details: str = ""


class IntegrityReport(BaseModel):
    model_config = ConfigDict(extra='forbid')
    passed: bool
    violations: List[str] = Field(default_factory=list)
    invariants_checked: List[InvariantCheck] = Field(default_factory=list)
    byte_identical_parts: List[str] = Field(default_factory=list)
    id_collisions_found: int = 0


class FitLoopRound(BaseModel):
    model_config = ConfigDict(extra='forbid')
    round: int
    overflowing_slots: List[str] = Field(default_factory=list)
    shortened_changes: List[str] = Field(default_factory=list)
    page_count: Optional[int] = None


class FitLoop(BaseModel):
    model_config = ConfigDict(extra='forbid')
    rounds_executed: int = 0
    overflow_resolved: bool = True
    history: List[FitLoopRound] = Field(default_factory=list)


class PerSlotLineCount(BaseModel):
    model_config = ConfigDict(extra='forbid')
    max_lines: int
    lines_before: Optional[int] = None
    lines_after: Optional[int] = None
    clipped: bool = False


class Status(str, Enum):
    ready = 'ready'
    layout_changed = 'layout_changed'
    failed = 'failed'
    # 1.0.0 compatibility
    success = 'success'
    warning = 'warning'


class CompositionResult(BaseModel):
    model_config = ConfigDict(extra='forbid')
    schema_version: SchemaVersion = SchemaVersion.field_1_1_0
    run_id: str
    resume_id: str
    composition_id: Optional[str] = None
    output_files: List[OutputFile]
    fidelity_score: confloat(ge=0.0, le=100.0)
    page_count_before: Optional[int] = None
    page_count_after: Optional[int] = None
    page_count_preserved: Optional[bool] = None
    integrity_report: Optional[IntegrityReport] = None
    fit_loop: Optional[FitLoop] = None
    per_slot_lines: Optional[Dict[str, PerSlotLineCount]] = None
    overflow_report: OverflowReport
    final_content: Optional[Dict[str, Any]] = None
    substituted_fonts: List[str] = Field(default_factory=list)
    whitespace_created_pt: float = 0.0
    warnings: List[str] = Field(default_factory=list)
    status: Status = Status.ready
