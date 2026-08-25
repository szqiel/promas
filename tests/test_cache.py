"""
Unit tests for promas.core.cache TTL caching layer
"""

import time

from promas.core.cache import clear_cache, get_cached_result, make_cache_key, set_cached_result
from promas.core.models import ProductImageResult


def test_cache_key_generation():
    key1 = make_cache_key("iPhone 16 Pro", 10, None)
    key2 = make_cache_key("iphone 16 pro  ", 10, None)
    key3 = make_cache_key("iPhone 16 Pro", 5, None)
    key4 = make_cache_key("iPhone 16 Pro", 10, "apple.com")

    assert key1 == key2  # Normalized case and whitespace
    assert key1 != key3  # Different max_images
    assert key1 != key4  # Different site_filter


def test_set_and_get_cached_result():
    clear_cache()
    query = "Test Product XYZ"
    sample_result = ProductImageResult(
        status="success",
        query=query,
        title="Test Title",
        sources_scraped=["https://example.com/item"],
        images=["https://example.com/image_2000x2000.jpg"]
    )

    # Initially None
    assert get_cached_result(query, 10, None) is None

    # Set in cache
    set_cached_result(query, sample_result, max_images=10, site_filter=None, ttl=60)

    # Cache HIT
    cached = get_cached_result(query, 10, None)
    assert cached is not None
    assert cached.query == query
    assert len(cached.images) == 1
    assert cached.images[0] == "https://example.com/image_2000x2000.jpg"


def test_cache_ttl_expiration():
    clear_cache()
    query = "Expiring Product"
    sample_result = ProductImageResult(
        status="success",
        query=query,
        title="Expiring Title",
        sources_scraped=[],
        images=["https://example.com/expiring.jpg"]
    )

    # 1 second TTL
    set_cached_result(query, sample_result, max_images=10, site_filter=None, ttl=1)
    assert get_cached_result(query, 10, None) is not None

    time.sleep(1.1)
    # Expired
    assert get_cached_result(query, 10, None) is None
