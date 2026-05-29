"""
Quantra — Market data service.

Fetches OHLCV data from yfinance / Alpha Vantage with fallback chain.
"""

from __future__ import annotations

import logging
from datetime import datetime

import pandas as pd

logger = logging.getLogger(__name__)


async def fetch_ohlcv(
    ticker: str,
    interval: str = "1d",
    period: str | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
) -> pd.DataFrame:
    """
    Fetch OHLCV data for a ticker.

    Uses yfinance as primary source, with Alpha Vantage as fallback.
    Returns a pandas DataFrame with columns: Open, High, Low, Close, Volume.
    """
    import yfinance as yf

    try:
        ticker_obj = yf.Ticker(ticker)

        kwargs = {"interval": interval, "progress": False}
        if period:
            kwargs["period"] = period
        elif start and end:
            kwargs["start"] = start.strftime("%Y-%m-%d")
            kwargs["end"] = end.strftime("%Y-%m-%d")
        else:
            kwargs["period"] = "1y"  # default to 1 year

        data = ticker_obj.history(**kwargs)

        if data.empty:
            logger.warning("No data from yfinance for %s — trying Alpha Vantage", ticker)
            return await _fetch_alpha_vantage(ticker, interval)

        return data

    except Exception as e:
        logger.error("yfinance error for %s: %s", ticker, e)
        return await _fetch_alpha_vantage(ticker, interval)


async def _fetch_alpha_vantage(ticker: str, interval: str = "1d") -> pd.DataFrame:
    """Fallback data source: Alpha Vantage API."""
    from app.config import get_settings

    settings = get_settings()
    if not settings.ALPHA_VANTAGE_API_KEY:
        logger.warning("Alpha Vantage API key not configured")
        return pd.DataFrame()

    try:
        import httpx

        function = "TIME_SERIES_DAILY" if interval in ("1d", "daily") else "TIME_SERIES_INTRADAY"
        params = {
            "function": function,
            "symbol": ticker,
            "apikey": settings.ALPHA_VANTAGE_API_KEY,
            "outputsize": "full",
            "datatype": "json",
        }
        if function == "TIME_SERIES_INTRADAY":
            params["interval"] = interval

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get("https://www.alphavantage.co/query", params=params)
            resp.raise_for_status()
            data = resp.json()

        # Parse Alpha Vantage response
        time_series_key = [k for k in data if "Time Series" in k]
        if not time_series_key:
            return pd.DataFrame()

        ts = data[time_series_key[0]]
        rows = []
        for date_str, values in ts.items():
            rows.append(
                {
                    "Date": pd.Timestamp(date_str),
                    "Open": float(values.get("1. open", 0)),
                    "High": float(values.get("2. high", 0)),
                    "Low": float(values.get("3. low", 0)),
                    "Close": float(values.get("4. close", 0)),
                    "Volume": int(float(values.get("5. volume", 0))),
                }
            )

        df = pd.DataFrame(rows)
        df.set_index("Date", inplace=True)
        df.sort_index(inplace=True)
        return df

    except Exception as e:
        logger.error("Alpha Vantage error for %s: %s", ticker, e)
        return pd.DataFrame()


async def fetch_stock_info(ticker: str) -> dict:
    """Fetch stock metadata from yfinance."""
    import yfinance as yf

    try:
        ticker_obj = yf.Ticker(ticker)
        info = ticker_obj.info
        return {
            "ticker": ticker,
            "name": info.get("shortName") or info.get("longName", ticker),
            "exchange": info.get("exchange"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "pb_ratio": info.get("priceToBook"),
            "roe": info.get("returnOnEquity"),
            "eps": info.get("trailingEps"),
            "dividend_yield": info.get("dividendYield"),
            "high_52w": info.get("fiftyTwoWeekHigh"),
            "low_52w": info.get("fiftyTwoWeekLow"),
            "current_price": info.get("currentPrice") or info.get("regularMarketPrice"),
        }
    except Exception as e:
        logger.error("Error fetching stock info for %s: %s", ticker, e)
        return {"ticker": ticker, "name": ticker}


async def search_stocks(query: str, limit: int = 20) -> list[dict]:
    """Fuzzy search for stocks by name or ticker."""
    from sqlalchemy import or_, select
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    from sqlalchemy.orm import sessionmaker

    from app.config import get_settings
    from app.models.stock_meta import StockMeta

    settings = get_settings()
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        pattern = f"%{query.upper()}%"
        result = await session.execute(
            select(StockMeta)
            .where(
                or_(
                    StockMeta.ticker.ilike(pattern),
                    StockMeta.name.ilike(pattern),
                )
            )
            .limit(limit)
        )
        stocks = result.scalars().all()
        await engine.dispose()
        return [
            {
                "ticker": s.ticker,
                "name": s.name,
                "exchange": s.exchange,
                "sector": s.sector,
            }
            for s in stocks
        ]
