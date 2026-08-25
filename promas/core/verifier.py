"""
Lightweight Image Verifier & Perceptual-Hash Deduplication Layer
Validates Content-Type, real pixel dimensions, and eliminates near-identical photo crops using perceptual hashing.
"""

import io
from typing import List, Optional

import httpx
import imagehash
from loguru import logger
from PIL import Image

from promas.core.config import settings


class VerifiedImage:
    """Represents a validated image with dimensions and perceptual hash."""
    def __init__(self, url: str, width: int, height: int, phash: Optional[imagehash.ImageHash]):
        self.url = url
        self.width = width
        self.height = height
        self.phash = phash
        self.total_pixels = width * height


async def verify_image_url(
    client: httpx.AsyncClient,
    url: str
) -> Optional[VerifiedImage]:
    """
    Asynchronously checks that URL returns a valid image with adequate dimensions.
    Computes perceptual hash for cross-source deduplication.
    """
    headers = {
        "User-Agent": settings.user_agent,
        "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8"
    }

    try:
        # Fetch image bytes (using streaming GET up to 1MB or full image)
        resp = await client.get(url, headers=headers, follow_redirects=True, timeout=settings.timeout_http_seconds)
        if resp.status_code != 200:
            logger.debug(f"Image verification failed: HTTP {resp.status_code} on {url[:80]}")
            return None

        # Verify Content-Type
        content_type = resp.headers.get("content-type", "").lower()
        if not content_type.startswith("image/"):
            logger.debug(f"Rejected non-image Content-Type '{content_type}' on {url[:80]}")
            return None

        content = resp.content
        if len(content) < settings.min_image_bytes:
            logger.debug(f"Rejected tiny tracking asset ({len(content)} bytes) on {url[:80]}")
            return None

        # Parse with PIL to verify valid image format and extract real pixel dimensions
        with Image.open(io.BytesIO(content)) as im:
            width, height = im.size
            if width < settings.min_image_dimension or height < settings.min_image_dimension:
                logger.debug(f"Rejected image with tiny dimensions ({width}x{height}) on {url[:80]}")
                return None

            # Compute perceptual hash
            img_phash = None
            if settings.enable_perceptual_dedup:
                try:
                    img_phash = imagehash.phash(im)
                except Exception as ex:
                    logger.debug(f"Could not calculate pHash on {url[:80]}: {ex}")

            logger.debug(f"Verified image: {width}x{height} ({len(content)} bytes, phash={img_phash}) on {url[:80]}")
            return VerifiedImage(url=url, width=width, height=height, phash=img_phash)

    except Exception as e:
        logger.debug(f"Image verification exception on {url[:80]}: {e}")
        return None


def deduplicate_by_phash(
    verified_images: List[VerifiedImage],
    hamming_threshold: int = 4
) -> List[str]:
    """
    Removes near-identical crops/duplicates based on perceptual hash Hamming distance.
    Preserves the higher-resolution version when near-duplicates are detected.
    """
    if not settings.enable_perceptual_dedup:
        return [img.url for img in verified_images]

    # Sort candidates by total pixels descending (so higher resolution images take priority)
    sorted_images = sorted(verified_images, key=lambda x: x.total_pixels, reverse=True)
    kept_images: List[VerifiedImage] = []

    for cand in sorted_images:
        if cand.phash is None:
            kept_images.append(cand)
            continue

        is_duplicate = False
        for kept in kept_images:
            if kept.phash is not None:
                distance = cand.phash - kept.phash  # Hamming distance
                if distance <= hamming_threshold:
                    logger.debug(
                        f"Perceptual duplicate detected (Hamming distance={distance}): "
                        f"Dropping {cand.url[:60]} in favor of {kept.url[:60]}"
                    )
                    is_duplicate = True
                    break

        if not is_duplicate:
            kept_images.append(cand)

    return [img.url for img in kept_images]


async def verify_and_deduplicate_candidate_images(
    candidate_urls: List[str]
) -> List[str]:
    """
    Concurrently verifies candidate URLs, filters out broken/non-image assets,
    and deduplicates near-identical photos via perceptual hashing.
    """
    if not candidate_urls:
        return []

    if not settings.enable_image_verification:
        return candidate_urls

    logger.info(f"Verifying {len(candidate_urls)} candidate image URLs via async HTTP/pHash...")
    verified: List[VerifiedImage] = []

    async with httpx.AsyncClient(timeout=settings.timeout_http_seconds) as client:
        # Check concurrently
        import asyncio
        tasks = [verify_image_url(client, url) for url in candidate_urls]
        results = await asyncio.gather(*tasks)

        for res in results:
            if res is not None:
                verified.append(res)

    logger.info(f"Verification passed for {len(verified)} / {len(candidate_urls)} images")

    # If verification filtered everything out (e.g. strict WAF on direct image download), fallback gracefully
    if not verified and candidate_urls:
        logger.warning("All direct image HEAD/GET checks were blocked; falling back to candidate URLs")
        return candidate_urls

    final_deduped_urls = deduplicate_by_phash(verified, settings.phash_hamming_threshold)
    logger.info(f"Perceptual deduplication resulted in {len(final_deduped_urls)} unique master photos")
    return final_deduped_urls
