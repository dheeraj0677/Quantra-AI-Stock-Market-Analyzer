"""
Quantra — FastAPI application entrypoint.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from app.config import get_settings
from app.core.kafka_producer import close_kafka_producer, get_kafka_producer
from app.core.redis_client import close_redis, get_redis
from app.db.session import dispose_engine

logger = logging.getLogger("quantra")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle hooks."""
    settings = get_settings()
    logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
    logger.info("🚀 Quantra backend starting (env=%s)", settings.APP_ENV)

    # Warm connections
    try:
        await get_redis()
        logger.info("✅ Redis connected")
    except Exception as e:
        logger.warning("⚠️  Redis not available: %s", e)

    try:
        await get_kafka_producer()
        logger.info("✅ Kafka producer connected")
    except Exception as e:
        logger.warning("⚠️  Kafka not available: %s", e)

    yield

    # Shutdown
    logger.info("🛑 Quantra backend shutting down")
    await close_redis()
    await close_kafka_producer()
    await dispose_engine()


app = FastAPI(
    title="Quantra — AI Stock Market Analyzer",
    description="AI-powered stock analysis, prediction, and personalized investment suggestions",
    version="0.1.0",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────
from app.api.v1 import api_router  # noqa: E402

app.include_router(api_router)


# ── Health Check ──────────────────────────────────────────────


@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "service": "quantra-backend",
        "version": "0.1.0",
    }


@app.get("/", tags=["System"])
async def root():
    return {
        "message": "Welcome to Quantra — AI Stock Market Analyzer API",
        "docs": "/docs",
        "health": "/health",
    }
