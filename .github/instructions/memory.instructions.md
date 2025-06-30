---
applyTo: '**'
---

# MEMORY MANAGEMENT INSTRUCTIONS (General Guidelines)

## PRIME DIRECTIVE FOR MEMORY USAGE
- **ALWAYS SEARCH KNOWLEDGE BASE FIRST**: Before proceeding with any task or answering questions, you MUST search available memory banks for relevant context, previous decisions, project structure, and user preferences.
- You MUST use available memory systems to store all important contextual information learned during conversations.
- You MUST retrieve relevant context from memory systems at the start of each new interaction.
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
6. Regularly review and refactor schemas to improve clarity and efficiency.

## SEMANTIC SEARCH CAPABILITIES (IF AVAILABLE)

### OVERVIEW
Many memory systems support intelligent semantic search using sentence-transformers for natural language queries and content discovery. This enables agents to find conceptually similar content even when exact keyword matches don't exist.

### SEMANTIC SEARCH TOOLS (WHEN AVAILABLE)
Common MCP tools for semantic operations:

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

### SEMANTIC SEARCH BEST PRACTICES

#### Threshold Guidelines (when available)
- **0.7-1.0**: Very similar content (strict matching)
- **0.5-0.7**: Moderately similar content (recommended for most use cases)
- **0.3-0.5**: Loosely related content (broader exploration)
- **0.1-0.3**: Distantly related content (discovery mode)

#### Performance Considerations
- **Embedding Generation**: Computationally intensive, done once per content update
- **Search Performance**: Fast once embeddings exist (cosine similarity calculation)
- **Storage Overhead**: Additional storage for vector embeddings
- **Batch Processing**: Embeddings generated in batches for efficiency

#### When to Use Each Tool (if available)
- **`semantic_search`**: Primary tool for natural language content discovery
- **`find_related`**: When you have specific text and want to find similar content
- **`smart_search`**: When you want both exact keyword matches AND semantic similarity
- **`add_embeddings`**: Setup tool to enable semantic search on tables
- **`embedding_stats`**: Monitoring tool to check semantic search readiness

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

### COMMON SCHEMA PATTERNS (OPTIONAL INSPIRATION)
The following are **example schemas** that have worked well in various contexts. Feel free to:
- **Adapt** them to your needs
- **Combine** multiple concepts into single tables
- **Split** concepts into multiple specialized tables
- **Create entirely different** structures that better fit your context

#### Pattern 1: Project Knowledge Schema (OPTIONAL)
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

#### Pattern 2: Conversation Memory Schema (OPTIONAL)  
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

#### Pattern 3: Domain-Specific Schema (OPTIONAL)
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

#### Pattern 4: Simple Unified Schema (OPTIONAL)
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

## BEST PRACTICES FOR EFFECTIVE MEMORY USAGE

### TRADITIONAL SQL QUERIES
1. Use specific queries to retrieve only relevant information:
```python
# Good - specific query
memory_read_rows(
    table_name='project_structure',
    where={'category': 'file_organization'}
)

# Bad - retrieving everything
memory_read_rows(
    table_name='project_structure',
    where={}
)
```

### SEMANTIC SEARCH QUERIES (IF AVAILABLE)
1. Use natural language for content discovery:
```python
# Find conceptually related content
semantic_results = memory_semantic_search(
    query='machine learning algorithms and AI techniques',
    tables=['project_knowledge', 'technical_decisions'],
    similarity_threshold=0.4,
    limit=10
)

# Discover related content from specific text
related_content = memory_find_related(
    text='database performance optimization strategies',
    table_name='project_insights',
    similarity_threshold=0.5
)
```

### HYBRID APPROACHES
1. Combine exact matching with semantic discovery:
```python
# Get specific technical decisions
exact_decisions = memory_read_rows(
    table_name='technical_decisions',
    where={'decision_name': 'API Design'}
)

# Find related architectural decisions (if semantic search available)
related_decisions = memory_semantic_search(
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

### ENABLING SEMANTIC SEARCH ON EXISTING TABLES (IF AVAILABLE)
1. Add semantic capabilities to existing data:
```python
# Enable semantic search on key tables (if supported)
memory_add_embeddings(
    table_name='project_knowledge',
    text_columns=['title', 'content']
)

