"""
Quantra — BSE India filings scraper.
"""

from __future__ import annotations

import logging
from datetime import datetime

import httpx

from app.scrapers.base_scraper import BaseScraper, ScrapedArticle

logger = logging.getLogger(__name__)


class BSEIndiaScraper(BaseScraper):
    SOURCE_NAME = "BSE India"
    ANNOUNCEMENTS_URL = "https://api.bseindia.com/BseIndiaAPI/api/AnnSubCategoryGetData/w"
    RATE_LIMIT_SECONDS = 3.0

    async def scrape(self, ticker: str | None = None) -> list[ScrapedArticle]:
        """Scrape BSE India corporate filings."""
        articles: list[ScrapedArticle] = []

        try:
            async with httpx.AsyncClient() as client:
                params = {
                    "pageno": "1",
                    "strCat": "-1",
                    "strPrevDate": "",
                    "strScrip": ticker or "",
                    "strSearch": "P",
                    "strToDate": "",
                    "strType": "C",
                }

                headers = self._get_headers()
                headers["Referer"] = "https://www.bseindia.com/corporates/ann.html"
                headers["Accept"] = "application/json"

                response = await client.get(
                    self.ANNOUNCEMENTS_URL,
                    params=params,
                    headers=headers,
                    timeout=15,
                )
                response.raise_for_status()
                data = response.json()

                table = data.get("Table", [])
                for item in table[:30]:
                    try:
                        headline = item.get("NEWSSUB", "").strip()
                        if not headline or len(headline) < 10:
                            continue

                        published_at = None
                        news_dt = item.get("NEWS_DT")
                        if news_dt:
                            try:
                                published_at = datetime.strptime(
                                    news_dt.split("T")[0], "%Y-%m-%d"
                                )
                            except ValueError:
                                pass

                        attachment = item.get("ATTACHMENTNAME", "")
                        url = (
                            f"https://www.bseindia.com/xml-data/corpfiling/AttachHis/{attachment}"
                            if attachment
                            else None
                        )

                        articles.append(
                            ScrapedArticle(
                                headline=headline,
                                summary=item.get("NEWSSUB", "")[:500],
                                url=url,
                                source=self.SOURCE_NAME,
                                published_at=published_at,
                                ticker=item.get("SCRIP_CD") or ticker,
                            )
                        )
                    except Exception as e:
                        logger.debug("Error parsing BSE filing: %s", e)
                        continue

        except Exception as e:
            logger.error("BSE India scrape error: %s", e)

        logger.info("BSE India: scraped %d filings for %s", len(articles), ticker)
        return articles

    async def scrape_feed(self) -> list[ScrapedArticle]:
        """Scrape latest BSE filings (no ticker filter)."""
        return await self.scrape(ticker=None)
