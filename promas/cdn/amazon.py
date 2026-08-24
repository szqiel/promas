"""
Amazon CDN Normalizer Rule
"""

import re
from promas.cdn.registry import register_cdn


@register_cdn("media-amazon.com")
@register_cdn("images-amazon.com")
@register_cdn("ssl-images-amazon.com")
def upscale_amazon(url: str) -> str:
    """Upscales Amazon product images to master 1500px resolution (._AC_SL1500_)."""
    return re.sub(r'\._[A-Z0-9_,]+_\.(jpg|jpeg|png|webp)', r'._AC_SL1500_.\1', url, flags=re.IGNORECASE)
