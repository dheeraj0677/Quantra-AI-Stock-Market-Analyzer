"""
Pydantic v2 schemas — Stock data.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class StockSearchResult(BaseModel):
    ticker: str
    name: str
    exchange: str | None = None
    sector: str | None = None


class StockProfile(BaseModel):
    ticker: str
    name: str
    exchange: str | None = None
    sector: str | None = None
    industry: str | None = None
    market_cap: float | None = None
    current_price: float | None = None
    ml_score: float | None = None
    pe_ratio: float | None = None
    pb_ratio: float | None = None
    roe: float | None = None
    eps: float | None = None
    dividend_yield: float | None = None
    high_52w: float | None = None
    low_52w: float | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class OHLCVBar(BaseModel):
    time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    interval: str = "1d"


class OHLCVResponse(BaseModel):
    ticker: str
    interval: str
    bars: list[OHLCVBar]
    count: int


class TechnicalIndicators(BaseModel):
    ticker: str
    rsi: float | None = None
    rsi_signal: str | None = None  # OVERSOLD | OVERBOUGHT | NEUTRAL
    macd: float | None = None
    macd_signal_line: float | None = None
    macd_histogram: float | None = None
    macd_crossover: str | None = None  # BULLISH | BEARISH | NONE
    bb_upper: float | None = None
    bb_middle: float | None = None
    bb_lower: float | None = None
    bb_position: float | None = None  # 0–1 position within bands
    atr: float | None = None
    obv: float | None = None
    obv_trend: str | None = None  # RISING | FALLING | FLAT
    ema_9: float | None = None
    ema_21: float | None = None
    ema_50: float | None = None
    ema_200: float | None = None
    volume_spike: bool | None = None
    patterns_detected: list[str] | None = None
    composite_score: float | None = None  # 0–100


class FundamentalData(BaseModel):
    ticker: str
    pe_ratio: float | None = None
    pb_ratio: float | None = None
    roe: float | None = None
    eps: float | None = None
    debt_to_equity: float | None = None
    dividend_yield: float | None = None
    market_cap: float | None = None
    earnings_growth_yoy: float | None = None
    revenue_growth_yoy: float | None = None
    promoter_holding_pct: float | None = None
    fii_holding_change: str | None = None

    model_config = {"from_attributes": True}


class SimilarStock(BaseModel):
    ticker: str
    name: str
    sector: str | None = None
    ml_score: float | None = None
    direction: str | None = None
