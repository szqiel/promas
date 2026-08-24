"""
Unit tests for is_valid_product_image validation in promas.cdn
"""

from promas.cdn import is_valid_product_image


def test_valid_product_image_urls():
    assert is_valid_product_image("https://static.nike.com/a/images/t_PDP_1728_v1/shoe.png") is True
    assert is_valid_product_image("https://m.media-amazon.com/images/I/71Xi58F2+wL._AC_SL1500_.jpg") is True
    assert is_valid_product_image("https://target.scene7.com/is/image/Target/GUEST_7c0750b4") is True
    assert is_valid_product_image("https://cdn.shopify.com/s/files/1/shoe_2048x2048.webp") is True


def test_blocked_ui_and_logo_images():
    assert is_valid_product_image("https://example.com/images/site-logo.png") is False
    assert is_valid_product_image("https://example.com/assets/favicon.ico") is False
    assert is_valid_product_image("https://example.com/icons/star-rating.png") is False
    assert is_valid_product_image("https://example.com/track/1x1-pixel.png") is False
    assert is_valid_product_image("https://www.google.com/images/branding/googleg_128dp.png") is False


def test_rejected_transformation_fragments():
    assert is_valid_product_image("https://example.com/id/w/fl_layer_apply") is False
    assert is_valid_product_image("https://static.nike.com/a/images/c_limit") is False
    assert is_valid_product_image("https://example.com/id/w/w_1.0") is False


def test_invalid_extensions():
    assert is_valid_product_image("https://example.com/assets/icon.svg") is False
    assert is_valid_product_image("https://example.com/animation.gif") is False
    assert is_valid_product_image("") is False
    assert is_valid_product_image(None) is False  # type: ignore
