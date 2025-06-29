"""
Discovery and Exploration Tools for SQLite Memory Bank
=====================================================

This module contains advanced discovery tools that help LLM agents intelligently
explore and understand memory bank content through guided workflows and orchestrated
discovery processes.

Author: Robert Meisner
"""

from typing import Any, Dict, List, Optional, cast
from datetime import datetime

from ..database import get_database
from ..semantic import is_semantic_search_available
from ..types import ToolResponse
from ..utils import catch_errors


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

        >>> intelligent_discovery("find_patterns", focus_area="technical_decisions")
        {"success": True, "discovery": {
            "patterns": {"decision_themes": [...], "temporal_trends": [...]},
            "insights": [...]
        }}

    FastMCP Tool Info:
        - **COMPLETELY AUTOMATED**: No manual tool chaining required
        - **GOAL-ORIENTED**: Tailored discovery based on your specific objectives
        - **ACTIONABLE INSIGHTS**: Always includes concrete next steps
        - **LEARNING**: Improves recommendations based on usage patterns
        - **PERFECT FOR AGENTS**: Single tool that orchestrates complex discovery workflows
    """
    try:
        from .. import server

        db = get_database(server.DB_PATH)

        # Initialize discovery session
        discovery_session = {
            "goal": discovery_goal,
            "focus_area": focus_area,
            "depth": depth,
            "timestamp": datetime.now().isoformat(),
            "agent_id": agent_id,
            "steps_completed": [],
            "insights": [],
            "recommendations": [],
        }

        # Step 1: Basic overview
        discovery_session["steps_completed"].append("basic_overview")
        tables_result = db.list_tables()
        if not tables_result.get("success"):
            return cast(
                ToolResponse,
                {
                    "success": False,
                    "error": "Failed to get basic overview",
                    "category": "DISCOVERY_ERROR",
                    "details": tables_result,
                },
            )

        tables = tables_result.get("tables", [])
        overview = {
            "total_tables": len(tables),
            "available_tables": tables,
            "semantic_search_available": is_semantic_search_available(),
        }

        # Step 2: Content analysis based on goal
        if discovery_goal in ["understand_content", "find_patterns", "assess_quality"]:
            discovery_session["steps_completed"].append("content_analysis")
            content_analysis = _analyze_content_for_discovery(
                db, tables, focus_area, depth
            )
            overview.update(content_analysis)

        # Step 3: Schema analysis for structure exploration
        if discovery_goal in ["explore_structure", "understand_content"]:
            discovery_session["steps_completed"].append("schema_analysis")
            schema_analysis = _analyze_schema_for_discovery(
                db, tables, focus_area, depth
            )
            overview.update(schema_analysis)

        # Step 4: Quality assessment
        if discovery_goal in ["assess_quality", "find_patterns"]:
            discovery_session["steps_completed"].append("quality_assessment")
            quality_analysis = _assess_content_quality(db, tables, focus_area, depth)
            overview.update(quality_analysis)

        # Step 5: Search readiness for search preparation
        if discovery_goal in ["prepare_search", "understand_content"]:
            discovery_session["steps_completed"].append("search_readiness")
            search_analysis = _analyze_search_readiness(db, tables, focus_area)
            overview.update(search_analysis)

        # Step 6: Generate insights and recommendations
        insights, recommendations, next_steps = _generate_discovery_insights(
            discovery_goal, overview, focus_area, depth
        )

        discovery_session["insights"] = insights
        discovery_session["recommendations"] = recommendations

        # Step 7: Store discovery pattern for learning (if agent_id provided)
        if agent_id:
            _store_discovery_pattern(db, discovery_session)

        return cast(
            ToolResponse,
            {
                "success": True,
                "discovery": {
                    "goal": discovery_goal,
                    "overview": overview,
                    "insights": insights,
                    "recommendations": recommendations,
                    "focus_area": focus_area,
                    "depth": depth,
                    "steps_completed": discovery_session["steps_completed"],
                },
                "next_steps": next_steps,
                "discovery_session": discovery_session,
                "quick_actions": _generate_quick_actions(
                    discovery_goal, overview, focus_area
                ),
            },
        )

    except Exception as e:
        return cast(
            ToolResponse,
            {
                "success": False,
                "error": f"Intelligent discovery failed: {str(e)}",
                "category": "DISCOVERY_ERROR",
                "details": {
                    "goal": discovery_goal,
                    "focus_area": focus_area,
                    "depth": depth,
                    "agent_id": agent_id,
                },
            },
        )


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
    try:
        templates = {
            "first_time_exploration": {
                "name": "First Time Exploration",
                "description": "Complete discovery workflow for agents new to this memory bank",
                "estimated_time": "2-3 minutes",
                "workflow": [
                    {
                        "step": 1,
                        "action": "Get Overview",
                        "tool": "intelligent_discovery",
                        "params": {
                            "discovery_goal": "understand_content",
                            "depth": "moderate",
                        },
                        "purpose": "Understand what data is available and how it's organized",
                        "look_for": ["total tables", "content types", "data volume"],
                    },
                    {
                        "step": 2,
                        "action": "Explore Structure",
                        "tool": "explore_tables",
                        "params": {"include_row_counts": True},
                        "purpose": "See detailed table schemas and sample data",
                        "look_for": [
                            "column types",
                            "sample content",
                            "data relationships",
                        ],
                    },
                    {
                        "step": 3,
                        "action": "Test Search Capabilities",
                        "tool": "auto_smart_search",
                        "params": {"query": "recent important information", "limit": 5},
                        "purpose": "Understand search capabilities and content accessibility",
                        "look_for": [
                            "search quality",
                            "result relevance",
                            "content types found",
                        ],
                    },
                    {
                        "step": 4,
                        "action": "Assess Quality",
                        "tool": "get_content_health_score",
                        "params": {},
                        "purpose": "Understand overall memory bank quality and opportunities",
                        "look_for": [
                            "health score",
                            "improvement recommendations",
                            "strengths",
                        ],
                    },
                ],
                "success_criteria": [
                    "Understand what types of information are stored",
                    "Know which tables contain the most valuable content",
                    "Identify best search strategies for this memory bank",
                    "Have actionable next steps for productive use",
                ],
            },
            "content_audit": {
                "name": "Content Quality Audit",
                "description": "Systematic review of content quality and completeness",
                "estimated_time": "5-7 minutes",
                "workflow": [
                    {
                        "step": 1,
                        "action": "Quality Assessment",
                        "tool": "get_content_health_score",
                        "params": {},
                        "purpose": "Get overall quality metrics and problem areas",
                        "look_for": [
                            "quality scores",
                            "problem tables",
                            "recommendations",
                        ],
                    },
                    {
                        "step": 2,
                        "action": "Pattern Analysis",
                        "tool": "analyze_memory_patterns",
                        "params": {},
                        "purpose": "Identify content patterns and organizational issues",
                        "look_for": [
                            "content distribution",
                            "sparse tables",
                            "organization gaps",
                        ],
                    },
                    {
                        "step": 3,
                        "action": "Table-by-Table Review",
                        "tool": "explore_tables",
                        "params": {"include_row_counts": True},
                        "purpose": "Detailed examination of each table's content",
                        "look_for": [
                            "empty tables",
                            "low-quality content",
                            "missing data",
                        ],
                    },
                    {
                        "step": 4,
                        "action": "Search Readiness",
                        "tool": "intelligent_discovery",
                        "params": {
                            "discovery_goal": "prepare_search",
                            "depth": "comprehensive",
                        },
                        "purpose": "Ensure content is optimally searchable",
                        "look_for": [
                            "embedding coverage",
                            "search optimization opportunities",
                        ],
                    },
                ],
                "success_criteria": [
                    "Identify all content quality issues",
                    "Have specific recommendations for improvement",
                    "Understand which content areas need attention",
                    "Know how to optimize for better searchability",
                ],
            },
            "search_optimization": {
                "name": "Search Optimization Setup",
                "description": "Prepare memory bank for optimal content discovery and searching",
                "estimated_time": "3-5 minutes",
                "workflow": [
                    {
                        "step": 1,
                        "action": "Search Capability Assessment",
                        "tool": "intelligent_discovery",
                        "params": {
                            "discovery_goal": "prepare_search",
                            "depth": "comprehensive",
                        },
                        "purpose": "Understand current search capabilities and gaps",
                        "look_for": [
                            "semantic readiness",
                            "text column identification",
                            "embedding status",
                        ],
                    },
                    {
                        "step": 2,
                        "action": "Content Analysis for Search",
                        "tool": "analyze_memory_patterns",
                        "params": {},
                        "purpose": "Identify high-value content for search optimization",
                        "look_for": [
                            "text-rich tables",
                            "high-value content",
                            "search opportunities",
                        ],
                    },
                    {
                        "step": 3,
                        "action": "Test Current Search",
                        "tool": "search_content",
                        "params": {"query": "test search capabilities", "limit": 10},
                        "purpose": "Baseline current search performance",
                        "look_for": ["search result quality", "coverage", "relevance"],
                    },
                    {
                        "step": 4,
                        "action": "Semantic Search Setup",
                        "tool": "auto_semantic_search",
                        "params": {"query": "important valuable content", "limit": 5},
                        "purpose": "Enable and test semantic search capabilities",
                        "look_for": [
                            "automatic embedding generation",
                            "semantic result quality",
                        ],
                    },
                ],
                "success_criteria": [
                    "Semantic search is enabled for key tables",
                    "Both keyword and semantic search work effectively",
                    "Search performance meets quality standards",
                    "Clear strategy for ongoing search optimization",
                ],
            },
            "problem_solving": {
                "name": "Problem-Solving Discovery",
                "description": "Find information to solve specific problems or answer questions",
                "estimated_time": "2-4 minutes",
                "workflow": [
                    {
                        "step": 1,
                        "action": "Quick Content Survey",
                        "tool": "intelligent_discovery",
                        "params": {
                            "discovery_goal": "understand_content",
                            "depth": "quick",
                        },
                        "purpose": "Rapid overview of available information",
                        "look_for": [
                            "relevant content areas",
                            "potential information sources",
                        ],
                    },
                    {
                        "step": 2,
                        "action": "Targeted Search",
                        "tool": "auto_smart_search",
                        "params": {
                            "query": "REPLACE_WITH_PROBLEM_KEYWORDS",
                            "limit": 10,
                        },
                        "purpose": "Find directly relevant information",
                        "look_for": [
                            "directly applicable content",
                            "related information",
                            "context clues",
                        ],
                    },
                    {
                        "step": 3,
                        "action": "Related Content Discovery",
                        "tool": "auto_semantic_search",
                        "params": {
                            "query": "REPLACE_WITH_CONCEPTUAL_TERMS",
                            "similarity_threshold": 0.3,
                        },
                        "purpose": "Find conceptually related information",
                        "look_for": [
                            "broader context",
                            "related concepts",
                            "background information",
                        ],
                    },
                    {
                        "step": 4,
                        "action": "Information Gap Analysis",
                        "tool": "explore_tables",
                        "params": {"include_row_counts": True},
                        "purpose": "Identify what information might be missing",
                        "look_for": [
                            "information gaps",
                            "additional context sources",
                            "related data",
                        ],
                    },
                ],
                "customization_note": "Replace REPLACE_WITH_PROBLEM_KEYWORDS and REPLACE_WITH_CONCEPTUAL_TERMS with your specific problem terms",
                "success_criteria": [
                    "Found directly relevant information",
                    "Identified related/contextual information",
                    "Understand what information might be missing",
                    "Have clear next steps for problem resolution",
                ],
            },
        }

        if template_type not in templates:
            available_templates = list(templates.keys())
            return cast(
                ToolResponse,
                {
                    "success": False,
                    "error": f"Template '{template_type}' not found",
                    "category": "TEMPLATE_ERROR",
                    "details": {
                        "available_templates": available_templates,
                        "requested_template": template_type,
                    },
                },
            )

        template = templates[template_type]

        # Customize template if requested
        if customize_for:
            template = _customize_template(template, customize_for)

        return cast(
            ToolResponse,
            {
                "success": True,
                "template": template,
                "template_type": template_type,
                "customized_for": customize_for,
                "available_templates": list(templates.keys()),
                "usage_tip": "Follow the workflow steps in order, adapting parameters as needed for your specific situation",
            },
        )

    except Exception as e:
        return cast(
            ToolResponse,
            {
                "success": False,
                "error": f"Discovery template generation failed: {str(e)}",
                "category": "TEMPLATE_ERROR",
                "details": {
                    "template_type": template_type,
                    "customize_for": customize_for,
                },
            },
        )


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
    try:
        from .. import server

        db = get_database(server.DB_PATH)

        # Get all tables or focus on specific table
        tables_result = db.list_tables()
        if not tables_result.get("success"):
            return cast(ToolResponse, tables_result)

        all_tables = tables_result.get("tables", [])
        target_tables = [table_name] if table_name else all_tables

        relationships = {}
        insights = []

        for target_table in target_tables:
            if target_table not in all_tables:
                continue

            table_relationships = {
                "foreign_key_refs": [],
                "semantic_similar": [],
                "temporal_related": [],
                "naming_related": [],
            }

            # Discover foreign key relationships
            if "foreign_keys" in relationship_types:
                fk_relationships = _discover_foreign_keys(db, target_table, all_tables)
                table_relationships["foreign_key_refs"] = fk_relationships
                if fk_relationships:
                    insights.append(
                        f"Table '{target_table}' has structural relationships with {len(fk_relationships)} other tables"
                    )

            # Discover semantic similarity relationships
            if (
                "semantic_similarity" in relationship_types
                and is_semantic_search_available()
            ):
                semantic_relationships = _discover_semantic_relationships(
                    db, target_table, all_tables, similarity_threshold
                )
                table_relationships["semantic_similar"] = semantic_relationships
                if semantic_relationships:
                    insights.append(
                        f"Table '{target_table}' has semantic similarity with {len(semantic_relationships)} tables"
                    )

            # Discover temporal patterns
            if "temporal_patterns" in relationship_types:
                temporal_relationships = _discover_temporal_relationships(
                    db, target_table, all_tables
                )
                table_relationships["temporal_related"] = temporal_relationships
                if temporal_relationships:
                    insights.append(
                        f"Table '{target_table}' shows temporal patterns with {len(temporal_relationships)} tables"
                    )

            # Discover naming pattern relationships
            if "naming_patterns" in relationship_types:
                naming_relationships = _discover_naming_relationships(
                    target_table, all_tables
                )
                table_relationships["naming_related"] = naming_relationships
                if naming_relationships:
                    insights.append(
                        f"Table '{target_table}' has naming pattern relationships with {len(naming_relationships)} tables"
                    )

            relationships[target_table] = table_relationships

        # Generate relationship insights
        total_relationships = sum(
            len(rel["foreign_key_refs"])
            + len(rel["semantic_similar"])
            + len(rel["temporal_related"])
            + len(rel["naming_related"])
            for rel in relationships.values()
        )

        if total_relationships == 0:
            insights.append(
                "No strong relationships discovered. Consider adding more content or setting up semantic search."
            )
        else:
            insights.append(
                f"Discovered {total_relationships} total relationships across {len(relationships)} tables"
            )

        return cast(
            ToolResponse,
            {
                "success": True,
                "relationships": relationships,
                "insights": insights,
                "relationship_summary": {
                    "total_relationships": total_relationships,
                    "tables_analyzed": len(relationships),
                    "strongest_connections": _identify_strongest_connections(
                        relationships
                    ),
                },
                "recommendations": _generate_relationship_recommendations(
                    relationships, insights
                ),
            },
        )

    except Exception as e:
        return cast(
            ToolResponse,
            {
                "success": False,
                "error": f"Relationship discovery failed: {str(e)}",
                "category": "RELATIONSHIP_ERROR",
                "details": {
                    "table_name": table_name,
                    "relationship_types": relationship_types,
                    "similarity_threshold": similarity_threshold,
                },
            },
        )


# Helper functions for discovery orchestration


def _analyze_content_for_discovery(
    db, tables: List[str], focus_area: Optional[str], depth: str
) -> Dict[str, Any]:
    """Analyze content patterns and distribution."""
    content_analysis = {
        "total_rows": 0,
        "content_distribution": {},
        "text_rich_tables": [],
        "sparse_tables": [],
        "high_value_tables": [],
    }

    target_tables = [focus_area] if focus_area and focus_area in tables else tables

    for table_name in target_tables:
        try:
            rows_result = db.read_rows(table_name)
            if rows_result.get("success"):
                rows = rows_result.get("rows", [])
                row_count = len(rows)
                content_analysis["total_rows"] += row_count
                content_analysis["content_distribution"][table_name] = row_count

                # Analyze content quality if depth allows
                if depth in ["moderate", "comprehensive"] and rows:
                    # Sample content quality
                    sample_size = min(3, len(rows))
                    total_content_length = 0

                    for row in rows[:sample_size]:
                        for value in row.values():
                            if isinstance(value, str):
                                total_content_length += len(value)

                    avg_content_length = (
                        total_content_length / sample_size if sample_size > 0 else 0
                    )

                    if avg_content_length > 200:
                        content_analysis["text_rich_tables"].append(table_name)
                    if avg_content_length > 500:
                        content_analysis["high_value_tables"].append(table_name)
                    if row_count < 5:
                        content_analysis["sparse_tables"].append(table_name)

        except Exception:
            continue

    return content_analysis


def _analyze_schema_for_discovery(
    db, tables: List[str], focus_area: Optional[str], depth: str
) -> Dict[str, Any]:
    """Analyze schema structure and organization."""
    schema_analysis = {
        "total_columns": 0,
        "text_columns_by_table": {},
        "well_structured_tables": [],
        "schema_issues": [],
    }

    target_tables = [focus_area] if focus_area and focus_area in tables else tables

    for table_name in target_tables:
        try:
            schema_result = db.describe_table(table_name)
            if schema_result.get("success"):
                columns = schema_result.get("columns", [])
                schema_analysis["total_columns"] += len(columns)

                # Find text columns
                text_columns = [
                    col for col in columns if "TEXT" in col.get("type", "").upper()
                ]
                schema_analysis["text_columns_by_table"][table_name] = len(text_columns)

                # Check for well-structured tables
                has_id = any(col.get("name") == "id" for col in columns)
                has_timestamp = any(
                    "timestamp" in col.get("name", "").lower() for col in columns
                )
                has_text_content = len(text_columns) > 0

                if has_id and has_timestamp and has_text_content:
                    schema_analysis["well_structured_tables"].append(table_name)

                # Identify schema issues
                if len(columns) < 2:
                    schema_analysis["schema_issues"].append(
                        f"Table '{table_name}' has very few columns"
                    )
                if not has_id:
                    schema_analysis["schema_issues"].append(
                        f"Table '{table_name}' lacks ID column"
                    )

        except Exception:
            continue

    return schema_analysis


def _assess_content_quality(
    db, tables: List[str], focus_area: Optional[str], depth: str
) -> Dict[str, Any]:
    """Assess overall content quality."""
    quality_analysis = {
        "quality_scores": {},
        "overall_quality": 0.0,
        "improvement_opportunities": [],
        "quality_distribution": {"high": 0, "medium": 0, "low": 0},
    }

    target_tables = [focus_area] if focus_area and focus_area in tables else tables
    total_score = 0
    table_count = 0

    for table_name in target_tables:
        try:
            rows_result = db.read_rows(table_name)
            if rows_result.get("success"):
                rows = rows_result.get("rows", [])

                if not rows:
                    quality_analysis["quality_scores"][table_name] = 0.0
                    quality_analysis["improvement_opportunities"].append(
                        f"Table '{table_name}' is empty"
                    )
                    quality_analysis["quality_distribution"]["low"] += 1
                    continue

                # Calculate quality score
                sample_size = min(5, len(rows))
                content_scores = []

                for row in rows[:sample_size]:
                    row_score = 0
                    non_null_fields = sum(
                        1 for v in row.values() if v is not None and str(v).strip()
                    )
                    total_content_length = sum(
                        len(str(v)) for v in row.values() if v is not None
                    )

                    # Score based on completeness and content richness
                    if non_null_fields > 2:
                        row_score += 3
                    if total_content_length > 100:
                        row_score += 4
                    if total_content_length > 500:
                        row_score += 3

                    content_scores.append(min(10, row_score))

                table_quality = (
                    sum(content_scores) / len(content_scores) if content_scores else 0
                )
                quality_analysis["quality_scores"][table_name] = round(table_quality, 1)

                # Categorize quality
                if table_quality >= 7:
                    quality_analysis["quality_distribution"]["high"] += 1
                elif table_quality >= 4:
                    quality_analysis["quality_distribution"]["medium"] += 1
                else:
                    quality_analysis["quality_distribution"]["low"] += 1
                    quality_analysis["improvement_opportunities"].append(
                        f"Table '{table_name}' has low content quality (score: {table_quality:.1f})"
                    )

                total_score += table_quality
                table_count += 1

        except Exception:
            continue

    quality_analysis["overall_quality"] = (
        round(total_score / table_count, 1) if table_count > 0 else 0.0
    )

    return quality_analysis


def _analyze_search_readiness(
    db, tables: List[str], focus_area: Optional[str]
) -> Dict[str, Any]:
    """Analyze readiness for effective searching."""
    search_analysis = {
        "semantic_ready_tables": [],
        "text_searchable_tables": [],
        "search_optimization_needed": [],
        "embedding_coverage": {},
    }

    target_tables = [focus_area] if focus_area and focus_area in tables else tables

    for table_name in target_tables:
        try:
            # Check schema for text content
            schema_result = db.describe_table(table_name)
            if schema_result.get("success"):
                columns = schema_result.get("columns", [])
                text_columns = [
                    col for col in columns if "TEXT" in col.get("type", "").upper()
                ]

                if text_columns:
                    search_analysis["text_searchable_tables"].append(table_name)

                    # Check semantic search readiness if available
                    if is_semantic_search_available():
                        embedding_stats = db.get_embedding_stats(table_name)
                        if embedding_stats.get("success"):
                            coverage = embedding_stats.get("coverage_percent", 0)
                            search_analysis["embedding_coverage"][table_name] = coverage

                            if coverage > 80:
                                search_analysis["semantic_ready_tables"].append(
                                    table_name
                                )
                            elif len(text_columns) > 0:
                                search_analysis["search_optimization_needed"].append(
                                    table_name
                                )

        except Exception:
            continue

    return search_analysis


def _generate_discovery_insights(
    discovery_goal: str, overview: Dict[str, Any], focus_area: Optional[str], depth: str
) -> tuple:
    """Generate insights and recommendations based on discovery results."""
    insights = []
    recommendations = []
    next_steps = []

    total_tables = overview.get("total_tables", 0)
    total_rows = overview.get("total_rows", 0)

    # Goal-specific insights
    if discovery_goal == "understand_content":
        insights.append(
            f"Memory bank contains {total_tables} tables with {total_rows} total rows"
        )

        high_value_tables = overview.get("high_value_tables", [])
        if high_value_tables:
            insights.append(
                f"High-value content found in: {', '.join(high_value_tables[:3])}"
            )
            recommendations.append(
                f"Focus search efforts on high-value tables: {', '.join(high_value_tables)}"
            )
            next_steps.append(
                f"Use auto_smart_search() to explore content in {high_value_tables[0]}"
            )

        sparse_tables = overview.get("sparse_tables", [])
        if sparse_tables:
            insights.append(f"Sparse tables detected: {', '.join(sparse_tables)}")
            recommendations.append("Consider consolidating or expanding sparse tables")

    elif discovery_goal == "find_patterns":
        text_rich_tables = overview.get("text_rich_tables", [])
        if text_rich_tables:
            insights.append(
                f"Text-rich content found in {len(text_rich_tables)} tables"
            )
            next_steps.append("Use semantic search to find content patterns")

        quality_scores = overview.get("quality_scores", {})
        if quality_scores:
            avg_quality = sum(quality_scores.values()) / len(quality_scores)
            insights.append(f"Average content quality: {avg_quality:.1f}/10")

    elif discovery_goal == "explore_structure":
        well_structured = overview.get("well_structured_tables", [])
        if well_structured:
            insights.append(f"Well-structured tables: {', '.join(well_structured)}")
            recommendations.append("Use well-structured tables as primary data sources")

        schema_issues = overview.get("schema_issues", [])
        if schema_issues:
            insights.extend(schema_issues[:3])  # Show first 3 issues

    elif discovery_goal == "assess_quality":
        overall_quality = overview.get("overall_quality", 0)
        insights.append(f"Overall content quality score: {overall_quality}/10")

        improvement_opportunities = overview.get("improvement_opportunities", [])
        recommendations.extend(improvement_opportunities[:3])

    elif discovery_goal == "prepare_search":
        semantic_ready = overview.get("semantic_ready_tables", [])
        optimization_needed = overview.get("search_optimization_needed", [])

        if semantic_ready:
            insights.append(f"Semantic search ready for {len(semantic_ready)} tables")
            next_steps.append("Use auto_semantic_search() for conceptual queries")

        if optimization_needed:
            insights.append(
                f"Search optimization needed for {len(optimization_needed)} tables"
            )
            next_steps.append(
                f"Set up embeddings for: {', '.join(optimization_needed[:2])}"
            )

    # Universal recommendations
    if overview.get("semantic_search_available"):
        recommendations.append("Use auto_smart_search() for best search results")
    else:
        recommendations.append(
            "Install sentence-transformers for semantic search capabilities"
        )

    if not next_steps:
        next_steps.append("Use explore_tables() for detailed content examination")
        next_steps.append("Try auto_smart_search() to find specific information")

    return insights, recommendations, next_steps


def _generate_quick_actions(
    discovery_goal: str, overview: Dict[str, Any], focus_area: Optional[str]
) -> List[Dict[str, Any]]:
    """Generate quick action suggestions."""
    actions = []

    high_value_tables = overview.get("high_value_tables", [])

    if discovery_goal == "understand_content" and high_value_tables:
        actions.append(
            {
                "action": "Explore High-Value Content",
                "tool": "read_rows",
                "params": {"table_name": high_value_tables[0]},
                "description": f"Examine content in {high_value_tables[0]} table",
            }
        )

    if overview.get("semantic_search_available"):
        actions.append(
            {
                "action": "Smart Search",
                "tool": "auto_smart_search",
                "params": {"query": "important recent information", "limit": 5},
                "description": "Find important content using intelligent search",
            }
        )

    actions.append(
        {
            "action": "Quality Assessment",
            "tool": "get_content_health_score",
            "params": {},
            "description": "Get detailed quality metrics and recommendations",
        }
    )

    return actions


def _store_discovery_pattern(db, discovery_session: Dict[str, Any]) -> None:
    """Store discovery pattern for learning (if agent learning table exists)."""
    try:
        # Check if discovery_patterns table exists
        tables_result = db.list_tables()
        if tables_result.get("success") and "discovery_patterns" in tables_result.get(
            "tables", []
        ):
            # Store the discovery session
            db.insert_row(
                "discovery_patterns",
                {
                    "agent_id": discovery_session.get("agent_id"),
                    "goal": discovery_session.get("goal"),
                    "focus_area": discovery_session.get("focus_area"),
                    "depth": discovery_session.get("depth"),
                    "steps_completed": str(
                        discovery_session.get("steps_completed", [])
                    ),
                    "success": True,
                    "timestamp": discovery_session.get("timestamp"),
                },
            )
    except Exception:
        # Silently fail if learning storage isn't available
        pass


def _customize_template(template: Dict[str, Any], customize_for: str) -> Dict[str, Any]:
    """Customize template for specific domain or topic."""
    customized = template.copy()

    # Add customization note
    customized["customized_for"] = customize_for
    customized["customization_note"] = f"Template customized for: {customize_for}"

    # Modify search queries in workflow to include customization
    for step in customized.get("workflow", []):
        if step.get("tool") in [
            "auto_smart_search",
            "auto_semantic_search",
            "search_content",
        ]:
            params = step.get("params", {})
            if "query" in params and params["query"].startswith("REPLACE_WITH"):
                # Keep the placeholder for user customization
                continue
            elif "query" in params:
                # Add customization to existing query
                params["query"] = f"{customize_for} {params['query']}"

    return customized


# Relationship discovery helper functions


def _discover_foreign_keys(db, target_table: str, all_tables: List[str]) -> List[str]:
    """Discover foreign key relationships."""
    relationships = []

    try:
        # Get target table schema
        target_schema = db.describe_table(target_table)
        if not target_schema.get("success"):
            return relationships

        target_columns = target_schema.get("columns", [])
        target_col_names = [col.get("name", "") for col in target_columns]

        # Check other tables for potential foreign key references
        for other_table in all_tables:
            if other_table == target_table:
                continue

            try:
                other_schema = db.describe_table(other_table)
                if other_schema.get("success"):
                    other_columns = other_schema.get("columns", [])

                    for col in other_columns:
                        col_name = col.get("name", "")
                        # Look for naming patterns that suggest foreign keys
                        if col_name.endswith("_id") or col_name.endswith("Id"):
                            potential_ref = col_name.replace("_id", "").replace(
                                "Id", ""
                            )
                            if (
                                potential_ref == target_table
                                or f"{potential_ref}s" == target_table
                            ):
                                relationships.append(f"{other_table}.{col_name}")

                        # Look for exact column name matches (potential shared keys)
                        if col_name in target_col_names and col_name != "id":
                            relationships.append(
                                f"{other_table}.{col_name} (shared key)"
                            )

            except Exception:
                continue

    except Exception:
        pass

    return relationships


def _discover_semantic_relationships(
    db, target_table: str, all_tables: List[str], threshold: float
) -> List[Dict[str, Any]]:
    """Discover semantic similarity relationships."""
    relationships = []

    if not is_semantic_search_available():
        return relationships

    try:
        # Get sample content from target table
        target_rows = db.read_rows(target_table)
        if not target_rows.get("success") or not target_rows.get("rows"):
            return relationships

        # Create a sample query from target table content
        sample_row = target_rows["rows"][0]
        sample_text = " ".join(str(v) for v in sample_row.values() if v is not None)[
            :200
        ]

        if len(sample_text.strip()) < 10:
            return relationships

        # Search for similar content in other tables
        for other_table in all_tables:
            if other_table == target_table:
                continue

            try:
                # Try semantic search in the other table
                search_result = db.semantic_search(
                    sample_text,
                    [other_table],
                    "embedding",
                    None,
                    threshold,
                    3,
                    "all-MiniLM-L6-v2",
                )

                if search_result.get("success") and search_result.get("results"):
                    results = search_result["results"]
                    avg_similarity = sum(
                        r.get("similarity_score", 0) for r in results
                    ) / len(results)

                    if avg_similarity >= threshold:
                        relationships.append(
                            {
                                "table": other_table,
                                "similarity": round(avg_similarity, 2),
                                "related_content_count": len(results),
                            }
                        )

            except Exception:
                continue

    except Exception:
        pass

    return relationships


def _discover_temporal_relationships(
    db, target_table: str, all_tables: List[str]
) -> List[str]:
    """Discover temporal pattern relationships."""
    relationships = []

    try:
        # Check if target table has timestamp columns
        target_schema = db.describe_table(target_table)
        if not target_schema.get("success"):
            return relationships

        target_columns = target_schema.get("columns", [])
        target_has_timestamp = any(
            "timestamp" in col.get("name", "").lower()
            or "date" in col.get("name", "").lower()
            or "time" in col.get("name", "").lower()
            for col in target_columns
        )

        if not target_has_timestamp:
            return relationships

        # Check other tables for similar timestamp patterns
        for other_table in all_tables:
            if other_table == target_table:
                continue

            try:
                other_schema = db.describe_table(other_table)
                if other_schema.get("success"):
                    other_columns = other_schema.get("columns", [])
                    other_has_timestamp = any(
                        "timestamp" in col.get("name", "").lower()
                        or "date" in col.get("name", "").lower()
                        or "time" in col.get("name", "").lower()
                        for col in other_columns
                    )

                    if other_has_timestamp:
                        relationships.append(other_table)

            except Exception:
                continue

    except Exception:
        pass

    return relationships


def _discover_naming_relationships(
    target_table: str, all_tables: List[str]
) -> List[str]:
    """Discover relationships based on naming conventions."""
    relationships = []

    # Look for tables with similar names or naming patterns
    target_lower = target_table.lower()

    for other_table in all_tables:
        if other_table == target_table:
            continue

        other_lower = other_table.lower()

        # Check for plural/singular relationships
        if (target_lower.endswith("s") and other_lower == target_lower[:-1]) or (
            other_lower.endswith("s") and target_lower == other_lower[:-1]
        ):
            relationships.append(other_table)
            continue

        # Check for common prefixes or suffixes
        if len(target_lower) > 3 and len(other_lower) > 3:
            # Common prefix (at least 4 characters)
            if target_lower[:4] == other_lower[:4]:
                relationships.append(other_table)
                continue

            # Common suffix (at least 4 characters)
            if target_lower[-4:] == other_lower[-4:]:
                relationships.append(other_table)
                continue

        # Check for semantic name relationships
        name_words = set(target_lower.split("_"))
        other_words = set(other_lower.split("_"))

        # If tables share significant word overlap
        if len(name_words.intersection(other_words)) > 0:
            relationships.append(other_table)

    return relationships


def _identify_strongest_connections(
    relationships: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """Identify the strongest connections across all relationships."""
    connections = []

    for table, rels in relationships.items():
        # Count total connections for this table
        total_connections = (
            len(rels.get("foreign_key_refs", []))
            + len(rels.get("semantic_similar", []))
            + len(rels.get("temporal_related", []))
            + len(rels.get("naming_related", []))
        )

        if total_connections > 0:
            connections.append(
                {
                    "table": table,
                    "total_connections": total_connections,
                    "connection_types": {
                        "structural": len(rels.get("foreign_key_refs", [])),
                        "semantic": len(rels.get("semantic_similar", [])),
                        "temporal": len(rels.get("temporal_related", [])),
                        "naming": len(rels.get("naming_related", [])),
                    },
                }
            )

    # Sort by total connections and return top 5
    connections.sort(key=lambda x: x["total_connections"], reverse=True)
    return connections[:5]


def _generate_relationship_recommendations(
    relationships: Dict[str, Any], insights: List[str]
) -> List[str]:
    """Generate actionable recommendations based on discovered relationships."""
    recommendations = []

    # Find tables with many connections
    highly_connected = []
    for table, rels in relationships.items():
        total_connections = (
            len(rels.get("foreign_key_refs", []))
            + len(rels.get("semantic_similar", []))
            + len(rels.get("temporal_related", []))
            + len(rels.get("naming_related", []))
        )
        if total_connections >= 3:
            highly_connected.append(table)

    if highly_connected:
        recommendations.append(
            f"Focus queries on highly connected tables: {', '.join(highly_connected[:3])}"
        )

    # Find tables with semantic relationships
    semantic_tables = []
    for table, rels in relationships.items():
        if rels.get("semantic_similar"):
            semantic_tables.append(table)

    if semantic_tables:
        recommendations.append(
            f"Use semantic search across related tables: {', '.join(semantic_tables[:3])}"
        )

    # Find tables with temporal relationships
    temporal_tables = []
    for table, rels in relationships.items():
        if rels.get("temporal_related"):
            temporal_tables.append(table)

    if temporal_tables:
        recommendations.append(
            f"Consider temporal analysis for time-related tables: {', '.join(temporal_tables[:3])}"
        )

    if not recommendations:
        recommendations.append(
            "Consider adding more structured relationships or content to improve discoverability"
        )

    return recommendations
