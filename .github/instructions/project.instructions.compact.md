---
applyTo: '**'
---

# SQLite Memory Bank Project Instructions (Compact)

## PROJECT OVERVIEW
Dynamic, agent-friendly SQLite memory bank as FastMCP server. Explicit, discoverable APIs for LLM frameworks.

**Core Components**: server.py (FastMCP tools), types.py (exceptions), utils.py (error handling), examples/ (usage patterns)
**Design Principles**: Explicit over implicit, type safety, discoverability, consistent error handling, input validation

## DEVELOPMENT PATTERNS

### FastMCP Tools
```python
@mcp.tool()
def tool_name(param: Type) -> ToolResponse:
    """Tool description for LLM discovery."""
    # Implementation with cast(ToolResponse, error_dict) for errors
```
- Use `_impl` functions for internal Python calls (decorated functions not callable)
- Always return `{"success": True, "data": result}` or error dict
- Use `Optional[Type]` instead of `Type = None`

### Error Handling
- **Custom Exceptions**: MemoryBankError → ValidationError, DatabaseError, SchemaError, DataError
- **Response Format**: `{"success": false, "error": "message", "category": "type", "details": {}}`
- **Decorator**: `@catch_errors` wraps exceptions automatically

### Database Patterns
- **Schema**: snake_case, appropriate constraints, consistent naming
- **Storage**: `create_row('table', {...})`, `upsert_memory()` for deduplication
- **Retrieval**: `read_rows('table', {'where': 'clause'})`, semantic search for discovery

## TESTING & VALIDATION

### Test Structure
- `tests/test_api.py`: FastMCP integration, `tests/test_server.py`: unit tests
- Use `extract_result()` for MCP response parsing
- Temporary DB fixtures: `tempfile.mkstemp(suffix='.db')`

### Type Safety Protocol
1. **Before changes**: Run Pylance/mypy, fix ALL type errors
2. **During development**: Fix type errors immediately
3. **After changes**: Verify zero type errors

## 🚨 CRITICAL: SYNTAX ERROR PREVENTION

### Mandatory Validation Workflow
```powershell
# BEFORE any edits - check for existing syntax errors
flake8 src/ tests/ --select=E999 --count  # Must be 0

# AFTER any edits - verify no new syntax errors
flake8 src/ tests/ --select=E999 --count  # Must still be 0
```

### F-String Safety Rules
❌ **NEVER**: Multi-line f-strings `f"text {variable_on_newline} more"`  
✅ **ALWAYS**: Single line `f"text {variable} more"` or proper parentheses grouping

### String Replacement Safety
- Always validate syntax before/after `replace_string_in_file`
- If errors introduced: `git checkout -- <file_path>` and retry

## QUALITY ASSURANCE

### Pre-Commit Requirements (MANDATORY)
```powershell
# Complete quality check before every commit
flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,W503 --count

# If violations found, run automated fixes:
black src/ tests/ --line-length=88; autopep8 --in-place --aggressive --recursive src/ tests/; autoflake --in-place --remove-unused-variables --remove-all-unused-imports --recursive src/ tests/
```

### VS Code Configuration
```json
{
    "python.linting.flake8Enabled": true,
    "python.linting.flake8Args": ["--select=E999,F821,F822,F823", "--max-line-length=88"],
    "python.linting.lintOnSave": true,
    "python.linting.lintOnType": true,
    "python.formatting.provider": "black"
}
```

## VS CODE MCP WORKFLOW

### Critical: Manual Server Restart Required
**Code changes NOT automatically loaded** - Always restart MCP server after changes:
- `Ctrl+Shift+P` → `MCP: Restart Server` OR `.\restart-mcp.ps1`

### Development Cycle
1. Make changes → 2. Save files → 3. **Restart MCP server** → 4. Test → 5. Repeat

## GIT WORKFLOW (MANDATORY - NO EXCEPTIONS)

### Branch Strategy
- ❌ **FORBIDDEN**: Direct commits/pushes to main branch
- ✅ **REQUIRED**: Feature branches → Pull Requests → Merge to main

### Development Workflow
```bash
git checkout main && git pull origin main
git checkout -b feature/descriptive-name
# Make changes, commit, push
git push origin feature/descriptive-name
gh pr create --title "Feature: Description" --body "Details"
# Wait for CI/CD checks and code reviews
# Merge only after approval + green checks + resolved reviews
```

## DEPLOYMENT WORKFLOW

### Pre-Deployment Checklist (MANDATORY)
1. **Quality**: Run flake8, mypy, Pylance - fix ALL errors
2. **Tests**: Full test suite - ALL TESTS MUST PASS  
3. **Version**: Update pyproject.toml, __init__.py if needed
4. **Documentation**: Update README.md, docs/, instruction files

### Professional Git Release Process
```bash
git checkout main && git pull origin main
git checkout -b release/v1.x.x
git commit -m "chore: prepare release v1.x.x"
git push origin release/v1.x.x
gh pr create --title "Release v1.x.x" --body "Release notes"
```

### ⚠️ CRITICAL: CI/CD Compliance
- **WAIT for ALL checks**: pytest, flake8, mypy, coverage, security
- **CHECK GitHub comments**: `gh pr view <PR> --comments` for automated reviews
- **RESOLVE ALL feedback**: Security issues, performance problems, code quality
- **NEVER merge with failing checks** or unresolved critical issues

### After Green CI/CD + Resolved Reviews
```bash
# Merge PR (via GitHub interface)
git checkout main && git pull origin main
git tag v1.x.x && git push --tags
python -m build && twine upload dist/*
gh release create v1.x.x --latest
```

## EMERGENCY PROTOCOLS

### Syntax Error Crisis Recovery
```powershell
# Mass fix (emergency only)
git stash push -m "backup before recovery"
black src/ tests/ --line-length=88
autopep8 --in-place --aggressive --recursive src/ tests/
autoflake --in-place --remove-unused-variables --remove-all-unused-imports --recursive src/ tests/
flake8 src/ tests/ --select=E999 --count  # Verify 0 errors
```

### Deployment Failure Protocols
- **Immediate**: Stop deployments, assess impact, rollback if needed
- **Analysis**: Root cause analysis, document violation consequences  
- **Prevention**: Update procedures, strengthen protections, team education

## KEY LESSONS & COMMITMENTS

### From June 29, 2025 Crises
- **700+ E999 syntax errors**: Prevention > remediation (3+ hours emergency fix)
- **v1.6.0 deployment failure**: NEVER bypass CI/CD checks, even with admin privileges
- **Quality gates work**: CI/CD correctly prevented deployment of broken code

### Never Again Commitments
- **EVERY edit session** starts with syntax validation
- **EVERY commit** blocked if syntax errors exist  
- **EVERY PR** waits for CI/CD + resolves ALL code review feedback
- **ZERO tolerance** for E999 errors or bypassing quality checks

## COMMON PITFALLS TO AVOID

1. **FastMCP**: Never call decorated functions directly (use `_impl` versions)
2. **Type Safety**: Use `cast(ToolResponse, ...)` for error responses
3. **Database**: Parameterized queries, validate table/column names
4. **Testing**: Temporary DBs, cleanup resources, test error conditions
5. **Deployment**: Wait for checks, review comments, professional Git workflow

---

**Remember**: This is a professional codebase with enterprise-grade quality standards. Follow ALL protocols without exceptions - they prevent production failures and maintain code quality. 🛡️
