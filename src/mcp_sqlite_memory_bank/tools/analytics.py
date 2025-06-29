"""
Analytics and Content Analysis Tools for SQLite Memory Bank
===========================================================

This module contains tools for analyzing memory bank content, assessing health,
and providing insights for better knowledge organization.
"""

import logging
from typing import cast

from ..database import get_database
from ..semantic import is_semantic_search_available
from ..types import ToolResponse
from ..utils import catch_errors


@catch_errors
def analyze_memory_patterns() -> ToolResponse:
    """
    🔍 **MEMORY PATTERN ANALYSIS** - Discover insights in your memory bank!

    Analyzes content patterns, usage statistics, and identifies opportunities
    for better organization and knowledge discovery.

    Returns:
        ToolResponse: On success: {"success": True, "analysis": dict}
                     On error: {"success": False, "error": str, "category": str, "details": dict}

    Examples:
        >>> analyze_memory_patterns()
        {"success": True, "analysis": {
            "content_distribution": {"technical_decisions": 15, "project_notes": 8},
            "text_density": {"high": ["documentation"], "low": ["metadata"]},
            "semantic_readiness": {"ready": 2, "needs_setup": 1},
            "recommendations": ["Consider embedding setup for 'notes' table"]
        }}

    FastMCP Tool Info:
        - **CONTENT INSIGHTS**: Analyzes distribution and quality of stored content
        - **SEMANTIC READINESS**: Shows which tables are ready for semantic search
        - **ORGANIZATION TIPS**: Suggests improvements for better knowledge discovery
        - **USAGE PATTERNS**: Identifies most and least used content areas
    """
    try:
        from .. import server

        db = get_database(server.DB_PATH)

        # Get all tables
        tables_result = db.list_tables()
        if not tables_result.get("success"):
            return cast(ToolResponse, tables_result)

        tables = tables_result.get("tables", [])
        analysis = {
            "content_distribution": {},
            "text_density": {"high": [], "medium": [], "low": []},
            "semantic_readiness": {"ready": [], "partial": [], "needs_setup": []},
            "schema_analysis": {},
            "recommendations": [],
            "total_tables": len(tables),
            "total_content_rows": 0,
        }

        for table_name in tables:
            try:
                # Get basic table info
                rows_result = db.read_rows(table_name)
                if not rows_result.get("success"):
                    continue

                rows = rows_result.get("rows", [])
                row_count = len(rows)
                analysis["content_distribution"][table_name] = row_count
                analysis["total_content_rows"] += row_count

                # Analyze schema
                schema_result = db.describe_table(table_name)
                if schema_result.get("success"):
                    columns = schema_result.get("columns", [])
                    text_columns = [col for col in columns if "TEXT" in col.get("type", "").upper()]

                    analysis["schema_analysis"][table_name] = {
                        "total_columns": len(columns),
                        "text_columns": len(text_columns),
                        "has_id_column": any(col.get("name") == "id" for col in columns),
                        "has_timestamp": any("timestamp" in col.get("name", "").lower() for col in columns),
                    }

                    # Analyze text density
                    if rows and text_columns:
                        text_content_lengths = []
                        for row in rows[:10]:  # Sample first 10 rows
                            for col in text_columns:
                                content = row.get(col["name"], "")
                                if content:
                                    text_content_lengths.append(len(str(content)))

                        if text_content_lengths:
                            avg_length = sum(text_content_lengths) / len(text_content_lengths)
                            if avg_length > 500:
                                analysis["text_density"]["high"].append(table_name)
                            elif avg_length > 100:
                                analysis["text_density"]["medium"].append(table_name)
                            else:
                                analysis["text_density"]["low"].append(table_name)

                # Check semantic readiness
                if is_semantic_search_available():
                    embedding_stats = db.get_embedding_stats(table_name)
                    if embedding_stats.get("success"):
                        coverage = embedding_stats.get("coverage_percent", 0)
                        if coverage >= 80:
                            analysis["semantic_readiness"]["ready"].append(table_name)
                        elif coverage > 0:
                            analysis["semantic_readiness"]["partial"].append(table_name)
                        else:
                            analysis["semantic_readiness"]["needs_setup"].append(table_name)

            except Exception as e:
                logging.warning(f"Error analyzing table {table_name}: {e}")
                continue

        # Generate recommendations
        recommendations = []

        # Semantic search recommendations
        if len(analysis["semantic_readiness"]["needs_setup"]) > 0:
            high_value_tables = [
                t for t in analysis["semantic_readiness"]["needs_setup"] if t in analysis["text_density"]["high"] + analysis["text_density"]["medium"]
            ]
            if high_value_tables:
                recommendations.append(f"Consider setting up semantic search for high-value tables: {', '.join(high_value_tables[:3])}")

        # Content organization recommendations
        large_tables = [t for t, count in analysis["content_distribution"].items() if count > 50]
        if large_tables:
            recommendations.append(f"Large tables detected: {', '.join(large_tables)}. Consider organizing with categories or tags.")

        # Empty or sparse tables
        sparse_tables = [t for t, count in analysis["content_distribution"].items() if count < 5 and count > 0]
        if sparse_tables:
            recommendations.append(f"Sparse tables found: {', '.join(sparse_tables)}. Consider consolidating or adding more content.")

        # Schema improvements
        tables_without_timestamps = [t for t, schema in analysis["schema_analysis"].items() if not schema.get("has_timestamp")]
        if len(tables_without_timestamps) > 2:
            recommendations.append("Consider adding timestamp columns to track when content was created/modified.")

        analysis["recommendations"] = recommendations

        return cast(
            ToolResponse,
            {
                "success": True,
                "analysis": analysis,
                "summary": {
                    "tables_analyzed": len(tables),
                    "total_rows": analysis["total_content_rows"],
                    "semantic_ready": len(analysis["semantic_readiness"]["ready"]),
                    "high_value_content": len(analysis["text_density"]["high"]),
                    "recommendations_count": len(recommendations),
                },
            },
        )

    except Exception as e:
        return cast(
            ToolResponse,
            {
                "success": False,
                "error": f"Memory pattern analysis failed: {str(e)}",
                "category": "ANALYSIS",
                "details": {"exception": str(e)},
            },
        )


