"""
Search Backend Base Interface
Defines the standard contract for official API search backends and experimental browser backends.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from playwright.async_api import Page


class BaseSearchBackend(ABC):
    """Abstract base class for search discovery backends."""

    name: str = "base"
    is_experimental: bool = False
    requires_api_key: bool = False

    @abstractmethod
    def is_available(self) -> bool:
        """Returns True if the backend has valid credentials / configuration to run."""
        pass

    @abstractmethod
    async def search(
        self,
        query: str,
        site_filter: Optional[str] = None,
        page: Optional[Page] = None
    ) -> List[str]:
        """
        Executes search and returns a list of candidate destination URLs.
        """
        pass
