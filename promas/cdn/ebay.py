"""
eBay CDN Normalizer Rule
"""

import re
from promas.cdn.registry import register_cdn


@register_cdn("i.ebayimg.com")
def upscale_ebay(url: str) -> str:
    """Upscales eBay gallery images to master 1600px resolution (/s-l1600.)."""
    return re.sub(r'/s-l\d+\.(jpg|jpeg|png|webp)', r'/s-l1600.\1', url, flags=re.IGNORECASE)
