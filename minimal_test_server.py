#!/usr/bin/env python3
"""
Minimal FastMCP server test to diagnose stdio communication issues.
"""

import sys
import logging
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Create minimal FastMCP server
mcp = FastMCP("Minimal Test Server")

@mcp.tool()
def test_tool() -> str:
    """A simple test tool."""
    return "Hello from test tool!"

if __name__ == "__main__":
    logger.info("Starting minimal FastMCP test server")
    try:
        mcp.run(transport="stdio")
    except Exception as e:
        logger.error(f"Error running server: {e}")
        sys.exit(1)
