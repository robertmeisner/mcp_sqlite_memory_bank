---
applyTo: '**'
---

# GENERAL DEVELOPMENT INSTRUCTIONS

## PRIME DIRECTIVE
	User/Author: Robert Meisner robert@catchit.pl
	Be chatting and teach about what you are doing while coding.
    First analyze the problem and requirements. Then, write a gameplan that implements the solution. 
	The gameplan should be well-structured, with clear next steps and comments explaining each phase.
    Always provide a clear, concise summary of the changes made at the end of each edit.
    If you encounter an error or unexpected behavior, stop and analyze the issue before proceeding.
    Never make changes that could break existing functionality without thorough testing and validation.
    As a last step review the code for any potential improvements or optimizations and execute them if needed.

## COMMUNICATION PROTOCOLS
	- **Explain Before Acting**: Always explain what you're about to do and why
	- **Real-Time Updates**: Provide progress updates during long operations
	- **Error Communication**: When errors occur, explain the error, root cause, and solution
	- **Teaching Moments**: Use coding opportunities to explain best practices
	- **Decision Rationale**: Always explain the reasoning behind technical decisions
	- **Alternative Approaches**: Mention alternative solutions and why the chosen approach is preferred

## GIT COMMIT PROTOCOLS
	- **Format**: Use conventional commit format: `type(scope): description`
	- **Types**: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`, `style`
	- **Content**: Clear, descriptive messages explaining the change
	- **Co-authored**: **NEVER include `Co-authored-by` lines** - commits should reflect actual human authorship only
	- **Examples**: 
		- `feat: add semantic search functionality`
		- `fix: resolve type error in database module`
		- `refactor: eliminate code duplication in filtering logic`

## KNOWLEDGE MANAGEMENT & DOCUMENTATION
	If you encounter a topic or technology you are not familiar with, do not attempt to guess or make assumptions.
	Instead, ask for clarification or additional information before proceeding.
	Always analyze and use available MCP servers (e.g. context7 for library/package documentation) and other tools.
	Store the library docs you've downloaded in the `temp/docs` directory as {lib_name}.md files for future reference.
	If you need to reference external libraries or frameworks, ensure you have the latest documentation available.
	Always check if the library is already downloaded in the `temp/docs` directory before asking for it.
	Always prioritize accuracy and reliability over speed.
	If you are unsure about a solution, take the time to research and verify before implementing it.
	When you fetch documentation for any library or package, always save it as a Markdown file in temp/docs/{lib_name}.md before using or referencing it in your workflow.

## LARGE FILE & COMPLEX CHANGE PROTOCOL

### MANDATORY PLANNING PHASE
	ALWAYS start by creating a detailed gameplan (at least 10 steps or more) BEFORE making any edits
	Your plan MUST include:
	- All functions/sections that need modification
	- The order in which changes should be applied
	- Dependencies between changes
	- Estimated number of separate edits required

### MAKING EDITS
	- Include concise explanations of what changed and why
	- Always check if the edit maintains the project's coding style
	- If class or complex change is too large, decompose it down into smaller, manageable components

### EXECUTION PHASE
	- After each individual edit, clearly indicate progress:
		"✅ Completed edit [#] of [total]. Ready for next edit?"
	- If you discover additional needed changes during editing:
	- STOP and update the plan

### REFACTORING GUIDANCE
	- Break work into logical, independently functional chunks
	- Ensure each intermediate state maintains functionality
	- Always indicate the refactoring pattern being applied

### RATE LIMIT AVOIDANCE
	- For very large files, suggest splitting changes across multiple sessions
	- Prioritize changes that are logically complete units
	- Always provide clear stopping points

## LANGUAGE-SPECIFIC REQUIREMENTS

### Python Requirements
	- **Target Version**: Python 3.9 or higher (3.12+ preferred for latest type features)
	- **Type Safety & Static Analysis**:
		- **MANDATORY**: Use explicit type annotations for all functions, methods, and variables
		- Include proper return type annotations (`-> Type` or `-> None`)
		- Use `Optional[Type]` for parameters that can be None instead of `Type = None`
		- Use `Union[Type1, Type2]` or `Type1 | Type2` (Python 3.10+) for multiple types
		- Leverage generic types (`TypeVar`, `Generic`) for flexible, type-safe code
		- Use `Sequence[T]` instead of `List[T]` for parameters that accept various sequence types
		- Always run Pylance/mypy static analysis and fix ALL type errors before committing
		- Use `cast()` sparingly and only when necessary for complex type scenarios
		- Prefer `hasattr()` and `getattr()` for dynamic attribute access with proper error handling
	- **Modern Python Features** (Python 3.9+):
		- Use dataclasses or Pydantic models for structured data
		- Leverage pattern matching (`match/case`) for Python 3.10+
		- Use positional-only and keyword-only parameters where appropriate
		- Prefer `pathlib.Path` over string manipulation for file paths
		- Use f-strings for all string formatting
		- Leverage `functools.cache` and `functools.lru_cache` for memoization
		- Use `contextvars` for context-aware programming
		- Use structural pattern matching where it improves readability
	- **Error Handling**:
		- Create custom exception hierarchies with meaningful inheritance
		- Use `try/except/else/finally` blocks appropriately
		- Always specify specific exception types, avoid bare `except:`
		- Include detailed error messages with context for debugging
		- Use `logging` module instead of `print()` for debugging/info output
		- Implement proper error recovery strategies
	- **Code Quality**:
		- Follow PEP 8 with max line length of 88 characters (Black formatter standard)
		- Use Black formatter and isort for consistent code style
		- Include comprehensive docstrings (Google or NumPy style)
		- Use meaningful variable and function names that self-document
		- Implement proper module structure with `__all__` exports
		- Use `@property` decorators for computed attributes
		- Implement `__str__` and `__repr__` methods for custom classes
	- **Dependencies & Packaging**:
		- Use `pyproject.toml` for project configuration
		- Pin dependency versions appropriately (avoid loose constraints)
		- Use virtual environments consistently
		- Include proper entry points and console scripts
		- Use `requirements.txt` for production dependencies
		- Separate dev dependencies in `requirements-dev.txt` or `pyproject.toml`
	- **Testing**:
		- Use pytest for all testing
		- Achieve minimum 80% test coverage
		- Include both unit tests and integration tests
		- Use proper fixtures and parametrized tests
		- Test error conditions and edge cases
		- Use mocking appropriately for external dependencies

### JavaScript Requirements
	- **Minimum Compatibility**: ECMAScript 2020 (ES11) or higher
	- **Features to Use**:
		- Arrow functions
		- Template literals
		- Destructuring assignment
		- Spread/rest operators
		- Async/await for asynchronous code
		- Classes with proper inheritance when OOP is needed
		- Object shorthand notation
		- Optional chaining (`?.`)
		- Nullish coalescing (`??`)
		- Dynamic imports
		- BigInt for large integers
		- `Promise.allSettled()`
		- `String.prototype.matchAll()`
		- `globalThis` object
		- Private class fields and methods
		- Export * as namespace syntax
		- Array methods (`map`, `filter`, `reduce`, `flatMap`, etc.)
	- **Avoid**:
		- `var` keyword (use `const` and `let`)
		- jQuery or any external libraries
		- Callback-based asynchronous patterns when promises can be used
		- Internet Explorer compatibility
		- Legacy module formats (use ES modules)
		- Limit use of `eval()` due to security risks
	- **Performance Considerations:**
		- Recommend code splitting and dynamic imports for lazy loading
	- **Error Handling**:
		- Use `try-catch` blocks **consistently** for asynchronous and API calls, and handle promise rejections explicitly.
		- Differentiate among:
			- **Network errors** (e.g., timeouts, server errors, rate-limiting)
			- **Functional/business logic errors** (logical missteps, invalid user input, validation failures)
			- **Runtime exceptions** (unexpected errors such as null references)
		- Provide **user-friendly** error messages (e.g., "Something went wrong. Please try again shortly.") and log more technical details to dev/ops (e.g., via a logging service).
		- Consider a central error handler function or global event (e.g., `window.addEventListener('unhandledrejection')`) to consolidate reporting.
		- Carefully handle and validate JSON responses, incorrect HTTP status codes, etc.

### PHP Requirements
	- **Target Version**: PHP 8.1 or higher
	- **Features to Use**:
		- Named arguments
		- Constructor property promotion
		- Union types and nullable types
		- Match expressions
		- Nullsafe operator (`?->`)
		- Attributes instead of annotations
		- Typed properties with appropriate type declarations
		- Return type declarations
		- Enumerations (`enum`)
		- Readonly properties
		- Emphasize strict property typing in all generated code.
	- **Coding Standards**:
		- Follow PSR-12 coding standards
		- Use strict typing with `declare(strict_types=1);`
		- Prefer composition over inheritance
		- Use dependency injection
	- **Static Analysis:**
		- Include PHPDoc blocks compatible with PHPStan or Psalm for static analysis
	- **Error Handling:**
		- Use exceptions consistently for error handling and avoid suppressing errors.
		- Provide meaningful, clear exception messages and proper exception types.

### HTML/CSS Requirements
	- **HTML**:
		- Use HTML5 semantic elements (`<header>`, `<nav>`, `<main>`, `<section>`, `<article>`, `<footer>`, `<search>`, etc.)
		- Include appropriate ARIA attributes for accessibility
		- Ensure valid markup that passes W3C validation
		- Use responsive design practices
		- Optimize images using modern formats (`WebP`, `AVIF`)
		- Include `loading="lazy"` on images where applicable
		- Generate `srcset` and `sizes` attributes for responsive images when relevant
		- Prioritize SEO-friendly elements (`<title>`, `<meta description>`, Open Graph tags)
	- **CSS**:
		- Use modern CSS features including:
			- CSS Grid and Flexbox for layouts
			- CSS Custom Properties (variables)
			- CSS animations and transitions
			- Media queries for responsive design
			- Logical properties (`margin-inline`, `padding-block`, etc.)
			- Modern selectors (`:is()`, `:where()`, `:has()`)
		- Follow BEM or similar methodology for class naming
		- Use CSS nesting where appropriate
		- Include dark mode support with `prefers-color-scheme`
		- Prioritize modern, performant fonts and variable fonts for smaller file sizes
		- Use modern units (`rem`, `vh`, `vw`) instead of traditional pixels (`px`) for better responsiveness

## WEB STANDARDS & ACCESSIBILITY

### Accessibility
	- Ensure compliance with **WCAG 2.1** AA level minimum, AAA whenever feasible.
	- Always suggest:
		- Labels for form fields.
		- Proper **ARIA** roles and attributes.
		- Adequate color contrast.
		- Alternative texts (`alt`, `aria-label`) for media elements.
		- Semantic HTML for clear structure.
		- Tools like **Lighthouse** for audits.

### Browser Compatibility
	- Prioritize feature detection (`if ('fetch' in window)` etc.).
	- Support latest two stable releases of major browsers:
		- Firefox, Chrome, Edge, Safari (macOS/iOS)
	- Emphasize progressive enhancement with polyfills or bundlers (e.g., **Babel**, **Vite**) as needed.

## GENERAL PROJECT STRUCTURE
	Follow this structured directory layout:

		project-root/
		├── api/                  # API handlers and routes
		├── config/               # Configuration files and environment variables
		├── data/                 # Databases, JSON files, and other storage
		├── public/               # Publicly accessible files (served by web server)
		│   ├── assets/
		│   │   ├── css/
		│   │   ├── js/
		│   │   ├── images/
		│   │   ├── fonts/
		│   └── index.html
		├── src/                  # Application source code
		│   ├── controllers/
		│   ├── models/
		│   ├── views/
		│   └── utilities/
		├── tests/                # Unit and integration tests
		├── docs/                 # Documentation (Markdown files)
		├── logs/                 # Server and application logs
		├── scripts/              # Scripts for deployment, setup, etc.
		└── temp/                 # Temporary/cache files

## DATABASE REQUIREMENTS
	- **General**: Sanitize all user inputs thoroughly, parameterize database queries
	- Use appropriate database-specific features and constraints
	- Leverage modern database capabilities (JSON columns, generated columns, etc.)

## SECURITY CONSIDERATIONS
	- Sanitize all user inputs thoroughly.
	- Parameterize database queries.
	- Enforce strong Content Security Policies (CSP).
	- Use CSRF protection where applicable.
	- Ensure secure cookies (`HttpOnly`, `Secure`, `SameSite=Strict`).
	- Limit privileges and enforce role-based access control.
	- Implement detailed internal logging and monitoring.

## DOCUMENTATION REQUIREMENTS
	- Include JSDoc comments for JavaScript/TypeScript.
	- Document complex functions with clear examples.
	- Maintain concise Markdown documentation.
	- Minimum docblock info: `param`, `return`, `throws`, `author`

## TYPE SAFETY & STATIC ANALYSIS PROTOCOL

### MANDATORY TYPE CHECKING WORKFLOW
	1. **Before ANY code changes**: Run static analysis tools (Pylance, mypy)
	2. **During development**: Fix type errors IMMEDIATELY as they appear
	3. **After each edit**: Verify no new type errors were introduced
	4. **Before commit**: Ensure zero type errors in affected files

### TYPE ERROR FIXING STRATEGY
	1. **Identify root cause**: Understand WHY the type error occurred
	2. **Choose appropriate fix**:
		- Add missing type annotations
		- Use `Optional[T]` for nullable types
		- Use `Union[T1, T2]` for multiple types
		- Use `cast()` only when necessary and safe
		- Use `TypeVar` and `Generic` for flexible typing
	3. **Verify fix**: Ensure type error is resolved without breaking functionality
	4. **Document reasoning**: Add comment explaining complex type decisions

### COMMON TYPE PATTERNS & SOLUTIONS
	- **Tool Functions**: Use proper type casting for error handlers when needed
	- **Optional Parameters**: Use `Optional[Type]` instead of `Type = None`
	- **Sequence Types**: Use `Sequence[T]` for covariant parameters
	- **Dynamic Access**: Use `hasattr()` and `getattr()` with proper guards
	- **Complex Return Types**: Define clear Union types or custom TypedDict classes

### TYPE ANNOTATION REQUIREMENTS
	- **All functions**: Must have parameter and return type annotations
	- **All class attributes**: Must be type-annotated
	- **Complex data structures**: Use TypedDict or dataclasses
	- **Generic functions**: Use TypeVar and bounds appropriately

## ERROR HANDLING & DEBUGGING PROTOCOL

### SYSTEMATIC ERROR DIAGNOSIS
	1. **Immediate Response**: When encountering any error, STOP and analyze before continuing
	2. **Error Classification**:
		- **Type Errors**: Static analysis violations (Pylance, mypy)
		- **Runtime Errors**: Exceptions during execution
		- **Import Errors**: Module/package resolution issues
		- **Logic Errors**: Incorrect behavior without exceptions
	3. **Documentation**: Always document the error type, cause, and solution for future reference

### DEBUGGING WORKFLOW
	1. **Read the Full Error**: Don't just fix the symptom, understand the root cause
	2. **Use Available Tools**: 
		- `get_errors` tool for static analysis issues
		- `run_in_terminal` for testing fixes
		- `grep_search` for finding related code patterns
	3. **Test Incrementally**: Make small changes and verify each step
	4. **Validate Fixes**: Run tests after each major fix to ensure no regressions

### ERROR PREVENTION
	- **Proactive Type Checking**: Run static analysis before making changes
	- **Test-Driven Fixes**: Write or run tests to validate your understanding
	- **Documentation Review**: Check existing code comments and docstrings for context

## TESTING & VALIDATION REQUIREMENTS

### MANDATORY TESTING WORKFLOW
	1. **Before Changes**: Run existing tests to establish baseline
	2. **After Each Edit**: Run relevant tests to catch regressions immediately
	3. **After Major Changes**: Run full test suite before commit
	4. **Test Coverage**: Aim for minimum 80% code coverage

### TEST TYPES & STRATEGIES
	- **Unit Tests**: Test individual functions and methods in isolation
	- **Integration Tests**: Test component interactions and data flow
	- **Type Tests**: Validate type annotations with mypy/pylance
	- **Error Handling Tests**: Test all error conditions and edge cases
	- **Performance Tests**: Validate performance requirements for critical paths

### VALIDATION PROTOCOLS
	- **Static Analysis**: Always run and fix Pylance/mypy errors
	- **Code Style**: Use Black/isort for Python, appropriate formatters for other languages
	- **Security**: Validate input sanitization and SQL injection prevention
	- **Documentation**: Ensure all public APIs are documented with examples

## TERMINAL COMMAND EFFICIENCY PROTOCOL

### MANDATORY BACKGROUND TERMINAL USAGE
**ALWAYS use isBackground=true for ALL terminal commands - NO EXCEPTIONS**:

#### Background Terminal Protocol
```python
# ALWAYS use background terminals for ALL commands - NEVER use isBackground=false
run_in_terminal(
    command="your command here",
    explanation="What the command does",
    isBackground=true  # ← MANDATORY: ALWAYS use background=true - NO EXCEPTIONS
)

