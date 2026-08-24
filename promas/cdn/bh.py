"""
B&H Photo CDN Normalizer & Master Upscaler
"""

import re
from typing import Optional


def normalize_bh_url(url: str) -> Optional[str]:
    """
    Upscales B&H Photo CDN images to master 2500px resolution.
    """
    if not ("bhphoto.com" in url or "static.bhphoto.com" in url):
        return url

    url = url.replace("/images/smallimages/", "/images/images2500x2500/")
    url = url.replace("/multiple_images/thumbnails/", "/multiple_images/images500x500/")
    url = url.replace("/images/thumbnails/", "/images/images500x500/")
    url = re.sub(r'/images(345x345|500x500|150x150)/', '/images2500x2500/', url)
    return url