@catch_errors
def get_content_health_score() -> ToolResponse:
    """
    📊 **CONTENT HEALTH ASSESSMENT** - Rate the quality of your memory bank!

    Provides a comprehensive health score based on content quality, organization,
    semantic search readiness, and usage patterns.

    Returns:
        ToolResponse: On success: {"success": True, "health_score": float, "metrics": dict}
                     On error: {"success": False, "error": str, "category": str, "details": dict}

    Examples:
        >>> get_content_health_score()
        {"success": True, "health_score": 8.5, "metrics": {
            "content_quality": 9.0, "organization": 7.5, "semantic_readiness": 8.0,
            "accessibility": 9.0, "recommendations": [...]
        }}

    FastMCP Tool Info:
        - **OVERALL SCORE**: Single metric (0-10) indicating memory bank health
        - **DETAILED METRICS**: Breakdown by quality, organization, and readiness
        - **ACTIONABLE INSIGHTS**: Specific recommendations for improvement
        - **TREND TRACKING**: Compare health over time (if run regularly)
    """
    try:
        # Get the pattern analysis first - call database methods directly
        from .. import server

        db = get_database(server.DB_PATH)

        # Get all tables
        tables_result = db.list_tables()
        if not tables_result.get("success"):
            return cast(
                ToolResponse,
                {
                    "success": False,
                    "error": "Failed to get tables for health analysis",
                    "category": "DATABASE",
                    "details": tables_result,
                },
            )

        tables = tables_result.get("tables", [])

        # Build basic analysis for health scoring
        analysis = {
            "content_distribution": {},
            "text_density": {"high": [], "medium": [], "low": []},
            "semantic_readiness": {"ready": [], "partial": [], "needs_setup": []},
            "schema_analysis": {},
            "total_tables": len(tables),
            "total_content_rows": 0,
        }

        for table_name in tables:
            try:
                # Get basic table info
                rows_result = db.read_rows(table_name)
                if not rows_result.get("success"):
                    continue

                rows = rows_result.get("rows", [])
                row_count = len(rows)
                analysis["content_distribution"][table_name] = row_count
                analysis["total_content_rows"] += row_count

                # Analyze schema
                schema_result = db.describe_table(table_name)
                if schema_result.get("success"):
                    columns = schema_result.get("columns", [])
                    text_columns = [col for col in columns if "TEXT" in col.get("type", "").upper()]

                    analysis["schema_analysis"][table_name] = {
                        "total_columns": len(columns),
                        "text_columns": len(text_columns),
                        "has_id_column": any(col.get("name") == "id" for col in columns),
                        "has_timestamp": any("timestamp" in col.get("name", "").lower() for col in columns),
                    }

                    # Analyze text density
                    if rows and text_columns:
                        text_content_lengths = []
                        for row in rows[:10]:  # Sample first 10 rows
                            for col in text_columns:
                                content = row.get(col["name"], "")
                                if content:
                                    text_content_lengths.append(len(str(content)))

                        if text_content_lengths:
                            avg_length = sum(text_content_lengths) / len(text_content_lengths)
                            if avg_length > 500:
                                analysis["text_density"]["high"].append(table_name)
                            elif avg_length > 100:
                                analysis["text_density"]["medium"].append(table_name)
                            else:
                                analysis["text_density"]["low"].append(table_name)

                # Check semantic readiness
                if is_semantic_search_available():
                    embedding_stats = db.get_embedding_stats(table_name)
                    if embedding_stats.get("success"):
                        coverage = embedding_stats.get("coverage_percent", 0)
                        if coverage >= 80:
                            analysis["semantic_readiness"]["ready"].append(table_name)
                        elif coverage > 0:
                            analysis["semantic_readiness"]["partial"].append(table_name)
                        else:
                            analysis["semantic_readiness"]["needs_setup"].append(table_name)

            except Exception as e:
                logging.warning(f"Error analyzing table {table_name}: {e}")
                continue

        summary = {
            "tables_analyzed": len(tables),
            "total_rows": analysis["total_content_rows"],
            "semantic_ready": len(analysis["semantic_readiness"]["ready"]),
            "high_value_content": len(analysis["text_density"]["high"]),
        }

        # Calculate health metrics (0-10 scale)
        metrics = {}

        # 1. Content Quality Score (based on text density and volume)
        total_rows = summary.get("total_rows", 0)
        high_quality_tables = len(analysis.get("text_density", {}).get("high", []))
        total_tables = summary.get("tables_analyzed", 1)

        if total_rows == 0:
            metrics["content_volume"] = 0.0
        elif total_rows < 10:
            metrics["content_volume"] = 3.0
        elif total_rows < 50:
            metrics["content_volume"] = 6.0
        elif total_rows < 200:
            metrics["content_volume"] = 8.0
        else:
            metrics["content_volume"] = 10.0

        metrics["content_quality"] = min(10.0, (high_quality_tables / total_tables) * 10 + 3)

        # 2. Organization Score (based on schema quality)
        schema_analysis = analysis.get("schema_analysis", {})
        organization_factors = []

        for table_name, schema in schema_analysis.items():
            table_score = 0
            if schema.get("has_id_column"):
                table_score += 2
            if schema.get("has_timestamp"):
                table_score += 2
            if schema.get("text_columns", 0) > 0:
                table_score += 3
            if 2 <= schema.get("total_columns", 0) <= 10:  # Good column count
                table_score += 3
            organization_factors.append(table_score)

        metrics["organization"] = (sum(organization_factors) / len(organization_factors)) if organization_factors else 5.0

        # 3. Semantic Readiness Score
        semantic_ready = len(analysis.get("semantic_readiness", {}).get("ready", []))
        semantic_partial = len(analysis.get("semantic_readiness", {}).get("partial", []))
        if not is_semantic_search_available():
            metrics["semantic_readiness"] = 5.0  # Neutral score if not available
            metrics["semantic_note"] = "Semantic search dependencies not available"
        else:
            semantic_score = ((semantic_ready * 2 + semantic_partial) / (total_tables * 2)) * 10
            metrics["semantic_readiness"] = min(10.0, semantic_score)

        # 4. Accessibility Score (how easy it is to find and use content)
        medium_density = len(analysis.get("text_density", {}).get("medium", []))

        # Prefer medium density (not too verbose, not too sparse)
        if total_tables == 0:
            metrics["accessibility"] = 5.0
        else:
            accessibility_score = ((high_quality_tables + medium_density * 1.5) / total_tables) * 8 + 2
            metrics["accessibility"] = min(10.0, accessibility_score)

        # 5. Overall Health Score (weighted average)
        weights = {
            "content_volume": 0.2,
            "content_quality": 0.3,
            "organization": 0.2,
            "semantic_readiness": 0.15,
            "accessibility": 0.15,
        }

        health_score = sum(metrics[key] * weights[key] for key in weights.keys())

        # Generate health-specific recommendations
        health_recommendations = []

        if metrics["content_volume"] < 5:
            health_recommendations.append("🔴 LOW CONTENT: Add more valuable content to your memory bank")
        elif metrics["content_volume"] < 7:
            health_recommendations.append("🟡 MODERATE CONTENT: Consider expanding your knowledge base")

        if metrics["content_quality"] < 6:
            health_recommendations.append("🔴 CONTENT QUALITY: Focus on adding more detailed, rich content")

        if metrics["organization"] < 6:
            health_recommendations.append("🔴 ORGANIZATION: Improve table schemas with timestamps and proper columns")

        if metrics["semantic_readiness"] < 5 and is_semantic_search_available():
            health_recommendations.append("🟡 SEMANTIC SEARCH: Set up embeddings for better content discovery")

        if metrics["accessibility"] < 6:
            health_recommendations.append("🔴 ACCESSIBILITY: Improve content structure for easier discovery")

        # Health grade
        if health_score >= 9:
            grade = "A+ (Excellent)"
        elif health_score >= 8:
            grade = "A (Great)"
        elif health_score >= 7:
            grade = "B+ (Good)"
        elif health_score >= 6:
            grade = "B (Adequate)"
        elif health_score >= 5:
            grade = "C (Needs Improvement)"
        else:
            grade = "D (Poor - Needs Attention)"

        return cast(
            ToolResponse,
            {
                "success": True,
                "health_score": round(health_score, 1),
                "grade": grade,
                "metrics": {k: round(v, 1) for k, v in metrics.items()},
                "recommendations": health_recommendations,
                "detailed_analysis": analysis,
                "improvement_priority": {
                    "highest": [k for k, v in metrics.items() if v < 5],
                    "medium": [k for k, v in metrics.items() if 5 <= v < 7],
                    "good": [k for k, v in metrics.items() if v >= 7],
                },
            },
        )

    except Exception as e:
        return cast(
            ToolResponse,
            {
                "success": False,
                "error": f"Content health assessment failed: {str(e)}",
                "category": "ANALYSIS",
                "details": {"exception": str(e)},
            },
        )
