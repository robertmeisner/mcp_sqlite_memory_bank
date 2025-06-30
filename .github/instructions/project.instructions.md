---
applyTo: '**'
---

# SQLite Memory Bank Project Instructions (MCP Server Specific)

## PROJECT OVERVIEW
Dynamic, agent-friendly SQLite memory bank as FastMCP server. Explicit, discoverable APIs for LLM frameworks.

**Core Components**: server.py (FastMCP tools), types.py (exceptions), utils.py (error handling), examples/ (usage patterns)
**Design Principles**: Explicit over implicit, type safety, discoverability, consistent error handling, input validation

## PROJECT-SPECIFIC DATABASE REQUIREMENTS
- **SQLite 3.46+**: Leverage JSON columns, generated columns, strict mode, foreign keys, check constraints, and transactions
- **Schema Management**: snake_case, appropriate constraints, consistent naming
- **Storage Patterns**: Use `create_row('table', {...})` and `upsert_memory()` for deduplication
- **Retrieval Patterns**: Use `read_rows('table', {'where': 'clause'})` and semantic search for discovery

## PROJECT-SPECIFIC PATTERNS

### **FastMCP Architecture**
- **server.py**: FastMCP implementation with all tool definitions
- **types.py**: Custom exception classes and type definitions  
- **utils.py**: Utility functions with error handling decorators
- **examples/**: Example scripts showing usage patterns

### **SQLite Memory Bank Usage**
- **Error Responses**: Always return `{"success": True, "data": result}` or error dict
- **Custom Exceptions**: MemoryBankError → ValidationError, DatabaseError, SchemaError, DataError
- **Response Format**: `{"success": false, "error": "message", "category": "type", "details": {}}`
- **Decorator**: `@catch_errors` automatically wraps exceptions

### **FastMCP Tools Development**
```python
@mcp.tool()
def tool_name(param: Type) -> ToolResponse:
    """Tool description for LLM discovery."""
    # Implementation with cast(ToolResponse, error_dict) for errors
```
- Use `_impl` functions for internal Python calls (decorated functions not callable)
- Always return `{"success": True, "data": result}` or error dict
- Use `Optional[Type]` instead of `Type = None`

### **Testing Patterns**
- **Test Structure**: `tests/test_api.py` for FastMCP, `tests/test_server.py` for units
- **Response Testing**: Use `extract_result()` for MCP response parsing
- **Database Testing**: Temporary DB fixtures with `tempfile.mkstemp(suffix='.db')`
- **Error Testing**: Test all error conditions and edge cases

## PROJECT-SPECIFIC QUALITY ASSURANCE

### **Syntax Error Prevention (Python/FastMCP Specific)**
```powershell
# BEFORE any edits - check for existing syntax errors
flake8 src/ tests/ --select=E999 --count  # Must be 0

# AFTER any edits - verify no new syntax errors
flake8 src/ tests/ --select=E999 --count  # Must still be 0
```

### **F-String Safety Rules (Python Specific)**
❌ **NEVER**: Multi-line f-strings `f"text {variable_on_newline} more"`  
✅ **ALWAYS**: Single line `f"text {variable} more"` or proper parentheses grouping

### **Pre-Commit Requirements (Project Specific)**
```powershell
# Complete quality check before every commit
flake8 src/ tests/ --max-line-length=150 --extend-ignore=E203,W503 --count

# If violations found, run automated fixes:
black src/ tests/ --line-length=150; autopep8 --in-place --aggressive --recursive src/ tests/; autoflake --in-place --remove-unused-variables --remove-all-unused-imports --recursive src/ tests/
```

### **VS Code Configuration (Python/FastMCP Specific)**
```json
{
    "python.linting.flake8Enabled": true,
    "python.linting.flake8Args": ["--select=E999,F821,F822,F823", "--max-line-length=150"],
    "python.linting.lintOnSave": true,
    "python.linting.lintOnType": true,
    "python.formatting.provider": "black"
}
```

## VS CODE MCP WORKFLOW (PROJECT SPECIFIC)

### **Critical: Manual Server Restart Required**
**Code changes NOT automatically loaded** - Always restart MCP server after changes:
- `Ctrl+Shift+P` → `MCP: Restart Server` OR `.\restart-mcp.ps1`

### **Development Cycle**
1. Make changes → 2. Save files → 3. **Restart MCP server** → 4. Test → 5. Repeat

## PROJECT-SPECIFIC DEPLOYMENT ADDITIONS

### **Additional Deployment Steps (MCP Server Specific)**
```bash
# MCP-specific deployment steps (in addition to general workflow)
python -m build && twine upload dist/*
# Restart MCP servers in production environments
# Update MCP server configurations if needed
```

### **GitHub Repository Specific Commands**
```bash
# Check automated reviews and status (project-specific)
gh pr status --repo robertmeisner/mcp_sqlite_memory_bank
```

## PROJECT-SPECIFIC EMERGENCY PROTOCOLS

### **Syntax Error Crisis Recovery (Python Specific)**
```powershell
# Mass fix (emergency only)
git stash push -m "backup before recovery"
black src/ tests/ --line-length=150
autopep8 --in-place --aggressive --recursive src/ tests/
autoflake --in-place --remove-unused-variables --remove-all-unused-imports --recursive src/ tests/
flake8 src/ tests/ --select=E999 --count  # Verify 0 errors
```

## KEY PROJECT LESSONS & COMMITMENTS

### **From June 29, 2025 Crises (Project Specific)**
- **700+ E999 syntax errors**: Prevention > remediation (3+ hours emergency fix)
- **v1.6.0 deployment failure**: NEVER bypass CI/CD checks, even with admin privileges
- **Quality gates work**: CI/CD correctly prevented deployment of broken code

## PROJECT-SPECIFIC COMMON PITFALLS TO AVOID

1. **FastMCP**: Never call decorated functions directly (use `_impl` versions)
2. **Type Safety**: Use `cast(ToolResponse, ...)` for error responses
3. **Database**: Parameterized queries, validate table/column names
4. **Testing**: Temporary DBs, cleanup resources, test error conditions
5. **MCP Server**: Always restart server after code changes for testing

---

**Remember**: This is a professional FastMCP codebase with enterprise-grade quality standards. Follow ALL protocols without exceptions - they prevent production failures and maintain code quality. 🛡️
