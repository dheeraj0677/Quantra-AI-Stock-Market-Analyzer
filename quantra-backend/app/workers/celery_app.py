"""
Quantra — Celery application init.
"""

from __future__ import annotations

from celery import Celery

from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "quantra",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.workers.tasks.ingest_prices",
        "app.workers.tasks.ingest_news",
        "app.workers.tasks.run_ml_score",
        "app.workers.tasks.run_predictions",
        "app.workers.tasks.check_alerts",
        "app.workers.tasks.run_backtest",
        "app.workers.tasks.generate_suggestions",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    result_expires=86400,  # 24 hours
    task_soft_time_limit=300,  # 5 minutes
    task_time_limit=600,  # 10 minutes hard limit
)

# Import beat schedule
from app.workers.beats import CELERYBEAT_SCHEDULE  # noqa: E402

celery_app.conf.beat_schedule = CELERYBEAT_SCHEDULE
