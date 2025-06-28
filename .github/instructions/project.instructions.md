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
5. Fix linting issues with `flake8` and type issues with mypy and pylance errors
6. **RESTART MCP SERVER IN VS CODE**: Use `Ctrl+Shift+P` → `MCP: Restart Server` to load code changes for testing
7. When I say "DEPLOY!", follow the professional Git workflow deployment process outlined in the DEPLOYMENT WORKFLOW section below.

## VS CODE MCP DEVELOPMENT WORKFLOW

### ⚠️ CRITICAL: Manual Server Restart Required
- **Code changes are NOT automatically loaded** in VS Code MCP environment
- **ALWAYS restart MCP server** after making code changes before testing
- **Keyboard shortcut**: `Ctrl+Shift+P` → Type `MCP: Restart Server` → Enter
- **Alternative**: Use restart script: `.\restart-mcp.ps1` in terminal

### VS Code MCP Testing Pattern
1. **Make code changes** (edit files)
2. **Save files** (Ctrl+S)
3. **Restart MCP server** (Ctrl+Shift+P → `MCP: Restart Server`)
4. **Test changes** using MCP tools
5. **Repeat cycle** as needed

### Why This Matters
- **Cached modules**: VS Code MCP client caches Python modules
- **Stale code**: Testing without restart uses old code version
- **False negatives**: Fixes may appear not to work due to stale cache
- **Development efficiency**: Proper restart cycle prevents debugging phantom issues

## DEPLOYMENT WORKFLOW

When I say **"DEPLOY!"**, follow these steps in order:

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

1. **Ensure on main branch**: `git checkout main && git pull origin main`
2. **Create Release Branch**: `git checkout -b release/v1.x.x`
3. **Commit Release**: `git commit -m "chore: prepare release v1.x.x"`
4. **Push Release Branch**: `git push origin release/v1.x.x`
5. **Create Release PR**: `gh pr create --title "Release v1.x.x" --body "Release notes"`

### ⏳ CRITICAL: Wait for CI/CD Checks to Complete
**🚫 NEVER MERGE WITHOUT GREEN CHECKS 🚫**

6. **Monitor CI/CD Pipeline**: Wait for ALL automated checks to complete
   - ✅ **pytest tests**: All tests must pass
   - ✅ **Code quality**: flake8, mypy, pylance checks
   - ✅ **Security scans**: No vulnerabilities detected
   - ✅ **Coverage reports**: Maintain test coverage standards
7. **Address Failures IMMEDIATELY**: If any check fails:
   - ❌ **DO NOT MERGE the PR**
   - 🔧 **Fix the issue in the release branch**
   - 🔄 **Push fixes and wait for checks to re-run**
   - ✅ **Only proceed when ALL checks are green**

### 🚀 Deployment After Successful CI/CD
**Only proceed after ALL automated checks pass**

8. **Merge PR**: Only after approval AND green CI/CD checks
9. **Switch to Main**: `git checkout main && git pull origin main`
10. **Tag Version**: `git tag v1.x.x && git push --tags`
11. **Build Package**: `python -m build`
12. **Deploy to PyPI**: `twine upload dist/*`
13. **GitHub Release**: `gh release create v1.x.x --latest`

### 📋 CI/CD Check Requirements
**All of these MUST pass before merging:**

- **✅ pytest**: All unit and integration tests pass
- **✅ flake8**: No linting errors
- **✅ mypy/pylance**: No type errors
- **✅ Coverage**: Minimum coverage thresholds met
- **✅ Security**: No vulnerabilities detected
- **✅ Build**: Package builds successfully

### 🚨 Error Handling During Deployment
**If CI/CD checks fail:**

1. **STOP**: Do not proceed with deployment
2. **Analyze**: Review failed check logs carefully
3. **Fix**: Address the root cause in the release branch
4. **Test**: Verify fix locally before pushing
5. **Re-run**: Push fix and wait for checks to complete
6. **Verify**: Ensure ALL checks are now green
7. **Document**: Update CHANGELOG if fix affects functionality

### 🚨 DEPLOYMENT FAILURE PROTOCOLS & LEARNING

#### **When Deployment Violations Occur:**
If CI/CD checks were bypassed or failed tests were merged to production:

1. **IMMEDIATE ASSESSMENT**:
   - Stop any ongoing deployments
   - Assess severity of production impact
   - Document the violation and its consequences

2. **ROLLBACK PROCEDURES**:
   - Revert to last known good version if production is affected
   - Notify stakeholders about the rollback
   - Document rollback actions and timeline

3. **ROOT CAUSE ANALYSIS**:
   - Analyze why CI/CD checks were bypassed
   - Identify specific test failure that reached production
   - Review deployment logs and decision-making process
   - Document findings in technical_decisions table

4. **PROCESS IMPROVEMENT**:
   - Update deployment procedures to prevent recurrence
   - Strengthen branch protection rules if necessary
   - Add additional automated checks if gaps identified
   - Ensure team understands updated procedures

