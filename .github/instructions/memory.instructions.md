---
applyTo: '**'
---

# SQLITE MEMORY BANK USAGE INSTRUCTIONS (Project-Specific)

## PRIME DIRECTIVE
- You MUST use the SQLite_Memory bank to store all important contextual information learned during our conversations.
- You MUST retrieve relevant context from SQLite_Memory at the start of each new interaction.
- Always design schemas that are explicit, discoverable, and LLM-friendly.
- ALWAYS verify data storage and handle errors gracefully.
- Use MCP tools consistently for all memory operations.

## MEMORY MANAGEMENT PROTOCOL

### SETUP & INITIALIZATION
1. Check if required tables exist at the beginning of each session.
2. Create missing tables with appropriate schemas before storing data.
3. When creating tables, follow these naming conventions:
   - Use snake_case for table and column names
   - Use descriptive, semantic names
   - Include appropriate primary keys and constraints

### STORAGE & RETRIEVAL
1. Store information immediately after learning it.
2. Categorize information appropriately in the correct tables.
3. Before answering questions, query relevant tables for context.
4. Use specific WHERE clauses to retrieve only relevant information.

### SCHEMA MAINTENANCE
1. Maintain consistent schemas across sessions.
2. Update existing records rather than creating duplicates.
3. Use appropriate data types for columns.
4. Create relationships between tables when appropriate.

## MEMORY SCHEMAS & CATEGORIES

The following table schemas should be created and maintained:

### 1. Project Structure Table
```sql
CREATE TABLE project_structure (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,      -- e.g., 'architecture', 'file_organization', 'module_relationships'
    title TEXT NOT NULL,         -- Brief title of the structure element
    content TEXT NOT NULL,       -- Detailed description
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
);
```

**Example Usage:**
```python
# Storing project structure information
create_row('project_structure', {
    'category': 'file_organization',
    'title': 'Core module structure',
    'content': 'The project follows a modular design with server.py containing the FastMCP implementation, types.py defining data structures, and utils.py providing helper functions.'
})

# Retrieving project structure information
architecture_info = read_rows('project_structure', {'category': 'architecture'})
```

### 2. Technical Decisions Table
```sql
CREATE TABLE technical_decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    decision_name TEXT NOT NULL,
    chosen_approach TEXT NOT NULL,
    alternatives TEXT,
    rationale TEXT NOT NULL,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
);
```

**Example Usage:**
```python
# Storing a technical decision
create_row('technical_decisions', {
    'decision_name': 'API Design Pattern',
    'chosen_approach': 'Explicit function-based tools',
    'alternatives': 'Single multiplex function with operation parameter',
    'rationale': 'Explicit function-based tools provide better discoverability for LLMs and clients, with clearer type hints and validation.'
})

# Retrieving technical decisions
api_decisions = read_rows('technical_decisions', {'decision_name': 'API Design Pattern'})
```

### 3. User Preferences Table
```sql
CREATE TABLE user_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    preference_type TEXT NOT NULL,
    preference_value TEXT NOT NULL,
    context TEXT,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
);
```

**Example Usage:**
```python
# Storing user preferences
create_row('user_preferences', {
    'preference_type': 'code_style',
    'preference_value': 'explicit type annotations',
    'context': 'User prefers explicit type annotations for all functions and variables'
})

# Retrieving user preferences
coding_preferences = read_rows('user_preferences', {'preference_type': 'code_style'})
```

### 4. Session Context Table
```sql
CREATE TABLE session_context (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    topic TEXT NOT NULL,
    progress_state TEXT NOT NULL,
    next_steps TEXT,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
);
```

**Example Usage:**
```python
# Storing session context
create_row('session_context', {
    'session_id': '2025-06-26-1',
    'topic': 'Refactoring API design',
    'progress_state': 'analyzing_current_implementation',
    'next_steps': 'Identify inconsistencies in current API design'
})

# Retrieving session context
current_session = read_rows('session_context', {'session_id': '2025-06-26-1'})
```

### 5. Documentation Table
```sql
CREATE TABLE documentation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    library_name TEXT NOT NULL,
    topic TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
);
```

**Example Usage:**
```python
# Storing documentation
create_row('documentation', {
    'library_name': 'fastmcp',
    'topic': 'tool_registration',
    'content': 'FastMCP tools are registered using the @mcp.tool decorator...'
})

# Retrieving documentation
fastmcp_docs = read_rows('documentation', {'library_name': 'fastmcp'})
```

## BEST PRACTICES FOR EFFECTIVE MEMORY USAGE

### Querying Strategies
1. Use specific queries to retrieve only relevant information:
```python
# Good - specific query
project_files = read_rows('project_structure', {'category': 'file_organization'})

# Bad - retrieving everything
all_project_info = read_rows('project_structure', {})
```

2. Join information from multiple tables when necessary:
```python
# Get technical decisions and related project structure
decisions = read_rows('technical_decisions', {'decision_name': 'API Design'})
related_structure = read_rows('project_structure', {'category': 'architecture'})
```

### Data Maintenance
1. Update existing records instead of creating duplicates:
```python
# Check if record exists
existing = read_rows('user_preferences', {'preference_type': 'code_style'})
if existing:
    # Update existing record
    update_rows('user_preferences', 
                {'preference_value': 'explicit type annotations'}, 
                {'id': existing[0]['id']})
else:
    # Create new record
    create_row('user_preferences', {
        'preference_type': 'code_style',
        'preference_value': 'explicit type annotations'
    })
```

2. Verify data was stored correctly:
```python
# Store data
create_row('technical_decisions', {'decision_name': 'Database Schema'})

# Verify storage
verification = read_rows('technical_decisions', {'decision_name': 'Database Schema'})
if not verification:
    # Handle error - data not stored correctly
    pass
```

### Working with Large Context
1. Split large documentation into logical chunks:
```python
# Store large documentation in manageable chunks
create_row('documentation', {
    'library_name': 'fastapi',
    'topic': 'routing_part1',
    'content': '...'
})
create_row('documentation', {
    'library_name': 'fastapi',
    'topic': 'routing_part2',
    'content': '...'
})
```

2. Use relationships between records:
```python
# Store parent record
parent_id = create_row('project_structure', {
    'category': 'architecture',
    'title': 'Overall Architecture',
    'content': '...'
})['id']

# Store related child records
create_row('project_structure', {
    'category': 'architecture_component',
    'title': 'Database Layer',
    'content': '...',
    'parent_id': parent_id
})
```

By following these instructions and examples, you will maintain an effective, structured memory system across our interactions, enabling more contextual and helpful assistance over time.