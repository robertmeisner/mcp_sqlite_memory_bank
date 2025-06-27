# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.1] - 2025-06-27

### Fixed
- **Critical**: Added missing SQLAlchemy and semantic search dependencies to pyproject.toml
- Fixed MCP server startup failures when installed via uvx/PyPI
- Ensured all semantic search dependencies are properly declared

## [1.3.0] - 2025-06-27

### Added
- **Semantic Search Engine**: Complete implementation using sentence-transformers for natural language queries
- **5 New MCP Tools** for semantic operations:
  - `add_embeddings`: Enable semantic search on tables by adding vector embeddings
  - `semantic_search`: Natural language search across content using vector similarity
  - `find_related`: Discover similar content based on input text
  - `smart_search`: Hybrid approach combining semantic and keyword search
  - `embedding_stats`: Monitor embedding coverage and storage statistics
- **SemanticSearchEngine Class**: Comprehensive engine with embedding generation, cosine similarity calculations, and hybrid search
- **Database Enhancements**: 6 new methods in SQLiteMemoryDatabase for semantic operations
- **Vector Storage**: JSON-based embedding storage directly in SQLite with 384-dimensional vectors
- **Graceful Fallbacks**: Automatic fallback to keyword search when semantic dependencies unavailable
- **Type Safety**: Enhanced type system with new response types for semantic operations
- **Agent-Friendly APIs**: Explicit, discoverable tools with comprehensive documentation and examples

### Enhanced
- **Memory Instructions**: Updated with comprehensive semantic search guidance and best practices
- **Search Capabilities**: Beyond rigid WHERE clause filtering to intelligent knowledge discovery
- **Content Discovery**: Natural language queries like "find information about machine learning algorithms"
- **Similarity Thresholds**: Configurable similarity thresholds for different discovery modes (0.1-1.0)

### Dependencies
- Added `sentence-transformers>=2.2.0` for semantic search functionality
- Added `torch>=1.9.0` for neural network computations
- Added `numpy>=1.21.0` for vector operations
- All dependencies optional with graceful degradation

### Performance
- **Batch Processing**: Efficient embedding generation with configurable batch sizes
- **Caching**: Semantic model caching for improved performance
- **Optimized Storage**: JSON-based vector storage with minimal overhead
- **Fast Similarity**: Optimized cosine similarity calculations using numpy

### Backward Compatibility
- All existing functionality preserved and working
- 17 existing tests continue to pass
- No breaking changes to existing APIs
- Semantic features are additive enhancements

### Testing
- Comprehensive test coverage for semantic functionality
- Demonstrated working semantic search with 0.441+ similarity scores
- Multi-threshold testing and validation
- Performance and accuracy verification

## [1.2.0] - 2025-06-27

### Added
- Console script entry point for uvx compatibility
- `mcp-sqlite-memory-bank` command-line executable
- Main function with argument parsing for server configuration
- Support for `uvx mcp-sqlite-memory-bank` execution

### Fixed
- Syntax errors in `_delete_rows_impl` function
- Console script compatibility with modern Python packaging

### Changed
- Package now provides executable via `[project.scripts]` in pyproject.toml
- Server can now be started with command-line arguments: `--host`, `--port`, `--db-path`, `--reload`

## [1.1.1] - 2025-06-26

### Changed
- Updated PyPI description with improved README content

## [1.1.0] - 2025-06-26

### Added
- Pre-commit hooks with flake8 for code quality enforcement
- mypy static type checking in CI pipeline
- pytest-asyncio support for async test execution
- Comprehensive development setup documentation
- Flake8 configuration with modern line length limits (130 chars)
- GitHub Actions workflow improvements with proper Python path handling

### Fixed
- All flake8 linting errors across the codebase
- Syntax errors in test files (unterminated string literals)
- Import path issues preventing tests from running in CI
- mypy type annotation errors
- Async test execution failures

### Changed
- Updated README.md with clear development setup instructions
- Improved code formatting and removed unused imports
- Enhanced CI/CD pipeline with better error handling
- Modernized Python code style with longer line limits

### Developer Experience
- Added pre-commit configuration for automatic code quality checks
- Improved documentation for contributors
- Better error messages and type safety
- Streamlined development workflow

## [0.1.1] - Initial Release

### Added
- Core SQLite memory bank functionality
- FastMCP server implementation
- Basic CRUD operations for memory management
- Initial test suite
- Basic documentation
