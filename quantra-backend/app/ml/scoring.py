"""
Quantra — Batch scoring for all tracked tickers.
"""

from __future__ import annotations

import logging

from app.ml.pipeline import run_pipeline

logger = logging.getLogger(__name__)


def batch_score(
    ticker_data: dict[str, dict],
) -> list[dict]:
    """
    Score all tickers in batch.

    Args:
        ticker_data: Dict mapping ticker → {ohlcv_df, articles, stock_meta}

    Returns:
        List of {ticker, ml_score, direction, direction_confidence}
    """
    results = []

    for ticker, data in ticker_data.items():
        try:
            result = run_pipeline(
                ohlcv_df=data.get("ohlcv_df"),
                articles=data.get("articles"),
                stock_meta=data.get("stock_meta"),
            )
            result["ticker"] = ticker
            results.append(result)
            logger.debug("Scored %s: ml_score=%.1f direction=%s", ticker, result["ml_score"], result["direction"])

        except Exception as e:
            logger.error("Scoring failed for %s: %s", ticker, e)
            results.append({
                "ticker": ticker,
                "ml_score": 50.0,
                "direction": "SIDEWAYS",
                "direction_confidence": 0.4,
            })

    logger.info("Batch scoring complete: %d tickers", len(results))
    return results
