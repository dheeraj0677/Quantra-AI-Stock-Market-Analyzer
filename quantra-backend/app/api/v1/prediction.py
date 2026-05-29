"""Quantra — Prediction API endpoints."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import RateLimiter, get_current_user, get_db
from app.models.prediction import Prediction
from app.models.user import User
from app.services.prediction_service import quick_prediction

router = APIRouter()


@router.get("/{ticker}", dependencies=[Depends(RateLimiter(times=30, seconds=60))])
async def predict_quick(ticker: str, horizon_days: int = 5):
    """Quick prediction (cached, <200ms)."""
    return await quick_prediction(ticker.upper(), horizon_days)


@router.post("/{ticker}/deep", status_code=status.HTTP_202_ACCEPTED)
async def predict_deep(ticker: str, user: User = Depends(get_current_user)):
    """Full deep research (async, ~10-30s). Returns job_id to poll."""

    job_id = str(uuid.uuid4())
    # Queue Celery task (would call deep_researcher.deep_research)
    # For now return job structure
    return {
        "job_id": job_id,
        "ticker": ticker.upper(),
        "status": "queued",
        "estimated_time_seconds": 15,
    }


@router.get("/{ticker}/deep/{job_id}")
async def poll_deep_research(ticker: str, job_id: str):
    """Poll deep research result."""
    # In production: check Celery result backend
    return {"job_id": job_id, "ticker": ticker.upper(), "status": "processing"}


@router.get("/{ticker}/history")
async def prediction_history(ticker: str, db: AsyncSession = Depends(get_db)):
    """Past predictions + accuracy tracking."""
    result = await db.execute(
        select(Prediction).where(Prediction.ticker == ticker.upper())
        .order_by(desc(Prediction.generated_at)).limit(20)
    )
    predictions = result.scalars().all()
    return [
        {
            "id": str(p.id), "ticker": p.ticker, "direction": p.direction,
            "confidence": float(p.confidence), "generated_at": p.generated_at.isoformat(),
        }
        for p in predictions
    ]
