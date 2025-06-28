#!/usr/bin/env python3
"""Test script for the upsert_memory functionality."""

import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mcp_sqlite_memory_bank.tools.basic import upsert_memory

# Test data
test_decision = {
    "decision_name": "Semantic Search Results Cleanup",
    "chosen_approach": "Remove embedding vectors from search results",
    "rationale": "Embedding vectors pollute LLM responses with unnecessary technical data"
}

# Test 1: Create new record
print("=== Test 1: Creating new record ===")
result1 = upsert_memory(
    table_name="technical_decisions",
    data=test_decision,
    match_columns=["decision_name"]
)
print(f"Result 1: {result1}")

# Test 2: Update existing record (should update the same record)
print("\n=== Test 2: Updating existing record ===")
updated_decision = test_decision.copy()
updated_decision["rationale"] = "Embedding vectors pollute LLM responses with unnecessary technical data - UPDATED VERSION"

result2 = upsert_memory(
    table_name="technical_decisions", 
    data=updated_decision,
    match_columns=["decision_name"]
)
print(f"Result 2: {result2}")

# Test 3: Different decision name (should create new record)
print("\n=== Test 3: Creating different record ===")
different_decision = {
    "decision_name": "Memory Upsert Implementation",
    "chosen_approach": "Smart upsert with match columns",
    "rationale": "Prevents duplicate records and maintains data consistency"
}

result3 = upsert_memory(
    table_name="technical_decisions",
    data=different_decision,
    match_columns=["decision_name"]
)
print(f"Result 3: {result3}")

print("\n=== All tests completed ===")
