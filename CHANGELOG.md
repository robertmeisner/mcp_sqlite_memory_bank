# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.5.0] - Major Agent Experience Improvements (2025-06-28)

### 🚀 Major New Features
- **Intelligent Search Tool**: New `intelligent_search()` function that automatically detects optimal search strategy
  - Auto-analyzes query complexity to choose between semantic, keyword, or hybrid search
  - Automatically sets up embeddings when beneficial and requested
  - Provides intelligent fallback with detailed strategy explanations
  - Replaces complex multi-step workflows with single, powerful tool

- **Enhanced Search Algorithm**: Completely redesigned search relevance scoring
  - Multi-factor relevance calculation (exact phrase, term frequency, position, column importance)
  - Context-aware snippet generation with ellipsis handling
  - Match quality assessment (high/medium/low) and match count tracking
  - Column importance weighting (title/name columns get priority bonus)

- **Advanced Analytics & Insights**: New content analysis and health assessment tools
  - `analyze_memory_patterns()`: Comprehensive content distribution and organization analysis
  - `get_content_health_score()`: Overall health scoring (0-10) with actionable recommendations
  - Text density analysis, semantic readiness assessment, schema quality evaluation
  - Automated improvement suggestions with priority ranking

- **Enhanced Error Handling**: Revolutionary error recovery system
  - `suggest_recovery()`: AI-powered error analysis with auto-recovery suggestions
  - Context-aware diagnostics for dependency, database, schema, and method errors
  - Detailed recovery steps with installation commands and next actions
  - Enhanced error decorator with traceback, environment context, and recovery guidance

### 🔄 Real-time MCP Resources
- **Live Activity Feed**: `memory://live/recent-activity` - Real-time changes and additions
- **Content Suggestions**: `memory://live/content-suggestions` - AI-powered organization recommendations
- **Analytics Insights**: `memory://live/analytics/insights` - Real-time usage patterns and health metrics
- **Dynamic Updates**: All resources update automatically with current data

### 💡 Agent Experience Improvements
- **Zero-Setup Semantic Search**: Automatic embedding generation and setup
- **Intelligent Strategy Detection**: Query analysis determines optimal search approach
- **Graceful Fallback**: Robust error handling with automatic method switching
- **Rich Insights**: Detailed explanations of search strategies and results
- **Self-Healing**: Auto-recovery suggestions for common issues

### 🔧 Technical Enhancements
- **Better Relevance Scoring**: Multi-dimensional scoring with position and importance weighting
- **Enhanced MCP Resources**: Live-updating resources with real-time insights
- **Improved Type Safety**: Enhanced error handling with detailed context
- **Performance Optimizations**: Smarter caching and batch processing

### 📊 Analytics & Health
- **Content Health Scoring**: Comprehensive assessment with grades (A+ to D)
- **Usage Pattern Analysis**: Automated insights into content quality and organization
- **Semantic Readiness**: Assessment of tables ready for semantic search
- **Improvement Recommendations**: Prioritized suggestions for better knowledge management

### 🛡️ Error Handling & Recovery
- **Auto-Recovery System**: Intelligent suggestions for common errors
- **Detailed Diagnostics**: Environment context, stack traces, and recovery steps
- **Error Categorization**: Systematic classification with appropriate recovery actions
- **Context-Aware Help**: Function-specific guidance and troubleshooting

### 📈 Performance & Usability
- **Unified Search Interface**: Single tool replaces complex multi-step workflows
- **Smart Defaults**: Intelligent parameter selection based on content analysis
- **Real-time Feedback**: Live insights into search strategies and performance
- **Enhanced Documentation**: Rich examples and usage patterns in tool descriptions

### 🔍 Search Quality Improvements
- **Context Snippets**: Intelligent excerpt generation with proper ellipsis handling
- **Match Quality Scoring**: Automatic assessment of result relevance and quality
- **Multi-column Analysis**: Comprehensive text analysis across all searchable columns
- **Position-aware Scoring**: Earlier matches receive higher relevance scores

### 💻 Developer Experience
- **Enhanced Error Messages**: Detailed context with recovery suggestions
- **Better Tool Discovery**: Rich documentation with usage examples
- **Live Resource Updates**: Real-time insights into memory bank status
- **Comprehensive Analytics**: Deep insights into content quality and usage

### 🧪 Quality Assurance
- **All Tests Pass**: 18/18 existing tests continue to pass - no breaking changes
- **Enhanced Type Safety**: Improved static analysis with better error handling
- **Comprehensive Demo**: Full demonstration script showcasing all new features
- **Backward Compatibility**: All existing functionality preserved and enhanced

### 🎯 Impact Summary
This release transforms the SQLite Memory Bank from a powerful but complex tool into an intelligent, self-managing knowledge assistant. The new intelligent_search() tool alone eliminates the need for multi-step workflows while providing superior results. Enhanced analytics give users deep insights into their knowledge base health, while the advanced error recovery system makes troubleshooting effortless.

