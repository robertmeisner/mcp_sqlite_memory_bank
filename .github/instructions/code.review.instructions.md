---
applyTo: '**'
---
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
