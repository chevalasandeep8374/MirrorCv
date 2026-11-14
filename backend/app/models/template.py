import uuid
from typing import Optional
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class UploadedTemplate(Base):
    __tablename__ = "uploaded_templates"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    original_filename: Mapped[str] = mapped_column(String, nullable=False)
    file_path: Mapped[str] = mapped_column(String, nullable=False)
    pdf_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    fingerprint: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    role_map: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    content: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    style: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    content_to_paragraphs: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