**Upgrade Priority: HIGH** - Significant improvements in usability, capability, and reliability.

---

## [1.4.3] - Type Safety and Testing Enhancement (2025-06-27)

### 🔧 Improvements
- **Type Safety**: Enhanced type annotations in auto_semantic_search and auto_smart_search functions
- **Database Layer**: Improved return type handling for embedding_stats function
- **Testing Coverage**: Added comprehensive semantic search test suite with 18 new test cases
- **Code Quality**: Fixed type compatibility issues for better static analysis

### 📝 Documentation
- **Deployment Instructions**: Added comprehensive deployment workflow to project instructions
- **Type Definitions**: Improved SemanticSearchResponse type definition for better type safety

### 🧪 Testing
- **Semantic Search Tests**: Full test coverage for all semantic search functionality
- **Auto-Search Tests**: Comprehensive testing of zero-setup semantic search features
- **Error Handling Tests**: Robust error handling validation for semantic features
- **Integration Tests**: End-to-end testing of hybrid search workflows

### 💡 Impact
- **Better Developer Experience**: Improved type safety reduces development errors
- **Reliable Semantic Search**: Comprehensive testing ensures robust semantic functionality
- **Production Ready**: Enhanced test coverage provides confidence for production deployments
- **Maintainability**: Better type annotations improve code maintainability

## [1.4.2] - Agent UX Enhancement (2025-06-27)

### 🎯 Agent Experience Improvements
- **Enhanced Tool Guidance**: Added warning labels to advanced semantic search tools (`add_embeddings`, `semantic_search`, `smart_search`)
- **Simplified Workflows**: Clear recommendations directing agents to use `auto_smart_search()` and `auto_semantic_search()` for easier setup
- **Better Documentation**: Enhanced tool descriptions with explicit "ADVANCED TOOL" warnings and "RECOMMENDATION" guidance
- **Reduced Complexity**: Agents no longer need to manually manage embedding setup - auto-tools handle everything automatically

### 📝 Documentation
- **Clear Agent Guidance**: Added ⚠️ warning icons and explicit recommendations in tool docstrings
- **Simplified Onboarding**: Auto-tools promoted as primary options for agent workflows
- **User Experience**: Prevents frustration with complex manual embedding management

### 🔧 Quality of Life
- All existing functionality preserved and working
- No breaking changes - backward compatibility maintained
- Improved agent developer experience through clearer tool selection

### 💡 Impact
- **Agents can now use semantic search with zero setup** via `auto_smart_search()`
- **Reduced learning curve** for new agent implementations
- **Better tool discoverability** with clear advanced vs. beginner tool distinction
- **Improved workflow efficiency** for LLM/agent frameworks

## [1.4.1] - Code Quality and Documentation Update (2025-06-27)

### 🔧 Fixes
- **Code Quality**: Fixed flake8 linting issues including unused imports, import order, and whitespace
- **Import Organization**: Moved dynamic imports to top-level to fix E402 errors
- **Documentation**: Enhanced README.md with comprehensive MCP features documentation
- **Configuration**: Updated flake8 configuration for better code quality standards

### 📝 Documentation
- **Enhanced README**: Added detailed MCP Resources and Prompts usage examples
- **Tool Organization**: Updated documentation to reflect new tool categorization
- **MCP Compliance**: Added comprehensive documentation of MCP features and capabilities

## [1.4.0] - MCP Compliance Enhancement (2025-06-27)

### 🚀 Major Features
- **MCP Resources Support**: Added 5 MCP resources for exposing memory content (`memory://tables/list`, `memory://tables/{table}/schema`, `memory://tables/{table}/data`, `memory://search/{query}`, `memory://analytics/overview`)
- **MCP Prompts Support**: Added 4 intelligent prompts for enhanced workflows (`analyze-memory-content`, `search-and-summarize`, `technical-decision-analysis`, `memory-bank-context`)
- **Tool Categorization**: Added `list_tool_categories()` and `get_tools_by_category()` for better tool organization and discoverability

### 💡 Improvements
- **Enhanced Agent Experience**: Better tool organization and discovery for LLM/agent frameworks
- **MCP Specification Compliance**: Significant improvement in MCP protocol compliance with Resources and Prompts support
- **Dynamic Context Provision**: Resources provide real-time access to memory content for AI applications
- **Workflow Templates**: Prompts offer pre-built templates for common memory analysis tasks

### 🎯 Developer Experience
- All new features are properly typed and tested
- Resources provide JSON-formatted content for easy consumption
- Prompts leverage existing search and analytics capabilities
- Backward compatible with existing tool interfaces

### 📊 Impact
- Enhanced discoverability: Tools now organized in logical categories
- Better MCP compliance: Resources and Prompts bring the server closer to full MCP specification
- Improved agent usability: Structured access to memory content through standardized MCP interfaces
- Workflow acceleration: Pre-built prompts for common analysis tasks

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
