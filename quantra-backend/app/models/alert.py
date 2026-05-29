"""
Alert ORM model.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import ARRAY, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDMixin


class Alert(UUIDMixin, Base):
    __tablename__ = "alerts"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    ticker: Mapped[str | None] = mapped_column(Text, nullable=True)
    condition: Mapped[Any] = mapped_column(JSONB, nullable=False)
    channels: Mapped[list[str]] = mapped_column(
        ARRAY(Text), default=["push"], server_default="{push}"
    )
    webhook_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    triggered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    user = relationship("User", back_populates="alerts")

    def __repr__(self) -> str:
        return f"<Alert {self.ticker} active={self.is_active}>"
