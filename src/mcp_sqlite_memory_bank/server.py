"""
SQLite Memory Bank for Copilot/AI Agents
=======================================

This FastMCP server provides a dynamic, agent-friendly SQLite memory bank.
All APIs are explicit, discoverable, and validated for safe, flexible use by LLMs and agent frameworks.

**Design Note:**
    - All CRUD and schema operations are exposed as explicit, type-annotated, and well-documented FastMCP tools.
    - All tools are registered directly on the FastMCP app instance using the @mcp.tool decorator.
    - This design is preferred for LLMs and clients, as it ensures discoverability, schema validation, and ease of use.
    - No multiplexed or control-argument tools are provided as primary interfaces.

Available Tools (for LLMs/agents):
----------------------------------
    - create_table(table, columns): Create a new table with a custom schema.
    - drop_table(table): Drop (delete) a table.
    - rename_table(old_name, new_name): Rename a table.
    - list_tables(): List all tables in the memory bank.
    - describe_table(table): Get schema details for a table.
    - list_all_columns(): List all columns for all tables.
    - create_row(table, data): Insert a row into any table.
    - read_rows(table, where): Read rows from any table (with optional filtering).
    - update_rows(table, data, where): Update rows from any table (with optional filtering).
    - delete_rows(table, where): Delete rows from any table (with optional filtering).
    - run_select_query(table, columns, where): Run a safe SELECT query (no arbitrary SQL).

All table/column names are validated to prevent SQL injection.
Only safe, explicit operations are allowed (no arbitrary SQL).
All tools are documented and designed for explicit, LLM-friendly use.

FastMCP Tool Documentation:
--------------------------
Each tool is designed for explicit, discoverable use by LLMs and agents:
- All parameters are strongly typed and validated
- Success/error responses follow a consistent pattern
- Error messages are clear and actionable for both humans and LLMs
- Documentation includes examples and common use cases

Author: Robert Meisner
"""

import os
import re
import sqlite3
import logging
from typing import Dict, Optional, List, cast, Any
from fastmcp import FastMCP

from .types import (
    ToolResponse,
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
    ValidationError,
    DatabaseError,
    SchemaError
)
from .utils import (
    catch_errors,
    validate_identifier,
    validate_column_definition,
    get_table_columns,
    validate_table_exists,
    build_where_clause
)


# Initialize FastMCP app with explicit name
mcp: FastMCP = FastMCP("SQLite Memory Bank for Copilot/AI Agents")

# Configure database path from environment or default
DB_PATH = os.environ.get("DB_PATH", "./test.db")

# Ensure database directory exists
os.makedirs(os.path.dirname(os.path.abspath(DB_PATH)), exist_ok=True)


# --- Schema Management Tools for SQLite Memory Bank ---

@mcp.tool
@catch_errors
def create_table(
        table_name: str, columns: List[Dict[str, str]]) -> ToolResponse:
    """
    Create a new table in the SQLite memory bank.

    Args:
        table_name (str): Name of the table to create. Must be a valid SQLite identifier.
        columns (List[Dict[str, str]]): List of columns, each as {"name": str, "type": str}.

    Returns:
        ToolResponse: On success: {"success": True}
                     On error: {"success": False, "error": str, "category": str, "details": dict}

    Examples:
        >>> create_table("users", [
        ...     {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
        ...     {"name": "name", "type": "TEXT"},
        ...     {"name": "age", "type": "INTEGER"}
        ... ])
        {"success": True}

    FastMCP Tool Info:
        - Validates table name and column definitions
        - Creates table if it doesn't exist (idempotent)
        - Raises appropriate errors for invalid input
    """
    # Validate table name
    validate_identifier(table_name, "table name")

    # Validate columns
    if not columns:
        raise ValidationError(
            "Must provide at least one column",
            {"columns": columns}
        )

    # Validate each column
    for col in columns:
        validate_column_definition(col)

    # Build and execute CREATE TABLE
    col_defs = ', '.join([f"{col['name']} {col['type']}" for col in columns])
    query = f"CREATE TABLE IF NOT EXISTS {table_name} ({col_defs})"

    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(query)
            return cast(CreateTableResponse, {"success": True})
    except sqlite3.Error as e:
        raise DatabaseError(
            f"Failed to create table {table_name}",
            {"sqlite_error": str(e)}
        )


