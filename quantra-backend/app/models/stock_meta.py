"""
Stock metadata ORM model.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class StockMeta(Base):
    __tablename__ = "stock_meta"

    ticker: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    exchange: Mapped[str | None] = mapped_column(String(20), nullable=True)
    sector: Mapped[str | None] = mapped_column(Text, nullable=True)
    industry: Mapped[str | None] = mapped_column(Text, nullable=True)
    market_cap: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    pe_ratio: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    pb_ratio: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    roe: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    eps: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    dividend_yield: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    high_52w: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    low_52w: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<StockMeta {self.ticker}: {self.name}>"