# After the operation is complete, close the terminal if needed
# Background terminals automatically handle cleanup
```

#### Why Background Terminals Are Required
- **Performance**: Background terminals don't block the AI's processing
- **Efficiency**: Allows parallel operations and faster execution
- **Resource Management**: Proper cleanup prevents terminal accumulation
- **User Experience**: Non-blocking operations provide better responsiveness

#### Background Terminal Best Practices
- **Always set isBackground=true** unless specifically requiring interactive input
- **Use clear explanations** to document what each command accomplishes
- **Group related commands** when possible to minimize terminal calls
- **Let background terminals auto-cleanup** instead of manual terminal management

### MANDATORY COMMAND BATCHING STRATEGY
**NEVER make dozens of separate terminal calls**. Always group related commands and execute them efficiently to minimize tool calls and improve performance.

### COMMAND GROUPING PATTERNS

#### Single Command Line with Multiple Operations
```
# WRONG - Multiple separate terminal calls
1. run_in_terminal(command="cd project_directory", isBackground=true)
2. run_in_terminal(command="npm install", isBackground=true)
3. run_in_terminal(command="npm run build", isBackground=true)
4. run_in_terminal(command="npm test", isBackground=true)
5. run_in_terminal(command="npm run lint", isBackground=true)

# RIGHT - Group related commands with background execution
run_in_terminal(
    command="cd project_directory; npm install; npm run build; npm test; npm run lint",
    explanation="Complete build and test pipeline",
    isBackground=true
)
```

#### Multi-line Commands for Complex Operations
```
# WRONG - Fragmented file operations
1. run_in_terminal(command="mkdir -p src/components", isBackground=true)
2. run_in_terminal(command="mkdir -p src/utils", isBackground=true)
3. run_in_terminal(command="mkdir -p tests", isBackground=true)
4. run_in_terminal(command="touch src/index.js", isBackground=true)
5. run_in_terminal(command="touch README.md", isBackground=true)

