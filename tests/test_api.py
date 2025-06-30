import os
import tempfile
import pytest
import json
from typing import Any, Dict, cast, TypeVar, Sequence
from fastmcp import Client
from mcp_sqlite_memory_bank import server as smb

# Check for semantic search dependencies
try:
    pass

    SEMANTIC_SEARCH_AVAILABLE = True
except ImportError:
    SEMANTIC_SEARCH_AVAILABLE = False

# Define a type variable for MCPContent or any other response type
T = TypeVar("T")


def extract_result(resp: Sequence[T]) -> Dict[str, Any]:
    """Helper to extract tool output as dict from FastMCP Client response."""
    r = resp[0]
    if hasattr(r, "text") and isinstance(getattr(r, "text"), str):
        try:
            return json.loads(getattr(r, "text"))
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": f"Invalid JSON response in TextContent: {getattr(r, 'text')}",
            }
    if isinstance(r, str):
        try:
            return json.loads(r)
        except json.JSONDecodeError:
            return {"success": False, "error": f"Invalid JSON response: {r}"}
    if isinstance(r, dict):
        return r
    if hasattr(r, "model_dump") and callable(getattr(r, "model_dump")):
        return cast(Dict[str, Any], getattr(r, "model_dump")())
    return {"success": False, "error": f"Unexpected response format: {r}"}


@pytest.fixture()
def temp_db(monkeypatch):
    # Use a temporary file for the test DB
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)
    orig_db = smb.DB_PATH
    smb.DB_PATH = db_path
    yield db_path
    smb.DB_PATH = orig_db

    # Explicitly close database connections
    try:
        from mcp_sqlite_memory_bank.database import _db_instance

        if _db_instance:
            _db_instance.close()
    except Exception:
        pass

    import gc

    gc.collect()
    try:
        os.remove(db_path)
    except PermissionError:
        import time

        time.sleep(0.5)
        try:
            os.remove(db_path)
        except PermissionError:
            # On Windows, sometimes files remain locked, just pass
            pass


