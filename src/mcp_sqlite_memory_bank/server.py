"""
SQLite Memory Bank for Copilot/AI Agents
=======================================

This FastMCP server provides a dynamic, agent-friendly SQLite memory bank.
All APIs are explicit, discoverable, and validated for safe, flexible use by LLMs and agent frameworks.

**Design Note:**
    - All CRUD and schema operations are exposed as explicit, type-annotated, and well-documented FastMCP tools.
    - All tools are registered directly on the FastMCP app instance using the @mcp.tool decorator.
    - This design is preferred for LLMs and clients, as it ensures discoverability, schema validation, and ease of use.
    - No multiplexed or control-argument tools are provided as primary interfaces.
    - Uses SQLAlchemy Core for robust, type-safe database operations.

Available Tools (for LLMs/agents):
----------------------------------
    - create_table(table, columns): Create a new table with a custom schema.
    - drop_table(table): Drop (delete) a table.
    - rename_table(old_name, new_name): Rename a table.
    - list_tables(): List all tables in the memory bank.
    - describe_table(table): Get schema details for a table.
    - list_all_columns(): List all columns for all tables.
    - create_row(table, data): Insert a row into any table.
    - read_rows(table, where): Read rows from any table (with optional filtering).
    - update_rows(table, data, where): Update rows from any table (with optional filtering).
    - delete_rows(table, where): Delete rows from any table (with optional filtering).
    - run_select_query(table, columns, where): Run a safe SELECT query (no arbitrary SQL).
    - search_content(query, tables): Perform full-text search across table content.
    - explore_tables(pattern): Discover table structures and content for better searchability.

All table/column names are validated to prevent SQL injection.
Only safe, explicit operations are allowed (no arbitrary SQL).
All tools are documented and designed for explicit, LLM-friendly use.

FastMCP Tool Documentation:
--------------------------
Each tool is designed for explicit, discoverable use by LLMs and agents:
- All parameters are strongly typed and validated
- Success/error responses follow a consistent pattern
- Error messages are clear and actionable for both humans and LLMs
- Documentation includes examples and common use cases

Author: Robert Meisner
"""

import os
import re
import logging
from typing import Dict, Optional, List, cast, Any
from fastmcp import FastMCP

from .database import get_database
from .semantic import is_semantic_search_available
from .types import (
    ToolResponse,
    CreateTableResponse,
    DropTableResponse,
    RenameTableResponse,
    ListTablesResponse,
    DescribeTableResponse,
    ListAllColumnsResponse,
    CreateRowResponse,
    ReadRowsResponse,
    UpdateRowsResponse,
    DeleteRowsResponse,
    SelectQueryResponse,
)
from .utils import catch_errors
from .resources import setup_mcp_resources
from .prompts import setup_mcp_prompts

# Import modular tool implementations (for aliases only)
from .tools import basic, search, analytics

# Initialize FastMCP app with explicit name
mcp: FastMCP = FastMCP("SQLite Memory Bank for Copilot/AI Agents")

# Configure database path from environment or default
DB_PATH = os.environ.get("DB_PATH", "./test.db")

# Ensure database directory exists
os.makedirs(os.path.dirname(os.path.abspath(DB_PATH)), exist_ok=True)

# Initialize database
db = get_database(DB_PATH)

# Set up MCP Resources for enhanced context provision
setup_mcp_resources(mcp, DB_PATH)

# Set up MCP Prompts for enhanced workflow support
setup_mcp_prompts(mcp, DB_PATH)

# All tools are registered via @mcp.tool decorators below
# No explicit registration needed - decorators handle this automatically


# --- Schema Management Tools for SQLite Memory Bank ---


@mcp.tool
@catch_errors
def create_table(table_name: str, columns: List[Dict[str, str]]) -> ToolResponse:
    """
    Create a new table in the SQLite memory bank.

    Args:
        table_name (str): Name of the table to create. Must be a valid SQLite identifier.
        columns (List[Dict[str, str]]): List of columns, each as {"name": str, "type": str}.

    Returns:
        ToolResponse: On success: {"success": True}
                     On error: {"success": False, "error": str, "category": str, "details": dict}

    Examples:
        >>> create_table("users", [
        ...     {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
        ...     {"name": "name", "type": "TEXT"},
        ...     {"name": "age", "type": "INTEGER"}
        ... ])
        {"success": True}

    FastMCP Tool Info:
        - Validates table name and column definitions
        - Creates table if it doesn't exist (idempotent)
        - Raises appropriate errors for invalid input
    """
    return cast(
        CreateTableResponse, get_database(DB_PATH).create_table(table_name, columns)
    )


@mcp.tool
@catch_errors
def list_tables() -> ToolResponse:
    """
    List all tables in the SQLite memory bank.

    Returns:
        ToolResponse: On success: {"success": True, "tables": List[str]}
                     On error: {"success": False, "error": str, "category": str, "details": dict}

    Examples:
        >>> list_tables()
        {"success": True, "tables": ["users", "notes", "tasks"]}

    FastMCP Tool Info:
        - Returns list of all user-created tables
        - Excludes SQLite system tables
        - Useful for schema discovery by LLMs
    """
    return cast(ListTablesResponse, get_database(DB_PATH).list_tables())


