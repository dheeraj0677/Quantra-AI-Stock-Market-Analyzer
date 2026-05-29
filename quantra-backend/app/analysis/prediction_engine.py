"""
Quantra — Prediction Engine.

Weighted ensemble: technicals (40%) + sentiment (35%) + fundamental (25%)
Combined with ML classifier probability: 60% ML + 40% composite.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any

from app.analysis.factor_explainer import explain_factors

logger = logging.getLogger(__name__)


@dataclass
class PredictionResult:
    """Final prediction output."""

    ticker: str
    direction: str = "SIDEWAYS"  # UP | DOWN | SIDEWAYS
    confidence: float = 0.5
    horizon_days: int = 5
    ml_score: float = 50.0
    technical_score: float = 50.0
    sentiment_score: float = 0.0
    fundamental_score: float = 50.0
    summary: str = ""
    key_factors: list[dict[str, Any]] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    valid_until: datetime | None = None


# Default weights
WEIGHTS = {
    "technical": 0.40,
    "sentiment": 0.35,
    "fundamental": 0.25,
}

ML_WEIGHT = 0.60
COMPOSITE_WEIGHT = 0.40


def compute_final_prediction(
    technical_score: float,
    sentiment_score: float,
    fundamental_score: float,
    ml_direction_prob: float | None = None,
) -> tuple[str, float]:
    """
    Compute direction and confidence from all signal components.

    Args:
        technical_score: 0–100 composite technical score
        sentiment_score: -1.0 to +1.0 news sentiment
        fundamental_score: 0–100 fundamental quality score
        ml_direction_prob: 0.0–1.0 ML classifier probability (optional)

    Returns:
        (direction, confidence) tuple
    """
    # Normalize sentiment from [-1, 1] to [0, 100]
    sentiment_normalized = (sentiment_score + 1) * 50

    composite = (
        technical_score * WEIGHTS["technical"]
        + sentiment_normalized * WEIGHTS["sentiment"]
        + fundamental_score * WEIGHTS["fundamental"]
    )

    # Determine direction from composite
    if composite > 58:
        direction = "UP"
    elif composite < 42:
        direction = "DOWN"
    else:
        direction = "SIDEWAYS"

    # Combine with ML classifier if available
    if ml_direction_prob is not None:
        final_confidence = ML_WEIGHT * ml_direction_prob + COMPOSITE_WEIGHT * (composite / 100)
    else:
        # Without ML, use composite directly with wider confidence range
        final_confidence = composite / 100

    # Adjust confidence — SIDEWAYS should have lower confidence
    if direction == "SIDEWAYS":
        final_confidence *= 0.7

    return direction, round(max(0.0, min(1.0, final_confidence)), 3)


async def generate_prediction(
    ticker: str,
    technical_result=None,
    news_analysis=None,
    fundamental_data: dict | None = None,
    ml_score: float | None = None,
    ml_direction_prob: float | None = None,
    horizon_days: int = 5,
) -> PredictionResult:
    """
    Generate a complete prediction by orchestrating all signal sources.

    This is the main entry point for the prediction engine.
    """
    result = PredictionResult(ticker=ticker, horizon_days=horizon_days)

    # ── Technical Score ──
    if technical_result is not None:
        result.technical_score = technical_result.composite_score
    else:
        result.technical_score = 50.0

    # ── Sentiment Score ──
    if news_analysis is not None:
        result.sentiment_score = news_analysis.sentiment_30d
    else:
        result.sentiment_score = 0.0

    # ── Fundamental Score ──
    if fundamental_data:
        result.fundamental_score = _compute_fundamental_score(fundamental_data)
    else:
        result.fundamental_score = 50.0

    # ── ML Score ──
    result.ml_score = ml_score if ml_score is not None else 50.0

    # ── Compute Direction & Confidence ──
    result.direction, result.confidence = compute_final_prediction(
        technical_score=result.technical_score,
        sentiment_score=result.sentiment_score,
        fundamental_score=result.fundamental_score,
        ml_direction_prob=ml_direction_prob,
    )

    # ── Generate Factors ──
    result.key_factors = _collect_factors(
        technical_result, news_analysis, fundamental_data
    )

    # ── Generate Summary ──
    result.summary = _generate_summary(result)

    # ── Identify Risks ──
    result.risks = _identify_risks(
        technical_result, news_analysis, fundamental_data
    )

    # ── Validity ──
    result.valid_until = result.generated_at + timedelta(hours=6)

    return result


def _compute_fundamental_score(data: dict) -> float:
    """Compute a fundamental quality score (0–100) from financial metrics."""
    score = 50.0

    # PE Ratio — lower is better (relative to sector)
    pe = data.get("pe_ratio")
    if pe is not None:
        if pe < 15:
            score += 12
        elif pe < 25:
            score += 5
        elif pe > 40:
            score -= 10
        elif pe > 60:
            score -= 15

    # ROE — higher is better
    roe = data.get("roe")
    if roe is not None:
        if roe > 0.25:
            score += 12
        elif roe > 0.15:
            score += 6
        elif roe < 0.05:
            score -= 8

    # Debt ratio — lower is better
    de = data.get("debt_to_equity")
    if de is not None:
        if de < 0.3:
            score += 8
        elif de < 1.0:
            score += 3
        elif de > 2.0:
            score -= 10

    # Earnings growth
    eg = data.get("earnings_growth_yoy")
    if eg is not None:
        if eg > 20:
            score += 10
        elif eg > 10:
            score += 5
        elif eg < -10:
            score -= 10

    # Dividend yield (bonus for income)
    dy = data.get("dividend_yield")
    if dy is not None and dy > 0.02:
        score += 5

    return max(0.0, min(100.0, score))


def _collect_factors(
    technical_result,
    news_analysis,
    fundamental_data: dict | None,
) -> list[dict[str, Any]]:
    """Collect and format key prediction factors."""
    factors = []

    # Technical factors
    if technical_result and hasattr(technical_result, "signals"):
        for sig in technical_result.signals[:3]:
            factors.append(
                {
                    "type": "TECHNICAL",
                    "name": sig["name"],
                    "impact": sig["impact"],
                    "desc": explain_factors("TECHNICAL", sig["name"], sig.get("points", 0)),
                }
            )

    # News factors
    if news_analysis:
        if news_analysis.sentiment_30d > 0.3:
            factors.append(
                {
                    "type": "NEWS",
                    "name": "Positive News Sentiment",
                    "impact": "BULLISH",
                    "desc": f"Rolling 30-day sentiment is {news_analysis.sentiment_30d:.2f} "
                    f"based on {news_analysis.article_count_30d} articles",
                }
            )
        elif news_analysis.sentiment_30d < -0.3:
            factors.append(
                {
                    "type": "NEWS",
                    "name": "Negative News Sentiment",
                    "impact": "BEARISH",
                    "desc": f"Rolling 30-day sentiment is {news_analysis.sentiment_30d:.2f} "
                    f"based on {news_analysis.article_count_30d} articles",
                }
            )

        if news_analysis.key_events:
            factors.append(
                {
                    "type": "NEWS",
                    "name": news_analysis.key_events[0][:60],
                    "impact": "BULLISH" if news_analysis.sentiment_7d > 0 else "BEARISH",
                    "desc": f"Key event: {news_analysis.key_events[0]}",
                }
            )

    # Fundamental factors
    if fundamental_data:
        roe = fundamental_data.get("roe")
        if roe and roe > 0.20:
            factors.append(
                {
                    "type": "FUNDAMENTAL",
                    "name": "Strong ROE",
                    "impact": "BULLISH",
                    "desc": f"Return on Equity of {roe*100:.1f}% indicates strong profitability",
                }
            )

        pe = fundamental_data.get("pe_ratio")
        if pe and pe < 15:
            factors.append(
                {
                    "type": "FUNDAMENTAL",
                    "name": "Low PE Ratio",
                    "impact": "BULLISH",
                    "desc": f"PE ratio of {pe:.1f} suggests stock may be undervalued",
                }
            )

    return factors[:6]  # Cap at 6 factors


def _generate_summary(result: PredictionResult) -> str:
    """Generate a human-readable summary of the prediction."""
    direction_text = {
        "UP": "bullish momentum",
        "DOWN": "bearish signals",
        "SIDEWAYS": "consolidation pattern",
    }

    confidence_text = (
        "high" if result.confidence > 0.7
        else "moderate" if result.confidence > 0.5
        else "low"
    )

    factors_text = ""
    if result.key_factors:
        bullish = [f for f in result.key_factors if f.get("impact") == "BULLISH"]
        bearish = [f for f in result.key_factors if f.get("impact") == "BEARISH"]
        parts = []
        if bullish:
            parts.append(f"{', '.join(f['name'] for f in bullish[:2])}")
        if bearish:
            parts.append(f"offset by {', '.join(f['name'] for f in bearish[:2])}")
        factors_text = f" backed by {' '.join(parts)}" if parts else ""

    return (
        f"{result.ticker} shows {direction_text.get(result.direction, 'mixed signals')} "
        f"with {confidence_text} confidence ({result.confidence:.0%})"
        f"{factors_text}."
    )


def _identify_risks(
    technical_result,
    news_analysis,
    fundamental_data: dict | None,
) -> list[str]:
    """Identify key risk factors."""
    risks = []

    if technical_result:
        if technical_result.rsi and technical_result.rsi > 70:
            risks.append("RSI in overbought zone — correction risk")
        if technical_result.volume_spike:
            risks.append("Unusual volume spike — potential volatility ahead")

    if news_analysis:
        if news_analysis.sentiment_trend == "DECLINING":
            risks.append("Declining news sentiment trend over past week")
        neg_high_impact = [
            e for e in (news_analysis.top_negative or [])
        ]
        if neg_high_impact:
            risks.append(f"Negative news: {neg_high_impact[0].get('headline', '')[:80]}")

    if fundamental_data:
        de = fundamental_data.get("debt_to_equity")
        if de and de > 1.5:
            risks.append(f"High debt-to-equity ratio ({de:.2f})")

    if not risks:
        risks.append("General market risk — past performance doesn't guarantee future results")

    return risks[:5]
