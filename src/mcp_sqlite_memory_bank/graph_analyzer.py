"""
Generic Knowledge Graph Analyzer for SQLite Memory Bank

This module automatically discovers graph relationships in ANY schema,
making knowledge graph visualization work across different projects
without requiring specific node/edge table structures.

Author: Robert Meisner
"""

from typing import Any, Dict, List
from dataclasses import dataclass
import re
from .database import SQLiteMemoryDatabase


@dataclass
class GraphNode:
    """Universal node representation for any schema."""

    id: str
    label: str
    node_type: str  # 'record', 'concept', 'person', 'project', 'category'
    source_table: str
    source_record_id: Any
    properties: Dict[str, Any]
    # Visual properties
    color: str = "#1976D2"
    size: int = 20
    shape: str = "circle"


@dataclass
class GraphEdge:
    """Universal edge representation for any relationship."""

    id: str
    source_id: str
    target_id: str
    relationship_type: str  # 'structural', 'semantic', 'temporal', 'inferred'
    strength: float  # 0.0 to 1.0
    properties: Dict[str, Any]
    # Visual properties
    color: str = "#666666"
    thickness: int = 2
    style: str = "solid"  # 'solid', 'dashed', 'dotted'


class GenericGraphAnalyzer:
    """
    Analyzes any SQLite memory bank schema and builds knowledge graphs
    automatically without requiring specific node/edge table structures.
    """

    def __init__(self, db: SQLiteMemoryDatabase):
        self.db = db

        # Node type detection patterns
        self.node_patterns = {
            "person": re.compile(r"(name|user|author|owner|person|member)", re.I),
            "project": re.compile(r"(project|initiative|task|goal|plan)", re.I),
            "concept": re.compile(r"(concept|idea|topic|category|theme)", re.I),
            "decision": re.compile(r"(decision|choice|resolution|conclusion)", re.I),
            "document": re.compile(r"(document|note|article|content|text)", re.I),
        }

        # Relationship type patterns
        self.relationship_patterns = {
            "ownership": re.compile(r"(created_by|owned_by|author|owner)", re.I),
            "hierarchy": re.compile(r"(parent|child|super|sub)", re.I),
            "reference": re.compile(r"(ref|reference|link|related)", re.I),
            "temporal": re.compile(r"(created|updated|modified|timestamp)", re.I),
        }

    def analyze_schema_structure(self) -> Dict[str, Any]:
        """
        Analyze the entire database schema to understand its structure
        and identify potential graph relationships.
        """
        try:
            tables_result = self.db.list_tables()
            if not tables_result.get("success"):
                return {"error": "Failed to list tables", "schema_analysis": {}}

            tables = tables_result.get("tables", [])
            schema_analysis = {
                "tables": {},
                "foreign_keys": [],
                "potential_relationships": [],
                "text_columns": [],
            }

            for table_name in tables:
                # Get table schema
                table_info_result = self.db.describe_table(table_name)
                if not table_info_result.get("success"):
                    continue

                columns = {col["name"]: col for col in table_info_result.get("columns", [])}

                schema_analysis["tables"][table_name] = {
                    "columns": columns,
                    "row_count": self._get_row_count(table_name),
                    "detected_node_type": self._detect_node_type(table_name, columns),
                    "text_columns": self._find_text_columns(columns),
                    "reference_columns": self._find_reference_columns(columns),
                }

                # Find text columns for semantic analysis
                for col_name, col_info in columns.items():
                    if "TEXT" in col_info["type"].upper():
                        schema_analysis["text_columns"].append({"table": table_name, "column": col_name})

            return schema_analysis

        except Exception as e:
            return {"error": str(e), "schema_analysis": {}}

    def build_generic_graph(
        self,
        include_semantic: bool = True,
        semantic_threshold: float = 0.5,
        max_nodes: int = 100,
    ) -> Dict[str, Any]:
        """
        Build a knowledge graph from ANY schema by detecting relationships
        automatically across all tables.
        """
        try:
            # Analyze schema first
            schema = self.analyze_schema_structure()
            if "error" in schema:
                return schema

            nodes = []
            edges = []

            # Build nodes from all tables
            for table_name, table_info in schema["tables"].items():
                table_nodes = self._build_nodes_from_table(
                    table_name,
                    table_info,
                    max_nodes_per_table=max(10, max_nodes // len(schema["tables"])),
                )
                nodes.extend(table_nodes)

            # Build structural relationships (foreign keys, references)
            structural_edges = self._detect_structural_relationships(schema)
            edges.extend(structural_edges)

            # Build semantic relationships if requested
            if include_semantic and schema["text_columns"]:
                semantic_edges = self._detect_semantic_relationships(schema, threshold=semantic_threshold)
                edges.extend(semantic_edges)

            # Build inferred relationships (naming patterns)
            inferred_edges = self._detect_inferred_relationships(schema)
            edges.extend(inferred_edges)

            return {
                "success": True,
                "graph": {
                    "nodes": [self._node_to_dict(n) for n in nodes],
                    "edges": [self._edge_to_dict(e) for e in edges],
                    "statistics": {
                        "node_count": len(nodes),
                        "edge_count": len(edges),
                        "tables_analyzed": len(schema["tables"]),
                        "relationship_types": len(set(e.relationship_type for e in edges)),
                    },
                },
                "schema_analysis": schema,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_row_count(self, table_name: str) -> int:
        """Get the number of rows in a table."""
        try:
            result = self.db.read_rows(table_name, where={})
            if result.get("success"):
                return len(result.get("rows", []))
            return 0
        except BaseException:
            return 0

    def _detect_node_type(self, table_name: str, columns: Dict) -> str:
        """Detect what type of nodes this table likely represents."""
        table_lower = table_name.lower()
        column_names = " ".join(columns.keys()).lower()

        # Check table name and column patterns
        for node_type, pattern in self.node_patterns.items():
            if pattern.search(table_lower) or pattern.search(column_names):
                return node_type

        return "record"  # Default fallback

    def _find_text_columns(self, columns: Dict) -> List[str]:
        """Find columns that contain text suitable for semantic analysis."""
        text_columns = []
        for col_name, col_info in columns.items():
            if "TEXT" in col_info["type"].upper():
                # Prioritize meaningful text columns
                if any(
                    keyword in col_name.lower()
                    for keyword in [
                        "content",
                        "description",
                        "text",
                        "body",
                        "note",
                        "comment",
                    ]
                ):
                    text_columns.append(col_name)
        return text_columns

    def _find_reference_columns(self, columns: Dict) -> List[str]:
        """Find columns that likely reference other records."""
        ref_columns = []
        for col_name, col_info in columns.items():
            col_lower = col_name.lower()
            if col_lower.endswith("_id") or col_lower.endswith("_ref") or "reference" in col_lower or "parent" in col_lower:
                ref_columns.append(col_name)
        return ref_columns

    def _build_nodes_from_table(self, table_name: str, table_info: Dict, max_nodes_per_table: int) -> List[GraphNode]:
        """Build graph nodes from a table's records."""
        nodes = []
        try:
            # Get sample of records from the table
            result = self.db.read_rows(table_name, where={})
            if not result.get("success"):
                rows = []
            else:
                rows = result.get("rows", [])[:max_nodes_per_table]

            for row in rows:
                # Create a meaningful label for the node
                label = self._create_node_label(row, table_name)

                node = GraphNode(
                    id=f"{table_name}_{row.get('id', len(nodes))}",
                    label=label,
                    node_type=table_info["detected_node_type"],
                    source_table=table_name,
                    source_record_id=row.get("id"),
                    properties=row,
                    color=self._get_node_color(table_info["detected_node_type"]),
                    size=min(40, max(15, len(str(label)))),  # Size based on label length
                    shape=self._get_node_shape(table_info["detected_node_type"]),
                )
                nodes.append(node)

        except Exception as e:
            # If table reading fails, create a table-level node
            nodes.append(
                GraphNode(
                    id=f"table_{table_name}",
                    label=f"Table: {table_name}",
                    node_type="table",
                    source_table=table_name,
                    source_record_id=None,
                    properties={"table_name": table_name, "error": str(e)},
                    color="#FF5722",
                    size=30,
                    shape="square",
                )
            )

        return nodes

    def _create_node_label(self, row: Dict, table_name: str) -> str:
        """Create a meaningful label for a node based on its data."""
        # Priority order for label fields
        label_fields = ["title", "name", "label", "decision_name", "topic", "content"]

        for field in label_fields:
            if field in row and row[field]:
                label = str(row[field])
                # Truncate if too long
                return label[:50] + "..." if len(label) > 50 else label

        # Fallback to table name + ID
        record_id = row.get("id", "unknown")
        return f"{table_name}#{record_id}"

    def _get_node_color(self, node_type: str) -> str:
        """Get color for node type."""
        colors = {
            "person": "#2196F3",  # Blue
            "project": "#4CAF50",  # Green
            "concept": "#FF9800",  # Orange
            "decision": "#9C27B0",  # Purple
            "document": "#607D8B",  # Blue Grey
            "record": "#795548",  # Brown
            "table": "#FF5722",  # Deep Orange
        }
        return colors.get(node_type, "#666666")

    def _get_node_shape(self, node_type: str) -> str:
        """Get shape for node type."""
        shapes = {
            "person": "circle",
            "project": "square",
            "concept": "triangle",
            "decision": "diamond",
            "document": "rectangle",
            "record": "circle",
            "table": "square",
        }
        return shapes.get(node_type, "circle")

    def _detect_structural_relationships(self, schema: Dict) -> List[GraphEdge]:
        """Detect relationships based on database structure (foreign keys, references)."""
        edges = []
        # Implementation would analyze foreign key constraints and reference patterns
        # This is a simplified version - full implementation would be more sophisticated
        return edges

    def _detect_semantic_relationships(self, schema: Dict, threshold: float) -> List[GraphEdge]:
        """Detect relationships based on content similarity."""
        edges = []
        # Implementation would use existing semantic search capabilities
        # to find content-based relationships between records
        return edges

    def _detect_inferred_relationships(self, schema: Dict) -> List[GraphEdge]:
        """Detect relationships based on naming patterns and conventions."""
        edges = []
        # Implementation would analyze column names and data patterns
        # to infer likely relationships
        return edges

    def _node_to_dict(self, node: GraphNode) -> Dict:
        """Convert GraphNode to dictionary for JSON serialization."""
        return {
            "id": node.id,
            "label": node.label,
            "nodeType": node.node_type,
            "sourceTable": node.source_table,
            "sourceRecordId": node.source_record_id,
            "properties": node.properties,
            "color": node.color,
            "size": node.size,
            "shape": node.shape,
        }

    def _edge_to_dict(self, edge: GraphEdge) -> Dict:
        """Convert GraphEdge to dictionary for JSON serialization."""
        return {
            "id": edge.id,
            "source": edge.source_id,
            "target": edge.target_id,
            "relationshipType": edge.relationship_type,
            "strength": edge.strength,
            "properties": edge.properties,
            "color": edge.color,
            "thickness": edge.thickness,
            "style": edge.style,
        }
