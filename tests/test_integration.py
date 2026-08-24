"""
Golden Integration Tests (Canary tests against live sites)
Skipped by default in CI; run with pytest --run-integration
"""

import pytest

from promas.orchestrator import get_product_images


@pytest.mark.integration
@pytest.mark.asyncio
async def test_live_direct_apple_url():
    url = "https://www.apple.com/iphone-16-pro/"
    result = await get_product_images(query=url, max_images=5)
    assert result.status == "success"
    assert len(result.images) > 0
    assert any("apple.com" in img for img in result.images)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_live_search_sony_gear():
    result = await get_product_images(query="Sony FX3 Cinema Camera", max_images=5)
    assert result.status == "success"
    assert len(result.images) > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_live_search_nike_shoes():
    result = await get_product_images(query="Nike Air Jordan 1", max_images=5)
    assert result.status == "success"
    assert len(result.images) > 0
