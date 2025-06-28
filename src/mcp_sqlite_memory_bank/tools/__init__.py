"""
Tools module for SQLite Memory Bank MCP server.

This module organizes the various MCP tools into logical categories:
- analytics: Content analysis and health assessment tools
- search: Intelligent search and discovery tools
- discovery: Advanced exploration and relationship discovery tools
- basic: Core CRUD operations and table management
"""

# Import all tools to make them available at the package level
from .analytics import (
    analyze_memory_patterns,
    get_content_health_score,
)
from .search import (
    search_content,
    explore_tables,
    add_embeddings,
    semantic_search,
    find_related,
    smart_search,
    embedding_stats,
    auto_semantic_search,
    auto_smart_search,
)
from .discovery import (
    intelligent_discovery,
    discovery_templates,
    discover_relationships,
)
from .basic import (
    create_table,
    list_tables,
    describe_table,
    drop_table,
    rename_table,
    create_row,
    read_rows,
    update_rows,
    delete_rows,
    run_select_query,
    list_all_columns,
)

__all__ = [
    # Analytics tools
    "analyze_memory_patterns",
    "get_content_health_score",
    # Search tools
    "search_content",
    "explore_tables",
    "add_embeddings",
    "semantic_search",
    "find_related",
    "smart_search",
    "embedding_stats",
    "auto_semantic_search",
    "auto_smart_search",
    # Discovery tools
    "intelligent_discovery",
    "discovery_templates",
    "discover_relationships",
    # Basic tools
    "create_table",
    "list_tables",
    "describe_table",
    "drop_table",
    "rename_table",
    "create_row",
    "read_rows",
    "update_rows",
    "delete_rows",
    "run_select_query",
    "list_all_columns",
]
