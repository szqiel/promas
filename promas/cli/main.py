"""
Promas Command-Line Interface
"""

import argparse
import asyncio

from promas.orchestrator import get_product_images


async def async_main():
    parser = argparse.ArgumentParser(description="Promas: Universal Product Image Scraper CLI")
    parser.add_argument("query", nargs="?", default="iPhone 16 Pro", help="Product query or direct URL")
    parser.add_argument("--max-images", type=int, default=10, help="Maximum images to return (default: 10)")
    parser.add_argument("--site", default=None, help="Optional site domain filter (e.g. apple.com, nike.com)")
    args = parser.parse_args()

    print(f"[*] Promas querying: '{args.query}' (max: {args.max_images}, site: {args.site})...")
    result = await get_product_images(query=args.query, max_images=args.max_images, site_filter=args.site)
    print(result.model_dump_json(indent=2))


def main():
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
