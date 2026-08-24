"""
Nike CDN Normalizer & Master Upscaler
"""

import re
from typing import Optional


def normalize_nike_url(url: str) -> Optional[str]:
    """
    Upscales Nike static CDN images to master 1728px resolution (t_PDP_1728_v1).
    """
    if "static.nike.com" not in url:
        return url

    nike_match = re.search(r'static\.nike\.com/a/images/(?:.+/)?([0-9a-fA-F\-]{36})/([^\s/]+\.(?:png|jpg|jpeg|webp))', url)
    if nike_match:
        uid = nike_match.group(1)
        fname = nike_match.group(2)
        return f"https://static.nike.com/a/images/t_PDP_1728_v1/f_auto,q_auto:eco/{uid}/{fname}"

    url = re.sub(r'/(?:t_[^/]+|w_\d+[^/]*|c_limit[^/]*)/', r'/t_PDP_1728_v1/f_auto,q_auto:eco/', url)
    return url
