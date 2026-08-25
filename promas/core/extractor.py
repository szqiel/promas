"""
Universal Page Extractor Pipeline
Extracts high-resolution product imagery from Schema.org JSON-LD, Microdata, OpenGraph, dynamic JS datasets, and responsive DOM images.
"""

import json
import re
from typing import Any, Dict, List, Optional

from loguru import logger
from playwright.async_api import Page

from promas.cdn.registry import clean_and_upscale_image_url, is_valid_product_image


def parse_srcset_images(srcset_val: str, base_url: Optional[str] = None) -> List[str]:
    """
    Parses srcset candidate URLs without breaking on Cloudinary / Nike comma parameters.
    """
    candidates: List[tuple[int, str]] = []
    if not srcset_val:
        return []

    # Split candidates by comma only when followed by a new URL starting with http(s):// or /
    raw_entries = re.split(r',\s+(?=https?://|/|\S+\.\w{3,4})', srcset_val.strip())
    for entry in raw_entries:
        parts = entry.strip().split()
        if not parts:
            continue
        src = parts[0].rstrip(",")
        if not src or len(src) < 5:
            continue

        size = 0
        if len(parts) > 1:
            size_str = parts[1]
            if size_str.endswith("w"):
                try:
                    size = int(float(size_str[:-1]))
                except ValueError:
                    size = 0
            elif size_str.endswith("x"):
                try:
                    size = int(float(size_str[:-1]) * 1000)
                except ValueError:
                    size = 0

        cleaned = clean_and_upscale_image_url(src, base_url)
        if cleaned and is_valid_product_image(cleaned):
            candidates.append((size, cleaned))

    if candidates:
        candidates.sort(key=lambda x: x[0], reverse=True)
        return [c[1] for c in candidates]
    return []


def parse_json_ld_images(raw_json: str, base_url: Optional[str] = None) -> List[str]:
    """
    Extracts image URLs from Schema.org JSON-LD scripts across any website.
    """
    images: List[str] = []
    try:
        data = json.loads(raw_json)
    except Exception as e:
        logger.debug(f"Failed to decode JSON-LD script block: {e}")
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
    1. Triggers scroll to load lazy-loaded product cards and galleries.
    2. Schema.org JSON-LD
    3. Microdata & RDFa ([itemprop="image"])
    4. OpenGraph & Twitter Cards
    5. Dynamic JS data blobs (Amazon, Shopify, Nike)
    6. High-Res DOM Selectors & srcset
    """
    images: List[str] = []
    title = await page.title()

    # Trigger brief scroll to hydrate lazy-loaded images
    try:
        await page.evaluate("window.scrollBy(0, 600)")
        await page.wait_for_timeout(400)
    except Exception as e:
        logger.debug(f"Hydration scroll on {url} encountered notice: {e}")

    # 1. Schema.org JSON-LD
    schemas = await page.locator('script[type="application/ld+json"]').all_inner_texts()
    if not schemas:
        logger.debug(f"No JSON-LD scripts found on {url}")
    for s in schemas:
        found = parse_json_ld_images(s, url)
        for img in found:
            if img not in images:
                images.append(img)
    if schemas and images:
        logger.debug(f"Extracted {len(images)} images via JSON-LD on {url}")

    # 2. OpenGraph & Twitter Cards Meta
    meta_selectors = [
        'meta[property="og:image"]',
        'meta[property="og:image:secure_url"]',
        'meta[name="twitter:image"]',
        'meta[name="twitter:image:src"]',
        'meta[itemprop="image"]'
    ]
    og_count = 0
    for meta_sel in meta_selectors:
        locs = page.locator(meta_sel)
        cnt = await locs.count()
        for i in range(cnt):
            content = await locs.nth(i).get_attribute("content")
            if content:
                cleaned = clean_and_upscale_image_url(content, url)
                if cleaned and is_valid_product_image(cleaned) and cleaned not in images:
                    images.append(cleaned)
                    og_count += 1
    if og_count > 0:
        logger.debug(f"Extracted {og_count} meta OpenGraph/Twitter images on {url}")

    # 3. Microdata & RDFa
    microdata_locs = page.locator('[itemprop="image"]')
    cnt = await microdata_locs.count()
    if cnt == 0:
        logger.debug(f"No [itemprop='image'] Microdata elements found on {url}")
    for i in range(cnt):
        loc = microdata_locs.nth(i)
        tag_name = await loc.evaluate("el => el.tagName.toLowerCase()")
        src = await loc.get_attribute("src") if tag_name == "img" else await loc.get_attribute("href")
        if src:
            cleaned = clean_and_upscale_image_url(src, url)
            if cleaned and is_valid_product_image(cleaned) and cleaned not in images:
                images.append(cleaned)

    # 4. Amazon Dynamic Image Data JSON
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
    except Exception as e:
        logger.debug(f"Amazon dynamic image data parsing notice: {e}")

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
        'img[data-testid*="product-card"]',
        'img.product-image',
        'img.gallery-image',
        'img[class*="product"]',
        'img[id*="product"]',
        'img[src*="static.nike.com/a/images"]',
        'img[src*="i.ebayimg.com"]',
        'img[src*="target.scene7.com"]',
        'img[src*="static.bhphoto.com"]'
    ]
    for sel in dom_image_selectors:
        locs = page.locator(sel)
        cnt = min(await locs.count(), 20)
        for i in range(cnt):
            loc = locs.nth(i)
            for attr in ["data-zoom-image", "data-high-res-src", "data-large-img", "data-old-hires", "data-zoom-image-src"]:
                hires_val = await loc.get_attribute(attr)
                if hires_val:
                    cleaned = clean_and_upscale_image_url(hires_val, url)
                    if cleaned and is_valid_product_image(cleaned) and cleaned not in images:
                        images.append(cleaned)

            srcset_val = await loc.get_attribute("srcset")
            if srcset_val:
                srcset_imgs = parse_srcset_images(srcset_val, url)
                for s_img in srcset_imgs:
                    if s_img and is_valid_product_image(s_img) and s_img not in images:
                        images.append(s_img)

            src_val = await loc.get_attribute("src")
            if src_val:
                cleaned = clean_and_upscale_image_url(src_val, url)
                if cleaned and is_valid_product_image(cleaned) and cleaned not in images:
                    images.append(cleaned)

    # 6. Page Title
    h1_loc = page.locator('h1').first
    if await h1_loc.count() > 0:
        h1_text = (await h1_loc.inner_text()).strip()
        if h1_text and len(h1_text) > 3:
            title = h1_text

    logger.info(f"Finished extraction on {url}: found {len(images)} images (title='{title}')")
    return {
        "title": title,
        "url": url,
        "images": images
    }
