"""
Quantra — Deep Researcher.

Full company deep-dive: fundamentals + news + technicals + sector comparison.
Runs as an async Celery task (~10-30 seconds).
"""

from __future__ import annotations

import logging
from typing import Any

from app.analysis.news_analyzer import fetch_and_analyze, full_news_analysis
from app.analysis.prediction_engine import generate_prediction
from app.analysis.technical_analyzer import analyze as technical_analyze
from app.services.market_data_service import fetch_ohlcv, fetch_stock_info

logger = logging.getLogger(__name__)


async def deep_research(
    ticker: str,
    user_risk_profile: str = "moderate",
    horizon_days: int = 5,
) -> dict[str, Any]:
    """
    Run a comprehensive deep-dive analysis on a stock.

    Gathers:
    - Full OHLCV (1 year daily + 30 days intraday)
    - All news in last 90 days + sentiment
    - Fundamental data
    - Sector comparison
    - Full prediction pipeline
    - Investment suggestion with position sizing

    Returns:
        Deep research result dict matching the DeepResearchResponse schema
    """
    logger.info("Starting deep research for %s", ticker)
    result: dict[str, Any] = {"ticker": ticker, "status": "processing"}

    try:
        # ── 1. Company Overview ──
        stock_info = await fetch_stock_info(ticker)
        result["company_overview"] = {
            "name": stock_info.get("name", ticker),
            "sector": stock_info.get("sector"),
            "industry": stock_info.get("industry"),
            "market_cap": stock_info.get("market_cap"),
            "description": f"{stock_info.get('name', ticker)} operates in the {stock_info.get('industry', 'N/A')} industry within the {stock_info.get('sector', 'N/A')} sector.",
        }

        # ── 2. OHLCV Data ──
        df_daily = await fetch_ohlcv(ticker, interval="1d", period="1y")

        # ── 3. Technical Analysis ──
        tech_result = None
        if not df_daily.empty:
            tech_result = technical_analyze(ticker, df_daily)
            result["technical_analysis"] = {
                "trend": tech_result.trend or "SIDEWAYS",
                "support_levels": tech_result.support_levels,
                "resistance_levels": tech_result.resistance_levels,
                "patterns_detected": tech_result.patterns_detected,
                "indicators": {
                    "rsi": tech_result.rsi,
                    "macd": tech_result.macd_crossover or "neutral",
                    "bb_position": tech_result.bb_position,
                    "obv_trend": tech_result.obv_trend,
                    "ema_9": tech_result.ema_9,
                    "ema_21": tech_result.ema_21,
                    "ema_50": tech_result.ema_50,
                    "ema_200": tech_result.ema_200,
                    "atr": tech_result.atr,
                    "composite_score": tech_result.composite_score,
                },
            }

        # ── 4. News Analysis (90 days) ──
        articles = await fetch_and_analyze(ticker)
        news_result = await full_news_analysis(ticker, articles)
        result["news_analysis"] = {
            "sentiment_30d": news_result.sentiment_30d,
            "article_count": news_result.article_count_30d,
            "top_positive": news_result.top_positive,
            "top_negative": news_result.top_negative,
            "key_events": news_result.key_events,
            "sentiment_trend": news_result.sentiment_trend,
        }

        # ── 5. Fundamental Analysis ──
        fundamental_data = {
            "pe_ratio": stock_info.get("pe_ratio"),
            "pb_ratio": stock_info.get("pb_ratio"),
            "roe": stock_info.get("roe"),
            "eps": stock_info.get("eps"),
            "dividend_yield": stock_info.get("dividend_yield"),
            "market_cap": stock_info.get("market_cap"),
        }

        valuation = "fairly_valued"
        pe = fundamental_data.get("pe_ratio")
        if pe:
            if pe < 15:
                valuation = "undervalued"
            elif pe > 35:
                valuation = "overvalued"

        result["fundamental_analysis"] = {
            "valuation": valuation,
            "pe_ratio": pe,
            "pb_ratio": fundamental_data.get("pb_ratio"),
            "roe": fundamental_data.get("roe"),
            "eps": fundamental_data.get("eps"),
            "dividend_yield": fundamental_data.get("dividend_yield"),
        }

        # ── 6. Sector Comparison ──
        result["sector_comparison"] = await _sector_comparison(
            ticker, stock_info.get("sector")
        )

        # ── 7. Prediction ──
        prediction = await generate_prediction(
            ticker=ticker,
            technical_result=tech_result,
            news_analysis=news_result,
            fundamental_data=fundamental_data,
            horizon_days=horizon_days,
        )

        # Compute target price and stop-loss
        current_price = stock_info.get("current_price")
        target_price = None
        stop_loss = None

        if current_price and tech_result:
            if tech_result.resistance_levels:
                target_price = tech_result.resistance_levels[0]
            else:
                # Estimate based on confidence and direction
                move_pct = prediction.confidence * 0.05  # up to 5% move
                if prediction.direction == "UP":
                    target_price = round(current_price * (1 + move_pct), 2)
                elif prediction.direction == "DOWN":
                    target_price = round(current_price * (1 - move_pct), 2)

            if tech_result.support_levels:
                stop_loss = tech_result.support_levels[-1]
            elif current_price:
                stop_loss = round(current_price * 0.95, 2)  # 5% below

        result["prediction"] = {
            "direction": prediction.direction,
            "confidence": prediction.confidence,
            "target_price": target_price,
            "stop_loss": stop_loss,
            "ml_score": prediction.ml_score,
            "technical_score": prediction.technical_score,
            "sentiment_score": prediction.sentiment_score,
            "fundamental_score": prediction.fundamental_score,
        }

        # ── 8. Investment Suggestion ──
        result["investment_suggestion"] = _generate_suggestion(
            prediction, user_risk_profile, current_price, target_price, stop_loss
        )

        result["status"] = "completed"
        logger.info("Deep research completed for %s", ticker)

    except Exception as e:
        logger.error("Deep research failed for %s: %s", ticker, e, exc_info=True)
        result["status"] = "failed"
        result["error"] = str(e)

    return result


