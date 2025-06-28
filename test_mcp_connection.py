#!/usr/bin/env python3
"""
Test MCP server connection directly via stdio.

This script tests if the MCP server responds correctly to an initialize request.
"""
import subprocess
import json
import sys
import time

def test_mcp_server():
    """Test MCP server stdio connection."""
    cmd = [
        "C:\\Users\\Robert\\anaconda3\\Scripts\\conda.exe",
        "run", "-n", "llm_dev", "python", "-m", "src.mcp_sqlite_memory_bank.server"
    ]
    
    print("Starting MCP server...")
    print(f"Command: {' '.join(cmd)}")
    
    process = None
    try:
        # Start the server process
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0
        )
        
        # Send initialize request
        initialize_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {
                        "listChanged": True
                    },
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        print("Sending initialize request...")
        request_json = json.dumps(initialize_request) + "\n"
        print(f"Request: {request_json.strip()}")
        
        if process.stdin:
            process.stdin.write(request_json)
            process.stdin.flush()
        
        # Wait for response (with timeout)
        print("Waiting for response...")
        time.sleep(2)
        
        # Check if process is still running
        if process.poll() is not None:
            print(f"Process exited with code: {process.returncode}")
            if process.stderr:
                stderr_output = process.stderr.read()
                if stderr_output:
                    print(f"Stderr: {stderr_output}")
            return False
        
        # Try to read response
        try:
            if process.stdout:
                response = process.stdout.readline()
                if response:
                    print(f"Response: {response.strip()}")
                    return True
                else:
                    print("No response received")
                    return False
            else:
                print("No stdout available")
                return False
        except Exception as e:
            print(f"Error reading response: {e}")
            return False
            
    except Exception as e:
        print(f"Error running server: {e}")
        return False
    finally:
        if process is not None:
            process.terminate()
            process.wait()

if __name__ == "__main__":
    success = test_mcp_server()
    sys.exit(0 if success else 1)
