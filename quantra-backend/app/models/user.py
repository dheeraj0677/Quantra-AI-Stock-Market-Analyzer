"""
User ORM model.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import ARRAY, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDMixin


class User(UUIDMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(Text, unique=True, nullable=False, index=True)
    name: Mapped[str | None] = mapped_column(Text, nullable=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    plan: Mapped[str] = mapped_column(String(20), default="free", server_default="free")
    risk_profile: Mapped[str] = mapped_column(
        String(20), default="moderate", server_default="moderate"
    )
    preferred_sectors: Mapped[list[str] | None] = mapped_column(
        ARRAY(Text), nullable=True
    )
    investment_horizon: Mapped[str] = mapped_column(
        String(20), default="medium", server_default="medium"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    last_login: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    portfolios = relationship("Portfolio", back_populates="user", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="user", cascade="all, delete-orphan")
    suggestions = relationship("Suggestion", back_populates="user", cascade="all, delete-orphan")
    backtest_runs = relationship("BacktestRun", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User {self.email}>"
