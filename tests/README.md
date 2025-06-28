# Test Suite Documentation

## Overview

The SQLite Memory Bank test suite provides comprehensive testing coverage across multiple dimensions with **57 total tests**:

- **Functional Testing**: Core CRUD operations and API functionality
- **Performance Testing**: Load testing, scalability, and resource usage
- **Edge Case Testing**: Boundary conditions, malformed inputs, and error scenarios
- **Mock Testing**: Simplified mocking and isolated component testing
- **Integration Testing**: End-to-end workflows and complex scenarios

## Test Structure

```
tests/
├── conftest.py              # Shared test configuration and utilities
├── test_api.py              # FastMCP integration and API tests (existing)
├── test_server.py           # Unit tests for server functions (existing)  
├── test_performance.py      # Performance and load testing (new)
├── test_edge_cases.py       # Edge cases and boundary testing (new)
├── test_mocks.py           # Mock testing and isolation (new)
└── README.md               # This documentation
```

## Test Categories

### 🔧 **Functional Tests** (`test_api.py`, `test_server.py`)
- CRUD operations (Create, Read, Update, Delete)
- Table schema management
- Data validation and constraints
- Search functionality (text and semantic)
- Error handling and recovery

### ⚡ **Performance Tests** (`test_performance.py`)
- Bulk insert operations (1000+ rows)
- Large query performance (2000+ rows)
- Embedding generation performance (100+ documents)
- Semantic search performance (multiple queries)
- Concurrent read/write operations
- Memory usage with large datasets
- Connection pooling behavior

### 🛡️ **Edge Case Tests** (`test_edge_cases.py`)
- Empty string handling
- Very large text data (1MB+)
- Unicode and special characters
- Numeric boundary values (max/min integers)
- Long table/column names
- Malformed inputs and SQL injection attempts
- Invalid WHERE clauses
- Complex nested data structures
- Transaction rollback scenarios
- Recovery from corrupted inputs

### 🎭 **Mock Tests** (`test_mocks.py`)
- Semantic search availability flags and error handling
- Error response structure validation
- Input validation with controlled scenarios
- JSON serialization and data type handling
- Concurrent operation simulation
- Table validation and boundary conditions
- Invalid operation handling and recovery

## Test Fixtures and Utilities

### Database Fixtures
- `temp_db_isolated`: Completely isolated test database
- `test_client`: FastMCP client with isolated database
- `test_db_path`: Temporary database path only

### Utility Classes
- `TestDataGenerator`: Consistent test data generation
- `TestAssertions`: Common assertion patterns
- `PerformanceMonitor`: Performance measurement utilities

### Helper Functions
- `extract_result()`: Enhanced response extraction with error handling
- `run_async_test()`: Async test execution helper

## Running Tests

### Full Test Suite
```bash
python -m pytest tests/ -v
```

### By Category
```bash
# Performance tests only
python -m pytest tests/test_performance.py -v

# Edge case tests only  
python -m pytest tests/test_edge_cases.py -v

# Mock tests only
python -m pytest tests/test_mocks.py -v
```

### By Marker
```bash
# Performance-related tests
python -m pytest -m performance -v

# Integration tests
python -m pytest -m integration -v

# Semantic search tests
python -m pytest -m semantic -v

# Slow tests (for CI/CD optimization)
python -m pytest -m "not slow" -v
```

### With Coverage
```bash
python -m pytest tests/ --cov=mcp_sqlite_memory_bank --cov-report=html
```

## Test Markers

Tests are categorized using pytest markers:

- `@pytest.mark.performance`: Performance and load tests
- `@pytest.mark.integration`: End-to-end integration tests
- `@pytest.mark.unit`: Isolated unit tests
- `@pytest.mark.semantic`: Semantic search functionality tests
- `@pytest.mark.edge_case`: Edge cases and boundary conditions
- `@pytest.mark.mock`: Tests using mocked dependencies
- `@pytest.mark.slow`: Potentially slow-running tests

## Performance Benchmarks

Expected performance thresholds:

### CRUD Operations
- **Bulk Insert**: >50 operations/second (1000 rows)
- **Complex Query**: <1 second (2000 rows with filters)
- **Concurrent Reads**: >20 operations/second (5 concurrent clients)
- **Concurrent Writes**: >10 operations/second (3 concurrent clients)

### Semantic Search
- **Embedding Generation**: >5 documents/second (100 documents)
- **Semantic Search**: <2 seconds per query (240 documents)
- **Auto-Search**: Automatic embedding + search in reasonable time

