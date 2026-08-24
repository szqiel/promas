"""
Shopify CDN Normalizer & Master Upscaler
"""

import re
from typing import Optional


def normalize_shopify_url(url: str) -> Optional[str]:
    """
    Upscales Shopify CDN images to master 2048px resolution.
    """
    if "cdn.shopify.com" not in url:
        return url

    return re.sub(r'_(?:\d+x\d*|\d*x\d+)\.(jpg|jpeg|png|webp)', r'_2048x2048.\1', url, flags=re.IGNORECASE)
