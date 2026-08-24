"""
Nike CDN Normalizer Rule
"""

import re

from promas.cdn.registry import register_cdn


@register_cdn("static.nike.com")
def upscale_nike(url: str) -> str:
    """Upscales Nike static CDN images to master 1728px resolution (t_PDP_1728_v1)."""
    # 1. Matches /<id>/<filename.ext>
    match_with_id = re.search(r'static\.nike\.com/a/images/(?:.+/)?([0-9a-fA-F\-]{8,36})/([^\s/]+\.(?:png|jpg|jpeg|webp))', url)
    if match_with_id:
        uid = match_with_id.group(1)
        fname = match_with_id.group(2)
        if not any(t in uid for t in ["c_limit", "w_", "t_product", "fl_relative", "c_scale", "f_auto"]):
            return f"https://static.nike.com/a/images/t_PDP_1728_v1/f_auto,q_auto:eco/{uid}/{fname}"

    # 2. Fallback matches /<filename.ext>
    match_file = re.search(r'static\.nike\.com/a/images/(?:.+/)?([^\s/]+\.(?:png|jpg|jpeg|webp))', url)
    if match_file:
        fname = match_file.group(1)
        return f"https://static.nike.com/a/images/t_PDP_1728_v1/f_auto,q_auto:eco/{fname}"

    return url