@mcp.tool
@catch_errors
def describe_table(table_name: str) -> ToolResponse:
    """
    Get detailed schema information for a table.

    Args:
        table_name (str): Name of the table to describe.

    Returns:
        ToolResponse: On success: {"success": True, "columns": List[TableColumn]}
                     On error: {"success": False, "error": str, "category": str, "details": dict}

        Where TableColumn is:
        {
            "name": str,
            "type": str,
            "nullable": bool,
            "default": Any,
            "primary_key": bool
        }

    Examples:
        >>> describe_table("users")
        {
            "success": True,
            "columns": [
                {"name": "id", "type": "INTEGER", "nullable": False, "default": null, "primary_key": True},
                {"name": "name", "type": "TEXT", "nullable": True, "default": null, "primary_key": False}
            ]
        }

    FastMCP Tool Info:
        - Returns detailed column information
        - Validates table existence
        - Useful for schema introspection by LLMs
    """
    return cast(DescribeTableResponse, get_database(DB_PATH).describe_table(table_name))


@mcp.tool
@catch_errors
def drop_table(table_name: str) -> ToolResponse:
    """
    Drop (delete) a table from the SQLite memory bank.

    Args:
        table_name (str): Name of the table to drop. Must be a valid SQLite identifier.

    Returns:
        ToolResponse: On success: {"success": True}
                     On error: {"success": False, "error": str, "category": str, "details": dict}

    Examples:
        >>> drop_table('notes')
        {"success": True}

    FastMCP Tool Info:
        - Validates table name
        - Confirms table exists before dropping
        - WARNING: This operation is irreversible and deletes all data in the table
    """
    return cast(DropTableResponse, get_database(DB_PATH).drop_table(table_name))


@mcp.tool
@catch_errors
def rename_table(old_name: str, new_name: str) -> ToolResponse:
    """
    Rename a table in the SQLite memory bank.

    Args:
        old_name (str): Current table name. Must be a valid SQLite identifier.
        new_name (str): New table name. Must be a valid SQLite identifier.

    Returns:
        ToolResponse: On success: {"success": True}
                     On error: {"success": False, "error": str, "category": str, "details": dict}

    Examples:
        >>> rename_table('notes', 'archive_notes')
        {"success": True}

    FastMCP Tool Info:
        - Validates both old and new table names
        - Confirms old table exists and new name doesn't conflict
    """
    return cast(
        RenameTableResponse, get_database(DB_PATH).rename_table(old_name, new_name)
    )


@mcp.tool
@catch_errors
def create_row(table_name: str, data: Dict[str, Any]) -> ToolResponse:
    """
    Insert a new row into any table in the SQLite Memory Bank for Copilot/AI agents.

    Args:
        table_name (str): Table name.
        data (Dict[str, Any]): Data to insert (column-value pairs matching the table schema).

    Returns:
        ToolResponse: On success: {"success": True, "id": rowid}
                     On error: {"success": False, "error": str, "category": str, "details": dict}

    Examples:
        >>> create_row('notes', {'content': 'Remember to hydrate!'})
        {"success": True, "id": 1}

    FastMCP Tool Info:
        - Validates table name and column names
        - Auto-converts data types where possible
        - Returns the row ID of the inserted row
    """
    return cast(CreateRowResponse, get_database(DB_PATH).insert_row(table_name, data))


@mcp.tool
@catch_errors
def upsert_memory(
    table_name: str, data: Dict[str, Any], match_columns: List[str]
) -> ToolResponse:
    """
    🔄 **SMART MEMORY UPSERT** - Prevent duplicates and maintain data consistency!

    Update existing records or create new ones based on matching columns.
    This is the preferred method for memory management as it prevents duplicates.

    Args:
        table_name (str): Table to upsert into
        data (Dict[str, Any]): Data to upsert (column-value pairs)
        match_columns (List[str]): Columns to use for finding existing records

    Returns:
        ToolResponse: On success: {"success": True, "action": "updated"|"created", "id": rowid}
                     On error: {"success": False, "error": str, "category": str, "details": dict}

    Examples:
        >>> upsert_memory('technical_decisions',
        ...     {'decision_name': 'API Design', 'chosen_approach': 'REST'},
        ...     ['decision_name'])
        {"success": True, "action": "updated", "id": 15, "rows_affected": 1}

    FastMCP Tool Info:
        - **PREVENTS DUPLICATES**: Automatically updates existing records instead of creating duplicates
        - **SMART MATCHING**: Uses specified columns to find existing records
        - **EFFICIENT MEMORY MANAGEMENT**: Ideal for agent memory patterns
        - **CLEAR FEEDBACK**: Returns whether record was created or updated
        - **PERFECT FOR AGENTS**: Handles the common "update or create" pattern automatically
    """
    return basic.upsert_memory(table_name, data, match_columns)


@mcp.tool
@catch_errors
def read_rows(table_name: str, where: Optional[Dict[str, Any]] = None) -> ToolResponse:
    """
    Read rows from any table in the SQLite memory bank, with optional filtering.

    Args:
        table_name (str): Name of the table to read from.
        where (Optional[Dict[str, Any]]): Optional filter conditions as {"column": value} pairs.

    Returns:
        ToolResponse: On success: {"success": True, "rows": List[Dict[str, Any]]}
                     On error: {"success": False, "error": str, "category": str, "details": dict}

    Examples:
        >>> read_rows("users", {"age": 25})
        {"success": True, "rows": [{"id": 1, "name": "Alice", "age": 25}, ...]}

    FastMCP Tool Info:
        - Validates table name and filter conditions
        - Returns rows as list of dictionaries
        - Parameterizes all queries for safety
    """
    return cast(ReadRowsResponse, get_database(DB_PATH).read_rows(table_name, where))


