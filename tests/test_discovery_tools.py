"""
Test coverage for the new discovery tools: intelligent_discovery, discovery_templates, discover_relationships
"""
import os
import tempfile
import pytest
import pytest_asyncio
import json
from typing import Any, Dict, cast, TypeVar, Sequence
from fastmcp import Client
from mcp_sqlite_memory_bank import server as smb

# Import helper from test_api
from test_api import extract_result


@pytest.fixture()
def temp_db(monkeypatch):
    """Use a temporary file for the test DB."""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)
    orig_db = smb.DB_PATH
    smb.DB_PATH = db_path
    yield db_path
    smb.DB_PATH = orig_db

    # Explicitly close database connections
    try:
        from mcp_sqlite_memory_bank.database import _db_instance
        if _db_instance:
            _db_instance.close()
    except Exception:
        pass


@pytest_asyncio.fixture
async def client_with_sample_data(temp_db):
    """Client with sample data for discovery testing."""
    async with Client(smb.app) as client:
        # Create sample data structure for testing discovery
        # Create users table
        await client.call_tool("create_table", {
            "table_name": "users",
            "columns": [
                {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
                {"name": "username", "type": "TEXT NOT NULL"},
                {"name": "email", "type": "TEXT"},
                {"name": "profile", "type": "TEXT"},
                {"name": "created_at", "type": "TEXT DEFAULT CURRENT_TIMESTAMP"}
            ]
        })
        
        # Create projects table with foreign key relationship
        await client.call_tool("create_table", {
            "table_name": "projects", 
            "columns": [
                {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
                {"name": "name", "type": "TEXT NOT NULL"},
                {"name": "description", "type": "TEXT"},
                {"name": "owner_id", "type": "INTEGER"},
                {"name": "status", "type": "TEXT DEFAULT 'active'"},
                {"name": "created_at", "type": "TEXT DEFAULT CURRENT_TIMESTAMP"}
            ]
        })
        
        # Create knowledge table for content analysis
        await client.call_tool("create_table", {
            "table_name": "knowledge",
            "columns": [
                {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
                {"name": "title", "type": "TEXT NOT NULL"},
                {"name": "content", "type": "TEXT"},
                {"name": "category", "type": "TEXT"},
                {"name": "importance", "type": "INTEGER DEFAULT 5"},
                {"name": "created_at", "type": "TEXT DEFAULT CURRENT_TIMESTAMP"}
            ]
        })
        
        # Add sample data
        sample_users = [
            {"username": "alice", "email": "alice@example.com", "profile": "Senior developer with expertise in Python and AI"},
            {"username": "bob", "email": "bob@example.com", "profile": "Product manager focused on user experience and market analysis"},
            {"username": "charlie", "email": "charlie@example.com", "profile": "Data scientist specializing in machine learning and analytics"}
        ]
        
        for user in sample_users:
            await client.call_tool("create_row", {"table_name": "users", "data": user})
        
        sample_projects = [
            {"name": "AI Assistant", "description": "Intelligent chatbot for customer support using natural language processing", "owner_id": 1, "status": "active"},
            {"name": "Data Pipeline", "description": "Automated data processing pipeline for real-time analytics", "owner_id": 3, "status": "development"},
            {"name": "User Dashboard", "description": "Interactive dashboard for user engagement metrics and insights", "owner_id": 2, "status": "planning"}
        ]
        
        for project in sample_projects:
            await client.call_tool("create_row", {"table_name": "projects", "data": project})
        
        sample_knowledge = [
            {"title": "Machine Learning Best Practices", "content": "Deep dive into ML model development, training strategies, hyperparameter tuning, and deployment considerations for production systems", "category": "technical", "importance": 9},
            {"title": "API Design Principles", "content": "RESTful API design patterns, versioning strategies, authentication methods, and documentation best practices for scalable web services", "category": "architecture", "importance": 8},
            {"title": "Database Optimization", "content": "SQL query optimization techniques, indexing strategies, connection pooling, and performance monitoring for high-traffic applications", "category": "performance", "importance": 7},
            {"title": "Team Meeting Notes", "content": "Weekly standup discussions, project updates, blockers, and action items for the development team", "category": "management", "importance": 5},
            {"title": "Security Guidelines", "content": "Comprehensive security checklist including input validation, authentication, authorization, encryption, and vulnerability assessment", "category": "security", "importance": 10}
        ]
        
        for knowledge in sample_knowledge:
            await client.call_tool("create_row", {"table_name": "knowledge", "data": knowledge})
        
        yield client


class TestIntelligentDiscovery:
    """Test cases for intelligent_discovery tool."""

    @pytest.mark.asyncio
    @pytest.mark.asyncio

    async def test_understand_content_goal(self, client_with_sample_data):
        """Test intelligent discovery with understand_content goal."""
        client = client_with_sample_data
        
        result = await client.call_tool("intelligent_discovery", {
            "discovery_goal": "understand_content",
            "depth": "moderate"
        })
        
        output = extract_result(result)
        assert output["success"] is True
        assert "discovery" in output
        assert "next_steps" in output
        
        discovery = output["discovery"]
        assert discovery["goal"] == "understand_content"
        assert "overview" in discovery
        assert "insights" in discovery
        assert "recommendations" in discovery
        
        # Check overview content
        overview = discovery["overview"]
        assert overview["total_tables"] == 3  # users, projects, knowledge
        assert "available_tables" in overview
        assert set(overview["available_tables"]) == {"users", "projects", "knowledge"}
        
        # Verify insights are generated
        insights = discovery["insights"]
        assert len(insights) > 0
        assert any("3 tables" in insight for insight in insights)
        
        # Verify next steps are provided
        next_steps = output["next_steps"]
        assert len(next_steps) > 0
        assert any("search" in step.lower() for step in next_steps)

    @pytest.mark.asyncio
    @pytest.mark.asyncio

    async def test_explore_structure_goal(self, client_with_sample_data):
        """Test intelligent discovery with explore_structure goal."""
        client = client_with_sample_data
        
        result = await client.call_tool("intelligent_discovery", {
            "discovery_goal": "explore_structure",
            "depth": "quick"
        })
        
        output = extract_result(result)
        assert output["success"] is True
        
        discovery = output["discovery"]
        assert discovery["goal"] == "explore_structure"
        
        # Should include schema analysis
        assert "steps_completed" in discovery
        assert "schema_analysis" in discovery["steps_completed"]

    @pytest.mark.asyncio
    @pytest.mark.asyncio

    async def test_assess_quality_goal(self, client_with_sample_data):
        """Test intelligent discovery with assess_quality goal."""
        client = client_with_sample_data
        
        result = await client.call_tool("intelligent_discovery", {
            "discovery_goal": "assess_quality",
            "depth": "comprehensive"
        })
        
        output = extract_result(result)
        assert output["success"] is True
        
        discovery = output["discovery"]
        assert discovery["goal"] == "assess_quality"
        
        # Should include quality assessment
        assert "steps_completed" in discovery
        assert "quality_assessment" in discovery["steps_completed"]

    @pytest.mark.asyncio
    @pytest.mark.asyncio

    async def test_find_patterns_goal(self, client_with_sample_data):
        """Test intelligent discovery with find_patterns goal."""
        client = client_with_sample_data
        
        result = await client.call_tool("intelligent_discovery", {
            "discovery_goal": "find_patterns",
            "focus_area": "knowledge"
        })
        
        output = extract_result(result)
        assert output["success"] is True
        
        discovery = output["discovery"]
        assert discovery["goal"] == "find_patterns"
        assert discovery["focus_area"] == "knowledge"

    @pytest.mark.asyncio
    @pytest.mark.asyncio

    async def test_prepare_search_goal(self, client_with_sample_data):
        """Test intelligent discovery with prepare_search goal."""
        client = client_with_sample_data
        
        result = await client.call_tool("intelligent_discovery", {
            "discovery_goal": "prepare_search",
            "agent_id": "test_agent_123"
        })
        
        output = extract_result(result)
        assert output["success"] is True
        
        discovery = output["discovery"]
        assert discovery["goal"] == "prepare_search"
        
        # Should include search readiness analysis
        assert "steps_completed" in discovery
        assert "search_readiness" in discovery["steps_completed"]

    @pytest.mark.asyncio
    @pytest.mark.asyncio

    async def test_invalid_goal(self, client_with_sample_data):
        """Test intelligent discovery with invalid goal."""
        client = client_with_sample_data
        
        result = await client.call_tool("intelligent_discovery", {
            "discovery_goal": "invalid_goal"
        })
        
        output = extract_result(result)
        # Should still work but with default behavior
        assert output["success"] is True


class TestDiscoveryTemplates:
    """Test cases for discovery_templates tool."""

    @pytest.mark.asyncio


    async def test_first_time_exploration_template(self, client_with_sample_data):
        """Test first_time_exploration template."""
        client = client_with_sample_data
        
        result = await client.call_tool("discovery_templates", {
            "template_type": "first_time_exploration"
        })
        
        output = extract_result(result)
        assert output["success"] is True
        assert "template" in output
        
        template = output["template"]
        assert template["name"] == "First Time Exploration"
        assert "workflow" in template
        assert len(template["workflow"]) > 0
        
        # Verify workflow structure
        workflow = template["workflow"]
        for step in workflow:
            assert "step" in step
            assert "action" in step
            assert "tool" in step
            assert "params" in step
            assert "purpose" in step
            assert "look_for" in step
        
        # Verify success criteria
        assert "success_criteria" in template
        assert len(template["success_criteria"]) > 0

    @pytest.mark.asyncio


    async def test_content_audit_template(self, client_with_sample_data):
        """Test content_audit template."""
        client = client_with_sample_data
        
        result = await client.call_tool("discovery_templates", {
            "template_type": "content_audit"
        })
        
        output = extract_result(result)
        assert output["success"] is True
        
        template = output["template"]
        assert template["name"] == "Content Quality Audit"
        assert "estimated_time" in template
        assert "workflow" in template

    @pytest.mark.asyncio


    async def test_search_optimization_template(self, client_with_sample_data):
        """Test search_optimization template."""
        client = client_with_sample_data
        
        result = await client.call_tool("discovery_templates", {
            "template_type": "search_optimization"
        })
        
        output = extract_result(result)
        assert output["success"] is True
        
        template = output["template"]
        assert template["name"] == "Search Optimization Setup"

    @pytest.mark.asyncio


    async def test_problem_solving_template(self, client_with_sample_data):
        """Test problem_solving template."""
        client = client_with_sample_data
        
        result = await client.call_tool("discovery_templates", {
            "template_type": "problem_solving"
        })
        
        output = extract_result(result)
        assert output["success"] is True
        
        template = output["template"]
        assert template["name"] == "Problem-Solving Discovery"
        assert "customization_note" in template

    @pytest.mark.asyncio


    async def test_customized_template(self, client_with_sample_data):
        """Test template customization."""
        client = client_with_sample_data
        
        result = await client.call_tool("discovery_templates", {
            "template_type": "first_time_exploration",
            "customize_for": "machine learning project"
        })
        
        output = extract_result(result)
        assert output["success"] is True
        assert output["customized_for"] == "machine learning project"

    @pytest.mark.asyncio


    async def test_invalid_template_type(self, client_with_sample_data):
        """Test invalid template type."""
        client = client_with_sample_data
        
        result = await client.call_tool("discovery_templates", {
            "template_type": "nonexistent_template"
        })
        
        output = extract_result(result)
        assert output["success"] is False
        assert "available_templates" in output["details"]

    @pytest.mark.asyncio


    async def test_available_templates_list(self, client_with_sample_data):
        """Test that available templates are listed."""
        client = client_with_sample_data
        
        result = await client.call_tool("discovery_templates", {
            "template_type": "first_time_exploration"
        })
        
        output = extract_result(result)
        assert output["success"] is True
        assert "available_templates" in output
        
        available = output["available_templates"]
        expected_templates = ["first_time_exploration", "content_audit", "search_optimization", "problem_solving"]
        for template in expected_templates:
            assert template in available


class TestDiscoverRelationships:
    """Test cases for discover_relationships tool."""

    @pytest.mark.asyncio


    async def test_discover_all_relationships(self, client_with_sample_data):
        """Test discovering relationships for all tables."""
        client = client_with_sample_data
        
        result = await client.call_tool("discover_relationships")
        
        output = extract_result(result)
        assert output["success"] is True
        assert "relationships" in output
        assert "insights" in output
        assert "relationship_summary" in output
        
        relationships = output["relationships"]
        # Should analyze all 3 tables
        assert len(relationships) == 3
        assert "users" in relationships
        assert "projects" in relationships
        assert "knowledge" in relationships
        
        # Each table should have relationship categories
        for table_name, table_rels in relationships.items():
            assert "foreign_key_refs" in table_rels
            assert "semantic_similar" in table_rels
            assert "temporal_related" in table_rels
            assert "naming_related" in table_rels

    @pytest.mark.asyncio


    async def test_discover_specific_table_relationships(self, client_with_sample_data):
        """Test discovering relationships for specific table."""
        client = client_with_sample_data
        
        result = await client.call_tool("discover_relationships", {
            "table_name": "users"
        })
        
        output = extract_result(result)
        assert output["success"] is True
        
        relationships = output["relationships"]
        # Should only analyze the users table
        assert len(relationships) == 1
        assert "users" in relationships

    @pytest.mark.asyncio


    async def test_custom_relationship_types(self, client_with_sample_data):
        """Test discovering specific relationship types."""
        client = client_with_sample_data
        
        result = await client.call_tool("discover_relationships", {
            "relationship_types": ["naming_patterns", "semantic_similarity"],
            "similarity_threshold": 0.5
        })
        
        output = extract_result(result)
        assert output["success"] is True
        
        # Verify only requested relationship types are analyzed
        relationships = output["relationships"]
        for table_rels in relationships.values():
            # Should have requested types
            assert "semantic_similar" in table_rels
            assert "naming_related" in table_rels

    @pytest.mark.asyncio


    async def test_relationship_insights_generated(self, client_with_sample_data):
        """Test that relationship insights are properly generated."""
        client = client_with_sample_data
        
        result = await client.call_tool("discover_relationships")
        
        output = extract_result(result)
        assert output["success"] is True
        
        insights = output["insights"]
        assert len(insights) > 0
        
        # Should have summary insight
        assert any("relationships" in insight.lower() for insight in insights)

    @pytest.mark.asyncio


    async def test_relationship_recommendations(self, client_with_sample_data):
        """Test that relationship recommendations are provided."""
        client = client_with_sample_data
        
        result = await client.call_tool("discover_relationships")
        
        output = extract_result(result)
        assert output["success"] is True
        
        assert "recommendations" in output
        recommendations = output["recommendations"]
        assert isinstance(recommendations, list)

    @pytest.mark.asyncio


    async def test_invalid_table_name(self, client_with_sample_data):
        """Test discovering relationships for non-existent table."""
        client = client_with_sample_data
        
        result = await client.call_tool("discover_relationships", {
            "table_name": "nonexistent_table"
        })
        
        output = extract_result(result)
        assert output["success"] is True  # Should succeed but find no relationships
        
        relationships = output["relationships"]
        assert len(relationships) == 0 or (len(relationships) == 1 and not any(relationships.values()))


class TestDiscoveryIntegration:
    """Integration tests for discovery tools working together."""

    @pytest.mark.asyncio


    async def test_discovery_workflow_integration(self, client_with_sample_data):
        """Test a complete discovery workflow using multiple tools."""
        client = client_with_sample_data
        
        # Step 1: Get discovery template
        template_result = await client.call_tool("discovery_templates", {
            "template_type": "first_time_exploration"
        })
        template_output = extract_result(template_result)
        assert template_output["success"] is True
        
        # Step 2: Execute intelligent discovery as recommended in template
        discovery_result = await client.call_tool("intelligent_discovery", {
            "discovery_goal": "understand_content",
            "depth": "moderate"
        })
        discovery_output = extract_result(discovery_result)
        assert discovery_output["success"] is True
        
        # Step 3: Discover relationships
        relationship_result = await client.call_tool("discover_relationships")
        relationship_output = extract_result(relationship_result)
        assert relationship_output["success"] is True
        
        # Verify all tools work together cohesively
        assert discovery_output["discovery"]["overview"]["total_tables"] == 3
        assert len(relationship_output["relationships"]) == 3

    @pytest.mark.asyncio
    async def test_discovery_with_empty_database(self, temp_db):
        """Test discovery tools with empty database."""
        async with Client(smb.app) as client:
            # Test intelligent discovery on empty database
            result = await client.call_tool("intelligent_discovery", {
                "discovery_goal": "understand_content"
            })
            
            output = extract_result(result)
            assert output["success"] is True
            assert output["discovery"]["overview"]["total_tables"] == 0
            
            # Test relationship discovery on empty database
            relationship_result = await client.call_tool("discover_relationships")
            relationship_output = extract_result(relationship_result)
            assert relationship_output["success"] is True
            assert len(relationship_output["relationships"]) == 0

    @pytest.mark.asyncio


    async def test_error_handling_robustness(self, client_with_sample_data):
        """Test that discovery tools handle errors gracefully."""
        client = client_with_sample_data
        
        # Test with extreme parameters
        result = await client.call_tool("intelligent_discovery", {
            "discovery_goal": "understand_content",
            "depth": "ultra_extreme_depth",  # Invalid depth
            "focus_area": "definitely_not_a_table"  # Invalid table
        })
        
        output = extract_result(result)
        # Should still succeed with graceful handling
        assert output["success"] is True


# Performance and edge case tests
class TestDiscoveryPerformance:
    """Performance and stress tests for discovery tools."""

    @pytest.mark.asyncio
    async def test_large_database_discovery(self, temp_db):
        """Test discovery tools with larger dataset."""
        async with Client(smb.app) as client:
            # Create table with more substantial data
            await client.call_tool("create_table", {
                "table_name": "large_dataset",
                "columns": [
                    {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
                    {"name": "category", "type": "TEXT"},
                    {"name": "content", "type": "TEXT"},
                    {"name": "metadata", "type": "TEXT"}
                ]
            })
            
            # Add 50 rows of test data
            for i in range(50):
                await client.call_tool("create_row", {
                    "table_name": "large_dataset",
                    "data": {
                        "category": f"category_{i % 5}",
                        "content": f"This is content item {i} with substantial text to test content analysis algorithms",
                        "metadata": f"metadata_{i}"
                    }
                })
            
            # Test intelligent discovery on larger dataset
            result = await client.call_tool("intelligent_discovery", {
                "discovery_goal": "understand_content",
                "depth": "comprehensive"
            })
            
            output = extract_result(result)
            assert output["success"] is True
            assert output["discovery"]["overview"]["total_rows"] == 50

    @pytest.mark.asyncio


    async def test_concurrent_discovery_calls(self, client_with_sample_data):
        """Test multiple discovery calls don't interfere with each other."""
        client = client_with_sample_data
        
        # Run multiple discovery operations
        tasks = [
            client.call_tool("intelligent_discovery", {"discovery_goal": "understand_content"}),
            client.call_tool("discovery_templates", {"template_type": "content_audit"}),
            client.call_tool("discover_relationships", {"table_name": "users"})
        ]
        
        # All should complete successfully
        results = []
        for task in tasks:
            result = await task
            output = extract_result(result)
            results.append(output)
            assert output["success"] is True
        
        # Verify results are consistent
        assert len(results) == 3