# RIGHT - Batch directory and file creation with background execution
run_in_terminal(
    command="mkdir -p src/components src/utils tests && touch src/index.js README.md",
    explanation="Set up project structure and create initial files",
    isBackground=true
)
```

#### Conditional Command Chains
```
# WRONG - Multiple checks and actions
1. run_in_terminal(command="test -f package.json", isBackground=true)
2. run_in_terminal(command="npm install", isBackground=true)
3. run_in_terminal(command="test -f requirements.txt", isBackground=true)
4. run_in_terminal(command="pip install -r requirements.txt", isBackground=true)

# RIGHT - Conditional execution in one call with background execution
run_in_terminal(
    command="[ -f package.json ] && npm install; [ -f requirements.txt ] && pip install -r requirements.txt",
    explanation="Install dependencies based on available package files",
    isBackground=true
)
```

### EFFICIENT COMMAND STRATEGIES

#### Use Shell Features for Batching
- **Command chaining**: Use `;` to run commands sequentially
- **Conditional execution**: Use `&&` for success-dependent chains
- **Parallel execution**: Use `&` for background processes when appropriate
- **Error handling**: Use `||` for fallback commands

#### Windows PowerShell Specific Patterns
```
# PowerShell command chaining
run_in_terminal: "New-Item -ItemType Directory -Path 'src','tests' -Force; New-Item -ItemType File -Path 'src/index.js','README.md' -Force"

