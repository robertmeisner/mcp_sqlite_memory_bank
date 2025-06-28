"""
Edge case and boundary testing for SQLite Memory Bank.
Tests extreme conditions, malformed inputs, and boundary behaviors.
"""

import os
import tempfile
import pytest
import json
from fastmcp import Client
from mcp_sqlite_memory_bank import server as smb
from tests.test_api import extract_result


@pytest.fixture()
def temp_db_edge(monkeypatch):
    """Edge case testing database fixture."""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)
    orig_db = smb.DB_PATH
    smb.DB_PATH = db_path
    yield db_path
    smb.DB_PATH = orig_db

    # Cleanup
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
            pass


class TestBoundaryConditions:
    """Test boundary conditions and extreme inputs."""

    @pytest.mark.asyncio
    async def test_empty_string_handling(self, temp_db_edge):
        """Test handling of empty strings in various contexts."""
        async with Client(smb.app) as client:
            # Create table with text columns
            await client.call_tool(
                "create_table",
                {
                    "table_name": "empty_string_test",
                    "columns": [
                        {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
                        {"name": "empty_text", "type": "TEXT"},
                        {"name": "nullable_text", "type": "TEXT"},
                    ],
                },
            )

            # Test empty string insertion
            result = await client.call_tool(
                "create_row",
                {
                    "table_name": "empty_string_test",
                    "data": {"empty_text": "", "nullable_text": ""},
                },
            )
            result_out = extract_result(result)
            assert result_out["success"]

            # Test reading empty strings
            read_result = await client.call_tool("read_rows", {"table_name": "empty_string_test"})
            read_out = extract_result(read_result)
            assert read_out["success"]
            row = read_out["rows"][0]
            assert row["empty_text"] == ""
            assert row["nullable_text"] == ""

            # Test searching with empty strings
            search_result = await client.call_tool(
                "read_rows", {"table_name": "empty_string_test", "where": {"empty_text": ""}}
            )
            search_out = extract_result(search_result)
            assert search_out["success"]
            assert len(search_out["rows"]) == 1

    @pytest.mark.asyncio
    async def test_very_large_text_data(self, temp_db_edge):
        """Test handling of very large text data."""
        async with Client(smb.app) as client:
            await client.call_tool(
                "create_table",
                {
                    "table_name": "large_text_test",
                    "columns": [
                        {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
                        {"name": "large_content", "type": "TEXT"},
                    ],
                },
            )

            # Test with 1MB of text data
            large_content = "A" * (1024 * 1024)  # 1MB string

            result = await client.call_tool(
                "create_row",
                {"table_name": "large_text_test", "data": {"large_content": large_content}},
            )
            result_out = extract_result(result)
            assert result_out["success"]

            # Verify large content can be retrieved
            read_result = await client.call_tool("read_rows", {"table_name": "large_text_test"})
            read_out = extract_result(read_result)
            assert read_out["success"]
            assert len(read_out["rows"][0]["large_content"]) == 1024 * 1024

    @pytest.mark.asyncio
    async def test_unicode_and_special_characters(self, temp_db_edge):
        """Test handling of Unicode and special characters."""
        async with Client(smb.app) as client:
            await client.call_tool(
                "create_table",
                {
                    "table_name": "unicode_test",
                    "columns": [
                        {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
                        {"name": "unicode_text", "type": "TEXT"},
                        {"name": "emoji_text", "type": "TEXT"},
                        {"name": "special_chars", "type": "TEXT"},
                    ],
                },
            )

            # Test various Unicode and special characters
            test_data = {
                "unicode_text": "Hello, 世界! ¡Hola, mundo! Здравствуй, мир! مرحبا بالعالم",
                "emoji_text": "🚀🎯💻🧠🔥⚡🌟💡🎨🎭🎪🎨",
                "special_chars": "!@#$%^&*()_+-=[]{}|;':\",./<>?`~\n\t\r\\",
            }

            result = await client.call_tool(
                "create_row", {"table_name": "unicode_test", "data": test_data}
            )
            result_out = extract_result(result)
            assert result_out["success"]

            # Verify Unicode data integrity
            read_result = await client.call_tool("read_rows", {"table_name": "unicode_test"})
            read_out = extract_result(read_result)
            assert read_out["success"]
            row = read_out["rows"][0]

            assert row["unicode_text"] == test_data["unicode_text"]
            assert row["emoji_text"] == test_data["emoji_text"]
            assert row["special_chars"] == test_data["special_chars"]

    @pytest.mark.asyncio
    async def test_numeric_boundary_values(self, temp_db_edge):
        """Test numeric boundary values and edge cases."""
        async with Client(smb.app) as client:
            await client.call_tool(
                "create_table",
                {
                    "table_name": "numeric_boundary_test",
                    "columns": [
                        {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
                        {"name": "max_int", "type": "INTEGER"},
                        {"name": "min_int", "type": "INTEGER"},
                        {"name": "zero_val", "type": "INTEGER"},
                        {"name": "float_precision", "type": "REAL"},
                    ],
                },
            )

            # Test boundary values
            boundary_data = {
                "max_int": 9223372036854775807,  # Max 64-bit signed integer
                "min_int": -9223372036854775808,  # Min 64-bit signed integer
                "zero_val": 0,
                "float_precision": 1.23456789012345678901234567890,
            }

            result = await client.call_tool(
                "create_row", {"table_name": "numeric_boundary_test", "data": boundary_data}
            )
            result_out = extract_result(result)
            assert result_out["success"]

            # Verify boundary value preservation
            read_result = await client.call_tool(
                "read_rows", {"table_name": "numeric_boundary_test"}
            )
            read_out = extract_result(read_result)
            assert read_out["success"]
            row = read_out["rows"][0]

            assert row["max_int"] == boundary_data["max_int"]
            assert row["min_int"] == boundary_data["min_int"]
            assert row["zero_val"] == 0
            # Float precision may be limited by SQLite
            assert abs(row["float_precision"] - boundary_data["float_precision"]) < 1e-10

    @pytest.mark.asyncio
    async def test_table_and_column_name_boundaries(self, temp_db_edge):
        """Test edge cases for table and column names."""
        async with Client(smb.app) as client:
            # Test very long table name (SQLite limit is implementation-dependent)
            long_table_name = "a" * 50  # Reasonable length

            result = await client.call_tool(
                "create_table",
                {
                    "table_name": long_table_name,
                    "columns": [
                        {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
                        {"name": "a" * 50, "type": "TEXT"},  # Long column name
                    ],
                },
            )
            result_out = extract_result(result)
            assert result_out["success"]

            # Test that the table was created and is usable
            insert_result = await client.call_tool(
                "create_row", {"table_name": long_table_name, "data": {"a" * 50: "test_value"}}
            )
            insert_out = extract_result(insert_result)
            assert insert_out["success"]

            # Test table with special characters in name (should be handled safely)
            safe_special_table = "test_with_underscores_123"

            special_result = await client.call_tool(
                "create_table",
                {
                    "table_name": safe_special_table,
                    "columns": [
                        {"name": "id", "type": "INTEGER PRIMARY KEY"},
                        {"name": "column_with_numbers_123", "type": "TEXT"},
                    ],
                },
            )
            special_out = extract_result(special_result)
            assert special_out["success"]


class TestMalformedInputs:
    """Test handling of malformed and invalid inputs."""

    @pytest.mark.asyncio
    async def test_invalid_json_data(self, temp_db_edge):
        """Test handling of invalid JSON-like data structures."""
        async with Client(smb.app) as client:
            await client.call_tool(
                "create_table",
                {
                    "table_name": "json_test",
                    "columns": [
                        {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
                        {"name": "json_text", "type": "TEXT"},
                    ],
                },
            )

            # Test storing invalid JSON as text
            invalid_json_samples = [
                '{"key": "value"',  # Missing closing brace
                '{"key": value}',  # Unquoted value
                '{key: "value"}',  # Unquoted key
                '{"nested": {"incomplete":}',  # Incomplete nested structure
                "null",  # Valid JSON null
                "true",  # Valid JSON boolean
                "[]",  # Empty array
                "{}",  # Empty object
            ]

            for i, json_text in enumerate(invalid_json_samples):
                result = await client.call_tool(
                    "create_row", {"table_name": "json_test", "data": {"json_text": json_text}}
                )
                result_out = extract_result(result)
                assert result_out["success"], f"Failed to store sample {i}: {json_text}"

            # Verify all samples were stored
            read_result = await client.call_tool("read_rows", {"table_name": "json_test"})
            read_out = extract_result(read_result)
            assert read_out["success"]
            assert len(read_out["rows"]) == len(invalid_json_samples)

    @pytest.mark.asyncio
    async def test_sql_injection_prevention(self, temp_db_edge):
        """Test SQL injection prevention mechanisms."""
        async with Client(smb.app) as client:
            await client.call_tool(
                "create_table",
                {
                    "table_name": "injection_test",
                    "columns": [
                        {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
                        {"name": "user_input", "type": "TEXT"},
                    ],
                },
            )

            # Test potential SQL injection strings
            injection_attempts = [
                "'; DROP TABLE injection_test; --",
                "1' OR '1'='1",
                "1'; DELETE FROM injection_test; --",
                "UNION SELECT * FROM sqlite_master",
                "Robert'); DROP TABLE students;--",  # Classic Bobby Tables
                "<script>alert('xss')</script>",  # XSS attempt (should be stored as text)
                "NULL; UPDATE injection_test SET user_input='hacked' WHERE 1=1; --",
            ]

            # All injection attempts should be safely stored as text data
            for attempt in injection_attempts:
                result = await client.call_tool(
                    "create_row", {"table_name": "injection_test", "data": {"user_input": attempt}}
                )
                result_out = extract_result(result)
                assert result_out["success"], f"Failed to safely store: {attempt}"

            # Verify table still exists and data is intact
            read_result = await client.call_tool("read_rows", {"table_name": "injection_test"})
            read_out = extract_result(read_result)
            assert read_out["success"]
            assert len(read_out["rows"]) == len(injection_attempts)

            # Verify table structure is unchanged
            tables_result = await client.call_tool("list_tables")
            tables_out = extract_result(tables_result)
            assert "injection_test" in tables_out["tables"]

    @pytest.mark.asyncio
    async def test_invalid_where_clauses(self, temp_db_edge):
        """Test handling of invalid WHERE clause constructions."""
        async with Client(smb.app) as client:
            await client.call_tool(
                "create_table",
                {
                    "table_name": "where_test",
                    "columns": [
                        {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
                        {"name": "name", "type": "TEXT"},
                        {"name": "value", "type": "INTEGER"},
                    ],
                },
            )

            # Insert test data
            await client.call_tool(
                "create_row", {"table_name": "where_test", "data": {"name": "test1", "value": 1}}
            )

            # Test invalid column names in WHERE clauses
            invalid_where_tests = [
                {"nonexistent_column": "value"},  # Column doesn't exist
                {"name": None},  # None value (should be handled)
                {"": "empty_key"},  # Empty string key
            ]

            for where_clause in invalid_where_tests:
                result = await client.call_tool(
                    "read_rows", {"table_name": "where_test", "where": where_clause}
                )
                result_out = extract_result(result)
                # Should either succeed with empty results or fail gracefully
                assert "success" in result_out

    @pytest.mark.asyncio
    async def test_extremely_nested_data_structures(self, temp_db_edge):
        """Test handling of complex nested data structures."""
        async with Client(smb.app) as client:
            await client.call_tool(
                "create_table",
                {
                    "table_name": "nested_test",
                    "columns": [
                        {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
                        {"name": "complex_data", "type": "TEXT"},
                    ],
                },
            )

            # Create deeply nested dictionary as JSON string
            nested_data = {
                "level1": {
                    "level2": {"level3": {"level4": {"level5": {"value": "deep_nested_value"}}}}
                }
            }

            result = await client.call_tool(
                "create_row",
                {"table_name": "nested_test", "data": {"complex_data": json.dumps(nested_data)}},
            )
            result_out = extract_result(result)
            assert result_out["success"]

            # Verify data integrity
            read_result = await client.call_tool("read_rows", {"table_name": "nested_test"})
            read_out = extract_result(read_result)
            assert read_out["success"]

            retrieved_data = json.loads(read_out["rows"][0]["complex_data"])
            assert (
                retrieved_data["level1"]["level2"]["level3"]["level4"]["level5"]["value"]
                == "deep_nested_value"
            )


class TestErrorRecovery:
    """Test error recovery and graceful degradation."""

    @pytest.mark.asyncio
    async def test_transaction_rollback_behavior(self, temp_db_edge):
        """Test behavior during failed operations and rollback scenarios."""
        async with Client(smb.app) as client:
            # Create test table
            await client.call_tool(
                "create_table",
                {
                    "table_name": "rollback_test",
                    "columns": [
                        {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
                        {"name": "required_field", "type": "TEXT NOT NULL"},
                        {"name": "optional_field", "type": "TEXT"},
                    ],
                },
            )

            # Insert valid data first
            valid_result = await client.call_tool(
                "create_row",
                {
                    "table_name": "rollback_test",
                    "data": {"required_field": "valid_data", "optional_field": "optional"},
                },
            )
            valid_out = extract_result(valid_result)
            assert valid_out["success"]

            # Attempt invalid operation (violating NOT NULL constraint)
            invalid_result = await client.call_tool(
                "create_row",
                {
                    "table_name": "rollback_test",
                    "data": {"optional_field": "should_fail"},
                },  # Missing required_field
            )
            invalid_out = extract_result(invalid_result)
            assert not invalid_out["success"]  # Should fail

            # Verify the database is still in a consistent state
            read_result = await client.call_tool("read_rows", {"table_name": "rollback_test"})
            read_out = extract_result(read_result)
            assert read_out["success"]
            assert len(read_out["rows"]) == 1  # Only the valid row should exist
            assert read_out["rows"][0]["required_field"] == "valid_data"

    @pytest.mark.asyncio
    async def test_corrupted_input_recovery(self, temp_db_edge):
        """Test recovery from corrupted or malformed inputs."""
        async with Client(smb.app) as client:
            await client.call_tool(
                "create_table",
                {
                    "table_name": "recovery_test",
                    "columns": [
                        {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
                        {"name": "data", "type": "TEXT"},
                    ],
                },
            )

            # Test recovery after various problematic inputs
            problematic_inputs = [
                {"data": "\x00\x01\x02"},  # Binary data
                {"data": "a" * 100000},  # Very large string
                {"data": "\n\r\t\v\f"},  # Various whitespace characters
            ]

            success_count = 0
            for i, data in enumerate(problematic_inputs):
                result = await client.call_tool(
                    "create_row", {"table_name": "recovery_test", "data": data}
                )
                result_out = extract_result(result)
                if result_out["success"]:
                    success_count += 1

                # After each attempt, verify database is still operational
                health_check = await client.call_tool("list_tables")
                health_out = extract_result(health_check)
                assert health_out["success"], f"Database became unresponsive after input {i}"

            # Should handle at least some of the inputs successfully
            assert success_count >= len(problematic_inputs) // 2

    @pytest.mark.asyncio
    async def test_semantic_search_fallback_behavior(self, temp_db_edge):
        """Test fallback behavior when semantic search dependencies are missing."""
        async with Client(smb.app) as client:
            # Create test table
            await client.call_tool(
                "create_table",
                {
                    "table_name": "fallback_test",
                    "columns": [
                        {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
                        {"name": "content", "type": "TEXT"},
                    ],
                },
            )

            # Insert test data
            await client.call_tool(
                "create_row",
                {"table_name": "fallback_test", "data": {"content": "test content for search"}},
            )

            # Test auto_semantic_search - should handle gracefully if embeddings fail
            auto_search_result = await client.call_tool(
                "auto_semantic_search",
                {
                    "query": "test search query",
                    "tables": ["fallback_test"],
                    "similarity_threshold": 0.5,
                },
            )
            auto_search_out = extract_result(auto_search_result)
            # Should either succeed or fail gracefully
            assert "success" in auto_search_out

            # Test that basic search functionality still works
            content_search = await client.call_tool(
                "search_content", {"query": "test", "tables": ["fallback_test"]}
            )
            content_out = extract_result(content_search)
            assert content_out["success"]
            assert len(content_out["results"]) > 0

    @pytest.mark.asyncio
    async def test_table_schema_edge_cases(self, temp_db_edge):
        """Test edge cases in table schema creation and modification."""
        async with Client(smb.app) as client:
            # Test table with minimal schema
            minimal_result = await client.call_tool(
                "create_table",
                {
                    "table_name": "minimal_table",
                    "columns": [{"name": "id", "type": "INTEGER PRIMARY KEY"}],
                },
            )
            minimal_out = extract_result(minimal_result)
            assert minimal_out["success"]

            # Test table with many columns
            many_columns = [{"name": "id", "type": "INTEGER PRIMARY KEY"}]
            for i in range(50):  # SQLite can handle many columns
                many_columns.append({"name": f"col_{i}", "type": "TEXT"})

            many_cols_result = await client.call_tool(
                "create_table", {"table_name": "many_columns_table", "columns": many_columns}
            )
            many_cols_out = extract_result(many_cols_result)
            assert many_cols_out["success"]

            # Verify tables were created
            tables_result = await client.call_tool("list_tables")
            tables_out = extract_result(tables_result)
            assert "minimal_table" in tables_out["tables"]
            assert "many_columns_table" in tables_out["tables"]

            # Test describe table functionality on complex table
            describe_result = await client.call_tool(
                "describe_table", {"table_name": "many_columns_table"}
            )
            describe_out = extract_result(describe_result)
            assert describe_out["success"]
            assert len(describe_out["columns"]) == 51  # 1 + 50 columns
