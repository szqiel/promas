"""
Promas CDN Package
Auto-imports all registered CDN upscaler plugins.
"""

from promas.cdn.registry import (
    CDN_RULES,
    register_cdn,
    clean_and_upscale_image_url,
    is_valid_product_image,
)

# Import all CDN rules to execute their @register_cdn decorators
import promas.cdn.shopify
import promas.cdn.nike
import promas.cdn.amazon
import promas.cdn.ebay
import promas.cdn.bh
import promas.cdn.scene7
import promas.cdn.imgix

__all__ = [
    "CDN_RULES",
    "register_cdn",
    "clean_and_upscale_image_url",
    "is_valid_product_image",
]
