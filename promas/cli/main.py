"""
Promas Command-Line Interface
"""

import argparse
import asyncio

from promas.core.config import settings
from promas.orchestrator import get_product_images


async def async_main():
    parser = argparse.ArgumentParser(description="Promas: Universal Product Image Scraper CLI")
    parser.add_argument("query", nargs="?", default="iPhone 16 Pro", help="Product query or direct URL")
    parser.add_argument("--max-images", type=int, default=10, help="Maximum images to return (default: 10)")
    parser.add_argument("--site", default=None, help="Optional site domain filter (e.g. apple.com, nike.com)")
    parser.add_argument("--no-cache", action="store_true", help="Bypass diskcache and force live scrape")
    parser.add_argument("--no-verify", action="store_true", help="Disable async image verification and pHash dedup")
    args = parser.parse_args()

    if args.no_verify:
        settings.enable_image_verification = False
        settings.enable_perceptual_dedup = False

    use_cache = not args.no_cache

    print(f"[*] Promas querying: '{args.query}' (max: {args.max_images}, site: {args.site}, cache: {use_cache})...")
    result = await get_product_images(
        query=args.query,
        max_images=args.max_images,
        site_filter=args.site,
        use_cache=use_cache
    )
    print(result.model_dump_json(indent=2))


def main():
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
