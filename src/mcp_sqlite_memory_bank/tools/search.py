"""
Search tools module for SQLite Memory Bank.

This module contains all search-related MCP tools including content search,
semantic search, embedding management, and intelligent search capabilities.
"""

import logging
import traceback
from typing import List, Optional, cast

from ..database import get_database
from ..types import ToolResponse
from ..utils import catch_errors


def _auto_embed_tables(
    search_tables: List[str], model_name: str = "all-MiniLM-L6-v2"
) -> List[str]:
    """
    Auto-embed text columns in tables that don't have embeddings.

    Args:
        search_tables: List of table names to process
        model_name: Model to use for embedding generation

    Returns:
        List of table names that were successfully auto-embedded
    """
    from .. import server

    db = get_database(server.DB_PATH)
    auto_embedded_tables: List[str] = []

    for table_name in search_tables:
        try:
            # Check if table has embeddings
            stats_result = db.get_embedding_stats(table_name, "embedding")
            coverage_percent = stats_result.get("coverage_percent", 0)
            if (
                stats_result.get("success")
                and isinstance(coverage_percent, (int, float))
                and coverage_percent > 0
            ):
                continue  # Table already has embeddings

            # Get table schema to find text columns
            schema_result = db.describe_table(table_name)
            if not schema_result.get("success"):
                continue

            # Find text columns
            text_columns = []
            columns = schema_result.get("columns", [])
            if isinstance(columns, list):
                for col in columns:
                    if isinstance(col, dict) and "TEXT" in col.get("type", "").upper():
                        text_columns.append(col["name"])

            # Auto-embed text columns
            if text_columns:
                embed_result = db.generate_embeddings(
                    table_name, text_columns, "embedding", model_name
                )
                if embed_result.get("success"):
                    auto_embedded_tables.append(table_name)

        except Exception:
            # If auto-embedding fails, continue without it
            continue

    return auto_embedded_tables


def _get_search_tables(tables: Optional[List[str]]) -> List[str]:
    """
    Get tables to search - either provided list or all available tables.

    Args:
        tables: Optional list of specific tables to search

    Returns:
        List of table names to search
    """
    from .. import server

    if tables:
        return tables

    db = get_database(server.DB_PATH)
    tables_result = db.list_tables()
    if not tables_result.get("success"):
        return []

    all_tables = tables_result.get("tables", [])
    return all_tables if isinstance(all_tables, list) else []


@catch_errors
def search_content(
    query: str,
    tables: Optional[List[str]] = None,
    limit: int = 50,
) -> ToolResponse:
    """Perform full-text search across table content using natural language queries."""
    from .. import server

    return cast(
        ToolResponse, get_database(server.DB_PATH).search_content(query, tables, limit)
    )


@catch_errors
def explore_tables(
    pattern: Optional[str] = None,
    include_row_counts: bool = True,
) -> ToolResponse:
    """Explore and discover table structures and content for better searchability."""
    from .. import server

    return cast(
        ToolResponse,
        get_database(server.DB_PATH).explore_tables(pattern, include_row_counts),
    )


@catch_errors
def add_embeddings(
    table_name: str,
    text_columns: List[str],
    embedding_column: str = "embedding",
    model_name: str = "all-MiniLM-L6-v2",
) -> ToolResponse:
    """Generate and store vector embeddings for semantic search on table content."""
    from .. import server

    return cast(
        ToolResponse,
        get_database(server.DB_PATH).generate_embeddings(
            table_name, text_columns, embedding_column, model_name
        ),
    )


@catch_errors
def semantic_search(
    query: str,
    tables: Optional[List[str]] = None,
    similarity_threshold: float = 0.5,
    limit: int = 10,
    model_name: str = "all-MiniLM-L6-v2",
) -> ToolResponse:
    """Find content using natural language semantic similarity rather than exact keyword matching."""
    from .. import server

    return cast(
        ToolResponse,
        get_database(server.DB_PATH).semantic_search(
            query, tables, "embedding", None, similarity_threshold, limit, model_name
        ),
    )


@catch_errors
def find_related(
    table_name: str,
    row_id: int,
    similarity_threshold: float = 0.5,
    limit: int = 5,
    model_name: str = "all-MiniLM-L6-v2",
) -> ToolResponse:
    """Find content related to a specific row by semantic similarity."""
    from .. import server

    return cast(
        ToolResponse,
        get_database(server.DB_PATH).find_related_content(
            table_name, row_id, "embedding", similarity_threshold, limit, model_name
        ),
    )


@catch_errors
def smart_search(
    query: str,
    tables: Optional[List[str]] = None,
    semantic_weight: float = 0.7,
    text_weight: float = 0.3,
    limit: int = 10,
    model_name: str = "all-MiniLM-L6-v2",
) -> ToolResponse:
    """Intelligent hybrid search combining semantic understanding with keyword matching."""
    from .. import server

    return cast(
        ToolResponse,
        get_database(server.DB_PATH).hybrid_search(
            query,
            tables,
            None,
            "embedding",
            semantic_weight,
            text_weight,
            limit,
            model_name,
        ),
    )


