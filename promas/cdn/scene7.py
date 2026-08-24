"""
Adobe Scene7 CDN Normalizer (Target, Best Buy, Home Depot)
"""

from typing import Optional


def normalize_scene7_url(url: str) -> Optional[str]:
    """
    Unwraps Scene7 CDN URLs to unconstrained master assets.
    """
    if "scene7.com" not in url:
        return url

    return url.split("?")[0]
