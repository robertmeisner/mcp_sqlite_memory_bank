# mcp_sqlite_memory_bank

![PyPI](https://img.shields.io/pypi/v/mcp_sqlite_memory_bank)
![CI](https://github.com/yourusername/mcp_sqlite_memory_bank/actions/workflows/ci.yml/badge.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

## Overview

**mcp_sqlite_memory_bank** is a dynamic, agent- and LLM-friendly SQLite memory bank designed for Model Context Protocol (MCP) servers and modern AI agent platforms.

This project provides a robust, discoverable API for creating, exploring, and managing SQLite tables and knowledge graphs. It enables Claude, Anthropic, Github Copilot, Claude Desktop, VS Code, Cursor, and other LLM-powered tools to interact with structured data in a safe, explicit, and extensible way.

**Key Use Cases:**
- Build and query knowledge graphs for semantic search and reasoning
- Store, retrieve, and organize notes or structured data for LLM agents
- Enable natural language workflows for database management and exploration
- Integrate with FastMCP, Claude Desktop, and other agent platforms for seamless tool discovery

**Why mcp_sqlite_memory_bank?**
- Explicit, discoverable APIs for LLMs and agents
- Safe, parameterized queries and schema management
- Designed for extensibility and open source collaboration

---

## Features

- **Dynamic Table Management:** Create, list, describe, rename, and drop tables at runtime
- **CRUD Operations:** Insert, read, update, and delete rows in any table
- **Safe SQL:** Run parameterized SELECT queries with input validation
- **Knowledge Graph Tools:** Built-in support for node/edge schemas and property graphs
- **Agent/LLM Integration:** Explicit, tool-based APIs for easy discovery and automation
- **Open Source:** MIT licensed, fully tested, and ready for community use

---


## Tools & API Reference

All tools are designed for explicit, discoverable use by LLMs, agents, and developers. Each function is available as a direct Python import and as an MCP tool.

### Table Management Tools

| Tool | Description | Required Parameters | Optional Parameters |
|------|-------------|---------------------|---------------------|
| `create_table` | Create new table with custom schema | `table_name` (str), `columns` (list[dict]) | None |
| `drop_table` | Delete a table | `table_name` (str) | None |
| `rename_table` | Rename an existing table | `old_name` (str), `new_name` (str) | None |
| `list_tables` | List all tables | None | None |
| `describe_table` | Get schema details | `table_name` (str) | None |
| `list_all_columns` | List all columns for all tables | None | None |

### Data Management Tools

| Tool | Description | Required Parameters | Optional Parameters |
|------|-------------|---------------------|---------------------|
| `create_row` | Insert row into table | `table_name` (str), `data` (dict) | None |
| `read_rows` | Read rows from table | `table_name` (str) | `where` (dict), `limit` (int) |
| `update_rows` | Update existing rows | `table_name` (str), `data` (dict), `where` (dict) | None |
| `delete_rows` | Delete rows from table | `table_name` (str), `where` (dict) | None |
| `run_select_query` | Run safe SELECT query | `table_name` (str) | `columns` (list[str]), `where` (dict), `limit` (int) |

Each tool validates inputs and returns consistent response formats with success/error indicators and appropriate data payloads.

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
git clone https://github.com/yourusername/mcp_sqlite_memory_bank.git
cd mcp_sqlite_memory_bank
pip install -e .
```

### Option 3: Run via NPX-style Command
```bash
python -m pip install --user pipx
pipx run mcp_sqlite_memory_bank
```

### Option 4: Run via UVX
```bash
# Install UVX if you don't have it
curl -fsSL https://uvx.zip/install.sh | bash

# Run directly without installation
uvx run mcp_sqlite_memory_bank

# Or, specify a version
uvx run mcp_sqlite_memory_bank@1.0.0
```

### Option 5: Docker (Containerized)
```bash
# Pull the image
docker pull yourusername/mcp_sqlite_memory_bank:latest

# Run with stdio transport (for Claude Desktop)
docker run -i --rm \
  --mount type=bind,src=/path/to/data/dir,dst=/data \
  yourusername/mcp_sqlite_memory_bank:latest stdio

# Run with HTTP transport (for API access)
docker run -p 8000:8000 --rm \
  --mount type=bind,src=/path/to/data/dir,dst=/data \
  yourusername/mcp_sqlite_memory_bank:latest http
```

### Transport Options

SQLite Memory Bank currently supports:

- **stdio** (default): For direct integration with Claude Desktop and other MCP clients

Planned transport options (not yet implemented):
- **http**: For web access and API usage
- **streamable-http**: For the latest MCP specification

Run with the default transport:
```bash
python -m mcp_sqlite_memory_bank.server
```

---

## Setup and Configuration

You can configure the database path and other options via environment variables or a `.env` file in your project root.

**Environment Variables:**
- `DB_PATH`: Path to the SQLite database file (default: `./test.db`)
- Any other options supported by the server (see API docs)

**Example `.env`:**
```env
DB_PATH=./test.db
```

---

## Integration with Editors & Agent Platforms

### VS Code Integration

#### Quick Install
[Install with Python Module in VS Code](https://insiders.vscode.dev/redirect/mcp/install?name=sqlite-memory&config=%7B%22command%22%3A%22python%22%2C%22args%22%3A%5B%22-m%22%2C%22mcp_sqlite_memory_bank%22%5D%7D)

[Install with Docker in VS Code](https://insiders.vscode.dev/redirect/mcp/install?name=sqlite-memory&config=%7B%22command%22%3A%22docker%22%2C%22args%22%3A%5B%22run%22%2C%22-i%22%2C%22--rm%22%2C%22--mount%22%2C%22type%3Dbind%2Csrc%3D%24%7BworkspaceFolder%7D%2Cdst%3D%2Fdata%22%2C%22yourusername%2Fmcp_sqlite_memory_bank%3Alatest%22%5D%7D)

#### Manual Configuration

Add or update `.vscode/mcp.json` in your project root:
```jsonc
{
  "servers": {
    "SQLite_Memory": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "mcp_sqlite_memory_bank.server"],
      "env": {
        "DB_PATH": "${workspaceFolder}/data/memory.db"
      }
    }
  }
}
```

## FastMCP Integration (Planned)

```bash
# Coming soon - not yet implemented
fastmcp install mcp_sqlite_memory_bank/server.py --name "SQLite Memory Bank"
```

### Claude Desktop Integration

Add to your `claude_desktop_config.json`:

```jsonc
{
  "mcpServers": {
    "sqlite_memory": {
      "command": "python",
      "args": ["-m", "mcp_sqlite_memory_bank.server"],
      "env": {
        "DB_PATH": "/path/to/your/memory.db"
      }
    }
  }
}
```

#### Docker Option for Claude Desktop

```jsonc
{
  "mcpServers": {
    "sqlite_memory": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "--mount", "type=bind,src=/path/to/data/dir,dst=/data",
        "yourusername/mcp_sqlite_memory_bank:latest"
      ],
      "env": {
        "DB_PATH": "/data/memory.db"
      }
    }
  }
}
```

- Open your project in VS Code, Cursor, or Claude Desktop. The MCP server will be auto-discovered by Copilot Chat, Cursor, Claude, or any compatible agent.
- Use natural language to create tables, store notes, or build knowledge graphs.

---

## Running the Server

### Transport Options

SQLite Memory Bank currently supports stdio transport only:

**Stdio Transport (Default - for Claude Desktop):**
```bash
python -m mcp_sqlite_memory_bank.server
```

**HTTP Transport (REST API - Planned):**
```bash
# Coming soon - not yet implemented
python -m mcp_sqlite_memory_bank.server http --port 8000
```

**Streamable HTTP Transport (Latest MCP Spec - Planned):**
```bash
# Coming soon - not yet implemented
python -m mcp_sqlite_memory_bank.server streamable-http --port 8000
```

**With the example runner:**
```bash
python examples/run_server.py
```

**With FastMCP (Planned):**
```bash
# Coming soon - not yet implemented
fastmcp install mcp_sqlite_memory_bank/server.py --name "SQLite Memory Bank"
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


## Support & Contact

- [GitHub Issues](https://github.com/yourusername/mcp_sqlite_memory_bank/issues) — Bug reports & feature requests
- [GitHub Discussions](https://github.com/yourusername/mcp_sqlite_memory_bank/discussions) — Q&A and community support
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
