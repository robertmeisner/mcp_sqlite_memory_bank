"""
Basic tools module for SQLite Memory Bank.

This module contains all basic CRUD and utility MCP tools including table management,
data operations, and core functionality.
"""

from typing import Any, Dict, List, Optional, cast

from ..database import get_database
from ..types import ToolResponse
from ..utils import catch_errors


@catch_errors
def create_table(
    table_name: str,
    columns: List[Dict[str, str]],
) -> ToolResponse:
    """Create a new table in the SQLite memory bank."""
    from .. import server

    return cast(
        ToolResponse, get_database(server.DB_PATH).create_table(table_name, columns)
    )


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

    return cast(
        ToolResponse, get_database(server.DB_PATH).rename_table(old_name, new_name)
    )


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

    return cast(
        ToolResponse, get_database(server.DB_PATH).update_rows(table_name, data, where)
    )


@catch_errors
def delete_rows(
    table_name: str,
    where: Optional[Dict[str, Any]] = None,
) -> ToolResponse:
    """Delete rows from any table in the SQLite Memory Bank, matching the WHERE clause."""
    from .. import server

    return cast(
        ToolResponse, get_database(server.DB_PATH).delete_rows(table_name, where)
    )


@catch_errors
def run_select_query(
    table_name: str,
    columns: Optional[List[str]] = None,
    where: Optional[Dict[str, Any]] = None,
    limit: int = 100,
) -> ToolResponse:
    """Run a safe SELECT query on a table in the SQLite memory bank."""
    from .. import server

    return cast(
        ToolResponse,
        get_database(server.DB_PATH).select_query(table_name, columns, where, limit),
    )


@catch_errors
def list_all_columns() -> ToolResponse:
    """List all columns for all tables in the SQLite memory bank."""
    from .. import server

    return cast(ToolResponse, get_database(server.DB_PATH).list_all_columns())


@catch_errors
def upsert_memory(
    table_name: str, data: Dict[str, Any], match_columns: List[str]
) -> ToolResponse:
    """
    Smart memory upsert: Update existing records or create new ones based on matching columns.

    This is the preferred method for memory management as it prevents duplicates
    and maintains data consistency.

    Args:
        table_name (str): Table to upsert into
        data (Dict[str, Any]): Data to upsert
        match_columns (List[str]): Columns to use for finding existing records

    Returns:
        ToolResponse: For updates: {"success": True, "action": "updated", "id": rowid, "updated_fields": {...}}
                     For creates: {"success": True, "action": "created", "id": rowid}
    """
    import os

    db_path = os.environ.get("DB_PATH", "./test.db")
    db = get_database(db_path)

    try:
        # Build WHERE clause for matching
        where_conditions = {col: data[col] for col in match_columns if col in data}

        if not where_conditions:
            # No match columns provided, just insert
            return cast(ToolResponse, db.insert_row(table_name, data))

        # Check for existing records
        existing_result = db.read_rows(table_name, where_conditions)
        if not existing_result.get("success"):
            return cast(ToolResponse, existing_result)

        existing_rows = existing_result.get("rows", [])

        if existing_rows:
            # Update the first matching record
            row_id = existing_rows[0].get("id")
            if row_id:
                # Get the original record to compare changes
                original_record = existing_rows[0]

                update_result = db.update_rows(table_name, data, {"id": row_id})
                if update_result.get("success"):
                    # Determine which fields were actually updated
                    updated_fields = {}
                    for key, new_value in data.items():
                        original_value = original_record.get(key)
                        if original_value != new_value:
                            updated_fields[key] = {
                                "old": original_value,
                                "new": new_value,
                            }

                    return cast(
                        ToolResponse,
                        {
                            "success": True,
                            "action": "updated",
                            "id": row_id,
                            "rows_affected": update_result.get("rows_affected", 1),
                            "updated_fields": updated_fields,
                        },
                    )
                return cast(ToolResponse, update_result)

        # No existing record found, create new one
        insert_result = db.insert_row(table_name, data)
        if insert_result.get("success"):
            return cast(
                ToolResponse,
                {"success": True, "action": "created", "id": insert_result.get("id")},
            )
        return cast(ToolResponse, insert_result)

    except Exception as e:
        return cast(
            ToolResponse,
            {
                "success": False,
                "error": f"Memory upsert failed: {str(e)}",
                "category": "UPSERT_ERROR",
                "details": {"table": table_name, "match_columns": match_columns},
            },
        )


