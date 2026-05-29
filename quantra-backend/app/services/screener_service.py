"""Quantra — Screener service (filter DSL → SQL)."""

from __future__ import annotations

import hashlib
import json
import logging
from typing import Any

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis_client import get_screener_cache, set_screener_cache
from app.models.stock_meta import StockMeta
from app.schemas.screener import ScreenerRequest

logger = logging.getLogger(__name__)

# Field → DB column mapping
FIELD_MAP = {
    "pe": "pe_ratio", "pb": "pb_ratio", "roe": "roe", "eps": "eps",
    "dividend_yield": "dividend_yield", "market_cap": "market_cap",
    "sector": "sector", "industry": "industry", "exchange": "exchange",
    "high_52w": "high_52w", "low_52w": "low_52w",
}

SORT_MAP = {
    "ml_score": "pe_ratio",  # fallback — ML score comes from Redis
    "pe": "pe_ratio", "market_cap": "market_cap", "roe": "roe",
}

PRESETS = [
    {"name": "undervalued", "description": "Low PE, high ROE stocks", "filters": [
        {"field": "pe", "op": "lte", "value": 20},
        {"field": "roe", "op": "gte", "value": 0.15},
    ]},
    {"name": "momentum", "description": "High ML score, bullish direction", "filters": [
        {"field": "ml_score", "op": "gte", "value": 70},
    ]},
    {"name": "high_sentiment", "description": "Stocks with positive news sentiment", "filters": [
        {"field": "sentiment", "op": "gte", "value": 0.3},
    ]},
]


async def run_screener(request: ScreenerRequest, db: AsyncSession) -> dict[str, Any]:
    """Execute screener query with filter DSL."""
    # Check cache
    cache_hash = hashlib.md5(json.dumps(request.model_dump(), sort_keys=True, default=str).encode()).hexdigest()
    cached = await get_screener_cache(cache_hash)
    if cached:
        return cached

    # Build query
    query = select(StockMeta)
    conditions = []

    for f in request.filters:
        col_name = FIELD_MAP.get(f.field)
        if not col_name:
            continue  # Skip unknown fields (ml_score, sentiment handled separately)

        column = getattr(StockMeta, col_name, None)
        if column is None:
            continue

        if f.op == "eq":
            conditions.append(column == f.value)
        elif f.op == "neq":
            conditions.append(column != f.value)
        elif f.op == "gt":
            conditions.append(column > f.value)
        elif f.op == "gte":
            conditions.append(column >= f.value)
        elif f.op == "lt":
            conditions.append(column < f.value)
        elif f.op == "lte":
            conditions.append(column <= f.value)
        elif f.op == "between" and isinstance(f.value, list) and len(f.value) == 2:
            conditions.append(column.between(f.value[0], f.value[1]))
        elif f.op == "in" and isinstance(f.value, list):
            conditions.append(column.in_(f.value))

    if conditions:
        query = query.where(and_(*conditions))

    # Sort
    sort_col_name = SORT_MAP.get(request.sort_by, "pe_ratio")
    sort_col = getattr(StockMeta, sort_col_name, StockMeta.pe_ratio)
    if request.sort_order == "desc":
        query = query.order_by(sort_col.desc().nullslast())
    else:
        query = query.order_by(sort_col.asc().nullsfirst())

    query = query.limit(request.limit)

    result = await db.execute(query)
    stocks = result.scalars().all()

    response = {
        "results": [
            {
                "ticker": s.ticker, "name": s.name, "sector": s.sector,
                "pe_ratio": float(s.pe_ratio) if s.pe_ratio else None,
                "current_price": None,  # Would come from Redis
                "ml_score": None, "sentiment": None, "direction": None,
            }
            for s in stocks
        ],
        "total": len(stocks),
        "filters_applied": len(request.filters),
    }

    await set_screener_cache(cache_hash, response)
    return response
