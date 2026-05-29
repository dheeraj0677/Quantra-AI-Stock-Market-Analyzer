"""
Pydantic v2 schemas — Screener.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ScreenerFilter(BaseModel):
    field: str  # pe, rsi, ml_score, sentiment, direction, sector, ...
    op: str  # eq, neq, gt, gte, lt, lte, between, in
    value: Any  # single value, list, or [min, max] for between


class ScreenerRequest(BaseModel):
    filters: list[ScreenerFilter]
    sort_by: str = Field(default="ml_score")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")
    limit: int = Field(default=30, ge=1, le=200)


class ScreenerResultItem(BaseModel):
    ticker: str
    name: str
    sector: str | None = None
    current_price: float | None = None
    pe_ratio: float | None = None
    rsi: float | None = None
    ml_score: float | None = None
    sentiment: float | None = None
    direction: str | None = None
    confidence: float | None = None


class ScreenerResponse(BaseModel):
    results: list[ScreenerResultItem]
    total: int
    filters_applied: int


class FilterFieldInfo(BaseModel):
    field: str
    label: str
    type: str  # numeric, text, enum
    min_value: float | None = None
    max_value: float | None = None
    options: list[str] | None = None


class PresetScreen(BaseModel):
    name: str
    description: str
    filters: list[ScreenerFilter]
