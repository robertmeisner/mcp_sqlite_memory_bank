#!/usr/bin/env python3
"""
Entry point for running the SQLite Memory Bank MCP server.

This module provides a clean entry point for MCP clients to start the server
without import issues or circular dependencies.
"""

import logging
import sys
import os

# Add the project root to Python path to avoid import issues
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Configure logging before any other imports
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

def main() -> None:
    """Main entry point for the MCP server."""
    try:
        # Import here to avoid circular import issues
        from .server import app, DB_PATH
        
        # Handle help argument
        if "--help" in sys.argv or "-h" in sys.argv:
            print("SQLite Memory Bank MCP Server")
            print("Usage: python -m src.mcp_sqlite_memory_bank")
            print("")
            print("This starts the SQLite Memory Bank as an MCP (Model Context Protocol) server.")
            print("The server communicates via STDIO and provides memory management tools")
            print("for LLMs and AI agents.")
            print("")
            print(f"Database location: {DB_PATH}")
            print("")
            print("Environment variables:")
            print("  DB_PATH: Override the default database path")
            return
        
        # Log startup information
        logging.info(f"Starting SQLite Memory Bank MCP server with database at {DB_PATH}")
        
        # Run the FastMCP app in stdio mode for MCP clients
        app.run(transport="stdio")
        
    except KeyboardInterrupt:
        logging.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Failed to start MCP server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
