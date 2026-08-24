"""
CDN Normalizer Registry
Plugin-style decorator pattern mapping domain strings to dedicated upscaler functions.
"""

from typing import Optional, Callable, Dict
from promas.cdn.generic import clean_generic_url, is_valid_product_image

# Global Registry: domain pattern -> normalizer function
CDN_RULES: Dict[str, Callable[[str], str]] = {}


def register_cdn(domain: str):
    r"""
    Decorator to register a CDN domain normalizer rule.
    Example:
        @register_cdn("cdn.shopify.com")
        def upscale_shopify(url: str) -> str:
            return re.sub(r'_(\d+x\d*|\d*x\d+)\.', '_2048x2048.', url)
    """
    def wrap(fn: Callable[[str], str]) -> Callable[[str], str]:
        CDN_RULES[domain] = fn
        return fn
    return wrap


def clean_and_upscale_image_url(url: str, base_url: Optional[str] = None) -> Optional[str]:
    """
    Cleans raw URL and dispatches to registered CDN normalizer rule if matched.
    """
    cleaned = clean_generic_url(url, base_url)
    if not cleaned:
        return None

    # Check registered CDN rules
    for domain_pattern, normalizer_fn in CDN_RULES.items():
        if domain_pattern in cleaned:
            cleaned = normalizer_fn(cleaned)
            break

    return cleaned


__all__ = [
    "CDN_RULES",
    "register_cdn",
    "clean_and_upscale_image_url",
    "is_valid_product_image",
]
