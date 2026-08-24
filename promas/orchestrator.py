"""
Promas Master Orchestrator
Coordinates dynamic search discovery, parallel browser contexts, universal extraction, and fallback indexing.
"""

import asyncio
from typing import List, Optional

from playwright.async_api import async_playwright

try:
    from playwright_stealth import Stealth
    HAS_STEALTH = True
except ImportError:
    HAS_STEALTH = False

from promas.core.discovery import discover_product_urls, scrape_image_index_fallback
from promas.core.extractor import extract_page_product_images
from promas.core.models import ProductImageResult


async def get_product_images(
    query: str,
    max_images: int = 10,
    site_filter: Optional[str] = None
) -> ProductImageResult:
    """
    Universal entry point: Scrapes high-resolution product imagery from any URL or search query.

    Args:
        query: Product name/model (e.g. 'Sony FX5', 'Marlboro Cigarette', 'Le Minerale Water') OR a direct URL
        max_images: Maximum number of high-res images to return (default: 10)
        site_filter: Optional domain filter (e.g. 'apple.com', 'nike.com', 'bhphotovideo.com')
    """
    query = query.strip()
    is_direct_url = query.startswith("http://") or query.startswith("https://")

    pw_cm = Stealth().use_async(async_playwright()) if HAS_STEALTH else async_playwright()

    async with pw_cm as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-infobars",
                "--disable-dev-shm-usage",
                "--window-size=1920,1080"
            ]
        )

        all_images: List[str] = []
        sources_scraped: List[str] = []
        primary_title: Optional[str] = None
        semaphore = asyncio.Semaphore(3)

        async def scrape_single_url(target_url: str):
            nonlocal primary_title
            async with semaphore:
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                    viewport={"width": 1920, "height": 1080},
                    locale="en-US"
                )
                page = await context.new_page()
                try:
                    await page.goto(target_url, wait_until="domcontentloaded", timeout=25000)
                    result = await extract_page_product_images(page, target_url)
                    if result.get("title") and not primary_title:
                        primary_title = result["title"]
                    return result
                except Exception:
                    return {"title": None, "url": target_url, "images": []}
                finally:
                    await context.close()

        try:
            if is_direct_url:
                target_urls = [query]
            else:
                # 1. Discover top product URLs dynamically
                search_context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                    viewport={"width": 1920, "height": 1080},
                    locale="en-US"
                )
                search_page = await search_context.new_page()
                target_urls = await discover_product_urls(search_page, query, site_filter=site_filter, max_urls=3)
                await search_context.close()

                # If no product URLs discovered, target_urls remains empty and triggers image search index
                if not target_urls:
                    target_urls = []

            seen_keys = set()
            # 2. Scrape target product pages in parallel (if any valid target URLs)
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
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
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

            final_images = all_images[:max_images]

            if final_images:
                return ProductImageResult(
                    status="success",
                    query=query,
                    title=primary_title or query,
                    sources_scraped=sources_scraped,
                    images=final_images
                )
            else:
                return ProductImageResult(
                    status="error",
                    query=query,
                    sources_scraped=sources_scraped,
                    error_message=f"No high-resolution product images could be extracted for '{query}'."
                )

        except Exception as e:
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
