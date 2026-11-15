import uuid
from typing import Optional
from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, JSON, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class TailoringJob(Base):
    __tablename__ = "tailoring_jobs"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    template_id: Mapped[str] = mapped_column(
        String, ForeignKey("uploaded_templates.id", ondelete="CASCADE"), nullable=False, index=True
    )

    status: Mapped[str] = mapped_column(String, default="pending", nullable=False)
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    current_step: Mapped[str] = mapped_column(String, default="queued", nullable=False)

    jd_text: Mapped[str] = mapped_column(Text, nullable=False)
    jd_analysis: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    tailored_content: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    changes: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    skills_missing: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    match_score_before: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    match_score_after: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    tailored_docx_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    tailored_pdf_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    fidelity_tier: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    fidelity_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    warnings: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
