"""
Promas TTL-Based Cache Layer
Provides persistent query & URL caching using diskcache to reduce duplicate scraping and avoid rate limits.
"""

import hashlib
from pathlib import Path
from typing import Optional

from diskcache import Cache
from loguru import logger

from promas.core.config import settings
from promas.core.models import ProductImageResult

# Cache directory from settings or user cache
_cache_path = settings.cache_dir or str(Path.home() / ".cache" / "promas")

try:
    _cache = Cache(_cache_path) if settings.cache_enabled else None
except Exception as e:
    logger.warning(f"Could not initialize diskcache at {_cache_path}: {e}. Caching disabled.")
    _cache = None


def make_cache_key(query: str, max_images: int, site_filter: Optional[str] = None) -> str:
    """Generates a normalized deterministic cache key."""
    norm_q = query.strip().lower()
    norm_site = site_filter.strip().lower() if site_filter else ""
    raw = f"{norm_q}::{max_images}::{norm_site}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def get_cached_result(
    query: str,
    max_images: int = 10,
    site_filter: Optional[str] = None
) -> Optional[ProductImageResult]:
    """Retrieves cached ProductImageResult if valid and unexpired."""
    if _cache is None or not settings.cache_enabled:
        return None

    key = make_cache_key(query, max_images, site_filter)
    try:
        data = _cache.get(key)
        if data:
            logger.debug(f"Cache HIT for query='{query}' (key={key[:8]})")
            return ProductImageResult.model_validate_json(data)
        logger.debug(f"Cache MISS for query='{query}'")
    except Exception as e:
        logger.debug(f"Cache read error: {e}")
    return None


def set_cached_result(
    query: str,
    result: ProductImageResult,
    max_images: int = 10,
    site_filter: Optional[str] = None,
    ttl: Optional[int] = None
) -> None:
    """Saves ProductImageResult into cache with specified TTL in seconds."""
    if _cache is None or not settings.cache_enabled or result.status != "success":
        return

    key = make_cache_key(query, max_images, site_filter)
    expire_ttl = ttl if ttl is not None else settings.cache_ttl_seconds
    try:
        _cache.set(key, result.model_dump_json(), expire=expire_ttl)
        logger.debug(f"Cached result for query='{query}' with TTL={expire_ttl}s")
    except Exception as e:
        logger.debug(f"Cache write error: {e}")


def clear_cache() -> None:
    """Clears all cached entries."""
    if _cache is not None:
        _cache.clear()
        logger.info("Promas disk cache cleared.")
