"""
Test configuration and utilities for SQLite Memory Bank test suite.
Provides shared fixtures, utilities, and configuration for all test modules.
"""

import os
import tempfile
import pytest
import asyncio
import json
from typing import Any, Dict, TypeVar, Sequence, Optional
from fastmcp import Client
from mcp_sqlite_memory_bank import server as smb

# Type variable for response extraction
T = TypeVar("T")


def extract_result(resp: Sequence[T]) -> Dict[str, Any]:
    """
    Enhanced helper to extract tool output as dict from FastMCP Client response.
    Handles various response formats and provides better error reporting.
    """
    if not resp:
        return {"success": False, "error": "Empty response received"}

    r = resp[0]

    # Handle TextContent with JSON text
    if hasattr(r, "text") and isinstance(getattr(r, "text"), str):
        try:
            return json.loads(getattr(r, "text"))
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Invalid JSON response in TextContent: {getattr(r, 'text')[:100]}...",
                "parse_error": str(e),
            }

    # Handle direct string responses
    if isinstance(r, str):
        try:
            return json.loads(r)
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Invalid JSON response: {r[:100]}...",
                "parse_error": str(e),
            }

    # Handle direct dict responses
    if isinstance(r, dict):
        return r

    # Handle objects with model_dump method (Pydantic models)
    if hasattr(r, "model_dump") and callable(getattr(r, "model_dump")):
        try:
            return getattr(r, "model_dump")()
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to extract model data: {str(e)}",
                "response_type": str(type(r)),
            }

    # Fallback for unexpected response types
    return {
        "success": False,
        "error": f"Unexpected response format: {type(r)}",
        "response_preview": str(r)[:200],
    }


@pytest.fixture()
def test_db_path():
    """
    Provides a temporary database path for testing.
    Does not automatically set it as the global DB_PATH.
    """
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)
    yield db_path

    # Cleanup
    try:
        os.remove(db_path)
    except (PermissionError, FileNotFoundError):
        import time

        time.sleep(0.1)
        try:
            os.remove(db_path)
        except (PermissionError, FileNotFoundError):
            pass  # Windows sometimes keeps files locked


@pytest.fixture()
def temp_db_isolated(monkeypatch):
    """
    Isolated database fixture that completely isolates the test database.
    Recommended for most tests to avoid interference.
    """
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)

    # Store original DB_PATH
    orig_db = smb.DB_PATH

    # Set test database path
    monkeypatch.setattr(smb, "DB_PATH", db_path)

    yield db_path

    # Restore original DB_PATH
    smb.DB_PATH = orig_db

    # Explicit cleanup
    try:
        from mcp_sqlite_memory_bank.database import _db_instance

        if _db_instance:
            _db_instance.close()
            # Reset the singleton instance
            import mcp_sqlite_memory_bank.database as db_module

            db_module._db_instance = None
    except Exception:
        pass

    import gc

    gc.collect()

    # Remove test database file
    try:
        os.remove(db_path)
    except PermissionError:
        import time

        time.sleep(0.5)
        try:
            os.remove(db_path)
        except PermissionError:
            pass  # Windows file locking issues


@pytest.fixture()
async def test_client(temp_db_isolated):
    """
    Async fixture providing a FastMCP client connected to an isolated test database.
    Automatically handles client lifecycle.
    """
    client = Client(smb.app)
    await client.__aenter__()
    try:
        yield client
    finally:
        try:
            await client.__aexit__(None, None, None)
        except Exception:
            pass