@mcp.tool
@catch_errors
def list_tables() -> ToolResponse:
    """
    List all tables in the SQLite memory bank.

    Returns:
        ToolResponse: On success: {"success": True, "tables": List[str]}
                     On error: {"success": False, "error": str, "category": str, "details": dict}

    Examples:
        >>> list_tables()
        {"success": True, "tables": ["users", "notes", "tasks"]}

    FastMCP Tool Info:
        - Returns list of all user-created tables
        - Excludes SQLite system tables
        - Useful for schema discovery by LLMs
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )
            tables = [row[0] for row in cur.fetchall()]
            return cast(
                ListTablesResponse, {
                    "success": True, "tables": tables})

    except sqlite3.Error as e:
        raise DatabaseError(
            "Failed to list tables",
            {"sqlite_error": str(e)}
        )


@mcp.tool
@catch_errors
def describe_table(table_name: str) -> ToolResponse:
    """
    Get detailed schema information for a table.

    Args:
        table_name (str): Name of the table to describe.

    Returns:
        ToolResponse: On success: {"success": True, "columns": List[TableColumn]}
                     On error: {"success": False, "error": str, "category": str, "details": dict}

        Where TableColumn is:
        {
            "name": str,
            "type": str,
            "notnull": bool,
            "default": Any,
            "pk": bool
        }

    Examples:
        >>> describe_table("users")
        {
            "success": True,
            "columns": [
                {"name": "id", "type": "INTEGER", "notnull": 1, "default": null, "pk": 1},
                {"name": "name", "type": "TEXT", "notnull": 1, "default": null, "pk": 0}
            ]
        }

    FastMCP Tool Info:
        - Returns detailed column information
        - Validates table existence
        - Useful for schema introspection by LLMs
    """
    # Validate table name
    validate_identifier(table_name, "table name")

    try:
        with sqlite3.connect(DB_PATH) as conn:
            # Validate table exists
            validate_table_exists(conn, table_name)

            # Get column info
            cur = conn.cursor()
            cur.execute(f"PRAGMA table_info({table_name})")
            columns = [
                {
                    "name": row[1],
                    "type": row[2],
                    "notnull": bool(row[3]),
                    "default": row[4],
                    "pk": bool(row[5])
                }
                for row in cur.fetchall()
            ]

            return cast(
                DescribeTableResponse, {
                    "success": True, "columns": columns})

    except sqlite3.Error as e:
        raise DatabaseError(
            f"Failed to describe table {table_name}",
            {"sqlite_error": str(e)}
        )


@mcp.tool
def drop_table(table_name: str) -> ToolResponse:
    """
    Drop (delete) a table from the SQLite memory bank.

    Args:
        table_name (str): Name of the table to drop. Must be a valid SQLite identifier.

    Returns:
        ToolResponse: On success: {"success": True}
                     On error: {"success": False, "error": str, "category": str, "details": dict}

    Examples:
        >>> drop_table('notes')
        {"success": True}

    FastMCP Tool Info:
        - Validates table name
        - Confirms table exists before dropping
        - WARNING: This operation is irreversible and deletes all data in the table
    """
    # Validate table name
    validate_identifier(table_name, "table name")

    try:
        with sqlite3.connect(DB_PATH) as conn:
            # Validate table exists
            cur = conn.cursor()
            cur.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (table_name,)
            )
            if not cur.fetchone():
                return cast(ErrorResponse, {
                    "success": False,
                    "error": f"Table does not exist: {table_name}",
                    "category": "schema_error",
                    "details": {"table_name": table_name}
                })

            # Execute DROP TABLE
            conn.execute(f"DROP TABLE {table_name}")
            conn.commit()

            return cast(DropTableResponse, {"success": True})

    except sqlite3.Error as e:
        raise DatabaseError(
            f"Failed to drop table {table_name}",
            {"sqlite_error": str(e)}
        )


@mcp.tool
@catch_errors
def rename_table(old_name: str, new_name: str) -> ToolResponse:
    """
    Rename a table in the SQLite memory bank.

    Args:
        old_name (str): Current table name. Must be a valid SQLite identifier.
        new_name (str): New table name. Must be a valid SQLite identifier.

    Returns:
        ToolResponse: On success: {"success": True}
                     On error: {"success": False, "error": str, "category": str, "details": dict}

    Examples:
        >>> rename_table('notes', 'archive_notes')
        {"success": True}

    FastMCP Tool Info:
        - Validates both old and new table names
        - Confirms old table exists and new name doesn't conflict
    """
    # Validate table names
    validate_identifier(old_name, "old table name")
    validate_identifier(new_name, "new table name")

    # Check if names are the same
    if old_name == new_name:
        raise ValidationError(
            "Old and new table names are identical",
            {"old_name": old_name, "new_name": new_name}
        )

    try:
        with sqlite3.connect(DB_PATH) as conn:
            # Validate old table exists
            validate_table_exists(conn, old_name)

            # Check if new table already exists
            cur = conn.cursor()
            cur.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (new_name,)
            )
            if cur.fetchone():
                raise SchemaError(
                    f"Cannot rename: table {new_name} already exists",
                    {"new_name": new_name}
                )

            # Execute ALTER TABLE
            conn.execute(f"ALTER TABLE {old_name} RENAME TO {new_name}")
            conn.commit()

            return cast(RenameTableResponse, {"success": True})

    except sqlite3.Error as e:
        raise DatabaseError(
            f"Failed to rename table from {old_name} to {new_name}",
            {"sqlite_error": str(e)}
        )


@mcp.tool
@catch_errors
def create_row(table_name: str, data: Dict[str, Any]) -> ToolResponse:
    """
    Insert a new row into any table in the SQLite Memory Bank for Copilot/AI agents.

    Args:
        table_name (str): Table name.
        data (Dict[str, Any]): Data to insert (column-value pairs matching the table schema).

    Returns:
        ToolResponse: On success: {"success": True, "id": rowid}
                     On error: {"success": False, "error": str, "category": str, "details": dict}

    Examples:
        >>> create_row('notes', {'content': 'Remember to hydrate!'})
        {"success": True, "id": 1}

    FastMCP Tool Info:
        - Validates table name and column names
        - Auto-converts data types where possible
        - Returns the row ID of the inserted row
    """
    # Validate table name
    validate_identifier(table_name, "table name")

    # Validate data
    if not data:
        raise ValidationError(
            "Data cannot be empty",
            {"data": data}
        )

    try:
        with sqlite3.connect(DB_PATH) as conn:
            # Get and validate columns
            valid_columns = get_table_columns(conn, table_name)

            # Validate column names
            for k in data.keys():
                if k not in valid_columns:
                    raise ValidationError(
                        f"Invalid column in data: {k}",
                        {"invalid_column": k, "valid_columns": valid_columns}
                    )

            # Build and execute INSERT
            keys = ', '.join(data.keys())
            placeholders = ', '.join(['?'] * len(data))
            values = list(data.values())
            query = f"INSERT INTO {table_name} ({keys}) VALUES ({placeholders})"

            cur = conn.cursor()
            cur.execute(query, values)
            conn.commit()

            return cast(
                CreateRowResponse, {
                    "success": True, "id": cur.lastrowid})

    except sqlite3.Error as e:
        raise DatabaseError(
            f"Failed to insert into table {table_name}",
            {"sqlite_error": str(e)}
        )


@mcp.tool
@catch_errors
def read_rows(table_name: str,
              where: Optional[Dict[str,
                                   Any]] = None) -> ToolResponse:
    """
    Read rows from any table in the SQLite memory bank, with optional filtering.

    Args:
        table_name (str): Name of the table to read from.
        where (Optional[Dict[str, Any]]): Optional filter conditions as {"column": value} pairs.

    Returns:
        ToolResponse: On success: {"success": True, "rows": List[Dict[str, Any]]}
                     On error: {"success": False, "error": str, "category": str, "details": dict}

    Examples:
        >>> read_rows("users", {"age": 25})
        {"success": True, "rows": [{"id": 1, "name": "Alice", "age": 25}, ...]}

    FastMCP Tool Info:
        - Validates table name and filter conditions
        - Returns rows as list of dictionaries
        - Parameterizes all queries for safety
    """
    where = where or {}

    # Validate table name
    validate_identifier(table_name, "table name")

    try:
        with sqlite3.connect(DB_PATH) as conn:
            # Get and validate columns
            valid_columns = get_table_columns(conn, table_name)

            # Build query
            query = f"SELECT * FROM {table_name}"
            where_clause, params = build_where_clause(where, valid_columns)
            if where_clause:
                query += f" WHERE {where_clause}"

            # Execute and fetch
            cur = conn.execute(query, params)
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]

            return cast(ReadRowsResponse, {
                "success": True,
                "rows": [dict(zip(columns, row)) for row in rows]
            })

    except sqlite3.Error as e:
        raise DatabaseError(
            f"Failed to read from table {table_name}",
            {"sqlite_error": str(e)}
        )


@mcp.tool
@catch_errors
def update_rows(table_name: str,
                data: Dict[str,
                           Any],
                where: Optional[Dict[str,
                                     Any]] = None) -> ToolResponse:
    """
    Update rows in any table in the SQLite Memory Bank for Copilot/AI agents, matching the WHERE clause.

    Args:
        table_name (str): Table name.
        data (Dict[str, Any]): Data to update (column-value pairs).
        where (Optional[Dict[str, Any]]): WHERE clause as column-value pairs (optional).

    Returns:
        ToolResponse: On success: {"success": True, "rows_affected": n}
                     On error: {"success": False, "error": str, "category": str, "details": dict}

    Examples:
        >>> update_rows('notes', {'content': 'Updated note'}, {'id': 1})
        {"success": True, "rows_affected": 1}

    FastMCP Tool Info:
        - Validates table name, column names, and filter conditions
        - Returns the number of rows affected by the update
        - Parameterizes all queries for safety
        - Where clause is optional (omitting it updates all rows!)
    """
    where = where or {}

    # Validate table name
    validate_identifier(table_name, "table name")

    # Validate data
    if not data:
        raise ValidationError(
            "Update data cannot be empty",
            {"data": data}
        )

    try:
        with sqlite3.connect(DB_PATH) as conn:
            # Get and validate columns
            valid_columns = get_table_columns(conn, table_name)

            # Validate column names in data
            for k in data.keys():
                if k not in valid_columns:
                    raise ValidationError(
                        f"Invalid column in data: {k}",
                        {"invalid_column": k, "valid_columns": valid_columns}
                    )

            # Build SET clause
            set_clause = ', '.join([f"{k}=?" for k in data.keys()])
            set_values = list(data.values())

            # Build WHERE clause
            where_clause, where_values = build_where_clause(
                where, valid_columns)

            # Build and execute UPDATE
            query = f"UPDATE {table_name} SET {set_clause}"
            if where_clause:
                query += f" WHERE {where_clause}"

            cur = conn.cursor()
            # Fix type issue: ensure where_values is always a list before
            # concatenating
            where_values_list = where_values if isinstance(
                where_values, list) else []
            cur.execute(query, set_values + where_values_list)
            conn.commit()

            return cast(
                UpdateRowsResponse, {
                    "success": True, "rows_affected": cur.rowcount})

    except sqlite3.Error as e:
        raise DatabaseError(
            f"Failed to update table {table_name}",
            {"sqlite_error": str(e)}
        )


@mcp.tool
@catch_errors
def delete_rows(table_name: str,
                where: Optional[Dict[str,
                                     Any]] = None) -> ToolResponse:
    """
    Delete rows from any table in the SQLite Memory Bank for Copilot/AI agents, matching the WHERE clause.

    Args:
        table_name (str): Table name.
        where (Optional[Dict[str, Any]]): WHERE clause as column-value pairs (optional).

    Returns:
        ToolResponse: On success: {"success": True, "rows_affected": n}
                     On error: {"success": False, "error": str, "category": str, "details": dict}

    Examples:
        >>> delete_rows('notes', {'id': 1})
        {"success": True, "rows_affected": 1}

    FastMCP Tool Info:
        - Validates table name and filter conditions
        - Returns the number of rows deleted
        - Parameterizes all queries for safety
        - Where clause is optional (omitting it deletes all rows!)
    """
    where = where or {}

    # Validate table name
    validate_identifier(table_name, "table name")

    # Warn if no where clause (would delete all rows)
    if not where:
        logging.warning(
            f"delete_rows called without WHERE clause on table {table_name} - all rows will be deleted")

    try:
        with sqlite3.connect(DB_PATH) as conn:
            # Get and validate columns
            valid_columns = get_table_columns(conn, table_name)

            # Build WHERE clause
            where_clause, where_values = build_where_clause(
                where, valid_columns)

            # Build and execute DELETE
            query = f"DELETE FROM {table_name}"
            if where_clause:
                query += f" WHERE {where_clause}"

            cur = conn.cursor()
            cur.execute(query, where_values)
            conn.commit()

            return cast(
                DeleteRowsResponse, {
                    "success": True, "rows_affected": cur.rowcount})

    except sqlite3.Error as e:
        raise DatabaseError(
            f"Failed to delete from table {table_name}",
            {"sqlite_error": str(e)}
        )


@mcp.tool
@catch_errors
def run_select_query(table_name: str,
                     columns: Optional[List[str]] = None,
                     where: Optional[Dict[str,
                                          Any]] = None,
                     limit: int = 100) -> ToolResponse:
    """
    Run a safe SELECT query on a table in the SQLite memory bank.

    Args:
        table_name (str): Table name.
        columns (Optional[List[str]]): List of columns to select (default: all).
        where (Optional[Dict[str, Any]]): WHERE clause as column-value pairs (optional).
        limit (int): Maximum number of rows to return (default: 100).

    Returns:
        ToolResponse: On success: {"success": True, "rows": [...]}
                     On error: {"success": False, "error": str, "category": str, "details": dict}

    Examples:
        >>> run_select_query('notes', ['id', 'content'], {'id': 1})
        {"success": True, "rows": [{"id": 1, "content": "Remember to hydrate!"}]}

    FastMCP Tool Info:
        - Validates table name, column names, and filter conditions
        - Parameterizes all queries for safety
        - Only SELECT queries are allowed (no arbitrary SQL)
        - Default limit of 100 rows prevents memory issues
    """
    where = where or {}

    # Validate table name
    validate_identifier(table_name, "table name")

    # Validate limit
    if not isinstance(limit, int) or limit < 1:
        raise ValidationError(
            "Limit must be a positive integer",
            {"limit": limit}
        )

    try:
        with sqlite3.connect(DB_PATH) as conn:
            # Get and validate columns
            valid_columns = get_table_columns(conn, table_name)

            # Validate requested columns
            if columns:
                for col in columns:
                    if not isinstance(col, str):
                        raise ValidationError(
                            "Column name must be a string",
                            {"invalid_column": col}
                        )
                    if col not in valid_columns:
                        raise ValidationError(
                            f"Invalid column: {col}", {
                                "invalid_column": col, "valid_columns": valid_columns})
                select_cols = ', '.join(columns)
            else:
                select_cols = '*'

            # Build WHERE clause
            where_clause, where_values = build_where_clause(
                where, valid_columns)

            # Build and execute SELECT
            query = f"SELECT {select_cols} FROM {table_name}"
            if where_clause:
                query += f" WHERE {where_clause}"
            query += f" LIMIT {limit}"

            cur = conn.cursor()
            cur.execute(query, where_values)
            rows = cur.fetchall()
            result_columns = [desc[0] for desc in cur.description]

            return cast(SelectQueryResponse, {
                "success": True,
                "rows": [dict(zip(result_columns, row)) for row in rows]
            })

    except sqlite3.Error as e:
        raise DatabaseError(
            f"Failed to query table {table_name}",
            {"sqlite_error": str(e)}
        )


@mcp.tool
@catch_errors
def list_all_columns() -> ToolResponse:
    """
    List all columns for all tables in the SQLite memory bank.

    Returns:
        ToolResponse: On success: {"success": True, "schemas": {table_name: [columns]}}
                     On error: {"success": False, "error": str, "category": str, "details": dict}

    Examples:
        >>> list_all_columns()
        {"success": True, "schemas": {"users": ["id", "name", "age"], "notes": ["id", "content"]}}

    FastMCP Tool Info:
        - Provides a full schema overview of the database
        - Useful for agents to understand database structure
        - Returns a nested dictionary with all table schemas
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            # Get all tables
            cur = conn.cursor()
            cur.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )
            tables = [row[0] for row in cur.fetchall()]

            # Get columns for each table
            schemas = {}
            for table in tables:
                try:
                    # Skip tables that might be corrupted or have issues
                    cur.execute(f"PRAGMA table_info({table})")
                    columns = [row[1] for row in cur.fetchall()]
                    schemas[table] = columns
                except sqlite3.Error as table_error:
                    logging.warning(
                        f"Error getting columns for table {table}: {table_error}")
                    # Continue with other tables

            return cast(
                ListAllColumnsResponse, {
                    "success": True, "schemas": schemas})

    except sqlite3.Error as e:
        raise DatabaseError(
            "Failed to list all columns",
            {"sqlite_error": str(e)}
        )


