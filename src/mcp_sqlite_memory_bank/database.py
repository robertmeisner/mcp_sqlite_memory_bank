"""
Database abstraction layer for SQLite Memory Bank using SQLAlchemy Core.

This module provides a clean, type-safe abstraction over SQLite operations,
dramatically simplifying the complex database logic in server.py.

Author: Robert Meisner
"""

import os
import logging
from functools import wraps
from typing import Dict, List, Any, Optional, Callable
from sqlalchemy import create_engine, MetaData, Table, select, insert, update, delete, text, inspect, and_, or_
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager

from .types import ValidationError, DatabaseError, SchemaError, ToolResponse


class SQLiteMemoryDatabase:
    """
    SQLAlchemy Core-based database abstraction for SQLite Memory Bank.

    This class handles all database operations with automatic:
    - Connection management
    - Error handling and translation
    - SQL injection protection
    - Type conversion
    - Transaction management
    """

    def __init__(self, db_path: str):
        """Initialize database connection and metadata."""
        self.db_path = os.path.abspath(db_path)
        self.engine: Engine = create_engine(f"sqlite:///{self.db_path}", echo=False)
        self.metadata = MetaData()

        # Ensure database directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        # Initialize connection
        self._refresh_metadata()

    def close(self) -> None:
        """Close all database connections and dispose of the engine."""
        try:
            if hasattr(self, "engine"):
                self.engine.dispose()
        except Exception as e:
            logging.warning(f"Error closing database: {e}")

    def __del__(self):
        """Ensure cleanup when object is garbage collected."""
        self.close()

    def _refresh_metadata(self) -> None:
        """Refresh metadata to reflect current database schema."""
        try:
            self.metadata.clear()
            self.metadata.reflect(bind=self.engine)
        except SQLAlchemyError as e:
            logging.warning(f"Failed to refresh metadata: {e}")

    @contextmanager
    def get_connection(self):
        """Get a database connection with automatic cleanup."""
        conn = self.engine.connect()
        try:
            yield conn
        finally:
            conn.close()

    def _ensure_table_exists(self, table_name: str) -> Table:
        """Get table metadata, refreshing if needed.
        Raises ValidationError if not found.
        """
        if table_name not in self.metadata.tables:
            self._refresh_metadata()

        if table_name not in self.metadata.tables:
            raise ValidationError(f"Table '{table_name}' does not exist")

        return self.metadata.tables[table_name]

    def _validate_columns(self, table: Table, column_names: List[str], context: str = "operation") -> None:
        """Validate that all column names exist in the table."""
        valid_columns = set(col.name for col in table.columns)
        for col_name in column_names:
            if col_name not in valid_columns:
                raise ValidationError(f"Invalid column '{col_name}' for table " f"'{table.name}' in {context}")

    def _build_where_conditions(self, table: Table, where: Dict[str, Any]) -> List:
        """Build SQLAlchemy WHERE conditions from a dictionary."""
        if not where:
            return []

        self._validate_columns(table, list(where.keys()), "WHERE clause")
        return [table.c[col_name] == value for col_name, value in where.items()]

    def _execute_with_commit(self, stmt) -> Any:
        """Execute a statement with automatic connection mgmt and commit."""
        with self.get_connection() as conn:
            result = conn.execute(stmt)
            conn.commit()
            return result

    def _database_operation(self, operation_name: str):
        """Decorator for database operations with standardized error handling."""

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> ToolResponse:
                try:
                    return func(*args, **kwargs)
                except (ValidationError, SchemaError) as e:
                    raise e
                except SQLAlchemyError as e:
                    raise DatabaseError(f"Failed to {operation_name}: {str(e)}")

            return wrapper

        return decorator

    def create_table(self, table_name: str, columns: List[Dict[str, str]]) -> ToolResponse:
        """Create a new table with the specified columns."""
        # Input validation
        if not table_name or not table_name.isidentifier():
            raise ValidationError(f"Invalid table name: {table_name}")
        if not columns:
            raise ValidationError("Must provide at least one column")

        # Validate column definitions
        for col_def in columns:
            if "name" not in col_def or "type" not in col_def:
                raise ValidationError(f"Column must have 'name' and 'type': {col_def}")
            if not col_def["name"].isidentifier():
                raise ValidationError(f"Invalid column name: {col_def['name']}")

        try:
            # Use raw SQL for full SQLite type support
            col_defs = ", ".join([f"{col['name']} {col['type']}" for col in columns])
            sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({col_defs})"

            with self.get_connection() as conn:
                conn.execute(text(sql))
                conn.commit()

            self._refresh_metadata()
            return {"success": True}

        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to create table {table_name}: {str(e)}")

    def list_tables(self) -> ToolResponse:
        """List all user-created tables."""
        try:
            with self.get_connection() as conn:
                inspector = inspect(conn)
                tables = [name for name in inspector.get_table_names() if not name.startswith("sqlite_")]
            return {"success": True, "tables": tables}
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to list tables: {str(e)}")

    def describe_table(self, table_name: str) -> ToolResponse:
        """Get detailed schema information for a table."""
        try:
            table = self._ensure_table_exists(table_name)
            columns = [
                {
                    "name": col.name,
                    "type": str(col.type),
                    "nullable": col.nullable,
                    "default": col.default,
                    "primary_key": col.primary_key,
                }
                for col in table.columns
            ]
            return {"success": True, "columns": columns}
        except (ValidationError, SQLAlchemyError) as e:
            if isinstance(e, ValidationError):
                raise e
            raise DatabaseError(f"Failed to describe table {table_name}: {str(e)}")

    def drop_table(self, table_name: str) -> ToolResponse:
        """Drop a table."""
        try:
            self._ensure_table_exists(table_name)  # Validates existence
            self._execute_with_commit(text(f"DROP TABLE {table_name}"))
            self._refresh_metadata()
            return {"success": True}
        except (ValidationError, SQLAlchemyError) as e:
            if isinstance(e, ValidationError):
                raise e
            raise DatabaseError(f"Failed to drop table {table_name}: {str(e)}")

    def rename_table(self, old_name: str, new_name: str) -> ToolResponse:
        """Rename a table."""
        if old_name == new_name:
            raise ValidationError("Old and new table names are identical")

        try:
            self._ensure_table_exists(old_name)  # Validates old table exists

            # Check if new name already exists
            with self.get_connection() as conn:
                inspector = inspect(conn)
                if new_name in inspector.get_table_names():
                    raise ValidationError(f"Table '{new_name}' already exists")

                conn.execute(text(f"ALTER TABLE {old_name} RENAME TO {new_name}"))
                conn.commit()

            self._refresh_metadata()
            return {"success": True}
        except (ValidationError, SQLAlchemyError) as e:
            if isinstance(e, ValidationError):
                raise e
            raise DatabaseError(f"Failed to rename table from {old_name} to {new_name}: {str(e)}")

    def insert_row(self, table_name: str, data: Dict[str, Any]) -> ToolResponse:
        """Insert a row into a table."""
        if not data:
            raise ValidationError("Data cannot be empty")

        try:
            table = self._ensure_table_exists(table_name)
            self._validate_columns(table, list(data.keys()), "insert operation")

            result = self._execute_with_commit(insert(table).values(**data))
            return {"success": True, "id": result.lastrowid}
        except (ValidationError, SQLAlchemyError) as e:
            if isinstance(e, ValidationError):
                raise e
            raise DatabaseError(f"Failed to insert into table {table_name}: {str(e)}")

    def read_rows(self, table_name: str, where: Optional[Dict[str, Any]] = None, limit: Optional[int] = None) -> ToolResponse:
        """Read rows from a table with optional filtering."""
        try:
            table = self._ensure_table_exists(table_name)
            stmt = select(table)

            # Apply WHERE conditions
            conditions = self._build_where_conditions(table, where or {})
            if conditions:
                stmt = stmt.where(and_(*conditions))

            # Apply LIMIT
            if limit:
                stmt = stmt.limit(limit)

            with self.get_connection() as conn:
                result = conn.execute(stmt)
                rows = [dict(row._mapping) for row in result.fetchall()]

            return {"success": True, "rows": rows}
        except (ValidationError, SQLAlchemyError) as e:
            if isinstance(e, ValidationError):
                raise e
            raise DatabaseError(f"Failed to read from table {table_name}: {str(e)}")

    def update_rows(self, table_name: str, data: Dict[str, Any], where: Optional[Dict[str, Any]] = None) -> ToolResponse:
        """Update rows in a table."""
        if not data:
            raise ValidationError("Update data cannot be empty")

        try:
            table = self._ensure_table_exists(table_name)
            self._validate_columns(table, list(data.keys()), "update operation")

            stmt = update(table).values(**data)

            # Apply WHERE conditions
            conditions = self._build_where_conditions(table, where or {})
            if conditions:
                stmt = stmt.where(and_(*conditions))

            result = self._execute_with_commit(stmt)
            return {"success": True, "rows_affected": result.rowcount}
        except (ValidationError, SQLAlchemyError) as e:
            if isinstance(e, ValidationError):
                raise e
            raise DatabaseError(f"Failed to update table {table_name}: {str(e)}")

    def delete_rows(self, table_name: str, where: Optional[Dict[str, Any]] = None) -> ToolResponse:
        """Delete rows from a table."""
        try:
            table = self._ensure_table_exists(table_name)
            stmt = delete(table)

            # Apply WHERE conditions
            conditions = self._build_where_conditions(table, where or {})
            if conditions:
                stmt = stmt.where(and_(*conditions))
            else:
                logging.warning(f"delete_rows called without WHERE clause on table {table_name}")

            result = self._execute_with_commit(stmt)
            return {"success": True, "rows_affected": result.rowcount}
        except (ValidationError, SQLAlchemyError) as e:
            if isinstance(e, ValidationError):
                raise e
            raise DatabaseError(f"Failed to delete from table {table_name}: {str(e)}")

    def select_query(
        self, table_name: str, columns: Optional[List[str]] = None, where: Optional[Dict[str, Any]] = None, limit: int = 100
    ) -> ToolResponse:
        """Run a SELECT query with specified columns and conditions."""
        if limit < 1:
            raise ValidationError("Limit must be a positive integer")

        try:
            table = self._ensure_table_exists(table_name)

            # Build SELECT columns
            if columns:
                self._validate_columns(table, columns, "SELECT operation")
                select_columns = [table.c[col_name] for col_name in columns]
                stmt = select(*select_columns)
            else:
                stmt = select(table)

            # Apply WHERE conditions
            conditions = self._build_where_conditions(table, where or {})
            if conditions:
                stmt = stmt.where(and_(*conditions))

            stmt = stmt.limit(limit)

            with self.get_connection() as conn:
                result = conn.execute(stmt)
                rows = [dict(row._mapping) for row in result.fetchall()]

            return {"success": True, "rows": rows}
        except (ValidationError, SQLAlchemyError) as e:
            if isinstance(e, ValidationError):
                raise e
            raise DatabaseError(f"Failed to query table {table_name}: {str(e)}")

    def list_all_columns(self) -> ToolResponse:
        """List all columns for all tables."""
        try:
            self._refresh_metadata()
            schemas = {table_name: [col.name for col in table.columns] for table_name, table in self.metadata.tables.items()}
            return {"success": True, "schemas": schemas}
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to list all columns: {str(e)}")

    def search_content(self, query: str, tables: Optional[List[str]] = None, limit: int = 50) -> ToolResponse:
        """Perform full-text search across table content."""
        if not query or not query.strip():
            raise ValidationError("Search query cannot be empty")
        if limit < 1:
            raise ValidationError("Limit must be a positive integer")

        try:
            self._refresh_metadata()
            search_tables = tables or list(self.metadata.tables.keys())
            results = []

            with self.get_connection() as conn:
                for table_name in search_tables:
                    if table_name not in self.metadata.tables:
                        continue

                    table = self.metadata.tables[table_name]
                    text_columns = [
                        col for col in table.columns if "TEXT" in str(col.type).upper() or "VARCHAR" in str(col.type).upper()
                    ]

                    if not text_columns:
                        continue

                    # Build search conditions and execute
                    conditions = [col.like(f"%{query}%") for col in text_columns]
                    stmt = select(table).where(or_(*conditions)).limit(limit)

                    for row in conn.execute(stmt).fetchall():
                        row_dict = dict(row._mapping)

                        # Calculate relevance and matched content
                        relevance = 0.0
                        matched_content = []
                        query_lower = query.lower()

                        for col in text_columns:
                            if col.name in row_dict and row_dict[col.name]:
                                content = str(row_dict[col.name]).lower()
                                if query_lower in content:
                                    frequency = content.count(query_lower)
                                    relevance += frequency / len(content)
                                    matched_content.append(f"{col.name}: {row_dict[col.name]}")

                        if relevance > 0:
                            results.append(
                                {
                                    "table": table_name,
                                    "row_id": row_dict.get("id"),
                                    "row_data": row_dict,
                                    "matched_content": matched_content,
                                    "relevance": round(relevance, 3),
                                }
                            )

            # Sort by relevance and limit results
            results.sort(key=lambda x: x["relevance"], reverse=True)
            results = results[:limit]

            return {
                "success": True,
                "results": results,
                "query": query,
                "tables_searched": search_tables,
                "total_results": len(results),
            }
        except (ValidationError, SQLAlchemyError) as e:
            if isinstance(e, ValidationError):
                raise e
            raise DatabaseError(f"Failed to search content: {str(e)}")

    def explore_tables(self, pattern: Optional[str] = None, include_row_counts: bool = True) -> ToolResponse:
        """Explore table structures and content."""
        try:
            self._refresh_metadata()
            table_names = list(self.metadata.tables.keys())

            if pattern:
                table_names = [name for name in table_names if pattern.replace("%", "") in name]

            exploration = {"tables": [], "total_tables": len(table_names), "total_rows": 0}

            with self.get_connection() as conn:
                for table_name in table_names:
                    table = self.metadata.tables[table_name]

                    # Build column info and identify text columns
                    columns = []
                    text_columns = []

                    for col in table.columns:
                        col_data = {
                            "name": col.name,
                            "type": str(col.type),
                            "nullable": col.nullable,
                            "default": col.default,
                            "primary_key": col.primary_key,
                        }
                        columns.append(col_data)

                        if "TEXT" in str(col.type).upper() or "VARCHAR" in str(col.type).upper():
                            text_columns.append(col.name)

                    table_info = {"name": table_name, "columns": columns, "text_columns": text_columns}

                    # Add row count if requested
                    if include_row_counts:
                        count_result = conn.execute(select(text("COUNT(*)")).select_from(table))
                        row_count = count_result.scalar()
                        table_info["row_count"] = row_count
                        exploration["total_rows"] += row_count

                    # Add sample data
                    sample_result = conn.execute(select(table).limit(3))
                    sample_rows = [dict(row._mapping) for row in sample_result.fetchall()]
                    if sample_rows:
                        table_info["sample_data"] = sample_rows

                    # Add content preview for text columns
                    if text_columns:
                        content_preview = {}
                        for col_name in text_columns[:3]:  # Limit to first 3 text columns
                            col = table.c[col_name]
                            preview_result = conn.execute(select(col).distinct().where(col.isnot(None)).limit(5))
                            unique_values = [row[0] for row in preview_result.fetchall() if row[0]]
                            if unique_values:
                                content_preview[col_name] = unique_values

                        if content_preview:
                            table_info["content_preview"] = content_preview

                    exploration["tables"].append(table_info)

            return {"success": True, "exploration": exploration}
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to explore tables: {str(e)}")


# Global database instance
_db_instance: Optional[SQLiteMemoryDatabase] = None


def get_database(db_path: Optional[str] = None) -> SQLiteMemoryDatabase:
    """Get or create the global database instance."""
    global _db_instance

    actual_path = db_path or os.environ.get("DB_PATH", "./test.db")
    if _db_instance is None or (db_path and db_path != _db_instance.db_path):
        # Close previous instance if it exists
        if _db_instance is not None:
            _db_instance.close()
        _db_instance = SQLiteMemoryDatabase(actual_path)

    return _db_instance