class TestDataGenerator:
    """
    Utility class for generating test data consistently across test modules.
    """

    @staticmethod
    def sample_table_schema(table_name: str = "test_table") -> Dict[str, Any]:
        """Generate a standard test table schema."""
        return {
            "table_name": table_name,
            "columns": [
                {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
                {"name": "name", "type": "TEXT NOT NULL"},
                {"name": "description", "type": "TEXT"},
                {"name": "value", "type": "INTEGER"},
                {"name": "created_at", "type": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"},
            ],
        }

    @staticmethod
    def sample_row_data(name_prefix: str = "item", count: int = 1) -> list:
        """Generate sample row data for testing."""
        return [
            {
                "name": f"{name_prefix}_{i:03d}",
                "description": f"Description for {name_prefix} number {i}",
                "value": i * 10,
            }
            for i in range(count)
        ]

    @staticmethod
    def semantic_test_data() -> list:
        """Generate data specifically for semantic search testing."""
        return [
            {
                "title": "Machine Learning Fundamentals",
                "content": "Introduction to supervised and unsupervised learning algorithms, including neural networks and deep learning approaches.",
            },
            {
                "title": "Database Design Principles",
                "content": "Normalization, indexing, and query optimization techniques for relational database management systems.",
            },
            {
                "title": "Web Development Best Practices",
                "content": "Modern web frameworks, API design patterns, and frontend-backend integration strategies.",
            },
            {
                "title": "Cloud Computing Architecture",
                "content": "Scalable infrastructure design, microservices patterns, and distributed system principles.",
            },
            {
                "title": "Cybersecurity Fundamentals",
                "content": "Encryption protocols, authentication mechanisms, and secure software development practices.",
            },
        ]

    @staticmethod
    def large_text_data(size_kb: int = 10) -> str:
        """Generate large text data for performance testing."""
        base_text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 100
        multiplier = (size_kb * 1024) // len(base_text)
        return base_text * multiplier

    @staticmethod
    def unicode_test_data() -> Dict[str, str]:
        """Generate Unicode and special character test data."""
        return {
            "unicode_text": "Hello, 世界! ¡Hola, mundo! Здравствуй, мир! مرحبا بالعالم",
            "emoji_text": "🚀🎯💻🧠🔥⚡🌟💡🎨🎭🎪🎨",
            "special_chars": "!@#$%^&*()_+-=[]{}|;':\",./<>?`~\\",
            "mixed_content": "Data with 数字123 and symbols!@# and émojis🌟",
            "json_like": '{"key": "value", "number": 42, "array": [1,2,3]}',
            "sql_injection": "'; DROP TABLE users; --",
            "newlines_tabs": "Line 1\nLine 2\tTabbed\rCarriage Return",
        }


class TestAssertions:
    """
    Custom assertion helpers for common test patterns.
    """

    @staticmethod
    def assert_success_response(response: Dict[str, Any], message: str = ""):
        """Assert that a response indicates success."""
        assert response.get("success") is True, f"Expected success but got: {response}. {message}"

    @staticmethod
    def assert_error_response(
        response: Dict[str, Any], expected_error: Optional[str] = None, message: str = ""
    ):
        """Assert that a response indicates an error."""
        assert (
            response.get("success") is False
        ), f"Expected error but got success: {response}. {message}"
        assert "error" in response, f"Error response missing 'error' field: {response}. {message}"

        if expected_error:
            assert (
                expected_error.lower() in response["error"].lower()
            ), f"Expected error containing '{expected_error}' but got: {response['error']}. {message}"

    @staticmethod
    def assert_table_exists(client_response: Dict[str, Any], table_name: str):
        """Assert that a table exists in the list_tables response."""
        TestAssertions.assert_success_response(client_response)
        tables = client_response.get("tables", [])
        assert table_name in tables, f"Table '{table_name}' not found in tables list: {tables}"

    @staticmethod
    def assert_row_count(client_response: Dict[str, Any], expected_count: int):
        """Assert that a read_rows response contains the expected number of rows."""
        TestAssertions.assert_success_response(client_response)
        rows = client_response.get("rows", [])
        assert (
            len(rows) == expected_count
        ), f"Expected {expected_count} rows but got {len(rows)}: {rows}"

    @staticmethod
    def assert_semantic_search_results(
        response: Dict[str, Any], min_results: int = 1, min_similarity: float = 0.0
    ):
        """Assert semantic search response format and quality."""
        TestAssertions.assert_success_response(response)
        results = response.get("results", [])
        assert (
            len(results) >= min_results
        ), f"Expected at least {min_results} results but got {len(results)}"

        for i, result in enumerate(results):
            assert "similarity_score" in result, f"Result {i} missing similarity_score: {result}"
            similarity = result["similarity_score"]
            assert (
                similarity >= min_similarity
            ), f"Result {i} similarity {similarity} below threshold {min_similarity}: {result}"


class PerformanceMonitor:
    """
    Utility class for monitoring test performance and resource usage.
    """

    def __init__(self):
        self.metrics = {}
        self.start_times = {}

    def start_timer(self, operation: str):
        """Start timing an operation."""
        import time

        self.start_times[operation] = time.time()

    def end_timer(self, operation: str) -> float:
        """End timing an operation and return duration."""
        import time

        if operation not in self.start_times:
            return 0.0

        duration = time.time() - self.start_times[operation]
        self.metrics[operation] = duration
        return duration

    def assert_performance(self, operation: str, max_duration: float):
        """Assert that an operation completed within the expected time."""
        duration = self.metrics.get(operation, float("inf"))
        assert (
            duration <= max_duration
        ), f"Operation '{operation}' took {duration:.3f}s, expected <= {max_duration:.3f}s"

    def get_summary(self) -> Dict[str, float]:
        """Get performance summary for all measured operations."""
        return self.metrics.copy()


# Test markers for categorizing tests
pytest_plugins = []


# Custom markers
def pytest_configure(config):
    """Configure custom test markers."""
    config.addinivalue_line("markers", "performance: mark test as a performance test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line(
        "markers", "semantic: mark test as requiring semantic search functionality"
    )
    config.addinivalue_line(
        "markers", "edge_case: mark test as testing edge cases or boundary conditions"
    )
    config.addinivalue_line("markers", "mock: mark test as using mocked dependencies")
    config.addinivalue_line("markers", "slow: mark test as potentially slow-running")


# Async test utilities
def run_async_test(coro):
    """Helper to run async tests in sync context."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# Environment setup for tests
def setup_test_environment():
    """Set up test environment variables and configuration."""
    os.environ.setdefault("TESTING", "1")
    os.environ.setdefault("LOG_LEVEL", "WARNING")

    # Disable some features for testing
    os.environ.setdefault("DISABLE_PERFORMANCE_LOGGING", "1")


# Call setup on import
setup_test_environment()
