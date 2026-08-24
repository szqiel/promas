"""
Promas CLI & Library Entrypoint
"""
import sys
import os

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from promas.core.models import ProductImageResult
from promas.orchestrator import get_product_images, scrape_product_images
from promas.cli.main import main, async_main

if __name__ == "__main__":
    main()
