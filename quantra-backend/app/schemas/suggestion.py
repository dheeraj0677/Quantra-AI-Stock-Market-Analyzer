"""
Pydantic v2 schemas — Suggestions (AI-personalized).
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class SuggestionResponse(BaseModel):
    id: str
    ticker: str
    action: str  # BUY | WATCH | AVOID
    confidence: float
    reason: str
    ml_score: float | None = None
    current_price: float | None = None
    target_price: float | None = None
    risk_level: str | None = None  # LOW | MEDIUM | HIGH
    expires_at: datetime | None = None
    is_read: bool = False

    model_config = {"from_attributes": True}


class SuggestionListResponse(BaseModel):
    suggestions: list[SuggestionResponse]
    generated_at: datetime | None = None
    user_risk_profile: str | None = None
