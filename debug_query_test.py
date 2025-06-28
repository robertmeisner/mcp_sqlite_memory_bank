#!/usr/bin/env python3
"""Test specific query terms to understand the search behavior."""

import asyncio
import tempfile
import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mcp_sqlite_memory_bank import server as smb
from tests.conftest import extract_result
from fastmcp import Client

async def test_specific_queries():
    """Test specific query terms."""
    
    # Setup temporary database
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)
    
    # Set the database path
    original_db_path = smb.DB_PATH
    smb.DB_PATH = db_path
    
    try:
        async with Client(smb.app) as client:
            print("🔧 Setting up test data...")
            
            # Create table
            await client.call_tool(
                "create_table",
                {
                    "table_name": "research_papers",
                    "columns": [
                        {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
                        {"name": "title", "type": "TEXT"},
                        {"name": "abstract", "type": "TEXT"},
                        {"name": "keywords", "type": "TEXT"},
                    ],
                },
            )
            
            papers = [
                {
                    "title": "Deep Learning for Computer Vision",
                    "abstract": "Convolutional neural networks for image recognition and object detection",
                    "keywords": "deep learning, CNN, computer vision, image processing",
                },
                {
                    "title": "Natural Language Processing with Transformers",
                    "abstract": "Attention mechanisms and transformer architectures for language understanding",
                    "keywords": "NLP, transformers, attention, language models",
                },
                {
                    "title": "Reinforcement Learning in Robotics",
                    "abstract": "Learning optimal control policies through trial and error in robotic systems",
                    "keywords": "reinforcement learning, robotics, control, AI",
                },
            ]

            for paper in papers:
                await client.call_tool(
                    "create_row", {"table_name": "research_papers", "data": paper}
                )
            
            # Test queries that should definitely match
            queries_to_test = [
                "Deep Learning",  # Exact match in title
                "neural networks",  # Exact match in abstract
                "transformers",  # Exact match in keywords
                "learning",  # Should match multiple entries
                "artificial intelligence neural networks learning",  # Original failing query
            ]
            
            for query in queries_to_test:
                print(f"\n🔍 Testing query: '{query}'")
                
                # Test text search
                text_result = await client.call_tool(
                    "search_content",
                    {"query": query, "tables": ["research_papers"], "limit": 10}
                )
                text_out = extract_result(text_result)
                print(f"  Text search: {len(text_out.get('results', []))} results")
                
                # Test auto smart search
                smart_result = await client.call_tool(
                    "auto_smart_search",
                    {"query": query, "tables": ["research_papers"], "limit": 10}
                )
                smart_out = extract_result(smart_result)
                print(f"  Smart search: {len(smart_out.get('results', []))} results")
                
                if smart_out.get('results'):
                    print(f"    Sample result: {smart_out['results'][0].get('title', 'No title')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        smb.DB_PATH = original_db_path
        try:
            os.unlink(db_path)
        except:
            pass

if __name__ == "__main__":
    asyncio.run(test_specific_queries())
