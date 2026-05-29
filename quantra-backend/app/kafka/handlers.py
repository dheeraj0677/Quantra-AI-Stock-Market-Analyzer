"""Quantra — Kafka event handlers."""

from __future__ import annotations

import logging
from typing import Any

from app.core.redis_client import invalidate_prediction_cache, set_price, set_sentiment
from app.core.sse import broadcast_price_update, broadcast_signal
from app.kafka.topics import NEWS_EVENT, PRICE_TICK, SIGNAL

logger = logging.getLogger(__name__)


async def handle_event(topic: str, key: bytes | None, value: dict[str, Any]) -> None:
    """Route Kafka events to appropriate handlers."""
    ticker = key.decode("utf-8") if key else value.get("ticker", "UNKNOWN")

    if topic == PRICE_TICK:
        await _handle_price_tick(ticker, value)
    elif topic == NEWS_EVENT:
        await _handle_news_event(ticker, value)
    elif topic == SIGNAL:
        await _handle_signal(ticker, value)
    else:
        logger.warning("Unknown Kafka topic: %s", topic)


async def _handle_price_tick(ticker: str, data: dict) -> None:
    """Handle price tick — update Redis cache and broadcast SSE."""
    price = data.get("close") or data.get("price")
    if price:
        await set_price(ticker, float(price))
        change_pct = data.get("change_pct", 0.0)
        await broadcast_price_update(ticker, float(price), float(change_pct))


async def _handle_news_event(ticker: str, data: dict) -> None:
    """Handle news event — bust prediction cache and update sentiment."""
    # Invalidate prediction cache for this ticker (new news = stale prediction)
    await invalidate_prediction_cache(ticker)

    # Update sentiment cache if provided
    sentiment_score = data.get("sentiment_score")
    if sentiment_score is not None:
        await set_sentiment(ticker, float(sentiment_score))

    logger.info("News event for %s — cache invalidated", ticker)


async def _handle_signal(ticker: str, data: dict) -> None:
    """Handle trading signal — broadcast to SSE subscribers."""
    await broadcast_signal(
        ticker=ticker,
        direction=data.get("direction", "UNKNOWN"),
        confidence=data.get("confidence", 0.0),
        summary=data.get("summary", ""),
    )
