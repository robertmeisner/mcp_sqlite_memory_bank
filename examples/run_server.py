"""
Example: Run the MCP SQLite Memory Bank server with FastAPI.

Usage:
    python run_server.py [--host 0.0.0.0] [--port 8000]

Requirements:
    - FastAPI
    - Uvicorn

If you see import errors, ensure you are running this script from the project root
or that the package is installed in your environment.
"""

import sys



# --- Import FastMCP app and FastAPI ---
try:
    from mcp_sqlite_memory_bank.server import app as mcp_app
    try:
        print("[DEBUG-top] mcp_app type:", type(mcp_app))
        print("[DEBUG-top] mcp_app._tools:", getattr(mcp_app, '_tools', None))
        print("[DEBUG-top] mcp_app dir:", dir(mcp_app))
        for attr in dir(mcp_app):
            if not attr.startswith('__'):
                try:
                    value = getattr(mcp_app, attr)
                    print(f"[DEBUG-top] mcp_app.{attr}: type={type(value)} value={str(value)[:120]}")
                except Exception as attr_e:
                    print(f"[DEBUG-top] mcp_app.{attr}: <error: {attr_e}>")
    except Exception as debug_e:
        print("[DEBUG-top] Error accessing mcp_app attributes:", debug_e)
except ImportError as e:
    print("ERROR: Could not import 'app' from 'mcp_sqlite_memory_bank.server'.")
    print("Details:", e)
    print("Tip: Run this script from the project root or install the package with:")
    print("    pip install -e .")
    sys.exit(1)

try:
    from fastapi import FastAPI
except ImportError:
    print("ERROR: FastAPI is not installed. Install it with:")
    print("    pip install fastapi")
    sys.exit(1)

try:
    import uvicorn
except ImportError:
    print("ERROR: Uvicorn is not installed. Install it with:")
    print("    pip install uvicorn")
    sys.exit(1)

import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Run the MCP SQLite Memory Bank server with FastAPI docs and FastMCP API.",
        epilog="Tip: For development, run with: uvicorn examples.run_server:fastapi_app --reload"
    )
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind (default: 8000)")
    args = parser.parse_args()

    try:
        # --- Debug: Print mcp_app._tools at startup ---
        print("[DEBUG] mcp_app type:", type(mcp_app))
        print("[DEBUG] mcp_app._tools:", getattr(mcp_app, '_tools', None))
        # --- Create FastAPI app and mount FastMCP ---
        fastapi_app = FastAPI(
            title="MCP SQLite Memory Bank API",
            description="Interactive API docs for SQLite Memory Bank.\n\n- FastMCP API is available at `/mcp` (for LLMs/agents).\n- Interactive docs: `/docs` (Swagger UI), `/redoc` (ReDoc).",
            version="1.0.0"
        )


        @fastapi_app.get("/", tags=["root"])
        async def root():
            return {
                "message": "Welcome to the MCP SQLite Memory Bank API!",
                "docs": "/docs",
                "redoc": "/redoc",
                "mcp_api": "/mcp",
                "tools": "/tools"
            }

        @fastapi_app.get("/tools", tags=["tools"], summary="List all FastMCP tools and their docstrings")
        async def list_tools():
            """
            List all available FastMCP tools and their docstrings at runtime.
            Returns:
                Dict[str, Any]: {"success": True, "tools": [{"name": str, "doc": str}]} or error info.
            """
            import inspect
            try:
                if hasattr(mcp_app, 'get_tools'):
                    tool_objs = mcp_app.get_tools()
                    if inspect.iscoroutine(tool_objs):
                        tool_objs = await tool_objs
                    # tool_objs may be a dict or list
                    if isinstance(tool_objs, dict):
                        tool_iter = tool_objs.values()
                    else:
                        tool_iter = tool_objs
                    tools = []
                    for tool in tool_iter:
                        name = getattr(tool, 'name', None) or getattr(tool, '__name__', None) or str(tool)
                        # Try to get docstring from likely attributes
                        doc = (
                            getattr(tool, 'doc', None) or
                            getattr(getattr(tool, 'fn', None), '__doc__', None) or
                            getattr(getattr(tool, 'func', None), '__doc__', None) or
                            getattr(getattr(tool, 'callback', None), '__doc__', None) or
                            getattr(tool, '__doc__', None) or
                            ''
                        )
                        tools.append({"name": name, "doc": doc.strip()})
                    return {"success": True, "tools": tools, "tools_count": len(tools)}
                else:
                    return {"success": False, "error": "mcp_app.get_tools() not found"}
            except Exception as e:
                return {"success": False, "error": str(e)}

        # Mount FastMCP ASGI app at /mcp
        fastapi_app.mount("/mcp", mcp_app.http_app())

        print(f"Starting MCP SQLite Memory Bank server at http://{args.host}:{args.port} ...")
        print("- Interactive docs: /docs\n- FastMCP API: /mcp")
        uvicorn.run(fastapi_app, host=args.host, port=args.port)
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
        sys.exit(0)
    except Exception as e:
        import traceback
        print("Unexpected error:", e)
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        print("Fatal error during startup:", e)
        traceback.print_exc()
        sys.exit(1)
