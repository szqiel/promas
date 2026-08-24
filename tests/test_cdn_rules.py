"""
Unit tests for CDN upscaler rules in promas.cdn
"""

from promas.cdn import clean_and_upscale_image_url


def test_shopify_cdn_upscaling():
    raw_url = "https://cdn.shopify.com/s/files/1/0001/products/shoe_300x300.jpg?v=123"
    upscaled = clean_and_upscale_image_url(raw_url)
    assert upscaled is not None
    assert "_2048x2048.jpg" in upscaled


def test_nike_cdn_upscaling():
    raw_url = "https://static.nike.com/a/images/c_limit,w_592,f_auto/t_product_v1/u_126ab356,c_scale,fl_relative,w_1.0,h_1.0,fl_layer_apply/67a4da17-e875-4818-8ef0-13badbe30e80/AIR+JORDAN+1+LOW.png"
    upscaled = clean_and_upscale_image_url(raw_url)
    assert upscaled is not None
    assert "t_PDP_1728_v1" in upscaled
    assert "67a4da17-e875-4818-8ef0-13badbe30e80" in upscaled
    assert "AIR+JORDAN+1+LOW.png" in upscaled


def test_amazon_cdn_upscaling():
    raw_url = "https://m.media-amazon.com/images/I/71Xi58F2+wL._AC_SL300_.jpg"
    upscaled = clean_and_upscale_image_url(raw_url)
    assert upscaled is not None
    assert "._AC_SL1500_.jpg" in upscaled


def test_ebay_cdn_upscaling():
    raw_url = "https://i.ebayimg.com/images/g/abc123/s-l300.jpg"
    upscaled = clean_and_upscale_image_url(raw_url)
    assert upscaled is not None
    assert "/s-l1600.jpg" in upscaled


def test_bh_cdn_upscaling():
    raw_url = "https://static.bhphoto.com/images/images500x500/1614080143_1624226.jpg"
    upscaled = clean_and_upscale_image_url(raw_url)
    assert upscaled is not None
    assert "/images2500x2500/" in upscaled


def test_scene7_cdn_upscaling():
    raw_url = "https://target.scene7.com/is/image/Target/GUEST_7c0750b4?wid=800&hei=800&qlt=80"
    upscaled = clean_and_upscale_image_url(raw_url)
    assert upscaled is not None
    assert upscaled == "https://target.scene7.com/is/image/Target/GUEST_7c0750b4"


def test_imgix_cloudinary_upscaling():
    raw_imgix = "https://example.imgix.net/product.jpg?w=300&h=300"
    upscaled_imgix = clean_and_upscale_image_url(raw_imgix)
    assert upscaled_imgix is not None
    assert "w=2000" in upscaled_imgix

    raw_cloudinary = "https://res.cloudinary.com/demo/image/upload/w_300,h_300/sample.jpg"
    upscaled_cloud = clean_and_upscale_image_url(raw_cloudinary)
    assert upscaled_cloud is not None
    assert "/w_2000,h_2000/" in upscaled_cloud


def test_cloudflare_unwrap():
    cf_wrapped = "https://example.com/cdn-cgi/image/fit=scale-down,width=500/https://static.bhphoto.com/images/images500x500/123_456.jpg"
    upscaled = clean_and_upscale_image_url(cf_wrapped)
    assert upscaled is not None
    assert "/cdn-cgi/image/" not in upscaled
    assert "https://static.bhphoto.com/images/images2500x2500/123_456.jpg" == upscaled
