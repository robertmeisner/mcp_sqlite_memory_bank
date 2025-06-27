---
applyTo: '**'
---

# SQLITE MEMORY BANK USAGE INSTRUCTIONS (Project-Specific)

## PRIME DIRECTIVE
- **ALWAYS SEARCH KNOWLEDGE BASE FIRST**: Before proceeding with any task or answering questions, you MUST search the SQLite_Memory knowledge base for relevant context, previous decisions, project structure, and user preferences.
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
5. **LEVERAGE SEMANTIC SEARCH**: Use semantic search capabilities for intelligent knowledge discovery when exact matches aren't sufficient.

### SCHEMA MAINTENANCE
1. Maintain consistent schemas across sessions.
2. Update existing records rather than creating duplicates.
3. Use appropriate data types for columns.
4. Create relationships between tables when appropriate.
5. Drop tables only when they are no longer needed, and document the reason for deletion.
6. Regularly review and refactor schemas (drop tables and recreate them when you want to change the structure, keep the data migration in mind) to improve clarity and efficiency.

## SEMANTIC SEARCH CAPABILITIES

### OVERVIEW
The SQLite Memory Bank now supports intelligent semantic search using sentence-transformers for natural language queries and content discovery. This enables agents to find conceptually similar content even when exact keyword matches don't exist.

### SEMANTIC SEARCH TOOLS
Available MCP tools for semantic operations:

1. **`add_embeddings`**: Add vector embedding storage to existing tables
2. **`semantic_search`**: Natural language search across content 
3. **`find_related`**: Discover similar content based on input text
4. **`smart_search`**: Hybrid keyword + semantic search
5. **`embedding_stats`**: Monitor embedding coverage and storage

### WHEN TO USE SEMANTIC SEARCH
- **Natural Language Queries**: "Find information about machine learning algorithms"
- **Conceptual Discovery**: Find content about AI when stored text mentions "neural networks"
- **Content Exploration**: Discover related topics and connections
- **Fuzzy Matching**: Find relevant content when exact terms aren't used
- **Knowledge Discovery**: Explore memory bank content without knowing exact keywords

### SEMANTIC SEARCH WORKFLOW

#### 1. Enable Semantic Search on Tables
```python
# Add embedding column to existing table
mcp_sqlite_memory_add_embeddings(
    table_name='project_knowledge',
    text_columns=['content', 'title']  # Columns to create embeddings for
)
```

#### 2. Generate Embeddings for Content
```python
# Generate embeddings for existing data
mcp_sqlite_memory_add_embeddings(
    table_name='project_knowledge', 
    text_columns=['content']
)
# Note: This automatically generates embeddings during the add process
```

#### 3. Perform Semantic Searches
```python
# Natural language search
results = mcp_sqlite_memory_semantic_search(
    query='artificial intelligence and machine learning',
    tables=['project_knowledge', 'technical_decisions'],
    similarity_threshold=0.3,  # Adjust for strictness
    limit=10
)

# Find related content
related = mcp_sqlite_memory_find_related(
    text='neural network optimization techniques',
    table_name='project_knowledge',
    similarity_threshold=0.4,
    limit=5
)

# Hybrid search (combines semantic + keyword)
hybrid_results = mcp_sqlite_memory_smart_search(
    query='database performance optimization',
    tables=['project_knowledge'],
    use_semantic=True,
    use_keywords=True,
    limit=15
)
```

#### 4. Monitor Embedding Coverage
```python
# Check embedding statistics
stats = mcp_sqlite_memory_embedding_stats(
    table_name='project_knowledge'
)
# Returns: total_rows, rows_with_embeddings, embedding_column, embedding_dimension
```

### SEMANTIC SEARCH BEST PRACTICES

#### Threshold Guidelines
- **0.7-1.0**: Very similar content (strict matching)
- **0.5-0.7**: Moderately similar content (recommended for most use cases)
- **0.3-0.5**: Loosely related content (broader exploration)
- **0.1-0.3**: Distantly related content (discovery mode)

#### Performance Considerations
- **Embedding Generation**: Computationally intensive, done once per content update
- **Search Performance**: Fast once embeddings exist (cosine similarity calculation)
- **Storage Overhead**: ~384 floating-point numbers per text field (JSON stored)
- **Batch Processing**: Embeddings generated in batches for efficiency

#### When to Use Each Tool
- **`semantic_search`**: Primary tool for natural language content discovery
- **`find_related`**: When you have specific text and want to find similar content
- **`smart_search`**: When you want both exact keyword matches AND semantic similarity
- **`add_embeddings`**: Setup tool to enable semantic search on tables
- **`embedding_stats`**: Monitoring tool to check semantic search readiness

