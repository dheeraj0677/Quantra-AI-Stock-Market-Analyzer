"""Quantra — Stock API endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.analysis.technical_analyzer import analyze as technical_analyze
from app.core.redis_client import get_ml_score, get_price
from app.dependencies import get_db
from app.models.stock_meta import StockMeta
from app.services.market_data_service import fetch_ohlcv, fetch_stock_info

router = APIRouter()


@router.get("/search")
async def search(q: str = Query(..., min_length=1), limit: int = Query(20, le=50), db: AsyncSession = Depends(get_db)):
    """Fuzzy search stocks by name or ticker."""
    pattern = f"%{q.upper()}%"
    result = await db.execute(
        select(StockMeta).where(or_(StockMeta.ticker.ilike(pattern), StockMeta.name.ilike(pattern))).limit(limit)
    )
    stocks = result.scalars().all()
    return [{"ticker": s.ticker, "name": s.name, "exchange": s.exchange, "sector": s.sector} for s in stocks]


@router.get("/{ticker}")
async def stock_profile(ticker: str, db: AsyncSession = Depends(get_db)):
    """Full stock profile with current price and ML score."""
    result = await db.execute(select(StockMeta).where(StockMeta.ticker == ticker.upper()))
    stock = result.scalar_one_or_none()

    if stock is None:
        info = await fetch_stock_info(ticker)
        return {**info, "current_price": await get_price(ticker), "ml_score": await get_ml_score(ticker)}

    return {
        "ticker": stock.ticker, "name": stock.name, "exchange": stock.exchange,
        "sector": stock.sector, "industry": stock.industry, "market_cap": float(stock.market_cap) if stock.market_cap else None,
        "pe_ratio": float(stock.pe_ratio) if stock.pe_ratio else None,
        "pb_ratio": float(stock.pb_ratio) if stock.pb_ratio else None,
        "roe": float(stock.roe) if stock.roe else None,
        "eps": float(stock.eps) if stock.eps else None,
        "current_price": await get_price(ticker), "ml_score": await get_ml_score(ticker),
    }


@router.get("/{ticker}/ohlcv")
async def get_ohlcv(ticker: str, interval: str = Query("1d"), period: str = Query("6mo")):
    """Get OHLCV bars."""
    df = await fetch_ohlcv(ticker.upper(), interval=interval, period=period)
    if df.empty:
        return {"ticker": ticker, "interval": interval, "bars": [], "count": 0}
    bars = [
        {"time": idx.isoformat(), "open": float(r.Open), "high": float(r.High), "low": float(r.Low), "close": float(r.Close), "volume": int(r.Volume), "interval": interval}
        for idx, r in df.iterrows()
    ]
    return {"ticker": ticker, "interval": interval, "bars": bars, "count": len(bars)}


@router.get("/{ticker}/technicals")
async def get_technicals(ticker: str):
    """Compute all technical indicators."""
    df = await fetch_ohlcv(ticker.upper(), interval="1d", period="1y")
    if df.empty:
        return {"error": "No data available"}
    result = technical_analyze(ticker.upper(), df)
    return {
        "ticker": result.ticker, "rsi": result.rsi, "rsi_signal": result.rsi_signal,
        "macd": result.macd, "macd_crossover": result.macd_crossover,
        "bb_position": result.bb_position, "atr": result.atr,
        "obv_trend": result.obv_trend, "volume_spike": result.volume_spike,
        "trend": result.trend, "patterns_detected": result.patterns_detected,
        "support_levels": result.support_levels, "resistance_levels": result.resistance_levels,
        "composite_score": result.composite_score,
    }


@router.get("/{ticker}/fundamentals")
async def get_fundamentals(ticker: str):
    """Get fundamental data."""
    return await fetch_stock_info(ticker.upper())


@router.get("/{ticker}/news")
async def get_stock_news(ticker: str, page: int = 1, page_size: int = 20, db: AsyncSession = Depends(get_db)):
    """Get recent news with sentiment per article."""
    from app.services.news_service import get_ticker_news
    return await get_ticker_news(db, ticker.upper(), page, page_size)


@router.get("/{ticker}/similar")
async def get_similar(ticker: str, db: AsyncSession = Depends(get_db)):
    """Similar stocks in same sector."""
    result = await db.execute(select(StockMeta).where(StockMeta.ticker == ticker.upper()))
    stock = result.scalar_one_or_none()
    if not stock or not stock.sector:
        return []
    peers = await db.execute(
        select(StockMeta).where(StockMeta.sector == stock.sector, StockMeta.ticker != ticker.upper()).limit(10)
    )
    return [{"ticker": s.ticker, "name": s.name, "sector": s.sector} for s in peers.scalars().all()]
