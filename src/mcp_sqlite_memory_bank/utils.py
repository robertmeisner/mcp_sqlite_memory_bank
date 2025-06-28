"""
Utility functions for SQLite Memory Bank.

This module provides common functionality used across the project,
including validation, error handling, and database utilities.
"""

import re
import os
import sqlite3
import logging
import sys
import traceback
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Dict, List, TypeVar, cast, Union, Tuple
from .types import (
    ValidationError,
    DatabaseError,
    SchemaError,
    MemoryBankError,
    ToolResponse,
)

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
                ToolResponse,
                DatabaseError(
                    f"Database error in {f.__name__}: {e}", {"sqlite_error": str(e)}
                ).to_dict(),
            )
        except Exception as e:
            logging.error(f"Unexpected error in {f.__name__}: {e}")
            return cast(
                ToolResponse,
                DatabaseError(f"Unexpected error in {f.__name__}: {e}").to_dict(),
            )

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
        raise ValidationError(
            "Column definition must be a dictionary", {"received": str(type(column))}
        )
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
        raise SchemaError(
            f"Table does not exist: {table_name}", {"table_name": table_name}
        )
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
            cur.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (table_name,),
            )
            if not cur.fetchone():
                return {
                    "success": False,
                    "error": f"Table '{table_name}' does not exist",
                }

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
    cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,)
    )
    if not cur.fetchone():
        raise SchemaError(
            f"Table does not exist: {table_name}", {"table_name": table_name}
        )


def build_where_clause(
    where: Dict[str, Any], valid_columns: List[str]
) -> Union[Tuple[str, List[Any]], Dict[str, Any]]:
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
                return {
                    "success": False,
                    "error": f"Invalid column in where clause: {col}",
                }
            conditions.append(f"{col}=?")
            values.append(val)

        clause = " AND ".join(conditions)
        return clause, values
    except Exception as e:
        logging.error(f"Error in build_where_clause: {e}")
        return {"success": False, "error": f"Error building WHERE clause: {e}"}


def suggest_recovery(error: Exception, function_name: str) -> Dict[str, Any]:
    """
    Suggest recovery actions based on the error type and context.

    Args:
        error: The exception that occurred
        function_name: Name of the function where error occurred

    Returns:
        Dictionary with recovery suggestions
    """
    suggestions = {
        "auto_recovery_available": False,
        "manual_steps": [],
        "documentation_links": [],
        "similar_errors": [],
    }

    error_str = str(error).lower()
    error_type = type(error).__name__

    # Dependency-related errors
    if "sentence-transformers" in error_str or "transformers" in error_str:
        suggestions.update(
            {
                "auto_recovery_available": True,
                "install_command": "pip install sentence-transformers",
                "manual_steps": [
                    "Install sentence-transformers: pip install sentence-transformers",
                    "Restart the MCP server",
                    "Try the semantic search operation again",
                ],
                "explanation": "Semantic search requires the sentence-transformers library",
                "fallback_available": "Keyword search is available as fallback",
            }
        )

    # Database errors
    elif "database" in error_str or "sqlite" in error_str:
        suggestions.update(
            {
                "manual_steps": [
                    "Check if database file exists and is writable",
                    "Verify disk space is available",
                    "Check if another process is using the database",
                    "Try creating a new database file",
                ],
                "auto_recovery_available": False,
                "diagnostics": {
                    "check_db_path": "Verify DB_PATH environment variable",
                    "check_permissions": "Ensure write permissions to database directory",
                },
            }
        )

    # Table/schema errors
    elif "table" in error_str and ("not exist" in error_str or "missing" in error_str):
        suggestions.update(
            {
                "auto_recovery_available": True,
                "manual_steps": [
                    "List available tables with list_tables()",
                    "Check table name spelling",
                    "Create the table if it doesn't exist",
                    "Refresh your table list",
                ],
                "next_actions": ["call list_tables() to see available tables"],
            }
        )

    # Column errors
    elif "column" in error_str and ("not exist" in error_str or "invalid" in error_str):
        suggestions.update(
            {
                "auto_recovery_available": True,
                "manual_steps": [
                    "Use describe_table() to see available columns",
                    "Check column name spelling and case",
                    "Verify the column exists in the table schema",
                ],
                "next_actions": ["call describe_table() to see column schema"],
            }
        )

    # Import/module errors
    elif "import" in error_str or "module" in error_str:
        suggestions.update(
            {
                "manual_steps": [
                    "Check if required packages are installed",
                    "Verify Python environment is correct",
                    "Try reinstalling the package",
                    "Check for version compatibility issues",
                ],
                "diagnostics": {
                    "python_version": sys.version,
                    "check_packages": "pip list | grep -E '(torch|transformers|sentence)'",
                },
            }
        )

    # Function/method errors (like our recent 'FunctionTool' issue)
    elif "not callable" in error_str or "has no attribute" in error_str:
        suggestions.update(
            {
                "manual_steps": [
                    "Check if you're using the correct function/method name",
                    "Verify the object type is what you expect",
                    "Check for import issues or namespace conflicts",
                    "Try restarting the MCP server",
                ],
                "diagnostics": {
                    "object_type": "Check the actual type of the object being called",
                    "namespace_check": "Verify imports and module loading",
                },
                "likely_causes": [
                    "Using PyPI version instead of local development code",
                    "Import conflicts between different module versions",
                    "Object not properly initialized",
                ],
            }
        )

    # Add context-specific suggestions
    if function_name.startswith("semantic") or function_name.startswith("embedding"):
        suggestions["context_help"] = {
            "semantic_search_help": "Semantic search requires sentence-transformers and embeddings to be generated",
            "embedding_help": "Use add_embeddings() and generate_embeddings() before semantic search",
            "fallback_option": "Consider using search_content() for keyword-based search",
        }

    return suggestions


