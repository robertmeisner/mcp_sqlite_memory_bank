"""
Example: Using SQLite Memory Bank for LLM Agent Memory Management

This example demonstrates how to use SQLite Memory Bank to implement 
persistent memory for LLM agents, allowing them to:
1. Store and retrieve project information
2. Track technical decisions
3. Remember user preferences
4. Maintain session context

For detailed memory usage instructions, see memory_instructions.md

Usage:
    python examples/agent_memory_example.py

Requirements:
    - mcp_sqlite_memory_bank
"""

import asyncio
import datetime
from typing import Optional
from mcp_sqlite_memory_bank.server import (
    _create_row_impl, _read_rows_impl, _update_rows_impl, _delete_rows_impl
)

# Import additional functions for table management
import sqlite3
import os
from mcp_sqlite_memory_bank.utils import validate_identifier, validate_column_definition

def create_table(table_name: str, columns: list) -> dict:
    """Create a table with the given name and columns."""
    try:
        validate_identifier(table_name, "table name")
        for column in columns:
            validate_column_definition(column)
        
        # Connect to database
        db_path = os.environ.get("DB_PATH", "./test.db")
        with sqlite3.connect(db_path) as conn:
            # Build column definitions
            column_defs = []
            for col in columns:
                column_defs.append(f"{col['name']} {col['type']}")
            
            # Create table
            query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(column_defs)})"
            conn.execute(query)
            conn.commit()
            
            return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

def list_tables() -> dict:
    """List all tables in the database."""
    try:
        db_path = os.environ.get("DB_PATH", "./test.db")
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = [row[0] for row in cur.fetchall()]
            return {"success": True, "tables": tables}
    except Exception as e:
        return {"success": False, "error": str(e)}

def create_row(table_name: str, data: dict) -> dict:
    """Create a row in the given table."""
    return _create_row_impl(table_name, data)

def read_rows(table_name: str, where: Optional[dict] = None) -> dict:
    """Read rows from the given table."""
    return _read_rows_impl(table_name, where)

def update_rows(table_name: str, data: dict, where: Optional[dict] = None) -> dict:
    """Update rows in the given table."""
    return _update_rows_impl(table_name, data, where)

def delete_rows(table_name: str, where: Optional[dict] = None) -> dict:
    """Delete rows from the given table."""
    return _delete_rows_impl(table_name, where)

