"""
Bing Browser Stealth Search Backend
"""

import base64
import re
import urllib.parse
from typing import List, Optional

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
    """Stealth Playwright Bing Organic Search Backend."""

    async def search(self, page: Page, query: str, site_filter: Optional[str] = None) -> List[str]:
        search_query = query if not site_filter else f"site:{site_filter} {query}"
        encoded = urllib.parse.quote(f"{search_query} buy")
        bing_url = f"https://www.bing.com/search?q={encoded}"
        discovered_urls: List[str] = []

        try:
            await page.goto(bing_url, wait_until="domcontentloaded", timeout=15000)
            links = await page.locator('#b_results h2 a').all()
            for link in links:
                href = await link.get_attribute("href")
                decoded = decode_bing_redirect(href)
                if decoded and decoded not in discovered_urls:
                    discovered_urls.append(decoded)
        except Exception:
            pass

        return discovered_urls
