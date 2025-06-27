import os
import tempfile
import pytest
import json
from typing import Any, Dict, cast, TypeVar, Sequence
from fastmcp import Client
from mcp_sqlite_memory_bank import server as smb

# Define a type variable for MCPContent or any other response type
T = TypeVar("T")


def extract_result(resp: Sequence[T]) -> Dict[str, Any]:
    """Helper to extract tool output as dict from FastMCP Client response."""
    r = resp[0]
    if hasattr(r, "text") and isinstance(getattr(r, "text"), str):
        try:
            return json.loads(getattr(r, "text"))
        except json.JSONDecodeError:
            return {"success": False, "error": f"Invalid JSON response in TextContent: {getattr(r, 'text')}"}
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
                "columns": [{"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"}, {"name": "content", "type": "TEXT"}],
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
                "columns": [{"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"}, {"name": "name", "type": "TEXT"}],
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
                "columns": [{"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"}, {"name": "val", "type": "TEXT"}],
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
                "columns": [{"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"}, {"name": "name", "type": "TEXT"}],
            },
        )

        # Insert test data
        create_result = await client.call_tool(
            "create_row", {"table_name": "products", "data": {"name": "Test Product", "price": "9.99"}}
        )
        row_out = extract_result(create_result)
        assert row_out["success"]
        product_id = row_out["id"]

        # Update row
        update_result = await client.call_tool(
            "update_rows", {"table_name": "products", "data": {"price": "19.99"}, "where": {"id": product_id}}
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
                "data": {"int_val": 2147483647, "real_val": 1.23456789, "decimal_val": "1234567.8901"},  # Max 32-bit integer
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
        create1 = await client.call_tool("create_row", {"table_name": "with_nulls", "data": {"required_text": "test1"}})
        create1_out = extract_result(create1)
        assert create1_out["success"]

        # Insert with mixed NULL and non-NULL optional values
        create2 = await client.call_tool(
            "create_row",
            {"table_name": "with_nulls", "data": {"required_text": "test2", "optional_int": None, "optional_text": "provided"}},
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
        bad_create = await client.call_tool("create_row", {"table_name": "with_nulls", "data": {"optional_text": "will fail"}})
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
        update = await client.call_tool("update_rows", {"table_name": "batch_test", "data": {"value": 100}, "where": {"id": 1}})
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
            "update_rows", {"table_name": "batch_test", "data": {"nonexistent": 1}, "where": {"id": 2}}
        )
        bad_out = extract_result(bad_update)
        assert not bad_out["success"]
        assert "error" in bad_out
