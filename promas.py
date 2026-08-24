"""
Promas (Product Image Scraper) - Universal Search-Driven Engine & CLI
Scalable, zero-hardcoding product image scraper and universal URL extractor for AI agents.
"""

import json
import re
import urllib.parse
import asyncio
import argparse
from typing import List, Optional, Dict, Any, Tuple
from pydantic import BaseModel, Field
from playwright.async_api import async_playwright, Page, BrowserContext

try:
    from playwright_stealth import Stealth
    HAS_STEALTH = True
except ImportError:
    HAS_STEALTH = False


class ProductImageResult(BaseModel):
    status: str = Field(description="'success' or 'error'")
    query: str = Field(description="Search query or URL requested")
    title: Optional[str] = Field(default=None, description="Title of the matched product or primary page")
    sources_scraped: List[str] = Field(default_factory=list, description="URLs or domains scraped")
    images: List[str] = Field(default_factory=list, description="Array of high-resolution image URLs")
    error_message: Optional[str] = Field(default=None, description="Error message if scraping failed")


# ==============================================================================
# Image Normalization, Upscaling & Quality Filtering
# ==============================================================================

# Bad keywords indicating icons, logos, badges, tracking pixels
BLOCKED_PATTERNS = [
    r'logo', r'icon', r'badge', r'avatar', r'spacer', r'pixel', r'blank',
    r'tracking', r'spinner', r'placeholder', r'arrow', r'rating', r'star',
    r'payment', r'credit-card', r'visa', r'mastercard', r'paypal', r'favicon'
]
BLOCKED_REGEX = re.compile('|'.join(BLOCKED_PATTERNS), re.IGNORECASE)


def clean_and_upscale_image_url(url: str, base_url: Optional[str] = None) -> Optional[str]:
    """
    Cleans Cloudflare/Imgix/Shopify wrappers and upgrades resolution constraints
    to retrieve the highest-resolution master asset.
    """
    if not url or not isinstance(url, str):
        return None

    url = url.strip()
    if not url or url.startswith("data:image"):
        return None

    # Handle relative URLs
    if url.startswith("//"):
        url = "https:" + url
    elif url.startswith("/"):
        if base_url:
            parsed_base = urllib.parse.urlparse(base_url)
            url = f"{parsed_base.scheme}://{parsed_base.netloc}{url}"
        else:
            return None
    elif not url.startswith("http://") and not url.startswith("https://"):
        if base_url:
            url = urllib.parse.urljoin(base_url, url)
        else:
            return None

    # Filter out SVGs and animated GIFs
    clean_path = url.split("?")[0].lower()
    if clean_path.endswith(".svg") or clean_path.endswith(".gif"):
        return None

    # 1. Cloudflare CDN wrapper unwrap: /cdn-cgi/image/.../(https?://...)
    cf_match = re.search(r'/cdn-cgi/image/[^/]+/(https?://.+)', url)
    if cf_match:
        url = cf_match.group(1)

    # 2. Shopify CDN resolution upscaler: _300x300.jpg, _500x.png -> _2048x2048.jpg
    if "cdn.shopify.com" in url:
        url = re.sub(r'_(?:\d+x\d*|\d*x\d+)\.(jpg|jpeg|png|webp)', r'_2048x2048.\1', url, flags=re.IGNORECASE)

    # 3. Amazon image resolution upscaler: ._AC_SL300_.jpg -> ._AC_SL1500_.jpg
    if "media-amazon.com" in url or "images-amazon.com" in url or "ssl-images-amazon.com" in url:
        url = re.sub(r'\._[A-Z0-9_,]+_\.(jpg|jpeg|png|webp)', r'._AC_SL1500_.\1', url, flags=re.IGNORECASE)

    # 4. eBay image upscaler: s-l300.jpg, s-l500.jpg -> s-l1600.jpg
    if "i.ebayimg.com" in url:
        url = re.sub(r'/s-l\d+\.(jpg|jpeg|png|webp)', r'/s-l1600.\1', url, flags=re.IGNORECASE)

    # 5. B&H Photo CDN upscaler: images500x500 -> images2500x2500
    if "bhphoto.com" in url or "static.bhphoto.com" in url:
        url = url.replace("/images/smallimages/", "/images/images2500x2500/")
        url = url.replace("/multiple_images/thumbnails/", "/multiple_images/images500x500/")
        url = url.replace("/images/thumbnails/", "/images/images500x500/")
        url = re.sub(r'/images(345x345|500x500|150x150)/', '/images2500x2500/', url)

    # 6. Generic Imgix / Cloudinary query width/height stripping or upscaling
    if "imgix.net" in url or "cloudinary.com" in url or "fastly.net" in url:
        # Increase width/height parameters or remove downscaling
        url = re.sub(r'([?&])w=\d+', r'\1w=2000', url)
        url = re.sub(r'([?&])width=\d+', r'\1width=2000', url)
        url = re.sub(r'/w_\d+,h_\d+/', r'/w_2000,h_2000/', url)

    # 7. Adobe Scene7 CDN (Target, Home Depot, Best Buy, etc.) - unwrap to master original
    if "scene7.com" in url:
        url = url.split("?")[0]

    return url


