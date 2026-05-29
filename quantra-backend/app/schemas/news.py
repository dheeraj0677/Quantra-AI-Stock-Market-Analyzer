"""
Pydantic v2 schemas — News.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class NewsArticleResponse(BaseModel):
    id: str
    ticker: str | None = None
    headline: str
    summary: str | None = None
    source: str | None = None
    url: str | None = None
    published_at: datetime | None = None
    sentiment: str | None = None  # POSITIVE | NEGATIVE | NEUTRAL
    sentiment_score: float | None = None  # -1.0 to +1.0
    impact_level: str | None = None  # HIGH | MEDIUM | LOW

    model_config = {"from_attributes": True}


class NewsFeedResponse(BaseModel):
    articles: list[NewsArticleResponse]
    total: int
    page: int
    page_size: int


class NewsSentimentDetail(BaseModel):
    article_id: str
    headline: str
    raw_sentiment: str
    raw_score: float
    adjusted_score: float  # weighted by source credibility
    source_weight: float
    key_phrases: list[str] | None = None
    entities_detected: list[str] | None = None


class TickerSentimentSummary(BaseModel):
    ticker: str
    sentiment_7d: float
    sentiment_30d: float
    article_count_7d: int
    article_count_30d: int
    sentiment_trend: str  # IMPROVING | DECLINING | STABLE