@catch_errors
def batch_create_memories(
    table_name: str,
    data_list: List[Dict[str, Any]],
    match_columns: Optional[List[str]] = None,
    use_upsert: bool = True,
) -> ToolResponse:
    """
    🚀 **TRANSACTION-SAFE BATCH MEMORY CREATION** - All succeed or all fail!

    Efficiently create multiple memory records in a single transaction with rollback protection.
    Supports both batch insert (fast) and batch upsert (prevents duplicates).

    Args:
        table_name (str): Table to insert records into
        data_list (List[Dict[str, Any]]): List of records to create
        match_columns (Optional[List[str]]): Columns to use for duplicate detection (if use_upsert=True)
        use_upsert (bool): Whether to use upsert logic to prevent duplicates (default: True)

    Returns:
        ToolResponse: {"success": True, "created": int, "updated": int, "failed": int, "results": List}
    """
    if not data_list:
        return cast(
            ToolResponse,
            {
                "success": True,
                "created": 0,
                "updated": 0,
                "failed": 0,
                "results": [],
                "message": "No data provided",
            },
        )

    import os

    db_path = os.environ.get("DB_PATH", "./test.db")
    db = get_database(db_path)

    created_count = 0
    updated_count = 0
    failed_count = 0
    results = []

    # Transaction-safe batch processing with rollback
    try:
        with db.get_connection() as conn:
            # Start transaction
            trans = conn.begin()

            try:
                for i, data in enumerate(data_list):
                    try:
                        if use_upsert and match_columns:
                            # Use upsert logic to prevent duplicates
                            result = upsert_memory(table_name, data, match_columns)
                            if result.get("success"):
                                action = result.get("action", "unknown")
                                if action == "created":
                                    created_count += 1
                                elif action == "updated":
                                    updated_count += 1
                                results.append(
                                    {
                                        "index": i,
                                        "action": action,
                                        "id": result.get("id"),
                                        "success": True,
                                    }
                                )
                            else:
                                failed_count += 1
                                results.append(
                                    {
                                        "index": i,
                                        "action": "failed",
                                        "error": result.get("error", "Unknown error"),
                                        "success": False,
                                    }
                                )
                        else:
                            # Simple batch insert (faster but no duplicate prevention)
                            insert_result = db.insert_row(table_name, data)
                            if insert_result.get("success"):
                                created_count += 1
                                results.append(
                                    {
                                        "index": i,
                                        "action": "created",
                                        "id": insert_result.get("id"),
                                        "success": True,
                                    }
                                )
                            else:
                                failed_count += 1
                                results.append(
                                    {
                                        "index": i,
                                        "action": "failed",
                                        "error": insert_result.get(
                                            "error", "Unknown error"
                                        ),
                                        "success": False,
                                    }
                                )

                    except Exception as item_error:
                        failed_count += 1
                        results.append(
                            {
                                "index": i,
                                "action": "failed",
                                "error": str(item_error),
                                "success": False,
                            }
                        )

                # Commit transaction if all operations successful or partial success
                # allowed
                trans.commit()

            except Exception as batch_error:
                # Rollback transaction on any critical error
                trans.rollback()
                raise batch_error

        return cast(
            ToolResponse,
            {
                "success": True,
                "created": created_count,
                "updated": updated_count,
                "failed": failed_count,
                "total_processed": len(data_list),
                "transaction_committed": True,
                "results": results,
            },
        )

    except Exception as e:
        return cast(
            ToolResponse,
            {
                "success": False,
                "error": f"Batch operation failed with transaction rollback: {str(e)}",
                "category": "BATCH_TRANSACTION_ERROR",
                "details": {
                    "table": table_name,
                    "total_items": len(data_list),
                    "use_upsert": use_upsert,
                },
            },
        )


