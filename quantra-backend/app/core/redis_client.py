"""
Quantra — Async Redis client with connection pooling & key helpers.
"""

from __future__ import annotations

import json
import logging
from typing import Any

import redis.asyncio as aioredis

from app.config import get_settings

logger = logging.getLogger(__name__)

_pool: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    """Return (or create) the global Redis connection pool."""
    global _pool
    if _pool is None:
        settings = get_settings()
        _pool = aioredis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            max_connections=50,
        )
    return _pool


async def close_redis() -> None:
    """Shutdown hook — close the Redis pool."""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


# ── Key Helpers ────────────────────────────────────────────────
# All Redis key patterns as specified in the design doc.


async def set_price(ticker: str, price: float) -> None:
    """Cache latest price with 5-second TTL."""
    r = await get_redis()
    await r.set(f"price:{ticker}", str(price), ex=5)


async def get_price(ticker: str) -> float | None:
    """Retrieve cached price."""
    r = await get_redis()
    val = await r.get(f"price:{ticker}")
    return float(val) if val else None


async def set_ml_score(ticker: str, score: float) -> None:
    """Cache ML quality score (0–100) with 1-hour TTL."""
    r = await get_redis()
    await r.set(f"score:{ticker}", str(score), ex=3600)


async def get_ml_score(ticker: str) -> float | None:
    r = await get_redis()
    val = await r.get(f"score:{ticker}")
    return float(val) if val else None


async def set_prediction(ticker: str, days: int, data: dict[str, Any]) -> None:
    """Cache prediction JSON with 6-hour TTL."""
    r = await get_redis()
    await r.set(f"prediction:{ticker}:{days}", json.dumps(data), ex=21600)


async def get_prediction(ticker: str, days: int) -> dict[str, Any] | None:
    r = await get_redis()
    val = await r.get(f"prediction:{ticker}:{days}")
    return json.loads(val) if val else None


async def set_sentiment(ticker: str, score: float) -> None:
    """Cache rolling sentiment score with 30-min TTL."""
    r = await get_redis()
    await r.set(f"sentiment:{ticker}", str(score), ex=1800)


async def get_sentiment(ticker: str) -> float | None:
    r = await get_redis()
    val = await r.get(f"sentiment:{ticker}")
    return float(val) if val else None


async def set_screener_cache(cache_hash: str, data: dict[str, Any]) -> None:
    """Cache screener results with 30-second TTL."""
    r = await get_redis()
    await r.set(f"screener:cache:{cache_hash}", json.dumps(data), ex=30)


async def get_screener_cache(cache_hash: str) -> dict[str, Any] | None:
    r = await get_redis()
    val = await r.get(f"screener:cache:{cache_hash}")
    return json.loads(val) if val else None


async def set_news_latest(ticker: str, headlines: list[dict]) -> None:
    """Cache last 10 headlines with 15-min TTL."""
    r = await get_redis()
    await r.set(f"news:latest:{ticker}", json.dumps(headlines), ex=900)


async def get_news_latest(ticker: str) -> list[dict] | None:
    r = await get_redis()
    val = await r.get(f"news:latest:{ticker}")
    return json.loads(val) if val else None


async def set_session(user_id: str, refresh_token: str) -> None:
    """Store refresh token with 7-day TTL."""
    r = await get_redis()
    await r.set(f"session:{user_id}", refresh_token, ex=604800)


async def get_session(user_id: str) -> str | None:
    r = await get_redis()
    return await r.get(f"session:{user_id}")


async def delete_session(user_id: str) -> None:
    r = await get_redis()
    await r.delete(f"session:{user_id}")


async def set_suggestions(user_id: str, data: list[dict]) -> None:
    """Cache today's suggestions with 24-hour TTL."""
    r = await get_redis()
    await r.set(f"suggestion:{user_id}", json.dumps(data), ex=86400)


async def get_suggestions(user_id: str) -> list[dict] | None:
    r = await get_redis()
    val = await r.get(f"suggestion:{user_id}")
    return json.loads(val) if val else None


async def invalidate_prediction_cache(ticker: str) -> None:
    """Bust prediction cache for a ticker (triggered by new news)."""
    r = await get_redis()
    async for key in r.scan_iter(f"prediction:{ticker}:*"):
        await r.delete(key)
    logger.info("Invalidated prediction cache for %s", ticker)
