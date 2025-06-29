"""
Visualization tools for SQLite Memory Bank.

This module provides tools for generating visual representations of stored data,
including knowledge graphs and relationship diagrams.
"""

import html
import json
import sqlite3
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union, cast
import webbrowser

from ..types import ToolResponse
from ..database import get_database


def generate_knowledge_graph(
    output_path: str = "knowledge_graphs",
    include_temporal: bool = True,
    min_connections: int = 1,
    open_in_browser: bool = False,
) -> ToolResponse:
    """
    🚨 **DEPRECATED - USE create_interactive_d3_graph() INSTEAD**

    ⚠️ This basic knowledge graph tool is deprecated in favor of the premium D3.js
    interactive visualizations. Please use create_interactive_d3_graph() from the
    d3_visualization tools for:
    - Professional enterprise styling
    - Advanced interactivity features
    - Export capabilities (PNG, SVG, JSON)
    - Semantic relationship detection
    - Real-time filtering

    🎯 **MIGRATION PATH**:
    ```python
    # OLD (deprecated)
    generate_knowledge_graph()

    # NEW (recommended)
    create_interactive_d3_graph(
        layout_algorithm="force",
        color_scheme="professional",
        export_formats=["png", "svg"]
    )
    ```

    This function is maintained for backward compatibility but will be removed
    in a future version. All new features are added to the D3.js tools.
    """
    print("⚠️  WARNING: generate_knowledge_graph() is DEPRECATED")
    print("🎯  Please use create_interactive_d3_graph() for premium features")
    print("📖  See d3_visualization tools for modern alternatives")

    # Continue with original implementation for backward compatibility
    try:
        # Get the working directory (where VS Code is running)
        workspace_root = os.getcwd()

        # Create output directory in workspace
        output_dir = os.path.join(workspace_root, output_path)
        os.makedirs(output_dir, exist_ok=True)

        # Get database connection
        db_path = os.environ.get("DB_PATH", "./test.db")
        get_database(db_path)

        # Initialize analyzer
        analyzer = KnowledgeGraphAnalyzer(db_path)

        # Generate the graph
        graph_data = analyzer.generate_graph_data(
            include_temporal=include_temporal, min_connections=min_connections
        )

        # Create timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"knowledge_graph_{timestamp}.html"
        file_path = os.path.join(output_dir, filename)

        # Generate HTML visualization
        html_content = _generate_html_visualization(graph_data)

        # Write to file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        # Convert to file:// URL for clickable link
        file_url = f"file:///{file_path.replace(os.sep, '/')}"

        # Optionally open in browser
        if open_in_browser:
            try:
                webbrowser.open(file_url)
            except Exception:
                pass  # Ignore browser open errors

        # Prepare stats
        nodes_list = cast(List[Dict[str, Any]], graph_data["nodes"])
        edges_list = cast(List[Dict[str, Any]], graph_data["edges"])

        stats = {
            "nodes": len(nodes_list),
            "edges": len(edges_list),
            "tables": len(set(node["table"] for node in nodes_list)),
            "relationship_types": len(set(edge["type"] for edge in edges_list)),
            "file_size_kb": round(os.path.getsize(file_path) / 1024, 2),
        }

        return cast(
            ToolResponse,
            {
                "success": True,
                "file_path": file_path,
                "file_url": file_url,
                "stats": stats,
                "output_directory": output_dir,
                "timestamp": timestamp,
            },
        )

    except Exception as e:
        return cast(
            ToolResponse,
            {
                "success": False,
                "error": f"Failed to generate knowledge graph: {str(e)}",
                "category": "visualization_error",
                "details": {"output_path": output_path},
            },
        )


