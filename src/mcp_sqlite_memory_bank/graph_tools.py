"""
Generic Knowledge Graph MCP Tools

These tools provide schema-agnostic knowledge graph visualization
that works with ANY database schema without requiring specific
node/edge table structures.

Author: Robert Meisner
"""

from typing import Optional, Dict, Any, List, cast
from .types import ToolResponse
from .database import SQLiteMemoryDatabase
from .graph_analyzer import GenericGraphAnalyzer


def analyze_graph_potential_impl(db: SQLiteMemoryDatabase) -> ToolResponse:
    """
    Analyze the current database schema to assess its potential
    for knowledge graph visualization.

    Returns insights about:
    - Detected node types and relationship patterns
    - Tables suitable for graph visualization
    - Recommended graph analysis approaches
    - Estimated graph complexity and size
    """
    try:
        analyzer = GenericGraphAnalyzer(db)
        schema_analysis = analyzer.analyze_schema_structure()

        if "error" in schema_analysis:
            return cast(
                ToolResponse, {"success": False, "error": schema_analysis["error"]}
            )

        # Analyze graph potential
        tables = schema_analysis.get("tables", {})
        total_nodes = sum(info.get("row_count", 0) for info in tables.values())
        node_types = list(
            set(info.get("detected_node_type", "record") for info in tables.values())
        )
        text_columns = len(schema_analysis.get("text_columns", []))

        # Assess graph visualization potential
        potential_score = min(
            10,
            (
                min(3, len(tables))  # Table diversity (max 3 points)
                + min(2, len(node_types))  # Node type diversity (max 2 points)
                + min(3, text_columns // 2)  # Semantic potential (max 3 points)
                + min(2, min(total_nodes // 10, 2))  # Data volume (max 2 points)
            ),
        )

        potential_assessment = "Low"
        if potential_score >= 7:
            potential_assessment = "High"
        elif potential_score >= 4:
            potential_assessment = "Medium"

        recommendations = []
        if text_columns >= 3:
            recommendations.append(
                "Enable semantic relationships for richer connections"
            )
        if len(tables) >= 3:
            recommendations.append(
                "Use structural analysis to find foreign key relationships"
            )
        if total_nodes > 50:
            recommendations.append(
                "Consider filtering by node type or date range for clarity"
            )
        if len(node_types) == 1:
            recommendations.append(
                "Data appears homogeneous - consider categorization by content"
            )

        return cast(
            ToolResponse,
            {
                "success": True,
                "graph_potential": {
                    "score": potential_score,
                    "assessment": potential_assessment,
                    "total_potential_nodes": total_nodes,
                    "detected_node_types": node_types,
                    "tables_with_text": text_columns,
                    "recommendations": recommendations,
                },
                "schema_analysis": schema_analysis,
            },
        )

    except Exception as e:
        return cast(
            ToolResponse,
            {"success": False, "error": f"Failed to analyze graph potential: {str(e)}"},
        )


def build_knowledge_graph_impl(
    db: SQLiteMemoryDatabase,
    include_semantic: bool = True,
    semantic_threshold: float = 0.5,
    max_nodes: int = 100,
    node_types: Optional[List[str]] = None,
    layout_algorithm: str = "force",
) -> ToolResponse:
    """
    Build a knowledge graph from the current database schema automatically.

    Works with ANY schema by detecting relationships through:
    - Structural analysis (foreign keys, references)
    - Semantic analysis (content similarity)
    - Pattern analysis (naming conventions)

    Args:
        include_semantic: Enable semantic relationship detection
        semantic_threshold: Minimum similarity for semantic edges (0.0-1.0)
        max_nodes: Maximum nodes to include in visualization
        node_types: Filter to specific node types (None = all types)
        layout_algorithm: Graph layout algorithm ('force', 'circular', 'hierarchical')
    """
    try:
        analyzer = GenericGraphAnalyzer(db)
        graph_result = analyzer.build_generic_graph(
            include_semantic=include_semantic,
            semantic_threshold=semantic_threshold,
            max_nodes=max_nodes,
        )

        if not graph_result.get("success"):
            return {
                "success": False,
                "error": graph_result.get("error", "Failed to build graph"),
            }

        graph_data = graph_result["graph"]

        # Apply node type filtering if specified
        if node_types:
            filtered_nodes = [
                node for node in graph_data["nodes"] if node["nodeType"] in node_types
            ]
            # Also filter edges to only include nodes that remain
            remaining_node_ids = {node["id"] for node in filtered_nodes}
            filtered_edges = [
                edge
                for edge in graph_data["edges"]
                if edge["source"] in remaining_node_ids
                and edge["target"] in remaining_node_ids
            ]

            graph_data["nodes"] = filtered_nodes
            graph_data["edges"] = filtered_edges
            graph_data["statistics"]["node_count"] = len(filtered_nodes)
            graph_data["statistics"]["edge_count"] = len(filtered_edges)

        # Add layout information
        graph_data["layout"] = {
            "algorithm": layout_algorithm,
            "parameters": _get_layout_parameters(
                layout_algorithm, len(graph_data["nodes"])
            ),
        }

        return {
            "success": True,
            "knowledge_graph": graph_data,
            "visualization_ready": True,
            "schema_analysis": graph_result.get("schema_analysis", {}),
        }

    except Exception as e:
        return {"success": False, "error": f"Failed to build knowledge graph: {str(e)}"}


def get_graph_insights_impl(db: SQLiteMemoryDatabase) -> ToolResponse:
    """
    Analyze the knowledge graph structure and provide actionable insights
    about the data organization, relationship patterns, and opportunities
    for improved knowledge management.
    """
    try:
        # First build the graph
        graph_result = build_knowledge_graph_impl(db, max_nodes=200)
        if not graph_result.get("success"):
            return graph_result

        graph_data = graph_result["knowledge_graph"]
        nodes = graph_data["nodes"]
        edges = graph_data["edges"]

        if not nodes:
            return {
                "success": True,
                "insights": {
                    "summary": "No data available for graph analysis",
                    "recommendations": [
                        "Add data to your memory bank to enable graph insights"
                    ],
                },
            }

        # Analyze node distribution
        node_types = {}
        table_distribution = {}
        for node in nodes:
            node_type = node["nodeType"]
            table = node["sourceTable"]
            node_types[node_type] = node_types.get(node_type, 0) + 1
            table_distribution[table] = table_distribution.get(table, 0) + 1

        # Analyze relationship patterns
        relationship_types = {}
        for edge in edges:
            rel_type = edge["relationshipType"]
            relationship_types[rel_type] = relationship_types.get(rel_type, 0) + 1

        # Calculate graph metrics
        total_nodes = len(nodes)
        total_edges = len(edges)
        connectivity = (total_edges / total_nodes) if total_nodes > 0 else 0

        # Identify isolated nodes (no connections)
        connected_nodes = set()
        for edge in edges:
            connected_nodes.add(edge["source"])
            connected_nodes.add(edge["target"])
        isolated_nodes = [node for node in nodes if node["id"] not in connected_nodes]

        # Generate insights and recommendations
        insights = {
            "summary": f"Knowledge graph contains {total_nodes} nodes and {total_edges} relationships",
            "node_analysis": {
                "total_nodes": total_nodes,
                "node_types": node_types,
                "table_distribution": table_distribution,
                "isolated_nodes": len(isolated_nodes),
            },
            "relationship_analysis": {
                "total_relationships": total_edges,
                "relationship_types": relationship_types,
                "average_connectivity": round(
                    connectivity,
                    2),
            },
            "recommendations": [],
        }

        # Generate recommendations based on analysis
        if len(isolated_nodes) > total_nodes * 0.3:
            insights["recommendations"].append(
                f"High isolation: {len(isolated_nodes)} nodes have no connections. "
                f"Consider adding semantic relationships or reviewing data organization.")

        if connectivity < 0.5:
            insights["recommendations"].append(
                "Low connectivity detected. Enable semantic relationship detection to discover hidden connections."
            )

        if len(node_types) == 1:
            insights["recommendations"].append(
                "All nodes are the same type. Consider adding categorization or creating different entity types."
            )

        if "semantic" not in relationship_types and len(table_distribution) > 1:
            insights["recommendations"].append(
                "No semantic relationships found. Enable semantic analysis to discover content-based connections."
            )

        if not insights["recommendations"]:
            insights["recommendations"].append(
                "Graph structure looks healthy! Consider exploring different visualization layouts or adding more data."
            )

        return {
            "success": True,
            "insights": insights,
            "isolated_nodes": [
                {"id": node["id"], "label": node["label"]}
                for node in isolated_nodes[:10]
            ],
            "graph_health_score": min(
                10,
                max(
                    1,
                    int(connectivity * 5 + (1 - len(isolated_nodes) / total_nodes) * 5),
                ),
            ),
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to analyze graph insights: {str(e)}",
        }


def export_graph_data_impl(
    db: SQLiteMemoryDatabase, format_type: str = "json", include_positions: bool = False
) -> ToolResponse:
    """
    Export knowledge graph data in various formats for use in external
    visualization tools or for backup/sharing purposes.

    Args:
        format_type: Export format ('json', 'gexf', 'graphml', 'cypher')
        include_positions: Whether to include node position data
    """
    try:
        # Build the graph
        graph_result = build_knowledge_graph_impl(db, max_nodes=500)
        if not graph_result.get("success"):
            return graph_result

        graph_data = graph_result["knowledge_graph"]

        if format_type.lower() == "json":
            export_data = graph_data
            if not include_positions:
                # Remove position data from nodes
                for node in export_data["nodes"]:
                    node.pop("x", None)
                    node.pop("y", None)

        elif format_type.lower() == "cypher":
            # Generate Cypher CREATE statements for Neo4j
            cypher_statements = []

            # Create nodes
            for node in graph_data["nodes"]:
                label = node["nodeType"].capitalize()
                properties = {
                    "id": node["id"],
                    "label": node["label"],
                    "sourceTable": node["sourceTable"],
                }
                props_str = ", ".join([f"{k}: '{v}'" for k, v in properties.items()])
                cypher_statements.append(f"CREATE (:{label} {{{props_str}}})")

            # Create relationships
            for edge in graph_data["edges"]:
                rel_type = edge["relationshipType"].upper()
                cypher_statements.append(
                    f"MATCH (a {{id: '{edge['source']}'}}), (b {{id: '{edge['target']}'}})"
                    f"CREATE (a)-[:{rel_type}]->(b)"
                )

            export_data = {
                "format": "cypher",
                "statements": cypher_statements,
                "total_statements": len(cypher_statements),
            }

        else:
            return {
                "success": False,
                "error": f"Unsupported export format: {format_type}. Supported: json, cypher",
            }

        return {
            "success": True,
            "export_data": export_data,
            "format": format_type,
            "node_count": len(graph_data["nodes"]),
            "edge_count": len(graph_data["edges"]),
        }

    except Exception as e:
        return {"success": False, "error": f"Failed to export graph data: {str(e)}"}


def _get_layout_parameters(algorithm: str, node_count: int) -> Dict[str, Any]:
    """Get appropriate layout parameters based on algorithm and node count."""
    if algorithm == "force":
        return {
            "iterations": min(300, max(50, node_count * 2)),
            "strength": -200 if node_count < 50 else -400,
            "distance": 100 if node_count < 50 else 150,
        }
    elif algorithm == "circular":
        return {"radius": max(100, node_count * 3)}
    elif algorithm == "hierarchical":
        return {"direction": "vertical", "level_separation": 80, "node_separation": 60}
    else:
        return {}
