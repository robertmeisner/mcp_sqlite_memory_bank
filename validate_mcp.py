#!/usr/bin/env python3
"""
MCP Configuration Validator

Validates that the MCP server configuration is correct and all dependencies are available.
Run this script to ensure your MCP setup will work properly.
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def validate_python_environment():
    """Validate Python environment and dependencies."""
    print("🐍 Validating Python Environment...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version < (3, 10):
        print(f"❌ Python version {python_version.major}.{python_version.minor} is too old. Requires 3.10+")
        return False
    else:
        print(f"✅ Python version {python_version.major}.{python_version.minor}.{python_version.micro} is compatible")
    
    # Check key dependencies
    required_packages = [
        "fastmcp",
        "sqlite3",  # Built-in, but we can check
    ]
    
    for package in required_packages:
        try:
            if package == "sqlite3":
                import sqlite3
                print(f"✅ {package} (built-in) is available")
            else:
                __import__(package)
                print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is not installed")
            return False
    
    return True

def validate_mcp_config():
    """Validate MCP configuration file."""
    print("\n📋 Validating MCP Configuration...")
    
    config_path = Path(__file__).parent / ".vscode" / "mcp.json"
    if not config_path.exists():
        print(f"❌ MCP config file not found: {config_path}")
        return False
    
    try:
        with open(config_path) as f:
            config = json.load(f)
        print("✅ MCP config file is valid JSON")
    except json.JSONDecodeError as e:
        print(f"❌ MCP config file has invalid JSON: {e}")
        return False
    
    # Check SQLite_Memory server config
    if "SQLite_Memory" not in config.get("servers", {}):
        print("❌ SQLite_Memory server not configured in mcp.json")
        return False
    
    sqlite_config = config["servers"]["SQLite_Memory"]
    
    # Validate Python command
    python_cmd = sqlite_config.get("command")
    if not python_cmd or not Path(python_cmd).exists():
        print(f"❌ Python command not found: {python_cmd}")
        return False
    else:
        print(f"✅ Python command exists: {python_cmd}")
    
    # Validate module args
    args = sqlite_config.get("args", [])
    if "-m" not in args or "src.mcp_sqlite_memory_bank" not in args:
        print("❌ Invalid module args in MCP config")
        return False
    else:
        print("✅ Module args are correct")
    
    return True

def validate_project_structure():
    """Validate project structure."""
    print("\n📁 Validating Project Structure...")
    
    project_root = Path(__file__).parent
    required_paths = [
        "src/mcp_sqlite_memory_bank/__init__.py",
        "src/mcp_sqlite_memory_bank/__main__.py", 
        "src/mcp_sqlite_memory_bank/server.py",
        "pyproject.toml"
    ]
    
    for path_str in required_paths:
        path = project_root / path_str
        if not path.exists():
            print(f"❌ Missing required file: {path_str}")
            return False
        else:
            print(f"✅ Found: {path_str}")
    
    return True

def test_mcp_server():
    """Test that the MCP server can start."""
    print("\n🧪 Testing MCP Server Startup...")
    
    try:
        # Try to run the server with --help to see if it starts
        result = subprocess.run([
            sys.executable, "-m", "src.mcp_sqlite_memory_bank", "--help"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ MCP server starts successfully")
            print(f"Server help output:\n{result.stdout}")
            return True
        else:
            print(f"❌ MCP server failed to start: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ MCP server startup timed out")
        return False
    except Exception as e:
        print(f"❌ Error testing MCP server: {e}")
        return False

def main():
    """Main validation function."""
    print("🔍 MCP SQLite Memory Bank Configuration Validator")
    print("=" * 50)
    
    validations = [
        ("Python Environment", validate_python_environment),
        ("MCP Configuration", validate_mcp_config),
        ("Project Structure", validate_project_structure),
        ("MCP Server Startup", test_mcp_server),
    ]
    
    all_passed = True
    for name, validator in validations:
        try:
            passed = validator()
            if not passed:
                all_passed = False
        except Exception as e:
            print(f"❌ Error in {name} validation: {e}")
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All validations passed! Your MCP setup is ready to use.")
        print("\nTo use with VS Code, ensure the MCP extension is installed and configured.")
    else:
        print("⚠️  Some validations failed. Please fix the issues above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
