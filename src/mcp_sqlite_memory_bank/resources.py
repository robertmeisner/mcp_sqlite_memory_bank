"""
MCP Resources Support for SQLite Memory Bank
==========================================

This module adds MCP Resources support, allowing the memory bank to expose
stored content as MCP resources that can be consumed by LLM applications.

Resources provide context and data that can be accessed by AI models through
the standardized MCP protocol.

Author: Robert Meisner
"""

from typing import Dict, Any, cast
from fastmcp import FastMCP
from .database import get_database
from .semantic import is_semantic_search_available
import json


class MemoryBankResources:
    """Manages MCP Resources for the SQLite Memory Bank."""

    def __init__(self, mcp_app: FastMCP, db_path: str):
        self.mcp = mcp_app
        self.db_path = db_path
        self._register_resources()

    def _register_resources(self):
        """Register MCP resources with the FastMCP app."""

        @self.mcp.resource("memory://tables/list")
        async def get_tables_list() -> str:
            """Provide a list of all available tables as an MCP resource."""
            db = get_database(self.db_path)
            result = cast(Dict[str, Any], db.list_tables())

            if not result.get("success"):
                return json.dumps({"error": "Failed to fetch tables", "details": result})

            resource_content = {
                "resource_type": "table_list",
                "description": "List of all available tables in the memory bank",
                "tables": result.get("tables", []),
                "total_count": len(result.get("tables", [])),
                "last_updated": "dynamic",
            }

            return json.dumps(resource_content, indent=2)

        @self.mcp.resource("memory://tables/{table_name}/schema")
        async def get_table_schema(table_name: str) -> str:
            """Provide table schema information as an MCP resource."""
            db = get_database(self.db_path)
            result = cast(Dict[str, Any], db.describe_table(table_name))

            if not result.get("success"):
                return json.dumps(
                    {
                        "error": f"Failed to fetch schema for table '{table_name}'",
                        "details": result,
                    }
                )

            resource_content = {
                "resource_type": "table_schema",
                "table_name": table_name,
                "description": f"Schema definition for table '{table_name}'",
                "columns": result.get("columns", []),
                "column_count": len(result.get("columns", [])),
                "last_updated": "dynamic",
            }

            return json.dumps(resource_content, indent=2)

        @self.mcp.resource("memory://tables/{table_name}/data")
        async def get_table_data(table_name: str) -> str:
            """Provide table data as an MCP resource."""
            db = get_database(self.db_path)
            result = cast(Dict[str, Any], db.read_rows(table_name, {}))

            if not result.get("success"):
                return json.dumps(
                    {
                        "error": f"Failed to fetch data for table '{table_name}'",
                        "details": result,
                    }
                )

            rows = result.get("rows", [])
            resource_content = {
                "resource_type": "table_data",
                "table_name": table_name,
                "description": f"All data from table '{table_name}'",
                "rows": rows,
                "row_count": len(rows),
                "last_updated": "dynamic",
            }

            return json.dumps(resource_content, indent=2)

        @self.mcp.resource("memory://search/{query}")
        async def search_memory_content(query: str) -> str:
            """Provide search results as an MCP resource."""
            db = get_database(self.db_path)
            result = cast(
                Dict[str, Any], db.search_content(query, None, 50)
            )  # Search all tables, limit to 50 results

            if not result.get("success"):
                return json.dumps({"error": f"Failed to search for '{query}'", "details": result})

            search_results = result.get("results", [])
            resource_content = {
                "resource_type": "search_results",
                "query": query,
                "description": f"Search results for query: '{query}'",
                "results": search_results,
                "result_count": len(search_results),
                "last_updated": "dynamic",
            }

            return json.dumps(resource_content, indent=2)

        @self.mcp.resource("memory://analytics/overview")
        async def get_memory_overview() -> str:
            """Provide memory bank overview analytics as an MCP resource."""
            db = get_database(self.db_path)

            # Get table list
            tables_result = cast(Dict[str, Any], db.list_tables())
            if not tables_result.get("success"):
                return json.dumps(
                    {
                        "error": "Failed to fetch memory overview",
                        "details": tables_result,
                    }
                )

            tables = tables_result.get("tables", [])
            total_rows = 0
            table_stats = {}

            # Get row counts for each table
            for table in tables:
                try:
                    rows_result = cast(Dict[str, Any], db.read_rows(table, {}))
                    if rows_result.get("success"):
                        row_count = len(rows_result.get("rows", []))
                        table_stats[table] = {
                            "row_count": row_count,
                            "status": "accessible",
                        }
                        total_rows += row_count
                    else:
                        table_stats[table] = {"row_count": 0, "status": "error"}
                except Exception as e:
                    table_stats[table] = {"row_count": 0, "status": f"error: {str(e)}"}

            # Find largest table
            largest_table = None
            if table_stats:
                max_rows = 0
                for table_name, stats in table_stats.items():
                    row_count_obj = stats.get("row_count", 0)
                    row_count = int(row_count_obj) if isinstance(row_count_obj, (int, str)) else 0
                    if row_count > max_rows:
                        max_rows = row_count
                        largest_table = table_name

            resource_content = {
                "resource_type": "memory_overview",
                "description": "Overview of memory bank contents and usage",
                "summary": {
                    "total_tables": len(tables),
                    "total_rows": total_rows,
                    "largest_table": largest_table,
                },
                "table_statistics": table_stats,
                "last_updated": "dynamic",
            }

            return json.dumps(resource_content, indent=2)

        @self.mcp.resource("memory://live/recent-activity")
        async def get_recent_activity() -> str:
            """Real-time feed of recent memory bank changes and activity."""
            db = get_database(self.db_path)

            # Get tables with timestamp columns for activity tracking
            tables_result = cast(Dict[str, Any], db.list_tables())
            if not tables_result.get("success"):
                return json.dumps({"error": "Failed to get tables", "details": tables_result})

            recent_activity = []
            tables = tables_result.get("tables", [])

            for table_name in tables:
                try:
                    # Check if table has timestamp column
                    schema_result = cast(Dict[str, Any], db.describe_table(table_name))
                    if not schema_result.get("success"):
                        continue

                    columns = schema_result.get("columns", [])
                    timestamp_cols = [
                        col for col in columns if "timestamp" in col.get("name", "").lower()
                    ]

                    if timestamp_cols:
                        # Get recent entries (last 10)
                        recent_result = cast(Dict[str, Any], db.read_rows(table_name, None, 10))
                        if recent_result.get("success"):
                            rows = recent_result.get("rows", [])
                            for row in rows:
                                activity_entry = {
                                    "table": table_name,
                                    "action": "content_added",
                                    "timestamp": row.get(timestamp_cols[0]["name"]),
                                    "content_preview": (
                                        str(row).replace('"', "'")[:100] + "..."
                                        if len(str(row)) > 100
                                        else str(row)
                                    ),
                                    "row_id": row.get("id"),
                                }
                                recent_activity.append(activity_entry)

                except Exception:
                    continue

            # Sort by timestamp (most recent first)
            recent_activity.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            recent_activity = recent_activity[:20]  # Limit to 20 most recent

            resource_content = {
                "resource_type": "recent_activity",
                "description": "Recent changes and additions to the memory bank",
                "activities": recent_activity,
                "activity_count": len(recent_activity),
                "last_updated": "real-time",
                "refresh_rate": "dynamic",
            }

            return json.dumps(resource_content, indent=2)

        @self.mcp.resource("memory://live/content-suggestions")
        async def get_content_suggestions() -> str:
            """AI-powered suggestions for content improvements and organization."""
            db = get_database(self.db_path)

            suggestions: dict[str, list[dict[str, Any]]] = {
                "organization_suggestions": [],
                "content_gaps": [],
                "semantic_opportunities": [],
                "quality_improvements": [],
            }

            try:
                # Get basic analysis
                tables_result = cast(Dict[str, Any], db.list_tables())
                if not tables_result.get("success"):
                    return json.dumps(
                        {"error": "Failed to analyze content", "details": tables_result}
                    )

                tables = tables_result.get("tables", [])

                for table_name in tables:
                    try:
                        # Analyze table content
                        rows_result = cast(Dict[str, Any], db.read_rows(table_name))
                        if not rows_result.get("success"):
                            continue

                        rows = rows_result.get("rows", [])

                        # Check for organization opportunities
                        if len(rows) > 50:
                            suggestions["organization_suggestions"].append(
                                {
                                    "table": table_name,
                                    "suggestion": "Consider adding categories or tags for better organization",
                                    "reason": f"Large table with {len(rows)} rows could benefit from categorization",
                                }
                            )

                        # Check for semantic search opportunities
                        if is_semantic_search_available():
                            embedding_stats = cast(
                                Dict[str, Any], db.get_embedding_stats(table_name)
                            )
                            if (
                                embedding_stats.get("success")
                                and embedding_stats.get("coverage_percent", 0) == 0
                            ):
                                schema_result = cast(Dict[str, Any], db.describe_table(table_name))
                                if schema_result.get("success"):
                                    text_cols = [
                                        col
                                        for col in schema_result.get("columns", [])
                                        if "TEXT" in col.get("type", "").upper()
                                    ]
                                    if text_cols and len(rows) > 5:
                                        suggestions["semantic_opportunities"].append(
                                            {
                                                "table": table_name,
                                                "suggestion": "Set up semantic search for better content discovery",
                                                "reason": f"Table has {len(text_cols)} text columns and {len(rows)} rows",
                                                "action": f"Use add_embeddings('{table_name}', {[col['name'] for col in text_cols[:3]]})",
                                            }
                                        )

                        # Check for content gaps (sparse tables)
                        if 1 <= len(rows) <= 5:
                            suggestions["content_gaps"].append(
                                {
                                    "table": table_name,
                                    "suggestion": "Consider adding more content or consolidating with other tables",
                                    "reason": f"Table has only {len(rows)} rows - might be underutilized",
                                }
                            )

                        # Sample content for quality analysis
                        if rows:
                            sample_row = rows[0]
                            short_values = [
                                k
                                for k, v in sample_row.items()
                                if isinstance(v, str) and 0 < len(v) < 10
                            ]
                            if len(short_values) > 2:
                                suggestions["quality_improvements"].append(
                                    {
                                        "table": table_name,
                                        "suggestion": "Consider adding more detailed content",
                                        "reason": f"Several columns have very short values: {short_values[:3]}",
                                    }
                                )

                    except Exception:
                        continue

                # Prioritize suggestions
                priority_order = [
                    "semantic_opportunities",
                    "organization_suggestions",
                    "quality_improvements",
                    "content_gaps",
                ]
                prioritized = {}
                for category in priority_order:
                    if suggestions[category]:
                        prioritized[category] = suggestions[category]

                resource_content = {
                    "resource_type": "content_suggestions",
                    "description": "AI-powered suggestions for improving your memory bank",
                    "suggestions": prioritized,
                    "total_suggestions": sum(len(v) for v in suggestions.values()),
                    "last_updated": "real-time",
                    "next_actions": [
                        "Review semantic opportunities for high-value tables",
                        "Consider organization improvements for large tables",
                        "Add more detailed content where suggested",
                    ],
                }

                return json.dumps(resource_content, indent=2)

            except Exception as e:
                return json.dumps(
                    {
                        "error": f"Failed to generate content suggestions: {str(e)}",
                        "suggestions": suggestions,
                    }
                )

        @self.mcp.resource("memory://analytics/insights")
        async def get_memory_insights() -> str:
            """Real-time analytics and insights about memory bank usage and patterns."""
            db = get_database(self.db_path)

            insights: dict[str, dict[str, Any]] = {
                "usage_patterns": {},
                "content_trends": {},
                "search_recommendations": {},
                "health_indicators": {},
            }

            try:
                tables_result = cast(Dict[str, Any], db.list_tables())
                if not tables_result.get("success"):
                    return json.dumps({"error": "Failed to get insights", "details": tables_result})

                tables = tables_result.get("tables", [])
                total_rows = 0
                content_quality_scores = []

                for table_name in tables:
                    rows_result = cast(Dict[str, Any], db.read_rows(table_name))
                    if rows_result.get("success"):
                        rows = rows_result.get("rows", [])
                        row_count = len(rows)
                        total_rows += row_count

                        # Calculate content quality score for this table
                        if rows:
                            # Sample content to estimate quality
                            sample_size = min(5, len(rows))
                            total_content_length = 0
                            for row in rows[:sample_size]:
                                for value in row.values():
                                    if isinstance(value, str):
                                        total_content_length += len(value)

                            avg_content_length = (
                                total_content_length / sample_size if sample_size > 0 else 0
                            )
                            quality_score = min(10, avg_content_length / 50)  # Normalize to 0-10
                            content_quality_scores.append(quality_score)

                            insights["usage_patterns"][table_name] = {
                                "row_count": row_count,
                                "avg_content_length": round(avg_content_length),
                                "quality_score": round(quality_score, 1),
                                "category": (
                                    "high_value"
                                    if quality_score > 7
                                    else ("medium_value" if quality_score > 3 else "low_value")
                                ),
                            }

                # Overall health indicators
                avg_quality = (
                    sum(content_quality_scores) / len(content_quality_scores)
                    if content_quality_scores
                    else 0
                )
                insights["health_indicators"] = {
                    "total_tables": len(tables),
                    "total_content_rows": total_rows,
                    "average_content_quality": round(avg_quality, 1),
                    "content_distribution": (
                        "balanced"
                        if len(tables) > 0 and total_rows / len(tables) > 10
                        else "sparse"
                    ),
                    "semantic_readiness": (
                        "available" if is_semantic_search_available() else "unavailable"
                    ),
                }

                # Search recommendations
                high_value_tables = [
                    name
                    for name, data in insights["usage_patterns"].items()
                    if data.get("category") == "high_value"
                ]

                if high_value_tables:
                    insights["search_recommendations"]["intelligent_search"] = {
                        "recommended_tables": high_value_tables,
                        "strategy": "Use intelligent_search() for best results across high-value content",
                    }

                if is_semantic_search_available():
                    insights["search_recommendations"]["semantic_opportunities"] = {
                        "suggestion": "Consider semantic search for conceptual queries",
                        "best_for": "Finding related concepts, patterns, and thematic content",
                    }

                resource_content = {
                    "resource_type": "memory_insights",
                    "description": "Real-time analytics and insights about your memory bank",
                    "insights": insights,
                    "last_updated": "real-time",
                    "recommendations": [
                        (
                            f"Focus on high-value tables: {', '.join(high_value_tables[:3])}"
                            if high_value_tables
                            else "Add more detailed content to improve value"
                        ),
                        "Use intelligent_search() for optimal search results",
                        (
                            "Consider semantic search setup for better content discovery"
                            if is_semantic_search_available()
                            else "Install sentence-transformers for semantic search"
                        ),
                    ],
                }

                return json.dumps(resource_content, indent=2)

            except Exception as e:
                return json.dumps(
                    {
                        "error": f"Failed to generate insights: {str(e)}",
                        "insights": insights,
                    }
                )


def setup_mcp_resources(mcp_app: FastMCP, db_path: str) -> MemoryBankResources:
    """Set up MCP Resources for the memory bank."""
    return MemoryBankResources(mcp_app, db_path)
