"""
Unit tests for promas.core.rate_limiter domain rate limiting
"""

import pytest

from promas.core.rate_limiter import DomainRateLimiter


def test_domain_extraction():
    limiter = DomainRateLimiter()
    assert limiter._extract_domain("https://www.apple.com/shop/buy-iphone") == "apple.com"
    assert limiter._extract_domain("https://m.media-amazon.com/images/I/123.jpg") == "media-amazon.com"
    assert limiter._extract_domain("https://target.scene7.com/is/image/Target/123") == "target.scene7.com"
    assert limiter._extract_domain("https://static.nike.com/a/images/123.jpg") == "static.nike.com"


@pytest.mark.asyncio
async def test_domain_rate_limiter_acquire():
    limiter = DomainRateLimiter(global_concurrency=2, per_domain_concurrency=1, domain_delay_seconds=0.01)
    url = "https://www.apple.com/iphone"

    async with limiter.acquire(url):
        assert limiter.global_semaphore._value < 2