@pytest.mark.asyncio
async def test_create_and_read_table(temp_db):
    async with Client(smb.app) as client:
        # Create table
        result = await client.call_tool(
            "create_table",
            {
                "table_name": "notes",
                "columns": [
                    {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
                    {"name": "content", "type": "TEXT"},
                ],
            },
        )
        out = extract_result(result)
        assert out["success"]  # type: ignore
        # Insert row
        row = await client.call_tool("create_row", {"table_name": "notes", "data": {"content": "Hello, agent!"}})
        row_out = extract_result(row)
        assert row_out["success"]  # type: ignore
        # Read row
        rows = await client.call_tool("read_rows", {"table_name": "notes"})
        rows_out = extract_result(rows)
        assert rows_out["success"]  # type: ignore
        # type: ignore
        assert any(r["content"] == "Hello, agent!" for r in rows_out["rows"])


@pytest.mark.asyncio
async def test_error_handling(temp_db):
    async with Client(smb.app) as client:
        # Try to read from a non-existent table
        res = await client.call_tool("read_rows", {"table_name": "not_a_table"})
        res_out = extract_result(res)
        assert not res_out["success"]  # type: ignore
        assert "error" in res_out
        # Try to create a row with invalid column
        await client.call_tool(
            "create_table",
            {
                "table_name": "users",
                "columns": [
                    {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
                    {"name": "name", "type": "TEXT"},
                ],
            },
        )
        res2 = await client.call_tool("create_row", {"table_name": "users", "data": {"notacol": 1}})
        res2_out = extract_result(res2)
        assert not res2_out["success"]  # type: ignore
        assert "error" in res2_out


@pytest.mark.asyncio
async def test_tool_discovery_and_introspection(temp_db):
    """Test FastMCP protocol tool discovery and schema introspection capabilities."""
    async with Client(smb.app) as client:
        # 1. Tool Discovery via FastMCP protocol
        tools = await client.list_tools()
        tool_names = [t.name for t in tools]

        # Verify all required tools are available
        required_tools = {
            "create_table",
            "drop_table",
            "rename_table",
            "list_tables",
            "describe_table",
            "create_row",
            "read_rows",
            "update_rows",
            "delete_rows",
            "run_select_query",
            "list_all_columns",
        }
        assert all(tool in tool_names for tool in required_tools), f"Missing required tools. Found: {tool_names}"

        # 2. Schema Introspection
        # Create a test table
        create_result = await client.call_tool(
            "create_table",
            {
                "table_name": "test_table",
                "columns": [
                    {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
                    {"name": "data", "type": "TEXT"},
                    {"name": "created_at", "type": "TIMESTAMP"},
                ],
            },
        )
        create_out = extract_result(create_result)
        assert create_out["success"]

        # Verify table description
        desc_result = await client.call_tool("describe_table", {"table_name": "test_table"})
        desc_out = extract_result(desc_result)
        assert desc_out["success"]

        # Check column definitions
        columns = {col["name"]: col["type"] for col in desc_out["columns"]}
        assert "id" in columns
        assert "data" in columns
        assert "created_at" in columns

    # --- Additional integration tests for schema management tools ---


@pytest.mark.asyncio
async def test_drop_table_success_and_error(temp_db):
    async with Client(smb.app) as client:
        # Create a table to drop
        result = await client.call_tool(
            "create_table",
            {
                "table_name": "todelete",
                "columns": [
                    {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
                    {"name": "val", "type": "TEXT"},
                ],
            },
        )
        out = extract_result(result)
        assert out["success"]
        # Drop the table
        drop = await client.call_tool("drop_table", {"table_name": "todelete"})
        drop_out = extract_result(drop)
        assert drop_out["success"]
        # Try to drop again (should error)
        drop2 = await client.call_tool("drop_table", {"table_name": "todelete"})
        drop2_out = extract_result(drop2)
        assert not drop2_out["success"]
        assert "error" in drop2_out


@pytest.mark.asyncio
async def test_update_rows_and_list_columns(temp_db):
    """Test row updates and schema listing capabilities."""
    async with Client(smb.app) as client:
        # Create test tables
        await client.call_tool(
            "create_table",
            {
                "table_name": "products",
                "columns": [
                    {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "price", "type": "DECIMAL(10,2)"},
                ],
            },
        )

        await client.call_tool(
            "create_table",
            {
                "table_name": "categories",
                "columns": [
                    {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
                    {"name": "name", "type": "TEXT"},
                ],
            },
        )

        # Insert test data
        create_result = await client.call_tool(
            "create_row",
            {
                "table_name": "products",
                "data": {"name": "Test Product", "price": "9.99"},
            },
        )
        row_out = extract_result(create_result)
        assert row_out["success"]
        product_id = row_out["id"]

        # Update row
        update_result = await client.call_tool(
            "update_rows",
            {
                "table_name": "products",
                "data": {"price": "19.99"},
                "where": {"id": product_id},
            },
        )
        update_out = extract_result(update_result)
        assert update_out["success"]

        # Verify update
        read_result = await client.call_tool("read_rows", {"table_name": "products", "where": {"id": product_id}})
        read_out = extract_result(read_result)
        assert read_out["success"]
        # SQLite returns DECIMAL as float/numeric, not string
        assert float(read_out["rows"][0]["price"]) == 19.99

        # Test list_all_columns
        columns_result = await client.call_tool("list_all_columns")
        columns_out = extract_result(columns_result)
        assert columns_out["success"]

        # Verify both tables and their columns are listed
        schemas = columns_out["schemas"]
        assert "products" in schemas
        assert "categories" in schemas
        assert "id" in schemas["products"]
        assert "name" in schemas["products"]
        assert "price" in schemas["products"]


@pytest.mark.asyncio
async def test_numeric_types_handling(temp_db):
    """Test handling of various SQLite numeric types."""
    async with Client(smb.app) as client:
        # Create table with different numeric types
        result = await client.call_tool(
            "create_table",
            {
                "table_name": "numerics",
                "columns": [
                    {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
                    {"name": "int_val", "type": "INTEGER"},
                    {"name": "real_val", "type": "REAL"},
                    {"name": "decimal_val", "type": "DECIMAL(15,4)"},
                ],
            },
        )
        out = extract_result(result)
        assert out["success"]

        # Test integer boundaries
        await client.call_tool(
            "create_row",
            {
                "table_name": "numerics",
                "data": {
                    "int_val": 2147483647,
                    "real_val": 1.23456789,
                    "decimal_val": "1234567.8901",
                },  # Max 32-bit integer
            },
        )

        # Test floating point precision
        await client.call_tool(
            "create_row",
            {
                "table_name": "numerics",
                "data": {
                    "int_val": -2147483648,  # Min 32-bit integer
                    "real_val": 1.23e-4,  # Scientific notation
                    "decimal_val": "0.0001",
                },
            },
        )

        # Verify data integrity
        rows = await client.call_tool("read_rows", {"table_name": "numerics"})
        rows_out = extract_result(rows)
        assert rows_out["success"]

        # Check first row (max values)
        row1 = rows_out["rows"][0]
        assert row1["int_val"] == 2147483647
        # Account for float precision
        assert abs(row1["real_val"] - 1.23456789) < 1e-6
        assert float(row1["decimal_val"]) == 1234567.8901

        # Check second row (min/scientific values)
        row2 = rows_out["rows"][1]
        assert row2["int_val"] == -2147483648
        assert abs(row2["real_val"] - 0.000123) < 1e-6
        assert float(row2["decimal_val"]) == 0.0001


@pytest.mark.asyncio
async def test_null_and_optional_columns(temp_db):
    """Test handling of NULL values and optional columns."""
    async with Client(smb.app) as client:
        # Create table with optional columns
        result = await client.call_tool(
            "create_table",
            {
                "table_name": "with_nulls",
                "columns": [
                    {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
                    {"name": "required_text", "type": "TEXT NOT NULL"},
                    {"name": "optional_int", "type": "INTEGER"},
                    {"name": "optional_text", "type": "TEXT DEFAULT NULL"},
                    {"name": "defaulted_text", "type": "TEXT DEFAULT 'unknown'"},
                ],
            },
        )
        out = extract_result(result)
        assert out["success"]

        # Insert with minimal required data
        create1 = await client.call_tool(
            "create_row",
            {"table_name": "with_nulls", "data": {"required_text": "test1"}},
        )
        create1_out = extract_result(create1)
        assert create1_out["success"]

        # Insert with mixed NULL and non-NULL optional values
        create2 = await client.call_tool(
            "create_row",
            {
                "table_name": "with_nulls",
                "data": {
                    "required_text": "test2",
                    "optional_int": None,
                    "optional_text": "provided",
                },
            },
        )
        create2_out = extract_result(create2)
        assert create2_out["success"]

        # Verify data
        rows = await client.call_tool("read_rows", {"table_name": "with_nulls"})
        rows_out = extract_result(rows)
        assert rows_out["success"]

        # Check first row (minimal data)
        row1 = rows_out["rows"][0]
        assert row1["required_text"] == "test1"
        assert row1["optional_int"] is None
        assert row1["optional_text"] is None
        assert row1["defaulted_text"] == "unknown"

        # Check second row (mixed nulls)
        row2 = rows_out["rows"][1]
        assert row2["required_text"] == "test2"
        assert row2["optional_int"] is None
        assert row2["optional_text"] == "provided"
        assert row2["defaulted_text"] == "unknown"

        # Test that NOT NULL constraint is enforced
        bad_create = await client.call_tool(
            "create_row",
            {"table_name": "with_nulls", "data": {"optional_text": "will fail"}},
        )
        bad_out = extract_result(bad_create)
        assert not bad_out["success"]
        assert "error" in bad_out


@pytest.mark.asyncio
async def test_batch_operations(temp_db):
    """Test batch operations and implicit transactions."""
    async with Client(smb.app) as client:
        # Create test table
        await client.call_tool(
            "create_table",
            {
                "table_name": "batch_test",
                "columns": [
                    {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "value", "type": "INTEGER"},
                ],
            },
        )

        # Insert multiple rows
        bulk_data = [{"name": f"item{i}", "value": i} for i in range(1, 6)]

        for data in bulk_data:
            create = await client.call_tool("create_row", {"table_name": "batch_test", "data": data})
            create_out = extract_result(create)
            assert create_out["success"]

        # Verify initial inserts
        rows = await client.call_tool("read_rows", {"table_name": "batch_test", "where": {"value": 3}})
        rows_out = extract_result(rows)
        assert rows_out["success"]
        assert rows_out["rows"][0]["name"] == "item3"

        # Batch update multiple rows
        update = await client.call_tool(
            "update_rows",
            {"table_name": "batch_test", "data": {"value": 100}, "where": {"id": 1}},
        )
        update_out = extract_result(update)
        assert update_out["success"]

        # Verify the update
        read = await client.call_tool("read_rows", {"table_name": "batch_test", "where": {"id": 1}})
        read_out = extract_result(read)
        assert read_out["success"]
        assert read_out["rows"][0]["value"] == 100

        # Delete multiple rows
        delete = await client.call_tool("delete_rows", {"table_name": "batch_test", "where": {"id": 1}})
        delete_out = extract_result(delete)
        assert delete_out["success"]

        # Verify deletion
        remaining = await client.call_tool("read_rows", {"table_name": "batch_test", "where": {"id": 1}})
        remaining_out = extract_result(remaining)
        assert remaining_out["success"]
        assert len(remaining_out["rows"]) == 0

        # Test error handling with invalid column
        bad_update = await client.call_tool(
            "update_rows",
            {
                "table_name": "batch_test",
                "data": {"nonexistent": 1},
                "where": {"id": 2},
            },
        )
        bad_out = extract_result(bad_update)
        assert not bad_out["success"]
        assert "error" in bad_out


# --- Semantic Search and Advanced Features Tests ---


@pytest.mark.asyncio
async def test_search_content_functionality(temp_db):
    """Test full-text search capabilities."""
    async with Client(smb.app) as client:
        # Create test table with searchable content
        await client.call_tool(
            "create_table",
            {
                "table_name": "documents",
                "columns": [
                    {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
                    {"name": "title", "type": "TEXT"},
                    {"name": "content", "type": "TEXT"},
                    {"name": "category", "type": "TEXT"},
                ],
            },
        )

        # Insert test documents
        test_docs = [
            {
                "title": "Python Programming",
                "content": "Learn Python programming with examples",
                "category": "programming",
            },
            {
                "title": "Machine Learning",
                "content": "Introduction to artificial intelligence and ML algorithms",
                "category": "ai",
            },
            {
                "title": "Database Design",
                "content": "SQL database optimization and design patterns",
                "category": "data",
            },
            {
                "title": "Web Development",
                "content": "Modern web frameworks and API development",
                "category": "programming",
            },
        ]

        for doc in test_docs:
            create = await client.call_tool("create_row", {"table_name": "documents", "data": doc})
            create_out = extract_result(create)
            assert create_out["success"]

        # Test search functionality
        search = await client.call_tool("search_content", {"query": "programming", "tables": ["documents"]})
        search_out = extract_result(search)
        assert search_out["success"]
        assert len(search_out["results"]) >= 2  # Should find both programming-related docs

        # Test more specific search
        search2 = await client.call_tool("search_content", {"query": "machine learning", "tables": ["documents"]})
        search2_out = extract_result(search2)
        assert search2_out["success"]
        assert len(search2_out["results"]) >= 1


@pytest.mark.asyncio
async def test_explore_tables_functionality(temp_db):
    """Test table exploration and discovery capabilities."""
    async with Client(smb.app) as client:
        # Create multiple test tables
        await client.call_tool(
            "create_table",
            {
                "table_name": "users",
                "columns": [
                    {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "email", "type": "TEXT"},
                ],
            },
        )

        await client.call_tool(
            "create_table",
            {
                "table_name": "posts",
                "columns": [
                    {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
                    {"name": "title", "type": "TEXT"},
                    {"name": "user_id", "type": "INTEGER"},
                ],
            },
        )

        # Insert sample data
        user_result = await client.call_tool(
            "create_row",
            {
                "table_name": "users",
                "data": {"name": "Alice", "email": "alice@example.com"},
            },
        )
        user_out = extract_result(user_result)
        user_id = user_out["id"]

        await client.call_tool(
            "create_row",
            {
                "table_name": "posts",
                "data": {"title": "Hello World", "user_id": user_id},
            },
        )

        # Test table exploration
        explore = await client.call_tool("explore_tables", {"include_row_counts": True})
        explore_out = extract_result(explore)
        assert explore_out["success"]

        exploration = explore_out["exploration"]
        assert "tables" in exploration
        assert exploration["total_tables"] >= 2

        # Find our test tables
        table_names = [table["name"] for table in exploration["tables"]]
        assert "users" in table_names
        assert "posts" in table_names


@pytest.mark.skipif(not SEMANTIC_SEARCH_AVAILABLE, reason="sentence-transformers not available")
@pytest.mark.asyncio
async def test_add_embeddings_functionality(temp_db):
    """Test semantic embedding generation."""
    async with Client(smb.app) as client:
        # Create test table with text content
        await client.call_tool(
            "create_table",
            {
                "table_name": "knowledge_base",
                "columns": [
                    {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
                    {"name": "topic", "type": "TEXT"},
                    {"name": "description", "type": "TEXT"},
                ],
            },
        )

        # Insert test content
        test_content = [
            {
                "topic": "Machine Learning",
                "description": "Algorithms that learn from data to make predictions",
            },
            {
                "topic": "Database Systems",
                "description": "Structured storage and retrieval of information",
            },
            {
                "topic": "Web Development",
                "description": "Creating interactive applications for the internet",
            },
        ]

        for content in test_content:
            create = await client.call_tool("create_row", {"table_name": "knowledge_base", "data": content})
            create_out = extract_result(create)
            assert create_out["success"]

        # Generate embeddings
        embed_result = await client.call_tool(
            "add_embeddings",
            {
                "table_name": "knowledge_base",
                "text_columns": ["topic", "description"],
                "embedding_column": "embedding",
            },
        )
        embed_out = extract_result(embed_result)
        assert embed_out["success"]
        assert embed_out["processed"] == 3  # Should process all 3 rows
        assert "model" in embed_out


@pytest.mark.skipif(not SEMANTIC_SEARCH_AVAILABLE, reason="sentence-transformers not available")
@pytest.mark.asyncio
async def test_semantic_search_functionality(temp_db):
    """Test semantic search capabilities."""
    async with Client(smb.app) as client:
        # Create and populate test table
        await client.call_tool(
            "create_table",
            {
                "table_name": "tech_docs",
                "columns": [
                    {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
                    {"name": "title", "type": "TEXT"},
                    {"name": "content", "type": "TEXT"},
                ],
            },
        )

        tech_docs = [
            {
                "title": "Neural Networks",
                "content": "Deep learning with artificial neural networks for pattern recognition",
            },
            {
                "title": "SQL Queries",
                "content": "Database queries using structured query language for data retrieval",
            },
            {
                "title": "Python Programming",
                "content": "Object-oriented programming language for software development",
            },
            {
                "title": "Machine Learning",
                "content": "Algorithms that enable computers to learn from data automatically",
            },
        ]

        for doc in tech_docs:
            create = await client.call_tool("create_row", {"table_name": "tech_docs", "data": doc})
            create_out = extract_result(create)
            assert create_out["success"]

        # Generate embeddings first
        embed_result = await client.call_tool(
            "add_embeddings",
            {"table_name": "tech_docs", "text_columns": ["title", "content"]},
        )
        embed_out = extract_result(embed_result)
        assert embed_out["success"]

        # Test semantic search
        search_result = await client.call_tool(
            "semantic_search",
            {
                "query": "artificial intelligence and deep learning",
                "tables": ["tech_docs"],
                "similarity_threshold": 0.3,
                "limit": 10,
            },
        )
        search_out = extract_result(search_result)
        assert search_out["success"]
        assert "results" in search_out
        assert len(search_out["results"]) > 0

        # Should find neural networks and machine learning as most relevant
        top_result = search_out["results"][0]
        assert "similarity_score" in top_result
        assert top_result["similarity_score"] > 0.3


@pytest.mark.skipif(not SEMANTIC_SEARCH_AVAILABLE, reason="sentence-transformers not available")
@pytest.mark.asyncio
async def test_smart_search_hybrid_functionality(temp_db):
    """Test hybrid semantic + text search."""
    async with Client(smb.app) as client:
        # Create test table
        await client.call_tool(
            "create_table",
            {
                "table_name": "articles",
                "columns": [
                    {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
                    {"name": "title", "type": "TEXT"},
                    {"name": "body", "type": "TEXT"},
                    {"name": "tags", "type": "TEXT"},
                ],
            },
        )

        articles = [
            {
                "title": "AI Revolution",
                "body": "Artificial intelligence is transforming industries",
                "tags": "technology,ai,future",
            },
            {
                "title": "Database Performance",
                "body": "Optimizing SQL database queries for better performance",
                "tags": "database,sql,optimization",
            },
            {
                "title": "Python Best Practices",
                "body": "Writing clean and efficient Python code",
                "tags": "programming,python,development",
            },
        ]

        for article in articles:
            create = await client.call_tool("create_row", {"table_name": "articles", "data": article})
            create_out = extract_result(create)
            assert create_out["success"]

        # Generate embeddings
        embed_result = await client.call_tool(
            "add_embeddings",
            {"table_name": "articles", "text_columns": ["title", "body", "tags"]},
        )
        embed_out = extract_result(embed_result)
        assert embed_out["success"]

        # Test hybrid search
        hybrid_result = await client.call_tool(
            "smart_search",
            {
                "query": "machine learning optimization",
                "tables": ["articles"],
                "semantic_weight": 0.7,
                "text_weight": 0.3,
                "limit": 5,
            },
        )
        hybrid_out = extract_result(hybrid_result)
        assert hybrid_out["success"]
        assert "results" in hybrid_out
        assert hybrid_out["search_type"] == "hybrid"


@pytest.mark.skipif(not SEMANTIC_SEARCH_AVAILABLE, reason="sentence-transformers not available")
@pytest.mark.asyncio
async def test_auto_semantic_search_zero_setup(temp_db):
    """Test auto semantic search with automatic embedding generation."""
    async with Client(smb.app) as client:
        # Create table without manual embedding setup
        await client.call_tool(
            "create_table",
            {
                "table_name": "auto_docs",
                "columns": [
                    {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
                    {"name": "subject", "type": "TEXT"},
                    {"name": "details", "type": "TEXT"},
                ],
            },
        )

        # Insert content
        docs = [
            {
                "subject": "Quantum Computing",
                "details": "Quantum algorithms using qubits for computational advantages",
            },
            {
                "subject": "Blockchain Technology",
                "details": "Distributed ledger systems for secure transactions",
            },
            {
                "subject": "Cloud Computing",
                "details": "Remote computing resources accessible over the internet",
            },
        ]

        for doc in docs:
            create = await client.call_tool("create_row", {"table_name": "auto_docs", "data": doc})
            create_out = extract_result(create)
            assert create_out["success"]

        # Test auto semantic search (should auto-generate embeddings)
        auto_search = await client.call_tool(
            "auto_semantic_search",
            {
                "query": "distributed computing and parallel processing",
                "tables": ["auto_docs"],
                "similarity_threshold": 0.2,
                "limit": 5,
            },
        )
        auto_out = extract_result(auto_search)
        assert auto_out["success"]
        assert "results" in auto_out
        assert "auto_embedded_tables" in auto_out
        # Should have auto-generated embeddings for our table
        assert "auto_docs" in auto_out["auto_embedded_tables"]


@pytest.mark.skipif(not SEMANTIC_SEARCH_AVAILABLE, reason="sentence-transformers not available")
@pytest.mark.asyncio
async def test_auto_smart_search_complete_workflow(temp_db):
    """Test complete auto smart search workflow with zero manual setup."""
    async with Client(smb.app) as client:
        # Create table for comprehensive test
        await client.call_tool(
            "create_table",
            {
                "table_name": "research_papers",
                "columns": [
                    {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
                    {"name": "title", "type": "TEXT"},
                    {"name": "abstract", "type": "TEXT"},
                    {"name": "keywords", "type": "TEXT"},
                ],
            },
        )

        papers = [
            {
                "title": "Deep Learning for Computer Vision",
                "abstract": "Convolutional neural networks for image recognition and object detection",
                "keywords": "deep learning, CNN, computer vision, image processing",
            },
            {
                "title": "Natural Language Processing with Transformers",
                "abstract": "Attention mechanisms and transformer architectures for language understanding",
                "keywords": "NLP, transformers, attention, language models",
            },
            {
                "title": "Reinforcement Learning in Robotics",
                "abstract": "Learning optimal control policies through trial and error in robotic systems",
                "keywords": "reinforcement learning, robotics, control, AI",
            },
        ]

        for paper in papers:
            create = await client.call_tool("create_row", {"table_name": "research_papers", "data": paper})
            create_out = extract_result(create)
            assert create_out["success"]

        # Test auto smart search (zero setup - should handle everything automatically)
        complete_search = await client.call_tool(
            "auto_smart_search",
            {
                "query": "artificial intelligence neural networks learning",
                "tables": ["research_papers"],
                "semantic_weight": 0.6,
                "text_weight": 0.4,
                "limit": 10,
            },
        )
        complete_out = extract_result(complete_search)
        assert complete_out["success"]
        assert "results" in complete_out
        assert complete_out["search_type"] == "auto_hybrid"
        assert "auto_embedded_tables" in complete_out

        # Should have found relevant papers
        assert len(complete_out["results"]) >= 2

        # Results should have both semantic and text scores
        for result in complete_out["results"]:
            assert "combined_score" in result
            assert "semantic_score" in result or "text_score" in result


@pytest.mark.skipif(not SEMANTIC_SEARCH_AVAILABLE, reason="sentence-transformers not available")
@pytest.mark.asyncio
async def test_find_related_content(temp_db):
    """Test finding related content by semantic similarity."""
    async with Client(smb.app) as client:
        # Create knowledge base
        await client.call_tool(
            "create_table",
            {
                "table_name": "knowledge",
                "columns": [
                    {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
                    {"name": "concept", "type": "TEXT"},
                    {"name": "explanation", "type": "TEXT"},
                ],
            },
        )

        concepts = [
            {
                "concept": "Machine Learning",
                "explanation": "Algorithms that improve automatically through experience",
            },
            {
                "concept": "Deep Learning",
                "explanation": "Multi-layered neural networks for complex pattern recognition",
            },
            {
                "concept": "Data Mining",
                "explanation": "Extracting patterns and knowledge from large datasets",
            },
            {
                "concept": "Statistics",
                "explanation": "Mathematical analysis of data collections and probability",
            },
        ]

        concept_ids = []
        for concept in concepts:
            create = await client.call_tool("create_row", {"table_name": "knowledge", "data": concept})
            create_out = extract_result(create)
            assert create_out["success"]
            concept_ids.append(create_out["id"])

        # Generate embeddings
        embed_result = await client.call_tool(
            "add_embeddings",
            {"table_name": "knowledge", "text_columns": ["concept", "explanation"]},
        )
        embed_out = extract_result(embed_result)
        assert embed_out["success"]

        # Find content related to Machine Learning (should find Deep Learning as
        # highly related)
        ml_id = concept_ids[0]  # Machine Learning ID
        related_result = await client.call_tool(
            "find_related",
            {
                "table_name": "knowledge",
                "row_id": ml_id,
                "similarity_threshold": 0.2,
                "limit": 3,
            },
        )
        related_out = extract_result(related_result)
        assert related_out["success"]
        assert "results" in related_out
        assert "target_row" in related_out

        # Should find related concepts
        assert len(related_out["results"]) >= 1

        # Target row should be Machine Learning
        assert related_out["target_row"]["concept"] == "Machine Learning"


@pytest.mark.asyncio
async def test_embedding_stats_and_coverage(temp_db):
    """Test embedding statistics and coverage reporting."""
    async with Client(smb.app) as client:
        # Create test table
        await client.call_tool(
            "create_table",
            {
                "table_name": "test_stats",
                "columns": [
                    {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "description", "type": "TEXT"},
                ],
            },
        )

        # Insert some data
        for i in range(5):
            create = await client.call_tool(
                "create_row",
                {
                    "table_name": "test_stats",
                    "data": {
                        "name": f"Item {i}",
                        "description": f"Description for item {i}",
                    },
                },
            )
            create_out = extract_result(create)
            assert create_out["success"]

        # Check stats before embeddings (should be 0% coverage)
        stats_before = await client.call_tool("embedding_stats", {"table_name": "test_stats"})
        stats_before_out = extract_result(stats_before)
        assert stats_before_out["success"]
        assert stats_before_out["coverage_percent"] == 0.0
        assert stats_before_out["total_rows"] == 5

        # Generate embeddings
        embed_result = await client.call_tool(
            "add_embeddings",
            {"table_name": "test_stats", "text_columns": ["name", "description"]},
        )
        embed_out = extract_result(embed_result)

        # Test BOTH scenarios: available and unavailable
        if not embed_out["success"]:
            # SCENARIO 1: sentence-transformers unavailable (current situation)
            # This tests graceful degradation
            assert "sentence-transformers" in embed_out["error"] or "Semantic search" in embed_out["error"]

            # Verify the system still works for basic embedding stats
            stats_after = await client.call_tool("embedding_stats", {"table_name": "test_stats"})
            stats_after_out = extract_result(stats_after)

            # Should still work but show 0 coverage since no embeddings were created
            if stats_after_out["success"]:
                assert stats_after_out["coverage_percent"] == 0.0
                assert stats_after_out["total_rows"] == 5
                assert stats_after_out["embedded_rows"] == 0
            else:
                # This is also acceptable - the function should gracefully fail
                assert "sentence-transformers" in stats_after_out["error"] or "Semantic search" in stats_after_out["error"]

            pytest.skip("sentence-transformers not available - tested graceful degradation")
            return
        else:
            # SCENARIO 2: sentence-transformers available and working
            # This tests the full semantic search functionality
            assert embed_out["success"]
            assert embed_out["processed"] == 5  # All 5 test rows should be processed

            # Check stats after embeddings (should be 100% coverage)
            stats_after = await client.call_tool("embedding_stats", {"table_name": "test_stats"})
            stats_after_out = extract_result(stats_after)
            assert stats_after_out["success"]
            assert stats_after_out["coverage_percent"] == 100.0
            assert stats_after_out["total_rows"] == 5
            assert stats_after_out["embedded_rows"] == 5
            assert "embedding_dimensions" in stats_after_out


@pytest.mark.asyncio
async def test_semantic_search_error_handling(temp_db):
    """Test error handling in semantic search functionality."""
    async with Client(smb.app) as client:
        # Test semantic search without embeddings (should gracefully handle)
        search_no_embeddings = await client.call_tool(
            "semantic_search",
            {
                "query": "test query",
                "tables": ["nonexistent_table"],
                "similarity_threshold": 0.5,
            },
        )
        search_out = extract_result(search_no_embeddings)
        # Should either succeed with empty results or fail gracefully
        assert "success" in search_out

        # Test auto search with invalid table (should handle gracefully)
        auto_search_invalid = await client.call_tool(
            "auto_semantic_search",
            {
                "query": "test query",
                "tables": ["definitely_not_a_table"],
                "similarity_threshold": 0.5,
            },
        )
        auto_out = extract_result(auto_search_invalid)
        # Should handle gracefully
        assert "success" in auto_out

        # Test find_related with invalid row ID
        create_table = await client.call_tool(
            "create_table",
            {
                "table_name": "error_test",
                "columns": [
                    {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
                    {"name": "text", "type": "TEXT"},
                ],
            },
        )
        table_out = extract_result(create_table)
        assert table_out["success"]

        related_invalid = await client.call_tool(
            "find_related",
            {
                "table_name": "error_test",
                "row_id": 999999,  # Non-existent ID
                "similarity_threshold": 0.5,
            },
        )
        related_out = extract_result(related_invalid)
        assert not related_out["success"]  # Should fail gracefully
        assert "error" in related_out


# --- end of semantic tests ---
