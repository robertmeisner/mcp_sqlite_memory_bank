"""
Database abstraction layer for SQLite Memory Bank using SQLAlchemy Core.

This module provides a clean, type-safe abstraction over SQLite operations,
dramatically simplifying the complex database logic in server.py.

Author: Robert Meisner
"""

import os
import json
import logging
from functools import wraps
from typing import Dict, List, Any, Optional, Callable, cast
from sqlalchemy import create_engine, MetaData, Table, select, insert, update, delete, text, inspect, and_, or_
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager

from .types import (
    ValidationError,
    DatabaseError,
    SchemaError,
    ToolResponse,
    EmbeddingColumnResponse,
    GenerateEmbeddingsResponse,
    SemanticSearchResponse,
    RelatedContentResponse,
    HybridSearchResponse,
)
from .semantic import get_semantic_engine, is_semantic_search_available


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

    def read_rows(
        self, table_name: str, where: Optional[Dict[str, Any]] = None, limit: Optional[int] = None
    ) -> ToolResponse:
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

    def update_rows(
        self, table_name: str, data: Dict[str, Any], where: Optional[Dict[str, Any]] = None
    ) -> ToolResponse:
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
        self,
        table_name: str,
        columns: Optional[List[str]] = None,
        where: Optional[Dict[str, Any]] = None,
        limit: int = 100,
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
            schemas = {
                table_name: [col.name for col in table.columns] for table_name, table in self.metadata.tables.items()
            }
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
                        col
                        for col in table.columns
                        if "TEXT" in str(col.type).upper() or "VARCHAR" in str(col.type).upper()
                    ]

                    if not text_columns:
                        continue

                    # Build search conditions and execute
                    conditions = [col.like(f"%{query}%") for col in text_columns]
                    stmt = select(table).where(or_(*conditions)).limit(limit)

                    for row in conn.execute(stmt).fetchall():
                        row_dict = dict(row._mapping)

                        # Enhanced relevance calculation with multiple scoring factors
                        relevance_scores = []
                        matched_content = []
                        query_lower = query.lower()
                        query_terms = query_lower.split()

                        for col in text_columns:
                            if col.name in row_dict and row_dict[col.name]:
                                content = str(row_dict[col.name]).lower()
                                content_length = len(content)
                                
                                if query_lower in content:
                                    # Factor 1: Exact phrase frequency (weighted higher)
                                    exact_frequency = content.count(query_lower)
                                    exact_score = (exact_frequency * 2.0) / content_length if content_length > 0 else 0
                                    
                                    # Factor 2: Individual term frequency
                                    term_score = 0.0
                                    for term in query_terms:
                                        if term in content:
                                            term_score += content.count(term) / content_length if content_length > 0 else 0
                                    
                                    # Factor 3: Position bonus (early matches score higher)
                                    position_bonus = 0.0
                                    first_occurrence = content.find(query_lower)
                                    if first_occurrence != -1:
                                        position_bonus = (content_length - first_occurrence) / content_length * 0.1
                                    
                                    # Factor 4: Column importance (title/name columns get bonus)
                                    column_bonus = 0.0
                                    if any(keyword in col.name.lower() for keyword in ['title', 'name', 'summary', 'description']):
                                        column_bonus = 0.2
                                    
                                    # Combined relevance score
                                    col_relevance = exact_score + term_score + position_bonus + column_bonus
                                    relevance_scores.append(col_relevance)
                                    
                                    # Enhanced matched content with context
                                    snippet_start = max(0, first_occurrence - 50)
                                    snippet_end = min(len(row_dict[col.name]), first_occurrence + len(query) + 50)
                                    snippet = str(row_dict[col.name])[snippet_start:snippet_end]
                                    if snippet_start > 0:
                                        snippet = "..." + snippet
                                    if snippet_end < len(str(row_dict[col.name])):
                                        snippet = snippet + "..."
                                    
                                    matched_content.append(f"{col.name}: {snippet}")

                        total_relevance = sum(relevance_scores)
                        if total_relevance > 0:
                            results.append(
                                {
                                    "table": table_name,
                                    "row_id": row_dict.get("id"),
                                    "row_data": row_dict,
                                    "matched_content": matched_content,
                                    "relevance": round(total_relevance, 4),
                                    "match_quality": "high" if total_relevance > 0.5 else "medium" if total_relevance > 0.1 else "low",
                                    "match_count": len(relevance_scores)
                                }
                            )

            # Sort by relevance and limit results
            def get_relevance(x: Dict[str, Any]) -> float:
                rel = x.get("relevance", 0)
                if isinstance(rel, (int, float)):
                    return float(rel)
                return 0.0
            results.sort(key=get_relevance, reverse=True)
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

            exploration: Dict[str, Any] = {"tables": [], "total_tables": len(table_names), "total_rows": 0}

            with self.get_connection() as conn:
                for table_name in table_names:
                    table = self.metadata.tables[table_name]

                    # Build column info and identify text columns
                    columns = []
                    text_columns: List[str] = []

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

                    table_info: Dict[str, Any] = {"name": table_name, "columns": columns, "text_columns": text_columns}

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
                        content_preview: Dict[str, List[Any]] = {}
                        for col_name in text_columns[:3]:  # Limit to first 3 text columns
                            col = table.c[col_name]
                            preview_result = conn.execute(select(col).distinct().where(col.isnot(None)).limit(5))
                            unique_values: List[Any] = [row[0] for row in preview_result.fetchall() if row[0]]
                            if unique_values:
                                content_preview[col_name] = unique_values

                        if content_preview:
                            table_info["content_preview"] = content_preview

                    exploration["tables"].append(table_info)

            return {"success": True, "exploration": exploration}
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to explore tables: {str(e)}")

    # --- Semantic Search Methods ---

    def add_embedding_column(self, table_name: str, embedding_column: str = "embedding") -> EmbeddingColumnResponse:
        """Add an embedding column to a table for semantic search."""
        try:
            table = self._ensure_table_exists(table_name)

            # Check if embedding column already exists
            if embedding_column in [col.name for col in table.columns]:
                return {"success": True, "message": f"Embedding column '{embedding_column}' already exists"}

            # Add embedding column as TEXT (JSON storage)
            with self.get_connection() as conn:
                conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {embedding_column} TEXT"))
                conn.commit()

            self._refresh_metadata()
            return {"success": True, "message": f"Added embedding column '{embedding_column}' to table '{table_name}'"}

        except (ValidationError, SQLAlchemyError) as e:
            if isinstance(e, ValidationError):
                raise e
            raise DatabaseError(f"Failed to add embedding column: {str(e)}")

    def generate_embeddings(
        self,
        table_name: str,
        text_columns: List[str],
        embedding_column: str = "embedding",
        model_name: str = "all-MiniLM-L6-v2",
        batch_size: int = 50,
    ) -> GenerateEmbeddingsResponse:
        """Generate embeddings for text content in a table."""
        if not is_semantic_search_available():
            raise ValidationError("Semantic search is not available. Please install sentence-transformers.")

        try:
            table = self._ensure_table_exists(table_name)
            semantic_engine = get_semantic_engine(model_name)

            # Validate text columns exist
            table_columns = [col.name for col in table.columns]
            for col in text_columns:
                if col not in table_columns:
                    raise ValidationError(f"Column '{col}' not found in table '{table_name}'")

            # Add embedding column if it doesn't exist
            if embedding_column not in table_columns:
                self.add_embedding_column(table_name, embedding_column)
                table = self._ensure_table_exists(table_name)  # Refresh

            # Get all rows that need embeddings
            with self.get_connection() as conn:
                # Select rows without embeddings or with null embeddings
                stmt = select(table).where(
                    or_(
                        table.c[embedding_column].is_(None),
                        table.c[embedding_column] == "",
                        table.c[embedding_column] == "null",
                    )
                )
                rows = conn.execute(stmt).fetchall()

                if not rows:
                    embedding_dim = semantic_engine.get_embedding_dimensions() or 0
                    return {
                        "success": True,
                        "message": "All rows already have embeddings",
                        "processed": 0,
                        "model": model_name,
                        "embedding_dimension": embedding_dim,
                    }

                processed = 0
                for i in range(0, len(rows), batch_size):
                    batch = rows[i : i + batch_size]

                    for row in batch:
                        row_dict = dict(row._mapping)

                        # Combine text from specified columns
                        text_parts = []
                        for col in text_columns:
                            if col in row_dict and row_dict[col]:
                                text_parts.append(str(row_dict[col]))

                        if text_parts:
                            combined_text = " ".join(text_parts)

                            # Generate embedding
                            embedding = semantic_engine.generate_embedding(combined_text)
                            embedding_json = json.dumps(embedding)

                            # Update row with embedding
                            update_stmt = (
                                update(table)
                                .where(table.c["id"] == row_dict["id"])
                                .values({embedding_column: embedding_json})
                            )

                            conn.execute(update_stmt)
                            processed += 1

                    conn.commit()
                    logging.info(f"Generated embeddings for batch {i//batch_size + 1}, processed {processed} rows")

                return {
                    "success": True,
                    "message": f"Generated embeddings for {processed} rows",
                    "processed": processed,
                    "model": model_name,
                    "embedding_dimension": semantic_engine.get_embedding_dimensions() or 0,
                }

        except (ValidationError, SQLAlchemyError) as e:
            if isinstance(e, ValidationError):
                raise e
            raise DatabaseError(f"Failed to generate embeddings: {str(e)}")

    def semantic_search(
        self,
        query: str,
        tables: Optional[List[str]] = None,
        embedding_column: str = "embedding",
        text_columns: Optional[List[str]] = None,
        similarity_threshold: float = 0.5,
        limit: int = 10,
        model_name: str = "all-MiniLM-L6-v2",
    ) -> SemanticSearchResponse:
        """Perform semantic search across tables using vector embeddings."""
        if not is_semantic_search_available():
            raise ValidationError("Semantic search is not available. Please install sentence-transformers.")

        if not query or not query.strip():
            raise ValidationError("Search query cannot be empty")

        try:
            self._refresh_metadata()
            search_tables = tables or list(self.metadata.tables.keys())
            semantic_engine = get_semantic_engine(model_name)

            all_results = []

            with self.get_connection() as conn:
                for table_name in search_tables:
                    if table_name not in self.metadata.tables:
                        continue

                    table = self.metadata.tables[table_name]

                    # Check if table has embedding column
                    if embedding_column not in [col.name for col in table.columns]:
                        logging.warning(f"Table '{table_name}' does not have embedding column '{embedding_column}'")
                        continue

                    # Get all rows with embeddings
                    stmt = select(table).where(
                        and_(
                            table.c[embedding_column].isnot(None),
                            table.c[embedding_column] != "",
                            table.c[embedding_column] != "null",
                        )
                    )
                    rows = conn.execute(stmt).fetchall()

                    if not rows:
                        continue

                    # Convert to list of dicts for semantic search
                    content_data = [dict(row._mapping) for row in rows]

                    # Determine text columns for highlighting
                    if text_columns is None:
                        text_cols = [
                            col.name
                            for col in table.columns
                            if "TEXT" in str(col.type).upper() or "VARCHAR" in str(col.type).upper()
                        ]
                    else:
                        text_cols = text_columns

                    # Perform semantic search on this table
                    table_results = semantic_engine.semantic_search(
                        query,
                        content_data,
                        embedding_column,
                        text_cols,
                        similarity_threshold,
                        limit * 2,  # Get more for global ranking
                    )

                    # Add table name to results
                    for result in table_results:
                        result["table_name"] = table_name

                    all_results.extend(table_results)

            # Sort all results by similarity score and limit
            all_results.sort(key=lambda x: x.get("similarity_score", 0), reverse=True)
            final_results = all_results[:limit]

            return {
                "success": True,
                "results": final_results,
                "query": query,
                "tables_searched": search_tables,
                "total_results": len(final_results),
                "model": model_name,
                "similarity_threshold": similarity_threshold,
            }

        except (ValidationError, SQLAlchemyError) as e:
            if isinstance(e, ValidationError):
                raise e
            raise DatabaseError(f"Semantic search failed: {str(e)}")

    def find_related_content(
        self,
        table_name: str,
        row_id: int,
        embedding_column: str = "embedding",
        similarity_threshold: float = 0.5,
        limit: int = 5,
        model_name: str = "all-MiniLM-L6-v2",
    ) -> RelatedContentResponse:
        """Find content related to a specific row by semantic similarity."""
        if not is_semantic_search_available():
            raise ValidationError("Semantic search is not available. Please install sentence-transformers.")

        try:
            table = self._ensure_table_exists(table_name)
            semantic_engine = get_semantic_engine(model_name)

            with self.get_connection() as conn:
                # Get the target row
                target_stmt = select(table).where(table.c["id"] == row_id)
                target_row = conn.execute(target_stmt).fetchone()

                if not target_row:
                    raise ValidationError(f"Row with id {row_id} not found in table '{table_name}'")

                target_dict = dict(target_row._mapping)

                # Check if target has embedding
                if (
                    embedding_column not in target_dict
                    or not target_dict[embedding_column]
                    or target_dict[embedding_column] in ["", "null"]
                ):
                    raise ValidationError(f"Row {row_id} does not have an embedding")

                # Get target embedding
                target_embedding = json.loads(target_dict[embedding_column])

                # Get all other rows with embeddings
                stmt = select(table).where(
                    and_(
                        table.c["id"] != row_id,
                        table.c[embedding_column].isnot(None),
                        table.c[embedding_column] != "",
                        table.c[embedding_column] != "null",
                    )
                )
                rows = conn.execute(stmt).fetchall()

                if not rows:
                    return {
                        "success": True,
                        "results": [],
                        "target_row": target_dict,
                        "total_results": 0,
                        "similarity_threshold": similarity_threshold,
                        "model": model_name,
                        "message": "No other rows with embeddings found",
                    }

                # Find similar rows
                content_data = [dict(row._mapping) for row in rows]
                candidate_embeddings = []
                valid_indices = []

                for idx, row_dict in enumerate(content_data):
                    try:
                        embedding = json.loads(row_dict[embedding_column])
                        candidate_embeddings.append(embedding)
                        valid_indices.append(idx)
                    except json.JSONDecodeError:
                        continue

                if not candidate_embeddings:
                    return {
                        "success": True,
                        "results": [],
                        "target_row": target_dict,
                        "total_results": 0,
                        "similarity_threshold": similarity_threshold,
                        "model": model_name,
                        "message": "No valid embeddings found for comparison",
                    }

                # Calculate similarities
                similar_indices = semantic_engine.find_similar_embeddings(
                    target_embedding, candidate_embeddings, similarity_threshold, limit
                )

                # Build results
                results = []
                for candidate_idx, similarity_score in similar_indices:
                    original_idx = valid_indices[candidate_idx]
                    row_dict = content_data[original_idx].copy()
                    row_dict["similarity_score"] = round(similarity_score, 3)
                    results.append(row_dict)

                return {
                    "success": True,
                    "results": results,
                    "target_row": target_dict,
                    "total_results": len(results),
                    "similarity_threshold": similarity_threshold,
                    "model": model_name,
                    "message": f"Found {len(results)} related items",
                }

        except (ValidationError, SQLAlchemyError) as e:
            if isinstance(e, ValidationError):
                raise e
            raise DatabaseError(f"Failed to find related content: {str(e)}")

    def hybrid_search(
        self,
        query: str,
        tables: Optional[List[str]] = None,
        text_columns: Optional[List[str]] = None,
        embedding_column: str = "embedding",
        semantic_weight: float = 0.7,
        text_weight: float = 0.3,
        limit: int = 10,
        model_name: str = "all-MiniLM-L6-v2",
    ) -> HybridSearchResponse:
        """Combine semantic search with keyword matching for optimal results."""
        if not is_semantic_search_available():
            # Fallback to text search only
            fallback_result = self.search_content(query, tables, limit)
            # Convert to HybridSearchResponse format
            return cast(
                HybridSearchResponse,
                {
                    **fallback_result,
                    "search_type": "text_only",
                    "semantic_weight": 0.0,
                    "text_weight": 1.0,
                    "model": "none",
                },
            )

        try:
            # Get semantic search results
            semantic_response = self.semantic_search(
                query,
                tables,
                embedding_column,
                text_columns,
                similarity_threshold=0.3,
                limit=limit * 2,
                model_name=model_name,
            )

            if not semantic_response.get("success"):
                return cast(
                    HybridSearchResponse,
                    {
                        **semantic_response,
                        "search_type": "semantic_failed",
                        "semantic_weight": semantic_weight,
                        "text_weight": text_weight,
                        "model": model_name,
                    },
                )

            semantic_results = semantic_response.get("results", [])

            if not semantic_results:
                # Fallback to text search
                fallback_result = self.search_content(query, tables, limit)
                return cast(
                    HybridSearchResponse,
                    {
                        **fallback_result,
                        "search_type": "text_fallback",
                        "semantic_weight": semantic_weight,
                        "text_weight": text_weight,
                        "model": model_name,
                    },
                )

            # Enhance with text matching scores
            try:
                semantic_engine = get_semantic_engine(model_name)
                
                # Verify the engine has the required method
                if not hasattr(semantic_engine, 'hybrid_search') or not callable(getattr(semantic_engine, 'hybrid_search')):
                    raise DatabaseError("Semantic engine hybrid_search method is not callable")
                
                enhanced_results = semantic_engine.hybrid_search(
                    query, semantic_results, text_columns or [], embedding_column, semantic_weight, text_weight, limit
                )
            except Exception as e:
                # If semantic enhancement fails, return semantic results without text enhancement
                logging.warning(f"Semantic enhancement failed: {e}")
                enhanced_results = semantic_results[:limit]

            return {
                "success": True,
                "results": enhanced_results,
                "query": query,
                "search_type": "hybrid",
                "semantic_weight": semantic_weight,
                "text_weight": text_weight,
                "total_results": len(enhanced_results),
                "model": model_name,
            }

        except (ValidationError, SQLAlchemyError) as e:
            if isinstance(e, ValidationError):
                raise e
            raise DatabaseError(f"Hybrid search failed: {str(e)}")

    def get_embedding_stats(self, table_name: str, embedding_column: str = "embedding") -> ToolResponse:
        """Get statistics about embeddings in a table."""
        try:
            table = self._ensure_table_exists(table_name)

            # Check if embedding column exists
            if embedding_column not in [col.name for col in table.columns]:
                # Return 0% coverage when column doesn't exist (for compatibility with tests)
                total_count = 0
                with self.get_connection() as conn:
                    total_count = conn.execute(select(text("COUNT(*)")).select_from(table)).scalar() or 0
                
                return {
                    "success": True,
                    "table_name": table_name,
                    "total_rows": total_count,
                    "embedded_rows": 0,
                    "coverage_percent": 0.0,
                    "embedding_dimensions": None,
                    "embedding_column": embedding_column,
                }

            with self.get_connection() as conn:
                # Count total rows
                total_count = conn.execute(select(text("COUNT(*)")).select_from(table)).scalar() or 0

                # Count rows with embeddings
                embedded_count = (
                    conn.execute(
                        select(text("COUNT(*)"))
                        .select_from(table)
                        .where(
                            and_(
                                table.c[embedding_column].isnot(None),
                                table.c[embedding_column] != "",
                                table.c[embedding_column] != "null",
                            )
                        )
                    ).scalar()
                    or 0
                )

                # Get sample embedding to check dimensions
                sample_stmt = (
                    select(table.c[embedding_column])
                    .where(
                        and_(
                            table.c[embedding_column].isnot(None),
                            table.c[embedding_column] != "",
                            table.c[embedding_column] != "null",
                        )
                    )
                    .limit(1)
                )

                sample_result = conn.execute(sample_stmt).fetchone()
                dimensions = None
                if sample_result and sample_result[0]:
                    try:
                        sample_embedding = json.loads(sample_result[0])
                        dimensions = len(sample_embedding)
                    except json.JSONDecodeError:
                        pass

                coverage_percent = (embedded_count / total_count * 100) if total_count > 0 else 0.0

                return {
                    "success": True,
                    "table_name": table_name,
                    "total_rows": total_count,
                    "embedded_rows": embedded_count,
                    "coverage_percent": round(coverage_percent, 1),
                    "embedding_dimensions": dimensions,
                    "embedding_column": embedding_column,
                }

        except (ValidationError, SQLAlchemyError) as e:
            if isinstance(e, ValidationError):
                raise e
            raise DatabaseError(f"Failed to get embedding stats: {str(e)}")


# Global database instance
_db_instance: Optional[SQLiteMemoryDatabase] = None


def get_database(db_path: Optional[str] = None) -> SQLiteMemoryDatabase:
    """Get or create the global database instance."""
    global _db_instance

    actual_path = db_path or os.environ.get("DB_PATH", "./test.db")
    if actual_path is None:
        actual_path = "./test.db"
    
    if _db_instance is None or (db_path and db_path != _db_instance.db_path):
        # Close previous instance if it exists
        if _db_instance is not None:
            _db_instance.close()
        _db_instance = SQLiteMemoryDatabase(actual_path)

    return _db_instance
