#!/usr/bin/env python3
"""
Debug script to test auto_smart_search functionality
"""

import os
import sys
sys.path.insert(0, 'src')

from mcp_sqlite_memory_bank.database import get_database
from mcp_sqlite_memory_bank.semantic import get_semantic_engine, is_semantic_search_available

def debug_semantic_search():
    print("=== Semantic Search Debug ===")
    print(f"Semantic search available: {is_semantic_search_available()}")
    
    if is_semantic_search_available():
        try:
            engine = get_semantic_engine()
            print(f"Engine type: {type(engine)}")
            print(f"Engine model: {engine.model_name}")
            print(f"Has hybrid_search: {hasattr(engine, 'hybrid_search')}")
            print(f"hybrid_search callable: {callable(getattr(engine, 'hybrid_search', None))}")
            print(f"hybrid_search type: {type(getattr(engine, 'hybrid_search', None))}")
        except Exception as e:
            print(f"Error creating semantic engine: {e}")
    
    print("\n=== Database Test ===")
    db_path = os.environ.get("DB_PATH", "./test.db")
    print(f"Using database: {db_path}")
    
    try:
        db = get_database(db_path)
        print(f"Database type: {type(db)}")
        
        # Test simple table list
        tables_result = db.list_tables()
        print(f"Tables result: {tables_result}")
        
    except Exception as e:
        print(f"Error with database: {e}")

if __name__ == "__main__":
    debug_semantic_search()
