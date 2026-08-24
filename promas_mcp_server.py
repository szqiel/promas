"""
Promas (Product Image Scraper) - FastMCP Server
Model Context Protocol (MCP) Server for AI agents to retrieve high-resolution product imagery.
"""

from mcp.server.fastmcp import FastMCP
from promas import scrape_product_images, ProductImageResult

mcp = FastMCP("promas")


@mcp.tool()
async def get_product_images(query: str, source: str = "bh") -> ProductImageResult:
    """
    Searches e-commerce platforms (B&H Photo, etc.) for a product and returns high-resolution image links and product metadata.

    Args:
        query: Name or model of the product (e.g. 'Sony FX3 Cinema Camera', 'Godox TT600')
        source: E-commerce platform to search (default: 'bh')
    """
    return await scrape_product_images(query=query, source=source)


@mcp.tool()
async def scrape_product_images_tool(query: str, source: str = "bh") -> ProductImageResult:
    """
    Alternative alias to scrape high-resolution product images.

    Args:
        query: Name or model of the product
        source: E-commerce platform to search (default: 'bh')
    """
    return await scrape_product_images(query=query, source=source)


if __name__ == "__main__":
    mcp.run()
