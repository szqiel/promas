"""
Search Backend Base Interface
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from playwright.async_api import Page


class BaseSearchBackend(ABC):
    """Abstract base class for search discovery backends."""

    @abstractmethod
    async def search(self, page: Page, query: str, site_filter: Optional[str] = None) -> List[str]:
        """Returns list of organic destination URLs."""
        pass
