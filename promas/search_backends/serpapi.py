"""
SerpAPI Google Search Backend (Primary / Alternative)
Official, ToS-compliant Google Search JSON API.
Requires SERPAPI_API_KEY environment variable.
"""

import os
from typing import List, Optional

import httpx
from loguru import logger
from playwright.async_api import Page

from promas.search_backends.base import BaseSearchBackend


class SerpApiSearchBackend(BaseSearchBackend):
    """
    Official SerpAPI Google Search Backend.
    Stable, fast, and requires no browser stealth evasion.
    """

    name: str = "serpapi"
    is_experimental: bool = False
    requires_api_key: bool = True

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("SERPAPI_API_KEY")

    def is_available(self) -> bool:
        return bool(self.api_key)

    async def search(
        self,
        query: str,
        site_filter: Optional[str] = None,
        page: Optional[Page] = None
    ) -> List[str]:
        if not self.is_available():
            logger.debug("SerpApiSearchBackend skipped: SERPAPI_API_KEY not configured")
            return []

        search_query = query if not site_filter else f"site:{site_filter} {query}"
        params: dict[str, str | int] = {
            "engine": "google",
            "q": f"{search_query} buy",
            "api_key": self.api_key or "",
            "num": 6,
        }

        try:
            logger.info(f"[SerpAPI] Querying Google for: '{search_query}'...")
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://serpapi.com/search",
                    params=params,
                    timeout=10.0
                )
                if resp.status_code == 200:
                    data = resp.json()
                    organic = data.get("organic_results", [])
                    urls = [item["link"] for item in organic if "link" in item]
                    logger.debug(f"[SerpAPI] Found {len(urls)} candidate URLs")
                    return urls
                else:
                    logger.warning(f"[SerpAPI] Request failed with status {resp.status_code}: {resp.text[:100]}")
        except Exception as e:
            logger.warning(f"[SerpAPI] Search exception: {e}")

        return []
