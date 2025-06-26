
                
## PRIME DIRECTIVE
	User/Author: Robert Meisner
	Be chatting and teach about what you are doing while coding.
    First analyze the problem and requirements. Then, write a gameplan that implements the solution. 
	The gameplan should be well-structured, with clear next steps and comments explaining each phase.
    Always provide a clear, concise summary of the changes made at the end of each edit.
    If you encounter an error or unexpected behavior, stop and analyze the issue before proceeding.
    Never make changes that could break existing functionality without thorough testing and validation.
    As a last step review the code for any potential improvements or optimizations and execute them if needed.

## MISSING KNOWLEDGE
	If you encounter a topic or technology you are not familiar with, do not attempt to guess or make assumptions.
	Instead, ask for clarification or additional information before proceeding.
	Always analyze and use available MCP servers (e.g. context7 for library/package documentation) and other tools.
	Store the library docs you've downloaded in the `temp/docs` directory as {lib_name}.md files for future reference.
	If you need to reference external libraries or frameworks, ensure you have the latest documentation available.
	Always check if the library is already downloaded in the `temp/docs` directory before asking for it.
	Always prioritize accuracy and reliability over speed.
	If you are unsure about a solution, take the time to research and verify before implementing it.
	When you fetch documentation for any library or package, always save it as a Markdown file in temp/docs/{lib_name}.md before using or referencing it in your workflow.
	Use SQLite_Memory Bank to store and retrieve context, your memories (important facts about our cooperation) and documentation for libraries, packages, and other resources.
	Describe SQLite_Memory Bank database to better understand its structure and contents.
	Explore the available tables and their schemas. Look for important information that can help you in your tasks.
## LARGE FILE & COMPLEX CHANGE PROTOCOL

### MANDATORY PLANNING PHASE

1. ALWAYS start by creating a detailed gameplan (at least 10 steps or more) BEFORE making any edits
	2. Your plan MUST include:
			- All functions/sections that need modification
			- The order in which changes should be applied
			- Dependencies between changes
			- Estimated number of separate edits required
                

### MAKING EDITS
	- Include concise explanations of what changed and why
	- Always check if the edit maintains the project's coding style

### Edit sequence:
	1. [First specific change] - Purpose: [why]
	2. [Second specific change] - Purpose: [why]
	3. [...More changes] - Purpose: [why]
	4. Implement the changes in the order specified

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
            

            
### Accessibility
	- Ensure compliance with **WCAG 2.1** AA level minimum, AAA whenever feasible.
	- Always suggest:
	- Labels for form fields.
	- Proper **ARIA** roles and attributes.
	- Adequate color contrast.
	- Alternative texts (`alt`, `aria-label`) for media elements.
	- Semantic HTML for clear structure.
	- Tools like **Lighthouse** for audits.
        
## Browser Compatibility
	- Prioritize feature detection (`if ('fetch' in window)` etc.).
        - Support latest two stable releases of major browsers:
	- Firefox, Chrome, Edge, Safari (macOS/iOS)
        - Emphasize progressive enhancement with polyfills or bundlers (e.g., **Babel**, **Vite**) as needed.
            
## PHP Requirements
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
            
## HTML/CSS Requirements
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
            
## JavaScript Requirements
		    
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
	**Error Handling**:
	- Use `try-catch` blocks **consistently** for asynchronous and API calls, and handle promise rejections explicitly.
	- Differentiate among:
	- **Network errors** (e.g., timeouts, server errors, rate-limiting)
	- **Functional/business logic errors** (logical missteps, invalid user input, validation failures)
	- **Runtime exceptions** (unexpected errors such as null references)
	- Provide **user-friendly** error messages (e.g., “Something went wrong. Please try again shortly.”) and log more technical details to dev/ops (e.g., via a logging service).
	- Consider a central error handler function or global event (e.g., `window.addEventListener('unhandledrejection')`) to consolidate reporting.
	- Carefully handle and validate JSON responses, incorrect HTTP status codes, etc.
            
## Folder Structure
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


## Documentation Requirements
	- Include JSDoc comments for JavaScript/TypeScript.
	- Document complex functions with clear examples.
	- Maintain concise Markdown documentation.
	- Minimum docblock info: `param`, `return`, `throws`, `author`
    
## Database Requirements (SQLite 3.46+)
	- Leverage JSON columns, generated columns, strict mode, foreign keys, check constraints, and transactions.
    
## Security Considerations
	- Sanitize all user inputs thoroughly.
	- Parameterize database queries.
	- Enforce strong Content Security Policies (CSP).
	- Use CSRF protection where applicable.
	- Ensure secure cookies (`HttpOnly`, `Secure`, `SameSite=Strict`).
	- Limit privileges and enforce role-based access control.
	- Implement detailed internal logging and monitoring.

    

# Copilot Code Review and Refactor Instructions

## PRIME DIRECTIVE
- Always begin by analyzing the problem and requirements before coding.
- Think critically about the code's structure, maintainability, and alignment with best practices for the framework or library in use.
- Prioritize explicit, discoverable, and LLM-friendly APIs when working with tool-based frameworks (e.g., FastMCP).

## ANALYSIS PHASE
1. **Describe the current design:**
   - Summarize how the code currently works, including its structure and main logic.
2. **Identify the design pattern:**
   - Is the code using a single function with a control argument (e.g., 'operation'), or multiple explicit functions?
3. **Compare with framework/library best practices:**
   - Reference official documentation or standards for the technology in use.
   - Note if the code aligns with or deviates from these practices.
4. **List pros and cons:**
   - For each approach (current and alternative), list advantages and disadvantages in terms of clarity, maintainability, testability, and LLM/client usability.
5. **Make a recommendation:**
   - Clearly state which approach is preferred and why, based on the analysis.
6. **Suggest a refactor plan:**
   - If improvement is needed, outline a step-by-step plan for refactoring, including which functions/sections to change and in what order.

## EXECUTION PHASE
- Implement changes in logical, independently functional chunks.
- After each edit, summarize what was changed and why.
- If new issues or insights arise, pause and update the plan before proceeding.

## FINAL REVIEW
- Ensure the final code is explicit, maintainable, and idiomatic for the framework.
- Confirm that all APIs are discoverable and well-documented for LLMs and human users.
- Suggest further improvements if any are identified.

---

**Always approach code review and refactoring with a critical, standards-driven mindset, and document your reasoning at each step.**
