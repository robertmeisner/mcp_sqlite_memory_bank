---
applyTo: '**'
---

# SQLite Memory Bank Project Instructions

## PROJECT OVERVIEW
This project provides a dynamic, agent-friendly SQLite memory bank implemented as a FastMCP server. The codebase is designed for LLM and agent frameworks with explicit, discoverable APIs.

## PROJECT-SPECIFIC ARCHITECTURE

### Core Components
- **server.py**: FastMCP implementation with all tool definitions
- **types.py**: Custom exception classes and type definitions
- **utils.py**: Utility functions with error handling decorators
- **examples/**: Example scripts showing usage patterns

### Design Principles
- **Explicit over Implicit**: Multiple explicit tools instead of multiplex functions
- **Type Safety**: All parameters and returns are properly typed
- **Discoverability**: Self-documenting tools with clear names and descriptions
- **Error Handling**: Consistent error response format across all tools
- **Validation**: All inputs validated before processing

## FASTMCP TOOL DEVELOPMENT PATTERNS

### Tool Registration
```python
@mcp.tool()
def tool_name(param: Type) -> ToolResponse:
    """Tool description for LLM discovery."""
    # Implementation
```

### Internal Implementation Functions
- Provide `_impl` functions for direct Python access
- Use `_impl` suffix for internal callable versions
- Example: `create_row()` (MCP tool) + `_create_row_impl()` (internal function)

### Error Response Pattern
```python
try:
    # Tool logic
    return {"success": True, "data": result}
except MemoryBankError as e:
    return cast(ToolResponse, e.to_dict())
except Exception as e:
    return cast(ToolResponse, DatabaseError(str(e)).to_dict())
```

### Type Safety for Tools
- All tool functions must return `ToolResponse` type
- Use `cast(ToolResponse, error_dict)` for error responses
- Validate all input parameters before processing
- Use `Optional[Type]` for nullable parameters

## SQLITE MEMORY BANK USAGE PATTERNS

### Database Schema Management
- Tables: project_structure, technical_decisions, user_preferences, session_context, documentation
- Use snake_case naming conventions
- Include appropriate constraints and indexes
- Maintain schema consistency across sessions

### Memory Storage Patterns
```python
# Store project information
create_row('project_structure', {
    'category': 'architecture',
    'title': 'Component Name',
    'content': 'Detailed description...'
})

# Store technical decisions
create_row('technical_decisions', {
    'decision_name': 'API Design Pattern',
    'chosen_approach': 'Explicit function-based tools',
    'rationale': 'Better discoverability for LLMs...'
})
```

### Memory Retrieval Patterns
```python
# Query specific information
architecture_info = read_rows('project_structure', {'category': 'architecture'})

# Get all user preferences
preferences = read_rows('user_preferences')
```

## PROJECT-SPECIFIC TESTING PATTERNS

### Test Structure
- `tests/test_api.py`: FastMCP client integration tests
- `tests/test_server.py`: Unit tests for individual functions
- Use `extract_result()` helper for parsing MCP responses

### Test Database Setup
```python
@pytest.fixture()
def temp_db(monkeypatch):
    # Use temporary file for test DB
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)
    orig_db = smb.DB_PATH
    smb.DB_PATH = db_path
    yield db_path
    # Cleanup
```

### MCP Response Testing
```python
# Test MCP tool responses
result = await client.call_tool("create_table", {
    "table_name": "test",
    "columns": [{"name": "id", "type": "INTEGER PRIMARY KEY"}]
})
out = extract_result(result)
assert out["success"]
```

## ERROR HANDLING PATTERNS

### Custom Exception Hierarchy
- `MemoryBankError`: Base exception class
- `ValidationError`: Input validation failures
- `DatabaseError`: SQLite operation failures
- `SchemaError`: Table/column schema issues
- `DataError`: Data integrity problems

### Error Response Format
```python
{
    "success": false,
    "error": "Human-readable error message",
    "category": "error_type",
    "details": {"additional": "context"}
}
```

### Decorator Usage
```python
@catch_errors
def tool_function(params):
    # Function automatically wraps exceptions
    # Returns appropriate error responses
```

## COMMON PROJECT PITFALLS

### FastMCP Tool Usage
- **Never call decorated functions directly** in Python code
- Use `_impl` functions for internal calls
- Remember: `@mcp.tool` decorated functions are not callable

### Type Safety Issues
- Always use `cast(ToolResponse, ...)` for error responses
- Use `Optional[Type]` instead of `Type = None`
- Ensure all functions have proper return type annotations

### Database Management
- Validate table/column names to prevent SQL injection
- Use parameterized queries for all data operations
- Handle SQLite connection cleanup properly

### Testing Considerations
- Use temporary databases for tests
- Clean up resources properly in fixtures
- Test both success and error conditions

## DEVELOPMENT WORKFLOW

### Before Making Changes
1. Run `get_errors` to check for type issues
2. Run existing tests to establish baseline
3. Check memory bank for related context

### During Development
1. Fix type errors immediately as they appear
2. Use internal `_impl` functions for direct calls
3. Maintain consistent error response format
4. Document decisions in memory bank

### After Changes
1. Run full test suite
2. Verify no new type errors
3. Update memory bank with new context
4. Validate error handling works correctly
5. Always before build and Fix linting issues with `flake8` and type issues with mypy and pylance errors
6. When I say “DEPLOY!”, perform these steps in order:
    1. Review CHANGELOG.md
    2. Bump the version if needed
    3. Update the documentation
    4. Commit all changes, TAag with the version number
    5. Push to GitHub
    6. Publish the package to PyPI
    7. Create a new GitHub release

## PROJECT-SPECIFIC COMMANDS

### Running Tests
```bash
python -m pytest                    # Run all tests
python -m pytest tests/test_api.py  # Run API tests only
```

### Running Examples
```bash
python examples/agent_memory_example.py     # Memory usage demo
python examples/client_example.py           # Client usage demo
```

### Type Checking
```bash
# Pylance/mypy will run automatically in VS Code
# Fix all type errors before committing
```

## INSTRUCTION MAINTENANCE PROTOCOL

### MANDATORY UPDATE REQUIREMENTS
When ANY of the following changes occur, you MUST update the relevant instruction files:

#### Project Architecture Changes
- **New components added** → Update PROJECT-SPECIFIC ARCHITECTURE section
- **Module relationships change** → Update Core Components documentation
- **Design patterns evolve** → Update Design Principles section

#### FastMCP Tool Changes
- **New tools added** → Update FASTMCP TOOL DEVELOPMENT PATTERNS
- **Tool signatures change** → Update Type Safety examples
- **Error handling patterns change** → Update Error Response Pattern section

#### Database Schema Changes
- **New tables added** → Update memory.instructions.md schemas
- **Column changes** → Update Memory Storage Patterns examples
- **Query patterns change** → Update Memory Retrieval Patterns

#### Testing Pattern Changes
- **New test utilities** → Update PROJECT-SPECIFIC TESTING PATTERNS
- **Test structure changes** → Update Test Structure section
- **New assertion patterns** → Update MCP Response Testing examples

#### Error Handling Changes
- **New exception types** → Update Custom Exception Hierarchy
- **Error response format changes** → Update Error Response Format
- **New decorator patterns** → Update Decorator Usage examples

### UPDATE WORKFLOW
1. **Identify Change Type**: Determine which instruction section is affected
2. **Update Documentation**: Modify the relevant instruction file(s)
3. **Verify Examples**: Ensure all code examples in instructions still work
4. **Test Instructions**: Validate that instructions are clear and complete
5. **Store Memory**: Update SQLite Memory Bank with documentation changes

### INSTRUCTION FILE RESPONSIBILITIES
- **project.instructions.md**: All SQLite Memory Bank specific patterns and architecture
- **memory.instructions.md**: Database schemas and memory usage patterns
- **general.instructions.md**: Universal coding standards (only update if patterns apply broadly)
- **code.review.instructions.md**: Review methodology (rarely needs updates)

### VALIDATION COMMANDS
After updating instructions, run these commands to verify accuracy:
```bash
# Test that examples in instructions work
python examples/agent_memory_example.py

# Verify no type errors in examples
# (Pylance will automatically check in VS Code)

# Run tests to ensure patterns still work
python -m pytest
```

### MEMORY BANK UPDATES
When updating instructions, also store the changes in memory:
```python
# Document instruction changes
create_row('technical_decisions', {
    'decision_name': 'Instruction Update',
    'chosen_approach': 'Updated [specific section]',
    'rationale': 'Changed due to [reason for change]'
})

# Update project structure if architectural changes
create_row('project_structure', {
    'category': 'documentation',
    'title': 'Instruction File Updates',
    'content': 'Updated instructions to reflect [specific changes]'
})
```

**CRITICAL**: Never let instruction files become outdated. Stale instructions lead to confusion and development errors.

This document should be updated whenever project-specific patterns or requirements change.