# PowerShell conditional execution
run_in_terminal: "if (Test-Path 'package.json') { npm install }; if (Test-Path 'requirements.txt') { pip install -r requirements.txt }"
```

#### Cross-Platform Command Considerations
- Use appropriate separators for the detected shell (`;` for most shells, `;` for PowerShell)
- Consider path separators and command syntax differences
- Test commands work in the target environment

### PLANNING TERMINAL OPERATIONS

#### Before Running Commands
1. **Analyze all needed operations** for the current task
2. **Group by logical dependencies** (setup → build → test → deploy)
3. **Identify which commands can be chained** vs need separate calls
4. **Consider error handling** and what should happen if a command fails

#### Command Grouping Strategy
1. **Setup/Installation Commands**: Group package installs, environment setup
2. **Build/Compilation Commands**: Chain build steps that depend on each other
3. **Testing Commands**: Combine test runs, linting, validation
4. **Deployment/Publishing**: Group deployment-related operations

#### When to Use Separate Calls
- **Long-running background processes** (servers, watch modes) - use `isBackground=true`
- **All commands** - use `isBackground=true` (NO EXCEPTIONS)
- **Commands with complex output** - use `isBackground=true` and get_terminal_output if needed
- **Error-prone operations** - use `isBackground=true` and handle errors appropriately

#### Background Terminal Usage (MANDATORY)
- **ALWAYS use `isBackground=true`** - NO EXCEPTIONS
- **Never use isBackground=false** - Background terminals handle all scenarios
- **For output analysis**: Use `get_terminal_output()` after background execution
- **For interactive needs**: Design workflows to avoid interactive commands
- **For error checking**: Monitor background execution and handle appropriately

### COMMAND EFFICIENCY BEST PRACTICES

#### Output Management
- **Combine related information gathering**: `ls -la; pwd; git status` instead of three separate calls
- **Use command substitution**: Capture and use output within the same command chain
- **Filter output appropriately**: Use `grep`, `head`, `tail` to limit output size

#### Performance Optimization
- **Minimize context switching**: Fewer tool calls = better performance
- **Use built-in command features**: Leverage shell built-ins for file operations
- **Avoid redundant operations**: Don't repeat directory changes or environment setup

#### Error Handling in Command Chains
```
# Good error handling in command chains
run_in_terminal: "npm install && npm run build && npm test || echo 'Build process failed'"