def is_valid_product_image(url: str) -> bool:
    """
    Validates if an image URL looks like a genuine product/gallery photo rather than UI noise.
    """
    if not url:
        return False

    url_lower = url.lower()
    # Check for blocked patterns (icons, badges, logos, etc.)
    if BLOCKED_REGEX.search(url_lower):
        # Allow if it's explicitly inside a known product/gallery path
        if not any(k in url_lower for k in ["/product", "/gallery", "/media", "/item", "/images2500x2500", "i.ebayimg.com"]):
            return False

    # Check for tiny dimension parameters in URL
    if re.search(r'[?&](?:w|width|h|height)=(?:[1-9][0-9]?|1[0-4][0-9])(?:&|$)', url_lower):
        return False

    return True


def parse_srcset_images(srcset_val: str, base_url: Optional[str] = None) -> List[str]:
    """
    Parses a srcset attribute and extracts the highest-resolution candidate.
    """
    candidates = []
    if not srcset_val:
        return candidates

    entries = srcset_val.split(",")
    for entry in entries:
        parts = entry.strip().split()
        if not parts:
            continue
        src = parts[0]
        size = 0
        if len(parts) > 1:
            size_str = parts[1]
            if size_str.endswith("w"):
                try:
                    size = int(size_str[:-1])
                except ValueError:
                    size = 0
            elif size_str.endswith("x"):
                try:
                    size = int(float(size_str[:-1]) * 1000)
                except ValueError:
                    size = 0
        cleaned = clean_and_upscale_image_url(src, base_url)
        if cleaned:
            candidates.append((size, cleaned))

    if candidates:
        # Sort by size descending and return highest
        candidates.sort(key=lambda x: x[0], reverse=True)
        return [c[1] for c in candidates]
    return []


# ==============================================================================
# Universal Semantic Extraction Pipeline
# ==============================================================================

