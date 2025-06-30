"""
Example: FastMCP Client for SQLite Memory Bank

- Connects to the running FastMCP server at http://localhost:8000/mcp
- Lists all available tools (using the 'list_tools' tool)
- Demonstrates calling 'list_tables' and prints the result
- Handles errors gracefully

Usage:
    python client_example.py

Requirements:
    - fastmcp (pip install fastmcp)
"""

import asyncio
from fastmcp.client import Client
import pprint

SERVER_URLS = [
    "http://localhost:8000/mcp/",  # Try with trailing slash
    "http://localhost:8000/mcp",  # Try without trailing slash
    "http://localhost:8000",  # Try root
]


async def main():

    for url in SERVER_URLS:
        print(f"Connecting to FastMCP server at {url} ...")
        try:
            async with Client(url) as client:
                # List all available tools
                print("\nAvailable tools:")
                tools_result = await client.call_tool("list_tools", {})
                # Print the raw result for debugging
                print("Raw result from 'list_tools':")
                pprint.pprint(tools_result)

                # Parse and print tool names and docstrings in a user-friendly way
                if isinstance(tools_result, dict):
                    tool_list = tools_result.get("tools", [])
                    if tool_list:
                        print("\nTool List:")
                        for tool in tool_list:
                            name = tool.get("name", "<unnamed>")
                            doc = tool.get("doc", "(No docstring)")
                            print(f"- {name}: {doc}")
                    else:
                        print("[Warning] No 'tools' key or empty list in 'list_tools' result.")
                else:
                    print("[Warning] Unexpected structure for 'list_tools' result.")

                # Demonstrate calling 'list_tables'
                print("\nCalling 'list_tables' tool:")
                tables_result = await client.call_tool("list_tables", {})
                # Print the raw result for debugging
                print("Raw result from 'list_tables':")
                pprint.pprint(tables_result)

                # Parse and print table names if present
                if isinstance(tables_result, dict):
                    table_list = tables_result.get("tables", [])
                    if table_list:
                        print("\nTables in SQLite Memory Bank:")
                        for table in table_list:
                            print(f"- {table}")
                    else:
                        print("[Warning] No 'tables' key or empty list in 'list_tables' result.")
                else:
                    print("[Warning] Unexpected structure for 'list_tables' result.")

            # If we get here, connection and calls succeeded
            break
        except Exception as e:
            print(f"Client error with {url}: {e}")
    else:
        print("All connection attempts failed. Please check the server URL and that the server is running.")


if __name__ == "__main__":
    asyncio.run(main())
