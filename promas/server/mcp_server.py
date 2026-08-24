"""
Promas FastMCP Server
Exposes Promas product image extraction tools over Model Context Protocol (MCP).
"""

from typing import Optional

from mcp.server.fastmcp import FastMCP

from promas.core.models import ProductImageResult
from promas.orchestrator import get_product_images

mcp = FastMCP("promas")


@mcp.tool()
async def fetch_product_images(
    query: str,
    max_images: int = 10,
    site_filter: Optional[str] = None
) -> ProductImageResult:
    """
    Universally retrieves high-resolution product imagery and official product links from across the web.

    Args:
        query: Product name/model (e.g. 'Sony FX5', 'Marlboro Cigarette', 'Le Minerale') OR a direct product URL
        max_images: Maximum number of images to return (default: 10)
        site_filter: Optional specific domain to search (e.g. 'apple.com', 'bhphotovideo.com', 'amazon.com')
    """
    return await get_product_images(query=query, max_images=max_images, site_filter=site_filter)


@mcp.tool()
async def get_product_images_tool(
    query: str,
    max_images: int = 10,
    site_filter: Optional[str] = None
) -> ProductImageResult:
    """
    Alias to fetch high-resolution product images.

    Args:
        query: Product name/model OR direct product URL
        max_images: Maximum images to return (default: 10)
        site_filter: Optional domain filter
    """
    return await get_product_images(query=query, max_images=max_images, site_filter=site_filter)


def run_server():
    mcp.run()


if __name__ == "__main__":
    run_server()