def enhanced_catch_errors(
    include_traceback: bool = False, auto_recovery: bool = True
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Enhanced error decorator with debugging context and auto-recovery suggestions.

    Args:
        include_traceback: Whether to include full traceback in error details
        auto_recovery: Whether to include auto-recovery suggestions
    """

    def decorator(f: T) -> T:
        @wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> ToolResponse:
            try:
                return f(*args, **kwargs)
            except Exception as e:
                # Enhanced error context
                error_context = {
                    "function": f.__name__,
                    "timestamp": datetime.now().isoformat(),
                    "args_preview": str(args)[:200],  # Truncate for safety
                    "kwargs_preview": {k: str(v)[:100] for k, v in kwargs.items()},
                    "python_version": sys.version,
                    "error_type": type(e).__name__,
                }

                # Add traceback if requested
                if include_traceback:
                    error_context["traceback"] = traceback.format_exc()

                # Auto-recovery suggestions
                recovery_suggestions = {}
                if auto_recovery:
                    recovery_suggestions = suggest_recovery(e, f.__name__)

                # Determine error category
                if isinstance(e, MemoryBankError):
                    category = (
                        e.category.name if hasattr(e, "category") else "MEMORY_BANK"
                    )
                    return cast(
                        ToolResponse,
                        {
                            "success": False,
                            "error": str(e),
                            "category": category,
                            "details": error_context,
                            "recovery": recovery_suggestions,
                        },
                    )
                elif isinstance(e, sqlite3.Error):
                    return cast(
                        ToolResponse,
                        {
                            "success": False,
                            "error": f"Database error: {str(e)}",
                            "category": "DATABASE",
                            "details": error_context,
                            "recovery": recovery_suggestions,
                        },
                    )
                else:
                    return cast(
                        ToolResponse,
                        {
                            "success": False,
                            "error": f"Unexpected error: {str(e)}",
                            "category": "SYSTEM",
                            "details": error_context,
                            "recovery": recovery_suggestions,
                        },
                    )

        return cast(T, wrapper)

    return decorator
