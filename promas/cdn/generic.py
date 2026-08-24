"""
Generic URL Cleaning & Image Quality Validation
"""

import re
import urllib.parse
from typing import Optional

BLOCKED_PATTERNS = [
    r'logo', r'icon', r'badge', r'avatar', r'spacer', r'pixel', r'blank',
    r'tracking', r'spinner', r'placeholder', r'arrow', r'rating', r'star',
    r'payment', r'credit-card', r'visa', r'mastercard', r'paypal', r'favicon',
    r'branding', r'googleg_', r'course', r'bundle', r'button', r'banner', r'seller',
    r'shop_snippet', r'1x1'
]
BLOCKED_REGEX = re.compile('|'.join(BLOCKED_PATTERNS), re.IGNORECASE)


def clean_generic_url(url: str, base_url: Optional[str] = None) -> Optional[str]:
    """
    Cleans raw URLs, resolves relative schemes/hosts, and unwraps Cloudflare wrappers.
    """
    if not url or not isinstance(url, str):
        return None

    url = url.strip()
    if not url or url.startswith("data:image"):
        return None

    # Handle relative URLs
    if url.startswith("//"):
        url = "https:" + url
    elif url.startswith("/"):
        if base_url:
            parsed_base = urllib.parse.urlparse(base_url)
            url = f"{parsed_base.scheme}://{parsed_base.netloc}{url}"
        else:
            return None
    elif not url.startswith("http://") and not url.startswith("https://"):
        if base_url:
            url = urllib.parse.urljoin(base_url, url)
        else:
            return None

    # Filter out SVGs and animated GIFs
    clean_path = url.split("?")[0].lower()
    if clean_path.endswith(".svg") or clean_path.endswith(".gif"):
        return None

    # Filter out generic header/footer banners
    if url.endswith("/image.png") or url.endswith("/image.jpg") or url.endswith("/image.webp"):
        return None

    # Filter out wikipedia thumbnail icons
    if "wikimedia.org" in url and ("svg.png" in url or re.search(r'/\d+px-', url)):
        return None

    # Cloudflare CDN wrapper unwrap: /cdn-cgi/image/.../(https?://...)
    cf_match = re.search(r'/cdn-cgi/image/[^/]+/(https?://.+)', url)
    if cf_match:
        url = cf_match.group(1)

    return url


def is_valid_product_image(url: str) -> bool:
    """
    Validates if an image URL represents genuine product imagery.
    """
    if not url or not isinstance(url, str):
        return False

    url_lower = url.lower()
    clean_path = url_lower.split("?")[0]

    valid_exts = (".jpg", ".jpeg", ".png", ".webp", ".avif")
    has_valid_ext = any(clean_path.endswith(ext) for ext in valid_exts)
    has_known_cdn = any(cdn in url_lower for cdn in [
        "scene7.com/is/image", "static.nike.com/a/images", "static.bhphoto.com/images",
        "media-amazon.com/images", "i.ebayimg.com", "images.stockx.com", "target.scene7.com"
    ])

    if not has_valid_ext and not has_known_cdn:
        return False

    # Reject transformation fragment artifacts
    if any(b in clean_path for b in ["fl_layer_apply", "c_limit", "fl_relative", "c_scale", "w_1.0", "h_1.0", "f_auto"]):
        if not ("static.nike.com/a/images/t_PDP_1728_v1" in url and clean_path.endswith(valid_exts)):
            return False

    # Check for blocked patterns anywhere in URL
    if BLOCKED_REGEX.search(url_lower):
        return False

    # Check for tiny dimension parameters
    if re.search(r'[?&](?:w|width|h|height)=(?:[1-9][0-9]?|1[0-4][0-9])(?:&|$)', url_lower):
        return False

    return True
