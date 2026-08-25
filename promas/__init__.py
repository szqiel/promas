"""
Promas - Universal Product Image Scraper
"""

from promas.core.config import settings
from promas.core.models import ProductImageResult
from promas.orchestrator import (
    discover_candidate_urls,
    get_product_images,
    scrape_product_images,
    scrape_single_page_url,
)

__version__ = "1.0.0"
__all__ = [
    "get_product_images",
    "scrape_product_images",
    "discover_candidate_urls",
    "scrape_single_page_url",
    "ProductImageResult",
    "settings",
]
