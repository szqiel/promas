"""
Unit tests for core/discovery.py pure scoring functions
"""

from promas.core.discovery import score_product_url


def test_score_product_url_boosts_retailers():
    score = score_product_url("https://www.apple.com/shop/buy-iphone/iphone-16", ["iphone", "16"])
    assert score > 30

    bh_score = score_product_url("https://www.bhphotovideo.com/c/product/123/sony.html", ["sony", "fx3"])
    assert bh_score > 30


def test_score_product_url_discards_non_retail():
    assert score_product_url("https://www.google.com/search?q=test", ["test"]) < 0
    assert score_product_url("https://en.wikipedia.org/wiki/IPhone", ["iphone"]) < 0
    assert score_product_url("https://theperfectfrench.com/grammar/le-la-les", ["le", "minerale"]) < 0
    assert score_product_url("https://wikileaks.org/something", ["marlboro"]) < 0


def test_score_product_url_keywords():
    score_with_kw = score_product_url("https://example.com/product/sony-fx3-camera", ["sony", "fx3", "camera"])
    score_no_kw = score_product_url("https://example.com/product/random-item", ["sony", "fx3", "camera"])
    assert score_with_kw > score_no_kw
