# SQLite Memory Bank Search Enhancement Roadmap

## 🎯 **Vision: From Rigid to Flexible Search**

Transform the SQLite Memory Bank from a rigid, column-based query system into a flexible, intelligent search platform that supports natural language discovery and semantic understanding.

## 📊 **Current State Analysis**

### ❌ **Current Limitations**
- **Rigid WHERE clauses** - Only exact matches on specific columns
- **No content search** - Can't search within text fields  
- **No semantic understanding** - Can't find related concepts
- **Poor discoverability** - Hard to explore what's available
- **Column-dependent** - Must know exact column names and values

### ✅ **Current Strengths**
- **Type safety** - All operations are validated
- **SQL performance** - Fast structured queries
- **Data integrity** - Consistent schema validation
- **Agent-friendly** - Explicit, discoverable APIs

## 🚀 **Enhancement Phases**

### **Phase 1: Full-Text Search (IMPLEMENTED)**
- ✅ `search_content()` - Natural language search across all text columns
- ✅ `explore_tables()` - Content discovery and data exploration
- ✅ Relevance scoring and ranking
- ✅ Multi-table search with result aggregation

**Capabilities Added:**
```python
# Natural language search
search_content("API design patterns")
search_content("user authentication security")
search_content("database schema decisions")

# Content exploration
explore_tables()  # See what data is available
explore_tables("user%")  # Explore user-related tables
```

### **Phase 2: SQLite FTS Integration (PLANNED)**
**Objective:** Add proper full-text search with indexing

**Implementation:**
- Create FTS5 virtual tables for text content
- Automatic indexing of text columns
- Advanced search operators (AND, OR, NOT, phrases)
- Highlighting and snippets

**New Tools:**
```python
@mcp.tool
def create_fts_index(table_name: str, text_columns: List[str]) -> ToolResponse:
    """Create FTS5 index for fast full-text search."""
    
@mcp.tool  
def fts_search(query: str, **options) -> ToolResponse:
    """Advanced full-text search with FTS5."""
```

### **Phase 3: Vector Embeddings & Semantic Search (PLANNED)**
**Objective:** Add semantic understanding and similarity search

**Implementation Options:**

#### Option A: SQLite-vec Extension
```python
# Use SQLite-vec for native vector storage
@mcp.tool
def add_embeddings(table_name: str, text_column: str, model: str = "all-MiniLM-L6-v2") -> ToolResponse:
    """Generate and store embeddings for text content."""

@mcp.tool
def semantic_search(query: str, similarity_threshold: float = 0.7) -> ToolResponse:
    """Find semantically similar content using vector similarity."""
```

#### Option B: External Vector Database Integration
```python
# Integration with Chroma/Pinecone/Weaviate
@mcp.tool
def sync_to_vector_db(table_name: str) -> ToolResponse:
    """Sync table content to external vector database."""

@mcp.tool
def hybrid_search(query: str, use_vector: bool = True, use_text: bool = True) -> ToolResponse:
    """Combine SQL, FTS, and vector search."""
```

### **Phase 4: Intelligent Query Understanding (PLANNED)**
**Objective:** Natural language to SQL translation

**Features:**
- Intent recognition (search vs. query vs. aggregation)
- Automatic column mapping ("find users" → search user tables)
- Query expansion (search related terms)
- Smart filtering suggestions

**Example:**
```python
@mcp.tool
def smart_query(natural_query: str) -> ToolResponse:
    """
    Process natural language queries intelligently.
    
    Examples:
    - "Find all decisions about API design"
    - "Show me recent user preferences" 
    - "What technical choices were made last week?"
    """
```

## 🛠 **Technical Implementation Details**

### **Vector Search Architecture**
```python
# Proposed vector-enhanced schema
class VectorTable:
    def __init__(self, base_table: str):
        self.base_table = base_table
        self.vector_table = f"{base_table}_vectors"
        self.embedding_model = "all-MiniLM-L6-v2"
    
    def add_embeddings(self, text_column: str):
        """Add vector embeddings for semantic search."""
        
    def semantic_search(self, query: str, top_k: int = 10):
        """Find similar content using cosine similarity."""
```

### **Hybrid Search Strategy**
```python
def unified_search(query: str, search_types: List[str] = ["exact", "text", "semantic"]):
    """
    Combine multiple search approaches:
    1. Exact SQL matches (current)
    2. Full-text search (Phase 1)
    3. Semantic similarity (Phase 3)
    4. Aggregate and rank results
    """
    results = []
    
    if "exact" in search_types:
        results.extend(exact_sql_search(query))
    
    if "text" in search_types:
        results.extend(full_text_search(query))
        
    if "semantic" in search_types:
        results.extend(vector_search(query))
    
    return rank_and_merge_results(results)
```

## 📈 **Success Metrics**

### **Search Quality**
- **Recall**: % of relevant results found
- **Precision**: % of results that are relevant  
- **User satisfaction**: Ease of finding information

### **Performance**
- **Search latency**: < 100ms for most queries
- **Index size**: Manageable storage overhead
- **Memory usage**: Efficient for large datasets

### **Usability** 
- **Natural language support**: Agents can search conversationally
- **Discovery**: Easy to explore unknown data
- **Flexibility**: Works across different schema designs

## 🎯 **Use Case Examples**

### **Before (Current State)**
```python
# Rigid, requires exact knowledge
read_rows('technical_decisions', {'decision_name': 'API Design Pattern'})
read_rows('project_structure', {'category': 'architecture'})
```

### **After (Enhanced Search)**
```python
# Natural, flexible discovery
search_content("API design patterns and architecture decisions")
semantic_search("How should I structure my API?")
smart_query("What decisions were made about user authentication?")
```

## 🔄 **Migration Strategy**

1. **Backward Compatibility**: All existing tools remain unchanged
2. **Gradual Enhancement**: New search tools complement existing ones
3. **Optional Features**: Vector search can be enabled per-table
4. **Performance Monitoring**: Track impact on existing operations

## 🚦 **Implementation Priority**

1. **Phase 1**: ✅ COMPLETED - Basic full-text search
2. **Phase 2**: 🟨 HIGH - SQLite FTS integration  
3. **Phase 3**: 🟨 MEDIUM - Vector embeddings
4. **Phase 4**: 🟩 LOW - Advanced NLP features

## 💡 **Benefits for Agents/LLMs**

### **Enhanced Discoverability**
- Agents can explore unknown datasets naturally
- No need to know exact column names or values
- Content-driven rather than schema-driven discovery

### **Semantic Understanding**
- Find related concepts even with different terminology
- Cross-reference information across tables
- Understand context and relationships

### **Flexible Query Patterns**
- Support for various search strategies
- Adaptive to different data organization styles
- Works with both structured and unstructured content

---

**Next Steps:** Implement Phase 2 (SQLite FTS) for production-ready full-text search capabilities.