memory_add_embeddings(
    table_name='technical_decisions', 
    text_columns=['chosen_approach', 'rationale']
)

# Check embedding coverage
stats = memory_embedding_stats(
    table_name='project_knowledge'
)
print(f"Embedded {stats['rows_with_embeddings']}/{stats['total_rows']} rows")
```

### DATA MAINTENANCE
1. Update existing records instead of creating duplicates:
```python
# Check if record exists
existing = memory_read_rows(
    table_name='user_preferences',
    where={'preference_type': 'code_style'}
)

if existing['rows']:
    # Update existing record
    memory_update_rows(
        table_name='user_preferences',
        data={'preference_value': 'explicit type annotations'},
        where={'id': existing['rows'][0]['id']}
    )
else:
    # Create new record
    memory_create_row(
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
result = memory_create_row(
    table_name='technical_decisions',
    data={'decision_name': 'Database Schema'}
)

# Verify storage
verification = memory_read_rows(
    table_name='technical_decisions',
    where={'decision_name': 'Database Schema'}
)

if not verification['rows']:
    # Handle error - data not stored correctly
    print("Error: Data storage failed")
```

### WORKING WITH SEMANTIC SEARCH (IF AVAILABLE)
1. Enable semantic search for intelligent discovery:
```python
# Store content and enable semantic search
memory_create_row(
    table_name='project_insights',
    data={
        'category': 'performance',
        'insight': 'Database optimization techniques using indexing',
        'details': 'Implemented proper B-tree indexes for query performance...'
    }
)

# Enable semantic search on the table (if supported)
memory_add_embeddings(
    table_name='project_insights',
    text_columns=['insight', 'details']
)

# Later: find related content semantically
related = memory_semantic_search(
    query='improving database speed and performance',
    tables=['project_insights'],
    similarity_threshold=0.4
)
```

### WORKING WITH LARGE CONTEXT
1. Split large documentation into logical chunks:
```python
# Store large documentation in manageable chunks
memory_create_row(
    table_name='documentation',
    data={
        'library_name': 'framework_name',
        'topic': 'routing_part1',
        'content': '...'
    }
)

memory_create_row(
    table_name='documentation',
    data={
        'library_name': 'framework_name',
        'topic': 'routing_part2',
        'content': '...'
    }
)
```

2. Use relationships between records:
```python
# Store parent record
parent_result = memory_create_row(
    table_name='project_structure',
    data={
        'category': 'architecture',
        'title': 'Overall Architecture',
        'content': '...'
    }
)

# Store related child record with parent reference
memory_create_row(
    table_name='project_structure',
    data={
        'category': 'architecture_component',
        'title': 'Database Layer',
        'content': '...',
        'parent_id': parent_result['id']
    }
)
```

## MEMORY SYSTEM ADAPTABILITY

### WHEN TO CREATE CUSTOM TABLES
- Project-specific data that doesn't fit existing patterns
- Complex relationships requiring specialized organization  
- Performance optimization for frequently queried data
- Domain-specific information unique to your context

### GUIDELINES FOR NEW TABLES
- Follow the same naming conventions (snake_case)
- Include appropriate primary keys and constraints
- Add timestamp columns for audit trails
- Use descriptive table and column names
- Document the purpose and structure

### FALLBACK BEHAVIOR
- **Dependencies Available**: Full semantic search functionality (if supported)
- **Dependencies Missing**: Graceful fallback to traditional keyword-based search
- **Error Handling**: Clear error messages when features unavailable
- **Backward Compatibility**: All existing functionality remains unchanged

By following these instructions and examples, you will maintain an effective, structured memory system across interactions, enabling more contextual and helpful assistance over time.
