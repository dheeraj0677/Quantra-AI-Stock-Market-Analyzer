"""
News article & sentiment ORM model.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, UUIDMixin


class NewsArticle(UUIDMixin, Base):
    __tablename__ = "news_articles"

    ticker: Mapped[str | None] = mapped_column(
        Text, ForeignKey("stock_meta.ticker"), nullable=True, index=True
    )
    headline: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str | None] = mapped_column(Text, nullable=True)
    url: Mapped[str | None] = mapped_column(Text, unique=True, nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    sentiment: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )  # POSITIVE | NEGATIVE | NEUTRAL
    sentiment_score: Mapped[float | None] = mapped_column(
        Numeric, nullable=True
    )  # -1.0 to +1.0
    impact_level: Mapped[str | None] = mapped_column(
        String(10), nullable=True
    )  # HIGH | MEDIUM | LOW

    def __repr__(self) -> str:
        return f"<NewsArticle {self.ticker}: {self.headline[:50]}>"
