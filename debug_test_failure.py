#!/usr/bin/env python3
"""Debug script to reproduce the test_auto_smart_search_complete_workflow failure."""

import asyncio
import tempfile
import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mcp_sqlite_memory_bank import server as smb
from tests.conftest import extract_result
from fastmcp import Client

async def debug_auto_smart_search():
    """Debug the failing auto_smart_search test."""
    
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
            create_table_result = await client.call_tool(
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
            print(f"Create table result: {create_table_result}")
            
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

            for i, paper in enumerate(papers):
                create_result = await client.call_tool(
                    "create_row", {"table_name": "research_papers", "data": paper}
                )
                print(f"Insert paper {i+1}: {create_result}")
            
            print("\n🔍 Testing search_content (text search fallback)...")
            
            # Test basic search_content first
            text_search_result = await client.call_tool(
                "search_content",
                {
                    "query": "artificial intelligence neural networks learning",
                    "tables": ["research_papers"],
                    "limit": 10,
                }
            )
            text_out = extract_result(text_search_result)
            print(f"Text search result: {text_out}")
            print(f"Text search found {len(text_out.get('results', []))} results")
            
            print("\n🚀 Testing auto_smart_search...")
            
            # Test auto_smart_search
            complete_search = await client.call_tool(
                "auto_smart_search",
                {
                    "query": "artificial intelligence neural networks learning",
                    "tables": ["research_papers"],
                    "semantic_weight": 0.6,
                    "text_weight": 0.4,
                    "limit": 10,
                },
            )
            complete_out = extract_result(complete_search)
            print(f"Auto smart search result: {complete_out}")
            print(f"Auto smart search found {len(complete_out.get('results', []))} results")
            
            # Check semantic search availability
            print("\n🧠 Checking semantic search availability...")
            from mcp_sqlite_memory_bank.semantic import is_semantic_search_available
            semantic_available = is_semantic_search_available()
            print(f"Semantic search available: {semantic_available}")
            
            return complete_out.get("results", [])
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        # Cleanup
        smb.DB_PATH = original_db_path
        try:
            os.unlink(db_path)
        except:
            pass

if __name__ == "__main__":
    results = asyncio.run(debug_auto_smart_search())
    print(f"\n📊 Final results count: {len(results)}")
