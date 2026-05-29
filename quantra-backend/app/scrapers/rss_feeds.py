"""
Quantra — Generic RSS/Atom feed parser.

Supports Reuters, Bloomberg, and any standard RSS/Atom feed.
"""

from __future__ import annotations

import logging
from email.utils import parsedate_to_datetime

import feedparser
import httpx

from app.scrapers.base_scraper import BaseScraper, ScrapedArticle

logger = logging.getLogger(__name__)

# Default financial news RSS feeds
DEFAULT_FEEDS = {
    "Reuters Business": "https://feeds.reuters.com/reuters/businessNews",
    "Reuters Markets": "https://feeds.reuters.com/reuters/marketsNews",
    "Yahoo Finance": "https://finance.yahoo.com/news/rssindex",
    "CNBC": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "MarketWatch": "https://feeds.marketwatch.com/marketwatch/topstories/",
    "Investing.com": "https://www.investing.com/rss/news.rss",
}


class RSSFeedScraper(BaseScraper):
    SOURCE_NAME = "RSS Feeds"
    RATE_LIMIT_SECONDS = 1.5

    def __init__(
        self,
        feeds: dict[str, str] | None = None,
        rate_limit: float | None = None,
    ):
        super().__init__(rate_limit)
        self.feeds = feeds or DEFAULT_FEEDS

    async def scrape(self, ticker: str | None = None) -> list[ScrapedArticle]:
        """Scrape all configured RSS feeds, optionally filtering by ticker."""
        all_articles = await self.scrape_feed()

        if ticker:
            ticker_upper = ticker.upper()
            return [
                a
                for a in all_articles
                if ticker_upper in (a.headline or "").upper()
                or ticker_upper in (a.summary or "").upper()
            ]

        return all_articles

    async def scrape_feed(self) -> list[ScrapedArticle]:
        """Parse all configured RSS feeds."""
        articles: list[ScrapedArticle] = []

        async with httpx.AsyncClient(timeout=15) as client:
            for source_name, feed_url in self.feeds.items():
                try:
                    response = await self._rate_limited_get(feed_url, client)
                    feed = feedparser.parse(response.text)

                    for entry in feed.entries[:15]:
                        try:
                            headline = entry.get("title", "").strip()
                            if not headline or len(headline) < 10:
                                continue

                            summary = entry.get("summary") or entry.get("description", "")
                            if summary:
                                from bs4 import BeautifulSoup
                                summary = BeautifulSoup(summary, "lxml").get_text(strip=True)

                            published_at = None
                            for date_field in ("published", "updated", "created"):
                                if entry.get(date_field):
                                    try:
                                        published_at = parsedate_to_datetime(
                                            entry[date_field]
                                        )
                                        break
                                    except Exception:
                                        continue

                            articles.append(
                                ScrapedArticle(
                                    headline=headline,
                                    summary=summary[:500] if summary else None,
                                    url=entry.get("link"),
                                    source=source_name,
                                    published_at=published_at,
                                )
                            )
                        except Exception as e:
                            logger.debug("Error parsing RSS entry from %s: %s", source_name, e)
                            continue

                    logger.debug("%s: parsed %d entries", source_name, len(feed.entries))

                except Exception as e:
                    logger.warning("RSS feed error for %s: %s", source_name, e)

        logger.info("RSS Feeds: scraped %d articles total from %d feeds", len(articles), len(self.feeds))
        return articles
