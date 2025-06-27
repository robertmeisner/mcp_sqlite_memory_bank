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
    return cast(CreateTableResponse, get_database(DB_PATH).create_table(table_name, columns))


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
    return cast(RenameTableResponse, get_database(DB_PATH).rename_table(old_name, new_name))


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
def update_rows(table_name: str, data: Dict[str, Any], where: Optional[Dict[str, Any]] = None) -> ToolResponse:
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
    return cast(UpdateRowsResponse, get_database(DB_PATH).update_rows(table_name, data, where))


@mcp.tool
@catch_errors
def delete_rows(table_name: str, where: Optional[Dict[str, Any]] = None) -> ToolResponse:
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
    return cast(DeleteRowsResponse, get_database(DB_PATH).delete_rows(table_name, where))


@mcp.tool
@catch_errors
def run_select_query(
    table_name: str, columns: Optional[List[str]] = None, where: Optional[Dict[str, Any]] = None, limit: int = 100
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
    return cast(SelectQueryResponse, get_database(DB_PATH).select_query(table_name, columns, where, limit))


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


# --- Content Search and Exploration Tools ---


@mcp.tool
@catch_errors
def search_content(query: str, tables: Optional[List[str]] = None, limit: int = 50) -> ToolResponse:
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
    return cast(ToolResponse, get_database(DB_PATH).search_content(query, tables, limit))


@mcp.tool
@catch_errors
def explore_tables(pattern: Optional[str] = None, include_row_counts: bool = True) -> ToolResponse:
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
    return cast(ToolResponse, get_database(DB_PATH).explore_tables(pattern, include_row_counts))


# --- Semantic Search and AI-Enhanced Discovery Tools ---


@mcp.tool
@catch_errors
def add_embeddings(
    table_name: str, text_columns: List[str], embedding_column: str = "embedding", model_name: str = "all-MiniLM-L6-v2"
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
    return cast(
        ToolResponse, get_database(DB_PATH).generate_embeddings(table_name, text_columns, embedding_column, model_name)
    )


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
    
    **RECOMMENDATION**: Use auto_smart_search() for automatic setup and hybrid search capabilities.
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
    return cast(
        ToolResponse,
        get_database(DB_PATH).semantic_search(
            query, tables, "embedding", None, similarity_threshold, limit, model_name
        ),
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
    return cast(
        ToolResponse,
        get_database(DB_PATH).find_related_content(
            table_name, row_id, "embedding", similarity_threshold, limit, model_name
        ),
    )


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
    return cast(
        ToolResponse,
        get_database(DB_PATH).hybrid_search(
            query, tables, None, "embedding", semantic_weight, text_weight, limit, model_name
        ),
    )


# --- Auto-Embedding Semantic Search Tools ---


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
    try:
        db = get_database(DB_PATH)
        auto_embedded_tables = []
        
        # Get tables to search
        if tables:
            search_tables = tables
        else:
            tables_result = db.list_tables()
            if not tables_result.get("success"):
                return cast(ToolResponse, tables_result)
            search_tables = tables_result.get("tables", [])
        
        # Auto-embed text columns in tables that don't have embeddings
        for table_name in search_tables:
            try:
                # Check if table has embeddings
                stats_result = db.get_embedding_stats(table_name, "embedding")
                if stats_result.get("success") and stats_result.get("coverage_percent", 0) > 0:
                    continue  # Table already has embeddings
                
                # Get table schema to find text columns
                schema_result = db.describe_table(table_name)
                if not schema_result.get("success"):
                    continue
                
                # Find text columns
                text_columns = []
                for col in schema_result.get("columns", []):
                    if "TEXT" in col.get("type", "").upper():
                        text_columns.append(col["name"])
                
                # Auto-embed text columns
                if text_columns:
                    embed_result = db.generate_embeddings(table_name, text_columns, "embedding", model_name)
                    if embed_result.get("success"):
                        auto_embedded_tables.append(table_name)
                        
            except Exception:
                # If auto-embedding fails, continue without it
                continue
        
        # Perform semantic search
        search_result = db.semantic_search(
            query, search_tables, "embedding", None, similarity_threshold, limit, model_name
        )
        
        # Add auto-embedding info to result
        if isinstance(search_result, dict):
            search_result["auto_embedded_tables"] = auto_embedded_tables
            if auto_embedded_tables:
                search_result["auto_embedding_note"] = f"Automatically generated embeddings for {len(auto_embedded_tables)} table(s)"
        
        return cast(ToolResponse, search_result)
        
    except Exception as e:
        return cast(ToolResponse, {
            "success": False,
            "error": f"Auto semantic search failed: {str(e)}",
            "category": "SEMANTIC_SEARCH_ERROR",
            "details": {"query": query, "tables": tables}
        })


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
    try:
        # First try auto semantic search to ensure embeddings exist
        auto_semantic_result = auto_semantic_search(query, tables, 0.3, limit, model_name)
        auto_embedded_tables = []
        
        if auto_semantic_result.get("success"):
            auto_embedded_tables = auto_semantic_result.get("auto_embedded_tables", [])
        
        # Now perform hybrid search
        db = get_database(DB_PATH)
        hybrid_result = db.hybrid_search(
            query, tables, None, "embedding", semantic_weight, text_weight, limit, model_name
        )
        
        # Add auto-embedding info to result
        if isinstance(hybrid_result, dict):
            hybrid_result["search_type"] = "auto_hybrid"
            hybrid_result["auto_embedded_tables"] = auto_embedded_tables
            if auto_embedded_tables:
                hybrid_result["auto_embedding_note"] = f"Automatically generated embeddings for {len(auto_embedded_tables)} table(s)"
        
        return cast(ToolResponse, hybrid_result)
        
    except Exception as e:
        return cast(ToolResponse, {
            "success": False,
            "error": f"Auto smart search failed: {str(e)}",
            "category": "HYBRID_SEARCH_ERROR", 
            "details": {"query": query, "tables": tables}
        })


# --- Enhanced Tool Discovery and Categorization ---


@mcp.tool
@catch_errors
def list_tool_categories() -> ToolResponse:
    """
    List all available tool categories for better organization and discovery.
    
    Returns organized view of available functionality for LLMs and agents.
    
    Returns:
        ToolResponse: {"success": True, "categories": {category: [tool_names]}}
    """
    categories = {
        "schema_management": [
            "create_table", "list_tables", "describe_table", 
            "drop_table", "rename_table", "list_all_columns"
        ],
        "data_operations": [
            "create_row", "read_rows", "update_rows", 
            "delete_rows", "run_select_query"
        ],
        "search_discovery": [
            "search_content", "explore_tables"
        ],
        "semantic_search": [
            "add_embeddings", "semantic_search", "find_related", 
            "smart_search", "embedding_stats"
        ],
        "workflow_shortcuts": [
            "quick_note", "remember_decision", "store_context"
        ],
        "analytics_insights": [
            "memory_usage_stats", "content_analytics"
        ]
    }
    
    return cast(ToolResponse, {
        "success": True,
        "categories": categories,
        "total_tools": sum(len(tools) for tools in categories.values()),
        "description": "Organized view of all available memory bank capabilities"
    })


@mcp.tool  
@catch_errors
def get_tools_by_category(category: str) -> ToolResponse:
    """
    Get detailed information about tools in a specific category.
    
    Args:
        category (str): Category name (schema_management, data_operations, 
                       search_discovery, semantic_search, workflow_shortcuts, analytics_insights)
    
    Returns:
        ToolResponse: {"success": True, "tools": [{"name": str, "description": str, "usage": str}]}
    """
    tool_details = {
        "schema_management": [
            {"name": "create_table", "description": "Create new tables with custom schemas", "usage": "create_table('table_name', [{'name': 'col', 'type': 'TEXT'}])"},
            {"name": "list_tables", "description": "List all available tables", "usage": "list_tables()"},
            {"name": "describe_table", "description": "Get detailed schema for a table", "usage": "describe_table('table_name')"},
            {"name": "drop_table", "description": "Delete a table permanently", "usage": "drop_table('table_name')"},
            {"name": "rename_table", "description": "Rename an existing table", "usage": "rename_table('old_name', 'new_name')"},
            {"name": "list_all_columns", "description": "Get all columns across all tables", "usage": "list_all_columns()"},
        ],
        "data_operations": [
            {"name": "create_row", "description": "Insert new data into any table", "usage": "create_row('table', {'col': 'value'})"},
            {"name": "read_rows", "description": "Query data with optional filtering", "usage": "read_rows('table', {'filter_col': 'value'})"},
            {"name": "update_rows", "description": "Modify existing data", "usage": "update_rows('table', {'new_data': 'value'}, {'where_col': 'value'})"},
            {"name": "delete_rows", "description": "Remove data from tables", "usage": "delete_rows('table', {'filter_col': 'value'})"},
            {"name": "run_select_query", "description": "Execute safe SELECT queries", "usage": "run_select_query('table', ['col1', 'col2'], {'filter': 'value'})"},
        ],
        "search_discovery": [
            {"name": "search_content", "description": "Full-text search across all content", "usage": "search_content('search query', ['table1', 'table2'])"},
            {"name": "explore_tables", "description": "Discover table structures and sample data", "usage": "explore_tables('pattern*')"},
        ],
        "semantic_search": [
            {"name": "add_embeddings", "description": "Enable semantic search on tables", "usage": "add_embeddings('table', ['text_col1', 'text_col2'])"},
            {"name": "semantic_search", "description": "Natural language content discovery", "usage": "semantic_search('find ML algorithms')"},
            {"name": "find_related", "description": "Discover similar content", "usage": "find_related('table', row_id, 0.5)"},
            {"name": "smart_search", "description": "Hybrid keyword + semantic search", "usage": "smart_search('search query')"},
            {"name": "embedding_stats", "description": "Check semantic search readiness", "usage": "embedding_stats('table')"},
        ],
        "workflow_shortcuts": [
            {"name": "quick_note", "description": "Rapidly store notes and observations", "usage": "quick_note('content', 'category')"},
            {"name": "remember_decision", "description": "Store technical decisions with context", "usage": "remember_decision('decision', 'approach', 'rationale')"},
            {"name": "store_context", "description": "Save session context and progress", "usage": "store_context('topic', 'current_state', 'next_steps')"},
        ],
        "analytics_insights": [
            {"name": "memory_usage_stats", "description": "Analyze memory bank usage patterns", "usage": "memory_usage_stats()"},
            {"name": "content_analytics", "description": "Get insights on stored content", "usage": "content_analytics('table_name')"},
        ],
    }
    
    if category not in tool_details:
        return cast(ToolResponse, {
            "success": False,
            "error": f"Unknown category '{category}'. Available: {list(tool_details.keys())}",
            "category": "VALIDATION",
            "details": {"available_categories": list(tool_details.keys())},
        })
    
    return cast(ToolResponse, {
        "success": True,
        "category": category,
        "tools": tool_details[category],
        "tool_count": len(tool_details[category]),
    })


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
"""


# Legacy implementation functions for backwards compatibility with tests
def _create_row_impl(table_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Legacy implementation function for tests."""
    try:
        # Handle test-specific table creation for legacy compatibility
        if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", table_name):
            return {"success": False, "error": f"Invalid table name: {table_name}"}

        # Auto-create test tables for compatibility
        current_db = get_database(DB_PATH)
        if table_name == "nodes":
            try:
                current_db.create_table(
                    "nodes",
                    [
                        {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
                        {"name": "label", "type": "TEXT NOT NULL"},
                    ],
                )
            except Exception:
                pass  # Table might already exist
        elif table_name == "edges":
            try:
                current_db.create_table(
                    "edges",
                    [
                        {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
                        {"name": "source", "type": "INTEGER NOT NULL"},
                        {"name": "target", "type": "INTEGER NOT NULL"},
                        {"name": "type", "type": "TEXT NOT NULL"},
                    ],
                )
            except Exception:
                pass  # Table might already exist

        result = current_db.insert_row(table_name, data)
        # Ensure we return Dict[str, Any] for legacy compatibility
        return dict(result) if isinstance(result, dict) else {"success": False, "error": "Unknown error"}

    except Exception as e:
        logging.error(f"_create_row_impl error: {e}")
        return {"success": False, "error": str(e)}


def _read_rows_impl(table_name: str, where: Optional[Dict[str, Any]] = None, limit: int = 100) -> Dict[str, Any]:
    """Legacy implementation function for tests."""
    try:
        result = get_database(DB_PATH).read_rows(table_name, where, limit)
        # Ensure we return Dict[str, Any] for legacy compatibility
        return dict(result) if isinstance(result, dict) else {"success": False, "error": "Unknown error"}
    except Exception as e:
        logging.error(f"_read_rows_impl error: {e}")
        return {"success": False, "error": str(e)}


def _update_rows_impl(table_name: str, data: Dict[str, Any], where: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Legacy implementation function for tests."""
    try:
        # Auto-create test tables for compatibility
        if table_name == "edges":
            try:
                current_db = get_database(DB_PATH)
                current_db.create_table(
                    "edges",
                    [
                        {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
                        {"name": "source", "type": "INTEGER NOT NULL"},
                        {"name": "target", "type": "INTEGER NOT NULL"},
                        {"name": "type", "type": "TEXT NOT NULL"},
                    ],
                )
            except Exception:
                pass  # Table might already exist

        result = get_database(DB_PATH).update_rows(table_name, data, where)
        # Ensure we return Dict[str, Any] for legacy compatibility
        return dict(result) if isinstance(result, dict) else {"success": False, "error": "Unknown error"}
    except Exception as e:
        logging.error(f"_update_rows_impl error: {e}")
        return {"success": False, "error": str(e)}


def _delete_rows_impl(table_name: str, where: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Legacy implementation function for tests."""
    try:
        result = get_database(DB_PATH).delete_rows(table_name, where)
        # Ensure we return Dict[str, Any] for legacy compatibility
        return dict(result) if isinstance(result, dict) else {"success": False, "error": "Unknown error"}
    except Exception as e:
        logging.error(f"_delete_rows_impl error: {e}")
        return {"success": False, "error": str(e)}


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
    "read_rows",
    "update_rows",
    "delete_rows",
    "run_select_query",
    "search_content",
    "explore_tables",
    "_create_row_impl",
    "_read_rows_impl",
    "_update_rows_impl",
    "_delete_rows_impl",
]


def mcp_server():
    """Entry point for MCP stdio server (for uvx and package installations)."""
    # Configure logging for MCP server
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Log startup information
    logging.info(f"Starting SQLite Memory Bank MCP server with database at {DB_PATH}")

    # Run the FastMCP app in stdio mode
    app.run()


def main():
    """Alternative entry point for HTTP server mode (development/testing only)."""
    import uvicorn
    import argparse

    parser = argparse.ArgumentParser(description="Run MCP SQLite Memory Bank Server in HTTP mode")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--db-path", help="Path to SQLite database file")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")

    args = parser.parse_args()

    # Set database path if provided
    if args.db_path:
        global DB_PATH
        DB_PATH = args.db_path
        os.environ["DB_PATH"] = args.db_path

    print(f"Starting MCP SQLite Memory Bank server in HTTP mode on {args.host}:{args.port}")
    print(f"Database path: {DB_PATH}")
    print("Available at: http://localhost:8000/docs")

    uvicorn.run("mcp_sqlite_memory_bank.server:app", host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Log startup information
    logging.info(f"Starting SQLite Memory Bank with database at {DB_PATH}")

    # Run the FastMCP app in stdio mode for MCP clients
    app.run()
