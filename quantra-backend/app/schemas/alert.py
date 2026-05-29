"""
Pydantic v2 schemas — Alerts.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class AlertCreate(BaseModel):
    ticker: str | None = None
    condition: dict[str, Any]  # e.g. {"field": "price", "op": "gte", "value": 1500}
    channels: list[str] = ["push"]
    webhook_url: str | None = None


class AlertResponse(BaseModel):
    id: str
    ticker: str | None = None
    condition: dict[str, Any]
    channels: list[str]
    webhook_url: str | None = None
    is_active: bool
    triggered_at: datetime | None = None

    model_config = {"from_attributes": True}


class AlertLogEntry(BaseModel):
    alert_id: str
    ticker: str
    triggered_at: datetime
    condition_met: str
    value_at_trigger: float | None = None
    channel_used: str