@mcp.tool
@catch_errors
def update_rows(
    table_name: str, data: Dict[str, Any], where: Optional[Dict[str, Any]] = None
) -> ToolResponse:
    """
    Update rows in any table in the SQLite Memory Bank for Copilot/AI agents, matching the WHERE clause.

    Args:
        table_name (str): Table name.
        data (Dict[str, Any]): Data to update (column-value pairs).
        where (Optional[Dict[str, Any]]): WHERE clause as column-value pairs (optional).

    Returns:
        ToolResponse: On success: {"success": True, "rows_affected": n}
                     On error: {"success": False, "error": str, "category": str, "details": dict}

    Examples:
        >>> update_rows('notes', {'content': 'Updated note'}, {'id': 1})
        {"success": True, "rows_affected": 1}

    FastMCP Tool Info:
        - Validates table name, column names, and filter conditions
        - Returns the number of rows affected by the update
        - Parameterizes all queries for safety
        - Where clause is optional (omitting it updates all rows!)
    """
    return cast(
        UpdateRowsResponse, get_database(DB_PATH).update_rows(table_name, data, where)
    )


@mcp.tool
@catch_errors
def delete_rows(
    table_name: str, where: Optional[Dict[str, Any]] = None
) -> ToolResponse:
    """
    Delete rows from any table in the SQLite Memory Bank for Copilot/AI agents, matching the WHERE clause.

    Args:
        table_name (str): Table name.
        where (Optional[Dict[str, Any]]): WHERE clause as column-value pairs (optional).

    Returns:
        ToolResponse: On success: {"success": True, "rows_affected": n}
                     On error: {"success": False, "error": str, "category": str, "details": dict}

    Examples:
        >>> delete_rows('notes', {'id': 1})
        {"success": True, "rows_affected": 1}

    FastMCP Tool Info:
        - Validates table name and filter conditions
        - Returns the number of rows deleted
        - Parameterizes all queries for safety
        - Where clause is optional (omitting it deletes all rows!)
    """
    return cast(
        DeleteRowsResponse, get_database(DB_PATH).delete_rows(table_name, where)
    )


@mcp.tool
@catch_errors
def run_select_query(
    table_name: str,
    columns: Optional[List[str]] = None,
    where: Optional[Dict[str, Any]] = None,
    limit: int = 100,
) -> ToolResponse:
    """
    Run a safe SELECT query on a table in the SQLite memory bank.

    Args:
        table_name (str): Table name.
        columns (Optional[List[str]]): List of columns to select (default: all).
        where (Optional[Dict[str, Any]]): WHERE clause as column-value pairs (optional).
        limit (int): Maximum number of rows to return (default: 100).

    Returns:
        ToolResponse: On success: {"success": True, "rows": [...]}
                     On error: {"success": False, "error": str, "category": str, "details": dict}

    Examples:
        >>> run_select_query('notes', ['id', 'content'], {'id': 1})
        {"success": True, "rows": [{"id": 1, "content": "Remember to hydrate!"}]}

    FastMCP Tool Info:
        - Validates table name, column names, and filter conditions
        - Parameterizes all queries for safety
        - Only SELECT queries are allowed (no arbitrary SQL)
        - Default limit of 100 rows prevents memory issues
    """
    return cast(
        SelectQueryResponse,
        get_database(DB_PATH).select_query(table_name, columns, where, limit),
    )


@mcp.tool
@catch_errors
def list_all_columns() -> ToolResponse:
    """
    List all columns for all tables in the SQLite memory bank.

    Returns:
        ToolResponse: On success: {"success": True, "schemas": {table_name: [columns]}}
                     On error: {"success": False, "error": str, "category": str, "details": dict}

    Examples:
        >>> list_all_columns()
        {"success": True, "schemas": {"users": ["id", "name", "age"], "notes": ["id", "content"]}}

    FastMCP Tool Info:
        - Provides a full schema overview of the database
        - Useful for agents to understand database structure
        - Returns a nested dictionary with all table schemas
    """
    return cast(ListAllColumnsResponse, get_database(DB_PATH).list_all_columns())


# Import the implementation functions from tools modules
from .tools.search import (
    search_content as search_content_impl,
    explore_tables as explore_tables_impl,
    add_embeddings as add_embeddings_impl,
    auto_semantic_search as auto_semantic_search_impl,
    auto_smart_search as auto_smart_search_impl,
    embedding_stats as embedding_stats_impl,
)

# Import the implementation functions from discovery module
from .tools.discovery import (
    intelligent_discovery as intelligent_discovery_impl,
    discovery_templates as discovery_templates_impl,
    discover_relationships as discover_relationships_impl,
)

# --- MCP Tool Definitions (Required in main server.py for FastMCP) ---


@mcp.tool
@catch_errors
def search_content(
    query: str,
    tables: Optional[List[str]] = None,
    limit: int = 50,
) -> ToolResponse:
    """
    Perform full-text search across table content using natural language queries.

    Args:
        query (str): Search query (supports natural language, keywords, phrases)
        tables (Optional[List[str]]): Specific tables to search (default: all tables)
        limit (int): Maximum number of results to return (default: 50)

    Returns:
        ToolResponse: On success: {"success": True, "results": List[SearchResult]}
                     On error: {"success": False, "error": str, "category": str, "details": dict}

    Examples:
        >>> search_content("API design patterns")
        {"success": True, "results": [
            {"table": "technical_decisions", "row_id": 1, "content": "...", "relevance": 0.85},
            {"table": "project_structure", "row_id": 3, "content": "...", "relevance": 0.72}
        ]}

    FastMCP Tool Info:
        - Searches all text columns across specified tables
        - Uses SQLite FTS for fast full-text search
        - Returns results ranked by relevance
        - Supports phrase search with quotes: "exact phrase"
        - Supports boolean operators: AND, OR, NOT
    """
    return search_content_impl(query, tables, limit)


