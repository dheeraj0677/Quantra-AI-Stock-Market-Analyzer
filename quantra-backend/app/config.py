"""
Quantra Backend — Application Configuration

All settings are driven by environment variables (loaded via .env).
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Central configuration loaded from environment / .env file."""

    # ── Application ──────────────────────────────────────
    APP_ENV: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: str = "http://localhost:3000"

    # ── Database ──────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://quantra:secret@localhost:5432/quantra"
    DATABASE_URL_SYNC: str = "postgresql://quantra:secret@localhost:5432/quantra"

    # ── Redis ─────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── Kafka ─────────────────────────────────────────────
    KAFKA_BROKER: str = "localhost:9092"

    # ── JWT / Auth ────────────────────────────────────────
    JWT_SECRET_KEY: str = "change-me-to-a-64-char-random-string"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── Market Data APIs ──────────────────────────────────
    ALPHA_VANTAGE_API_KEY: str | None = None
    TWELVE_DATA_API_KEY: str | None = None

    # ── MinIO (S3-compatible) ─────────────────────────────
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET_MODELS: str = "quantra-models"
    MINIO_SECURE: bool = False

    # ── Notifications ─────────────────────────────────────
    FCM_SERVER_KEY: str | None = None
    WEBHOOK_SECRET: str | None = None

    # ── Scraper Settings ──────────────────────────────────
    NEWS_SCRAPE_INTERVAL_MINUTES: int = 15
    SCRAPER_RATE_LIMIT_SECONDS: float = 2.0

    # ── Market Hours (IST) ────────────────────────────────
    MARKET_HOURS_START: str = "09:15"
    MARKET_HOURS_END: str = "15:30"
    MARKET_TIMEZONE: str = "Asia/Kolkata"

    # ── Computed Properties ───────────────────────────────

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper = v.upper()
        if upper not in allowed:
            raise ValueError(f"LOG_LEVEL must be one of {allowed}")
        return upper

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore",
    }


@lru_cache
def get_settings() -> Settings:
    """Singleton settings instance (cached after first call)."""
    return Settings()