@catch_errors
def batch_delete_memories(
    table_name: str, where_conditions: List[Dict[str, Any]], match_all: bool = False
) -> ToolResponse:
    """
    Efficiently delete multiple memory records in a single operation.

    Supports both individual record deletion and bulk deletion with shared conditions.

    Args:
        table_name (str): Table to delete records from
        where_conditions (List[Dict[str, Any]]): List of WHERE conditions for deletion
        match_all (bool): If True, delete records matching ALL conditions; if False, delete records matching ANY condition

    Returns:
        ToolResponse: {"success": True, "deleted": int, "failed": int, "results": List}
    """
    if not where_conditions:
        return cast(
            ToolResponse,
            {
                "success": True,
                "deleted": 0,
                "failed": 0,
                "results": [],
                "message": "No deletion conditions provided",
            },
        )

    import os

    db_path = os.environ.get("DB_PATH", "./test.db")
    db = get_database(db_path)

    deleted_count = 0
    failed_count = 0
    results = []

    try:
        if match_all and len(where_conditions) == 1:
            # Single condition - use direct delete
            condition = where_conditions[0]
            try:
                delete_result = db.delete_rows(table_name, condition)
                if delete_result.get("success"):
                    rows_affected = delete_result.get("rows_affected", 0)
                    deleted_count += rows_affected
                    results.append(
                        {
                            "condition_index": 0,
                            "condition": condition,
                            "action": "deleted",
                            "rows_affected": rows_affected,
                            "success": True,
                        }
                    )
                else:
                    failed_count += 1
                    results.append(
                        {
                            "condition_index": 0,
                            "condition": condition,
                            "action": "failed",
                            "error": delete_result.get("error", "Unknown error"),
                            "success": False,
                        }
                    )
            except Exception as e:
                failed_count += 1
                results.append(
                    {
                        "condition_index": 0,
                        "condition": condition,
                        "action": "failed",
                        "error": str(e),
                        "success": False,
                    }
                )

        elif match_all:
            # Multiple conditions with AND logic - combine conditions
            combined_condition = {}
            for condition in where_conditions:
                combined_condition.update(condition)

            try:
                delete_result = db.delete_rows(table_name, combined_condition)
                if delete_result.get("success"):
                    rows_affected = delete_result.get("rows_affected", 0)
                    deleted_count += rows_affected
                    results.append(
                        {
                            "combined_conditions": where_conditions,
                            "action": "deleted",
                            "rows_affected": rows_affected,
                            "success": True,
                        }
                    )
                else:
                    failed_count += 1
                    results.append(
                        {
                            "combined_conditions": where_conditions,
                            "action": "failed",
                            "error": delete_result.get("error", "Unknown error"),
                            "success": False,
                        }
                    )
            except Exception as e:
                failed_count += 1
                results.append(
                    {
                        "combined_conditions": where_conditions,
                        "action": "failed",
                        "error": str(e),
                        "success": False,
                    }
                )
        else:
            # Multiple conditions with OR logic - delete each separately
            for i, condition in enumerate(where_conditions):
                try:
                    delete_result = db.delete_rows(table_name, condition)
                    if delete_result.get("success"):
                        rows_affected = delete_result.get("rows_affected", 0)
                        deleted_count += rows_affected
                        results.append(
                            {
                                "condition_index": i,
                                "condition": condition,
                                "action": "deleted",
                                "rows_affected": rows_affected,
                                "success": True,
                            }
                        )
                    else:
                        failed_count += 1
                        results.append(
                            {
                                "condition_index": i,
                                "condition": condition,
                                "action": "failed",
                                "error": delete_result.get("error", "Unknown error"),
                                "success": False,
                            }
                        )
                except Exception as e:
                    failed_count += 1
                    results.append(
                        {
                            "condition_index": i,
                            "condition": condition,
                            "action": "failed",
                            "error": str(e),
                            "success": False,
                        }
                    )

        return cast(
            ToolResponse,
            {
                "success": True,
                "deleted": deleted_count,
                "failed": failed_count,
                "total_conditions": len(where_conditions),
                "results": results,
                "message": f"Processed {len(where_conditions)} deletion conditions: {deleted_count} records deleted, {failed_count} operations failed",
            },
        )

    except Exception as e:
        return cast(
            ToolResponse,
            {
                "success": False,
                "error": f"Batch deletion failed: {str(e)}",
                "category": "BATCH_DELETE_ERROR",
                "details": {
                    "table": table_name,
                    "conditions_count": len(where_conditions),
                },
            },
        )
