"""
Quantra — Celery Beat periodic schedule configuration.
"""

from __future__ import annotations

from celery.schedules import crontab

CELERYBEAT_SCHEDULE = {
    # ── Price Ingestion — every 5 min during market hours ──
    "ingest-prices-every-5min": {
        "task": "app.workers.tasks.ingest_prices.run",
        "schedule": crontab(minute="*/5"),
        "options": {"queue": "data"},
    },
    # ── News Ingestion — every 15 min ──
    "ingest-news-every-15min": {
        "task": "app.workers.tasks.ingest_news.run",
        "schedule": crontab(minute="*/15"),
        "options": {"queue": "data"},
    },
    # ── Alert Checks — every 5 min ──
    "check-alerts-every-5min": {
        "task": "app.workers.tasks.check_alerts.run",
        "schedule": crontab(minute="*/5"),
        "options": {"queue": "alerts"},
    },
    # ── Nightly ML Scoring — 12:30 AM IST ──
    "nightly-ml-score": {
        "task": "app.workers.tasks.run_ml_score.run",
        "schedule": crontab(hour=0, minute=30),
        "options": {"queue": "ml"},
    },
    # ── Nightly Predictions — 1:00 AM IST ──
    "nightly-predictions": {
        "task": "app.workers.tasks.run_predictions.run",
        "schedule": crontab(hour=1, minute=0),
        "options": {"queue": "ml"},
    },
    # ── Daily Suggestions — 7:00 AM IST (before market open) ──
    "daily-suggestions": {
        "task": "app.workers.tasks.generate_suggestions.run",
        "schedule": crontab(hour=7, minute=0),
        "options": {"queue": "suggestions"},
    },
}
