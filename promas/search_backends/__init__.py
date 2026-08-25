"""
Search Backends Package
Orchestrates primary API search backends (Brave / SerpAPI) and experimental browser stealth discovery.
"""

from typing import List, Optional

from loguru import logger
from playwright.async_api import Page

from promas.search_backends.base import BaseSearchBackend
from promas.search_backends.bing_browser import BingBrowserSearchBackend, decode_bing_redirect
from promas.search_backends.brave_search import BraveSearchBackend
from promas.search_backends.serpapi import SerpApiSearchBackend


def get_search_backend() -> BaseSearchBackend:
    """
    Returns the primary search backend based on available API credentials.
    Prioritizes official APIs (Brave -> SerpAPI) over experimental browser scraping.
    """
    brave = BraveSearchBackend()
    if brave.is_available():
        logger.debug("Using Brave Search API as primary discovery backend")
        return brave

    serpapi = SerpApiSearchBackend()
    if serpapi.is_available():
        logger.debug("Using SerpAPI as primary discovery backend")
        return serpapi

    logger.debug("No search API keys detected (BRAVE_API_KEY/SERPAPI_API_KEY). Using experimental browser fallback.")
    return BingBrowserSearchBackend()


async def search_candidate_urls(
    query: str,
    site_filter: Optional[str] = None,
    page: Optional[Page] = None
) -> List[str]:
    """
    Executes product search across the configured primary backend, falling back if necessary.
    """
    primary = get_search_backend()
    urls = await primary.search(query, site_filter=site_filter, page=page)

    # If primary API backend returned empty and we have a page instance, attempt experimental browser fallback
    if not urls and primary.requires_api_key and page is not None:
        logger.warning(f"Primary search backend '{primary.name}' returned 0 results. Falling back to browser discovery.")
        fallback = BingBrowserSearchBackend()
        urls = await fallback.search(query, site_filter=site_filter, page=page)

    return urls


__all__ = [
    "BaseSearchBackend",
    "BingBrowserSearchBackend",
    "BraveSearchBackend",
    "SerpApiSearchBackend",
    "decode_bing_redirect",
    "get_search_backend",
    "search_candidate_urls",
]
