"""
Utility functions for SQLite Memory Bank.

This module provides common functionality used across the project,
including validation, error handling, and database utilities.
"""

import re
import os
import sqlite3
import logging
from functools import wraps
from typing import Any, Callable, Dict, List, TypeVar, cast, Union, Tuple
from .types import ValidationError, DatabaseError, SchemaError, MemoryBankError, ToolResponse

T = TypeVar("T", bound=Callable[..., ToolResponse])


def catch_errors(f: T) -> T:
    """
    Decorator to standardize error handling across tools.
    Catches exceptions and converts them to appropriate error responses.
    """

    @wraps(f)
    def wrapper(*args: Any, **kwargs: Any) -> ToolResponse:
        try:
            return f(*args, **kwargs)
        except MemoryBankError as e:
            logging.error(f"{f.__name__} error: {e}")
            return cast(ToolResponse, e.to_dict())
        except sqlite3.Error as e:
            logging.error(f"{f.__name__} database error: {e}")
            return cast(
                ToolResponse, DatabaseError(f"Database error in {f.__name__}: {e}", {"sqlite_error": str(e)}).to_dict()
            )
        except Exception as e:
            logging.error(f"Unexpected error in {f.__name__}: {e}")
            return cast(ToolResponse, DatabaseError(f"Unexpected error in {f.__name__}: {e}").to_dict())

    return cast(T, wrapper)


def validate_identifier(name: str, context: str = "identifier") -> None:
    """
    Validate that a string is a valid SQLite identifier (table/column name).
    Raises ValidationError if invalid.

    Args:
        name: The identifier to validate
        context: Description of what's being validated (for error messages)
    """
    if not bool(re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", name)):
        raise ValidationError(
            f"Invalid {context}: {name}. Must start with letter/underscore and "
            f"contain only letters, numbers, underscores.",
            {"invalid_name": name},
        )


def validate_column_definition(column: Dict[str, Any]) -> None:
    """
    Validate a column definition dictionary.
    Raises ValidationError if invalid.

    Args:
        column: Dictionary with column definition (must have 'name' and 'type' keys)
    """
    if not isinstance(column, dict):
        raise ValidationError("Column definition must be a dictionary", {"received": str(type(column))})
    if "name" not in column or "type" not in column:
        raise ValidationError(
            "Column definition must have 'name' and 'type' keys",
            {"missing_keys": [k for k in ["name", "type"] if k not in column]},
        )
    validate_identifier(column["name"], "column name")


def get_table_columns(conn: sqlite3.Connection, table_name: str) -> List[str]:
    """
    Get list of column names for a table.
    Raises SchemaError if table doesn't exist.

    Args:
        conn: SQLite connection
        table_name: Name of table to check

    Returns:
        List of column names
    """
    validate_identifier(table_name, "table name")
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cur.fetchall()]
    if not columns:
        raise SchemaError(f"Table does not exist: {table_name}", {"table_name": table_name})
    return columns


# Compatibility function for direct table_name usage


def get_table_columns_by_name(table_name: str) -> Union[List[str], Dict[str, Any]]:
    """
    Get list of column names for a table by name.
    Compatibility function for the old implementation.

    Args:
        table_name: Name of table to check

    Returns:
        List of column names or error dict
    """
    try:
        validate_identifier(table_name, "table name")
        with sqlite3.connect(os.environ.get("DB_PATH", "./test.db")) as conn:
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            if not cur.fetchone():
                return {"success": False, "error": f"Table '{table_name}' does not exist"}

            # Get column information
            cur.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in cur.fetchall()]
            return columns
    except MemoryBankError as e:
        return e.to_dict()
    except Exception as e:
        return {"success": False, "error": f"Exception in get_table_columns: {e}"}


def validate_table_exists(conn: sqlite3.Connection, table_name: str) -> None:
    """
    Validate that a table exists.
    Raises SchemaError if it doesn't.

    Args:
        conn: SQLite connection
        table_name: Name of table to check
    """
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    if not cur.fetchone():
        raise SchemaError(f"Table does not exist: {table_name}", {"table_name": table_name})


def build_where_clause(where: Dict[str, Any], valid_columns: List[str]) -> Union[Tuple[str, list], Dict[str, Any]]:
    """
    Build a WHERE clause from a dictionary of column-value pairs.

    Args:
        where: Dictionary of {column: value} pairs
        valid_columns: List of valid column names for validation

    Returns:
        Tuple of (where_clause, parameter_values) or error dict if validation fails
    """
    if not where:
        return "", []

    try:
        # Validate column names
        conditions = []
        values = []

        for col, val in where.items():
            if col not in valid_columns:
                return {"success": False, "error": f"Invalid column in where clause: {col}"}
            conditions.append(f"{col}=?")
            values.append(val)

        clause = " AND ".join(conditions)
        return clause, values
    except Exception as e:
        logging.error(f"Error in build_where_clause: {e}")
        return {"success": False, "error": f"Error building WHERE clause: {e}"}