### INTEGRATION WITH EXISTING WORKFLOWS

#### Enhanced Memory Retrieval
```python
# Traditional exact match
exact_results = mcp_sqlite_memory_read_rows(
    table_name='technical_decisions',
    where={'decision_name': 'API Design'}
)

# Semantic discovery of related content
semantic_results = mcp_sqlite_memory_semantic_search(
    query='API design patterns and architecture decisions',
    tables=['technical_decisions', 'project_structure'],
    similarity_threshold=0.4
)

# Combine both approaches for comprehensive results
all_results = exact_results['rows'] + semantic_results.get('results', [])
```

#### Content Organization and Discovery
```python
# Store content with semantic search enabled
mcp_sqlite_memory_create_row(
    table_name='project_insights',
    data={
        'category': 'performance',
        'insight': 'Database query optimization using proper indexing strategies',
        'details': 'Implemented B-tree indexes on frequently queried columns...'
    }
)

# Enable semantic search for future discovery
mcp_sqlite_memory_add_embeddings(
    table_name='project_insights',
    text_columns=['insight', 'details']
)

# Later: discover related performance insights
related_insights = mcp_sqlite_memory_find_related(
    text='slow database queries and performance issues',
    table_name='project_insights',
    similarity_threshold=0.4
)
```

### FALLBACK BEHAVIOR
- **Dependencies Available**: Full semantic search functionality with sentence-transformers
- **Dependencies Missing**: Graceful fallback to traditional keyword-based search
- **Error Handling**: Clear error messages when semantic features unavailable
- **Backward Compatibility**: All existing functionality remains unchanged

## MEMORY DESIGN PHILOSOPHY

**🧠 Agent-Driven Schema Design**: You should design memory schemas that best fit your specific context, project needs, and working style. The examples below are **suggestions, not requirements**.

**🔄 Adaptive Structure**: Create tables and schemas that evolve with your understanding of the project and user needs.

**🔍 Intelligent Search**: Take advantage of semantic search capabilities for natural language queries and content discovery beyond rigid SQL constraints.

### SCHEMA DESIGN PRINCIPLES
Instead of prescriptive schemas, follow these **flexible principles**:

- **Semantic Organization**: Group related information logically
- **Queryable Structure**: Design for easy retrieval with WHERE clauses  
- **Temporal Tracking**: Include timestamps for chronological context
- **Relationship Awareness**: Consider how different pieces of information connect
- **Evolution-Friendly**: Design schemas that can grow with new insights

### EXAMPLE SCHEMAS (OPTIONAL INSPIRATION)
The following are **example schemas** that have worked well in similar contexts. Feel free to:
- **Adapt** them to your needs
- **Combine** multiple concepts into single tables
- **Split** concepts into multiple specialized tables
- **Create entirely different** structures that better fit your context

**When to Create Custom Tables:**
- Project-specific data that doesn't fit existing patterns
- Complex relationships requiring specialized organization  
- Performance optimization for frequently queried data
- Domain-specific information unique to your context

**When to Create New Tables:**
- Project-specific data that doesn't fit existing schemas
- Complex relationships requiring normalized data structure
- Performance optimization for frequently queried data
- Domain-specific information (e.g., security_incidents, user_sessions, api_endpoints)

**Guidelines for New Tables:**
- Follow the same naming conventions (snake_case)
- Include appropriate primary keys and constraints
- Add timestamp columns for audit trails
- Use descriptive table and column names
- Document the purpose and structure in project_structure table

**Example of Creating Project-Specific Tables:**
```python
# Create a security-specific table for tracking vulnerabilities
mcp_sqlite_memory_create_table(
    table_name='security_vulnerabilities',
    columns=[
        {'name': 'id', 'type': 'INTEGER PRIMARY KEY AUTOINCREMENT'},
        {'name': 'vulnerability_type', 'type': 'TEXT NOT NULL'},
        {'name': 'severity', 'type': 'TEXT NOT NULL'},
        {'name': 'description', 'type': 'TEXT NOT NULL'},
        {'name': 'status', 'type': 'TEXT DEFAULT "open"'},
        {'name': 'discovered_date', 'type': 'TEXT DEFAULT CURRENT_TIMESTAMP'},
        {'name': 'resolved_date', 'type': 'TEXT'}
    ]
)

# Document the new table structure
mcp_sqlite_memory_create_row(
    table_name='project_structure',
    data={
        'category': 'database_schema',
        'title': 'Security Vulnerabilities Table',
        'content': 'Tracks security vulnerabilities with severity levels, status, and resolution dates for the security startup project'
    }
)
```