class KnowledgeGraphAnalyzer:
    """Analyzes database content and generates knowledge graph data."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = sqlite3.connect(db_path)
        self.connection.row_factory = sqlite3.Row

    def __del__(self):
        if hasattr(self, "connection"):
            self.connection.close()

    def generate_graph_data(
        self, include_temporal: bool = True, min_connections: int = 1
    ) -> Dict[str, Union[List[Dict[str, Any]], Dict[str, Any]]]:
        """Generate nodes and edges for the knowledge graph."""

        nodes = []
        edges = []
        node_id_map = {}

        # Get all tables
        tables = self._get_tables()

        for table_name in tables:
            # Get table info and sample data
            self._get_table_info(table_name)
            sample_data = self._get_sample_data(table_name, limit=5)

            # Create nodes for each record
            for row in sample_data:
                row_dict = dict(row)
                node_id = f"{table_name}_{row_dict.get('id', len(nodes))}"

                # Determine node label and description
                label = self._generate_node_label(table_name, row_dict)
                description = self._generate_node_description(table_name, row_dict)

                # Enhanced node styling based on table type
                node_style = self._get_node_style(table_name, row_dict)

                node = {
                    "id": node_id,
                    "label": label,
                    "group": table_name,
                    "table": table_name,
                    "title": description,
                    "data": row_dict,
                    **node_style,  # Merge styling properties
                }

                nodes.append(node)
                node_id_map[node_id] = len(nodes) - 1

        # Generate relationships between nodes
        edges.extend(self._find_foreign_key_relationships(nodes, tables))
        edges.extend(self._find_naming_pattern_relationships(nodes))

        if include_temporal:
            edges.extend(self._find_temporal_relationships(nodes))

        # Apply semantic relationships if embeddings are available
        try:
            edges.extend(self._find_semantic_relationships(nodes))
        except Exception:
            pass  # Semantic relationships are optional

        # Filter nodes by minimum connections if specified
        if min_connections > 1:
            nodes, edges = self._filter_by_connections(nodes, edges, min_connections)

        return {
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "tables": tables,
                "total_nodes": len(nodes),
                "total_edges": len(edges),
                "generation_timestamp": datetime.now().isoformat(),
            },
        }

    def _get_tables(self) -> List[str]:
        """Get list of all user tables."""
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """
        )
        return [row[0] for row in cursor.fetchall()]

    def _get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """Get column information for a table."""
        cursor = self.connection.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        return [dict(row) for row in cursor.fetchall()]

    def _get_sample_data(self, table_name: str, limit: int = 5) -> List[sqlite3.Row]:
        """Get sample data from a table."""
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
        return cursor.fetchall()

    def _generate_node_label(self, table_name: str, row_data: Dict[str, Any]) -> str:
        """Generate a concise label for a node."""
        # Priority order for label fields
        label_candidates = [
            "title",
            "name",
            "decision_name",
            "category",
            "topic",
            "content",
            "note",
        ]

        for candidate in label_candidates:
            if candidate in row_data and row_data[candidate]:
                value = str(row_data[candidate])
                return value[:30] + "..." if len(value) > 30 else value

        # Fallback to table name + ID
        record_id = row_data.get("id", row_data.get("rowid", "?"))
        return f"{table_name}#{record_id}"

    def _generate_node_description(
        self, table_name: str, row_data: Dict[str, Any]
    ) -> str:
        """Generate a detailed description for a node tooltip."""
        lines = [f"Table: {table_name}"]

        # Add key fields to description
        priority_fields = [
            "title",
            "name",
            "decision_name",
            "category",
            "content",
            "note",
        ]
        for field in priority_fields:
            if field in row_data and row_data[field]:
                value = str(row_data[field])
                display_value = value[:100] + "..." if len(value) > 100 else value
                lines.append(f"{field.title()}: {display_value}")

        # Add timestamp if available
        timestamp_fields = ["timestamp", "created_at", "date", "created_date"]
        for field in timestamp_fields:
            if field in row_data and row_data[field]:
                lines.append(f"Time: {row_data[field]}")
                break

        return "\\n".join(lines)

    def _get_node_style(
        self, table_name: str, row_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get enhanced styling for nodes based on table type and content."""
        # Define color schemes for different table types
        table_styles = {
            "project_structure": {
                "color": "#10b981",
                "shape": "box",
                "size": 25,
            },  # Green for structure
            "technical_decisions": {
                "color": "#f59e0b",
                "shape": "diamond",
                "size": 30,
            },  # Orange for decisions
            "user_preferences": {
                "color": "#8b5cf6",
                "shape": "star",
                "size": 28,
            },  # Purple for preferences
            "session_context": {
                "color": "#06b6d4",
                "shape": "triangle",
                "size": 22,
            },  # Cyan for sessions
            "documentation": {
                "color": "#ef4444",
                "shape": "square",
                "size": 24,
            },  # Red for docs
            "conversation_memory": {
                "color": "#84cc16",
                "shape": "dot",
                "size": 20,
            },  # Lime for conversations
            "domain_insights": {
                "color": "#f97316",
                "shape": "ellipse",
                "size": 26,
            },  # Orange for insights
            "unified_memory": {
                "color": "#6366f1",
                "shape": "circle",
                "size": 22,
            },  # Indigo for unified
            "notes": {"color": "#ec4899", "shape": "dot", "size": 18},  # Pink for notes
        }

        # Get base style for table type or use default
        base_style = table_styles.get(
            table_name, {"color": "#64748b", "shape": "dot", "size": 20}
        )

        # Enhance size based on content richness
        content_score = 0
        for key, value in row_data.items():
            if value and len(str(value)) > 50:
                content_score += 1

        # Adjust size based on content richness (more content = larger node)
        size_multiplier = 1 + (content_score * 0.1)
        enhanced_size = int(base_style["size"] * size_multiplier)

        # Determine border color based on data importance
        border_color = (
            "#2563eb"
            if any(key in ["id", "decision_name", "title"] for key in row_data.keys())
            else "#64748b"
        )

        return {
            "color": {
                "background": base_style["color"],
                "border": border_color,
                "highlight": {"background": base_style["color"], "border": "#1d4ed8"},
                "hover": {"background": base_style["color"], "border": "#3b82f6"},
            },
            "shape": base_style["shape"],
            "size": enhanced_size,
            "borderWidth": 3,
            "font": {
                "size": min(16, 12 + content_score),
                "color": "#1f2937",
                "bold": content_score > 2,
            },
        }

    def _find_foreign_key_relationships(
        self, nodes: List[Dict], tables: List[str]
    ) -> List[Dict]:
        """Find relationships based on foreign key patterns."""
        edges = []

        for table_name in tables:
            # Get foreign key info
            cursor = self.connection.cursor()
            cursor.execute(f"PRAGMA foreign_key_list({table_name})")
            foreign_keys = cursor.fetchall()

            for fk in foreign_keys:
                # Extract foreign key details
                from_column = fk[3]  # Column in the current table
                to_table = fk[2]  # Referenced table
                to_column = fk[4]  # Column in the referenced table

                # Find the source and target nodes
                from_node = next(
                    (
                        node
                        for node in nodes
                        if node["table"] == table_name
                        and node.get("column") == from_column
                    ),
                    None,
                )
                to_node = next(
                    (
                        node
                        for node in nodes
                        if node["table"] == to_table and node.get("column") == to_column
                    ),
                    None,
                )

                if from_node and to_node:
                    # Create an edge
                    edges.append(
                        {
                            "from": from_node["id"],
                            "to": to_node["id"],
                            "type": "foreign_key",
                            "title": f"{table_name}.{from_column} -> {to_table}.{to_column}",
                        }
                    )

        return edges

    def _find_naming_pattern_relationships(self, nodes: List[Dict]) -> List[Dict]:
        """Find relationships based on naming patterns and common values."""
        edges = []

        # Group nodes by table and content signature for efficient comparison
        grouped_nodes = {}
        for node in nodes:
            table_name = node["table"]
            content_signature = self._generate_content_signature(node)
            key = (table_name, content_signature)
            if key not in grouped_nodes:
                grouped_nodes[key] = []
            grouped_nodes[key].append(node)

        # Compare nodes within the same group (much more efficient)
        for group in grouped_nodes.values():
            for i, node1 in enumerate(group):
                for node2 in group[i + 1:]:
                    if node1["table"] != node2["table"]:
                        # Check for shared categories or similar content
                        similarity = self._calculate_simple_similarity(node1, node2)
                        if similarity > 0.3:  # Threshold for creating an edge
                            edges.append(
                                {
                                    "from": node1["id"],
                                    "to": node2["id"],
                                    "type": "content_similarity",
                                    "weight": similarity,
                                    "title": f"Content similarity: {similarity:.2f}",
                                }
                            )

        return edges

    def _generate_content_signature(self, node: Dict) -> str:
        """Generate a content signature for efficient grouping."""
        # Create a signature based on key content characteristics
        label = node.get("label", "").lower()
        description = node.get("description", "").lower()

        # Extract key words and create a signature
        key_words = []
        for text in [label, description]:
            words = text.split()[:5]  # Take first 5 words
            key_words.extend(words)

        # Sort and join to create consistent signature
        return "_".join(sorted(set(key_words)))

    def _find_temporal_relationships(self, nodes: List[Dict]) -> List[Dict]:
        """Find relationships based on temporal patterns."""
        edges = []

        # Group nodes by date/time patterns
        timestamp_nodes = []
        for node in nodes:
            timestamp = self._extract_timestamp(node["data"])
            if timestamp:
                timestamp_nodes.append((node, timestamp))

        # Sort by timestamp
        timestamp_nodes.sort(key=lambda x: x[1])

        # Create temporal sequence edges
        for i in range(len(timestamp_nodes) - 1):
            current_node, current_time = timestamp_nodes[i]
            next_node, next_time = timestamp_nodes[i + 1]

            # Only connect if reasonably close in time (same day or consecutive entries)
            if i < 5:  # Limit temporal connections
                edges.append(
                    {
                        "from": current_node["id"],
                        "to": next_node["id"],
                        "type": "temporal_sequence",
                        "weight": 0.5,
                        "title": f"Temporal: {current_time} → {next_time}",
                    }
                )

        return edges

    def _find_semantic_relationships(self, nodes: List[Dict]) -> List[Dict]:
        """Find relationships based on semantic similarity (requires embeddings)."""
        edges = []

        # This would require sentence-transformers and embeddings
        # For now, return empty list as semantic relationships are optional
        return edges

    def _calculate_simple_similarity(self, node1: Dict, node2: Dict) -> float:
        """Calculate simple text similarity between nodes."""
        # Extract text content from both nodes
        text1 = self._extract_text_content(node1["data"])
        text2 = self._extract_text_content(node2["data"])

        if not text1 or not text2:
            return 0.0

        # Simple word overlap similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union) if union else 0.0

    def _extract_text_content(self, row_data: Dict[str, Any]) -> str:
        """Extract all text content from a row."""
        text_fields = []
        text_columns = [
            "content",
            "title",
            "name",
            "decision_name",
            "category",
            "note",
            "description",
        ]

        for column in text_columns:
            if column in row_data and row_data[column]:
                text_fields.append(str(row_data[column]))

        return " ".join(text_fields)

    def _extract_timestamp(self, row_data: Dict[str, Any]) -> Optional[str]:
        """Extract timestamp from row data."""
        timestamp_fields = ["timestamp", "created_at", "date", "created_date"]

        for field in timestamp_fields:
            if field in row_data and row_data[field]:
                return str(row_data[field])

        return None

    def _filter_by_connections(
        self, nodes: List[Dict], edges: List[Dict], min_connections: int
    ) -> Tuple[List[Dict], List[Dict]]:
        """Filter nodes that don't meet minimum connection requirements."""
        # Count connections per node
        connection_counts = {}
        for edge in edges:
            connection_counts[edge["from"]] = connection_counts.get(edge["from"], 0) + 1
            connection_counts[edge["to"]] = connection_counts.get(edge["to"], 0) + 1

        # Filter nodes
        filtered_nodes = [
            node
            for node in nodes
            if connection_counts.get(node["id"], 0) >= min_connections
        ]

        # Get filtered node IDs
        filtered_node_ids = {node["id"] for node in filtered_nodes}

        # Filter edges to only include edges between filtered nodes
        filtered_edges = [
            edge
            for edge in edges
            if edge["from"] in filtered_node_ids and edge["to"] in filtered_node_ids
        ]

        return filtered_nodes, filtered_edges


def _generate_html_visualization(graph_data: Dict[str, Any]) -> str:
    """Generate HTML content for knowledge graph visualization."""

    # Properly escape JSON to prevent XSS attacks
    nodes_json = html.escape(json.dumps(graph_data["nodes"], indent=2))
    edges_json = html.escape(json.dumps(graph_data["edges"], indent=2))

    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Knowledge Graph - SQLite Memory Bank</title>
    <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            color: white;
            padding: 24px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5rem;
            font-weight: 700;
        }}
        .header p {{
            margin: 8px 0 0 0;
            font-size: 1.1rem;
            opacity: 0.9;
        }}
        .stats {{
            background: #f8fafc;
            padding: 16px 24px;
            border-bottom: 1px solid #e2e8f0;
            display: flex;
            justify-content: space-around;
            flex-wrap: wrap;
        }}
        .stat {{
            text-align: center;
            margin: 8px;
        }}
        .stat-value {{
            font-size: 1.8rem;
            font-weight: 700;
            color: #4f46e5;
        }}
        .stat-label {{
            font-size: 0.875rem;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        #mynetworkid {{
            width: 100%;
            height: 700px;
            border: none;
        }}
        .controls {{
            background: #f8fafc;
            padding: 16px 24px;
            border-top: 1px solid #e2e8f0;
            display: flex;
            justify-content: center;
            gap: 12px;
            flex-wrap: wrap;
        }}
        .btn {{
            background: #4f46e5;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.875rem;
            font-weight: 500;
            transition: background-color 0.2s;
        }}
        .btn:hover {{
            background: #4338ca;
        }}
        .help-modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
        }}
        .help-content {{
            background-color: white;
            margin: 5% auto;
            padding: 24px;
            border-radius: 12px;
            width: 80%;
            max-width: 600px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }}
        .help-close {{
            color: #aaa;
            float: right;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
        }}
        .help-close:hover {{
            color: #000;
        }}
        /* Use same modal structure for node details */
        .node-modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
        }}
        .node-content {{
            background-color: white;
            margin: 5% auto;
            padding: 24px;
            border-radius: 12px;
            width: 80%;
            max-width: 700px;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }}
        .node-close {{
            color: #aaa;
            float: right;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
        }}
        .node-close:hover {{
            color: #000;
        }}
        /* Content styling for node details */
        .detail-section {{
            margin-bottom: 20px;
        }}
        .detail-label {{
            font-weight: 600;
            color: #374151;
            margin-bottom: 8px;
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        .detail-value {{
            background: #f8fafc;
            padding: 12px;
            border-radius: 6px;
            border-left: 3px solid #4f46e5;
            font-family: 'Consolas', 'Monaco', monospace;
            word-break: break-all;
        }}
        .detail-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 8px;
        }}
        .detail-table th,
        .detail-table td {{
            padding: 8px 12px;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }}
        .detail-table th {{
            background: #f3f4f6;
            font-weight: 600;
            font-size: 0.875rem;
        }}
        .node-type-badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        .node-legend {{
            background: #f8fafc;
            padding: 12px;
            margin: 12px 0;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
        }}
        .legend-item {{
            display: inline-flex;
            align-items: center;
            margin: 4px 8px;
            font-size: 0.875rem;
        }}
        .legend-color {{
            width: 16px;
            height: 16px;
            border-radius: 50%;
            margin-right: 8px;
            border: 2px solid #fff;
            box-shadow: 0 1px 3px rgba(0,0,0,0.2);
        }}
        .footer {{
            background: #1e293b;
            color: #cbd5e1;
            padding: 16px 24px;
            text-align: center;
            font-size: 0.875rem;
        }}
        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 2rem;
            }}
            .stats {{
                justify-content: center;
            }}
            #mynetworkid {{
                height: 500px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 Knowledge Graph</h1>
            <p>Interactive visualization of your SQLite Memory Bank</p>
        </div>

        <div class="stats">
            <div class="stat">
                <div class="stat-value">{len(graph_data["nodes"])}</div>
                <div class="stat-label">Nodes</div>
            </div>
            <div class="stat">
                <div class="stat-value">{len(graph_data["edges"])}</div>
                <div class="stat-label">Relationships</div>
            </div>
            <div class="stat">
                <div class="stat-value">{len(set(node["table"] for node in graph_data["nodes"]))}</div>
                <div class="stat-label">Tables</div>
            </div>
            <div class="stat">
                <div class="stat-value">{datetime.now().strftime("%H:%M")}</div>
                <div class="stat-label">Generated</div>
            </div>
        </div>

        <div class="controls">
            <button class="btn" onclick="network.fit()">🔍 Fit to Screen</button>
            <button class="btn" onclick="togglePhysics()">⚡ Toggle Physics</button>
            <button class="btn" onclick="resetView()">🔄 Reset View</button>
            <button class="btn" onclick="stabilizeNetwork()">⚖️ Stabilize</button>
            <button class="btn" onclick="exportJSON()">💾 Export JSON</button>
            <button class="btn" onclick="showHelp()">❓ Help</button>
            <button class="btn" onclick="toggleNodeTypes()">🏷️ Toggle Types</button>
            <button class="btn" onclick="exportPNG()">📸 Export PNG</button>
        </div>

        <div id="mynetworkid"></div>

        <!-- Node Details Modal (same structure as help modal) -->
        <div id="nodeModal" class="node-modal">
            <div class="node-content">
                <span class="node-close" onclick="closeNodeDetails()">&times;</span>
                <div id="nodeDetailsContent">
                    <!-- Content will be populated by JavaScript -->
                </div>
            </div>
        </div>

        <div class="footer">
            Generated by SQLite Memory Bank - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        </div>
    </div>

    <!-- Help Modal -->
    <div id="helpModal" class="help-modal">
        <div class="help-content">
            <span class="help-close" onclick="closeHelp()">&times;</span>
            <h2>🧠 Knowledge Graph Help</h2>
            <h3>🎮 Controls</h3>
            <ul>
                <li><strong>🔍 Fit to Screen:</strong> Center and scale graph to fit view</li>
                <li><strong>⚡ Toggle Physics:</strong> Enable/disable node animations</li>
                <li><strong>� Reset View:</strong> Restore original positions if nodes disappear</li>
                <li><strong>⚖️ Stabilize:</strong> Re-stabilize network layout</li>
                <li><strong>�💾 Export JSON:</strong> Download graph data as JSON</li>
                <li><strong>📸 Export PNG:</strong> Save current view as image</li>
                <li><strong>🏷️ Toggle Types:</strong> Show/hide node type labels</li>
                <li><strong>❓ Help:</strong> Show this help dialog</li>
            </ul>
            <h3>🖱️ Navigation</h3>
            <ul>
                <li><strong>Click & Drag:</strong> Move individual nodes</li>
                <li><strong>Scroll Wheel:</strong> Zoom in/out</li>
                <li><strong>Click Node:</strong> View detailed information</li>
                <li><strong>Hover:</strong> Quick preview tooltip</li>
                <li><strong>⚠️ If nodes disappear:</strong> Use "🔄 Reset View" or "⚖️ Stabilize"</li>
            </ul>
            <h3>🎨 Visual Guide</h3>
            <div id="nodeLegend" class="node-legend">
                <!-- Legend will be populated by JavaScript -->
            </div>
        </div>
    </div>

    <script>
        // Data for the network
        const nodes = new vis.DataSet({nodes_json});
        const edges = new vis.DataSet({edges_json});

        // Network configuration
        const options = {{
            nodes: {{
                font: {{
                    size: 14,
                    color: '#343434'
                }},
                borderWidth: 2,
                shadow: {{
                    enabled: true,
                    color: 'rgba(0,0,0,0.1)',
                    size: 5,
                    x: 2,
                    y: 2
                }},
                chosen: {{
                    node: function(values, id, selected, hovering) {{
                        values.borderWidth = 4;
                        values.shadowSize = 8;
                    }}
                }}
            }},
            edges: {{
                width: 2,
                color: {{
                    color: '#848484',
                    highlight: '#4f46e5'
                }},
                smooth: {{
                    type: 'continuous'
                }},
                arrows: {{
                    to: {{
                        enabled: true,
                        scaleFactor: 1
                    }}
                }}
            }},
            physics: {{
                enabled: true,
                stabilization: {{
                    iterations: 100,
                    updateInterval: 25
                }},
                barnesHut: {{
                    gravitationalConstant: -2000,
                    centralGravity: 0.3,
                    springLength: 120,
                    springConstant: 0.04,
                    damping: 0.09,
                    avoidOverlap: 0.1
                }},
                maxVelocity: 50,
                minVelocity: 0.75,
                timestep: 0.5
            }},
            interaction: {{
                hover: true,
                tooltipDelay: 200,
                hideEdgesOnDrag: false,
                hideNodesOnDrag: false,
                dragNodes: true,
                dragView: true,
                zoomView: true,
                selectConnectedEdges: false
            }},
            groups: {{
                // Dynamic color assignment for different tables
            }}
        }};

        // Assign colors to different tables/groups
        const tableColors = [
            '#4f46e5', '#7c3aed', '#dc2626', '#ea580c', '#ca8a04',
            '#16a34a', '#0891b2', '#c2410c', '#9333ea', '#be123c'
        ];
        const tables = [...new Set(nodes.get().map(node => node.table))];
        tables.forEach((table, index) => {{
            options.groups[table] = {{
                color: {{
                    background: tableColors[index % tableColors.length],
                    border: tableColors[index % tableColors.length],
                    highlight: {{
                        background: tableColors[index % tableColors.length],
                        border: '#000000'
                    }}
                }}
            }};
        }});

        // Create the network
        const container = document.getElementById('mynetworkid');
        const data = {{ nodes: nodes, edges: edges }};
        const network = new vis.Network(container, data, options);

        // Event handlers
        network.on('click', function(params) {{
            console.log('Network clicked. Params:', params);
            if (params.nodes.length > 0) {{
                const nodeId = params.nodes[0];
                const node = nodes.get(nodeId);
                console.log('Node clicked:', node);
                showNodeDetails(node);
            }} else {{
                console.log('Clicked on empty space');
                closeNodeDetails();
            }}
        }});

        network.on('hoverNode', function(params) {{
            container.style.cursor = 'pointer';
        }});

        network.on('blurNode', function(params) {{
            container.style.cursor = 'default';
        }});

        // Enhanced node details display (same structure as help modal)
        function showNodeDetails(node) {{
            console.log('showNodeDetails called with:', node);

            const modal = document.getElementById('nodeModal');
            const content = document.getElementById('nodeDetailsContent');

            console.log('Modal element:', modal);
            console.log('Content element:', content);

            if (!modal || !content) {{
                console.error('Required elements not found!');
                console.error('modal:', modal, 'content:', content);
                return;
            }}

            // Define color scheme for table types
            const tableTypeColors = {{
                'project_structure': '#10b981',
                'technical_decisions': '#f59e0b',
                'user_preferences': '#8b5cf6',
                'session_context': '#06b6d4',
                'documentation': '#ef4444',
                'conversation_memory': '#84cc16',
                'domain_insights': '#f97316',
                'unified_memory': '#6366f1',
                'notes': '#ec4899'
            }};

            const badgeColor = tableTypeColors[node.table] || '#64748b';

            // Build detailed content (same format as help modal)
            let detailsHTML = `
                <h2>🔍 Node Details</h2>
                <div style="margin-bottom: 20px;">
                    <span class="node-type-badge" style="background: ${{badgeColor}}; color: white;">
                        ${{node.table.replace('_', ' ').toUpperCase()}}
                    </span>
                    <h3>${{node.label}}</h3>
                </div>
            `;

            // Basic info section
            detailsHTML += `
                <div class="detail-section">
                    <div class="detail-label">📋 Basic Information</div>
                    <table class="detail-table">
                        <tr><th>ID</th><td>${{node.id}}</td></tr>
                        <tr><th>Table</th><td>${{node.table}}</td></tr>
                        <tr><th>Group</th><td>${{node.group}}</td></tr>
                        <tr><th>Label</th><td>${{node.label}}</td></tr>
                    </table>
                </div>
            `;

            // Data section
            if (node.data && Object.keys(node.data).length > 0) {{
                detailsHTML += `
                    <div class="detail-section">
                        <div class="detail-label">💾 Stored Data</div>
                        <table class="detail-table">
                `;

                for (const [key, value] of Object.entries(node.data)) {{
                    if (value !== null && value !== undefined && value !== '') {{
                        let displayValue = String(value);
                        if (displayValue.length > 200) {{
                            displayValue = displayValue.substring(0, 200) + '...';
                        }}
                        // Escape HTML to prevent XSS
                        displayValue = displayValue.replace(/</g, '&lt;').replace(/>/g, '&gt;');
                        detailsHTML += `<tr><th>${{key}}</th><td>${{displayValue}}</td></tr>`;
                    }}
                }}

                detailsHTML += `
                        </table>
                    </div>
                `;
            }}

            // Visual properties section
            detailsHTML += `
                <div class="detail-section">
                    <div class="detail-label">🎨 Visual Properties</div>
                    <table class="detail-table">
                        <tr><th>Shape</th><td>${{node.shape || 'dot'}}</td></tr>
                        <tr><th>Size</th><td>${{node.size || 20}}</td></tr>
                        <tr><th>Color</th><td>
                            <span style="display: inline-block; width: 20px; height: 20px; background: ${{node.color?.background || node.color || '#64748b'}}; border-radius: 50%; margin-right: 8px;"></span>
                            ${{node.color?.background || node.color || '#64748b'}}
                        </td></tr>
                    </table>
                </div>
            `;

            // JSON export section (collapsible)
            detailsHTML += `
                <div class="detail-section">
                    <div class="detail-label">🔧 Raw Data (JSON)</div>
                    <details style="margin-top: 8px;">
                        <summary style="cursor: pointer; font-weight: 600;">Click to view JSON data</summary>
                        <div class="detail-value" style="margin-top: 8px;">
                            <pre style="max-height: 200px; overflow-y: auto;">${{JSON.stringify(node, null, 2)}}</pre>
                        </div>
                    </details>
                </div>
            `;

            content.innerHTML = detailsHTML;
            console.log('Setting modal display to block...');
            modal.style.display = 'block';
            console.log('Modal should now be visible');
        }}

        function closeNodeDetails() {{
            console.log('closeNodeDetails called');
            const modal = document.getElementById('nodeModal');
            if (modal) {{
                modal.style.display = 'none';
                console.log('Modal hidden');
            }} else {{
                console.error('Modal element not found for closing');
            }}
        }}

        // Control functions
        let physicsEnabled = true;
        let showNodeTypes = true;

        function togglePhysics() {{
            physicsEnabled = !physicsEnabled;
            network.setOptions({{physics: {{enabled: physicsEnabled}}}});
            const btn = event.target;
            btn.style.background = physicsEnabled ? '#4f46e5' : '#64748b';
            if (physicsEnabled) {{
                stabilizeNetwork();
            }}
        }}

        function resetView() {{
            // Reset node positions and re-stabilize
            network.setData({{nodes: nodes, edges: edges}});
            network.setOptions({{physics: {{enabled: true}}}});
            physicsEnabled = true;
            // Update physics button color
            document.querySelector('button[onclick="togglePhysics()"]').style.background = '#4f46e5';
            setTimeout(() => {{
                network.fit();
            }}, 1000);
        }}

        function stabilizeNetwork() {{
            network.setOptions({{
                physics: {{
                    enabled: true,
                    stabilization: {{
                        enabled: true,
                        iterations: 100,
                        updateInterval: 25,
                        onlyDynamicEdges: false,
                        fit: true
                    }}
                }}
            }});

            // Re-enable physics temporarily to stabilize
            setTimeout(() => {{
                if (!physicsEnabled) {{
                    network.setOptions({{physics: {{enabled: false}}}});
                }}
            }}, 2000);
        }}

        function exportJSON() {{
            const graphData = {{
                nodes: nodes.get(),
                edges: edges.get(),
                metadata: {{
                    exported: new Date().toISOString(),
                    total_nodes: nodes.length,
                    total_edges: edges.length,
                    tables: [...new Set(nodes.get().map(n => n.table))]
                }}
            }};
            const blob = new Blob([JSON.stringify(graphData, null, 2)], {{type: 'application/json'}});
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = 'knowledge-graph-data-{datetime.now().strftime("%Y%m%d_%H%M%S")}.json';
            link.click();
            URL.revokeObjectURL(url);
        }}

        function exportPNG() {{
            const canvas = document.querySelector('#mynetworkid canvas');
            const link = document.createElement('a');
            link.download = 'knowledge-graph-{datetime.now().strftime("%Y%m%d_%H%M%S")}.png';
            link.href = canvas.toDataURL();
            link.click();
        }}

        function toggleNodeTypes() {{
            showNodeTypes = !showNodeTypes;
            const nodeUpdate = nodes.get().map(node => ({{
                ...node,
                label: showNodeTypes ? `[${{node.table}}] ${{node.label}}` : node.label.replace(/^\\[.*?\\]\\s*/, '')
            }}));
            nodes.update(nodeUpdate);
            const btn = event.target;
            btn.textContent = showNodeTypes ? '🏷️ Hide Types' : '🏷️ Show Types';
        }}

        function showHelp() {{
            document.getElementById('helpModal').style.display = 'block';
            generateLegend();
        }}

        function closeHelp() {{
            document.getElementById('helpModal').style.display = 'none';
        }}

        function generateLegend() {{
            const tables = [...new Set(nodes.get().map(n => n.table))];
            const legendHtml = tables.map((table, index) => {{
                const color = tableColors[index % tableColors.length];
                return `<div class="legend-item">
                    <div class="legend-color" style="background-color: ${{color}}"></div>
                    <span>${{table}} (${{nodes.get().filter(n => n.table === table).length}} nodes)</span>
                </div>`;
            }}).join('');
            document.getElementById('nodeLegend').innerHTML = legendHtml;
        }}

        // Close modals when clicking outside
        window.onclick = function(event) {{
            const helpModal = document.getElementById('helpModal');
            const nodeModal = document.getElementById('nodeModal');
            if (event.target === helpModal) {{
                helpModal.style.display = 'none';
            }}
            if (event.target === nodeModal) {{
                nodeModal.style.display = 'none';
            }}
        }}

        // Initialize
        console.log('Knowledge Graph initialized with', nodes.length, 'nodes and', edges.length, 'edges');

        // Add keyboard shortcuts
        document.addEventListener('keydown', function(event) {{
            switch(event.key) {{
                case 'f':
                case 'F':
                    if (!event.ctrlKey) network.fit();
                    break;
                case 'p':
                case 'P':
                    if (!event.ctrlKey) togglePhysics();
                    break;
                case 'r':
                case 'R':
                    if (!event.ctrlKey) resetView();
                    break;
                case 's':
                case 'S':
                    if (!event.ctrlKey) stabilizeNetwork();
                    break;
                case 'h':
                case 'H':
                    if (!event.ctrlKey) showHelp();
                    break;
                case 'Escape':
                    closeHelp();
                    closeNodeDetails();
                    break;
            }}
        }});
    </script>
</body>
</html>"""

    return html_template
