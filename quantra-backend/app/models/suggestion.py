"""
Suggestion ORM model — AI-generated personalized investment suggestions.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDMixin


class Suggestion(UUIDMixin, Base):
    __tablename__ = "suggestions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    ticker: Mapped[str | None] = mapped_column(
        Text, ForeignKey("stock_meta.ticker"), nullable=True
    )
    action: Mapped[str | None] = mapped_column(
        String(10), nullable=True
    )  # BUY | WATCH | AVOID
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

    # Relationships
    user = relationship("User", back_populates="suggestions")

    def __repr__(self) -> str:
        return f"<Suggestion {self.ticker} {self.action}>"
