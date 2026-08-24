"""
Adobe Scene7 CDN Normalizer Rule (Target, Best Buy, Home Depot)
"""

from promas.cdn.registry import register_cdn


@register_cdn("scene7.com")
def upscale_scene7(url: str) -> str:
    """Unwraps Scene7 CDN URLs to unconstrained master assets."""
    return url.split("?")[0]
