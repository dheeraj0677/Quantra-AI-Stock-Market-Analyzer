"""
Quantra — News Analyzer.

Fetches news from all scrapers, deduplicates, runs sentiment analysis,
computes rolling sentiment scores, and classifies impact levels.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

from app.scrapers.base_scraper import ScrapedArticle
from app.scrapers.economictimes import EconomicTimesScraper
from app.scrapers.moneycontrol import MoneycontrolScraper
from app.scrapers.rss_feeds import RSSFeedScraper

logger = logging.getLogger(__name__)

# High-impact keywords
HIGH_IMPACT_KEYWORDS = {
    "earnings", "profit", "revenue", "acquisition", "merger", "deal",
    "buyback", "dividend", "split", "rbi", "fed", "interest rate",
    "quarterly results", "annual results", "guidance", "outlook",
    "downgrade", "upgrade", "target price", "rating",
}

# High-credibility sources
HIGH_CREDIBILITY_SOURCES = {
    "Economic Times", "Moneycontrol", "Reuters", "Bloomberg",
    "CNBC", "NSE India", "BSE India", "MarketWatch",
}


@dataclass
class SentimentResult:
    """Sentiment analysis result for a single article."""

    headline: str
    sentiment: str  # POSITIVE | NEGATIVE | NEUTRAL
    score: float  # -1.0 to +1.0
    confidence: float  # 0.0 to 1.0


@dataclass
class NewsAnalysis:
    """Complete news analysis for a ticker."""

    ticker: str
    articles: list[dict] = field(default_factory=list)
    sentiment_7d: float = 0.0
    sentiment_30d: float = 0.0
    article_count_7d: int = 0
    article_count_30d: int = 0
    sentiment_trend: str = "STABLE"  # IMPROVING | DECLINING | STABLE
    top_positive: list[dict] = field(default_factory=list)
    top_negative: list[dict] = field(default_factory=list)
    key_events: list[str] = field(default_factory=list)


async def analyze_sentiment(text: str) -> SentimentResult:
    """
    Run sentiment analysis on text using FinBERT.

    Falls back to a simple keyword-based approach if model is not loaded.
    """
    try:
        from app.ml.models.news_sentiment import get_sentiment_model

        model = get_sentiment_model()
        if model is not None:
            result = model.predict(text)
            return SentimentResult(
                headline=text,
                sentiment=result["label"],
                score=result["score"],
                confidence=result["confidence"],
            )
    except Exception as e:
        logger.debug("FinBERT not available, using keyword fallback: %s", e)

    # Keyword-based fallback
    return _keyword_sentiment(text)


def _keyword_sentiment(text: str) -> SentimentResult:
    """Simple keyword-based sentiment analysis as fallback."""
    text_lower = text.lower()

    positive_words = {
        "surge", "rally", "gain", "rise", "profit", "beat", "outperform",
        "bullish", "upgrade", "growth", "strong", "record", "high",
        "positive", "optimistic", "boost", "recover", "upside",
    }
    negative_words = {
        "fall", "drop", "decline", "loss", "crash", "bearish", "downgrade",
        "weak", "miss", "cut", "concern", "risk", "sell", "plunge",
        "negative", "pessimistic", "downturn", "slump", "warning",
    }

    pos_count = sum(1 for w in positive_words if w in text_lower)
    neg_count = sum(1 for w in negative_words if w in text_lower)
    total = pos_count + neg_count

    if total == 0:
        return SentimentResult(headline=text, sentiment="NEUTRAL", score=0.0, confidence=0.3)

    score = (pos_count - neg_count) / total
    if score > 0.2:
        label = "POSITIVE"
    elif score < -0.2:
        label = "NEGATIVE"
    else:
        label = "NEUTRAL"

    return SentimentResult(headline=text, sentiment=label, score=score, confidence=0.5)


def classify_impact(article: ScrapedArticle, sentiment_score: float) -> str:
    """Classify news impact as HIGH, MEDIUM, or LOW."""
    text = f"{article.headline} {article.summary or ''}".lower()
    source = (article.source or "").strip()

    # HIGH: credible source + high-impact keyword + strong sentiment
    is_credible = source in HIGH_CREDIBILITY_SOURCES
    has_impact_keyword = any(kw in text for kw in HIGH_IMPACT_KEYWORDS)
    strong_sentiment = abs(sentiment_score) > 0.5

    if is_credible and has_impact_keyword:
        return "HIGH"
    if has_impact_keyword and strong_sentiment:
        return "HIGH"
    if is_credible or has_impact_keyword:
        return "MEDIUM"
    return "LOW"


async def fetch_and_analyze(
    ticker: str,
    existing_urls: set | None = None,
) -> list[dict]:
    """
    Fetch articles from all scrapers, deduplicate, and run sentiment analysis.

    Returns list of processed article dicts ready for DB insertion.
    """
    existing_urls = existing_urls or set()
    all_articles: list[ScrapedArticle] = []

    # Gather from all scrapers
    scrapers = [
        MoneycontrolScraper(),
        EconomicTimesScraper(),
        RSSFeedScraper(),
    ]

    for scraper in scrapers:
        try:
            articles = await scraper.scrape(ticker)
            all_articles.extend(articles)
        except Exception as e:
            logger.error("Scraper %s failed for %s: %s", scraper.SOURCE_NAME, ticker, e)

    # Deduplicate by URL hash
    seen_hashes: set = set()
    unique_articles: list[ScrapedArticle] = []
    for article in all_articles:
        url_hash = article.url_hash
        if url_hash not in seen_hashes and article.url not in existing_urls:
            seen_hashes.add(url_hash)
            unique_articles.append(article)

    logger.info(
        "Ticker %s: %d articles fetched, %d unique after dedup",
        ticker,
        len(all_articles),
        len(unique_articles),
    )

    # Run sentiment analysis
    processed = []
    for article in unique_articles:
        text = f"{article.headline}. {article.summary or ''}"
        sentiment = await analyze_sentiment(text)
        impact = classify_impact(article, sentiment.score)

        processed.append(
            {
                "ticker": ticker,
                "headline": article.headline,
                "summary": article.summary,
                "source": article.source,
                "url": article.url,
                "published_at": article.published_at,
                "sentiment": sentiment.sentiment,
                "sentiment_score": sentiment.score,
                "impact_level": impact,
            }
        )

    return processed


def compute_rolling_sentiment(
    articles: list[dict],
    days: int = 30,
) -> float:
    """
    Compute a weighted rolling sentiment score.

    Recent articles and high-impact articles are weighted more.
    """
    if not articles:
        return 0.0

    now = datetime.now(UTC)
    cutoff = now - timedelta(days=days)

    total_weight = 0.0
    weighted_sum = 0.0

    for article in articles:
        published = article.get("published_at")
        if published and published.tzinfo is None:
            published = published.replace(tzinfo=UTC)

        if published and published < cutoff:
            continue

        score = article.get("sentiment_score", 0.0)
        impact = article.get("impact_level", "LOW")

        # Impact weight
        impact_weight = {"HIGH": 3.0, "MEDIUM": 2.0, "LOW": 1.0}.get(impact, 1.0)

        # Recency weight (more recent = higher weight)
        if published:
            days_ago = max((now - published).days, 1)
            recency_weight = 1.0 / (1 + 0.1 * days_ago)
        else:
            recency_weight = 0.5

        weight = impact_weight * recency_weight
        weighted_sum += score * weight
        total_weight += weight

    if total_weight == 0:
        return 0.0

    return round(weighted_sum / total_weight, 4)


async def full_news_analysis(ticker: str, articles: list[dict]) -> NewsAnalysis:
    """Build a complete news analysis summary for a ticker."""
    analysis = NewsAnalysis(ticker=ticker)
    now = datetime.now(UTC)

    # Filter by time windows
    articles_7d = []
    articles_30d = []

    for a in articles:
        pub = a.get("published_at")
        if pub:
            if pub.tzinfo is None:
                pub = pub.replace(tzinfo=UTC)
            if pub >= now - timedelta(days=7):
                articles_7d.append(a)
            if pub >= now - timedelta(days=30):
                articles_30d.append(a)
        else:
            articles_30d.append(a)

    analysis.article_count_7d = len(articles_7d)
    analysis.article_count_30d = len(articles_30d)
    analysis.sentiment_7d = compute_rolling_sentiment(articles_7d, days=7)
    analysis.sentiment_30d = compute_rolling_sentiment(articles_30d, days=30)

    # Sentiment trend
    if analysis.sentiment_7d > analysis.sentiment_30d + 0.1:
        analysis.sentiment_trend = "IMPROVING"
    elif analysis.sentiment_7d < analysis.sentiment_30d - 0.1:
        analysis.sentiment_trend = "DECLINING"
    else:
        analysis.sentiment_trend = "STABLE"

    # Top positive/negative
    sorted_by_score = sorted(articles_30d, key=lambda x: x.get("sentiment_score", 0))
    analysis.top_negative = [
        {"headline": a["headline"], "score": a.get("sentiment_score"), "source": a.get("source")}
        for a in sorted_by_score[:3]
        if a.get("sentiment_score", 0) < 0
    ]
    analysis.top_positive = [
        {"headline": a["headline"], "score": a.get("sentiment_score"), "source": a.get("source")}
        for a in reversed(sorted_by_score[-3:])
        if a.get("sentiment_score", 0) > 0
    ]

    # Key events (high-impact articles)
    analysis.key_events = [
        a["headline"]
        for a in articles_30d
        if a.get("impact_level") == "HIGH"
    ][:10]

    return analysis
