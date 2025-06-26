"""
mcp_sqlite_memory_bank: A dynamic, agent/LLM-friendly SQLite memory bank for MCP servers.

This package provides tools for creating, exploring, and managing SQLite tables and
knowledge graphs - enabling Copilot, Claude Desktop, VS Code, Cursor, and other
LLM-powered tools to interact with structured data in a safe, explicit, and extensible way.

Author: Robert Meisner
Version: 0.1.0
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
__version__ = "0.1.0"
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
