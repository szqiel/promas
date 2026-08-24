"""
Promas (Product Image Scraper) - Core Engine & CLI
High-speed, stealth-enabled product image extraction for AI agents.
"""

import json
import re
import urllib.parse
import asyncio
import argparse
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from playwright.async_api import async_playwright, Page, BrowserContext

try:
    from playwright_stealth import Stealth
    HAS_STEALTH = True
except ImportError:
    HAS_STEALTH = False


class ProductImageResult(BaseModel):
    status: str = Field(description="'success' or 'error'")
    source: str = Field(default="bh", description="Source platform scraped")
    query: str = Field(description="Search query used")
    title: Optional[str] = Field(default=None, description="Title of the matched product")
    product_url: Optional[str] = Field(default=None, description="Direct URL to product detail page")
    images: List[str] = Field(default_factory=list, description="Array of high-resolution image URLs")
    error_message: Optional[str] = Field(default=None, description="Error message if scraping failed")


def clean_and_upscale_image_url(url: str) -> str:
    """
    Cleans Cloudflare CDN wrappers and upgrades resolutions to high-res master URLs when applicable.
    """
    if not url:
        return url

    # Unwrap Cloudflare cdn-cgi wrappers: e.g. /cdn-cgi/image/.../https://static.bhphoto.com/...
    cdn_match = re.search(r'/cdn-cgi/image/[^/]+/(https?://.+)', url)
    if cdn_match:
        url = cdn_match.group(1)

    # If relative URL, prepend scheme/host
    if url.startswith("//"):
        url = "https:" + url
    elif url.startswith("/"):
        url = "https://www.bhphotovideo.com" + url

    # Replace smallimages with images2500x2500 for static.bhphoto.com
    url = url.replace("/images/smallimages/", "/images/images2500x2500/")
    url = url.replace("/multiple_images/thumbnails/", "/multiple_images/images500x500/")
    url = url.replace("/images/thumbnails/", "/images/images500x500/")
    
    # Replace low-res dimensions like images345x345 with images2500x2500 on static CDN
    if "static.bhphoto.com" in url:
        url = re.sub(r'/images(345x345|150x150)/', '/images2500x2500/', url)

    return url


def parse_json_ld_images(raw_json: str) -> List[str]:
    """
    Extracts image URLs from JSON-LD schema payload.
    Supports Product types, ImageObject, @graph containers, and plain strings/lists.
    """
    images = []
    try:
        data = json.loads(raw_json)
    except Exception:
        return images

    nodes = []
    if isinstance(data, list):
        nodes.extend(data)
    elif isinstance(data, dict):
        if "@graph" in data and isinstance(data["@graph"], list):
            nodes.extend(data["@graph"])
        else:
            nodes.append(data)

    for node in nodes:
        if not isinstance(node, dict):
            continue
        node_type = node.get("@type")
        if node_type in ["Product", "IndividualProduct", "ProductModel", "ItemPage"] or "image" in node:
            raw_img = node.get("image")
            if not raw_img:
                continue

            if isinstance(raw_img, str):
                images.append(clean_and_upscale_image_url(raw_img))
            elif isinstance(raw_img, list):
                for item in raw_img:
                    if isinstance(item, str):
                        images.append(clean_and_upscale_image_url(item))
                    elif isinstance(item, dict) and "url" in item:
                        images.append(clean_and_upscale_image_url(item["url"]))
                    elif isinstance(item, dict) and "contentUrl" in item:
                        images.append(clean_and_upscale_image_url(item["contentUrl"]))
            elif isinstance(raw_img, dict):
                if "url" in raw_img:
                    images.append(clean_and_upscale_image_url(raw_img["url"]))
                elif "contentUrl" in raw_img:
                    images.append(clean_and_upscale_image_url(raw_img["contentUrl"]))

    return images


