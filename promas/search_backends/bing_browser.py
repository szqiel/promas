"""
Bing & DuckDuckGo Browser Stealth Search Backend (Experimental / Best-Effort Fallback)
Used when no API keys (Brave / SerpAPI) are configured or when APIs are unavailable.
"""

import base64
import re
import urllib.parse
from typing import List, Optional

from loguru import logger
from playwright.async_api import Page

from promas.search_backends.base import BaseSearchBackend


def decode_bing_redirect(url: Optional[str]) -> Optional[str]:
    """
    Decodes Bing redirection links (/ck/a?...&u=a1<base64>) to direct destination URLs.
    """
    if not url:
        return None
    if "/ck/a?" in url and "&u=" in url:
        m = re.search(r'[?&]u=a1([a-zA-Z0-9_\-]+)', url)
        if m:
            b64 = m.group(1)
            b64 += "=" * ((4 - len(b64) % 4) % 4)
            try:
                decoded = base64.b64decode(b64.replace("-", "+").replace("_", "/")).decode("utf-8", errors="ignore")
                if decoded.startswith("http"):
                    return decoded
            except Exception:
                pass
    elif url.startswith("http") and "bing.com" not in url:
        return url
    return None


class BingBrowserSearchBackend(BaseSearchBackend):
    """
    Experimental Browser-Based Discovery Backend.
    Uses Playwright Stealth to query Bing and DuckDuckGo for candidate product pages.
    """

    name: str = "browser_stealth (experimental fallback)"
    is_experimental: bool = True
    requires_api_key: bool = False

    def is_available(self) -> bool:
        return True

    async def search(
        self,
        query: str,
        site_filter: Optional[str] = None,
        page: Optional[Page] = None
    ) -> List[str]:
        if page is None:
            logger.warning("[Browser Discovery] Playwright Page instance required for browser search backend")
            return []

        search_query = query if not site_filter else f"site:{site_filter} {query}"
        encoded = urllib.parse.quote(f"{search_query} buy")
        bing_url = f"https://www.bing.com/search?q={encoded}"
        discovered_urls: List[str] = []

        logger.info(f"[Browser Discovery] Querying Bing: '{search_query}' (experimental fallback)...")
        try:
            await page.goto(bing_url, wait_until="domcontentloaded", timeout=15000)
            links = await page.locator('#b_results h2 a').all()
            for link in links:
                href = await link.get_attribute("href")
                decoded = decode_bing_redirect(href)
                if decoded and decoded not in discovered_urls:
                    discovered_urls.append(decoded)
            logger.debug(f"[Browser Discovery] Discovered {len(discovered_urls)} raw links from Bing")
        except Exception as e:
            logger.warning(f"[Browser Discovery] Bing search error: {e}")

        # DuckDuckGo fallback if Bing returned 0 links
        if not discovered_urls:
            try:
                logger.info(f"[Browser Discovery] Falling back to DuckDuckGo: '{search_query}'...")
                ddg_url = f"https://duckduckgo.com/?q={urllib.parse.quote(search_query)}"
                await page.goto(ddg_url, wait_until="domcontentloaded", timeout=15000)
                await page.wait_for_timeout(1500)
                ddg_links = await page.locator('article h2 a, [data-testid="result-title-a"]').all()
                for link in ddg_links:
                    href = await link.get_attribute("href")
                    if href and href.startswith("http") and "duckduckgo.com" not in href and href not in discovered_urls:
                        discovered_urls.append(href)
            except Exception as e:
                logger.warning(f"[Browser Discovery] DuckDuckGo fallback error: {e}")

        return discovered_urls
