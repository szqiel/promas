"""
eBay CDN Normalizer & Master Upscaler
"""

import re
from typing import Optional


def normalize_ebay_url(url: str) -> Optional[str]:
    """
    Upscales eBay gallery images to master 1600px resolution (/s-l1600.).
    """
    if "i.ebayimg.com" not in url:
        return url

    return re.sub(r'/s-l\d+\.(jpg|jpeg|png|webp)', r'/s-l1600.\1', url, flags=re.IGNORECASE)