@mcp.tool
@catch_errors
def explore_tables(
    pattern: Optional[str] = None,
    include_row_counts: bool = True,
) -> ToolResponse:
    """
    Explore and discover table structures and content for better searchability.

    Args:
        pattern (Optional[str]): Optional pattern to filter table names (SQL LIKE pattern)
        include_row_counts (bool): Whether to include row counts for each table

    Returns:
        ToolResponse: On success: {"success": True, "exploration": Dict}
                     On error: {"success": False, "error": str, "category": str, "details": dict}

    Examples:
        >>> explore_tables()
        {"success": True, "exploration": {
            "tables": [
                {"name": "users", "columns": [...], "row_count": 42, "sample_data": [...]},
                {"name": "notes", "columns": [...], "row_count": 156, "sample_data": [...]}
            ],
            "total_tables": 2,
            "total_rows": 198
        }}

    FastMCP Tool Info:
        - Provides overview of all tables and their structure
        - Shows sample data for content discovery
        - Helps understand what data is available for searching
        - Useful for exploratory data analysis
    """
    return explore_tables_impl(pattern, include_row_counts)


@mcp.tool
@catch_errors
def add_embeddings(
    table_name: str,
    text_columns: List[str],
    embedding_column: str = "embedding",
    model_name: str = "all-MiniLM-L6-v2",
) -> ToolResponse:
    """
    ⚠️  **ADVANCED TOOL** - Most agents should use auto_smart_search() instead!

    Generate and store vector embeddings for semantic search on table content.

    **RECOMMENDATION**: Use auto_smart_search() or auto_semantic_search() for automatic setup.
    This tool is for advanced users who need manual control over embedding generation.

    This tool enables intelligent knowledge discovery by creating vector representations
    of text content that can be searched semantically rather than just by exact keywords.

    Args:
        table_name (str): Name of the table to add embeddings to
        text_columns (List[str]): List of text columns to generate embeddings from
        embedding_column (str): Column name to store embeddings (default: "embedding")
        model_name (str): Sentence transformer model to use (default: "all-MiniLM-L6-v2")

    Returns:
        ToolResponse: On success: {"success": True, "processed": int, "model": str}
                     On error: {"success": False, "error": str, "category": str, "details": dict}

    Examples:
        >>> add_embeddings("technical_decisions", ["decision_name", "rationale"])
        {"success": True, "processed": 15, "model": "all-MiniLM-L6-v2", "embedding_dimension": 384}

    FastMCP Tool Info:
        - Automatically creates embedding column if it doesn't exist
        - Combines multiple text columns into single embedding
        - Only processes rows that don't already have embeddings
        - Uses efficient batch processing for large datasets
        - Supports various sentence-transformer models for different use cases
    """
    return add_embeddings_impl(table_name, text_columns, embedding_column, model_name)


@mcp.tool
@catch_errors
def auto_semantic_search(
    query: str,
    tables: Optional[List[str]] = None,
    similarity_threshold: float = 0.5,
    limit: int = 10,
    model_name: str = "all-MiniLM-L6-v2",
) -> ToolResponse:
    """
    🚀 **ZERO-SETUP SEMANTIC SEARCH** - Just search, embeddings are handled automatically!

    Find content using natural language semantic similarity. If embeddings don't exist,
    they will be automatically generated for text columns. This is the easiest way to
    do semantic search - no manual setup required!

    Args:
        query (str): Natural language search query
        tables (Optional[List[str]]): Specific tables to search (default: all tables)
        similarity_threshold (float): Minimum similarity score (0.0-1.0, default: 0.5)
        limit (int): Maximum number of results to return (default: 10)
        model_name (str): Model to use for embeddings (default: "all-MiniLM-L6-v2")

    Returns:
        ToolResponse: On success: {"success": True, "results": List[...], "auto_embedded_tables": List[str]}
                     On error: {"success": False, "error": str, "category": str, "details": dict}

    Examples:
        >>> auto_semantic_search("API design patterns")
        {"success": True, "results": [
            {"table_name": "technical_decisions", "similarity_score": 0.87, "decision_name": "REST API Structure", ...}
        ], "auto_embedded_tables": ["technical_decisions"]}

        >>> auto_semantic_search("machine learning concepts")
        # Finds content about "ML", "AI", "neural networks", etc.
        # Automatically creates embeddings if they don't exist!

    FastMCP Tool Info:
        - **COMPLETELY AUTOMATIC**: No manual embedding setup required
        - Auto-detects text columns and creates embeddings as needed
        - Works across multiple tables simultaneously
        - Finds conceptually similar content regardless of exact wording
        - Returns relevance scores for ranking results
        - Supports fuzzy matching and concept discovery
        - Perfect for agents - just search and it works!
    """
    return auto_semantic_search_impl(
        query, tables, similarity_threshold, limit, model_name
    )


