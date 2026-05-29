"""
Quantra — Server-Sent Events (SSE) helpers.
"""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import AsyncGenerator
from typing import Any

from sse_starlette.sse import EventSourceResponse

logger = logging.getLogger(__name__)

# In-memory broadcast channels (per-topic subscriber lists)
_subscribers: dict[str, list[asyncio.Queue]] = {}


def _get_topic_subs(topic: str) -> list[asyncio.Queue]:
    if topic not in _subscribers:
        _subscribers[topic] = []
    return _subscribers[topic]


async def subscribe(topic: str) -> AsyncGenerator[dict[str, str], None]:
    """
    Subscribe to an SSE topic.

    Yields formatted SSE event dicts as they arrive.
    """
    queue: asyncio.Queue = asyncio.Queue(maxsize=100)
    subs = _get_topic_subs(topic)
    subs.append(queue)
    logger.debug("SSE subscriber added to topic=%s (total=%d)", topic, len(subs))

    try:
        while True:
            data = await queue.get()
            yield data
    except asyncio.CancelledError:
        pass
    finally:
        subs.remove(queue)
        logger.debug("SSE subscriber removed from topic=%s (total=%d)", topic, len(subs))


async def broadcast(topic: str, event: str, data: dict[str, Any]) -> None:
    """
    Broadcast an event to all subscribers of a topic.

    Drops messages for slow subscribers to prevent backpressure.
    """
    subs = _get_topic_subs(topic)
    if not subs:
        return

    message = {
        "event": event,
        "data": json.dumps(data),
    }

    dead: list[asyncio.Queue] = []
    for queue in subs:
        try:
            queue.put_nowait(message)
        except asyncio.QueueFull:
            dead.append(queue)
            logger.warning("Dropping SSE subscriber on topic=%s (queue full)", topic)

    for q in dead:
        subs.remove(q)


def create_sse_response(topic: str) -> EventSourceResponse:
    """
    Create an SSE EventSourceResponse for a given topic.

    Usage in a FastAPI route::

        @router.get("/signals/live")
        async def live_signals():
            return create_sse_response("signals")
    """
    return EventSourceResponse(subscribe(topic))


# ── Convenience Broadcast Helpers ─────────────────────────────


async def broadcast_price_update(ticker: str, price: float, change_pct: float) -> None:
    await broadcast(
        "signals",
        "price_update",
        {"ticker": ticker, "price": price, "change_pct": change_pct},
    )


async def broadcast_signal(
    ticker: str, direction: str, confidence: float, summary: str
) -> None:
    await broadcast(
        "signals",
        "signal",
        {
            "ticker": ticker,
            "direction": direction,
            "confidence": confidence,
            "summary": summary,
        },
    )


async def broadcast_alert_triggered(
    user_id: str, alert_id: str, ticker: str, message: str
) -> None:
    await broadcast(
        f"user:{user_id}",
        "alert_triggered",
        {"alert_id": alert_id, "ticker": ticker, "message": message},
    )
