"""
Unit tests for promas.core.verifier (verification & perceptual deduplication)
"""

import imagehash
from PIL import Image, ImageDraw

from promas.core.config import PromasSettings
from promas.core.verifier import VerifiedImage, deduplicate_by_phash


def test_settings_defaults_and_override():
    custom_settings = PromasSettings(
        global_concurrency=10,
        cache_ttl_seconds=3600,
        enable_image_verification=False
    )
    assert custom_settings.global_concurrency == 10
    assert custom_settings.cache_ttl_seconds == 3600
    assert custom_settings.enable_image_verification is False


def test_deduplicate_by_phash_near_identical():
    # Create test image and its resized / upscaled version
    img1 = Image.new("RGB", (300, 300), color="white")
    d1 = ImageDraw.Draw(img1)
    d1.rectangle([50, 50, 250, 250], fill="black")
    d1.line([0, 0, 300, 300], fill="red", width=5)

    # Upscaled version of the same image
    img2 = img1.resize((1000, 1000), Image.Resampling.BILINEAR)

    h1 = imagehash.phash(img1)
    h2 = imagehash.phash(img2)

    # Identical resized image yields distance 0
    assert (h1 - h2) == 0

    v1 = VerifiedImage(url="https://example.com/low_res.jpg", width=300, height=300, phash=h1)
    v2 = VerifiedImage(url="https://example.com/high_res.jpg", width=1000, height=1000, phash=h2)

    # Should keep only the higher-resolution version (1000x1000)
    deduped = deduplicate_by_phash([v1, v2], hamming_threshold=4)
    assert len(deduped) == 1
    assert deduped[0] == "https://example.com/high_res.jpg"


def test_deduplicate_by_phash_distinct_images():
    # Create two distinct images with different visual features
    img1 = Image.new("RGB", (300, 300), color="white")
    d1 = ImageDraw.Draw(img1)
    d1.rectangle([20, 20, 150, 280], fill="black")

    img2 = Image.new("RGB", (300, 300), color="white")
    d2 = ImageDraw.Draw(img2)
    d2.ellipse([100, 20, 280, 200], fill="black")
    d2.line([0, 300, 300, 0], fill="black", width=10)

    h1 = imagehash.phash(img1)
    h2 = imagehash.phash(img2)

    assert (h1 - h2) > 4

    v1 = VerifiedImage(url="https://example.com/photo1.jpg", width=500, height=500, phash=h1)
    v2 = VerifiedImage(url="https://example.com/photo2.jpg", width=500, height=500, phash=h2)

    deduped = deduplicate_by_phash([v1, v2], hamming_threshold=4)
    assert len(deduped) == 2