@mcp.tool
@catch_errors
def auto_smart_search(
    query: str,
    tables: Optional[List[str]] = None,
    semantic_weight: float = 0.7,
    text_weight: float = 0.3,
    limit: int = 10,
    model_name: str = "all-MiniLM-L6-v2",
) -> ToolResponse:
    """
    🚀 **ZERO-SETUP HYBRID SEARCH** - Best of both worlds with automatic embedding!

    Intelligent hybrid search combining semantic understanding with keyword matching.
    Automatically generates embeddings for text columns when needed. This is the
    ultimate search tool - no manual setup required!

    Args:
        query (str): Search query (natural language or keywords)
        tables (Optional[List[str]]): Tables to search (default: all)
        semantic_weight (float): Weight for semantic similarity (0.0-1.0, default: 0.7)
        text_weight (float): Weight for keyword matching (0.0-1.0, default: 0.3)
        limit (int): Maximum results (default: 10)
        model_name (str): Semantic model to use (default: "all-MiniLM-L6-v2")

    Returns:
        ToolResponse: On success: {"success": True, "results": List[...], "search_type": "auto_hybrid"}
                     On error: {"success": False, "error": str, "category": str, "details": dict}

    Examples:
        >>> auto_smart_search("user authentication security")
        {"success": True, "results": [
            {"combined_score": 0.89, "semantic_score": 0.92, "text_score": 0.82, ...}
        ], "search_type": "auto_hybrid", "auto_embedded_tables": ["user_data"]}

    FastMCP Tool Info:
        - **COMPLETELY AUTOMATIC**: No manual embedding setup required
        - Automatically balances semantic and keyword search
        - Auto-detects text columns and creates embeddings as needed
        - Provides separate scores for transparency
        - Falls back gracefully if semantic search unavailable
        - Optimal for both exploratory and precise searches
        - Perfect for agents - ultimate search tool that just works!
    """
    return auto_smart_search_impl(
        query, tables, semantic_weight, text_weight, limit, model_name
    )


@mcp.tool
@catch_errors
def embedding_stats(
    table_name: str,
    embedding_column: str = "embedding",
) -> ToolResponse:
    """
    Get statistics about semantic search readiness for a table.

    Check which content has embeddings and can be searched semantically.

    Args:
        table_name (str): Table to analyze
        embedding_column (str): Embedding column to check (default: "embedding")

    Returns:
        ToolResponse: On success: {"success": True, "coverage_percent": float, "total_rows": int}
                     On error: {"success": False, "error": str, "category": str, "details": dict}

    Examples:
        >>> embedding_stats("technical_decisions")
        {"success": True, "total_rows": 25, "embedded_rows": 25, "coverage_percent": 100.0,
         "embedding_dimensions": 384}

    FastMCP Tool Info:
        - Shows how much content is ready for semantic search
        - Helps identify tables that need embedding generation
        - Provides embedding dimension info for debugging
        - Useful for monitoring semantic search capabilities
    """
    return embedding_stats_impl(table_name, embedding_column)


@mcp.tool
@catch_errors
def semantic_search(
    query: str,
    tables: Optional[List[str]] = None,
    similarity_threshold: float = 0.5,
    limit: int = 10,
    model_name: str = "all-MiniLM-L6-v2",
) -> ToolResponse:
    """
    ⚠️  **ADVANCED TOOL** - Most agents should use auto_smart_search() instead!

    Find content using natural language semantic similarity rather than exact keyword matching.

    **RECOMMENDATION**: Use auto_smart_search() for the same functionality with automatic setup.
    This tool requires manual embedding setup via add_embeddings() first.

    This enables intelligent knowledge discovery - find related concepts even when
    they use different terminology or phrasing.

    Args:
        query (str): Natural language search query
        tables (Optional[List[str]]): Specific tables to search (default: all tables with embeddings)
        similarity_threshold (float): Minimum similarity score (0.0-1.0, default: 0.5)
        limit (int): Maximum number of results to return (default: 10)
        model_name (str): Model to use for query embedding (default: "all-MiniLM-L6-v2")

    Returns:
        ToolResponse: On success: {"success": True, "results": List[...], "total_results": int}
                     On error: {"success": False, "error": str, "category": str, "details": dict}

    Examples:
        >>> semantic_search("API design patterns")
        {"success": True, "results": [
            {"table_name": "technical_decisions", "similarity_score": 0.87, "decision_name": "REST API Structure", ...},
            {"table_name": "project_structure", "similarity_score": 0.72, "component": "API Gateway", ...}
        ]}

        >>> semantic_search("machine learning", tables=["technical_decisions"], similarity_threshold=0.7)
        # Finds content about "ML", "AI", "neural networks", etc.

    FastMCP Tool Info:
        - Works across multiple tables simultaneously
        - Finds conceptually similar content regardless of exact wording
        - Returns relevance scores for ranking results
        - Supports fuzzy matching and concept discovery
        - Much more powerful than keyword-based search for knowledge discovery
    """
    return _semantic_search_impl(query, tables, similarity_threshold, limit, model_name)


