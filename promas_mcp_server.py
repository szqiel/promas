"""
Promas FastMCP Server Entrypoint
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from promas.server.mcp_server import mcp, fetch_product_images, get_product_images_tool, run_server

if __name__ == "__main__":
    run_server()
