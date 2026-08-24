"""
B&H Photo CDN Normalizer Rule
"""

import re
from promas.cdn.registry import register_cdn


@register_cdn("static.bhphoto.com")
@register_cdn("bhphoto.com")
def upscale_bh(url: str) -> str:
    """Upscales B&H Photo CDN images to master 2500px resolution."""
    url = url.replace("/images/smallimages/", "/images/images2500x2500/")
    url = url.replace("/multiple_images/thumbnails/", "/multiple_images/images500x500/")
    url = url.replace("/images/thumbnails/", "/images/images500x500/")
    return re.sub(r'/images(345x345|500x500|150x150)/', '/images2500x2500/', url)