async def _sector_comparison(
    ticker: str, sector: str | None
) -> dict[str, Any]:
    """Compare ticker against sector peers."""
    # Simplified — in production this would query DB for peer rankings
    return {
        "sector": sector or "Unknown",
        "sector_rank": 1,  # placeholder
        "peers": [],
        "relative_strength": 1.0,
    }


def _generate_suggestion(
    prediction,
    risk_profile: str,
    current_price: float | None,
    target_price: float | None,
    stop_loss: float | None,
) -> dict[str, Any]:
    """Generate position sizing advice based on risk profile."""
    # Action determination
    if prediction.direction == "UP" and prediction.confidence > 0.6:
        action = "BUY"
    elif prediction.direction == "DOWN" and prediction.confidence > 0.6:
        action = "SELL"
    elif prediction.direction == "UP" and prediction.confidence > 0.4:
        action = "WATCH"
    else:
        action = "HOLD"

    # Position sizing by risk profile
    sizing = {
        "conservative": "1–2% of portfolio",
        "moderate": "2–3% of portfolio",
        "aggressive": "3–5% of portfolio",
    }.get(risk_profile, "2–3% of portfolio")

    # Time horizon
    if prediction.horizon_days <= 5:
        horizon_text = "1–2 weeks"
    elif prediction.horizon_days <= 15:
        horizon_text = "2–4 weeks"
    else:
        horizon_text = "1–3 months"

    # Rationale
    factors_str = ", ".join(f.get("name", "") for f in prediction.key_factors[:3])
    rationale = (
        f"{prediction.ticker} signals {prediction.direction.lower()} movement with "
        f"{prediction.confidence:.0%} confidence. Key drivers: {factors_str}. "
    )
    if target_price and current_price:
        upside = ((target_price - current_price) / current_price) * 100
        rationale += f"Estimated {'upside' if upside > 0 else 'downside'}: {abs(upside):.1f}%."

    return {
        "action": action,
        "rationale": rationale,
        "position_sizing": sizing,
        "time_horizon": horizon_text,
    }
