# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
