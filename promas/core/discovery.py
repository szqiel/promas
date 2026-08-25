"""
Product Discovery & URL Scoring
"""

import json
import urllib.parse
from typing import List, Optional

from loguru import logger
from playwright.async_api import Page
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from promas.cdn.registry import clean_and_upscale_image_url, is_valid_product_image
from promas.search_backends import search_candidate_urls

DISCARD_DOMAINS = [
    "google.com", "bing.com", "duckduckgo.com", "wikipedia.org", "wikimedia.org",
    "wikileaks.org", "wiktionary.org", "theperfectfrench.com", "dictionary.com",
    "merriam-webster.com", "cambridge.org", "youtube.com", "facebook.com", "twitter.com",
    "linkedin.com", "indeed.com", "glassdoor.com", "ziprecruiter.com", "governmentjobs.com",
    "governmentresource.com"
]


def score_product_url(url: str, query_keywords: List[str]) -> int:
    """
    Ranks candidate URLs based on e-commerce product indicators and keyword relevance.
    """
    score = 0
    url_lower = url.lower()

    # Discard non-retail / non-product domains immediately
    for d in DISCARD_DOMAINS:
        if d in url_lower:
            return -100

    # Authoritative store / brand domains
    high_priority_domains = [
        "apple.com", "sony.com", "nike.com", "samsung.com", "canon.com",
        "bhphotovideo.com", "adorama.com", "bestbuy.com", "amazon.com",
        "ebay.com", "walmart.com", "target.com", "stockx.com", "goat.com",
        "footlocker.com", "newegg.com", "microcenter.com", "tokopedia.com",
        "shopee.co.id", "blibli.com", "klikindomaret.com", "alfagift.id",
        "mayora.com", "leminerale.com"
    ]
    for d in high_priority_domains:
        if d in url_lower:
            score += 35
            break

    # E-commerce URL indicators
    ecom_indicators = [
        "/product/", "/dp/", "/p/", "/item/", "/buy/", "/shop/",
        "/pd/", "/t/", "/w/", "/find/", "/catalog/", "/detail/"
    ]
    for ind in ecom_indicators:
        if ind in url_lower:
            score += 25
            break

    # Penalize non-product pages
    penalize_indicators = ["/category/", "/tag/", "/forum/", "/thread/", "/news/", "/blog/", "/grammar/"]
    for pen in penalize_indicators:
        if pen in url_lower:
            score -= 40

    # Keyword match
    for kw in query_keywords:
        if len(kw) > 2 and kw in url_lower:
            score += 10

    return score


async def discover_product_urls(
    page: Optional[Page],
    query: str,
    site_filter: Optional[str] = None,
    max_urls: int = 3
) -> List[str]:
    """
    Discovers and scores top product pages dynamically across configured search backends.
    """
    logger.info(f"Discovering candidate URLs for query='{query}' (site_filter={site_filter})")
    discovered_urls = await search_candidate_urls(query, site_filter=site_filter, page=page)

    # Rank and filter URLs - only keep URLs with positive e-commerce relevance score
    query_kw = [k.lower() for k in query.split() if len(k) > 2]
    scored = [(score_product_url(u, query_kw), u) for u in discovered_urls]
    scored.sort(key=lambda x: x[0], reverse=True)

    final_urls = [u for score, u in scored if score > 0][:max_urls]
    logger.info(f"Selected {len(final_urls)} top candidate URLs for scraping: {final_urls}")
    return final_urls


@retry(
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=1, min=1, max=3),
    retry=retry_if_exception_type(Exception),
    reraise=False
)
async def _navigate_image_fallback(page: Page, url: str) -> None:
    await page.goto(url, wait_until="domcontentloaded", timeout=15000)


async def scrape_image_index_fallback(page: Page, query: str, max_images: int = 10) -> List[str]:
    """
    Fail-safe fallback: Queries open image search directly if PDPs fail or return 0 images.
    """
    images: List[str] = []
    encoded = urllib.parse.quote(f"{query} product pack photo")
    url = f"https://www.bing.com/images/search?q={encoded}&FORM=HDRSC2"

    logger.info(f"Querying fallback image search index for: '{query}'")
    try:
        await _navigate_image_fallback(page, url)
        locs = page.locator('a.iusc')
        cnt = min(await locs.count(), max_images * 3)
        if cnt == 0:
            logger.debug(f"Fallback image selector 'a.iusc' returned 0 results on {url}")

        for i in range(cnt):
            m_attr = await locs.nth(i).get_attribute("m")
            if m_attr:
                try:
                    data = json.loads(m_attr)
                    murl = data.get("murl")
                    if murl and murl.startswith("http"):
                        cleaned = clean_and_upscale_image_url(murl)
                        if cleaned and is_valid_product_image(cleaned) and cleaned not in images:
                            images.append(cleaned)
                            if len(images) >= max_images:
                                break
                except Exception as ex:
                    logger.debug(f"Failed to parse image index payload item: {ex}")
                    continue
    except Exception as e:
        logger.warning(f"Fallback image index scraping encountered error: {e}")

    logger.info(f"Fallback image search index extracted {len(images)} high-res photos")
    return images