async def scrape_bh(page: Page, query: str) -> Dict[str, Any]:
    """
    Scrapes B&H Photo product images using direct search URL, JSON-LD schema parsing, and DOM fallbacks.
    """
    encoded_query = urllib.parse.quote(query)
    search_url = f"https://www.bhphotovideo.com/c/search?Ntt={encoded_query}&N=0"

    # 1. Search Navigation
    await page.goto(search_url, wait_until="domcontentloaded", timeout=30000)

    # Check if direct redirect to PDP occurred
    current_url = page.url
    if "/c/product/" in current_url:
        product_url = current_url
        product_title = await page.title()
    else:
        # Locate First Product Link
        first_product = page.locator('a[data-selenium="miniProductPageProductNameLink"]').first
        try:
            await first_product.wait_for(timeout=10000)
            product_url = await first_product.get_attribute("href")
            product_title = (await first_product.inner_text()).strip()
        except Exception:
            # Try alternate product link selectors
            alt_product = page.locator('a[data-selenium="miniProductPageImgLink"], div[data-selenium="miniProductPage"] a').first
            if await alt_product.count() > 0:
                product_url = await alt_product.get_attribute("href")
                product_title = await page.title()
            else:
                raise RuntimeError(f"No product found for query '{query}' in search results.")

        if not product_url:
            raise RuntimeError("No product link found in search results.")

        if not product_url.startswith("http"):
            product_url = f"https://www.bhphotovideo.com{product_url}"

        # 2. Navigate to Product Detail Page (PDP)
        await page.goto(product_url, wait_until="domcontentloaded", timeout=30000)

    # 3. Extract High-Res Images from JSON-LD Schemas
    image_urls: List[str] = []
    schemas = await page.locator('script[type="application/ld+json"]').all_inner_texts()

    for raw_schema in schemas:
        found_imgs = parse_json_ld_images(raw_schema)
        for img in found_imgs:
            if img and img not in image_urls:
                image_urls.append(img)

    # 4. Extract OpenGraph and Twitter Meta Tags
    meta_selectors = [
        'meta[property="og:image"]',
        'meta[name="twitter:image"]',
        'meta[property="og:image:secure_url"]'
    ]
    for meta_sel in meta_selectors:
        loc = page.locator(meta_sel).first
        if await loc.count() > 0:
            content = await loc.get_attribute("content")
            if content:
                cleaned = clean_and_upscale_image_url(content)
                if cleaned and cleaned not in image_urls:
                    image_urls.append(cleaned)

    # 5. Extract Media Gallery & DOM Selectors
    dom_selectors = [
        '[data-selenium="inlineMediaMainImage"]',
        '[data-selenium="productMainImage"]',
        'img[data-selenium="inlineMediaThumbnailImage"]',
        'img[src*="bhphoto.com/images"]',
        'img[src*="static.bhphoto.com"]'
    ]
    for sel in dom_selectors:
        locs = page.locator(sel)
        cnt = await locs.count()
        for i in range(cnt):
            src = await locs.nth(i).get_attribute("src")
            if src:
                cleaned = clean_and_upscale_image_url(src)
                if cleaned and cleaned not in image_urls and not cleaned.endswith(".gif") and not cleaned.endswith(".svg"):
                    image_urls.append(cleaned)

    return {
        "title": product_title,
        "product_url": product_url,
        "images": image_urls
    }


async def scrape_product_images(query: str, source: str = "bh") -> ProductImageResult:
    """
    Main entry point for scraping product images across supported sources.
    """
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

        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="en-US"
        )
        page = await context.new_page()

        try:
            if source.lower() in ["bh", "b&h", "bhphoto", "bhphotovideo"]:
                scraped = await scrape_bh(page, query)
            else:
                # Default fallback
                scraped = await scrape_bh(page, query)

            return ProductImageResult(
                status="success",
                source=source,
                query=query,
                title=scraped.get("title"),
                product_url=scraped.get("product_url"),
                images=scraped.get("images", [])
            )

        except Exception as e:
            return ProductImageResult(
                status="error",
                source=source,
                query=query,
                error_message=str(e)
            )
        finally:
            await browser.close()



async def main():
    parser = argparse.ArgumentParser(description="Promas: Product Image Scraper CLI")
    parser.add_argument("query", nargs="?", default="Sony FX3", help="Product query to search")
    parser.add_argument("--source", default="bh", help="Source platform (default: bh)")
    args = parser.parse_args()

    print(f"[*] Promas searching for: '{args.query}' on source '{args.source}'...")
    result = await scrape_product_images(query=args.query, source=args.source)
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())
