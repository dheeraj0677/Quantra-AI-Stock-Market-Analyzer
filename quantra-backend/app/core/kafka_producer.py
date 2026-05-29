"""
Quantra — Async Kafka producer for publishing events.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from app.config import get_settings

logger = logging.getLogger(__name__)

_producer = None


async def get_kafka_producer():
    """Return (or create) the singleton async Kafka producer."""
    global _producer
    if _producer is not None:
        return _producer

    try:
        from aiokafka import AIOKafkaProducer

        settings = get_settings()
        _producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BROKER,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8") if k else None,
            acks="all",
            retry_backoff_ms=500,
            max_request_size=1_048_576,
        )
        await _producer.start()
        logger.info("Kafka producer connected to %s", settings.KAFKA_BROKER)
    except Exception as e:
        logger.warning("Kafka producer unavailable: %s — events will be dropped", e)
        _producer = None

    return _producer


async def close_kafka_producer() -> None:
    """Shutdown hook — flush and close the Kafka producer."""
    global _producer
    if _producer is not None:
        await _producer.stop()
        _producer = None
        logger.info("Kafka producer closed")


async def publish_event(
    topic: str,
    value: dict[str, Any],
    key: str | None = None,
) -> None:
    """
    Publish an event to a Kafka topic.

    Silently drops the event if Kafka is not available (graceful degradation).
    """
    producer = await get_kafka_producer()
    if producer is None:
        logger.debug("Kafka unavailable — dropping event on topic=%s", topic)
        return

    try:
        await producer.send_and_wait(topic, value=value, key=key)
        logger.debug("Published event to %s key=%s", topic, key)
    except Exception as e:
        logger.error("Failed to publish to %s: %s", topic, e)


async def publish_price_tick(ticker: str, price_data: dict[str, Any]) -> None:
    """Convenience — publish a price tick event."""
    await publish_event("PRICE_TICK", price_data, key=ticker)


async def publish_news_event(ticker: str, news_data: dict[str, Any]) -> None:
    """Convenience — publish a news event (triggers cache invalidation)."""
    await publish_event("NEWS_EVENT", news_data, key=ticker)


async def publish_signal(ticker: str, signal_data: dict[str, Any]) -> None:
    """Convenience — publish a trading signal event."""
    await publish_event("SIGNAL", signal_data, key=ticker)
