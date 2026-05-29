"""
Prediction & PredictionFactor ORM models.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDMixin


class Prediction(UUIDMixin, Base):
    __tablename__ = "predictions"

    ticker: Mapped[str] = mapped_column(
        Text, ForeignKey("stock_meta.ticker"), nullable=False, index=True
    )
    direction: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # UP | DOWN | SIDEWAYS
    confidence: Mapped[float] = mapped_column(Numeric, nullable=False)  # 0.0 to 1.0
    horizon_days: Mapped[int] = mapped_column(Integer, default=5, server_default="5")
    ml_score: Mapped[float | None] = mapped_column(Numeric, nullable=True)  # 0–100
    technical_score: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    sentiment_score: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    fundamental_score: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    reasoning: Mapped[Any | None] = mapped_column(JSONB, nullable=True)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    valid_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    factors = relationship(
        "PredictionFactor", back_populates="prediction", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Prediction {self.ticker} {self.direction} conf={self.confidence}>"


class PredictionFactor(Base):
    __tablename__ = "prediction_factors"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    prediction_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("predictions.id"), nullable=False, index=True
    )
    factor_type: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )  # TECHNICAL | NEWS | FUNDAMENTAL | PATTERN
    factor_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    impact: Mapped[str | None] = mapped_column(
        String(10), nullable=True
    )  # BULLISH | BEARISH | NEUTRAL
    weight: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    prediction = relationship("Prediction", back_populates="factors")

    def __repr__(self) -> str:
        return f"<PredictionFactor {self.factor_type}: {self.factor_name}>"
