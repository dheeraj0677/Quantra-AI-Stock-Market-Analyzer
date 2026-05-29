"""
Quantra — NSE India corporate announcements scraper.
"""

from __future__ import annotations

import logging
from datetime import datetime

import httpx

from app.scrapers.base_scraper import BaseScraper, ScrapedArticle

logger = logging.getLogger(__name__)


class NSEIndiaScraper(BaseScraper):
    SOURCE_NAME = "NSE India"
    BASE_URL = "https://www.nseindia.com"
    ANNOUNCEMENTS_URL = "https://www.nseindia.com/api/corporate-announcements"
    RATE_LIMIT_SECONDS = 3.0  # NSE is aggressive with rate limiting

    def _get_headers(self) -> dict[str, str]:
        headers = super()._get_headers()
        headers.update(
            {
                "Referer": "https://www.nseindia.com/companies-listing/corporate-filings-announcements",
                "Accept": "application/json",
            }
        )
        return headers

    async def scrape(self, ticker: str | None = None) -> list[ScrapedArticle]:
        """Scrape NSE corporate announcements for a specific ticker."""
        articles: list[ScrapedArticle] = []

        try:
            async with httpx.AsyncClient() as client:
                # NSE requires a session cookie — first hit the main page
                await self._rate_limited_get(self.BASE_URL, client)

                params = {"index": "equities", "from_date": "", "to_date": ""}
                if ticker:
                    params["symbol"] = ticker.upper()

                response = await self._rate_limited_get(
                    self.ANNOUNCEMENTS_URL, client, params=params
                )
                data = response.json()

                for item in data[:30]:
                    try:
                        headline = item.get("desc", "").strip()
                        if not headline or len(headline) < 10:
                            continue

                        published_at = None
                        if item.get("an_dt"):
                            try:
                                published_at = datetime.strptime(
                                    item["an_dt"], "%d-%b-%Y %H:%M:%S"
                                )
                            except ValueError:
                                pass

                        symbol = item.get("symbol", ticker)
                        attachment_url = item.get("attchmntFile")
                        url = (
                            f"{self.BASE_URL}/api/corporate-announcements?symbol={symbol}"
                            if not attachment_url
                            else f"https://archives.nseindia.com/corporate/ann/{attachment_url}"
                        )

                        articles.append(
                            ScrapedArticle(
                                headline=headline,
                                summary=item.get("desc", "")[:500],
                                url=url,
                                source=self.SOURCE_NAME,
                                published_at=published_at,
                                ticker=symbol,
                            )
                        )
                    except Exception as e:
                        logger.debug("Error parsing NSE announcement: %s", e)
                        continue

        except Exception as e:
            logger.error("NSE India scrape error: %s", e)

        logger.info("NSE India: scraped %d announcements for %s", len(articles), ticker)
        return articles

    async def scrape_feed(self) -> list[ScrapedArticle]:
        """Scrape latest corporate announcements (no ticker filter)."""
        return await self.scrape(ticker=None)
