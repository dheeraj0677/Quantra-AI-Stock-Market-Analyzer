"""Quantra — Backtest service."""
from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.backtest import BacktestRun

logger = logging.getLogger(__name__)

async def create_backtest(db: AsyncSession, user_id: UUID, strategy: dict) -> BacktestRun:
    run = BacktestRun(user_id=user_id, strategy=strategy, status="queued")
    db.add(run)
    await db.flush()
    return run

async def get_backtest(db: AsyncSession, backtest_id: UUID) -> BacktestRun | None:
    result = await db.execute(select(BacktestRun).where(BacktestRun.id == backtest_id))
    return result.scalar_one_or_none()

async def get_user_backtests(db: AsyncSession, user_id: UUID) -> list:
    result = await db.execute(
        select(BacktestRun).where(BacktestRun.user_id == user_id).order_by(desc(BacktestRun.started_at)).limit(20)
    )
    return list(result.scalars().all())