**Remember:** The memory system should evolve with your project needs. Don't hesitate to create specialized tables for better organization and query performance.

### Example 1: Project Knowledge Schema (OPTIONAL)
*Use this pattern if you need to track project structure and technical decisions*

```sql
-- Example project_knowledge table
CREATE TABLE project_knowledge (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    knowledge_type TEXT NOT NULL,    -- 'architecture', 'decision', 'pattern', 'preference'
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    context TEXT,                    -- Additional context or relationships
    confidence REAL DEFAULT 1.0,    -- How confident are you in this information?
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### Example 2: Conversation Memory Schema (OPTIONAL)  
*Use this pattern if you need to track conversation context and progress*

```sql
-- Example conversation_memory table
CREATE TABLE conversation_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    topic TEXT NOT NULL,
    key_information TEXT NOT NULL,
    action_items TEXT,
    references TEXT,                 -- Links to other memories or external resources
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### Example 3: Specialized Domain Schema (OPTIONAL)
*Adapt this pattern for domain-specific needs (security, API design, etc.)*

```sql  
-- Example domain_insights table (customize for your domain)
CREATE TABLE domain_insights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    domain TEXT NOT NULL,            -- 'security', 'performance', 'ux', 'api'
    insight_type TEXT NOT NULL,      -- 'pattern', 'anti-pattern', 'best-practice', 'warning'
    description TEXT NOT NULL,
    examples TEXT,
    related_tools TEXT,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### Example 4: Simple Unified Schema (OPTIONAL)
*Use this if you prefer a single, flexible table*

```sql
-- Example unified_memory table
CREATE TABLE unified_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,          -- Your own categorization system
    subcategory TEXT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    tags TEXT,                       -- JSON or comma-separated tags
    metadata TEXT,                   -- JSON for flexible additional data
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
);
```

## USAGE EXAMPLES

### Flexible Implementation Examples

**Example 1: Using Project Knowledge Schema**
```python
# Store a technical insight
mcp_sqlite_memory_create_row(
    table_name='project_knowledge',
    data={
        'knowledge_type': 'decision',
        'title': 'Memory Schema Approach',
        'content': 'Decided to use example-based guidance rather than prescriptive schemas to allow agent flexibility',
        'context': 'User feedback about rigid schema requirements',
        'confidence': 0.9
    }
)

# Query by knowledge type
decisions = mcp_sqlite_memory_read_rows(
    table_name='project_knowledge',
    where={'knowledge_type': 'decision'}
)
```

**Example 2: Creating Your Own Schema**
```python
# Create a completely custom schema for your specific needs
mcp_sqlite_memory_create_table(
    table_name='code_patterns',
    columns=[
        {'name': 'id', 'type': 'INTEGER PRIMARY KEY AUTOINCREMENT'},
        {'name': 'pattern_name', 'type': 'TEXT NOT NULL'},
        {'name': 'language', 'type': 'TEXT NOT NULL'},
        {'name': 'code_example', 'type': 'TEXT NOT NULL'},
        {'name': 'use_cases', 'type': 'TEXT'},
        {'name': 'anti_patterns', 'type': 'TEXT'},
        {'name': 'timestamp', 'type': 'TEXT DEFAULT CURRENT_TIMESTAMP'}
    ]
)
```

**Example 3: Minimal Approach**
```python
# Sometimes a simple notes table is all you need
mcp_sqlite_memory_create_table(
    table_name='notes',
    columns=[
        {'name': 'id', 'type': 'INTEGER PRIMARY KEY AUTOINCREMENT'},
        {'name': 'note', 'type': 'TEXT NOT NULL'},
        {'name': 'tags', 'type': 'TEXT'},
        {'name': 'timestamp', 'type': 'TEXT DEFAULT CURRENT_TIMESTAMP'}
    ]
)
```

## BEST PRACTICES FOR EFFECTIVE MEMORY USAGE

### TRADITIONAL SQL QUERIES
1. Use specific queries to retrieve only relevant information:
```python
# Good - specific query
mcp_sqlite_memory_read_rows(
    table_name='project_structure',
    where={'category': 'file_organization'}
)

# Bad - retrieving everything
mcp_sqlite_memory_read_rows(
    table_name='project_structure',
    where={}
)
```

### SEMANTIC SEARCH QUERIES
1. Use natural language for content discovery:
```python
# Find conceptually related content
semantic_results = mcp_sqlite_memory_semantic_search(
    query='machine learning algorithms and AI techniques',
    tables=['project_knowledge', 'technical_decisions'],
    similarity_threshold=0.4,
    limit=10
)

