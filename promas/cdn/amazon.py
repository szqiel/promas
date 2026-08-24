"""
Amazon CDN Normalizer & Master Upscaler
"""

import re
from typing import Optional


def normalize_amazon_url(url: str) -> Optional[str]:
    """
    Upscales Amazon product images to master 1500px resolution (._AC_SL1500_).
    """
    if not any(k in url for k in ["media-amazon.com", "images-amazon.com", "ssl-images-amazon.com"]):
        return url

    return re.sub(r'\._[A-Z0-9_,]+_\.(jpg|jpeg|png|webp)', r'._AC_SL1500_.\1', url, flags=re.IGNORECASE)
