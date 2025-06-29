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
5. **MANDATORY: Run code quality checks** (see CODE QUALITY PREVENTION section below)
6. **RESTART MCP SERVER IN VS CODE**: Use `Ctrl+Shift+P` → `MCP: Restart Server` to load code changes for testing
7. When I say "DEPLOY!", follow the professional Git workflow deployment process outlined in the DEPLOYMENT WORKFLOW section below.

## CODE QUALITY PREVENTION PROTOCOL

### ⚠️ MANDATORY PRE-COMMIT WORKFLOW
**NEVER commit code without running these checks first - prevents CI/CD pipeline failures**

#### 1. AUTOMATED LINTING CHECKS (REQUIRED BEFORE EVERY COMMIT)
```powershell
# Basic linting check (MANDATORY)
flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,W503 --count

# If critical violations found (F811, F841, F541, E303), run automated fixes:
black src/ tests/ --line-length=88
autopep8 --in-place --aggressive --recursive src/ tests/
autoflake --in-place --remove-unused-variables --remove-all-unused-imports --recursive src/ tests/
```

#### 2. CRITICAL VIOLATION TYPES TO PREVENT
- **F811**: Import redefinitions (multiple imports of same name)
- **F841**: Unused variables (leftover from development)
- **F541**: f-string placeholders without expressions
- **E303**: Too many blank lines between functions/classes
- **E501**: Line length violations (less critical but still important)

#### 3. AUTOMATED FORMATTING WORKFLOW
```powershell
# Complete automated formatting pipeline (run when linting fails)
black src/ tests/ --line-length=88; autopep8 --in-place --aggressive --recursive src/ tests/; autoflake --in-place --remove-unused-variables --remove-all-unused-imports --recursive src/ tests/; flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,W503 --count
```

### PREVENTION STRATEGIES

#### Pre-Commit Hook Setup (RECOMMENDED)
```powershell
# Create .git/hooks/pre-commit file with:
#!/bin/sh
echo "Running code quality checks..."
flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,W503 --count
if [ $? -ne 0 ]; then
    echo "❌ Linting failed! Run automated fixes before committing."
    echo "Run: black src/ tests/ --line-length=88"
    echo "Run: autopep8 --in-place --aggressive --recursive src/ tests/"
    echo "Run: autoflake --in-place --remove-unused-variables --remove-all-unused-imports --recursive src/ tests/"
    exit 1
fi
```

#### Editor Configuration (VS Code settings.json)
```json
{
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.flake8Args": ["--max-line-length=88", "--extend-ignore=E203,W503"],
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length=88"],
    "editor.formatOnSave": true,
    "python.linting.lintOnSave": true
}
```

#### Development Best Practices
1. **Import Organization**: Use consistent import ordering and avoid duplicate imports
2. **Variable Management**: Remove unused variables immediately during development
3. **F-String Usage**: Ensure all f-string placeholders have valid expressions
4. **Line Length**: Keep lines under 88 characters (Black standard)
5. **Blank Line Management**: Follow PEP 8 for spacing between functions/classes

### EMERGENCY LINTING REMEDIATION (When CI/CD Fails)

#### Phase 1: Automated Fixes
```powershell
# Step 1: Black formatting
black src/ tests/ --line-length=88

# Step 2: Aggressive autopep8 fixes
autopep8 --in-place --aggressive --recursive src/ tests/

# Step 3: Remove unused imports/variables
autoflake --in-place --remove-unused-variables --remove-all-unused-imports --recursive src/ tests/
```

#### Phase 2: Manual Critical Fixes
```powershell
# Check remaining critical violations
flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,W503,E501 --select=F811,F841,F541,E303

# Fix manually:
# F811: Remove duplicate imports
# F841: Remove unused variables
# F541: Fix f-string placeholders
# E303: Remove extra blank lines
```

#### Phase 3: Line Length Management (Optional)
```powershell
# Check line length violations (less critical)
flake8 src/ tests/ --max-line-length=88 --select=E501 --count
```

