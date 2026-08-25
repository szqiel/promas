"""
Promas Centralized Configuration
Managed with pydantic-settings; overridable via environment variables (PROMAS_*) or .env file.
"""

from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class PromasSettings(BaseSettings):
    """
    Central configuration for Promas scrapers, concurrency, caching, and verifications.
    """
    model_config = SettingsConfigDict(
        env_prefix="PROMAS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Browser Emulation & User Agent
    user_agent: str = Field(
        default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        description="Browser user agent string"
    )
    viewport_width: int = 1920
    viewport_height: int = 1080

    # Timeouts
    timeout_navigation_ms: int = 25000
    timeout_search_ms: int = 15000
    timeout_http_seconds: float = 8.0

    # Concurrency & Rate Limiting
    global_concurrency: int = 3
    per_domain_concurrency: int = 1
    domain_delay_seconds: float = 0.5

    # Caching
    cache_enabled: bool = True
    cache_ttl_seconds: int = 86400  # 24 hours
    cache_dir: Optional[str] = None

    # Verification & Perceptual Deduplication
    enable_image_verification: bool = True
    min_image_bytes: int = 3000  # 3KB minimum to reject 1x1 pixels / trackers
    min_image_dimension: int = 120  # 120px minimum width/height
    enable_perceptual_dedup: bool = True
    phash_hamming_threshold: int = 4  # Hamming distance <= 4 considered near-identical duplicate

    # Search API Keys (Direct or PROMAS_ prefixed)
    brave_api_key: Optional[str] = Field(default=None, alias="BRAVE_API_KEY")
    serpapi_api_key: Optional[str] = Field(default=None, alias="SERPAPI_API_KEY")

    # Blocked UI / Icon patterns
    blocked_patterns: List[str] = [
        r'logo', r'icon', r'badge', r'avatar', r'spacer', r'pixel', r'blank',
        r'tracking', r'spinner', r'placeholder', r'arrow', r'rating', r'star',
        r'payment', r'credit-card', r'visa', r'mastercard', r'paypal', r'favicon',
        r'branding', r'googleg_', r'course', r'bundle', r'button', r'banner', r'seller',
        r'shop_snippet', r'1x1'
    ]

    # Non-retail discard domains
    discard_domains: List[str] = [
        "google.com", "bing.com", "duckduckgo.com", "wikipedia.org", "wikimedia.org",
        "wikileaks.org", "wiktionary.org", "theperfectfrench.com", "dictionary.com",
        "merriam-webster.com", "cambridge.org", "youtube.com", "facebook.com", "twitter.com",
        "linkedin.com", "indeed.com", "glassdoor.com", "ziprecruiter.com", "governmentjobs.com",
        "governmentresource.com"
    ]


settings = PromasSettings()
