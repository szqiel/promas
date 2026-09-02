"""
Example: Using Promas in a LangChain ReAct Agent
Demonstrates how to wrap Promas as a structured LangChain Tool for visual product grounding.
"""

import asyncio
import json
from typing import Optional

from langchain_core.tools import tool

from promas import get_product_images


@tool
def fetch_product_images_tool(query: str, max_images: int = 5, site_filter: Optional[str] = None) -> str:
    """
    Universally extracts verified high-resolution product photography and official links.
    Args:
        query: Product name/model (e.g. 'Sony FX3', 'iPhone 16 Pro') or direct URL.
        max_images: Maximum number of images to return.
        site_filter: Optional domain filter (e.g. 'apple.com', 'nike.com').
    """
    result = asyncio.run(get_product_images(query=query, max_images=max_images, site_filter=site_filter))
    return result.model_dump_json()


def run_example():
    print("[*] Testing LangChain Tool directly...")
    raw_output = fetch_product_images_tool.invoke({
        "query": "Sony FX3 Cinema Camera",
        "max_images": 3
    })
    data = json.loads(raw_output)
    print(f"Status: {data.get('status')}")
    print(f"Title: {data.get('title')}")
    print(f"Images ({len(data.get('images', []))}):")
    for img in data.get("images", []):
        print(f" - {img}")


if __name__ == "__main__":
    run_example()