@mcp.tool
@catch_errors
def smart_search(
    query: str,
    tables: Optional[List[str]] = None,
    semantic_weight: float = 0.7,
    text_weight: float = 0.3,
    limit: int = 10,
    model_name: str = "all-MiniLM-L6-v2",
) -> ToolResponse:
    """
    ⚠️  **ADVANCED TOOL** - Most agents should use auto_smart_search() instead!

    Intelligent hybrid search combining semantic understanding with keyword matching.

    **RECOMMENDATION**: Use auto_smart_search() for the same functionality with automatic setup.
    This tool requires manual embedding setup via add_embeddings() first.

    Provides the best of both worlds - semantic similarity for concept discovery
    plus exact text matching for precise searches.

    Args:
        query (str): Search query (natural language or keywords)
        tables (Optional[List[str]]): Tables to search (default: all)
        semantic_weight (float): Weight for semantic similarity (0.0-1.0, default: 0.7)
        text_weight (float): Weight for keyword matching (0.0-1.0, default: 0.3)
        limit (int): Maximum results (default: 10)
        model_name (str): Semantic model to use (default: "all-MiniLM-L6-v2")

    Returns:
        ToolResponse: On success: {"success": True, "results": List[...], "search_type": "hybrid"}
                     On error: {"success": False, "error": str, "category": str, "details": dict}

    Examples:
        >>> smart_search("user authentication security")
        {"success": True, "results": [
            {"combined_score": 0.89, "semantic_score": 0.92, "text_score": 0.82, ...},
            {"combined_score": 0.76, "semantic_score": 0.71, "text_score": 0.85, ...}
        ], "search_type": "hybrid"}

    FastMCP Tool Info:
        - Automatically balances semantic and keyword search
        - Provides separate scores for transparency
        - Falls back gracefully if semantic search unavailable
        - Optimal for both exploratory and precise searches
        - Perfect for agents - ultimate search tool that just works!
    """
    return _smart_search_impl(
        query, tables, semantic_weight, text_weight, limit, model_name
    )


@mcp.tool
@catch_errors
def find_related(
    table_name: str,
    row_id: int,
    similarity_threshold: float = 0.5,
    limit: int = 5,
    model_name: str = "all-MiniLM-L6-v2",
) -> ToolResponse:
    """
    Find content related to a specific row by semantic similarity.

    Discover connections and related information that might not be obvious
    from direct references or tags.

    Args:
        table_name (str): Table containing the reference row
        row_id (int): ID of the row to find related content for
        similarity_threshold (float): Minimum similarity score (default: 0.5)
        limit (int): Maximum number of related items to return (default: 5)
        model_name (str): Model for similarity comparison (default: "all-MiniLM-L6-v2")

    Returns:
        ToolResponse: On success: {"success": True, "results": List[...], "target_row": Dict}
                     On error: {"success": False, "error": str, "category": str, "details": dict}

    Examples:
        >>> find_related("technical_decisions", 5)
        {"success": True, "results": [
            {"id": 12, "similarity_score": 0.84, "decision_name": "Related Architecture Choice", ...},
            {"id": 3, "similarity_score": 0.71, "decision_name": "Similar Technology Decision", ...}
        ], "target_row": {"id": 5, "decision_name": "API Framework Selection", ...}}

    FastMCP Tool Info:
        - Helps discover hidden relationships between data
        - Useful for finding similar decisions, related problems, or connected concepts
        - Can reveal patterns and themes across your knowledge base
        - Enables serendipitous discovery of relevant information
    """
    return _find_related_impl(
        table_name, row_id, similarity_threshold, limit, model_name
    )


# --- Advanced Discovery Tools for SQLite Memory Bank ---


@mcp.tool
@catch_errors
def intelligent_discovery(
    discovery_goal: str = "understand_content",
    focus_area: Optional[str] = None,
    depth: str = "moderate",
    agent_id: Optional[str] = None,
) -> ToolResponse:
    """
    🧠 **INTELLIGENT DISCOVERY** - AI-guided exploration of your memory bank!

    Orchestrates multiple discovery tools based on your exploration goals.
    Provides step-by-step guidance and actionable insights tailored to your needs.

    Args:
        discovery_goal (str): What you want to achieve
            - "understand_content": Learn what data is available and how it's organized
            - "find_patterns": Discover themes, relationships, and content patterns
            - "explore_structure": Understand database schema and organization
            - "assess_quality": Evaluate content quality and completeness
            - "prepare_search": Get ready for effective content searching
        focus_area (Optional[str]): Specific table or topic to focus on (default: all)
        depth (str): How thorough the discovery should be
            - "quick": Fast overview with key insights
            - "moderate": Balanced analysis with actionable recommendations
            - "comprehensive": Deep dive with detailed analysis
        agent_id (Optional[str]): Agent identifier for learning discovery patterns

    Returns:
        ToolResponse: On success: {"success": True, "discovery": Dict, "next_steps": List}
                     On error: {"success": False, "error": str, "category": str, "details": dict}

    Examples:
        >>> intelligent_discovery("understand_content")
        {"success": True, "discovery": {
            "overview": {"total_tables": 5, "total_rows": 234},
            "content_summary": {...},
            "recommendations": [...]
        }, "next_steps": ["Use auto_smart_search() for specific queries"]}

    FastMCP Tool Info:
        - **COMPLETELY AUTOMATED**: No manual tool chaining required
        - **GOAL-ORIENTED**: Tailored discovery based on your specific objectives
        - **ACTIONABLE INSIGHTS**: Always includes concrete next steps
        - **LEARNING**: Improves recommendations based on usage patterns
        - **PERFECT FOR AGENTS**: Single tool that orchestrates complex discovery workflows
    """
    return intelligent_discovery_impl(discovery_goal, focus_area, depth, agent_id)


