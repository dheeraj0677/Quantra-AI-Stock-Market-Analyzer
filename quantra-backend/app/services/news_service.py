"""Quantra — News service."""

from __future__ import annotations

import logging

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.news_article import NewsArticle

logger = logging.getLogger(__name__)


async def get_news_feed(db: AsyncSession, page: int = 1, page_size: int = 20) -> dict:
    """Get global news feed (paginated)."""
    offset = (page - 1) * page_size
    result = await db.execute(
        select(NewsArticle).order_by(desc(NewsArticle.scraped_at)).offset(offset).limit(page_size)
    )
    articles = result.scalars().all()
    return {"articles": articles, "total": len(articles), "page": page, "page_size": page_size}


async def get_ticker_news(db: AsyncSession, ticker: str, page: int = 1, page_size: int = 20) -> dict:
    """Get news for a specific ticker."""
    offset = (page - 1) * page_size
    result = await db.execute(
        select(NewsArticle).where(NewsArticle.ticker == ticker)
        .order_by(desc(NewsArticle.scraped_at)).offset(offset).limit(page_size)
    )
    articles = result.scalars().all()
    return {"articles": articles, "total": len(articles), "page": page, "page_size": page_size}


async def get_article(db: AsyncSession, article_id: str) -> NewsArticle | None:
    """Get single article by ID."""
    result = await db.execute(select(NewsArticle).where(NewsArticle.id == article_id))
    return result.scalar_one_or_none()
