"""Quantra — Market API endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.models.stock_meta import StockMeta

router = APIRouter()


@router.get("/summary")
async def market_summary():
    """NIFTY/SENSEX/indices summary."""
    import yfinance as yf
    indices = {"NIFTY_50": "^NSEI", "SENSEX": "^BSESN", "BANK_NIFTY": "^NSEBANK"}
    summary = {}
    for name, symbol in indices.items():
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            summary[name] = {
                "price": info.get("regularMarketPrice"),
                "change": info.get("regularMarketChange"),
                "change_pct": info.get("regularMarketChangePercent"),
            }
        except Exception:
            summary[name] = {"price": None, "change": None, "change_pct": None}
    return summary


@router.get("/movers")
async def market_movers(db: AsyncSession = Depends(get_db)):
    """Top gainers, losers, most active."""
    # Simplified — in production would use real-time data
    return {"gainers": [], "losers": [], "most_active": []}


@router.get("/sectors")
async def sector_performance(db: AsyncSession = Depends(get_db)):
    """Sector-wise performance heatmap data."""
    from sqlalchemy import func
    result = await db.execute(
        select(StockMeta.sector, func.count(StockMeta.ticker), func.avg(StockMeta.pe_ratio))
        .where(StockMeta.sector.isnot(None))
        .group_by(StockMeta.sector)
    )
    sectors = result.all()
    return [{"sector": s[0], "stock_count": s[1], "avg_pe": float(s[2]) if s[2] else None} for s in sectors]


@router.get("/sentiment")
async def market_sentiment():
    """Overall market sentiment score (news-based)."""
    return {"sentiment_score": 0.0, "label": "NEUTRAL", "article_count": 0}
