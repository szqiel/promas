"""
Unit tests for promas.server.mcp_server tool definitions and metadata
"""

from promas.server.mcp_server import (
    fetch_product_images,
    get_product_images_tool,
    mcp,
    scrape_single_url,
    search_product_urls,
)


def test_mcp_tool_registration():
    # Verify tools are registered on FastMCP instance
    tool_names = [t.name for t in mcp._tool_manager.list_tools()]
    assert "fetch_product_images" in tool_names
    assert "search_product_urls" in tool_names
    assert "scrape_single_url" in tool_names
    assert "get_product_images_tool" in tool_names


def test_mcp_tool_docstrings_and_descriptions():
    # Verify rich descriptions and examples are present in docstrings for agent inspection
    assert "Universally extracts" in (fetch_product_images.__doc__ or "")
    assert "EXAMPLE QUERIES" in (fetch_product_images.__doc__ or "")

    assert "Discovery only" in (search_product_urls.__doc__ or "")
    assert "EXAMPLE CALL" in (search_product_urls.__doc__ or "")

    assert "Extraction only" in (scrape_single_url.__doc__ or "")
    assert "RETURNS" in (scrape_single_url.__doc__ or "")
    assert get_product_images_tool is not None
