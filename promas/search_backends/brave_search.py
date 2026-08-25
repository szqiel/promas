"""
Brave Search API Backend (Primary / Recommended)
Official, ToS-compliant, high-speed JSON web search API.
Requires BRAVE_API_KEY environment variable.
"""

import os
from typing import List, Optional

import httpx
from loguru import logger
from playwright.async_api import Page

from promas.search_backends.base import BaseSearchBackend


class BraveSearchBackend(BaseSearchBackend):
    """
    Official Brave Search API Backend.
    Stable, fast, and requires no browser stealth evasion.
    """

    name: str = "brave_api"
    is_experimental: bool = False
    requires_api_key: bool = True

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("BRAVE_API_KEY")

    def is_available(self) -> bool:
        return bool(self.api_key)

    async def search(
        self,
        query: str,
        site_filter: Optional[str] = None,
        page: Optional[Page] = None
    ) -> List[str]:
        if not self.is_available():
            logger.debug("BraveSearchBackend skipped: BRAVE_API_KEY not configured")
            return []

        search_query = query if not site_filter else f"site:{site_filter} {query}"
        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": self.api_key or ""
        }
        params: dict[str, str | int] = {"q": f"{search_query} buy", "count": 6}

        try:
            logger.info(f"[Brave API] Querying: '{search_query}'...")
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://api.search.brave.com/res/v1/web/search",
                    headers=headers,
                    params=params,
                    timeout=10.0
                )
                if resp.status_code == 200:
                    data = resp.json()
                    web_results = data.get("web", {}).get("results", [])
                    urls = [item["url"] for item in web_results if "url" in item]
                    logger.debug(f"[Brave API] Found {len(urls)} candidate URLs")
                    return urls
                else:
                    logger.warning(f"[Brave API] Request failed with status {resp.status_code}: {resp.text[:100]}")
        except Exception as e:
            logger.warning(f"[Brave API] Search exception: {e}")

        return []
