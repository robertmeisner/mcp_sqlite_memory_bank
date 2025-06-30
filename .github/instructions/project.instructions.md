---
applyTo: '**'
---

# SQLite Memory Bank Project Instructions (Compact)

## PROJECT OVERVIEW
Dynamic, agent-friendly SQLite memory bank as FastMCP server. Explicit, discoverable APIs for LLM frameworks.

**Core Components**: server.py (FastMCP tools), types.py (exceptions), utils.py (error handling), examples/ (usage patterns)
**Design Principles**: Explicit over implicit, type safety, discoverability, consistent error handling, input validation

## 🚨 CRITICAL: TERMINAL USAGE PROTOCOL
**ALWAYS use `isBackground=true` for ALL terminal commands - NO EXCEPTIONS**
- Never use `isBackground=false` - background terminals handle all scenarios
- Use `get_terminal_output()` for output analysis after background execution
- Design workflows to avoid interactive commands requiring foreground execution

## PROJECT-SPECIFIC PATTERNS

### **FastMCP Architecture**
- **server.py**: FastMCP implementation with all tool definitions
- **types.py**: Custom exception classes and type definitions  
- **utils.py**: Utility functions with error handling decorators
- **examples/**: Example scripts showing usage patterns

### **SQLite Memory Bank Usage**
- **Schema Management**: snake_case, appropriate constraints, consistent naming
- **Storage Patterns**: Use `create_row('table', {...})` and `upsert_memory()` for deduplication
- **Retrieval Patterns**: Use `read_rows('table', {'where': 'clause'})` and semantic search for discovery
- **Error Responses**: Always return `{"success": True, "data": result}` or error dict

### **Testing Patterns**
- **Test Structure**: `tests/test_api.py` for FastMCP, `tests/test_server.py` for units
- **Response Testing**: Use `extract_result()` for MCP response parsing
- **Database Testing**: Temporary DB fixtures with `tempfile.mkstemp(suffix='.db')`
- **Error Testing**: Test all error conditions and edge cases

### **Error Handling Hierarchy**
- **Base**: `MemoryBankError` → `ValidationError`, `DatabaseError`, `SchemaError`, `DataError`
- **Decorator**: `@catch_errors` automatically wraps exceptions
- **Format**: `{"success": false, "error": "message", "category": "type", "details": {}}`

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
flake8 src/ tests/ --max-line-length=150 --extend-ignore=E203,W503 --count

# If violations found, run automated fixes:
black src/ tests/ --line-length=150; autopep8 --in-place --aggressive --recursive src/ tests/; autoflake --in-place --remove-unused-variables --remove-all-unused-imports --recursive src/ tests/
```

### VS Code Configuration
```json
{
    "python.linting.flake8Enabled": true,
    "python.linting.flake8Args": ["--select=E999,F821,F822,F823", "--max-line-length=150"],
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

### ⚠️ **FORBIDDEN ACTIONS - NO EXCEPTIONS:**
- ❌ **NEVER commit directly to main branch**
- ❌ **NEVER push directly to main branch**  
- ❌ **NEVER deploy without PR approval**
- ❌ **NEVER bypass workflow "because it's urgent"**

### **Branch Protection Strategy**
- **`main` branch**: Protected, production-ready code only - **ZERO DIRECT COMMITS**
- **Feature branches**: ALL development work (`feature/descriptive-name`)
- **Hotfix branches**: Critical fixes (`hotfix/security-patch`)

### **MANDATORY Development Workflow**
```bash
# Starting new feature
git checkout main && git pull origin main
git checkout -b feature/descriptive-name

# Development process
# Make changes, commit with conventional messages
git add . && git commit -m "feat: add new functionality"
git push origin feature/descriptive-name

# Create PR and wait for reviews
gh pr create --title "Feature: Description" --body "Details"
# MUST wait for CI/CD checks + code reviews + resolve ALL feedback
# Only merge after approval + green checks + resolved reviews
```

### **Branch Naming Conventions**
- **Features**: `feature/semantic-search-enhancement`
- **Bug fixes**: `fix/type-error-in-database`  
- **Tests**: `test/performance-benchmarks`
- **Docs**: `docs/api-documentation-update`
- **Hotfixes**: `hotfix/security-vulnerability`

### **Commit Message Guidelines**
- **Format**: Use conventional commit format: `type(scope): description`
- **Types**: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`, `style`
- **Content**: Clear, descriptive messages explaining the change
- **Co-authored**: **NEVER include `Co-authored-by` lines** - commits should reflect actual human authorship only
- **Examples**: 
  - `feat: add semantic search functionality`
  - `fix: resolve type error in database module`
  - `refactor: eliminate code duplication in filtering logic`

## DEPLOYMENT WORKFLOW

When you say **"DEPLOY!"**, follow these steps in order:

### ⚠️ CRITICAL: PRE-DEPLOYMENT COMPLIANCE CHECKLIST
**NEVER skip these steps - they prevent production failures**

1. **Review CHANGELOG.md**: Verify all changes are documented
2. **Quality Checks**: Run `flake8`, `mypy`, Pylance - fix all errors
3. **Test Suite**: Run full test suite - **ALL TESTS MUST PASS**
4. **Version Bump**: Update version in `pyproject.toml`, `__init__.py` if needed
5. **Documentation**: Update `README.md`, `docs/`, instruction files
6. **Clean Working Directory**: `git status` should show clean state

### 🔒 MANDATORY: Professional Git Workflow for Releases
**Follow this process exactly - NO SHORTCUTS ALLOWED**

```bash
# Step 1-5: Setup release branch
git checkout main && git pull origin main
git checkout -b release/v1.x.x
git commit -m "chore: prepare release v1.x.x"
git push origin release/v1.x.x
gh pr create --title "Release v1.x.x" --body "Release notes"
```

### ⏳ CRITICAL: Wait for CI/CD Checks to Complete
**🚫 NEVER MERGE WITHOUT GREEN CHECKS 🚫**

**Monitor CI/CD Pipeline** - Wait for ALL automated checks:
- ✅ **pytest tests**: All tests must pass
- ✅ **Code quality**: flake8, mypy, pylance checks
- ✅ **Security scans**: No vulnerabilities detected
- ✅ **Coverage reports**: Maintain test coverage standards

## MANDATORY GITHUB COMMENTS & CODE REVIEW PROTOCOL

### 🔍 **CRITICAL REQUIREMENT: ALWAYS CHECK BEFORE MERGE**
**Every PR merge MUST include comprehensive review of all GitHub comments and automated code reviews**

### **GitHub Comments Checking Commands**
```bash
# Check PR comments and reviews
gh pr view <PR_NUMBER> --comments

# Check automated reviews and status
gh pr status --repo robertmeisner/mcp_sqlite_memory_bank
```

### **Code Review Analysis Workflow**
1. **Automated Reviews**: GitHub Copilot bot, security scanners, code quality tools
2. **Priority Classification**:
   - **CRITICAL (Must Fix)**: Security vulnerabilities, breaking changes, critical bugs
   - **HIGH (Recommended)**: Code quality, performance issues, documentation
   - **MEDIUM (Consider)**: Style improvements, non-critical refactoring

### **Implementation Strategy**
- Create implementation checklist for each recommendation
- Implement fixes in release branch before merging
- Mark all review comments as resolved
- Re-run CI/CD checks after fixes

### 🔍 MANDATORY: GitHub Comments & Code Review Analysis
**🚫 NEVER MERGE WITHOUT REVIEWING ALL FEEDBACK 🚫**

```bash
# Check for automated and manual code reviews
gh pr view <PR_NUMBER> --comments
```

**Address ALL feedback**:
- 🤖 **GitHub Copilot Bot Reviews**: Automated code analysis
- 👥 **Human Code Reviews**: All reviewer comments and suggestions
- 🔒 **Security Findings**: Address ANY security vulnerabilities
- ⚡ **Performance Issues**: Fix performance bottlenecks
- ✅ **Review Resolution**: Mark all comments as resolved

### 🚀 Deployment After Successful CI/CD AND Review Resolution
**Only proceed after ALL checks pass AND reviews addressed**

```bash
# Final deployment steps (only after green CI/CD + resolved reviews)
git checkout main && git pull origin main
git tag v1.x.x && git push --tags
python -m build && twine upload dist/*
gh release create v1.x.x --latest
```

### 🚨 DEPLOYMENT FAILURE PROTOCOLS
**If CI/CD checks fail:**
1. **STOP**: Do not proceed with deployment
2. **Analyze**: Review failed check logs carefully
3. **Fix**: Address root cause in release branch
4. **Re-run**: Push fix and wait for checks to complete
5. **Document**: Update CHANGELOG if fix affects functionality

**Emergency Rollback**:
- Revert to last known good version if production affected
- Document violation and consequences
- Update procedures to prevent recurrence

## EMERGENCY PROTOCOLS

### Syntax Error Crisis Recovery
```powershell
# Mass fix (emergency only)
git stash push -m "backup before recovery"
black src/ tests/ --line-length=150
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
