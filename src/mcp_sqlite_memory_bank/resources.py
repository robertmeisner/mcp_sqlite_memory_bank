"""
MCP Resources Support for SQLite Memory Bank
==========================================

This module adds MCP Resources support, allowing the memory bank to expose
stored content as MCP resources that can be consumed by LLM applications.

Resources provide context and data that can be accessed by AI models through
the standardized MCP protocol.

Author: Robert Meisner
"""

from typing import Dict, Any, cast
from fastmcp import FastMCP
from .database import get_database
import json


class MemoryBankResources:
    """Manages MCP Resources for the SQLite Memory Bank."""
    
    def __init__(self, mcp_app: FastMCP, db_path: str):
        self.mcp = mcp_app
        self.db_path = db_path
        self._register_resources()
    
    def _register_resources(self):
        """Register MCP resources with the FastMCP app."""
        
        @self.mcp.resource("memory://tables/list")
        async def get_tables_list() -> str:
            """Provide a list of all available tables as an MCP resource."""
            db = get_database(self.db_path)
            result = cast(Dict[str, Any], db.list_tables())
            
            if not result.get("success"):
                return json.dumps({"error": "Failed to fetch tables", "details": result})
            
            resource_content = {
                "resource_type": "table_list",
                "description": "List of all available tables in the memory bank",
                "tables": result.get("tables", []),
                "total_count": len(result.get("tables", [])),
                "last_updated": "dynamic"
            }
            
            return json.dumps(resource_content, indent=2)
        
        @self.mcp.resource("memory://tables/{table_name}/schema")
        async def get_table_schema(table_name: str) -> str:
            """Provide table schema information as an MCP resource."""
            db = get_database(self.db_path)
            result = cast(Dict[str, Any], db.describe_table(table_name))
            
            if not result.get("success"):
                return json.dumps({"error": f"Failed to fetch schema for table '{table_name}'", "details": result})
            
            resource_content = {
                "resource_type": "table_schema",
                "table_name": table_name,
                "description": f"Schema definition for table '{table_name}'",
                "columns": result.get("columns", []),
                "column_count": len(result.get("columns", [])),
                "last_updated": "dynamic"
            }
            
            return json.dumps(resource_content, indent=2)
        
        @self.mcp.resource("memory://tables/{table_name}/data")
        async def get_table_data(table_name: str) -> str:
            """Provide table data as an MCP resource."""
            db = get_database(self.db_path)
            result = cast(Dict[str, Any], db.read_rows(table_name, {}))
            
            if not result.get("success"):
                return json.dumps({"error": f"Failed to fetch data for table '{table_name}'", "details": result})
            
            rows = result.get("rows", [])
            resource_content = {
                "resource_type": "table_data",
                "table_name": table_name,
                "description": f"All data from table '{table_name}'",
                "rows": rows,
                "row_count": len(rows),
                "last_updated": "dynamic"
            }
            
            return json.dumps(resource_content, indent=2)
        
        @self.mcp.resource("memory://search/{query}")
        async def search_memory_content(query: str) -> str:
            """Provide search results as an MCP resource."""
            db = get_database(self.db_path)
            result = cast(Dict[str, Any], db.search_content(query, None, 50))  # Search all tables, limit to 50 results
            
            if not result.get("success"):
                return json.dumps({"error": f"Failed to search for '{query}'", "details": result})
            
            search_results = result.get("results", [])
            resource_content = {
                "resource_type": "search_results",
                "query": query,
                "description": f"Search results for query: '{query}'",
                "results": search_results,
                "result_count": len(search_results),
                "last_updated": "dynamic"
            }
            
            return json.dumps(resource_content, indent=2)
        
        @self.mcp.resource("memory://analytics/overview")
        async def get_memory_overview() -> str:
            """Provide memory bank overview analytics as an MCP resource."""
            db = get_database(self.db_path)
            
            # Get table list
            tables_result = cast(Dict[str, Any], db.list_tables())
            if not tables_result.get("success"):
                return json.dumps({"error": "Failed to fetch memory overview", "details": tables_result})
            
            tables = tables_result.get("tables", [])
            total_rows = 0
            table_stats = {}
            
            # Get row counts for each table
            for table in tables:
                try:
                    rows_result = cast(Dict[str, Any], db.read_rows(table, {}))
                    if rows_result.get("success"):
                        row_count = len(rows_result.get("rows", []))
                        table_stats[table] = {
                            "row_count": row_count,
                            "status": "accessible"
                        }
                        total_rows += row_count
                    else:
                        table_stats[table] = {
                            "row_count": 0,
                            "status": "error"
                        }
                except Exception as e:
                    table_stats[table] = {
                        "row_count": 0,
                        "status": f"error: {str(e)}"
                    }
            
            # Find largest table
            largest_table = None
            if table_stats:
                max_rows = 0
                for table_name, stats in table_stats.items():
                    row_count_obj = stats.get("row_count", 0)
                    row_count = int(row_count_obj) if isinstance(row_count_obj, (int, str)) else 0
                    if row_count > max_rows:
                        max_rows = row_count
                        largest_table = table_name

            resource_content = {
                "resource_type": "memory_overview",
                "description": "Overview of memory bank contents and usage",
                "summary": {
                    "total_tables": len(tables),
                    "total_rows": total_rows,
                    "largest_table": largest_table
                },
                "table_statistics": table_stats,
                "last_updated": "dynamic"
            }
            
            return json.dumps(resource_content, indent=2)


def setup_mcp_resources(mcp_app: FastMCP, db_path: str) -> MemoryBankResources:
    """Set up MCP Resources for the memory bank."""
    return MemoryBankResources(mcp_app, db_path)
