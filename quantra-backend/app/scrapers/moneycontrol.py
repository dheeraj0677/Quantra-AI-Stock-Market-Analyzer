"""
Quantra — Moneycontrol news scraper.
"""

from __future__ import annotations

import logging
from datetime import datetime

import httpx
from bs4 import BeautifulSoup

from app.scrapers.base_scraper import BaseScraper, ScrapedArticle

logger = logging.getLogger(__name__)


class MoneycontrolScraper(BaseScraper):
    SOURCE_NAME = "Moneycontrol"
    BASE_URL = "https://www.moneycontrol.com"
    NEWS_URL = "https://www.moneycontrol.com/news/business/markets/"
    STOCK_NEWS_URL = "https://www.moneycontrol.com/news/tags/{ticker}.html"

    async def scrape(self, ticker: str | None = None) -> list[ScrapedArticle]:
        """Scrape Moneycontrol news for a specific ticker."""
        if not ticker:
            return await self.scrape_feed()

        articles: list[ScrapedArticle] = []
        url = self.STOCK_NEWS_URL.format(ticker=ticker.lower())

        try:
            async with httpx.AsyncClient() as client:
                response = await self._rate_limited_get(url, client)
                soup = BeautifulSoup(response.text, "lxml")

                news_items = soup.select("li.clearfix") or soup.select("div.news_listing li")

                for item in news_items[:20]:
                    try:
                        link = item.select_one("a")
                        if not link:
                            continue

                        headline = link.get_text(strip=True)
                        article_url = link.get("href", "")

                        if not headline or len(headline) < 10:
                            continue

                        # Try to extract summary
                        summary_el = item.select_one("p")
                        summary = summary_el.get_text(strip=True) if summary_el else None

                        # Try to extract date
                        date_el = item.select_one("span.date") or item.select_one("span.ago")
                        published_at = None
                        if date_el:
                            try:
                                published_at = datetime.strptime(
                                    date_el.get_text(strip=True), "%B %d, %Y %I:%M %p"
                                )
                            except ValueError:
                                pass

                        articles.append(
                            ScrapedArticle(
                                headline=headline,
                                summary=summary,
                                url=article_url if article_url.startswith("http") else f"{self.BASE_URL}{article_url}",
                                source=self.SOURCE_NAME,
                                published_at=published_at,
                                ticker=ticker,
                            )
                        )
                    except Exception as e:
                        logger.debug("Error parsing MC article: %s", e)
                        continue

        except Exception as e:
            logger.error("Moneycontrol scrape error for %s: %s", ticker, e)

        logger.info("Moneycontrol: scraped %d articles for %s", len(articles), ticker)
        return articles

    async def scrape_feed(self) -> list[ScrapedArticle]:
        """Scrape general market news from Moneycontrol."""
        articles: list[ScrapedArticle] = []

        try:
            async with httpx.AsyncClient() as client:
                response = await self._rate_limited_get(self.NEWS_URL, client)
                soup = BeautifulSoup(response.text, "lxml")

                news_items = soup.select("li.clearfix")[:30]
                for item in news_items:
                    try:
                        link = item.select_one("a")
                        if not link:
                            continue

                        headline = link.get_text(strip=True)
                        article_url = link.get("href", "")

                        if not headline or len(headline) < 10:
                            continue

                        articles.append(
                            ScrapedArticle(
                                headline=headline,
                                url=article_url if article_url.startswith("http") else f"{self.BASE_URL}{article_url}",
                                source=self.SOURCE_NAME,
                            )
                        )
                    except Exception:
                        continue

        except Exception as e:
            logger.error("Moneycontrol feed scrape error: %s", e)

        return articles
