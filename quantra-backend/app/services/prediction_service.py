"""Quantra — Prediction service."""

from __future__ import annotations

import logging

from app.analysis.prediction_engine import generate_prediction
from app.analysis.technical_analyzer import analyze as technical_analyze
from app.core.redis_client import get_ml_score, get_prediction, set_prediction
from app.services.market_data_service import fetch_ohlcv, fetch_stock_info

logger = logging.getLogger(__name__)


async def quick_prediction(ticker: str, horizon_days: int = 5) -> dict:
    """Quick prediction — cached, <200ms."""
    # Check cache
    cached = await get_prediction(ticker, horizon_days)
    if cached:
        return cached

    # Generate fresh prediction
    df = await fetch_ohlcv(ticker, interval="1d", period="6mo")
    tech_result = technical_analyze(ticker, df) if not df.empty else None
    stock_info = await fetch_stock_info(ticker)
    ml_score = await get_ml_score(ticker)

    result = await generate_prediction(
        ticker=ticker,
        technical_result=tech_result,
        fundamental_data=stock_info,
        ml_score=ml_score,
        horizon_days=horizon_days,
    )

    response = {
        "ticker": result.ticker,
        "direction": result.direction,
        "confidence": result.confidence,
        "horizon_days": result.horizon_days,
        "ml_score": result.ml_score,
        "technical_score": result.technical_score,
        "sentiment_score": result.sentiment_score,
        "fundamental_score": result.fundamental_score,
        "summary": result.summary,
        "key_factors": result.key_factors,
        "risks": result.risks,
        "generated_at": result.generated_at.isoformat(),
        "valid_until": result.valid_until.isoformat() if result.valid_until else None,
    }

    await set_prediction(ticker, horizon_days, response)
    return response
