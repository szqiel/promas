"""
Brave Search Backend (Optional API-key based)
"""

import os
from typing import List, Optional
import urllib.parse
from playwright.async_api import Page
from promas.search_backends.base import BaseSearchBackend

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False


class BraveSearchBackend(BaseSearchBackend):
    """Brave Search API Backend."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("BRAVE_API_KEY")

    async def search(self, page: Page, query: str, site_filter: Optional[str] = None) -> List[str]:
        if not self.api_key or not HAS_HTTPX:
            return []

        search_query = query if not site_filter else f"site:{site_filter} {query}"
        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": self.api_key
        }
        params = {"q": search_query, "count": 5}
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get("https://api.search.brave.com/res/v1/web/search", headers=headers, params=params, timeout=10.0)
                if resp.status_code == 200:
                    data = resp.json()
                    web_results = data.get("web", {}).get("results", [])
                    return [item["url"] for item in web_results if "url" in item]
        except Exception:
            pass
        return []