@catch_errors
def embedding_stats(
    table_name: str,
    embedding_column: str = "embedding",
) -> ToolResponse:
    """Get statistics about semantic search readiness for a table."""
    from .. import server

    return cast(
        ToolResponse,
        get_database(server.DB_PATH).get_embedding_stats(table_name, embedding_column),
    )


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
        from .. import server

        # Get tables to search and auto-embed text columns
        search_tables = _get_search_tables(tables)
        if not search_tables:
            return cast(
                ToolResponse,
                {
                    "success": False,
                    "error": "No tables available for search",
                    "category": "TABLE_ERROR",
                },
            )

        auto_embedded_tables = _auto_embed_tables(search_tables, model_name)

        # Perform semantic search
        db = get_database(server.DB_PATH)
        search_result = db.semantic_search(
            query,
            search_tables,
            "embedding",
            None,
            similarity_threshold,
            limit,
            model_name,
        )

        # Add auto-embedding info to result
        if isinstance(search_result, dict):
            search_result["auto_embedded_tables"] = auto_embedded_tables
            if auto_embedded_tables:
                search_result["auto_embedding_note"] = (
                    f"Automatically generated embeddings for {
                        len(auto_embedded_tables)} table(s)")

        return cast(ToolResponse, search_result)

    except Exception as e:
        return cast(
            ToolResponse,
            {
                "success": False,
                "error": f"Auto semantic search failed: {str(e)}",
                "category": "SEMANTIC_SEARCH_ERROR",
                "details": {"query": query, "tables": tables},
            },
        )


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
        from .. import server

        # Get tables to search and auto-embed text columns
        search_tables = _get_search_tables(tables)
        if not search_tables:
            return cast(
                ToolResponse,
                {
                    "success": False,
                    "error": "No tables available for search",
                    "category": "TABLE_ERROR",
                },
            )

        auto_embedded_tables = _auto_embed_tables(search_tables, model_name)

        # Now perform hybrid search using the same pattern as smart_search
        try:
            hybrid_result = get_database(server.DB_PATH).hybrid_search(
                query,
                search_tables,
                None,
                "embedding",
                semantic_weight,
                text_weight,
                limit,
                model_name,
            )
        except Exception as search_error:
            # If hybrid search fails, fall back to regular content search
            logging.warning(
                f"Hybrid search failed, falling back to content search: {search_error}"
            )
            try:
                fallback_result = get_database(server.DB_PATH).search_content(
                    query, search_tables, limit
                )
                if fallback_result.get("success"):
                    # Create a new dictionary to avoid type issues
                    enhanced_fallback = dict(fallback_result)
                    enhanced_fallback["search_type"] = "text_fallback"
                    enhanced_fallback["auto_embedded_tables"] = auto_embedded_tables
                    enhanced_fallback["fallback_reason"] = str(search_error)
                    return cast(ToolResponse, enhanced_fallback)
            except Exception as fallback_error:
                return cast(
                    ToolResponse,
                    {
                        "success": False,
                        "error": f"Both hybrid and fallback search failed. Hybrid: {search_error}, Fallback: {fallback_error}",
                        "category": "HYBRID_SEARCH_ERROR",
                        "details": {
                            "query": query,
                            "tables": tables},
                    },
                )

            # If we get here, both searches failed
            return cast(
                ToolResponse,
                {
                    "success": False,
                    "error": f"Hybrid search failed: {search_error}",
                    "category": "HYBRID_SEARCH_ERROR",
                    "details": {"query": query, "tables": tables},
                },
            )

        # Add auto-embedding info to result
        if isinstance(hybrid_result, dict) and hybrid_result.get("success"):
            # Convert to mutable dict to add extra fields
            final_result = dict(hybrid_result)
            final_result["search_type"] = "auto_hybrid"
            final_result["auto_embedded_tables"] = auto_embedded_tables
            if auto_embedded_tables:
                final_result["auto_embedding_note"] = (
                    f"Automatically generated embeddings for {
                        len(auto_embedded_tables)} table(s)")
            return cast(ToolResponse, final_result)
        else:
            return cast(ToolResponse, hybrid_result)

    except Exception as e:
        # Add detailed error information for debugging
        error_details = {
            "query": query,
            "tables": tables,
            "error_type": type(e).__name__,
            "error_str": str(e),
            "traceback": traceback.format_exc(),
        }
        return cast(
            ToolResponse,
            {
                "success": False,
                "error": f"Auto smart search failed: {str(e)}",
                "category": "HYBRID_SEARCH_ERROR",
                "details": error_details,
            },
        )