@mcp.tool
@catch_errors
def discovery_templates(
    template_type: str = "first_time_exploration", customize_for: Optional[str] = None
) -> ToolResponse:
    """
    📋 **DISCOVERY TEMPLATES** - Pre-built exploration workflows for common scenarios!

    Provides step-by-step discovery templates optimized for specific agent use cases.
    Each template includes the exact sequence of tools to call and what to look for.

    Args:
        template_type (str): Type of discovery template to provide
            - "first_time_exploration": Complete workflow for new agents
            - "content_audit": Systematic content quality review
            - "search_optimization": Prepare memory bank for optimal searching
            - "relationship_mapping": Discover connections between data
            - "problem_solving": Find information to solve specific problems
            - "knowledge_extraction": Extract insights from stored knowledge
        customize_for (Optional[str]): Customize template for specific domain/topic

    Returns:
        ToolResponse: {"success": True, "template": Dict, "workflow": List}

    Examples:
        >>> discovery_templates("first_time_exploration")
        {"success": True, "template": {
            "name": "First Time Exploration",
            "description": "Complete discovery workflow for new agents",
            "workflow": [
                {"step": 1, "tool": "intelligent_discovery", "params": {...}},
                {"step": 2, "tool": "explore_tables", "params": {...}}
            ]
        }}

    FastMCP Tool Info:
        - **PROVEN WORKFLOWS**: Battle-tested discovery sequences
        - **STEP-BY-STEP GUIDANCE**: Exact tools and parameters to use
        - **CUSTOMIZABLE**: Adapt templates to your specific needs
        - **LEARNING-OPTIMIZED**: Based on successful discovery patterns
    """
    return discovery_templates_impl(template_type, customize_for)


@mcp.tool
@catch_errors
def discover_relationships(
    table_name: Optional[str] = None,
    relationship_types: List[str] = [
        "foreign_keys",
        "semantic_similarity",
        "temporal_patterns",
    ],
    similarity_threshold: float = 0.6,
) -> ToolResponse:
    """
    🔗 **RELATIONSHIP DISCOVERY** - Find hidden connections in your data!

    Automatically discovers relationships between tables and content areas using
    both structural analysis and semantic similarity to reveal data connections.

    Args:
        table_name (Optional[str]): Focus on relationships for specific table (default: all)
        relationship_types (List[str]): Types of relationships to discover
            - "foreign_keys": Structural relationships via foreign keys
            - "semantic_similarity": Content-based relationships via semantic analysis
            - "temporal_patterns": Time-based relationships and patterns
            - "naming_patterns": Relationships based on naming conventions
        similarity_threshold (float): Minimum similarity for semantic relationships (0.0-1.0)

    Returns:
        ToolResponse: {"success": True, "relationships": Dict, "insights": List}

    Examples:
        >>> discover_relationships("users")
        {"success": True, "relationships": {
            "users": {
                "foreign_key_refs": ["posts.user_id", "comments.user_id"],
                "semantic_similar": [{"table": "profiles", "similarity": 0.8}],
                "temporal_related": ["user_sessions"]
            }
        }}

    FastMCP Tool Info:
        - **AUTOMATIC DETECTION**: Finds relationships you might not notice manually
        - **MULTIPLE METHODS**: Combines structural, semantic, and temporal analysis
        - **ACTIONABLE INSIGHTS**: Suggests how to leverage discovered relationships
        - **PERFECT FOR EXPLORATION**: Reveals hidden data organization patterns
    """
    return discover_relationships_impl(
        table_name, relationship_types, similarity_threshold
    )


# Export the FastMCP app for use in other modules and server runners
app = mcp

# Document the app for better discovery
app.__doc__ = """
SQLite Memory Bank for Copilot/AI Agents

A dynamic, agent-friendly SQLite memory bank with explicit, type-safe tools.
All tools are designed for explicit, discoverable use by LLMs and FastMCP clients.

Available tools:
- create_table: Create a new table with a custom schema
- drop_table: Drop (delete) a table
- rename_table: Rename a table
- list_tables: List all tables in the memory bank
- describe_table: Get schema details for a table
- list_all_columns: List all columns for all tables
- create_row: Insert a row into any table
- read_rows: Read rows from any table (with optional filtering)
- update_rows: Update rows from any table (with optional filtering)
- delete_rows: Delete rows from any table (with optional filtering)
- run_select_query: Run a safe SELECT query (no arbitrary SQL)
- search_content: Perform full-text search across table content
- explore_tables: Discover table structures and content for better searchability
- auto_semantic_search: Zero-setup semantic search with automatic embeddings
- auto_smart_search: Zero-setup hybrid search combining semantic and keyword search
- add_embeddings: Manual embedding generation for advanced users
- embedding_stats: Check semantic search readiness
"""


# Public API - these functions are available for direct Python use and as MCP tools
__all__ = [
    "app",
    "mcp",
    "create_table",
    "drop_table",
    "rename_table",
    "list_tables",
    "describe_table",
    "list_all_columns",
    "create_row",
    "upsert_memory",
    "read_rows",
    "update_rows",
    "delete_rows",
    "run_select_query",
    "search_content",
    "explore_tables",
    "add_embeddings",
    "auto_semantic_search",
    "auto_smart_search",
    "embedding_stats",
    "intelligent_discovery",
    "discovery_templates",
    "discover_relationships",
]


def mcp_server():
    """Entry point for MCP stdio server (for uvx and package installations)."""
    # Configure logging for MCP server
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Log startup information
    logging.info(f"Starting SQLite Memory Bank MCP server with database at {DB_PATH}")

    # Run the FastMCP app in stdio mode
    app.run()


