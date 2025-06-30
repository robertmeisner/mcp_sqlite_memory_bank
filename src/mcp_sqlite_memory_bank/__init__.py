"""
mcp_sqlite_memory_bank: A dynamic, agent/LLM-friendly SQLite memory bank for
MCP servers.

This package provides tools for creating, exploring, and managing SQLite
tables and knowledge graphs - enabling Copilot, Claude Desktop, VS Code,
Cursor, and other LLM-powered tools to interact with structured data in a
safe, explicit, and extensible way.

Author: Robert Meisner
Version: 1.6.6
License: MIT
"""

from .server import (
    # Core tools
    create_table,
    drop_table,
    rename_table,
    list_tables,
    describe_table,
    list_all_columns,
    create_row,
    read_rows,
    update_rows,
    delete_rows,
    run_select_query,
    # FastMCP app
    app,
    # Constants
    DB_PATH,
)

# Import search tools from the tools module
from .tools import (
    # Search tools
    search_content,
    explore_tables,
    add_embeddings,
    semantic_search,
    find_related,
    smart_search,
    embedding_stats,
    auto_semantic_search,
    auto_smart_search,
)

from .types import (
    # Response types
    CreateTableResponse,
    DropTableResponse,
    RenameTableResponse,
    ListTablesResponse,
    DescribeTableResponse,
    ListAllColumnsResponse,
    CreateRowResponse,
    ReadRowsResponse,
    UpdateRowsResponse,
    DeleteRowsResponse,
    SelectQueryResponse,
    ErrorResponse,
    ToolResponse,
    # Error types
    ValidationError,
    DatabaseError,
    SchemaError,
    DataError,
    MemoryBankError,
    ErrorCategory,
    # Data types
    TableColumn,
    SqliteType,
)

# Package metadata
__version__ = "1.6.8"
__author__ = "Robert Meisner"
__all__ = [
    # Core tools
    "create_table",
    "drop_table",
    "rename_table",
    "list_tables",
    "describe_table",
    "list_all_columns",
    "create_row",
    "read_rows",
    "update_rows",
    "delete_rows",
    "run_select_query",
    # Search tools
    "search_content",
    "explore_tables",
    "add_embeddings",
    "semantic_search",
    "find_related",
    "smart_search",
    "embedding_stats",
    "auto_semantic_search",
    "auto_smart_search",
    # FastMCP app
    "app",
    # Constants
    "DB_PATH",
    # Response types
    "CreateTableResponse",
    "DropTableResponse",
    "RenameTableResponse",
    "ListTablesResponse",
    "DescribeTableResponse",
    "ListAllColumnsResponse",
    "CreateRowResponse",
    "ReadRowsResponse",
    "UpdateRowsResponse",
    "DeleteRowsResponse",
    "SelectQueryResponse",
    "ErrorResponse",
    "ToolResponse",
    # Error types
    "ValidationError",
    "DatabaseError",
    "SchemaError",
    "DataError",
    "MemoryBankError",
    "ErrorCategory",
    # Data types
    "TableColumn",
    "SqliteType",
]
