"""
MCP Prompts Support for SQLite Memory Bank
=========================================

This module adds MCP Prompts support, providing templated prompts and workflows
that leverage the memory bank content for enhanced AI interactions.

Prompts provide reusable, contextual templates that can dynamically incorporate
stored memory content into LLM conversations.

Author: Robert Meisner
"""

from typing import Optional, Dict, List, Any, cast
from fastmcp import FastMCP
from .database import get_database
import json


class MemoryBankPrompts:
    """Manages MCP Prompts for the SQLite Memory Bank."""

    def __init__(self, mcp_app: FastMCP, db_path: str):
        self.mcp = mcp_app
        self.db_path = db_path
        self._register_prompts()

    def _register_prompts(self):
        """Register MCP prompts with the FastMCP app."""

        @self.mcp.prompt("analyze-memory-content")
        async def analyze_memory_content(table_name: Optional[str] = None) -> str:
            """Analyze memory bank content and provide insights."""
            db = get_database(self.db_path)

            if table_name:
                # Analyze specific table
                result = cast(Dict[str, Any], db.read_rows(table_name, {}))
                if not result.get("success"):
                    return f"Error: Could not access table '{table_name}'. Please check if it exists."

                rows = result.get("rows", [])
                prompt = f"""Please analyze the content in the '{table_name}' table from the memory bank.

Table: {table_name}
Row count: {len(rows)}
Sample data: {json.dumps(rows[:3], indent=2) if rows else "No data"}

Please provide:
1. A summary of the content patterns
2. Key insights or themes
3. Suggestions for better organization
4. Potential use cases for this data

Focus on actionable insights that could help improve how this information is stored and retrieved."""
            else:
                # Analyze all tables
                tables_result = cast(Dict[str, Any], db.list_tables())
                if not tables_result.get("success"):
                    return "Error: Could not access memory bank tables."

                tables = tables_result.get("tables", [])
                overview = {"tables": len(tables), "total_content": []}

                for table in tables[:5]:  # Limit to first 5 tables
                    rows_result = cast(Dict[str, Any], db.read_rows(table, {}))
                    if rows_result.get("success"):
                        rows = rows_result.get("rows", [])
                        total_content = cast(List[Any], overview["total_content"])
                        total_content.append(
                            {
                                "table": table,
                                "rows": len(rows),
                                "sample": rows[:2] if rows else [],
                            }
                        )

                prompt = f"""Please analyze the overall content in this memory bank.

Memory Bank Overview:
{json.dumps(overview, indent=2)}

Please provide:
1. Assessment of content organization
2. Identification of content patterns across tables
3. Recommendations for improving memory structure
4. Suggestions for leveraging this content more effectively

Focus on high-level strategic insights about the memory bank's utility and organization."""

            return prompt

        @self.mcp.prompt("search-and-summarize")
        async def search_and_summarize(
            query: str, max_results: Optional[int] = 10
        ) -> str:
            """Search memory content and create a summary prompt."""
            db = get_database(self.db_path)

            # Perform search
            result = cast(
                Dict[str, Any], db.search_content(query, None, max_results or 10)
            )
            if not result.get("success"):
                return f"Error: Could not search for '{query}'. {result.get('error', 'Unknown error')}"

            search_results = result.get("results", [])
            if not search_results:
                return f"No results found for query: '{query}'. Please try different search terms or check if relevant content exists in the memory bank."

            # Format results for prompt
            formatted_results = []
            for i, result in enumerate(search_results[: max_results or 10], 1):
                formatted_results.append(
                    f"{i}. Table: {result.get('table', 'unknown')}"
                )
                formatted_results.append(
                    f"   Content: {result.get('content', 'No content')[:200]}..."
                )
                formatted_results.append(
                    f"   Relevance: {result.get('relevance', 'N/A')}"
                )
                formatted_results.append("")

            prompt = f"""Based on the search query "{query}", here are the most relevant results from the memory bank:

Search Results:
{chr(10).join(formatted_results)}

Please provide:
1. A comprehensive summary of the key information found
2. Common themes or patterns across the results
3. Any gaps or additional information that might be needed
4. Actionable insights based on this content

Use this information to provide a thorough, well-organized response that synthesizes the search results."""

            return prompt

        @self.mcp.prompt("technical-decision-analysis")
        async def technical_decision_analysis(
            decision_topic: Optional[str] = None,
        ) -> str:
            """Analyze technical decisions from the memory bank."""
            db = get_database(self.db_path)

            # Try to find technical_decisions table
            tables_result = cast(Dict[str, Any], db.list_tables())
            if not tables_result.get("success"):
                return "Error: Could not access memory bank."

            tables = tables_result.get("tables", [])
            if "technical_decisions" not in tables:
                return """No technical decisions table found in the memory bank. 

To use this prompt effectively, please:
1. Create a 'technical_decisions' table
2. Store your technical decisions with context
3. Try this prompt again

The table should include fields like: decision_name, chosen_approach, rationale, alternatives, timestamp."""

            # Get technical decisions
            where_clause = {}
            if decision_topic:
                # This is a simplified search - in practice you'd want semantic search
                where_clause = {"decision_name": decision_topic}

            result = db.read_rows("technical_decisions", where_clause)
            if not result.get("success"):
                return "Error: Could not read technical decisions."

            decisions = result.get("rows", [])
            if not decisions:
                topic_msg = f" related to '{decision_topic}'" if decision_topic else ""
                return f"No technical decisions found{topic_msg}. Consider adding some decisions to the memory bank first."

            # Format decisions for analysis
            formatted_decisions = []
            decisions_list = cast(List[Dict[str, Any]], decisions)
            for i, decision in enumerate(decisions_list, 1):
                formatted_decisions.append(
                    f"{i}. Decision: {decision.get('decision_name', 'Unknown')}"
                )
                formatted_decisions.append(
                    f"   Approach: {decision.get('chosen_approach', 'Not specified')}"
                )
                formatted_decisions.append(
                    f"   Rationale: {decision.get('rationale', 'Not provided')}"
                )
                if decision.get("alternatives"):
                    formatted_decisions.append(
                        f"   Alternatives: {decision.get('alternatives')}"
                    )
                formatted_decisions.append(
                    f"   Date: {decision.get('timestamp', 'Unknown')}"
                )
                formatted_decisions.append("")

            prompt = f"""Please analyze these technical decisions from the memory bank:

Technical Decisions{f" (filtered by: {decision_topic})" if decision_topic else ""}:
{chr(10).join(formatted_decisions)}

Please provide:
1. Analysis of decision-making patterns
2. Assessment of the rationale quality
3. Identification of any decision dependencies or conflicts
4. Recommendations for future decisions
5. Suggestions for improving decision documentation

Focus on actionable insights that can improve technical decision-making processes."""

            return prompt

        @self.mcp.prompt("memory-bank-context")
        async def memory_bank_context(context_type: str = "full") -> str:
            """Provide memory bank context for AI conversations."""
            db = get_database(self.db_path)

            # Get overview
            tables_result = db.list_tables()
            if not tables_result.get("success"):
                return "Error: Could not access memory bank for context."

            tables = tables_result.get("tables", [])
            context_info = {
                "available_tables": tables,
                "capabilities": [
                    "Full-text search across all content",
                    "Semantic search (if embeddings are available)",
                    "Structured data queries",
                    "Content analytics and insights",
                ],
                "usage_suggestions": [
                    "Use search_content() for finding specific information",
                    "Use semantic_search() for conceptual queries",
                    "Use read_rows() for structured data access",
                    "Use explore_tables() to discover available content",
                ],
            }

            if context_type == "brief":
                tables_list = cast(List[str], tables)
                prompt = f"""Memory Bank Context (Brief):
Available tables: {', '.join(tables_list)}
Total tables: {len(tables_list)}

This memory bank contains structured information that can be searched and analyzed. Use the available tools to access specific content as needed."""
            else:
                # Get sample content from a few tables
                sample_content = {}
                tables_list = cast(List[str], tables)
                for table in tables_list[:3]:  # Sample from first 3 tables
                    try:
                        result = cast(Dict[str, Any], db.read_rows(table, {}))
                        if result.get("success"):
                            rows = cast(List[Any], result.get("rows", []))
                            sample_content[table] = {
                                "row_count": len(rows),
                                "sample_row": rows[0] if rows else None,
                            }
                    except Exception:
                        continue

                prompt = f"""Memory Bank Context (Full):

{json.dumps(context_info, indent=2)}

Sample Content:
{json.dumps(sample_content, indent=2)}

This memory bank contains structured information that can be searched, analyzed, and leveraged for various tasks. The content is organized in tables with different types of information. Use the available search and query tools to access specific content as needed for your current task."""

            return prompt


def setup_mcp_prompts(mcp_app: FastMCP, db_path: str) -> MemoryBankPrompts:
    """Set up MCP Prompts for the memory bank."""
    return MemoryBankPrompts(mcp_app, db_path)
