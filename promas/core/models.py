"""
Promas Data Models
Pydantic schemas for product image scraping results and metadata.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class ProductImageResult(BaseModel):
    """Unified result model returned by Promas."""
    status: str = Field(description="'success' or 'error'")
    query: str = Field(description="Search query or URL requested")
    title: Optional[str] = Field(default=None, description="Title of the matched product or primary page")
    sources_scraped: List[str] = Field(default_factory=list, description="URLs or domains scraped")
    images: List[str] = Field(default_factory=list, description="Array of high-resolution image URLs")
    error_message: Optional[str] = Field(default=None, description="Error message if scraping failed")