#### **Example Failure: v1.6.0 Deployment (June 28, 2025)**
**Issue**: Merged PR without waiting for CI/CD checks, resulting in failed test reaching production
- Test failure: `test_auto_smart_search_complete_workflow` (0 results expected >= 2)
- Root cause: Used `--admin` flag to bypass branch protection
- Impact: Production deployment with known failing test
- Lesson: NEVER use admin privileges to bypass CI/CD requirements

**Corrective Actions**:
- ✅ Updated project instructions to emphasize CI/CD wait requirements
- ✅ Added explicit warnings about bypassing automated checks
- ✅ Documented this failure as learning example
- 🔄 TODO: Strengthen branch protection to prevent admin bypasses
- 🔄 TODO: Add post-deployment verification scripts

#### **Prevention Strategies**:
- **Patience Over Speed**: Wait for all checks, even if it takes longer
- **No Admin Overrides**: Admin privileges are for emergencies only, not convenience
- **Double-Check Green Status**: Visually verify all checks are green before merging
- **Test in Production**: Quick smoke test after deployment to catch immediate issues

### GIT WORKFLOW & BRANCHING STRATEGY

### ⚠️ MANDATORY WORKFLOW - NO EXCEPTIONS ⚠️
**ALL development work MUST use feature branches, then Pull Requests to main**

#### **🚫 FORBIDDEN ACTIONS:**
- ❌ **NEVER commit directly to main branch**
- ❌ **NEVER push directly to main branch**  
- ❌ **NEVER deploy without PR approval**
- ❌ **NEVER bypass the workflow "because it's urgent"**

#### **Branch Protection Strategy:**
- **`main` branch**: Protected, production-ready code only - **ZERO DIRECT COMMITS**
- **Feature branches**: ALL development work (`feature/test-improvements`, `feature/semantic-search`, etc.)  
- **Hotfix branches**: Critical fixes (`hotfix/security-patch`, `hotfix/critical-bug`)

#### **MANDATORY Development Workflow:**
1. **ALWAYS Create Feature Branch**: `git checkout -b feature/descriptive-name`
2. **Develop & Test**: Make changes, ensure all tests pass
3. **Commit Changes**: Use conventional commit messages
4. **Push Feature Branch**: `git push origin feature/descriptive-name`
5. **ALWAYS Create Pull Request**: Via GitHub web interface or `gh` CLI
6. **Code Review**: Review changes, run CI/CD checks
7. **Merge to Main**: Only after approval and all checks pass
8. **Cleanup**: Delete feature branch after merge

**Deployment happens only after successful merge to main** (see Deployment Workflow section below)

#### **Branch Naming Conventions:**
- **Features**: `feature/semantic-search-enhancement`
- **Bug fixes**: `fix/type-error-in-database`
- **Tests**: `test/performance-benchmarks`
- **Docs**: `docs/api-documentation-update`
- **Hotfixes**: `hotfix/security-vulnerability`

#### **Pull Request Guidelines:**
- **Title**: Clear, descriptive (e.g., "Add comprehensive test suite with 57 tests")
- **Description**: What changed, why, testing done
- **Reviewers**: Assign appropriate reviewers
- **Labels**: Use GitHub labels for categorization
- **CI/CD**: Ensure all automated checks pass

### GIT COMMANDS FOR WORKFLOW

#### **Starting New Feature:**
```bash
git checkout main
git pull origin main
git checkout -b feature/your-feature-name
```

#### **Working on Feature:**
```bash
git add .
git commit -m "feat: descriptive commit message"
git push origin feature/your-feature-name
```

#### **Creating Pull Request:**
```bash
# Via GitHub CLI (recommended)
gh pr create --title "Feature: Your Feature Name" --body "Description of changes"

# Or via web interface at github.com
```

#### **After PR Approval:**
```bash
# Merge via GitHub interface (recommended) or:
git checkout main
git pull origin main
git branch -d feature/your-feature-name  # Delete local branch
git push origin --delete feature/your-feature-name  # Delete remote branch
```

### MAIN BRANCH PROTECTION

#### **Recommended Settings:**
- **Require pull request reviews**: At least 1 reviewer
- **Require status checks**: All CI/CD tests must pass
- **Require branches to be up to date**: Prevent conflicts
- **Restrict pushes to main**: Only via approved pull requests
- **Require linear history**: Clean commit history

#### **CI/CD Integration:**
```yaml
# .github/workflows/ci.yml should include:
- Automated testing (pytest)
- Code quality checks (flake8, mypy)
- Security scanning
- Performance benchmarks
- Documentation builds
```

### WHY THIS WORKFLOW?

#### **Benefits:**
- **Code Quality**: All changes reviewed before reaching main
- **Collaboration**: Multiple developers can work simultaneously
- **Rollback Safety**: Main branch always in deployable state
- **CI/CD Integration**: Automated testing prevents broken deployments
- **Documentation**: PR descriptions provide change history
- **Conflict Resolution**: Merge conflicts resolved in feature branches

#### **For Solo Development:**
- **Still Recommended**: Establishes good habits and practices
- **Local Testing**: Feature branches allow experimental work
- **Clean History**: Main branch has clean, logical commit history
- **Future Collaboration**: Ready for team development
