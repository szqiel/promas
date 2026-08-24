"""
Promas CDN Package
Auto-imports all registered CDN upscaler plugins.
"""

from promas.cdn import (
    amazon as amazon,
)
from promas.cdn import (
    bh as bh,
)
from promas.cdn import (
    ebay as ebay,
)
from promas.cdn import (
    generic as generic,
)
from promas.cdn import (
    imgix as imgix,
)
from promas.cdn import (
    nike as nike,
)
from promas.cdn import (
    scene7 as scene7,
)
from promas.cdn import (
    shopify as shopify,
)
from promas.cdn.registry import (
    CDN_RULES,
    clean_and_upscale_image_url,
    is_valid_product_image,
    register_cdn,
)

__all__ = [
    "CDN_RULES",
    "register_cdn",
    "clean_and_upscale_image_url",
    "is_valid_product_image",
    "shopify",
    "nike",
    "amazon",
    "ebay",
    "bh",
    "scene7",
    "imgix",
    "generic",
]
