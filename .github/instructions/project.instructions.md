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
6. When I say "DEPLOY!", follow the professional Git workflow deployment process outlined in the DEPLOYMENT WORKFLOW section below.

## DEPLOYMENT WORKFLOW

When I say **"DEPLOY!"**, follow these steps in order:

### Pre-Deployment Checklist
1. **Review CHANGELOG.md**: Verify all changes are documented
2. **Quality Checks**: Run `flake8`, `mypy`, Pylance - fix all errors
3. **Test Suite**: Run full test suite - all tests must pass
4. **Version Bump**: Update version in `pyproject.toml`, `__init__.py` if needed
5. **Documentation**: Update `README.md`, `docs/`, instruction files
6. **Clean Working Directory**: `git status` should show clean state

### Release Process (with Professional Git Workflow)
1. **Ensure on main branch**: `git checkout main && git pull origin main`
2. **Create Release Branch**: `git checkout -b release/v1.x.x`
3. **Commit Release**: `git commit -m "chore: prepare release v1.x.x"`
4. **Push Release Branch**: `git push origin release/v1.x.x`
5. **Create Release PR**: Merge release branch to main via PR
6. **Tag Version**: `git tag v1.x.x && git push --tags`
7. **Deploy to PyPI**: `twine upload dist/*`
8. **GitHub Release**: `gh release create v1.x.x --latest`

### Release Notes Best Practices
- Keep `--notes` parameter concise to avoid triggering interactive editor
- Complex release notes should be added via GitHub web interface if needed

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

## GIT WORKFLOW & BRANCHING STRATEGY

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
8. **Then Deploy**: Only after successful merge to main
9. **Cleanup**: Delete feature branch after merge

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

### DEPLOYMENT WORKFLOW

#### **PRE-DEPLOYMENT COMPLIANCE CHECKLIST:**
- [ ] **Branch Check**: Changes merged to main via approved PR
- [ ] **Test Status**: All tests passing
- [ ] **Code Quality**: No linting or type errors
- [ ] **Version Bump**: Version updated in pyproject.toml
- [ ] **Changelog**: CHANGELOG.md updated with changes
- [ ] **Memory Documentation**: Technical decisions recorded

#### **For Production Releases:**
1. **Feature Development**: Work in feature branches (**MANDATORY**)
2. **Pull Request**: Merge to main via PR (**MANDATORY**)
3. **Release Preparation**: Create release branch from main
4. **Version Bump**: Update version numbers, changelog
5. **Release Testing**: Final validation in release branch
6. **Tag & Deploy**: Tag version, deploy to PyPI
7. **GitHub Release**: Create release notes and artifacts

#### **WORKFLOW VIOLATION RECOVERY:**
If workflow was violated (direct commits to main):
1. **Document Violation**: Record in technical_decisions with rationale
2. **Assess Risk**: Evaluate if rollback is needed
3. **Immediate Review**: Get retroactive code review if possible
4. **Process Fix**: Implement stricter branch protection rules
5. **Team Learning**: Update procedures to prevent recurrence

#### **Emergency Hotfixes - CONTROLLED PROCESS:**
1. **STILL USE BRANCHES**: `git checkout -b hotfix/critical-issue main`
2. **Fix & Test**: Implement fix, ensure tests pass
3. **EXPEDITED PR**: Create PR with "URGENT" label for fast-track review
4. **MINIMAL REVIEW**: Single reviewer minimum, focus on fix scope
5. **IMMEDIATE DEPLOY**: Deploy after PR approval, not before
6. **POST-DEPLOYMENT**: Document emergency procedure use in technical_decisions

#### **DEPLOYMENT DECISION MATRIX:**

| Situation | Workflow Required | Time to Deploy |
|-----------|------------------|----------------|
| **Feature Addition** | Feature Branch → PR → Review → Deploy | 1-2 hours |
| **Bug Fix** | Feature Branch → PR → Review → Deploy | 30-60 minutes |
| **Critical Hotfix** | Hotfix Branch → EXPEDITED PR → Deploy | 15-30 minutes |
| **Emergency Security** | Hotfix Branch → EXPEDITED PR → Deploy | 5-15 minutes |

**⚠️ NO situation justifies bypassing PR process entirely**

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