### LESSONS LEARNED FROM LINTING CRISIS (June 29, 2025)

#### What Happened
- **700+ flake8 violations** blocked v1.6.3 deployment
- **CI/CD pipeline correctly prevented** deployment of poor-quality code
- **Emergency remediation required** 3-phase automated + manual fixing

#### Root Causes
1. **No pre-commit linting checks** in development workflow
2. **Accumulated technical debt** from incremental development
3. **Missing automated formatting** in regular development cycle
4. **Manual code formatting** led to inconsistent style

#### Prevention Measures Implemented
1. **Mandatory pre-commit checks** added to project instructions
2. **Automated formatting pipeline** documented for emergency use
3. **Editor configuration** provided for continuous quality assurance
4. **CI/CD compliance emphasis** in deployment instructions

#### Key Takeaways
- **Quality gates work**: CI/CD correctly prevented deployment of problematic code
- **Automation is essential**: Manual formatting is not scalable for large codebases
- **Prevention > Remediation**: Pre-commit checks are faster than emergency fixes
- **Professional workflows matter**: Following proper Git/CI processes saves time long-term

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

### 🚨 LESSONS FROM LINTING CRISIS: Why CI/CD Compliance Matters
**v1.6.3 Emergency (June 29, 2025)**: 700+ flake8 violations blocked deployment
- **What Happened**: Bypassed pre-commit checks, accumulated massive technical debt
- **CI/CD Response**: Quality gates correctly prevented deployment of poor-quality code
- **Emergency Fix**: Required 3-phase remediation (automated + manual fixes)
- **Key Lesson**: **PREVENTION > CRISIS REMEDIATION** - pre-commit checks are mandatory

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

#### **Example Crisis: v1.6.3 Linting Failure (June 29, 2025)**
**Issue**: Massive CI/CD pipeline failure due to 700+ flake8 violations blocking deployment
- Violation types: F811 (import redefinitions), F841 (unused variables), F541 (f-string placeholders), E303 (blank lines), E501 (line length)
- Root cause: No pre-commit linting checks, accumulated technical debt over time
- Impact: Complete deployment blockage requiring emergency 3-phase remediation
- Emergency fix: Black formatting → autopep8 aggressive fixes → autoflake cleanup → manual critical fixes
- Lesson: **Prevention is 100x easier than crisis remediation**

**Corrective Actions**:
- ✅ Added mandatory pre-commit linting workflow to project instructions
- ✅ Documented 3-phase emergency remediation process for future crises
- ✅ Created automated formatting pipeline commands
- ✅ Added VS Code editor configuration for continuous quality assurance
- ✅ Emphasized CI/CD compliance in deployment instructions
- 🔄 TODO: Set up automated pre-commit hooks
- 🔄 TODO: Add linting status badges to README

#### **Prevention Strategies**:
- **Patience Over Speed**: Wait for all checks, even if it takes longer
- **No Admin Overrides**: Admin privileges are for emergencies only, not convenience
- **Double-Check Green Status**: Visually verify all checks are green before merging
- **Test in Production**: Quick smoke test after deployment to catch immediate issues
- **Pre-Commit Quality Checks**: Run linting and formatting before every commit
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

### GIT PR CREATION BEST PRACTICES

#### **Avoid Interactive Mode Issues**
- **Never use complex multi-line --body arguments** with `gh pr create`
- **Use simple, single-line descriptions** for PR creation
- **Add detailed descriptions via GitHub web interface** after PR creation
- **Alternative**: Use separate commands for title and body

#### **Recommended PR Creation Pattern**
```bash
# Simple PR creation (avoid interactive mode)
gh pr create --title "feat: brief description of change" --body "Simple one-line description. Details added via web interface."

# Or even simpler
gh pr create --title "feat: brief description" --body "See commit message for details"
```

#### **Why This Matters**
- **Prevents Terminal Hang**: Complex --body arguments cause interactive mode
- **Faster Workflow**: Simple commands execute immediately  
- **Better UX**: Detailed formatting done in GitHub web interface
- **Reliable Automation**: Predictable command execution