def parse_json_ld_images(raw_json: str, base_url: Optional[str] = None) -> List[str]:
    """
    Extracts image URLs from Schema.org JSON-LD scripts across any website.
    Handles Products, ImageObjects, Graphs, nested structures, and arrays.
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

    def extract_from_value(val):
        if isinstance(val, str):
            cleaned = clean_and_upscale_image_url(val, base_url)
            if cleaned and is_valid_product_image(cleaned):
                images.append(cleaned)
        elif isinstance(val, list):
            for item in val:
                extract_from_value(item)
        elif isinstance(val, dict):
            for key in ["url", "contentUrl", "thumbnailUrl", "image"]:
                if key in val:
                    extract_from_value(val[key])

    for node in nodes:
        if not isinstance(node, dict):
            continue
        node_type = str(node.get("@type", ""))
        is_product_like = any(t in node_type for t in [
            "Product", "IndividualProduct", "ProductModel", "ProductGroup", "ItemPage", "ImageObject"
        ]) or "image" in node

        if is_product_like:
            if "image" in node:
                extract_from_value(node["image"])
            if "primaryImageOfPage" in node:
                extract_from_value(node["primaryImageOfPage"])
            if "photo" in node:
                extract_from_value(node["photo"])

    return images


async def extract_page_product_images(page: Page, url: str) -> Dict[str, Any]:
    """
    Universal extraction pipeline for any given web page:
    1. Schema.org JSON-LD
    2. Microdata & RDFa ([itemprop="image"])
    3. OpenGraph & Twitter Cards
    4. Dynamic JS data blobs (Amazon dynamic images, Shopify product JSON)
    5. High-Res DOM Selectors & srcset
    """
    images: List[str] = []
    title = await page.title()

    # 1. Schema.org JSON-LD
    schemas = await page.locator('script[type="application/ld+json"]').all_inner_texts()
    for s in schemas:
        found = parse_json_ld_images(s, url)
        for img in found:
            if img not in images:
                images.append(img)

    # 2. OpenGraph & Twitter Cards Meta
    meta_selectors = [
        'meta[property="og:image"]',
        'meta[property="og:image:secure_url"]',
        'meta[name="twitter:image"]',
        'meta[name="twitter:image:src"]',
        'meta[itemprop="image"]'
    ]
    for meta_sel in meta_selectors:
        locs = page.locator(meta_sel)
        cnt = await locs.count()
        for i in range(cnt):
            content = await locs.nth(i).get_attribute("content")
            if content:
                cleaned = clean_and_upscale_image_url(content, url)
                if cleaned and is_valid_product_image(cleaned) and cleaned not in images:
                    images.append(cleaned)

    # 3. Microdata & RDFa
    microdata_locs = page.locator('[itemprop="image"]')
    cnt = await microdata_locs.count()
    for i in range(cnt):
        loc = microdata_locs.nth(i)
        tag_name = await loc.evaluate("el => el.tagName.toLowerCase()")
        src = await loc.get_attribute("src") if tag_name == "img" else await loc.get_attribute("href")
        if src:
            cleaned = clean_and_upscale_image_url(src, url)
            if cleaned and is_valid_product_image(cleaned) and cleaned not in images:
                images.append(cleaned)

    # 4. Amazon Dynamic Image Data JSON / Scripts
    try:
        dyn_imgs = await page.locator('#landingImage, #imgBlkFront, [data-a-dynamic-image]').all()
        for dyn_el in dyn_imgs:
            dyn_data = await dyn_el.get_attribute("data-a-dynamic-image")
            if dyn_data:
                parsed_dyn = json.loads(dyn_data)
                for dyn_url in parsed_dyn.keys():
                    cleaned = clean_and_upscale_image_url(dyn_url, url)
                    if cleaned and is_valid_product_image(cleaned) and cleaned not in images:
                        images.append(cleaned)
    except Exception:
        pass

    # 5. DOM & Responsive srcset & High-Res attributes
    dom_image_selectors = [
        'img[data-zoom-image]',
        'img[data-high-res-src]',
        'img[data-large-img]',
        'img[data-old-hires]',
        'img[data-zoom-image-src]',
        'img[srcset]',
        'picture source[srcset]',
        '[data-selenium="inlineMediaMainImage"]',
        '[data-selenium="productMainImage"]',
        'img.product-image',
        'img.gallery-image',
        'img[class*="product"]',
        'img[id*="product"]'
    ]
    for sel in dom_image_selectors:
        locs = page.locator(sel)
        cnt = min(await locs.count(), 10)
        for i in range(cnt):
            loc = locs.nth(i)
            # Check high-res data attributes
            for attr in ["data-zoom-image", "data-high-res-src", "data-large-img", "data-old-hires", "data-zoom-image-src"]:
                hires_val = await loc.get_attribute(attr)
                if hires_val:
                    cleaned = clean_and_upscale_image_url(hires_val, url)
                    if cleaned and is_valid_product_image(cleaned) and cleaned not in images:
                        images.append(cleaned)

            # Check srcset
            srcset_val = await loc.get_attribute("srcset")
            if srcset_val:
                srcset_imgs = parse_srcset_images(srcset_val, url)
                for s_img in srcset_imgs:
                    if s_img and is_valid_product_image(s_img) and s_img not in images:
                        images.append(s_img)

            # Check standard src
            src_val = await loc.get_attribute("src")
            if src_val:
                cleaned = clean_and_upscale_image_url(src_val, url)
                if cleaned and is_valid_product_image(cleaned) and cleaned not in images:
                    images.append(cleaned)

    # 6. Clean Page Title if available
    h1_loc = page.locator('h1').first
    if await h1_loc.count() > 0:
        h1_text = (await h1_loc.inner_text()).strip()
        if h1_text and len(h1_text) > 3:
            title = h1_text

    return {
        "title": title,
        "url": url,
        "images": images
    }


# ==============================================================================
# Search-Driven Dynamic Discovery Engine
# ==============================================================================

def score_product_url(url: str, query_keywords: List[str]) -> int:
    """
    Ranks URLs based on e-commerce product indicators and query keyword relevance.
    """
    score = 0
    url_lower = url.lower()

    # Boost authoritative e-commerce / brand domains
    high_priority_domains = [
        "apple.com", "sony.com", "nike.com", "samsung.com", "canon.com",
        "bhphotovideo.com", "adorama.com", "bestbuy.com", "amazon.com",
        "ebay.com", "walmart.com", "target.com", "newegg.com", "microcenter.com"
    ]
    for d in high_priority_domains:
        if d in url_lower:
            score += 25
            break

    # Boost e-commerce URL patterns
    ecom_indicators = ["/product/", "/dp/", "/p/", "/item/", "/buy/", "/shop/", "/pd/", "/t/"]
    for ind in ecom_indicators:
        if ind in url_lower:
            score += 20
            break

    # Penalize non-product pages
    penalize_indicators = ["/category/", "/search", "/tag/", "/forum/", "/thread/", "/news/", "/blog/", "wikipedia.org", "youtube.com"]
    for pen in penalize_indicators:
        if pen in url_lower:
            score -= 30

    # Boost keyword matches in URL
    for kw in query_keywords:
        if len(kw) > 2 and kw in url_lower:
            score += 10

    return score


async def discover_product_urls(page: Page, query: str, site_filter: Optional[str] = None, max_urls: int = 3) -> List[str]:
    """
    Discovers top product pages dynamically via open search query.
    """
    search_query = query
    if site_filter:
        search_query = f"site:{site_filter} {query}"

    encoded = urllib.parse.quote(search_query)
    search_url = f"https://html.duckduckgo.com/html/?q={encoded}"

    discovered_urls: List[str] = []

    try:
        await page.goto(search_url, wait_until="domcontentloaded", timeout=20000)
        # Extract organic result links
        links = await page.locator('a.result__url, a.result__snippet, a.result__title').all()
        raw_urls = []
        for link in links:
            href = await link.get_attribute("href")
            if not href:
                continue

            # DuckDuckGo wraps URLs as //duckduckgo.com/l/?uddg=...
            if "uddg=" in href:
                parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
                if "uddg" in parsed and parsed["uddg"]:
                    actual_url = parsed["uddg"][0]
                    if actual_url.startswith("http") and actual_url not in raw_urls:
                        raw_urls.append(actual_url)
            elif href.startswith("http") and "duckduckgo.com" not in href and href not in raw_urls:
                raw_urls.append(href)

        # Rank and pick top URLs
        query_kw = [k.lower() for k in query.split() if len(k) > 2]
        scored_urls = [(score_product_url(u, query_kw), u) for u in raw_urls]
        scored_urls.sort(key=lambda x: x[0], reverse=True)

        discovered_urls = [u for score, u in scored_urls if score > 0][:max_urls]
        if not discovered_urls and raw_urls:
            discovered_urls = raw_urls[:max_urls]

    except Exception:
        # Fallback to direct search URL construction for prominent sites if search engine was blocked
        pass

    return discovered_urls


# ==============================================================================
# Fail-Safe Direct Image Index Fallback
# ==============================================================================

async def scrape_image_index_fallback(page: Page, query: str, max_images: int = 10) -> List[str]:
    """
    Fallback mechanism: Queries open image search directly if PDPs fail or return 0 images.
    """
    images: List[str] = []
    encoded = urllib.parse.quote(f"{query} product")
    url = f"https://www.bing.com/images/search?q={encoded}&FORM=HDRSC2"

    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=15000)
        # Bing image data is embedded in <a class="iusc" m='{"murl":"..."}'>
        locs = page.locator('a.iusc')
        cnt = min(await locs.count(), max_images * 2)
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
                except Exception:
                    continue
    except Exception:
        pass

    return images


# ==============================================================================
# Main Orchestrator
# ==============================================================================

async def get_product_images(
    query: str,
    max_images: int = 10,
    site_filter: Optional[str] = None
) -> ProductImageResult:
    """
    Universal entry point: Scrapes high-resolution product imagery from any URL or search query.

    Args:
        query: Product name/model (e.g. 'iPhone 16 Pro', 'Sony FX3') OR a direct URL
        max_images: Maximum number of high-res images to return (default: 10)
        site_filter: Optional domain filter (e.g. 'apple.com', 'bhphotovideo.com')
    """
    query = query.strip()
    is_direct_url = query.startswith("http://") or query.startswith("https://")

    stealth = Stealth() if HAS_STEALTH else None
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

                # Fallback URL if discovery returned empty
                if not target_urls:
                    encoded_q = urllib.parse.quote(query)
                    target_urls = [f"https://www.bhphotovideo.com/c/search?Ntt={encoded_q}&N=0"]

            # 2. Scrape target product pages in parallel
            tasks = [scrape_single_url(u) for u in target_urls]
            page_results = await asyncio.gather(*tasks)

            seen_keys = set()
            for pr in page_results:
                sources_scraped.append(pr["url"])
                for img in pr.get("images", []):
                    # Deduplicate based on base URL (ignoring minor query string variations)
                    base_key = img.split("?")[0].lower()
                    if base_key not in seen_keys and img not in all_images:
                        seen_keys.add(base_key)
                        all_images.append(img)

            # 3. Direct Image Search Index Fallback if 0 images found
            if not all_images and not is_direct_url:
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

            # Limit total images
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


# Alias for backward compatibility
scrape_product_images = get_product_images


async def main():
    parser = argparse.ArgumentParser(description="Promas: Universal Product Image Scraper CLI")
    parser.add_argument("query", nargs="?", default="iPhone 16 Pro", help="Product query or direct URL")
    parser.add_argument("--max-images", type=int, default=10, help="Maximum images to return (default: 10)")
    parser.add_argument("--site", default=None, help="Optional site domain filter (e.g. apple.com)")
    args = parser.parse_args()

    print(f"[*] Promas querying: '{args.query}' (max: {args.max_images}, site: {args.site})...")
    result = await get_product_images(query=args.query, max_images=args.max_images, site_filter=args.site)
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())