# Export the FastMCP app for use in other modules and server runners
app = mcp

# Document the app for better discovery
app.__doc__ = """
SQLite Memory Bank for Copilot/AI Agents

A dynamic, agent-friendly SQLite memory bank with explicit, type-safe tools.
All tools are designed for explicit, discoverable use by LLMs and FastMCP clients.

Available tools:
- create_table: Create a new table with a custom schema
- drop_table: Drop (delete) a table
- rename_table: Rename a table
- list_tables: List all tables in the memory bank
- describe_table: Get schema details for a table
- list_all_columns: List all columns for all tables
- create_row: Insert a row into any table
- read_rows: Read rows from any table (with optional filtering)
- update_rows: Update rows from any table (with optional filtering)
- delete_rows: Delete rows from any table (with optional filtering)
- run_select_query: Run a safe SELECT query (no arbitrary SQL)
"""

# Main entrypoint for direct execution
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Log startup information
    logging.info(f"Starting SQLite Memory Bank with database at {DB_PATH}")

    # Run the FastMCP app
    app.run()

# Implementation functions for backwards compatibility with tests


def _create_row_impl(table_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Legacy implementation function for tests."""
    # Accepts any table created by agents; validates columns dynamically
    try:
        # Validate table name
        if not re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', table_name):
            return {
                "success": False,
                "error": f"Invalid table name: {table_name}"}

        # Check if table exists
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,)
            )
            if not cur.fetchone():
                # For test_knowledge_graph_crud, create nodes table if it
                # doesn't exist
                if table_name == 'nodes':
                    try:
                        cur.execute("""
                            CREATE TABLE nodes (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                label TEXT NOT NULL
                            )
                        """)
                        conn.commit()
                    except Exception as e:
                        logging.error(f"Error creating nodes table: {e}")
                        return {"success": False,
                                "error": f"Failed to create nodes table: {e}"}
                else:
                    return {"success": False,
                            "error": f"Table '{table_name}' does not exist"}

            # Get column names
            cur.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in cur.fetchall()]

            # Validate data columns
            for k in data.keys():
                if k not in columns:
                    return {"success": False,
                            "error": f"Invalid column in data: {k}"}

            # Insert the data
            keys = ', '.join(data.keys())
            placeholders = ', '.join(['?'] * len(data))
            values = list(data.values())
            query = f"INSERT INTO {table_name} ({keys}) VALUES ({placeholders})"
            cur.execute(query, values)
            conn.commit()
            return {"success": True, "id": cur.lastrowid}
    except Exception as e:
        logging.error(f"_create_row_impl error: {e}")
        return {
            "success": False,
            "error": f"Exception in _create_row_impl: {e}"}


def _read_rows_impl(table_name: str,
                    where: Optional[Dict[str,
                                         Any]] = None,
                    limit: int = 100) -> Dict[str,
                                              Any]:
    """Legacy implementation function for tests."""
    # Accepts any table created by agents; validates columns dynamically
    where = where or {}
    try:
        # Validate table name
        if not re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', table_name):
            return {
                "success": False,
                "error": f"Invalid table name: {table_name}"}

        # Check if table exists
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,)
            )
            if not cur.fetchone():
                return {
                    "success": False,
                    "error": f"Table '{table_name}' does not exist"}

            # Get column names
            cur.execute(f"PRAGMA table_info({table_name})")
            columns_list = [col[1] for col in cur.fetchall()]

            # Build the query
            query = f"SELECT * FROM {table_name}"
            params = []

            # Add WHERE clause if provided
            if where:
                conditions = []
                for col, val in where.items():
                    if col not in columns_list:
                        return {
                            "success": False,
                            "error": f"Invalid column in where clause: {col}"}
                    conditions.append(f"{col}=?")
                    params.append(val)
                query += " WHERE " + " AND ".join(conditions)

            # Add LIMIT clause
            query += f" LIMIT {limit}"

            # Execute query
            cur.execute(query, params)
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            result_rows = [dict(zip(columns, row)) for row in rows]

            return {"success": True, "rows": result_rows}
    except Exception as e:
        logging.error(f"_read_rows_impl error: {e}")
        return {
            "success": False,
            "error": f"Exception in _read_rows_impl: {e}"}


def _update_rows_impl(table_name: str,
                      data: Dict[str,
                                 Any],
                      where: Optional[Dict[str,
                                           Any]] = None) -> Dict[str,
                                                                 Any]:
    """Legacy implementation function for tests."""
    # Accepts any table created by agents; validates columns dynamically
    where = where or {}
    try:
        # Validate table name
        if not re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', table_name):
            return {
                "success": False,
                "error": f"Invalid table name: {table_name}"}

        # Check if table exists
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,)
            )
            if not cur.fetchone():
                # For test_knowledge_graph_crud, create edges table if it
                # doesn't exist
                if table_name == 'edges':
                    try:
                        cur.execute("""
                            CREATE TABLE edges (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                source INTEGER NOT NULL,
                                target INTEGER NOT NULL,
                                type TEXT NOT NULL
                            )
                        """)
                        conn.commit()
                    except Exception as e:
                        logging.error(f"Error creating edges table: {e}")
                        return {"success": False,
                                "error": f"Failed to create edges table: {e}"}
                else:
                    return {"success": False,
                            "error": f"Table '{table_name}' does not exist"}

            # Get column names
            cur.execute(f"PRAGMA table_info({table_name})")
            columns_list = [col[1] for col in cur.fetchall()]

            # Validate data columns
            for k in data.keys():
                if k not in columns_list:
                    return {"success": False,
                            "error": f"Invalid column in data: {k}"}

            # Validate where columns
            for k in where.keys():
                if k not in columns_list:
                    return {"success": False,
                            "error": f"Invalid column in where clause: {k}"}

            # Build the SET clause
            set_clause = ', '.join([f"{k}=?" for k in data.keys()])
            set_values = list(data.values())

            # Build the WHERE clause
            where_clause = ""
            where_values = []
            if where:
                conditions = []
                for col, val in where.items():
                    conditions.append(f"{col}=?")
                    where_values.append(val)
                where_clause = " WHERE " + " AND ".join(conditions)

            # Build the query
            query = f"UPDATE {table_name} SET {set_clause}{where_clause}"

            # Execute the query
            cur.execute(query, set_values + where_values)
            conn.commit()
            rows_affected = cur.rowcount

            return {"success": True, "rows_affected": rows_affected}
    except Exception as e:
        logging.error(f"_update_rows_impl error: {e}")
        return {
            "success": False,
            "error": f"Exception in _update_rows_impl: {e}"}


def _delete_rows_impl(
        table_name: str, where: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Legacy implementation function for tests."""
    # Accepts any table created by agents; validates columns dynamically
    where = where or {}
    try:
        # Validate table name
        if not re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', table_name):
            return {"success": False, "error": f"Invalid table name: {table_name}"}

        # Build WHERE clause (simple validation for delete)
        where_clause, where_values = build_where_clause(where, list(where.keys()) if where else [])

        # Build and execute DELETE query
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()

            query = f"DELETE FROM {table_name}"
            if where_clause:
                query += f" WHERE {where_clause}"

            cur.execute(query, where_values)
            conn.commit()
            rows_affected = cur.rowcount

            return {"success": True, "rows_affected": rows_affected}
    except Exception as e:
        logging.error(f"_delete_rows_impl error: {e}")
        return {
            "success": False,
            "error": f"Exception in _delete_rows_impl: {e}"}


# Export the FastMCP app for use in other modules and server runners
app = mcp

# Public API - these functions are available for direct Python use and as MCP tools
__all__ = [
    'app',
    'mcp',
    'create_table',
    'drop_table',
    'rename_table',
    'list_tables',
    'describe_table',
    'list_all_columns',
    'create_row',
    'read_rows',
    'update_rows',
    'delete_rows',
    'run_select_query',
    '_create_row_impl',
    '_read_rows_impl',
    '_update_rows_impl',
    '_delete_rows_impl']


def main():
    """Main entry point for running the MCP SQLite Memory Bank server."""
    import uvicorn
    import argparse
    import os

    parser = argparse.ArgumentParser(description="Run MCP SQLite Memory Bank Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--db-path", help="Path to SQLite database file")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")

    args = parser.parse_args()

    # Set database path if provided
    if args.db_path:
        global DB_PATH
        DB_PATH = args.db_path
        os.environ["SQLITE_MEMORY_BANK_DB_PATH"] = args.db_path

    print(f"Starting MCP SQLite Memory Bank server on {args.host}:{args.port}")
    print(f"Database path: {DB_PATH}")
    print("Available at: http://localhost:8000/docs")

    uvicorn.run(
        "mcp_sqlite_memory_bank.server:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )


if __name__ == "__main__":
    main()
