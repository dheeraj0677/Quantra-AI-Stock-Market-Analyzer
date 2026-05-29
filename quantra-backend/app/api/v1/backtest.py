"""Quantra — Backtest API endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.backtest import BacktestRequest
from app.services.backtest_service import create_backtest, get_backtest, get_user_backtests

router = APIRouter()


@router.post("/run", status_code=status.HTTP_202_ACCEPTED)
async def run_backtest(payload: BacktestRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Queue async backtest (202 Accepted)."""
    run = await create_backtest(db, user.id, payload.strategy)
    # Queue Celery task
    from app.workers.tasks.run_backtest import run as run_task
    run_task.delay(str(run.id), payload.strategy, payload.tickers, payload.initial_capital)
    return {"id": str(run.id), "status": "queued"}


@router.get("/{job_id}")
async def get_status(job_id: str, db: AsyncSession = Depends(get_db)):
    """Poll status + results."""
    run = await get_backtest(db, job_id)
    if not run:
        return {"error": "Backtest not found"}
    return {"id": str(run.id), "status": run.status, "result": run.result, "started_at": run.started_at, "completed_at": run.completed_at}


@router.get("/history")
async def history(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """User's past backtest runs."""
    runs = await get_user_backtests(db, user.id)
    return [{"id": str(r.id), "status": r.status, "started_at": r.started_at} for r in runs]
