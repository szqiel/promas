"""
Promas - Universal Product Image Scraper
"""

from promas.core.models import ProductImageResult
from promas.orchestrator import get_product_images, scrape_product_images

__version__ = "1.0.0"
__all__ = ["get_product_images", "scrape_product_images", "ProductImageResult"]
