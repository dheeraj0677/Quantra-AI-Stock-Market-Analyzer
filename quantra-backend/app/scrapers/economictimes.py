"""
Quantra — Economic Times Markets RSS feed scraper.
"""

from __future__ import annotations

import logging
from email.utils import parsedate_to_datetime

import feedparser
import httpx

from app.scrapers.base_scraper import BaseScraper, ScrapedArticle

logger = logging.getLogger(__name__)


class EconomicTimesScraper(BaseScraper):
    SOURCE_NAME = "Economic Times"
    RSS_FEEDS = [
        "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
        "https://economictimes.indiatimes.com/markets/stocks/rssfeeds/2146842.cms",
        "https://economictimes.indiatimes.com/markets/commodities/rssfeeds/5618088.cms",
    ]

    async def scrape(self, ticker: str | None = None) -> list[ScrapedArticle]:
        """Scrape ET Markets RSS feeds, optionally filtering by ticker."""
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
        """Parse all ET Markets RSS feeds."""
        articles: list[ScrapedArticle] = []

        for feed_url in self.RSS_FEEDS:
            try:
                async with httpx.AsyncClient() as client:
                    response = await self._rate_limited_get(feed_url, client)
                    feed = feedparser.parse(response.text)

                    for entry in feed.entries[:20]:
                        try:
                            headline = entry.get("title", "").strip()
                            if not headline or len(headline) < 10:
                                continue

                            summary = entry.get("summary") or entry.get("description", "")
                            # Strip HTML tags from summary
                            if summary:
                                from bs4 import BeautifulSoup

                                summary = BeautifulSoup(summary, "lxml").get_text(strip=True)

                            # Parse publication date
                            published_at = None
                            if entry.get("published"):
                                try:
                                    published_at = parsedate_to_datetime(entry.published)
                                except Exception:
                                    pass

                            articles.append(
                                ScrapedArticle(
                                    headline=headline,
                                    summary=summary[:500] if summary else None,
                                    url=entry.get("link"),
                                    source=self.SOURCE_NAME,
                                    published_at=published_at,
                                )
                            )
                        except Exception as e:
                            logger.debug("Error parsing ET entry: %s", e)
                            continue

            except Exception as e:
                logger.error("ET feed scrape error for %s: %s", feed_url, e)

        logger.info("Economic Times: scraped %d articles", len(articles))
        return articles
