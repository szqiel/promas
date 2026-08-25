"""
Per-Domain Concurrency and Rate Limiter
Prevents overwhelming or triggering IP bans on specific target domains during parallel scraping.
"""

import asyncio
import urllib.parse
from contextlib import asynccontextmanager
from typing import Dict

from loguru import logger


class DomainRateLimiter:
    """
    Combines a global concurrency pool with per-domain locks and inter-request delays.
    """

    def __init__(
        self,
        global_concurrency: int = 3,
        per_domain_concurrency: int = 1,
        domain_delay_seconds: float = 0.5
    ):
        self.global_semaphore = asyncio.Semaphore(global_concurrency)
        self.per_domain_concurrency = per_domain_concurrency
        self.domain_delay = domain_delay_seconds
        self._domain_semaphores: Dict[str, asyncio.Semaphore] = {}
        self._lock = asyncio.Lock()

    def _extract_domain(self, url: str) -> str:
        """Extracts normalized hostname from URL."""
        try:
            parsed = urllib.parse.urlparse(url)
            host = parsed.netloc.lower().split(":")[0]
            # Strip subdomains like www. or m.
            if host.startswith("www."):
                host = host[4:]
            elif host.startswith("m."):
                host = host[2:]
            return host or "default"
        except Exception:
            return "default"

    async def _get_domain_semaphore(self, domain: str) -> asyncio.Semaphore:
        async with self._lock:
            if domain not in self._domain_semaphores:
                self._domain_semaphores[domain] = asyncio.Semaphore(self.per_domain_concurrency)
            return self._domain_semaphores[domain]

    @asynccontextmanager
    async def acquire(self, url: str):
        """
        Asynchronous context manager ensuring both global and per-domain limits.
        """
        domain = self._extract_domain(url)
        domain_sem = await self._get_domain_semaphore(domain)

        async with self.global_semaphore:
            async with domain_sem:
                logger.debug(f"Acquired scrape slot for domain '{domain}' ({url[:60]}...)")
                try:
                    yield
                finally:
                    if self.domain_delay > 0:
                        await asyncio.sleep(self.domain_delay)
                    logger.debug(f"Released scrape slot for domain '{domain}'")
