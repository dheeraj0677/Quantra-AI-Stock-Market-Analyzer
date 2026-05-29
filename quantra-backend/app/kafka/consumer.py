"""Quantra — Kafka consumer loop."""

from __future__ import annotations

import json
import logging

from app.config import get_settings
from app.kafka.handlers import handle_event
from app.kafka.topics import ALL_TOPICS

logger = logging.getLogger(__name__)


async def start_consumer():
    """Start the async Kafka consumer."""
    try:
        from aiokafka import AIOKafkaConsumer
    except ImportError:
        logger.warning("aiokafka not installed — Kafka consumer disabled")
        return

    settings = get_settings()

    consumer = AIOKafkaConsumer(
        *ALL_TOPICS,
        bootstrap_servers=settings.KAFKA_BROKER,
        group_id="quantra-backend",
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset="latest",
    )

    try:
        await consumer.start()
        logger.info("Kafka consumer started on topics: %s", ALL_TOPICS)

        async for msg in consumer:
            try:
                await handle_event(msg.topic, msg.key, msg.value)
            except Exception as e:
                logger.error("Error handling Kafka event: %s", e)

    except Exception as e:
        logger.error("Kafka consumer error: %s", e)
    finally:
        await consumer.stop()
