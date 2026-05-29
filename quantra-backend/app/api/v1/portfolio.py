"""Quantra — Portfolio API endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.portfolio import Portfolio, Position
from app.models.user import User
from app.schemas.portfolio import PortfolioCreate, PositionCreate
from app.services.portfolio_service import (
    compute_pnl,
    get_portfolio_with_positions,
    get_user_portfolios,
)

router = APIRouter()


@router.get("")
async def list_portfolios(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    portfolios = await get_user_portfolios(db, user.id)
    return [{"id": str(p.id), "name": p.name, "currency": p.currency, "created_at": p.created_at.isoformat()} for p in portfolios]


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_portfolio(payload: PortfolioCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    portfolio = Portfolio(user_id=user.id, name=payload.name, currency=payload.currency)
    db.add(portfolio)
    await db.flush()
    return {"id": str(portfolio.id), "name": portfolio.name, "currency": portfolio.currency}


@router.get("/{portfolio_id}")
async def get_portfolio(portfolio_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    portfolio = await get_portfolio_with_positions(db, portfolio_id)
    if not portfolio or str(portfolio.user_id) != str(user.id):
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return {
        "id": str(portfolio.id), "name": portfolio.name, "currency": portfolio.currency,
        "positions": [{"id": str(p.id), "ticker": p.ticker, "quantity": float(p.quantity), "avg_price": float(p.avg_price)} for p in (portfolio.positions or [])],
    }


@router.post("/{portfolio_id}/position", status_code=status.HTTP_201_CREATED)
async def add_position(portfolio_id: str, payload: PositionCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    pos = Position(portfolio_id=portfolio_id, ticker=payload.ticker.upper(), quantity=payload.quantity, avg_price=payload.avg_price)
    db.add(pos)
    await db.flush()
    return {"id": str(pos.id), "ticker": pos.ticker, "quantity": float(pos.quantity)}


@router.delete("/{portfolio_id}/position/{pos_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_position(portfolio_id: str, pos_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    from sqlalchemy import delete
    await db.execute(delete(Position).where(Position.id == pos_id, Position.portfolio_id == portfolio_id))


@router.get("/{portfolio_id}/pnl")
async def get_pnl(portfolio_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await compute_pnl(db, portfolio_id)


@router.get("/{portfolio_id}/analysis")
async def portfolio_analysis(portfolio_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return {"portfolio_id": portfolio_id, "diversification_score": 70, "risk_level": "MEDIUM", "suggestions": ["Consider adding international exposure"], "ai_summary": "Your portfolio is moderately diversified."}
