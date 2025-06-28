#!/usr/bin/env python3
"""Test semantic search with different thresholds."""

import asyncio
import tempfile
import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mcp_sqlite_memory_bank import server as smb
from tests.conftest import extract_result
from fastmcp import Client

async def test_semantic_thresholds():
    """Test semantic search with different similarity thresholds."""
    
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
            
            # Add embeddings manually first
            print("🧠 Adding embeddings...")
            embed_result = await client.call_tool(
                "add_embeddings",
                {
                    "table_name": "research_papers",
                    "text_columns": ["title", "abstract", "keywords"]
                }
            )
            embed_out = extract_result(embed_result)
            print(f"Embeddings result: {embed_out}")
            
            # Test semantic search with different thresholds
            query = "learning"
            thresholds = [0.1, 0.2, 0.3, 0.4, 0.5]
            
            for threshold in thresholds:
                print(f"\n🔍 Testing semantic search with threshold {threshold}")
                
                semantic_result = await client.call_tool(
                    "semantic_search",
                    {
                        "query": query,
                        "tables": ["research_papers"],
                        "similarity_threshold": threshold,
                        "limit": 10
                    }
                )
                semantic_out = extract_result(semantic_result)
                print(f"  Results: {len(semantic_out.get('results', []))}")
                
                if semantic_out.get('results'):
                    for i, result in enumerate(semantic_out['results'][:2]):
                        score = result.get('similarity_score', 0)
                        title = result.get('title', 'No title')
                        print(f"    {i+1}. {title} (score: {score:.3f})")
            
            # Test the hybrid search directly
            print(f"\n🔄 Testing direct hybrid search...")
            
            # Use the database's hybrid_search method directly  
            from mcp_sqlite_memory_bank.database import get_database
            db = get_database(smb.DB_PATH)
            
            hybrid_result = db.hybrid_search(
                query="learning",
                tables=["research_papers"],
                semantic_weight=0.6,
                text_weight=0.4,
                limit=10
            )
            print(f"Direct hybrid search result: {hybrid_result}")
            
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
    asyncio.run(test_semantic_thresholds())
