"""
CDN Normalizer Registry
Plugin-style dispatcher mapping domains/patterns to dedicated upscaler functions.
"""

from typing import Optional, Callable, Dict
from promas.cdn.generic import clean_generic_url, is_valid_product_image
from promas.cdn.nike import normalize_nike_url
from promas.cdn.shopify import normalize_shopify_url
from promas.cdn.amazon import normalize_amazon_url
from promas.cdn.ebay import normalize_ebay_url
from promas.cdn.bh import normalize_bh_url
from promas.cdn.scene7 import normalize_scene7_url


# Domain / Pattern -> Normalizer Function
NORMALIZERS: Dict[str, Callable[[str], Optional[str]]] = {
    "static.nike.com": normalize_nike_url,
    "cdn.shopify.com": normalize_shopify_url,
    "media-amazon.com": normalize_amazon_url,
    "images-amazon.com": normalize_amazon_url,
    "ssl-images-amazon.com": normalize_amazon_url,
    "i.ebayimg.com": normalize_ebay_url,
    "bhphoto.com": normalize_bh_url,
    "static.bhphoto.com": normalize_bh_url,
    "scene7.com": normalize_scene7_url,
}


def clean_and_upscale_image_url(url: str, base_url: Optional[str] = None) -> Optional[str]:
    """
    Cleans raw URL and applies domain-specific CDN upscaling.
    """
    cleaned = clean_generic_url(url, base_url)
    if not cleaned:
        return None

    # Check for matched domain normalizer
    for domain_pattern, normalizer_fn in NORMALIZERS.items():
        if domain_pattern in cleaned:
            cleaned = normalizer_fn(cleaned)
            break

    return cleaned


__all__ = ["clean_and_upscale_image_url", "is_valid_product_image", "NORMALIZERS"]
