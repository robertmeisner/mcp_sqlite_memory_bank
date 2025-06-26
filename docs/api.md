# API Reference: mcp_sqlite_memory_bank

## Tool Signatures

| Tool (Function) | Signature | Description |
|-----------------|-----------|-------------|
| `create_table`    | `create_table(table_name: str, columns: List[Dict[str, str]]) -> ToolResponse`    | Create a new table with a given schema. Returns `{"success": True}` on success. |
| `drop_table`      | `drop_table(table_name: str) -> ToolResponse`                                      | Drop (delete) a table. Returns `{"success": True}` on success. |
| `rename_table`    | `rename_table(old_name: str, new_name: str) -> ToolResponse`                        | Rename a table. Returns `{"success": True}` on success. |
| `list_tables`     | `list_tables() -> ToolResponse`                                                    | List all tables in the database. Returns `{"success": True, "tables": List[str]}`. |
| `describe_table`  | `describe_table(table_name: str) -> ToolResponse`                                  | Get schema details for a table. Returns `{"success": True, "columns": List[TableColumn]}`. |
| `list_all_columns`| `list_all_columns() -> ToolResponse`                                               | List all columns for all tables. Returns `{"success": True, "schemas": Dict[str, List[str]]}`. |
| `create_row`      | `create_row(table_name: str, data: Dict[str, Any]) -> ToolResponse`                 | Insert a row into any table. Returns `{"success": True, "id": int}`. |
| `read_rows`       | `read_rows(table_name: str, where: Optional[Dict[str, Any]] = None) -> ToolResponse`| Read rows from any table with optional filter. Returns `{"success": True, "rows": List[Dict[str, Any]]}`. |
| `update_rows`     | `update_rows(table_name: str, data: Dict[str, Any], where: Optional[Dict[str, Any]] = None) -> ToolResponse` | Update rows in any table. Returns `{"success": True, "rows_affected": int}`. |
| `delete_rows`     | `delete_rows(table_name: str, where: Optional[Dict[str, Any]] = None) -> ToolResponse`| Delete rows from any table. Returns `{"success": True, "rows_affected": int}`. |
| `run_select_query`| `run_select_query(table_name: str, columns: Optional[List[str]] = None, where: Optional[Dict[str, Any]] = None, limit: int = 100) -> ToolResponse` | Run a safe SELECT query. Returns `{"success": True, "rows": List[Dict[str, Any]]}`. |

See in-code docstrings for detailed usage and examples.

---

---


## Agent & Copilot Usage Scenarios

These tools are designed for explicit, discoverable use by LLMs, Copilot, Claude, and other agent platforms. Agents can discover available tools and invoke them using natural language or tool APIs.

### Example: Natural Language Prompts

- **Prompt:**
  > "Create a table called 'tasks' with columns 'id' (integer, primary key) and 'description' (text)."
  
  **Agent Action:**
  - Discovers the `create_table` tool and calls:
    ```json
    {
      "tool": "create_table",
      "args": {
        "table": "tasks",
        "columns": [
          {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
          {"name": "description", "type": "TEXT"}
        ]
      }
    }
    ```

- **Prompt:**
  > "Show me all notes containing the word 'meeting'."
  
  **Agent Action:**
  - Discovers the `run_select_query` tool and calls:
    ```json
    {
      "tool": "run_select_query",
      "args": {
        "query": "SELECT * FROM notes WHERE content LIKE :search LIMIT 10",
        "params": {"search": "%meeting%"}
      }
    }
    ```

- **Prompt:**
  > "List all tables and their columns."
  
  **Agent Action:**
  - Calls `list_tables` and then `describe_table` for each table.

### Discoverability & Safety
- All tools are registered with explicit names and signatures for agent/LLM discovery.
- Parameterized queries and schema validation ensure safe, reliable operation.
- Agents can enumerate available tools and their arguments for robust automation (e.g., via MCP tool discovery endpoints or OpenAPI schemas, depending on platform).

---

## Real-World Usage Scenarios (Python)

These examples show direct programmatic access from Python for developers and advanced users.

### 1. Note-Taking Agent
Create a table for notes, add a note, and retrieve all notes:
```python
create_table("notes", [
    {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
    {"name": "content", "type": "TEXT"}
])
create_row("notes", {"content": "Meeting at 3pm"})
notes = read_rows("notes")
```

### 2. Knowledge Graph Construction
Model entities and relationships for semantic search:
```python
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
```

### 3. Parameterized Query for LLM Safety
Run a safe SELECT query with user input:
```python
rows = run_select_query(
    "SELECT * FROM notes WHERE content LIKE :search LIMIT 10",
    params={"search": "%meeting%"}
)
```

### 4. Table Schema Discovery for Agents
List all tables and describe their schemas for tool discovery:
```python
tables = list_tables()
for t in tables:
    print(describe_table(t))
```

---

## Accessibility Considerations

- All APIs are designed to be explicit and discoverable for LLMs and agent platforms.
- When building UIs on top of this API, use semantic HTML, ARIA roles, and ensure keyboard navigation.
- Provide labels for all form fields and ensure color contrast meets WCAG 2.1 AA or higher.
- Use alternative text for icons and images in any UI.

---

## Security Notes

- All SQL queries are parameterized to prevent SQL injection.
- User input is validated and sanitized before execution.
- Database file paths should be controlled via environment variables and not exposed to untrusted users.
- For web/server deployments, enforce strong Content Security Policies (CSP) and use secure cookies if applicable.
- Limit privileges and use role-based access control if extending for multi-user scenarios.

---
