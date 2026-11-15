import uuid
from typing import Optional
from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, JSON, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Composition(Base):
    __tablename__ = "compositions"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String, nullable=False, index=True
    )
    resume_id: Mapped[str] = mapped_column(
        String, nullable=False, index=True
    )
    run_id: Mapped[str] = mapped_column(String, nullable=False, index=True)

    composition_result: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    status: Mapped[str] = mapped_column(String, default="ready", nullable=False)
    fidelity_score: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)

    page_count_before: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    page_count_after: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    storage_path_docx: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    storage_path_pdf: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    integrity_report: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    fit_loop: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
