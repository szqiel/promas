"""
Promas Master Orchestrator
Coordinates dynamic search discovery, per-domain rate limiting, parallel browser contexts,
universal extraction, async HTTP image verification, perceptual hash deduplication,
fallback indexing, tenacity retries, and TTL-based caching.
"""

import asyncio
from typing import List, Optional

from loguru import logger
from playwright.async_api import Page, async_playwright
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

try:
    from playwright_stealth import Stealth
    HAS_STEALTH = True
except ImportError:
    HAS_STEALTH = False

from promas.core.cache import get_cached_result, set_cached_result
from promas.core.config import settings
from promas.core.discovery import discover_product_urls, scrape_image_index_fallback
from promas.core.extractor import extract_page_product_images
from promas.core.models import ProductImageResult
from promas.core.rate_limiter import DomainRateLimiter
from promas.core.verifier import verify_and_deduplicate_candidate_images


@retry(
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=1, min=1, max=3),
    retry=retry_if_exception_type(Exception),
    reraise=True
)
async def _navigate_with_retry(page: Page, target_url: str) -> None:
    """Navigates to URL with exponential backoff on transient network errors."""
    try:
        await page.goto(target_url, wait_until="domcontentloaded", timeout=settings.timeout_navigation_ms)
    except Exception as e:
        logger.warning(f"Navigation to {target_url} failed ({e}), retrying with backoff...")
        raise


async def get_product_images(
    query: str,
    max_images: int = 10,
    site_filter: Optional[str] = None,
    use_cache: Optional[bool] = None
) -> ProductImageResult:
    """
    Universal entry point: Scrapes high-resolution product imagery from any URL or search query.

    Args:
        query: Product name/model (e.g. 'Sony FX5', 'Marlboro Cigarette', 'Le Minerale Water') OR a direct URL
        max_images: Maximum number of high-res images to return (default: 10)
        site_filter: Optional domain filter (e.g. 'apple.com', 'nike.com', 'bhphotovideo.com')
        use_cache: Whether to read/write from TTL disk cache (defaults to settings.cache_enabled)
    """
    query = query.strip()
    is_direct_url = query.startswith("http://") or query.startswith("https://")
    should_cache = use_cache if use_cache is not None else settings.cache_enabled

    # 1. Check TTL Cache
    if should_cache:
        cached = get_cached_result(query, max_images, site_filter)
        if cached:
            logger.info(f"Returning cached results for query='{query}' ({len(cached.images)} images)")
            return cached

    logger.info(f"Scraping product images for query='{query}' (max: {max_images}, site: {site_filter})")
    pw_cm = Stealth().use_async(async_playwright()) if HAS_STEALTH else async_playwright()
    rate_limiter = DomainRateLimiter(
        global_concurrency=settings.global_concurrency,
        per_domain_concurrency=settings.per_domain_concurrency,
        domain_delay_seconds=settings.domain_delay_seconds
    )

    async with pw_cm as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-infobars",
                "--disable-dev-shm-usage",
                f"--window-size={settings.viewport_width},{settings.viewport_height}"
            ]
        )

        all_images: List[str] = []
        sources_scraped: List[str] = []
        primary_title: Optional[str] = None

        async def scrape_single_url(target_url: str):
            nonlocal primary_title
            async with rate_limiter.acquire(target_url):
                context = await browser.new_context(
                    user_agent=settings.user_agent,
                    viewport={"width": settings.viewport_width, "height": settings.viewport_height},
                    locale="en-US"
                )
                page = await context.new_page()
                try:
                    await _navigate_with_retry(page, target_url)
                    result = await extract_page_product_images(page, target_url)
                    if result.get("title") and not primary_title:
                        primary_title = result["title"]
                    return result
                except Exception as e:
                    logger.warning(f"Whole page scrape failed for {target_url}: {e}")
                    return {"title": None, "url": target_url, "images": []}
                finally:
                    await context.close()

        try:
            if is_direct_url:
                target_urls = [query]
            else:
                # Discover top product URLs dynamically across configured backends
                search_context = await browser.new_context(
                    user_agent=settings.user_agent,
                    viewport={"width": settings.viewport_width, "height": settings.viewport_height},
                    locale="en-US"
                )
                search_page = await search_context.new_page()
                target_urls = await discover_product_urls(search_page, query, site_filter=site_filter, max_urls=3)
                await search_context.close()

                if not target_urls:
                    target_urls = []

            seen_keys = set()
            # 2. Scrape target product pages concurrently with per-domain limits
            if target_urls:
                tasks = [scrape_single_url(u) for u in target_urls]
                page_results = await asyncio.gather(*tasks)

                for pr in page_results:
                    sources_scraped.append(pr["url"])
                    for img in pr.get("images", []):
                        base_key = img.split("?")[0].lower()
                        if base_key not in seen_keys and img not in all_images:
                            seen_keys.add(base_key)
                            all_images.append(img)

            # 3. Direct Image Search Index Fallback if few images found
            if len(all_images) < 3 and not is_direct_url:
                fallback_context = await browser.new_context(
                    user_agent=settings.user_agent
                )
                fallback_page = await fallback_context.new_page()
                fallback_images = await scrape_image_index_fallback(fallback_page, query, max_images=max_images)
                await fallback_context.close()
                for img in fallback_images:
                    base_key = img.split("?")[0].lower()
                    if base_key not in seen_keys and img not in all_images:
                        seen_keys.add(base_key)
                        all_images.append(img)
                if fallback_images:
                    sources_scraped.append("image_search_index")

            # 4. Async HTTP Verification & Perceptual-Hash Deduplication
            verified_deduped_images = await verify_and_deduplicate_candidate_images(all_images)
            final_images = verified_deduped_images[:max_images]

            if final_images:
                result = ProductImageResult(
                    status="success",
                    query=query,
                    title=primary_title or query,
                    sources_scraped=sources_scraped,
                    images=final_images
                )
                if should_cache:
                    set_cached_result(query, result, max_images, site_filter)
                logger.info(f"Promas successfully completed '{query}': {len(final_images)} verified unique images")
                return result
            else:
                logger.warning(f"Promas found 0 verified product images for '{query}'")
                return ProductImageResult(
                    status="error",
                    query=query,
                    sources_scraped=sources_scraped,
                    error_message=f"No high-resolution product images could be extracted for '{query}'."
                )

        except Exception as e:
            logger.error(f"Fatal unhandled exception during scraping for '{query}': {e}")
            return ProductImageResult(
                status="error",
                query=query,
                sources_scraped=sources_scraped,
                error_message=str(e)
            )
        finally:
            await browser.close()


# Backward compatibility alias
scrape_product_images = get_product_images
