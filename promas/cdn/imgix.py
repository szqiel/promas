"""
Imgix, Cloudinary, and Fastly Dynamic CDN Normalizer Rule
"""

import re

from promas.cdn.registry import register_cdn


@register_cdn("imgix.net")
@register_cdn("cloudinary.com")
@register_cdn("fastly.net")
def upscale_imgix_cloudinary(url: str) -> str:
    """Upscales Imgix, Cloudinary, and Fastly dynamic resizing parameters."""
    url = re.sub(r'([?&])w=\d+', r'\1w=2000', url)
    url = re.sub(r'([?&])width=\d+', r'\1width=2000', url)
    return re.sub(r'/w_\d+,h_\d+/', r'/w_2000,h_2000/', url)
