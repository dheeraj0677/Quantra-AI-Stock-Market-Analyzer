"""Quantra — News API endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.services.news_service import get_article, get_news_feed, get_ticker_news

router = APIRouter()


@router.get("/feed")
async def news_feed(page: int = Query(1, ge=1), page_size: int = Query(20, le=50), db: AsyncSession = Depends(get_db)):
    """Global market news feed (paginated)."""
    result = await get_news_feed(db, page, page_size)
    return {
        "articles": [
            {"id": str(a.id), "ticker": a.ticker, "headline": a.headline, "summary": a.summary,
             "source": a.source, "url": a.url, "sentiment": a.sentiment,
             "sentiment_score": float(a.sentiment_score) if a.sentiment_score else None,
             "impact_level": a.impact_level, "published_at": a.published_at.isoformat() if a.published_at else None}
            for a in result["articles"]
        ],
        "total": result["total"], "page": result["page"], "page_size": result["page_size"],
    }


@router.get("/{ticker}")
async def ticker_news(ticker: str, page: int = 1, page_size: int = 20, db: AsyncSession = Depends(get_db)):
    """News for specific ticker (paginated)."""
    result = await get_ticker_news(db, ticker.upper(), page, page_size)
    return {
        "articles": [
            {"id": str(a.id), "headline": a.headline, "source": a.source,
             "sentiment": a.sentiment, "sentiment_score": float(a.sentiment_score) if a.sentiment_score else None,
             "published_at": a.published_at.isoformat() if a.published_at else None}
            for a in result["articles"]
        ],
        "total": result["total"],
    }


@router.get("/{article_id}")
async def single_article(article_id: str, db: AsyncSession = Depends(get_db)):
    """Single article with full sentiment breakdown."""
    article = await get_article(db, article_id)
    if not article:
        return {"error": "Article not found"}
    return {
        "id": str(article.id), "ticker": article.ticker, "headline": article.headline,
        "summary": article.summary, "source": article.source, "url": article.url,
        "sentiment": article.sentiment, "sentiment_score": float(article.sentiment_score) if article.sentiment_score else None,
        "impact_level": article.impact_level,
    }
