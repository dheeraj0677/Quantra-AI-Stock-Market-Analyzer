"""Quantra — Screener API endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import RateLimiter, get_db
from app.schemas.screener import ScreenerRequest
from app.services.screener_service import PRESETS, run_screener

router = APIRouter()


@router.post("/run", dependencies=[Depends(RateLimiter(times=20, seconds=60))])
async def run(request: ScreenerRequest, db: AsyncSession = Depends(get_db)):
    """Run dynamic filter DSL screener."""
    return await run_screener(request, db)


@router.get("/filters")
async def get_filters():
    """Available filter fields + valid ranges."""
    return [
        {"field": "pe", "label": "PE Ratio", "type": "numeric", "min_value": 0, "max_value": 200},
        {"field": "pb", "label": "PB Ratio", "type": "numeric", "min_value": 0, "max_value": 50},
        {"field": "roe", "label": "ROE", "type": "numeric", "min_value": -1, "max_value": 1},
        {"field": "rsi", "label": "RSI (14)", "type": "numeric", "min_value": 0, "max_value": 100},
        {"field": "ml_score", "label": "ML Score", "type": "numeric", "min_value": 0, "max_value": 100},
        {"field": "sentiment", "label": "Sentiment", "type": "numeric", "min_value": -1, "max_value": 1},
        {"field": "direction", "label": "Direction", "type": "enum", "options": ["UP", "DOWN", "SIDEWAYS"]},
        {"field": "sector", "label": "Sector", "type": "enum", "options": ["IT", "Finance", "Energy", "Healthcare", "FMCG", "Auto"]},
        {"field": "market_cap", "label": "Market Cap", "type": "numeric"},
        {"field": "dividend_yield", "label": "Dividend Yield", "type": "numeric", "min_value": 0, "max_value": 0.2},
    ]


@router.get("/presets")
async def get_presets():
    """Preset screens (undervalued, momentum, high-sentiment)."""
    return PRESETS
