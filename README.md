# mcp_sqlite_memory_bank

![PyPI](https://img.shields.io/pypi/v/mcp_sqlite_memory_bank)
![CI](https://github.com/robertmeisner/mcp_sqlite_memory_bank/actions/workflows/ci.yml/badge.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

## Overview

**mcp_sqlite_memory_bank** is a dynamic, agent- and LLM-friendly SQLite memory bank designed for Model Context Protocol (MCP) servers and modern AI agent platforms.

This project provides a robust, discoverable API for creating, exploring, and managing SQLite tables and knowledge graphs. It enables Claude, Anthropic, Github Copilot, Claude Desktop, VS Code, Cursor, and other LLM-powered tools to interact with structured data in a safe, explicit, and extensible way.

**Key Use Cases:**
- Build and query knowledge graphs for semantic search and reasoning
- Store, retrieve, and organize notes or structured data for LLM agents
- Enable natural language workflows for database management and exploration
- Intelligent content discovery with semantic search capabilities
- Access memory content through standardized MCP Resources and Prompts
- Integrate with FastMCP, Claude Desktop, and other agent platforms for seamless tool discovery

**Why mcp_sqlite_memory_bank?**
- **Full MCP Compliance:** Resources, Prompts, and 20+ organized tools
- **Semantic Search:** Natural language content discovery with AI-powered similarity matching
- **Explicit, discoverable APIs** for LLMs and agents with enhanced categorization
- Safe, parameterized queries and schema management
- Designed for extensibility and open source collaboration

---

## Quick Start

Get started with SQLite Memory Bank in your IDE in under 2 minutes:

### 1. Install and Run
```bash
# Install uvx if you don't have it
pip install uvx

# Run SQLite Memory Bank
uvx mcp-sqlite-memory-bank
```

### 2. Configure Your IDE

**VS Code / Cursor:** Add to `.vscode/mcp.json`:
```jsonc
{
  "servers": {
    "SQLite_Memory": {
      "type": "stdio",
      "command": "uvx",
      "args": ["--refresh", "mcp-sqlite-memory-bank"],
      "env": {
        "DB_PATH": "${workspaceFolder}/.vscode/project_memory.sqlite"
      }
    }
  }
}
```

**Claude Desktop:** Add to `claude_desktop_config.json`:
```jsonc
{
  "mcpServers": {
    "sqlite_memory": {
      "command": "uvx",
      "args": ["mcp-sqlite-memory-bank"],
      "env": {
        "DB_PATH": "/path/to/your/memory.db"
      }
    }
  }
}
```

### 3. Test It
Restart your IDE and try asking your AI assistant:
> "Create a table called 'notes' with columns 'id' (integer, primary key) and 'content' (text). Then add a note saying 'Hello SQLite Memory Bank!'"

✅ You should see the AI using the SQLite Memory Bank tools to create the table and add the note!

---

## Features

- **Dynamic Table Management:** Create, list, describe, rename, and drop tables at runtime
- **Advanced CRUD Operations:** Insert, read, update, delete with intelligent batch processing and change tracking
- **Safe SQL:** Run parameterized SELECT queries with comprehensive input validation
- **Semantic Search Engine:** Natural language search using sentence-transformers for intelligent content discovery
- **Zero-Setup Search:** Auto-embedding generation with `auto_semantic_search` and `auto_smart_search`
- **Batch Operations Suite:** Efficient bulk create, update, and delete operations with partial success handling
- **Advanced Optimization:** Duplicate detection, memory bank optimization, and intelligent archiving
- **LLM-Assisted Analysis:** AI-powered duplicate detection, optimization strategies, and archiving policies
- **Discovery & Intelligence:** AI-guided exploration, relationship discovery, and pre-built workflow templates
- **3D Visualization:** Stunning Three.js/WebGL knowledge graphs with real-time lighting and VR support
- **Interactive Dashboards:** Professional D3.js visualizations with enterprise-grade features
- **MCP Resources:** Access memory content through standardized MCP resource URIs
- **MCP Prompts:** Built-in intelligent prompts for common memory analysis workflows
- **Tool Categorization:** Organized tool discovery with detailed usage examples for enhanced LLM integration
- **Knowledge Graph Tools:** Built-in support for node/edge schemas and immersive 3D property graphs
- **Agent/LLM Integration:** Explicit, tool-based APIs for easy discovery and automation
- **Enterprise Scale:** Production-ready with comprehensive optimization and analytics capabilities
- **Open Source:** MIT licensed, fully tested, and ready for community use

---

## MCP Compliance & Enhanced Integration

SQLite Memory Bank v1.6.4+ provides full Model Context Protocol (MCP) compliance with advanced features for enhanced LLM and agent integration:

### 🔧 MCP Tools (30+ Available)
Organized into logical categories for easy discovery:
- **Schema Management** (6 tools): Table creation, modification, and inspection
- **Data Operations** (11 tools): CRUD operations with validation and advanced batch processing
- **Search & Discovery** (6 tools): Content search, exploration, and intelligent discovery
- **Semantic Search** (5 tools): AI-powered natural language content discovery
- **Optimization & Analytics** (8 tools): Memory bank optimization, duplicate detection, and insights
- **Visualization & Knowledge Graphs** (4 tools): Interactive visualizations and 3D knowledge graphs

### 📄 MCP Resources (5 Available)
Real-time access to memory content via standardized URIs:
- `memory://tables/list` - List of all available tables
- `memory://tables/{table_name}/schema` - Table schema information
- `memory://tables/{table_name}/data` - Table data content
- `memory://search/{query}` - Search results as resources
- `memory://analytics/overview` - Memory bank overview analytics

### 💡 MCP Prompts (4 Available)
Intelligent prompts for common memory analysis workflows:
- `analyze-memory-content` - Analyze memory bank content and provide insights
- `search-and-summarize` - Search and create summary prompts
- `technical-decision-analysis` - Analyze technical decisions from memory
- `memory-bank-context` - Provide memory bank context for AI conversations

### 🎯 Enhanced Discoverability
- **Tool Categorization:** `list_tool_categories()` for organized tool discovery
- **Usage Examples:** `get_tools_by_category()` with detailed examples for each tool
- **Semantic Search:** Natural language queries for intelligent content discovery
- **LLM-Friendly APIs:** Explicit, descriptive tool names and comprehensive documentation

---


## Tools & API Reference

All tools are designed for explicit, discoverable use by LLMs, agents, and developers. Each function is available as a direct Python import and as an MCP tool.

**🔍 Tool Discovery:** Use `list_tool_categories()` to see all organized tool categories, or `get_tools_by_category(category)` for detailed information about specific tool groups with usage examples.

### Schema Management Tools (6 tools)

| Tool | Description | Required Parameters | Optional Parameters |
|------|-------------|---------------------|---------------------|
| `create_table` | Create new table with custom schema | `table_name` (str), `columns` (list[dict]) | None |
| `drop_table` | Delete a table | `table_name` (str) | None |
| `rename_table` | Rename an existing table | `old_name` (str), `new_name` (str) | None |
| `list_tables` | List all tables | None | None |
| `describe_table` | Get schema details | `table_name` (str) | None |
| `list_all_columns` | List all columns for all tables | None | None |

### Data Operations Tools (11 tools)

| Tool | Description | Required Parameters | Optional Parameters |
|------|-------------|---------------------|---------------------|
| `create_row` | Insert row into table | `table_name` (str), `data` (dict) | None |
| `read_rows` | Read rows from table | `table_name` (str) | `where` (dict), `limit` (int) |
| `update_rows` | Update existing rows | `table_name` (str), `data` (dict), `where` (dict) | None |
| `delete_rows` | Delete rows from table | `table_name` (str), `where` (dict) | None |
| `run_select_query` | Run safe SELECT query | `table_name` (str) | `columns` (list[str]), `where` (dict), `limit` (int) |
| `upsert_memory` | Smart update or create memory record with change tracking | `table_name` (str), `data` (dict), `match_columns` (list[str]) | None |
| `batch_create_memories` | Efficiently create multiple memory records | `table_name` (str), `data_list` (list[dict]) | `match_columns` (list[str]), `use_upsert` (bool) |
| `batch_delete_memories` | Delete multiple memory records efficiently | `table_name` (str), `where_conditions` (list[dict]) | `match_all` (bool) |
| `find_duplicates` | Find duplicate and near-duplicate content | `table_name` (str), `content_columns` (list[str]) | `similarity_threshold` (float), `sample_size` (int) |
| `archive_old_memories` | Archive old memories to reduce active storage | `table_name` (str) | `archive_days` (int), `archive_table_suffix` (str), `delete_after_archive` (bool) |
| `optimize_memory_bank` | Comprehensive memory bank optimization | `table_name` (str) | `optimization_strategy` (str), `dry_run` (bool) |

### Search & Discovery Tools (6 tools)

| Tool | Description | Required Parameters | Optional Parameters |
|------|-------------|---------------------|---------------------|
| `search_content` | Full-text search across table content | `query` (str) | `tables` (list[str]), `limit` (int) |
| `explore_tables` | Explore and discover table structures | None | `pattern` (str), `include_row_counts` (bool) |
| `intelligent_discovery` | AI-guided exploration of memory bank | None | `discovery_goal` (str), `focus_area` (str), `depth` (str), `agent_id` (str) |
| `discovery_templates` | Pre-built exploration workflows | None | `template_type` (str), `customize_for` (str) |
| `discover_relationships` | Find hidden connections in data | None | `table_name` (str), `relationship_types` (list[str]), `similarity_threshold` (float) |
| `generate_knowledge_graph` | Create interactive HTML knowledge graphs | None | `output_path` (str), `include_temporal` (bool), `min_connections` (int), `open_in_browser` (bool) |

### Semantic Search Tools (5 tools)

| Tool | Description | Required Parameters | Optional Parameters |
|------|-------------|---------------------|---------------------|
| `add_embeddings` | Generate vector embeddings for semantic search | `table_name` (str), `text_columns` (list[str]) | `embedding_column` (str), `model_name` (str) |
| `semantic_search` | Natural language search using vector similarity | `query` (str) | `tables` (list[str]), `similarity_threshold` (float), `limit` (int) |
| `find_related` | Find content related to specific row by similarity | `table_name` (str), `row_id` (int) | `similarity_threshold` (float), `limit` (int) |
| `smart_search` | Hybrid keyword + semantic search | `query` (str) | `tables` (list[str]), `semantic_weight` (float), `text_weight` (float) |
| `embedding_stats` | Get statistics about semantic search readiness | `table_name` (str) | `embedding_column` (str) |

### Optimization & Analytics Tools (8 tools)

| Tool | Description | Required Parameters | Optional Parameters |
|------|-------------|---------------------|---------------------|
| `analyze_memory_patterns` | Comprehensive content distribution analysis | None | `focus_tables` (list[str]), `include_semantic` (bool) |
| `get_content_health_score` | Overall health scoring with recommendations | None | `tables` (list[str]), `detailed_analysis` (bool) |
| `intelligent_duplicate_analysis` | LLM-assisted semantic duplicate detection | `table_name` (str), `content_columns` (list[str]) | `analysis_depth` (str) |
| `intelligent_optimization_strategy` | AI-powered optimization planning | `table_name` (str) | `optimization_goals` (list[str]) |
| `smart_archiving_policy` | AI-powered retention strategy | `table_name` (str) | `business_context` (str), `retention_requirements` (dict) |
| `auto_semantic_search` | Zero-setup semantic search with auto-embeddings | `query` (str) | `tables` (list[str]), `similarity_threshold` (float), `limit` (int), `model_name` (str) |
| `auto_smart_search` | Zero-setup hybrid search with auto-embeddings | `query` (str) | `tables` (list[str]), `semantic_weight` (float), `text_weight` (float), `limit` (int), `model_name` (str) |
| `list_tool_categories` | List all available tool categories | None | None |

### Visualization & Knowledge Graphs Tools (4 tools)

| Tool | Description | Required Parameters | Optional Parameters |
|------|-------------|---------------------|---------------------|
| `create_3d_knowledge_graph` | Create stunning 3D knowledge graphs with Three.js | None | `output_path` (str), `table_name` (str), `include_semantic_links` (bool), `color_scheme` (str), `camera_position` (str), `animation_enabled` (bool), `export_formats` (list[str]) |
| `create_interactive_d3_graph` | Professional D3.js interactive knowledge graphs | None | `output_path` (str), `include_semantic_links` (bool), `filter_tables` (list[str]), `layout_algorithm` (str), `color_scheme` (str), `export_formats` (list[str]) |
| `create_advanced_d3_dashboard` | Enterprise D3.js dashboard with multiple visualizations | None | `output_path` (str), `dashboard_type` (str), `include_metrics` (bool), `real_time_updates` (bool), `custom_widgets` (list[str]) |
| `export_graph_data` | Export graph data in professional formats | None | `output_path` (str), `format` (str), `include_metadata` (bool), `compress_output` (bool) |

## [1.6.4] - 3D Visualization & Comprehensive Features (2025-06-29)

**Current Version**: The most advanced SQLite Memory Bank release with 30+ MCP tools, 3D visualization, LLM-assisted optimization, and enterprise-scale features.

### 🚀 Recent Major Features
- **3D Knowledge Graphs**: Immersive Three.js/WebGL visualizations with real-time lighting
- **Batch Operations**: Efficient bulk processing with smart duplicate prevention
- **LLM-Assisted Tools**: AI-powered optimization strategies and duplicate analysis
- **Advanced Discovery**: Intelligent exploration with relationship detection
- **Enhanced Upsert**: Detailed change tracking with old vs new value comparisons
- **Zero-Setup Search**: Automatic embedding generation for immediate semantic search
- **Enterprise Optimization**: Comprehensive memory bank optimization with archiving

For detailed changes, see [CHANGELOG.md](CHANGELOG.md).

## 🚀 Batch Operations & Advanced Memory Management

SQLite Memory Bank v1.6.0+ provides powerful batch operations and intelligent optimization for efficient memory management:

### Smart Memory Updates & Change Tracking
- **Enhanced `upsert_memory`**: Intelligent update-or-create with detailed change tracking
- **Field-Level Changes**: See exactly what changed with old vs new value comparisons
- **Duplicate Prevention**: Uses match columns to find existing records
- **Transparency**: Complete visibility into field modifications for debugging

### Efficient Batch Processing
- **`batch_create_memories`**: Create multiple records in a single operation
- **Smart vs Fast Modes**: Choose between upsert logic (prevents duplicates) or fast insertion
- **Partial Success Handling**: Continues processing even if some records fail
- **Detailed Feedback**: Returns counts for created, updated, and failed records

### Flexible Batch Deletion
- **`batch_delete_memories`**: Delete multiple records with complex conditions
- **Flexible Matching**: Support for OR logic (match_any) and AND logic (match_all)
- **Condition Lists**: Delete based on multiple different criteria
- **Safe Operations**: Validates conditions before deletion

### Advanced Optimization Suite
- **`find_duplicates`**: Detect exact and near-duplicate content with semantic analysis
- **`optimize_memory_bank`**: Comprehensive optimization with deduplication and archiving
- **`archive_old_memories`**: Intelligent archiving with configurable retention policies
- **Dry Run Support**: Analyze optimizations before applying changes

### LLM-Assisted Optimization
- **`intelligent_duplicate_analysis`**: AI-powered semantic duplicate detection
- **`intelligent_optimization_strategy`**: Customized optimization planning based on data patterns
- **`smart_archiving_policy`**: AI-generated retention strategies aligned with business needs

### Discovery & Relationship Intelligence
- **`intelligent_discovery`**: AI-guided exploration with goal-oriented workflows
- **`discovery_templates`**: Pre-built exploration patterns for common scenarios
- **`discover_relationships`**: Automatic detection of hidden data connections
- **Zero-Setup Search**: `auto_semantic_search` and `auto_smart_search` with automatic embedding generation

### Usage Examples

```python
# Enhanced upsert with change tracking
upsert_result = upsert_memory('technical_decisions', {
    'decision_name': 'API Design',
    'chosen_approach': 'REST APIs with GraphQL',
    'rationale': 'Better performance and flexibility'
}, match_columns=['decision_name'])
# Returns: {"updated_fields": {"chosen_approach": {"old": "REST APIs", "new": "REST APIs with GraphQL"}}}

# Batch create with duplicate prevention
batch_create_memories('project_insights', [
    {'category': 'performance', 'insight': 'Database indexing strategies'},
    {'category': 'security', 'insight': 'Input validation patterns'},
    {'category': 'architecture', 'insight': 'Microservice communication patterns'}
], match_columns=['category', 'insight'], use_upsert=True)

# Intelligent duplicate detection
find_duplicates('project_knowledge', ['title', 'content'], 
               similarity_threshold=0.85)

# AI-powered optimization strategy
intelligent_optimization_strategy('user_data', 
                                optimization_goals=['performance', 'storage'])

# Zero-setup semantic search
auto_smart_search('machine learning algorithms and AI patterns',
                 semantic_weight=0.7, text_weight=0.3)
```

## 🎨 Advanced Visualization & Knowledge Graphs

SQLite Memory Bank includes powerful visualization capabilities for exploring and presenting your data:

### 3D Knowledge Graphs
- **Three.js/WebGL Rendering**: Hardware-accelerated 3D graphics with real-time lighting
- **Interactive Camera Controls**: Orbit, pan, zoom with smooth animations
- **Multiple Themes**: Professional, vibrant, neon, and cosmic color schemes
- **Export Capabilities**: Screenshots, 3D model formats (GLTF, OBJ)
- **VR Ready**: WebXR support for immersive viewing experiences

### Interactive D3.js Visualizations
- **Professional Knowledge Graphs**: Enterprise-grade interactive visualizations
- **Multiple Layout Algorithms**: Force-directed, hierarchical, circular layouts
- **Real-time Filtering**: Dynamic node/edge filtering with search capabilities
- **Semantic Relationships**: AI-powered intelligent edge connections
- **Export Suite**: PNG, SVG, JSON export for presentations

### Enterprise Dashboards
- **Multi-Widget Dashboards**: Force graphs, timelines, metrics, heatmaps
- **Real-time Updates**: Live data refresh capabilities via WebSocket
- **Cross-widget Filtering**: Interactive drill-down and data exploration
- **Professional Styling**: Enterprise-grade UI/UX design
- **Mobile Responsive**: Optimized for desktop, tablet, and mobile

### Usage Examples

```python
# Create stunning 3D knowledge graph
create_3d_knowledge_graph(
    color_scheme="cosmic",
    animation_enabled=True,
    include_semantic_links=True
)

# Professional interactive D3.js graph
create_interactive_d3_graph(
    layout_algorithm="force",
    color_scheme="professional",
    export_formats=["png", "svg"]
)

# Enterprise dashboard with multiple visualizations
create_advanced_d3_dashboard(
    dashboard_type="enterprise",
    include_metrics=True,
    real_time_updates=True
)
```

---

## Transport Modes

### Stdio Mode (Default)
- **Use case**: MCP clients (VS Code, Claude Desktop, etc.)
- **Protocol**: JSON-RPC over stdin/stdout
- **Command**: `uvx mcp-sqlite-memory-bank`
- **Benefits**: Direct integration with AI assistants and IDEs

### HTTP Mode (Development)
- **Use case**: Development, testing, web APIs
- **Protocol**: HTTP REST API
- **Command**: `python -m mcp_sqlite_memory_bank.server main --port 8000`
- **Benefits**: Web browser access, curl testing, API integration

---

## Installation & Transport Options

**Requirements:**
- Python 3.8 or higher (required packages specified in pyproject.toml)
- FastAPI, Uvicorn (for server mode)
- Supported OS: Windows, macOS, Linux

### Option 1: Install from PyPI (Recommended)
```bash
pip install mcp_sqlite_memory_bank
```

### Option 2: Clone and Install from Source (For Contributors)
```bash
git clone https://github.com/robertmeisner/mcp_sqlite_memory_bank.git
cd mcp_sqlite_memory_bank
pip install -e .
```

### Option 3: Run via NPX-style Command
```bash
python -m pip install --user pipx
pipx run mcp_sqlite_memory_bank
```

### Option 4: Run via UVX (Recommended for MCP clients)
```bash
# Run directly with latest version (recommended)
uvx mcp-sqlite-memory-bank

# Force refresh to get latest updates
uvx --refresh mcp-sqlite-memory-bank
```

---

### Transport Options

SQLite Memory Bank currently supports **stdio transport** for MCP clients:

**Stdio Transport (Default - for MCP clients like VS Code, Claude Desktop):**
```bash
uvx mcp-sqlite-memory-bank
```

**HTTP Transport (Development/Testing only):**
```bash
python -m mcp_sqlite_memory_bank.server main --host 127.0.0.1 --port 8000
```

---

## Setup and Configuration

### Database Location

**Default Behavior (v1.2.5+):**
- **User-specific database**: `~/.mcp_sqlite_memory/memory.db`
- **Isolated per user**: Each user gets their own database
- **Persistent across projects**: Data is preserved between sessions

**Custom Database Paths:**
You can configure a custom database location via the `DB_PATH` environment variable:

- **Project-specific**: `DB_PATH=./project_memory.db`
- **Shared team database**: `DB_PATH=/shared/team_memory.db`
- **Temporary database**: `DB_PATH=/tmp/session_memory.db`

**Environment Variables:**
- `DB_PATH`: Path to the SQLite database file (default: `~/.mcp_sqlite_memory/memory.db`)

**Example `.env`:**
```env
# Use project-specific database
DB_PATH=./project_memory.db

# Or use a specific location
DB_PATH=/path/to/my/memory.db
```

**Migration Note:**
If you were using v1.2.4 or earlier, your data was stored in `./test.db` in the current working directory. To migrate your data:

1. Locate your old `test.db` file
2. Copy it to the new default location: `~/.mcp_sqlite_memory/memory.db`
3. Or set `DB_PATH` to point to your existing database

---

## Integration with Editors & Agent Platforms

### VS Code Integration

#### Manual Configuration

**Option 1: Use Default User Database (Recommended)**
```jsonc
{
  "servers": {
    "SQLite_Memory": {
      "type": "stdio",
      "command": "uvx",
      "args": ["--refresh", "mcp-sqlite-memory-bank"]
    }
  }
}
```

**Option 2: Project-Specific Database**
```jsonc
{
  "servers": {
    "SQLite_Memory": {
      "type": "stdio",
      "command": "uvx", 
      "args": ["--refresh", "mcp-sqlite-memory-bank"],
      "env": {
        "DB_PATH": "${workspaceFolder}/.mcp_memory.db"
      }
    }
  }
}
```

**Option 3: Custom Database Location**
```jsonc
{
  "servers": {
    "SQLite_Memory": {
      "type": "stdio",
      "command": "uvx",
      "args": ["--refresh", "mcp-sqlite-memory-bank"],
      "env": {
        "DB_PATH": "/path/to/your/custom/memory.db"
      }
    }
  }
}
```

### Claude Desktop Integration

Add to your `claude_desktop_config.json`:

```jsonc
{
  "mcpServers": {
    "sqlite_memory": {
      "command": "uvx",
      "args": ["mcp-sqlite-memory-bank"],
      "env": {
        "DB_PATH": "/path/to/your/memory.db"
      }
    }
  }
}
```

- Open your project in VS Code, Cursor, or Claude Desktop. The MCP server will be auto-discovered by Copilot Chat, Cursor, Claude, or any compatible agent.
- Use natural language to create tables, store notes, or build knowledge graphs.

---

## Running the Server

### MCP Stdio Mode (Recommended)

For use with VS Code, Claude Desktop, and other MCP clients:

```bash
# Run with uvx (automatically gets latest version)
uvx mcp-sqlite-memory-bank

# Force refresh to latest version
uvx --refresh mcp-sqlite-memory-bank
```

### Development/Testing Modes

**HTTP Server Mode (for development and testing):**
```bash
python -m mcp_sqlite_memory_bank.server main --port 8000
```

**Direct Python Module:**
```bash
python -m mcp_sqlite_memory_bank.server
```

---



## Resources

The server exposes all tools as MCP resources and supports knowledge graph schemas (nodes, edges, properties).

**Agent & Copilot Usage:**
- See [API documentation](docs/api.md) for:
  - Agent & Copilot usage scenarios (natural language prompt → tool mapping)
  - Accessibility and security notes
- See [Memory usage instructions](examples/memory_instructions.md) for:
  - Implementing persistent memory for LLM agents
  - Schema design and best practices for memory management

**Example Agent Prompt:**
> "Create a table called 'tasks' with columns 'id' (integer, primary key) and 'description' (text)."

This will trigger the `create_table` tool with the appropriate arguments. See the API docs for more agent prompt examples.

---

## Usage Examples

### Quickstart: Basic Table
```python
from mcp_sqlite_memory_bank import create_table, create_row, read_rows

create_table(
    "notes",
    [
        {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
        {"name": "content", "type": "TEXT"}
    ]
)
create_row("notes", {"content": "Hello, memory bank!"})
rows = read_rows("notes")
print(rows)
```

### Knowledge Graph (Nodes & Edges)
```python
# Basic implementation example for creating knowledge graphs
from mcp_sqlite_memory_bank import create_table, create_row, read_rows

create_table("nodes", [
    {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
    {"name": "label", "type": "TEXT"}
])
create_table("edges", [
    {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
    {"name": "source", "type": "INTEGER"},
    {"name": "target", "type": "INTEGER"},
    {"name": "type", "type": "TEXT"}
])
n1 = create_row("nodes", {"label": "Person"})
n2 = create_row("nodes", {"label": "Company"})
create_row("edges", {"source": n1["id"], "target": n2["id"], "type": "works_at"})
print(read_rows("nodes"))
print(read_rows("edges"))
```

### LLM Agent Memory Implementation

Here's an example of how a Python application might implement memory schemas, but remember that LLMs would interact with these capabilities through MCP tools and natural language:

```python
# Initialize memory schema
def initialize_agent_memory():
    tables = list_tables()
    
    # Create tables if they don't exist yet
    if 'user_preferences' not in tables['tables']:
        create_table('user_preferences', [
            {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
            {"name": "preference_type", "type": "TEXT NOT NULL"},
            {"name": "preference_value", "type": "TEXT NOT NULL"},
            {"name": "context", "type": "TEXT"}
        ])

# Store a user preference
def remember_preference(pref_type, pref_value, context=None):
    # Check if this preference already exists
    existing = read_rows('user_preferences', {'preference_type': pref_type})
    
    if existing['rows']:
        # Update existing preference
        update_rows('user_preferences', 
                    {'preference_value': pref_value, 'context': context}, 
                    {'id': existing['rows'][0]['id']})
    else:
        # Create new preference
        create_row('user_preferences', {
            'preference_type': pref_type,
            'preference_value': pref_value,
            'context': context
        })

# Retrieve user preferences
preferences = read_rows('user_preferences')
print(f"Remembered {len(preferences['rows'])} user preferences")
```

An LLM would accomplish the same tasks with natural language commands like:

```
Create a table called 'user_preferences' with columns for id (auto-incrementing primary key), 
preference_type (required text), preference_value (required text), and context (optional text).

Add a row to user_preferences with preference_type="code_style" and preference_value="tabs" and context="User prefers tabs over spaces"

Find all rows in the user_preferences table
```

For a complete agent memory implementation example, see [examples/agent_memory_example.py](examples/agent_memory_example.py) and the detailed [memory usage instructions](examples/memory_instructions.md).

---

## MCP Resources and Prompts Usage

### Using MCP Resources

MCP Resources provide real-time access to memory content through standardized URIs:

```python
# Access resource via MCP client
resource_uri = "memory://tables/list"
tables_resource = await client.read_resource(resource_uri)

# Get table schema
schema_uri = "memory://tables/user_preferences/schema"
schema_resource = await client.read_resource(schema_uri)

# Access table data
data_uri = "memory://tables/user_preferences/data"
data_resource = await client.read_resource(data_uri)

# Search as resource
search_uri = "memory://search/user preferences coding style"
search_resource = await client.read_resource(search_uri)

# Analytics overview
analytics_uri = "memory://analytics/overview"
analytics_resource = await client.read_resource(analytics_uri)
```

### Using MCP Prompts

MCP Prompts provide intelligent analysis workflows:

```python
# Analyze memory content
analysis_prompt = await client.get_prompt("analyze-memory-content", {
    "focus_area": "technical_decisions"
})

# Search and summarize
summary_prompt = await client.get_prompt("search-and-summarize", {
    "query": "database performance optimization",
    "max_results": 10
})

# Technical decision analysis
decision_analysis = await client.get_prompt("technical-decision-analysis", {
    "decision_category": "architecture"
})

# Get memory context for conversations
context_prompt = await client.get_prompt("memory-bank-context", {
    "conversation_topic": "API design patterns"
})
```

### Semantic Search Examples

```python
# 🌟 ZERO-SETUP SEMANTIC SEARCH (RECOMMENDED)
# Automatic semantic search - handles embedding generation automatically
results = auto_semantic_search("machine learning algorithms", 
                               similarity_threshold=0.4, 
                               limit=5)

# 🌟 ZERO-SETUP HYBRID SEARCH (RECOMMENDED)
# Automatic hybrid search - combines semantic + keyword automatically
hybrid_results = auto_smart_search("API design patterns",
                                  semantic_weight=0.7,
                                  text_weight=0.3)

# Advanced: Manual embedding setup (for power users)
add_embeddings("technical_decisions", ["decision_name", "rationale"])

# Advanced: Manual semantic search (requires pre-setup)
results = semantic_search("machine learning algorithms", 
                         similarity_threshold=0.4, 
                         limit=5)

# Find related content from specific text
related = find_related("technical_decisions", 
                      row_id=123, 
                      similarity_threshold=0.5)

# Check semantic search readiness
stats = embedding_stats("technical_decisions")
```

### Discovery & Intelligence Examples

```python
# 🧠 AI-GUIDED EXPLORATION (RECOMMENDED)
# Intelligent discovery with goal-oriented workflows
intelligent_discovery(
    discovery_goal="understand_content",
    depth="moderate",
    focus_area="technical_decisions"
)

# Pre-built exploration templates
discovery_templates("first_time_exploration")

# Automatic relationship discovery
discover_relationships(
    table_name="users",
    relationship_types=["foreign_keys", "semantic_similarity", "temporal_patterns"]
)

# LLM-assisted duplicate analysis
intelligent_duplicate_analysis(
    table_name="project_knowledge",
    content_columns=["title", "content"],
    analysis_depth="semantic"
)

# AI-powered optimization strategy
intelligent_optimization_strategy(
    table_name="user_data",
    optimization_goals=["performance", "storage"]
)

# Smart archiving policy generation
smart_archiving_policy(
    table_name="project_logs",
    business_context="Development project logs",
    retention_requirements={"legal_hold": "2_years", "active_period": "6_months"}
)
```

### Tool Organization Discovery

```python
# Discover tool categories
categories = list_tool_categories()
# Returns: {"schema_management": 6, "data_operations": 11, "optimization": 8, ...}

# Get detailed tool information by category
schema_tools = get_tools_by_category("schema_management")
# Returns detailed info with usage examples for each tool
```

---

## Troubleshooting

### Common MCP Connection Issues

**Server not starting / Connection timeout:**
```bash
# Force refresh uvx cache and try again
uvx --refresh mcp-sqlite-memory-bank

# Check if the command works directly
uvx mcp-sqlite-memory-bank --help
```

**VS Code: "Server exited before responding to initialize request":**
1. Check the MCP configuration in `.vscode/mcp.json`
2. Ensure `uvx` is installed and in your PATH
3. Try restarting VS Code or running "MCP: Restart Server" from Command Palette

**Tools not appearing in IDE:**
1. Verify the server is running: `uvx mcp-sqlite-memory-bank` should start without errors
2. Check that `"type": "stdio"` is set in your MCP configuration
3. Restart your IDE or reload MCP configuration

**Database permission errors:**
- Ensure the directory for `DB_PATH` exists and is writable
- Check file permissions on the SQLite database file
- Use absolute paths in `DB_PATH` to avoid path resolution issues

**Package not found / outdated version:**
```bash
# Clear uvx cache completely
uvx cache remove mcp-sqlite-memory-bank
uvx mcp-sqlite-memory-bank
```

### Semantic Search & Advanced Features Issues

**Semantic search not working / "Dependencies missing" errors:**
- The auto-tools (`auto_semantic_search`, `auto_smart_search`) handle dependencies automatically
- If manual tools fail, dependencies may be missing: `pip install sentence-transformers torch numpy`
- Check embedding generation: `embedding_stats('table_name')` to verify semantic readiness

**3D Knowledge Graph not rendering:**
- Ensure output directory exists and is writable
- Check browser JavaScript console for WebGL errors
- Modern browser required (Chrome 80+, Firefox 75+, Safari 14+)
- Hardware acceleration should be enabled for best performance

**Batch operations timing out:**
- Use smaller batch sizes for `batch_create_memories` (recommend 100-500 records)
- Enable `dry_run=True` for `optimize_memory_bank` to test before applying
- Check available memory for large duplicate detection operations

**LLM-assisted tools not working:**
- These tools require MCP sampling capability in your client
- Ensure your IDE/client supports advanced MCP features
- Check network connectivity for AI-powered analysis features

**Discovery tools returning empty results:**
- Ensure tables have sufficient data for pattern analysis
- Check that `intelligent_discovery` has appropriate permissions
- Verify relationship discovery has data with actual connections

---


## Running Tests

If you are using the `src/` layout, set the Python path so tests can import the package:

**On Windows (PowerShell):**
```powershell
$env:PYTHONPATH = 'src'
pytest
```
**On Linux/macOS:**
```bash
PYTHONPATH=src pytest
```
Or, use:
```bash
pytest --import-mode=importlib
```

---

## Development Setup

To ensure code quality and consistent style, this project uses `flake8` and `pre-commit` hooks.

**Install development dependencies:**

```sh
pip install -r requirements.txt
```

**Enable pre-commit hooks (recommended):**

```sh
pre-commit install
```

This will automatically run `flake8` on staged files before every commit. To manually check all files:

```sh
pre-commit run --all-files
```

If you see lint errors, fix them before committing. You can configure linting rules in the `.flake8` file.

## Support & Contact

- [GitHub Issues](https://github.com/robertmeisner/mcp_sqlite_memory_bank/issues) — Bug reports & feature requests
- [GitHub Discussions](https://github.com/robertmeisner/mcp_sqlite_memory_bank/discussions) — Q&A and community support
- Email: your@email.com

---

## Contributing

Pull requests, issues, and suggestions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

See [docs/api.md](docs/api.md) for a full API reference and [examples/run_server.py](examples/run_server.py) for a server example.

---

## License

MIT

---

## LLM Agent Memory Implementation

The SQLite Memory Bank provides a powerful foundation for implementing persistent memory in LLM agents, enabling them to maintain context across conversation sessions and provide more coherent, personalized assistance.

### Memory Management for LLM Agents

LLM agents can leverage the SQLite Memory Bank to store and retrieve:

1. **User Preferences & Context**
   - Coding style preferences
   - Project-specific terminology
   - Recurring tasks and workflows

2. **Technical Knowledge**
   - Project architecture
   - Design decisions and rationales
   - Documentation snippets

3. **Conversation History**
   - Previous interactions
   - Incomplete tasks
   - Follow-up items

### Memory Schema Example

When LLMs use SQLite Memory Bank, they interact with it through MCP tools rather than direct Python code. Here's how an LLM might create memory schemas through natural language commands:

```
Create a table called 'project_structure' with columns:
- id (integer, auto-incrementing primary key)
- category (required text)
- title (required text)
- content (required text)
- timestamp (text with default current timestamp)

Create a table called 'technical_decisions' with columns:
- id (integer, auto-incrementing primary key)
- decision_name (required text)
- chosen_approach (required text)
- alternatives (text)
- rationale (required text)
- timestamp (text with default current timestamp)
```

Behind the scenes, these natural language requests invoke the appropriate MCP tools (like `create_table`), without the LLM needing to write Python code directly.

The Python implementation shown below is what developers would use when integrating with the SQLite Memory Bank programmatically:

```python
# Initialize memory tables (run once at the start of each session)
def initialize_memory():
    # Check if tables exist
    tables = list_tables()
    
    # Create project structure table if needed
    if 'project_structure' not in tables['tables']:
        create_table('project_structure', [
            {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
            {"name": "category", "type": "TEXT NOT NULL"},
            {"name": "title", "type": "TEXT NOT NULL"},
            {"name": "content", "type": "TEXT NOT NULL"},
            {"name": "timestamp", "type": "TEXT DEFAULT CURRENT_TIMESTAMP"}
        ])
    
    # Create technical decisions table if needed
    if 'technical_decisions' not in tables['tables']:
        create_table('technical_decisions', [
            {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
            {"name": "decision_name", "type": "TEXT NOT NULL"},
            {"name": "chosen_approach", "type": "TEXT NOT NULL"},
            {"name": "alternatives", "type": "TEXT"},
            {"name": "rationale", "type": "TEXT NOT NULL"},
            {"name": "timestamp", "type": "TEXT DEFAULT CURRENT_TIMESTAMP"}
        ])
```

### Store and Retrieve Agent Memory

LLMs can store and retrieve memory through natural language commands that map to MCP tools:

```
Store in project_structure where category is "architecture" and title is "API Design":
Content: "The project uses a RESTful API design with explicit endpoint naming."

Find all entries in project_structure where category is "architecture"
```

For developers integrating programmatically, here's how the implementation might look:

```python
# Store project information
def remember_project_structure(category, title, content):
    # Check if this information already exists
    existing = read_rows('project_structure', {
        'category': category,
        'title': title
    })
    
    if existing:
        # Update existing record
        update_rows('project_structure', 
                    {'content': content}, 
                    {'id': existing[0]['id']})
        return existing[0]['id']
    else:
        # Create new record
        result = create_row('project_structure', {
            'category': category,
            'title': title,
            'content': content
        })
        return result['id']

# Retrieve relevant project information
def recall_project_structure(category=None):
    if category:
        return read_rows('project_structure', {'category': category})
    else:
        return read_rows('project_structure')
```

### Best Practices for Agent Memory

1. **Initialize memory tables** at the start of each session
2. **Check before writing** to avoid duplicate information
3. **Use specific queries** to retrieve only relevant context
4. **Update existing records** instead of creating duplicates
5. **Verify critical information** was saved correctly

For detailed implementation guidelines, see the [memory usage instructions](examples/memory_instructions.md).

---

## Advanced Features

> **Note:** The following features are all planned for future releases and are not currently implemented.

### Progress Reporting for Long Operations (Planned)

For operations that may take significant time, SQLite Memory Bank will provide progress updates:

```python
# Example of a planned feature - not yet implemented
result = run_complex_query('large_table', complex_filter, 
                          with_progress=True, timeout=30)
```

Progress notifications will be sent to the client with percentage complete and estimated time remaining.

### Memory Snapshots (Planned)

Create point-in-time snapshots of your database state:

```python
# Example of planned feature - not yet implemented
# Create a named snapshot
create_memory_snapshot('before_major_update')

# Later restore to that point
restore_memory_snapshot('before_major_update')

# List all available snapshots
list_memory_snapshots()
```

### Memory Federation (Planned Feature)

Connect multiple memory banks for distributed storage:

```python
# Example of planned feature - not yet implemented
# Register external memory bank
register_external_memory('project_knowledge', 'http://other-server:8000/mcp')

# Query across federated memory
federated_results = query_federated_memory('technical_decisions', 
                                          ['local', 'project_knowledge'])
```

## Security Considerations

### Access Controls

By default, SQLite Memory Bank operates with full read/write access to the database. For security-sensitive deployments:

- Use Docker with read-only mounts for specific directories
- Configure environment variables for access levels:
  - `SQLITE_MEMORY_ACCESS=read_only` for read-only mode (planned)
  - `SQLITE_MEMORY_ACCESS=schema_only` to prevent data modification (planned)
  - `SQLITE_MEMORY_ALLOWED_TABLES` to restrict access to specific tables (planned)

### Encryption (Planned Feature)

For sensitive data, enable encryption:

```bash
# Coming soon - not yet implemented
python -m mcp_sqlite_memory_bank --encrypt --password-file /path/to/key
```

### Performance Optimization (Planned)

For large datasets, these features will be added:

- Enable WAL mode with `DB_WAL_MODE=1`
- Set appropriate cache size with `DB_CACHE_SIZE=10000`
- Use the `create_index` tool to optimize frequent queries
- Consider `DB_MEMORY_TEMP=1` for in-memory temporary tables

## Extending SQLite Memory Bank

The following extension features are planned for future releases:

### Custom Schema Validators (Planned Feature)

Create schema validators to ensure data consistency:

```python
# Example of planned feature - not yet implemented
from mcp_sqlite_memory_bank import register_schema_validator

def validate_user_schema(columns):
    required_fields = ['username', 'email']
    for field in required_fields:
        if not any(col['name'] == field for col in columns):
            return False, f"Missing required field: {field}"
    return True, "Schema valid"

register_schema_validator('users', validate_user_schema)
```

### Custom Data Processors (Planned Feature)

Register processors to transform data on read/write:

```python
# Example of planned feature - not yet implemented
from mcp_sqlite_memory_bank import register_data_processor

def process_pii_data(row, operation):
    if operation == 'write' and 'email' in row:
        # Hash or encrypt PII data
        row['email'] = hash_email(row['email'])
    return row

register_data_processor('users', process_pii_data)
```

---