# Discover related content from specific text
related_content = mcp_sqlite_memory_find_related(
    text='database performance optimization strategies',
    table_name='project_insights',
    similarity_threshold=0.5
)
```

### HYBRID APPROACHES
1. Combine exact matching with semantic discovery:
```python
# Get specific technical decisions
exact_decisions = mcp_sqlite_memory_read_rows(
    table_name='technical_decisions',
    where={'decision_name': 'API Design'}
)

# Find related architectural decisions
related_decisions = mcp_sqlite_memory_semantic_search(
    query='API design patterns and microservice architecture',
    tables=['technical_decisions', 'project_structure'],
    similarity_threshold=0.4
)

# Combine for comprehensive context
all_relevant_info = {
    'exact_matches': exact_decisions['rows'],
    'related_content': related_decisions.get('results', [])
}
```

2. Join information from multiple tables when necessary:
```python
# Get technical decisions and related project structure
decisions = mcp_sqlite_memory_read_rows(
    table_name='technical_decisions',
    where={'decision_name': 'API Design'}
)

structure = mcp_sqlite_memory_read_rows(
    table_name='project_structure',
    where={'category': 'architecture'}
)
```

### ENABLING SEMANTIC SEARCH ON EXISTING TABLES
1. Add semantic capabilities to existing data:
```python
# Enable semantic search on key tables
mcp_sqlite_memory_add_embeddings(
    table_name='project_knowledge',
    text_columns=['title', 'content']
)

mcp_sqlite_memory_add_embeddings(
    table_name='technical_decisions', 
    text_columns=['chosen_approach', 'rationale']
)

# Check embedding coverage
stats = mcp_sqlite_memory_embedding_stats(
    table_name='project_knowledge'
)
print(f"Embedded {stats['rows_with_embeddings']}/{stats['total_rows']} rows")
```

### Data Maintenance
1. Update existing records instead of creating duplicates:
```python
# Check if record exists
existing = mcp_sqlite_memory_read_rows(
    table_name='user_preferences',
    where={'preference_type': 'code_style'}
)

if existing['rows']:
    # Update existing record
    mcp_sqlite_memory_update_rows(
        table_name='user_preferences',
        data={'preference_value': 'explicit type annotations'},
        where={'id': existing['rows'][0]['id']}
    )
else:
    # Create new record
    mcp_sqlite_memory_create_row(
        table_name='user_preferences',
        data={
            'preference_type': 'code_style',
            'preference_value': 'explicit type annotations'
        }
    )
```

2. Verify data was stored correctly:
```python
# Store data
result = mcp_sqlite_memory_create_row(
    table_name='technical_decisions',
    data={'decision_name': 'Database Schema'}
)

# Verify storage
verification = mcp_sqlite_memory_read_rows(
    table_name='technical_decisions',
    where={'decision_name': 'Database Schema'}
)

if not verification['rows']:
    # Handle error - data not stored correctly
    print("Error: Data storage failed")
```

### Working with Semantic Search
1. Enable semantic search for intelligent discovery:
```python
# Store content and enable semantic search
mcp_sqlite_memory_create_row(
    table_name='project_insights',
    data={
        'category': 'performance',
        'insight': 'Database optimization techniques using indexing',
        'details': 'Implemented proper B-tree indexes for query performance...'
    }
)

# Enable semantic search on the table
mcp_sqlite_memory_add_embeddings(
    table_name='project_insights',
    text_columns=['insight', 'details']
)

# Later: find related content semantically
related = mcp_sqlite_memory_semantic_search(
    query='improving database speed and performance',
    tables=['project_insights'],
    similarity_threshold=0.4
)
```

### Working with Large Context
1. Split large documentation into logical chunks:
```python
# Store large documentation in manageable chunks
mcp_sqlite_memory_create_row(
    table_name='documentation',
    data={
        'library_name': 'fastapi',
        'topic': 'routing_part1',
        'content': '...'
    }
)

mcp_sqlite_memory_create_row(
    table_name='documentation',
    data={
        'library_name': 'fastapi',
        'topic': 'routing_part2',
        'content': '...'
    }
)
```

2. Use relationships between records:
```python
# Store parent record
parent_result = mcp_sqlite_memory_create_row(
    table_name='project_structure',
    data={
        'category': 'architecture',
        'title': 'Overall Architecture',
        'content': '...'
    }
)

# Store related child record with parent reference
mcp_sqlite_memory_create_row(
    table_name='project_structure',
    data={
        'category': 'architecture_component',
        'title': 'Database Layer',
        'content': '...',
        'parent_id': parent_result['id']
    }
)
```

By following these instructions and examples, you will maintain an effective, structured memory system across our interactions, enabling more contextual and helpful assistance over time.