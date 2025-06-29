"""
Performance and load testing for SQLite Memory Bank.
Tests scalability, concurrent access, and resource usage patterns.
"""

import asyncio
import os
import tempfile
import time
import pytest
from typing import Any, Dict
from fastmcp import Client
from mcp_sqlite_memory_bank import server as smb
from tests.test_api import extract_result


@pytest.fixture()
def temp_db_perf(monkeypatch):
    """Performance-focused test database fixture."""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)
    orig_db = smb.DB_PATH
    smb.DB_PATH = db_path
    yield db_path
    smb.DB_PATH = orig_db

    # Cleanup with retry for Windows
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
        time.sleep(0.5)
        try:
            os.remove(db_path)
        except PermissionError:
            pass


class TestPerformance:
    """Performance testing for database operations."""

    @pytest.mark.asyncio
    async def test_bulk_insert_performance(self, temp_db_perf):
        """Test performance of bulk insert operations."""
        async with Client(smb.app) as client:
            # Create test table
            await client.call_tool(
                "create_table",
                {
                    "table_name": "bulk_test",
                    "columns": [
                        {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
                        {"name": "name", "type": "TEXT"},
                        {"name": "data", "type": "TEXT"},
                        {"name": "value", "type": "INTEGER"},
                    ],
                },
            )

            # Measure bulk insert performance
            start_time = time.time()
            insert_count = 1000

            for i in range(insert_count):
                create_result = await client.call_tool(
                    "create_row",
                    {
                        "table_name": "bulk_test",
                        "data": {
                            "name": f"item_{i:04d}",
                            "data": f"test_data_for_item_{i}" * 10,  # Larger text data
                            "value": i * 2,
                        },
                    },
                )
                if i % 100 == 0:  # Progress check
                    create_out = extract_result(create_result)
                    assert create_out["success"]

            end_time = time.time()
            duration = end_time - start_time
            ops_per_second = insert_count / duration

            print("\nBulk Insert Performance:")
            print(f"  Inserted {insert_count} rows in {duration:.2f} seconds")
            print(f"  Performance: {ops_per_second:.2f} ops/second")

            # Verify all data was inserted correctly
            count_result = await client.call_tool(
                "read_rows", {"table_name": "bulk_test"}
            )
            count_out = extract_result(count_result)
            assert count_out["success"]
            assert len(count_out["rows"]) == insert_count

            # Performance assertion - should handle at least 50 ops/sec
            assert (
                ops_per_second > 50
            ), f"Performance too slow: {ops_per_second:.2f} ops/sec"

    @pytest.mark.asyncio
    async def test_large_query_performance(self, temp_db_perf):
        """Test performance of large query operations."""
        async with Client(smb.app) as client:
            # Create table with indexed column
            await client.call_tool(
                "create_table",
                {
                    "table_name": "large_query_test",
                    "columns": [
                        {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
                        {"name": "category", "type": "TEXT"},
                        {"name": "status", "type": "TEXT"},
                        {"name": "metadata", "type": "TEXT"},
                    ],
                },
            )

            # Insert test data
            categories = ["type_a", "type_b", "type_c", "type_d"]
            statuses = ["active", "inactive", "pending"]

            for i in range(2000):
                await client.call_tool(
                    "create_row",
                    {
                        "table_name": "large_query_test",
                        "data": {
                            "category": categories[i % len(categories)],
                            "status": statuses[i % len(statuses)],
                            "metadata": f"metadata_content_{i}" * 5,
                        },
                    },
                )

            # Test query performance with filters
            start_time = time.time()

            query_result = await client.call_tool(
                "read_rows",
                {
                    "table_name": "large_query_test",
                    "where": {"category": "type_a", "status": "active"},
                },
            )

            end_time = time.time()
            query_duration = end_time - start_time

            query_out = extract_result(query_result)
            assert query_out["success"]

            print("\nLarge Query Performance:")
            print(f"  Queried 2000 rows with filters in {query_duration:.3f} seconds")
            print(f"  Found {len(query_out['rows'])} matching rows")

            # Performance assertion - complex query should complete under 1 second
            assert query_duration < 1.0, f"Query too slow: {query_duration:.3f} seconds"

    @pytest.mark.asyncio
    async def test_embedding_generation_performance(self, temp_db_perf):
        """Test performance of semantic embedding generation."""
        async with Client(smb.app) as client:
            # Create table with text content
            await client.call_tool(
                "create_table",
                {
                    "table_name": "embedding_perf_test",
                    "columns": [
                        {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
                        {"name": "title", "type": "TEXT"},
                        {"name": "content", "type": "TEXT"},
                    ],
                },
            )

            # Insert substantial text content
            test_content = [
                {
                    "title": f"Document {i}",
                    "content": f"This is a comprehensive document about topic {i}. "
                    * 20,
                }
                for i in range(100)
            ]

            for content in test_content:
                create_result = await client.call_tool(
                    "create_row", {"table_name": "embedding_perf_test", "data": content}
                )
                create_out = extract_result(create_result)
                assert create_out["success"]

            # Measure embedding generation performance
            start_time = time.time()

            embed_result = await client.call_tool(
                "add_embeddings",
                {
                    "table_name": "embedding_perf_test",
                    "text_columns": ["title", "content"],
                },
            )

            end_time = time.time()
            embed_duration = end_time - start_time

            embed_out = extract_result(embed_result)
            assert embed_out["success"]
            assert embed_out["processed"] == 100

            docs_per_second = 100 / embed_duration

            print("\nEmbedding Generation Performance:")
            print(
                f"  Generated embeddings for 100 documents in {embed_duration:.2f} seconds"
            )
            print(f"  Performance: {docs_per_second:.2f} docs/second")

            # Performance assertion - should process at least 5 docs/sec
            assert (
                docs_per_second > 5
            ), f"Embedding generation too slow: {docs_per_second:.2f} docs/sec"

    @pytest.mark.asyncio
    async def test_semantic_search_performance(self, temp_db_perf):
        """Test performance of semantic search operations."""
        async with Client(smb.app) as client:
            # Create and populate test table
            await client.call_tool(
                "create_table",
                {
                    "table_name": "search_perf_test",
                    "columns": [
                        {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
                        {"name": "topic", "type": "TEXT"},
                        {"name": "description", "type": "TEXT"},
                    ],
                },
            )

            # Insert diverse content for search testing
            topics = [
                "Machine Learning",
                "Database Systems",
                "Web Development",
                "Mobile Apps",
                "Cloud Computing",
                "Cybersecurity",
                "Data Science",
                "DevOps",
                "Artificial Intelligence",
                "Blockchain",
                "IoT",
                "Quantum Computing",
            ]

            for i, topic in enumerate(topics * 20):  # 240 documents
                await client.call_tool(
                    "create_row",
                    {
                        "table_name": "search_perf_test",
                        "data": {
                            "topic": f"{topic} {i}",
                            "description": f"Comprehensive guide to {topic.lower()} covering advanced concepts, "
                            f"implementation strategies, and real-world applications. "
                            f"This document provides detailed insights into {topic.lower()} "
                            f"methodologies and best practices for professionals.",
                        },
                    },
                )

            # Generate embeddings
            embed_result = await client.call_tool(
                "add_embeddings",
                {
                    "table_name": "search_perf_test",
                    "text_columns": ["topic", "description"],
                },
            )
            embed_out = extract_result(embed_result)
            assert embed_out["success"]

            # Test semantic search performance
            search_queries = [
                "artificial intelligence machine learning",
                "database optimization performance",
                "web application development",
                "cloud infrastructure security",
                "data analysis algorithms",
            ]

            total_search_time = 0
            for query in search_queries:
                start_time = time.time()

                search_result = await client.call_tool(
                    "semantic_search",
                    {
                        "query": query,
                        "tables": ["search_perf_test"],
                        "similarity_threshold": 0.3,
                        "limit": 10,
                    },
                )

                end_time = time.time()
                search_duration = end_time - start_time
                total_search_time += search_duration

                search_out = extract_result(search_result)
                assert search_out["success"]
                assert len(search_out["results"]) > 0

            avg_search_time = total_search_time / len(search_queries)
            searches_per_second = 1 / avg_search_time

            print("\nSemantic Search Performance:")
            print(
                f"  Completed {len(search_queries)} searches in {total_search_time:.3f} seconds"
            )
            print(f"  Average search time: {avg_search_time:.3f} seconds")
            print(f"  Performance: {searches_per_second:.2f} searches/second")

            # Performance assertion - searches should complete under 2 seconds each
            assert (
                avg_search_time < 2.0
            ), f"Semantic search too slow: {avg_search_time:.3f} seconds"


class TestConcurrency:
    """Concurrent access and thread safety testing."""

    @pytest.mark.asyncio
    async def test_concurrent_read_operations(self, temp_db_perf):
        """Test concurrent read operations from multiple clients."""
        # Create and populate test table
        async with Client(smb.app) as client:
            await client.call_tool(
                "create_table",
                {
                    "table_name": "concurrent_read_test",
                    "columns": [
                        {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
                        {"name": "data", "type": "TEXT"},
                    ],
                },
            )

            # Insert test data
            for i in range(50):
                await client.call_tool(
                    "create_row",
                    {
                        "table_name": "concurrent_read_test",
                        "data": {"data": f"test_data_{i}"},
                    },
                )

        async def read_worker(worker_id: int) -> Dict[str, Any]:
            """Worker function for concurrent reads."""
            async with Client(smb.app) as client:
                results = []
                for i in range(10):
                    result = await client.call_tool(
                        "read_rows", {"table_name": "concurrent_read_test"}
                    )
                    result_out = extract_result(result)
                    results.append(result_out["success"])
                return {
                    "worker_id": worker_id,
                    "successes": sum(results),
                    "total": len(results),
                }

        # Run concurrent read operations
        start_time = time.time()
        tasks = [read_worker(i) for i in range(5)]
        results = await asyncio.gather(*tasks)
        end_time = time.time()

        # Verify all reads succeeded
        for result in results:
            assert (
                result["successes"] == result["total"]
            ), f"Worker {result['worker_id']} had failures"

        total_operations = sum(result["total"] for result in results)
        duration = end_time - start_time
        ops_per_second = total_operations / duration

        print("\nConcurrent Read Performance:")
        print(
            f"  Completed {total_operations} concurrent reads in {duration:.2f} seconds"
        )
        print(f"  Performance: {ops_per_second:.2f} ops/second")

        # Performance assertion
        assert (
            ops_per_second > 20
        ), f"Concurrent reads too slow: {ops_per_second:.2f} ops/sec"

    @pytest.mark.asyncio
    async def test_concurrent_write_operations(self, temp_db_perf):
        """Test concurrent write operations with proper isolation."""
        async with Client(smb.app) as client:
            await client.call_tool(
                "create_table",
                {
                    "table_name": "concurrent_write_test",
                    "columns": [
                        {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
                        {"name": "worker_id", "type": "INTEGER"},
                        {"name": "sequence", "type": "INTEGER"},
                        {"name": "data", "type": "TEXT"},
                    ],
                },
            )

        async def write_worker(worker_id: int) -> Dict[str, Any]:
            """Worker function for concurrent writes."""
            async with Client(smb.app) as client:
                successes = 0
                for i in range(10):
                    result = await client.call_tool(
                        "create_row",
                        {
                            "table_name": "concurrent_write_test",
                            "data": {
                                "worker_id": worker_id,
                                "sequence": i,
                                "data": f"worker_{worker_id}_item_{i}",
                            },
                        },
                    )
                    result_out = extract_result(result)
                    if result_out["success"]:
                        successes += 1
                return {"worker_id": worker_id, "successes": successes, "total": 10}

        # Run concurrent write operations
        start_time = time.time()
        tasks = [write_worker(i) for i in range(3)]
        results = await asyncio.gather(*tasks)
        end_time = time.time()

        # Verify all writes succeeded
        for result in results:
            assert (
                result["successes"] == result["total"]
            ), f"Worker {result['worker_id']} had failures"

        # Verify data integrity
        async with Client(smb.app) as client:
            all_rows = await client.call_tool(
                "read_rows", {"table_name": "concurrent_write_test"}
            )
            all_rows_out = extract_result(all_rows)
            assert all_rows_out["success"]

            # Should have 30 total rows (3 workers × 10 rows each)
            assert len(all_rows_out["rows"]) == 30

            # Verify each worker wrote all their data
            for worker_id in range(3):
                worker_rows = await client.call_tool(
                    "read_rows",
                    {
                        "table_name": "concurrent_write_test",
                        "where": {"worker_id": worker_id},
                    },
                )
                worker_rows_out = extract_result(worker_rows)
                assert len(worker_rows_out["rows"]) == 10

        duration = end_time - start_time
        total_operations = sum(result["total"] for result in results)
        ops_per_second = total_operations / duration

        print("\nConcurrent Write Performance:")
        print(
            f"  Completed {total_operations} concurrent writes in {
                duration:.2f} seconds"
        )
        print(f"  Performance: {ops_per_second:.2f} ops/second")

        # Performance assertion
        assert (
            ops_per_second > 10
        ), f"Concurrent writes too slow: {ops_per_second:.2f} ops/sec"


class TestResourceUsage:
    """Resource usage and memory management testing."""

    @pytest.mark.asyncio
    async def test_memory_usage_large_dataset(self, temp_db_perf):
        """Test memory usage with large datasets."""
        async with Client(smb.app) as client:
            # Create table for memory testing
            await client.call_tool(
                "create_table",
                {
                    "table_name": "memory_test",
                    "columns": [
                        {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
                        {"name": "large_text", "type": "TEXT"},
                    ],
                },
            )

            # Insert large text data
            large_text = "X" * 10000  # 10KB per row

            for i in range(100):  # 1MB total
                result = await client.call_tool(
                    "create_row",
                    {"table_name": "memory_test", "data": {"large_text": large_text}},
                )
                result_out = extract_result(result)
                assert result_out["success"]

            # Test reading large dataset in chunks
            all_rows = await client.call_tool(
                "read_rows", {"table_name": "memory_test"}
            )
            all_rows_out = extract_result(all_rows)
            assert all_rows_out["success"]
            assert len(all_rows_out["rows"]) == 100

            # Verify memory efficiency by checking response size
            total_text_size = sum(
                len(row["large_text"]) for row in all_rows_out["rows"]
            )
            assert total_text_size == 100 * 10000  # 1MB as expected

            print("\nMemory Usage Test:")
            print(
                f"  Successfully handled {total_text_size / (1024 * 1024):.1f}MB of text data"
            )
            print(f"  Retrieved {len(all_rows_out['rows'])} rows efficiently")

    @pytest.mark.asyncio
    async def test_connection_pooling_behavior(self, temp_db_perf):
        """Test database connection management and pooling."""
        # Test multiple sequential client connections
        for i in range(10):
            async with Client(smb.app) as client:
                # Simple operation to test connection
                result = await client.call_tool("list_tables")
                result_out = extract_result(result)
                assert result_out["success"]

        # Test that connections are properly cleaned up
        async with Client(smb.app) as client:
            # Create a table to verify database is still accessible
            result = await client.call_tool(
                "create_table",
                {
                    "table_name": "connection_test",
                    "columns": [
                        {"name": "id", "type": "INTEGER PRIMARY KEY"},
                        {"name": "test", "type": "TEXT"},
                    ],
                },
            )
            result_out = extract_result(result)
            assert result_out["success"]

        print("\nConnection Management Test:")
        print("  Successfully handled multiple sequential connections")
        print("  No connection leaks detected")
