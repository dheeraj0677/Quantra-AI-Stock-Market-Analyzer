"""
Pydantic v2 schemas — Prediction.

Matches the exact JSON response formats from the design spec.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class PredictionFactorResponse(BaseModel):
    type: str  # TECHNICAL | NEWS | FUNDAMENTAL | PATTERN
    name: str
    impact: str  # BULLISH | BEARISH | NEUTRAL
    desc: str
    weight: float | None = None


class QuickPredictionResponse(BaseModel):
    ticker: str
    direction: str  # UP | DOWN | SIDEWAYS
    confidence: float  # 0.0–1.0
    horizon_days: int
    ml_score: float | None = None  # 0–100
    technical_score: float | None = None
    sentiment_score: float | None = None
    fundamental_score: float | None = None
    summary: str
    key_factors: list[PredictionFactorResponse]
    risks: list[str]
    generated_at: datetime
    valid_until: datetime | None = None


class DeepResearchRequest(BaseModel):
    horizon_days: int = 5
    include_sector_comparison: bool = True


class TechnicalAnalysisResult(BaseModel):
    trend: str  # UPTREND | DOWNTREND | SIDEWAYS
    support_levels: list[float]
    resistance_levels: list[float]
    patterns_detected: list[str]
    indicators: dict[str, Any]


class NewsAnalysisResult(BaseModel):
    sentiment_30d: float
    article_count: int
    top_positive: list[dict[str, Any]]
    top_negative: list[dict[str, Any]]
    key_events: list[str]


class FundamentalAnalysisResult(BaseModel):
    valuation: str  # undervalued | fairly_valued | overvalued
    earnings_growth_yoy: float | None = None
    debt_to_equity: float | None = None
    promoter_holding_pct: float | None = None
    fii_holding_change: str | None = None


class SectorComparisonResult(BaseModel):
    sector_rank: int
    peers: list[str]
    relative_strength: float


class InvestmentSuggestion(BaseModel):
    action: str  # BUY | SELL | HOLD | WATCH
    rationale: str
    position_sizing: str
    time_horizon: str


class DeepResearchResponse(BaseModel):
    ticker: str
    job_id: str
    status: str  # pending | processing | completed | failed
    company_overview: dict[str, Any] | None = None
    technical_analysis: TechnicalAnalysisResult | None = None
    news_analysis: NewsAnalysisResult | None = None
    fundamental_analysis: FundamentalAnalysisResult | None = None
    sector_comparison: SectorComparisonResult | None = None
    prediction: dict[str, Any] | None = None
    investment_suggestion: InvestmentSuggestion | None = None


class DeepResearchJobStatus(BaseModel):
    job_id: str
    status: str
    ticker: str
    estimated_time_seconds: int | None = None


class PredictionHistoryItem(BaseModel):
    id: str
    ticker: str
    direction: str
    confidence: float
    generated_at: datetime
    actual_direction: str | None = None
    was_correct: bool | None = None

    model_config = {"from_attributes": True}
