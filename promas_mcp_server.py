"""
Promas FastMCP Server Entrypoint
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from promas.server.mcp_server import run_server

if __name__ == "__main__":
    run_server()
