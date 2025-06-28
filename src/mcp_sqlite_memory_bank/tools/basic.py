"""
Basic tools module for SQLite Memory Bank.

This module contains all basic CRUD and utility MCP tools including table management,
data operations, and core functionality.
"""

from typing import Any, Dict, List, Optional, cast

from ..database import get_database
from ..types import MemoryBankError, DatabaseError, ToolResponse
from ..utils import catch_errors


@catch_errors
def create_table(
    table_name: str,
    columns: List[Dict[str, str]],
) -> ToolResponse:
    """Create a new table in the SQLite memory bank."""
    from .. import server
    return cast(ToolResponse, get_database(server.DB_PATH).create_table(table_name, columns))


@catch_errors
def list_tables() -> ToolResponse:
    """List all tables in the SQLite memory bank."""
    from .. import server
    return cast(ToolResponse, get_database(server.DB_PATH).list_tables())


@catch_errors
def describe_table(table_name: str) -> ToolResponse:
    """Get detailed schema information for a table."""
    from .. import server
    return cast(ToolResponse, get_database(server.DB_PATH).describe_table(table_name))


@catch_errors
def drop_table(table_name: str) -> ToolResponse:
    """Drop (delete) a table from the SQLite memory bank."""
    from .. import server
    return cast(ToolResponse, get_database(server.DB_PATH).drop_table(table_name))


@catch_errors
def rename_table(old_name: str, new_name: str) -> ToolResponse:
    """Rename a table in the SQLite memory bank."""
    from .. import server
    return cast(ToolResponse, get_database(server.DB_PATH).rename_table(old_name, new_name))


@catch_errors
def create_row(
    table_name: str,
    data: Dict[str, Any],
) -> ToolResponse:
    """Insert a new row into any table in the SQLite Memory Bank."""
    from .. import server
    return cast(ToolResponse, get_database(server.DB_PATH).insert_row(table_name, data))


@catch_errors
def read_rows(
    table_name: str,
    where: Optional[Dict[str, Any]] = None,
) -> ToolResponse:
    """Read rows from any table in the SQLite memory bank, with optional filtering."""
    from .. import server
    return cast(ToolResponse, get_database(server.DB_PATH).read_rows(table_name, where))


@catch_errors
def update_rows(
    table_name: str,
    data: Dict[str, Any],
    where: Optional[Dict[str, Any]] = None,
) -> ToolResponse:
    """Update rows in any table in the SQLite Memory Bank, matching the WHERE clause."""
    from .. import server
    return cast(ToolResponse, get_database(server.DB_PATH).update_rows(table_name, data, where))


@catch_errors
def delete_rows(
    table_name: str,
    where: Optional[Dict[str, Any]] = None,
) -> ToolResponse:
    """Delete rows from any table in the SQLite Memory Bank, matching the WHERE clause."""
    from .. import server
    return cast(ToolResponse, get_database(server.DB_PATH).delete_rows(table_name, where))


@catch_errors
def run_select_query(
    table_name: str,
    columns: Optional[List[str]] = None,
    where: Optional[Dict[str, Any]] = None,
    limit: int = 100,
) -> ToolResponse:
    """Run a safe SELECT query on a table in the SQLite memory bank."""
    from .. import server
    return cast(ToolResponse, get_database(server.DB_PATH).select_query(
        table_name, columns, where, limit
    ))


@catch_errors
def list_all_columns() -> ToolResponse:
    """List all columns for all tables in the SQLite memory bank."""
    from .. import server
    return cast(ToolResponse, get_database(server.DB_PATH).list_all_columns())
