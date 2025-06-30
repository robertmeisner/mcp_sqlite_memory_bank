# SQLite Memory Bank API Reference

*Auto-generated from source code*

This document provides comprehensive API reference for all MCP tools in the SQLite Memory Bank.

## Tool Categories

### Table of Contents

- **Server** (37 tools)
  - [create_table](#create-table)
  - [list_tables](#list-tables)
  - [describe_table](#describe-table)
  - [drop_table](#drop-table)
  - [rename_table](#rename-table)
  - [create_row](#create-row)
  - [upsert_memory](#upsert-memory)
  - [read_rows](#read-rows)
  - [update_rows](#update-rows)
  - [delete_rows](#delete-rows)
  - [run_select_query](#run-select-query)
  - [list_all_columns](#list-all-columns)
  - [search_content](#search-content)
  - [explore_tables](#explore-tables)
  - [add_embeddings](#add-embeddings)
  - [auto_semantic_search](#auto-semantic-search)
  - [auto_smart_search](#auto-smart-search)
  - [embedding_stats](#embedding-stats)
  - [semantic_search](#semantic-search)
  - [smart_search](#smart-search)
  - [find_related](#find-related)
  - [generate_knowledge_graph](#generate-knowledge-graph)
  - [create_interactive_d3_graph](#create-interactive-d3-graph)
  - [create_advanced_d3_dashboard](#create-advanced-d3-dashboard)
  - [export_graph_data](#export-graph-data)
  - [intelligent_discovery](#intelligent-discovery)
  - [discovery_templates](#discovery-templates)
  - [discover_relationships](#discover-relationships)
  - [batch_create_memories](#batch-create-memories)
  - [batch_delete_memories](#batch-delete-memories)
  - [find_duplicates](#find-duplicates)
  - [optimize_memory_bank](#optimize-memory-bank)
  - [archive_old_memories](#archive-old-memories)
  - [intelligent_duplicate_analysis](#intelligent-duplicate-analysis)
  - [intelligent_optimization_strategy](#intelligent-optimization-strategy)
  - [smart_archiving_policy](#smart-archiving-policy)
  - [create_3d_knowledge_graph](#create-3d-knowledge-graph)

## Server Tools

*Module: `server.py`*

### `create_table`

Create a new table in the SQLite memory bank.

**Signature:**
```python
def create_table(table_name: str, columns: List[Dict[Any]]) -> ToolResponse:
```

**Parameters:**

- `table_name` (str): Parameter description
- `columns` (List[Dict[Any]]): Parameter description

*Source: server.py:124*

---


### `list_tables`

List all tables in the SQLite memory bank.

**Signature:**
```python
def list_tables() -> ToolResponse:
```

*Source: server.py:154*

---


### `describe_table`

Get detailed schema information for a table.

**Signature:**
```python
def describe_table(table_name: str) -> ToolResponse:
```

**Parameters:**

- `table_name` (str): Parameter description

*Source: server.py:176*

---


### `drop_table`

Drop (delete) a table from the SQLite memory bank.

**Signature:**
```python
def drop_table(table_name: str) -> ToolResponse:
```

**Parameters:**

- `table_name` (str): Parameter description

*Source: server.py:216*

---


### `rename_table`

Rename a table in the SQLite memory bank.

**Signature:**
```python
def rename_table(old_name: str, new_name: str) -> ToolResponse:
```

**Parameters:**

- `old_name` (str): Parameter description
- `new_name` (str): Parameter description

*Source: server.py:241*

---


### `create_row`

Insert a new row into any table in the SQLite Memory Bank for Copilot/AI agents.

**Signature:**
```python
def create_row(table_name: str, data: Dict[Any]) -> ToolResponse:
```

**Parameters:**

- `table_name` (str): Parameter description
- `data` (Dict[Any]): Parameter description

*Source: server.py:266*

---


### `upsert_memory`

🔄 **SMART MEMORY UPSERT** - Prevent duplicates and maintain data consistency!

**Signature:**
```python
def upsert_memory(table_name: str, data: Dict[Any], match_columns: List[str]) -> ToolResponse:
```

**Parameters:**

- `table_name` (str): Parameter description
- `data` (Dict[Any]): Parameter description
- `match_columns` (List[str]): Parameter description

*Source: server.py:292*

---


### `read_rows`

Read rows from any table in the SQLite memory bank, with optional filtering.

**Signature:**
```python
def read_rows(table_name: str, where: Optional[Dict[Any]]) -> ToolResponse:
```

**Parameters:**

- `table_name` (str): Parameter description
- `where` (Optional[Dict[Any]]): Parameter description

*Source: server.py:326*

---


### `update_rows`

Update rows in any table in the SQLite Memory Bank for Copilot/AI agents, matching the WHERE clause.

**Signature:**
```python
def update_rows(table_name: str, data: Dict[Any], where: Optional[Dict[Any]]) -> ToolResponse:
```

**Parameters:**

- `table_name` (str): Parameter description
- `data` (Dict[Any]): Parameter description
- `where` (Optional[Dict[Any]]): Parameter description

*Source: server.py:352*

---


### `delete_rows`

Delete rows from any table in the SQLite Memory Bank for Copilot/AI agents, matching the WHERE clause.

**Signature:**
```python
def delete_rows(table_name: str, where: Optional[Dict[Any]]) -> ToolResponse:
```

**Parameters:**

- `table_name` (str): Parameter description
- `where` (Optional[Dict[Any]]): Parameter description

*Source: server.py:380*

---


### `run_select_query`

Run a safe SELECT query on a table in the SQLite memory bank.

**Signature:**
```python
def run_select_query(table_name: str, columns: Optional[List[str]], where: Optional[Dict[Any]], limit: int) -> ToolResponse:
```

**Parameters:**

- `table_name` (str): Parameter description
- `columns` (Optional[List[str]]): Parameter description
- `where` (Optional[Dict[Any]]): Parameter description
- `limit` (int): Parameter description

*Source: server.py:407*

---


### `list_all_columns`

List all columns for all tables in the SQLite memory bank.

**Signature:**
```python
def list_all_columns() -> ToolResponse:
```

*Source: server.py:444*

---


### `search_content`

Perform full-text search across table content using natural language queries.

**Signature:**
```python
def search_content(query: str, tables: Optional[List[str]], limit: int) -> ToolResponse:
```

**Parameters:**

- `query` (str): Parameter description
- `tables` (Optional[List[str]]): Parameter description
- `limit` (int): Parameter description

*Source: server.py:473*

---


### `explore_tables`

Explore and discover table structures and content for better searchability.

**Signature:**
```python
def explore_tables(pattern: Optional[str], include_row_counts: bool) -> ToolResponse:
```

**Parameters:**

- `pattern` (Optional[str]): Parameter description
- `include_row_counts` (bool): Parameter description

*Source: server.py:509*

---


### `add_embeddings`

⚠️  **ADVANCED TOOL** - Most agents should use auto_smart_search() instead!

**Signature:**
```python
def add_embeddings(table_name: str, text_columns: List[str], embedding_column: str, model_name: str) -> ToolResponse:
```

**Parameters:**

- `table_name` (str): Parameter description
- `text_columns` (List[str]): Parameter description
- `embedding_column` (str): Parameter description
- `model_name` (str): Parameter description

*Source: server.py:546*

---


### `auto_semantic_search`

🚀 **ZERO-SETUP SEMANTIC SEARCH** - Just search, embeddings are handled automatically!

**Signature:**
```python
def auto_semantic_search(query: str, tables: Optional[List[str]], similarity_threshold: float, limit: int, model_name: str) -> ToolResponse:
```

**Parameters:**

- `query` (str): Parameter description
- `tables` (Optional[List[str]]): Parameter description
- `similarity_threshold` (float): Parameter description
- `limit` (int): Parameter description
- `model_name` (str): Parameter description

*Source: server.py:589*

---


### `auto_smart_search`

🚀 **ZERO-SETUP HYBRID SEARCH** - Best of both worlds with automatic embedding!

**Signature:**
```python
def auto_smart_search(query: str, tables: Optional[List[str]], semantic_weight: float, text_weight: float, limit: int, model_name: str) -> ToolResponse:
```

**Parameters:**

- `query` (str): Parameter description
- `tables` (Optional[List[str]]): Parameter description
- `semantic_weight` (float): Parameter description
- `text_weight` (float): Parameter description
- `limit` (int): Parameter description
- `model_name` (str): Parameter description

*Source: server.py:638*

---


### `embedding_stats`

Get statistics about semantic search readiness for a table.

**Signature:**
```python
def embedding_stats(table_name: str, embedding_column: str) -> ToolResponse:
```

**Parameters:**

- `table_name` (str): Parameter description
- `embedding_column` (str): Parameter description

*Source: server.py:685*

---


### `semantic_search`

⚠️  **ADVANCED TOOL** - Most agents should use auto_smart_search() instead!

**Signature:**
```python
def semantic_search(query: str, tables: Optional[List[str]], similarity_threshold: float, limit: int, model_name: str) -> ToolResponse:
```

**Parameters:**

- `query` (str): Parameter description
- `tables` (Optional[List[str]]): Parameter description
- `similarity_threshold` (float): Parameter description
- `limit` (int): Parameter description
- `model_name` (str): Parameter description

*Source: server.py:718*

---


### `smart_search`

⚠️  **ADVANCED TOOL** - Most agents should use auto_smart_search() instead!

**Signature:**
```python
def smart_search(query: str, tables: Optional[List[str]], semantic_weight: float, text_weight: float, limit: int, model_name: str) -> ToolResponse:
```

**Parameters:**

- `query` (str): Parameter description
- `tables` (Optional[List[str]]): Parameter description
- `semantic_weight` (float): Parameter description
- `text_weight` (float): Parameter description
- `limit` (int): Parameter description
- `model_name` (str): Parameter description

*Source: server.py:769*

---


### `find_related`

Find content related to a specific row by semantic similarity.

**Signature:**
```python
def find_related(table_name: str, row_id: int, similarity_threshold: float, limit: int, model_name: str) -> ToolResponse:
```

**Parameters:**

- `table_name` (str): Parameter description
- `row_id` (int): Parameter description
- `similarity_threshold` (float): Parameter description
- `limit` (int): Parameter description
- `model_name` (str): Parameter description

*Source: server.py:819*

---


### `generate_knowledge_graph`

🎯 **KNOWLEDGE GRAPH GENERATOR** - Visualize your memory as an interactive graph!

**Signature:**
```python
def generate_knowledge_graph(output_path: str, include_temporal: bool, min_connections: int, open_in_browser: bool) -> ToolResponse:
```

**Parameters:**

- `output_path` (str): Parameter description
- `include_temporal` (bool): Parameter description
- `min_connections` (int): Parameter description
- `open_in_browser` (bool): Parameter description

*Source: server.py:864*

---


### `create_interactive_d3_graph`

🎨 **PREMIUM D3.JS KNOWLEDGE GRAPH** - Interactive enterprise visualization!

**Signature:**
```python
def create_interactive_d3_graph(output_path: Optional[str], include_semantic_links: bool, filter_tables: Optional[List[str]], min_connections: int, layout_algorithm: str, color_scheme: str, node_size_by: str, open_in_browser: bool, export_formats: Optional[List[str]]) -> ToolResponse:
```

**Parameters:**

- `output_path` (Optional[str]): Parameter description
- `include_semantic_links` (bool): Parameter description
- `filter_tables` (Optional[List[str]]): Parameter description
- `min_connections` (int): Parameter description
- `layout_algorithm` (str): Parameter description
- `color_scheme` (str): Parameter description
- `node_size_by` (str): Parameter description
- `open_in_browser` (bool): Parameter description
- `export_formats` (Optional[List[str]]): Parameter description

*Source: server.py:908*

---


### `create_advanced_d3_dashboard`

🚀 **ENTERPRISE D3.JS DASHBOARD** - Premium visualization dashboard!

**Signature:**
```python
def create_advanced_d3_dashboard(output_path: Optional[str], dashboard_type: str, include_metrics: bool, real_time_updates: bool, custom_widgets: Optional[List[str]]) -> ToolResponse:
```

**Parameters:**

- `output_path` (Optional[str]): Parameter description
- `dashboard_type` (str): Parameter description
- `include_metrics` (bool): Parameter description
- `real_time_updates` (bool): Parameter description
- `custom_widgets` (Optional[List[str]]): Parameter description

*Source: server.py:966*

---


### `export_graph_data`

📊 **GRAPH DATA EXPORT** - Professional data format conversion!

**Signature:**
```python
def export_graph_data(output_path: Optional[str], format: str, include_metadata: bool, compress_output: bool) -> ToolResponse:
```

**Parameters:**

- `output_path` (Optional[str]): Parameter description
- `format` (str): Parameter description
- `include_metadata` (bool): Parameter description
- `compress_output` (bool): Parameter description

*Source: server.py:1001*

---


### `intelligent_discovery`

🧠 **INTELLIGENT DISCOVERY** - AI-guided exploration of your memory bank!

**Signature:**
```python
def intelligent_discovery(discovery_goal: str, focus_area: Optional[str], depth: str, agent_id: Optional[str]) -> ToolResponse:
```

**Parameters:**

- `discovery_goal` (str): Parameter description
- `focus_area` (Optional[str]): Parameter description
- `depth` (str): Parameter description
- `agent_id` (Optional[str]): Parameter description

*Source: server.py:1036*

---


### `discovery_templates`

📋 **DISCOVERY TEMPLATES** - Pre-built exploration workflows for common scenarios!

**Signature:**
```python
def discovery_templates(template_type: str, customize_for: Optional[str]) -> ToolResponse:
```

**Parameters:**

- `template_type` (str): Parameter description
- `customize_for` (Optional[str]): Parameter description

*Source: server.py:1086*

---


### `discover_relationships`

🔗 **RELATIONSHIP DISCOVERY** - Find hidden connections in your data!

**Signature:**
```python
def discover_relationships(table_name: Optional[str], relationship_types: List[str], similarity_threshold: float) -> ToolResponse:
```

**Parameters:**

- `table_name` (Optional[str]): Parameter description
- `relationship_types` (List[str]): Parameter description
- `similarity_threshold` (float): Parameter description

*Source: server.py:1128*

---


### `batch_create_memories`

🚀 **BATCH MEMORY CREATION** - Efficiently add multiple memories at once!

**Signature:**
```python
def batch_create_memories(table_name: str, data_list: List[Dict[Any]], match_columns: Optional[List[str]], use_upsert: bool) -> ToolResponse:
```

**Parameters:**

- `table_name` (str): Parameter description
- `data_list` (List[Dict[Any]]): Parameter description
- `match_columns` (Optional[List[str]]): Parameter description
- `use_upsert` (bool): Parameter description

*Source: server.py:1304*

---


### `batch_delete_memories`

🗑️ **BATCH MEMORY DELETION** - Efficiently delete multiple memories at once!

**Signature:**
```python
def batch_delete_memories(table_name: str, where_conditions: List[Dict[Any]], match_all: bool) -> ToolResponse:
```

**Parameters:**

- `table_name` (str): Parameter description
- `where_conditions` (List[Dict[Any]]): Parameter description
- `match_all` (bool): Parameter description

*Source: server.py:1346*

---


### `find_duplicates`

🔍 **DUPLICATE DETECTION** - Find duplicate and near-duplicate content!

**Signature:**
```python
def find_duplicates(table_name: str, content_columns: List[str], similarity_threshold: float, sample_size: Optional[int]) -> ToolResponse:
```

**Parameters:**

- `table_name` (str): Parameter description
- `content_columns` (List[str]): Parameter description
- `similarity_threshold` (float): Parameter description
- `sample_size` (Optional[int]): Parameter description

*Source: server.py:1387*

---


### `optimize_memory_bank`

⚡ **MEMORY BANK OPTIMIZATION** - Optimize storage and performance!

**Signature:**
```python
def optimize_memory_bank(table_name: str, optimization_strategy: str, dry_run: bool) -> ToolResponse:
```

**Parameters:**

- `table_name` (str): Parameter description
- `optimization_strategy` (str): Parameter description
- `dry_run` (bool): Parameter description

*Source: server.py:1426*

---


### `archive_old_memories`

📦 **MEMORY ARCHIVING** - Archive old memories to reduce active storage!

**Signature:**
```python
def archive_old_memories(table_name: str, archive_days: int, archive_table_suffix: str, delete_after_archive: bool) -> ToolResponse:
```

**Parameters:**

- `table_name` (str): Parameter description
- `archive_days` (int): Parameter description
- `archive_table_suffix` (str): Parameter description
- `delete_after_archive` (bool): Parameter description

*Source: server.py:1460*

---


### `intelligent_duplicate_analysis`

🧠 **LLM-ASSISTED DUPLICATE DETECTION** - AI-powered semantic duplicate analysis!

**Signature:**
```python
def intelligent_duplicate_analysis(table_name: str, content_columns: List[str], analysis_depth: str) -> ToolResponse:
```

**Parameters:**

- `table_name` (str): Parameter description
- `content_columns` (List[str]): Parameter description
- `analysis_depth` (str): Parameter description

*Source: server.py:1503*

---


### `intelligent_optimization_strategy`

🎯 **LLM-GUIDED OPTIMIZATION STRATEGY** - AI-powered optimization planning!

**Signature:**
```python
def intelligent_optimization_strategy(table_name: str, optimization_goals: Optional[List[str]]) -> ToolResponse:
```

**Parameters:**

- `table_name` (str): Parameter description
- `optimization_goals` (Optional[List[str]]): Parameter description

*Source: server.py:1535*

---


### `smart_archiving_policy`

📋 **INTELLIGENT ARCHIVING POLICY** - AI-powered retention strategy!

**Signature:**
```python
def smart_archiving_policy(table_name: str, business_context: Optional[str], retention_requirements: Optional[Dict[Any]]) -> ToolResponse:
```

**Parameters:**

- `table_name` (str): Parameter description
- `business_context` (Optional[str]): Parameter description
- `retention_requirements` (Optional[Dict[Any]]): Parameter description

*Source: server.py:1561*

---


### `create_3d_knowledge_graph`

🌐 **THREE.JS 3D KNOWLEDGE GRAPH** - Immersive 3D data visualization!

**Signature:**
```python
def create_3d_knowledge_graph(output_path: Optional[str], table_name: str, include_semantic_links: bool, color_scheme: str, camera_position: str, animation_enabled: bool, export_formats: Optional[List[str]]) -> ToolResponse:
```

**Parameters:**

- `output_path` (Optional[str]): Parameter description
- `table_name` (str): Parameter description
- `include_semantic_links` (bool): Parameter description
- `color_scheme` (str): Parameter description
- `camera_position` (str): Parameter description
- `animation_enabled` (bool): Parameter description
- `export_formats` (Optional[List[str]]): Parameter description

*Source: server.py:1597*

---