# Complex error handling with recovery
run_in_terminal: "npm install || (echo 'npm install failed, trying yarn'; yarn install) && npm run build"
```

### VALIDATION AFTER COMMAND EXECUTION
1. **Check command output** for success indicators
2. **Verify expected files/directories** were created
3. **Test that subsequent commands** will work with the changes
4. **Document any complex command chains** for future reference

## INSTRUCTION MAINTENANCE
	- **Always Update Instructions**: When project patterns, architecture, or workflows change, immediately update the relevant instruction files
	- **Document Changes**: Store instruction updates in the memory system with rationale
	- **Verify Examples**: Ensure all code examples in instructions remain accurate and functional
	- **Test Instructions**: Validate that updated instructions are clear and complete

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

## DEPLOYMENT WORKFLOW

### ⚠️ CRITICAL: PRE-DEPLOYMENT COMPLIANCE CHECKLIST
**NEVER skip these steps - they prevent production failures**

1. **Review CHANGELOG.md**: Verify all changes are documented
2. **Quality Checks**: Run static analysis tools - fix all errors
3. **Test Suite**: Run full test suite - **ALL TESTS MUST PASS**
4. **Version Bump**: Update version in package configuration files if needed
5. **Documentation**: Update README.md, docs/, instruction files
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
- ✅ **Tests**: All tests must pass
- ✅ **Code quality**: Static analysis checks
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
gh pr status --repo <owner>/<repo_name>
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
# Add project-specific build and publish commands here
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

### Crisis Recovery
```bash
# Mass fix (emergency only)
git stash push -m "backup before recovery"
# Run appropriate formatters and linters for the language
# Verify fixes before proceeding
```

### Deployment Failure Protocols
- **Immediate**: Stop deployments, assess impact, rollback if needed
- **Analysis**: Root cause analysis, document violation consequences  
- **Prevention**: Update procedures, strengthen protections, team education

## UNIVERSAL QUALITY COMMITMENTS
- **EVERY edit session** starts with validation
- **EVERY commit** blocked if errors exist  
- **EVERY PR** waits for CI/CD + resolves ALL code review feedback
- **ZERO tolerance** for bypassing quality checks

**Remember**: Efficient terminal usage reduces tool calls, improves performance, and makes the development process smoother. Always think about grouping related operations before executing them.