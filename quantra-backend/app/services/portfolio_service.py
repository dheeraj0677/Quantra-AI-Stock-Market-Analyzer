"""Quantra — Portfolio service."""

from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis_client import get_price
from app.models.portfolio import Portfolio, Position

logger = logging.getLogger(__name__)


async def get_user_portfolios(db: AsyncSession, user_id: UUID) -> list[Portfolio]:
    result = await db.execute(select(Portfolio).where(Portfolio.user_id == user_id))
    return list(result.scalars().all())


async def get_portfolio_with_positions(db: AsyncSession, portfolio_id: UUID) -> Portfolio | None:
    result = await db.execute(select(Portfolio).where(Portfolio.id == portfolio_id))
    portfolio = result.scalar_one_or_none()
    if portfolio:
        pos_result = await db.execute(select(Position).where(Position.portfolio_id == portfolio_id))
        portfolio.positions = list(pos_result.scalars().all())
    return portfolio


async def compute_pnl(db: AsyncSession, portfolio_id: UUID) -> dict:
    """Compute live P&L using current prices from Redis."""
    pos_result = await db.execute(select(Position).where(Position.portfolio_id == portfolio_id))
    positions = pos_result.scalars().all()

    total_invested = 0.0
    current_value = 0.0
    position_details = []

    for pos in positions:
        invested = float(pos.quantity) * float(pos.avg_price)
        total_invested += invested

        current_price = await get_price(pos.ticker)
        if current_price:
            cur_val = float(pos.quantity) * current_price
            pnl = cur_val - invested
            pnl_pct = (pnl / invested * 100) if invested > 0 else 0.0
        else:
            cur_val = invested
            pnl = 0.0
            pnl_pct = 0.0

        current_value += cur_val
        position_details.append({
            "id": str(pos.id), "ticker": pos.ticker,
            "quantity": float(pos.quantity), "avg_price": float(pos.avg_price),
            "current_price": current_price, "pnl": round(pnl, 2),
            "pnl_pct": round(pnl_pct, 2), "opened_at": pos.opened_at.isoformat(),
        })

    total_pnl = current_value - total_invested
    return {
        "portfolio_id": str(portfolio_id),
        "total_invested": round(total_invested, 2),
        "current_value": round(current_value, 2),
        "total_pnl": round(total_pnl, 2),
        "total_pnl_pct": round((total_pnl / total_invested * 100) if total_invested > 0 else 0, 2),
        "positions": position_details,
    }
