"""
Quantra — Base scraper with rate limiting, retries, and user-agent rotation.
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

import httpx

logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
]


@dataclass
class ScrapedArticle:
    """Normalized article from any scraper."""

    headline: str
    summary: str | None = None
    url: str | None = None
    source: str | None = None
    published_at: datetime | None = None
    ticker: str | None = None
    raw_html: str | None = None

    @property
    def url_hash(self) -> str:
        """SHA-256 hash of URL for deduplication."""
        if self.url:
            return hashlib.sha256(self.url.encode()).hexdigest()
        return hashlib.sha256(self.headline.encode()).hexdigest()


class BaseScraper(ABC):
    """
    Abstract base class for all news scrapers.

    Provides:
    - Rate limiting (configurable delay between requests)
    - Retry logic with exponential backoff
    - User-agent rotation
    - Common HTTP client
    """

    SOURCE_NAME: str = "unknown"
    RATE_LIMIT_SECONDS: float = 2.0
    MAX_RETRIES: int = 3

    def __init__(self, rate_limit: float | None = None):
        self._rate_limit = rate_limit or self.RATE_LIMIT_SECONDS
        self._last_request_time: float = 0

    def _get_headers(self) -> dict[str, str]:
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }

    async def _rate_limited_get(
        self,
        url: str,
        client: httpx.AsyncClient,
        **kwargs,
    ) -> httpx.Response:
        """Make a rate-limited GET request with retries."""
        # Enforce rate limit
        await asyncio.sleep(self._rate_limit)

        for attempt in range(self.MAX_RETRIES):
            try:
                response = await client.get(
                    url,
                    headers=self._get_headers(),
                    follow_redirects=True,
                    timeout=15,
                    **kwargs,
                )
                response.raise_for_status()
                return response
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    wait = (2**attempt) * 5
                    logger.warning(
                        "%s: Rate limited — waiting %ds (attempt %d/%d)",
                        self.SOURCE_NAME,
                        wait,
                        attempt + 1,
                        self.MAX_RETRIES,
                    )
                    await asyncio.sleep(wait)
                elif e.response.status_code >= 500:
                    wait = 2**attempt
                    logger.warning(
                        "%s: Server error %d — retrying in %ds",
                        self.SOURCE_NAME,
                        e.response.status_code,
                        wait,
                    )
                    await asyncio.sleep(wait)
                else:
                    raise
            except (httpx.ConnectError, httpx.ReadTimeout) as e:
                wait = 2**attempt
                logger.warning(
                    "%s: Connection error — retrying in %ds: %s",
                    self.SOURCE_NAME,
                    wait,
                    e,
                )
                await asyncio.sleep(wait)

        raise httpx.HTTPError(f"{self.SOURCE_NAME}: Max retries exceeded for {url}")

    @abstractmethod
    async def scrape(self, ticker: str | None = None) -> list[ScrapedArticle]:
        """Scrape articles, optionally filtered by ticker."""
        ...

    @abstractmethod
    async def scrape_feed(self) -> list[ScrapedArticle]:
        """Scrape the general news feed (not ticker-specific)."""
        ...
