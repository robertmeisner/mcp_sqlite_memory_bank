#!/usr/bin/env python3
"""
Test script for enhanced upsert functionality
"""
import os
import sys
import tempfile

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mcp_sqlite_memory_bank.tools.basic import upsert_memory
from mcp_sqlite_memory_bank.database import get_database

# Create a temporary database for testing
with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
    db_path = tmp.name

# Set the database path
os.environ['DB_PATH'] = db_path

print("Testing enhanced upsert functionality...")
print("=" * 50)

try:
    # Create a test table first
    db = get_database(db_path)
    
    # Create table
    table_result = db.create_table('test_upsert', [
        {'name': 'id', 'type': 'INTEGER PRIMARY KEY AUTOINCREMENT'},
        {'name': 'username', 'type': 'TEXT'},
        {'name': 'email', 'type': 'TEXT'},
        {'name': 'status', 'type': 'TEXT'},
        {'name': 'age', 'type': 'INTEGER'}
    ])
    
    print("1. Table creation:", table_result)
    
    # Test 1: Create new record
    print("\n2. Creating new record...")
    result1 = upsert_memory('test_upsert', {
        'username': 'john_doe',
        'email': 'john@example.com',
        'status': 'active',
        'age': 25
    }, ['username'])
    
    print("Create result:", result1)
    
    # Test 2: Update existing record (should show updated fields)
    print("\n3. Updating existing record...")
    result2 = upsert_memory('test_upsert', {
        'username': 'john_doe',  # Same (match column)
        'email': 'john.doe@newdomain.com',  # Changed
        'status': 'inactive',  # Changed
        'age': 25  # Same
    }, ['username'])
    
    print("Update result:", result2)
    
    # Test 3: Update with same values (should show empty updated_fields)
    print("\n4. Updating with same values...")
    result3 = upsert_memory('test_upsert', {
        'username': 'john_doe',
        'email': 'john.doe@newdomain.com',
        'status': 'inactive',
        'age': 25
    }, ['username'])
    
    print("No-change result:", result3)
    
finally:
    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)
    
print("\n" + "=" * 50)
print("Test completed!")
