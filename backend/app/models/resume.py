import uuid
from typing import Optional, List
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(
        String, nullable=False, default="Untitled Resume"
    )
    doc_type: Mapped[str] = mapped_column(
        String, nullable=False, default="resume", index=True
    )

    target_job_title: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    tags: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    folder: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_archived: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)

    tailored_from_id: Mapped[Optional[str]] = mapped_column(
        String, ForeignKey("resumes.id", ondelete="SET NULL"), nullable=True
    )
    linked_resume_id: Mapped[Optional[str]] = mapped_column(
        String, ForeignKey("resumes.id", ondelete="SET NULL"), nullable=True
    )
    thumbnail_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Stored as JSON/JSONB
    content: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    style: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user = relationship("User", back_populates="resumes")
    tailored_from = relationship("Resume", remote_side=[id], foreign_keys=[tailored_from_id])


# Document is an alias for Resume to provide unified Document nomenclature for Phase 3
Document = Resume
