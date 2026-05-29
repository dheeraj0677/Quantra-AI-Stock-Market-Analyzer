"""
Pydantic v2 schemas — Portfolio.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class PortfolioCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    currency: str = Field(default="INR", max_length=10)


class PositionCreate(BaseModel):
    ticker: str
    quantity: float = Field(gt=0)
    avg_price: float = Field(gt=0)


class PositionResponse(BaseModel):
    id: str
    ticker: str
    quantity: float
    avg_price: float
    current_price: float | None = None
    pnl: float | None = None
    pnl_pct: float | None = None
    opened_at: datetime

    model_config = {"from_attributes": True}


class PortfolioResponse(BaseModel):
    id: str
    name: str
    currency: str
    created_at: datetime
    positions: list[PositionResponse] | None = None
    total_value: float | None = None
    total_pnl: float | None = None

    model_config = {"from_attributes": True}


class PnLResponse(BaseModel):
    portfolio_id: str
    total_invested: float
    current_value: float
    total_pnl: float
    total_pnl_pct: float
    positions: list[PositionResponse]


class PortfolioAnalysis(BaseModel):
    portfolio_id: str
    diversification_score: float  # 0–100
    risk_level: str  # LOW | MEDIUM | HIGH
    sector_allocation: dict[str, float]
    top_holdings_pct: float
    suggestions: list[str]
    ai_summary: str
