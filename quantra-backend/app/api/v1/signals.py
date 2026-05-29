"""Quantra — SSE Signals API."""
from __future__ import annotations

from fastapi import APIRouter

from app.core.sse import create_sse_response

router = APIRouter()


@router.get("/live")
async def live_signals():
    """SSE stream (price updates, signal triggers, P&L)."""
    return create_sse_response("signals")


@router.get("/history")
async def signal_history():
    """Signal history."""
    return []
