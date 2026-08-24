"""
SerpAPI Search Backend (Optional API-key based)
"""

import os
from typing import List, Optional

from playwright.async_api import Page

from promas.search_backends.base import BaseSearchBackend

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False


class SerpApiSearchBackend(BaseSearchBackend):
    """SerpAPI Google Search Backend."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("SERPAPI_API_KEY")

    async def search(self, page: Page, query: str, site_filter: Optional[str] = None) -> List[str]:
        if not self.api_key or not HAS_HTTPX:
            return []

        search_query = query if not site_filter else f"site:{site_filter} {query}"
        params: dict[str, str | int] = {
            "engine": "google",
            "q": search_query,
            "api_key": self.api_key,
            "num": 5,
        }
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get("https://serpapi.com/search", params=params, timeout=10.0)
                if resp.status_code == 200:
                    data = resp.json()
                    organic = data.get("organic_results", [])
                    return [item["link"] for item in organic if "link" in item]
        except Exception:
            pass
        return []
