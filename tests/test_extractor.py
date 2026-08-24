"""
Unit tests for core/extractor.py pure parsing functions
"""

import json

from promas.core.extractor import parse_json_ld_images, parse_srcset_images


def test_parse_json_ld_single_product():
    payload = json.dumps({
        "@context": "https://schema.org",
        "@type": "Product",
        "name": "Sony FX3",
        "image": "https://static.bhphoto.com/images/images500x500/123.jpg"
    })
    images = parse_json_ld_images(payload)
    assert len(images) == 1
    assert "images2500x2500" in images[0]


def test_parse_json_ld_array_images():
    payload = json.dumps({
        "@context": "https://schema.org",
        "@type": "IndividualProduct",
        "name": "Nike Shoe",
        "image": [
            "https://static.nike.com/a/images/123/AIR+JORDAN.png",
            "https://static.nike.com/a/images/456/AIR+JORDAN+2.png"
        ]
    })
    images = parse_json_ld_images(payload)
    assert len(images) == 2


def test_parse_json_ld_graph_structure():
    payload = json.dumps({
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebSite",
                "url": "https://example.com"
            },
            {
                "@type": "Product",
                "name": "Test Item",
                "image": {
                    "@type": "ImageObject",
                    "url": "https://m.media-amazon.com/images/I/71Xi58F2+wL._AC_SL300_.jpg"
                }
            }
        ]
    })
    images = parse_json_ld_images(payload)
    assert len(images) == 1
    assert "._AC_SL1500_." in images[0]


def test_parse_srcset_standard():
    srcset = "https://example.com/item_300.jpg 300w, https://example.com/item_1200.jpg 1200w, https://example.com/item_600.jpg 600w"
    candidates = parse_srcset_images(srcset)
    assert len(candidates) > 0
    # Highest resolution should be first
    assert "item_1200.jpg" in candidates[0]


def test_parse_srcset_with_path_commas():
    srcset = "https://static.nike.com/a/images/c_limit,w_592,f_auto/t_product_v1/u_123,c_scale,fl_relative,w_1.0,h_1.0,fl_layer_apply/AIR+JORDAN.png 592w, https://static.nike.com/a/images/c_limit,w_318,f_auto/AIR+JORDAN.png 318w"
    candidates = parse_srcset_images(srcset)
    assert len(candidates) > 0
    # Does not produce fragment errors
    assert all("c_limit" not in c for c in candidates)
    assert all("fl_layer_apply" not in c for c in candidates)
