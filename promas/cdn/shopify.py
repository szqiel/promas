"""
Shopify CDN Normalizer Rule
"""

import re
from promas.cdn.registry import register_cdn


@register_cdn("cdn.shopify.com")
def upscale_shopify(url: str) -> str:
    """Upscales Shopify CDN images to master 2048px resolution."""
    return re.sub(r'_(?:\d+x\d*|\d*x\d+)\.(jpg|jpeg|png|webp)', r'_2048x2048.\1', url, flags=re.IGNORECASE)