### Resource Usage
- **Memory**: Handle 1MB+ text data efficiently
- **Connection Management**: No connection leaks across multiple clients
- **Database Size**: Support databases with multiple tables and thousands of rows

## Error Scenarios Tested

### Input Validation
- Empty strings and null values
- Invalid table/column names
- Malformed JSON data
- SQL injection attempts
- Unicode and special characters

### System Failures
- Database connection failures
- File system permission errors
- Memory exhaustion
- Dependency unavailability (sentence-transformers)
- Async operation timeouts and cancellation

### Recovery Testing
- Transaction rollback behavior
- Graceful degradation when semantic search unavailable
- Database consistency after failed operations
- Auto-recovery suggestions for common errors

## Test Data Patterns

### Standard Test Data
- Small datasets (5-10 rows) for functional testing
- Medium datasets (100-500 rows) for integration testing
- Large datasets (1000+ rows) for performance testing

### Specialized Data
- Unicode text (multiple languages, emojis)
- Large text blocks (1MB+ content)
- Nested JSON structures
- Edge case numeric values (max/min integers)
- Potential security threats (SQL injection strings)

## CI/CD Integration

### Fast Test Subset (for pull requests)
```bash
python -m pytest tests/test_api.py tests/test_server.py -v
```

### Full Test Suite (for releases)
```bash
python -m pytest tests/ --cov=mcp_sqlite_memory_bank --cov-report=xml
```

### Performance Regression Testing
```bash
python -m pytest -m performance --benchmark-only
```

## Debugging Failed Tests

### Verbose Output
```bash
python -m pytest tests/test_performance.py::TestPerformance::test_bulk_insert_performance -v -s
```

### Debug Mode
```bash
python -m pytest tests/test_edge_cases.py -v --tb=long --capture=no
```

### Specific Test
```bash
python -m pytest tests/test_mocks.py::TestSemanticSearchMocking::test_sentence_transformers_unavailable -v -s
```

## Contributing New Tests

### Test Organization Guidelines
1. **Functional tests**: Add to existing `test_api.py` or `test_server.py`
2. **Performance tests**: Add to `test_performance.py`
3. **Edge cases**: Add to `test_edge_cases.py`
4. **Mocked scenarios**: Add to `test_mocks.py`

### Test Writing Best Practices
1. Use appropriate fixtures (`temp_db_isolated` recommended)
2. Use `TestAssertions` helpers for common patterns
3. Add appropriate markers (`@pytest.mark.performance`, etc.)
4. Include docstrings explaining test purpose
5. Use `TestDataGenerator` for consistent test data
6. Measure performance for performance tests
7. Test both success and failure scenarios

### Example Test Structure
```python
@pytest.mark.integration
@pytest.mark.semantic
async def test_new_feature(test_client):
    """Test description explaining what this test validates."""
    # Setup
    setup_data = TestDataGenerator.sample_table_schema("new_feature_test")
    
    # Create table
    result = await test_client.call_tool("create_table", setup_data)
    TestAssertions.assert_success_response(result)
    
    # Test functionality
    # ... test implementation ...
    
    # Verify results
    TestAssertions.assert_row_count(read_result, expected_count=5)
```

## Test Environment Configuration

### Environment Variables
- `TESTING=1`: Enables test mode
- `LOG_LEVEL=WARNING`: Reduces log noise during testing
- `DISABLE_PERFORMANCE_LOGGING=1`: Disables performance logging during tests

### Test Database Isolation
Each test uses an isolated temporary database to prevent interference:
- Automatic cleanup after each test
- Windows-compatible file handling
- Connection management and cleanup
- Singleton instance reset for fresh state

## Maintenance and Updates

### Regular Tasks
1. **Performance baseline updates**: Update performance thresholds as system improves
2. **New edge cases**: Add tests for newly discovered edge cases
3. **Dependency updates**: Update mock tests when dependencies change
4. **Coverage analysis**: Ensure new features have appropriate test coverage

### When to Add New Tests
- **New features**: Comprehensive testing for all new functionality
- **Bug fixes**: Regression tests to prevent reoccurrence
- **Performance improvements**: Benchmarks to validate improvements
- **Security enhancements**: Tests for new security measures

This comprehensive test suite ensures the SQLite Memory Bank maintains high quality, performance, and reliability across all use cases and environments.