def main():
    """Alternative entry point for HTTP server mode (development/testing only)."""
    import uvicorn
    import argparse

    parser = argparse.ArgumentParser(
        description="Run MCP SQLite Memory Bank Server in HTTP mode"
    )
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--db-path", help="Path to SQLite database file")
    parser.add_argument(
        "--reload", action="store_true", help="Enable auto-reload for development"
    )

    args = parser.parse_args()

    # Set database path if provided
    if args.db_path:
        global DB_PATH
        DB_PATH = args.db_path
        os.environ["DB_PATH"] = args.db_path

    print(
        f"Starting MCP SQLite Memory Bank server in HTTP mode on {args.host}:{args.port}"
    )
    print(f"Database path: {DB_PATH}")
    print("Available at: http://localhost:8000/docs")

    uvicorn.run(
        "mcp_sqlite_memory_bank.server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Log startup information
    logging.info(f"Starting SQLite Memory Bank with database at {DB_PATH}")

    # Run the FastMCP app in stdio mode for MCP clients
    app.run(transport="stdio")


# Compatibility aliases for tests that expect _impl functions
# Import modules already imported above for tool implementations

# Basic CRUD operation aliases
_create_row_impl = basic.create_row
_read_rows_impl = basic.read_rows
_update_rows_impl = basic.update_rows
_delete_rows_impl = basic.delete_rows
_list_tables_impl = basic.list_tables
_describe_table_impl = basic.describe_table
_drop_table_impl = basic.drop_table
_create_table_impl = basic.create_table

# Search operation aliases
_search_content_impl = search.search_content
_explore_tables_impl = search.explore_tables
_add_embeddings_impl = search.add_embeddings
_semantic_search_impl = search.semantic_search
_smart_search_impl = search.smart_search
_find_related_impl = search.find_related
_auto_semantic_search_impl = search.auto_semantic_search
_auto_smart_search_impl = search.auto_smart_search

# Analytics operation aliases
_analyze_memory_patterns_impl = analytics.analyze_memory_patterns
_get_content_health_score_impl = analytics.get_content_health_score

# Discovery operation aliases
_intelligent_discovery_impl = intelligent_discovery_impl
_discovery_templates_impl = discovery_templates_impl
_discover_relationships_impl = discover_relationships_impl


@mcp.tool
@catch_errors
def batch_create_memories(
    table_name: str,
    data_list: List[Dict[str, Any]],
    match_columns: Optional[List[str]] = None,
    use_upsert: bool = True,
) -> ToolResponse:
    """
    🚀 **BATCH MEMORY CREATION** - Efficiently add multiple memories at once!

    Create multiple memory records in a single operation with optional duplicate prevention.
    Much faster than creating records one by one.

    Args:
        table_name (str): Table to insert records into
        data_list (List[Dict[str, Any]]): List of memory records to create
        match_columns (Optional[List[str]]): Columns to use for duplicate detection (if use_upsert=True)
        use_upsert (bool): Whether to use upsert logic to prevent duplicates (default: True)

    Returns:
        ToolResponse: On success: {"success": True, "created": int, "updated": int, "failed": int}
                     On error: {"success": False, "error": str, "category": str, "details": dict}

    Examples:
        >>> batch_create_memories('technical_decisions', [
        ...     {'decision_name': 'API Design', 'chosen_approach': 'REST'},
        ...     {'decision_name': 'Database Choice', 'chosen_approach': 'SQLite'},
        ...     {'decision_name': 'Frontend Framework', 'chosen_approach': 'React'}
        ... ], match_columns=['decision_name'])
        {"success": True, "created": 2, "updated": 1, "failed": 0, "total_processed": 3}

    FastMCP Tool Info:
        - **EFFICIENT**: Process multiple records in one operation
        - **SMART DEDUPLICATION**: Optional upsert logic prevents duplicates
        - **DETAILED FEEDBACK**: Returns counts for created, updated, and failed records
        - **PARTIAL SUCCESS**: Continues processing even if some records fail
        - **PERFECT FOR BULK IMPORTS**: Ideal for importing knowledge bases or datasets
    """
    return basic.batch_create_memories(table_name, data_list, match_columns, use_upsert)


@mcp.tool
@catch_errors
def batch_delete_memories(
    table_name: str, where_conditions: List[Dict[str, Any]], match_all: bool = False
) -> ToolResponse:
    """
    🗑️ **BATCH MEMORY DELETION** - Efficiently delete multiple memories at once!

    Delete multiple memory records in a single operation with flexible matching conditions.
    Much faster than deleting records one by one.

    Args:
        table_name (str): Table to delete records from
        where_conditions (List[Dict[str, Any]]): List of WHERE conditions for deletion
        match_all (bool): If True, delete records matching ALL conditions; if False, delete records matching ANY condition (default: False)

    Returns:
        ToolResponse: On success: {"success": True, "deleted": int, "failed": int}
                     On error: {"success": False, "error": str, "category": str, "details": dict}

    Examples:
        >>> batch_delete_memories('technical_decisions', [
        ...     {'decision_name': 'Old Decision 1'},
        ...     {'decision_name': 'Old Decision 2'},
        ...     {'id': 42}
        ... ])
        {"success": True, "deleted": 3, "failed": 0, "total_conditions": 3}

        >>> batch_delete_memories('notes', [
        ...     {'category': 'temp', 'created_date': '2024-01-01'}
        ... ], match_all=True)
        {"success": True, "deleted": 15, "failed": 0}  # Deletes notes that are BOTH temp AND from that date

    FastMCP Tool Info:
        - **EFFICIENT**: Process multiple deletions in one operation
        - **FLEXIBLE MATCHING**: Support both OR logic (any condition) and AND logic (all conditions)
        - **DETAILED FEEDBACK**: Returns counts and per-condition results
        - **PARTIAL SUCCESS**: Continues processing even if some deletions fail
        - **SAFE**: Uses parameterized queries to prevent SQL injection
    """
    return basic.batch_delete_memories(table_name, where_conditions, match_all)
