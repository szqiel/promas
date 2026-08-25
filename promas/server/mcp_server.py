"""
Promas FastMCP Server
Exposes rich, multi-tool Model Context Protocol (MCP) endpoints with full schema descriptions and examples.
"""

from typing import List, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from promas.core.models import ProductImageResult
from promas.orchestrator import (
    discover_candidate_urls,
    get_product_images,
    scrape_single_page_url,
)

mcp = FastMCP("promas")


@mcp.tool()
async def fetch_product_images(
    query: str = Field(
        ...,
        description="The product name, model identifier, or direct e-commerce product URL to extract images for. Examples: 'iPhone 16 Pro', 'Nike Air Jordan 1 Low', 'Sony FX3 Cinema Camera', 'https://www.apple.com/iphone-16-pro/'"
    ),
    max_images: int = Field(
        default=10,
        description="Maximum number of verified, high-resolution master product images to return (1-20). Default is 10."
    ),
    site_filter: Optional[str] = Field(
        default=None,
        description="Optional domain to restrict the product search to (e.g. 'apple.com', 'nike.com', 'bhphotovideo.com', 'amazon.com')."
    ),
    no_cache: bool = Field(
        default=False,
        description="If True, bypasses the TTL disk cache and forces a live scrape."
    )
) -> ProductImageResult:
    """
    Universally extracts verified, high-resolution product photography and official sources across the web.

    USE THIS TOOL WHEN:
    - You need product photos, packshots, visual references, or master CDN assets for any physical item.
    - You want Promas to automatically discover authoritative stores, scrape candidate pages, verify images via HTTP, and deduplicate near-identical photo crops.

    EXAMPLE QUERIES:
    - fetch_product_images(query="Sony FX3 Cinema Camera", max_images=5)
    - fetch_product_images(query="Nike Air Jordan 1", site_filter="nike.com")
    - fetch_product_images(query="https://www.target.com/p/apple-iphone-16-pro/-/A-93597960")

    RETURNS:
    - ProductImageResult containing:
      - status: 'success' or 'error'
      - title: Cleaned product title
      - sources_scraped: List of retail & brand URLs visited
      - images: List of verified master-resolution image URLs (up to 2500px+)
    """
    return await get_product_images(
        query=query,
        max_images=max_images,
        site_filter=site_filter,
        use_cache=not no_cache
    )


@mcp.tool()
async def search_product_urls(
    query: str = Field(
        ...,
        description="Product name or keywords to search for. Example: 'Sony FX3 camera', 'Nike Air Jordan 1'"
    ),
    site_filter: Optional[str] = Field(
        default=None,
        description="Optional specific domain to restrict search results to (e.g. 'bhphotovideo.com', 'apple.com')"
    ),
    max_urls: int = Field(
        default=5,
        description="Maximum candidate product URLs to return (1-10). Default is 5."
    )
) -> List[str]:
    """
    Discovers and ranks candidate e-commerce product pages for a given query (Discovery only).

    USE THIS TOOL WHEN:
    - You want to find authoritative product detail pages (PDPs) across retailers without downloading or scraping images yet.
    - You want to preview which stores/URLs exist for a product before selecting one to scrape.

    EXAMPLE CALL:
    - search_product_urls(query="Sony FX3 Cinema Camera", max_urls=3)
    - search_product_urls(query="MacBook Pro M3", site_filter="apple.com")

    RETURNS:
    - A list of ranked, direct product destination URLs.
    """
    return await discover_candidate_urls(
        query=query,
        site_filter=site_filter,
        max_urls=max_urls
    )


@mcp.tool()
async def scrape_single_url(
    url: str = Field(
        ...,
        description="Direct web URL of the product detail page to extract images from. Example: 'https://www.apple.com/iphone-16-pro/' or 'https://www.bhphotovideo.com/c/product/1624226-REG/sony_ilme_fx3_fx3_cinema_line_camera.html'"
    ),
    max_images: int = Field(
        default=10,
        description="Maximum images to extract from this specific page. Default is 10."
    ),
    no_cache: bool = Field(
        default=False,
        description="If True, bypasses disk cache and scrapes live."
    )
) -> ProductImageResult:
    """
    Extracts high-resolution product imagery from a single direct product URL (Extraction only).

    USE THIS TOOL WHEN:
    - You already have an exact product URL (from search_product_urls or user input) and want to extract master photos strictly from that page.
    - Uses universal Schema.org JSON-LD, OpenGraph, dynamic JS datasets, DOM selectors, and CDN upscalers.

    EXAMPLE CALL:
    - scrape_single_url(url="https://www.apple.com/iphone-16-pro/")

    RETURNS:
    - ProductImageResult containing extracted images and metadata from the specified URL.
    """
    return await scrape_single_page_url(
        url=url,
        max_images=max_images,
        use_cache=not no_cache
    )


@mcp.tool()
async def get_product_images_tool(
    query: str,
    max_images: int = 10,
    site_filter: Optional[str] = None
) -> ProductImageResult:
    """
    Backward-compatible alias for fetch_product_images.
    """
    return await get_product_images(query=query, max_images=max_images, site_filter=site_filter)


def run_server():
    """Runs the FastMCP server on standard I/O."""
    mcp.run()


if __name__ == "__main__":
    run_server()