async def initialize_memory_schema():
    """Initialize the memory schema tables if they don't exist."""
    print("Initializing memory schema...")
    
    # Get existing tables
    tables_result = list_tables()
    existing_tables = tables_result['tables'] if tables_result.get('success', False) else []
    
    # Create project structure table if it doesn't exist
    if 'project_structure' not in existing_tables:
        print("Creating project_structure table...")
        create_table('project_structure', [
            {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
            {"name": "category", "type": "TEXT NOT NULL"},
            {"name": "title", "type": "TEXT NOT NULL"},
            {"name": "content", "type": "TEXT NOT NULL"},
            {"name": "timestamp", "type": "TEXT DEFAULT CURRENT_TIMESTAMP"}
        ])
    
    # Create technical decisions table if it doesn't exist
    if 'technical_decisions' not in existing_tables:
        print("Creating technical_decisions table...")
        create_table('technical_decisions', [
            {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
            {"name": "decision_name", "type": "TEXT NOT NULL"},
            {"name": "chosen_approach", "type": "TEXT NOT NULL"},
            {"name": "alternatives", "type": "TEXT"},
            {"name": "rationale", "type": "TEXT NOT NULL"},
            {"name": "timestamp", "type": "TEXT DEFAULT CURRENT_TIMESTAMP"}
        ])
    
    # Create user preferences table if it doesn't exist
    if 'user_preferences' not in existing_tables:
        print("Creating user_preferences table...")
        create_table('user_preferences', [
            {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
            {"name": "preference_type", "type": "TEXT NOT NULL"},
            {"name": "preference_value", "type": "TEXT NOT NULL"},
            {"name": "context", "type": "TEXT"},
            {"name": "timestamp", "type": "TEXT DEFAULT CURRENT_TIMESTAMP"}
        ])
    
    # Create session context table if it doesn't exist
    if 'session_context' not in existing_tables:
        print("Creating session_context table...")
        create_table('session_context', [
            {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
            {"name": "session_id", "type": "TEXT NOT NULL"},
            {"name": "topic", "type": "TEXT NOT NULL"},
            {"name": "progress_state", "type": "TEXT NOT NULL"},
            {"name": "next_steps", "type": "TEXT"},
            {"name": "timestamp", "type": "TEXT DEFAULT CURRENT_TIMESTAMP"}
        ])


async def store_project_information():
    """Store information about the project structure."""
    print("\nStoring project information...")
    
    # Store information about project architecture
    create_row('project_structure', {
        'category': 'architecture',
        'title': 'SQLite Memory Bank Structure',
        'content': 'The project follows a modular design with server.py containing the FastMCP implementation, types.py defining data structures, and utils.py providing helper functions.'
    })
    
    # Store information about file organization
    create_row('project_structure', {
        'category': 'file_organization',
        'title': 'Project Layout',
        'content': 'The project uses a src/ layout with package code in src/mcp_sqlite_memory_bank/, examples in examples/, and tests in tests/.'
    })


async def store_technical_decision():
    """Store a technical decision with rationale."""
    print("\nStoring technical decision...")
    
    # Store decision about API design
    create_row('technical_decisions', {
        'decision_name': 'API Design Pattern',
        'chosen_approach': 'Explicit function-based tools',
        'alternatives': 'Single multiplex function with operation parameter',
        'rationale': 'Explicit function-based tools provide better discoverability for LLMs and clients, with clearer type hints and validation.'
    })


async def store_user_preference():
    """Store user preferences."""
    print("\nStoring user preference...")
    
    # Check if preference already exists
    existing_prefs = read_rows('user_preferences', {
        'preference_type': 'code_style'
    })
    
    if existing_prefs and existing_prefs.get('success', False) and existing_prefs.get('rows', []):
        # Update existing preference
        print("Updating existing user preference...")
        update_rows('user_preferences', 
                    {'preference_value': 'explicit type annotations', 
                     'context': 'User prefers explicit type annotations for all functions and variables'},
                    {'id': existing_prefs['rows'][0]['id']})
    else:
        # Create new preference
        print("Creating new user preference...")
        create_row('user_preferences', {
            'preference_type': 'code_style',
            'preference_value': 'explicit type annotations',
            'context': 'User prefers explicit type annotations for all functions and variables'
        })


async def start_new_session():
    """Start a new session and store context."""
    print("\nStarting new session...")
    
    # Generate session ID from current timestamp
    session_id = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    
    # Store session context
    create_row('session_context', {
        'session_id': session_id,
        'topic': 'Agent Memory Implementation',
        'progress_state': 'initializing',
        'next_steps': 'Demonstrate memory retrieval'
    })
    
    return session_id


async def retrieve_and_display_memory():
    """Retrieve and display memory from all tables."""
    print("\nRetrieving memory...")
    
    # Retrieve project structure
    project_info = read_rows('project_structure')
    if project_info.get('success', False) and project_info.get('rows', []):
        print("\n--- Project Structure ---")
        for item in project_info['rows']:
            print(f"[{item['category']}] {item['title']}: {item['content'][:50]}...")
    
    # Retrieve technical decisions
    decisions = read_rows('technical_decisions')
    if decisions.get('success', False) and decisions.get('rows', []):
        print("\n--- Technical Decisions ---")
        for item in decisions['rows']:
            print(f"Decision: {item['decision_name']}")
            print(f"Approach: {item['chosen_approach']}")
            print(f"Rationale: {item['rationale'][:50]}...")
    
    # Retrieve user preferences
    preferences = read_rows('user_preferences')
    if preferences.get('success', False) and preferences.get('rows', []):
        print("\n--- User Preferences ---")
        for item in preferences['rows']:
            print(f"{item['preference_type']}: {item['preference_value']}")
            if item.get('context'):
                print(f"Context: {item['context']}")
    
    # Retrieve session context
    sessions = read_rows('session_context')
    if sessions.get('success', False) and sessions.get('rows', []):
        print("\n--- Session Context ---")
        for item in sessions['rows']:
            print(f"Session {item['session_id']}: {item['topic']}")
            print(f"Progress: {item['progress_state']}")
            if item.get('next_steps'):
                print(f"Next Steps: {item['next_steps']}")


async def update_session_progress(session_id):
    """Update the session progress."""
    print("\nUpdating session progress...")
    
    # Find the session
    session = read_rows('session_context', {'session_id': session_id})
    if session.get('success', False) and session.get('rows', []):
        # Update progress
        update_rows('session_context', 
                    {'progress_state': 'completed',
                     'next_steps': 'Session demonstration complete'},
                    {'id': session['rows'][0]['id']})
        print(f"Updated session {session_id} progress to 'completed'")
    else:
        print(f"Session {session_id} not found")


async def main():
    """Run the agent memory example."""
    print("=== SQLite Memory Bank for LLM Agent Memory Example ===")
    
    # Initialize memory schema
    await initialize_memory_schema()
    
    # Store various types of information
    await store_project_information()
    await store_technical_decision()
    await store_user_preference()
    
    # Start a new session
    session_id = await start_new_session()
    
    # Retrieve and display memory
    await retrieve_and_display_memory()
    
    # Update session progress
    await update_session_progress(session_id)
    
    print("\n=== Example Complete ===")
    print("Memory schema and data have been initialized and stored in the SQLite database.")
    print("This data will persist across sessions and can be used by LLM agents for context.")


if __name__ == "__main__":
    asyncio.run(main())
