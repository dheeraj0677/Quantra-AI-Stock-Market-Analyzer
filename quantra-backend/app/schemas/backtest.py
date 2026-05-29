"""
Pydantic v2 schemas — Backtest.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class BacktestRequest(BaseModel):
    strategy: dict[str, Any]  # Flexible strategy definition
    ticker: str | None = None
    tickers: list[str] | None = None
    start_date: str | None = None  # YYYY-MM-DD
    end_date: str | None = None
    initial_capital: float = Field(default=100_000, gt=0)


class BacktestStatus(BaseModel):
    id: str
    status: str  # queued | running | completed | failed
    started_at: datetime | None = None
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}


class BacktestTradeResult(BaseModel):
    ticker: str
    entry_date: str
    exit_date: str
    entry_price: float
    exit_price: float
    quantity: float
    pnl: float
    pnl_pct: float
    direction: str  # LONG | SHORT


class BacktestResult(BaseModel):
    id: str
    status: str
    strategy: dict[str, Any]
    total_return_pct: float
    annualized_return_pct: float | None = None
    sharpe_ratio: float | None = None
    max_drawdown_pct: float | None = None
    win_rate: float | None = None
    total_trades: int
    profitable_trades: int
    trades: list[BacktestTradeResult] | None = None
    equity_curve: list[dict[str, Any]] | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}
