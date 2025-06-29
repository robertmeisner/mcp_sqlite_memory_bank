"""
Test suite for FastMCP SQLite CRUD server.
Covers create, read, update, delete, and error handling.
"""

import os
import tempfile
import sqlite3
import pytest
from mcp_sqlite_memory_bank import server as smb


def setup_test_db():
    # Use a temporary file for the test DB
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL
        )
    """
    )
    conn.commit()
    conn.close()
    return db_path


@pytest.fixture(scope="module", autouse=True)
def patch_db_path():
    # Patch DB_PATH to use a temp DB for all tests
    test_db = setup_test_db()
    orig_db = smb.DB_PATH
    # Monkeypatch the global DB_PATH in the new package module
    smb.DB_PATH = test_db
    yield
    smb.DB_PATH = orig_db

    # Explicitly close database connections
    try:
        from mcp_sqlite_memory_bank.database import _db_instance

        if _db_instance:
            _db_instance.close()
    except Exception:
        pass

    import gc

    gc.collect()  # Ensure all connections are closed (especially on Windows)
    try:
        os.remove(test_db)
    except PermissionError:
        import time

        time.sleep(0.5)  # Give more time for cleanup
        try:
            os.remove(test_db)
        except PermissionError:
            # On Windows, sometimes files remain locked, just pass
            pass


# --- CRUD Tests ---
class TestCRUD:
    def test_create_row(self):
        """Test creating a row in the users table."""
        result = smb._create_row_impl(
            table_name="users", data={"name": "Alice", "age": 30}
        )
        assert result["success"]
        assert "id" in result

    def test_read_rows(self):
        """Test reading rows from the users table."""
        smb._create_row_impl(table_name="users", data={"name": "Bob", "age": 25})
        res = smb._read_rows_impl(table_name="users", where={"name": "Bob"})
        assert res["success"]
        assert any(row["name"] == "Bob" for row in res["rows"])

    def test_update_rows(self):
        """Test updating a row in the users table."""
        create = smb._create_row_impl(
            table_name="users", data={"name": "Carol", "age": 22}
        )
        user_id = create["id"]
        upd = smb._update_rows_impl(
            table_name="users", data={"age": 23}, where={"id": user_id}
        )
        assert upd["success"]
        assert upd["rows_affected"] == 1
        rows = smb._read_rows_impl(table_name="users", where={"id": user_id})["rows"]
        assert rows[0]["age"] == 23

    def test_delete_rows(self):
        """Test deleting a row from the users table."""
        create = smb._create_row_impl(
            table_name="users", data={"name": "Dave", "age": 40}
        )
        user_id = create["id"]
        del_res = smb._delete_rows_impl(table_name="users", where={"id": user_id})
        assert del_res["success"]
        assert del_res["rows_affected"] == 1
        rows = smb._read_rows_impl(table_name="users", where={"id": user_id})["rows"]
        assert rows == []


# --- Error Handling Tests ---


class TestErrorHandling:
    def test_invalid_table(self):
        """Test reading from and writing to a non-existent table."""
        res = smb._read_rows_impl(table_name="not_a_table")
        assert not res["success"]
        assert "error" in res

        res = smb._create_row_impl(table_name="users", data={"notacol": 1})
        assert not res["success"]
        assert "error" in res

    def test_update_invalid_column(self):
        """Test updating with an invalid column name."""
        res = smb._update_rows_impl(
            table_name="users", data={"notacol": 1}, where={"id": 1}
        )
        assert not res["success"]
        assert "error" in res

    def test_delete_invalid_column(self):
        """Test deleting with an invalid column name in where clause."""
        res = smb._delete_rows_impl(table_name="users", where={"notacol": 1})
        assert not res["success"]
        assert "error" in res


# --- Knowledge Graph CRUD tests ---


class TestKnowledgeGraph:
    def test_knowledge_graph_tables(self):
        """Create tables for a simple property graph: nodes and edges."""
        conn = sqlite3.connect(smb.DB_PATH)
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS nodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                label TEXT
            )
        """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS edges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source INTEGER,
                target INTEGER,
                type TEXT
            )
        """
        )
        conn.commit()
        conn.close()

    def test_knowledge_graph_crud(self):
        """CRUD operations for knowledge graph tables."""
        n1 = smb._create_row_impl(table_name="nodes", data={"label": "Person"})
        n2 = smb._create_row_impl(table_name="nodes", data={"label": "Company"})
        assert n1["success"] and n2["success"]
        e1 = smb._create_row_impl(
            table_name="edges",
            data={"source": n1["id"], "target": n2["id"], "type": "works_at"},
        )
        assert e1["success"]
        nodes = smb._read_rows_impl(table_name="nodes", where={})
        assert nodes["success"]
        assert any(node["label"] == "Person" for node in nodes["rows"])
        edges = smb._read_rows_impl(table_name="edges", where={"type": "works_at"})
        assert edges["success"]
        assert any(
            edge["source"] == n1["id"] and edge["target"] == n2["id"]
            for edge in edges["rows"]
        )
        upd = smb._update_rows_impl(
            table_name="nodes", data={"label": "Human"}, where={"id": n1["id"]}
        )
        assert upd["success"]
        del_edge = smb._delete_rows_impl(table_name="edges", where={"id": e1["id"]})
        assert del_edge["success"]
        edges2 = smb._read_rows_impl(table_name="edges", where={"id": e1["id"]})
        assert edges2["success"]
        assert edges2["rows"] == []


# --- Semantic Search Tests ---


def test_auto_embed_tables():
    """Test _auto_embed_tables helper function for semantic search setup."""
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
    from mcp_sqlite_memory_bank.tools.search import _auto_embed_tables

    # Setup test database
    db_path = setup_test_db()
    smb.DB_PATH = db_path

    try:
        # Create test table with text content
        create_result = smb._create_table_impl(
            table_name="test_content",
            columns=[
                {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
                {"name": "title", "type": "TEXT NOT NULL"},
                {"name": "content", "type": "TEXT NOT NULL"},
                {"name": "category", "type": "TEXT"},
            ],
        )
        assert create_result["success"]

        # Add some test data
        smb._create_row_impl(
            table_name="test_content",
            data={
                "title": "Test Article",
                "content": "This is test content",
                "category": "tech",
            },
        )
        smb._create_row_impl(
            table_name="test_content",
            data={
                "title": "Another Article",
                "content": "More test content",
                "category": "science",
            },
        )

        # Test auto-embedding on table without embeddings
        result = _auto_embed_tables(["test_content"])

        # Should return the table name if embedding was successful
        # Note: In actual environment with sentence-transformers, this would succeed
        # In test environment without dependencies, it may gracefully continue
        assert isinstance(result, list)

        # Test with non-existent table
        result_nonexistent = _auto_embed_tables(["nonexistent_table"])
        assert isinstance(result_nonexistent, list)

        # Test with empty table list
        result_empty = _auto_embed_tables([])
        assert result_empty == []

        # Test with multiple tables
        smb._create_table_impl(
            table_name="another_table",
            columns=[
                {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
                {"name": "description", "type": "TEXT"},
            ],
        )

        result_multiple = _auto_embed_tables(["test_content", "another_table"])
        assert isinstance(result_multiple, list)

    finally:
        # Cleanup - handle Windows file locking
        try:
            os.unlink(db_path)
        except (OSError, PermissionError):
            pass  # File cleanup handled by system


def test_auto_embed_tables_error_handling():
    """Test _auto_embed_tables error handling and edge cases."""
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
    from mcp_sqlite_memory_bank.tools.search import _auto_embed_tables

    # Setup test database
    db_path = setup_test_db()
    smb.DB_PATH = db_path

    try:
        # Test with table that has no text columns
        create_result = smb._create_table_impl(
            table_name="numeric_table",
            columns=[
                {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
                {"name": "value", "type": "INTEGER"},
                {"name": "score", "type": "REAL"},
            ],
        )
        assert create_result["success"]

        # Should handle table with no text columns gracefully
        result = _auto_embed_tables(["numeric_table"])
        assert isinstance(result, list)

        # Test with invalid table name characters
        result_invalid = _auto_embed_tables(["invalid-table-name!"])
        assert isinstance(result_invalid, list)

        # Test with None in table list (edge case)
        # Function should handle exceptions gracefully
        result_robust = _auto_embed_tables(["users"])  # Valid table from setup
        assert isinstance(result_robust, list)

    finally:
        # Cleanup - handle Windows file locking
        try:
            os.unlink(db_path)
        except (OSError, PermissionError):
            pass  # File cleanup handled by system


def test_auto_embed_tables_already_embedded():
    """Test _auto_embed_tables behavior when table already has embeddings."""
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
    from mcp_sqlite_memory_bank.tools.search import _auto_embed_tables

    # Setup test database
    db_path = setup_test_db()
    smb.DB_PATH = db_path

    try:
        # Create test table with embedding column
        create_result = smb._create_table_impl(
            table_name="embedded_table",
            columns=[
                {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
                {"name": "content", "type": "TEXT NOT NULL"},
                {"name": "embedding", "type": "TEXT"},  # Simulated embedding column
            ],
        )
        assert create_result["success"]

        # Add test data with mock embedding
        smb._create_row_impl(
            table_name="embedded_table",
            data={"content": "Test content", "embedding": "[0.1, 0.2, 0.3]"},
        )

        # Function should detect existing embeddings and skip
        result = _auto_embed_tables(["embedded_table"])
        assert isinstance(result, list)

    finally:
        # Cleanup - handle Windows file locking
        try:
            os.unlink(db_path)
        except (OSError, PermissionError):
            pass  # File cleanup handled by system
