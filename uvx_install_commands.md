# UVX Installation Commands for Fresh Projects

## Problem
Even after deploying v1.6.7 with numpy constraint fixes, fresh projects using uvx still encounter numpy 1.26.4 compilation errors.

## Root Cause
- uvx caching old dependency resolution
- PyPI propagation delays
- uvx attempting source builds despite wheel availability

## **WORKING SOLUTIONS**

### Option 1: Clear uvx Cache + Force Latest Version
```bash
# Clear uvx cache completely
uvx cache clear

# Install with explicit latest version
uvx --python 3.10 run --spec mcp-sqlite-memory-bank==1.6.7 mcp-sqlite-memory-bank --help
```

### Option 2: Use Alternative Installation Method
```bash
# Use pip in temporary virtual environment
python -m venv temp_env
temp_env\Scripts\activate
pip install mcp-sqlite-memory-bank==1.6.7
mcp-sqlite-memory-bank --help
deactivate
rmdir /s temp_env
```

### Option 3: Pre-install Dependencies (Bypass uvx Compilation)
```bash
# Pre-install numpy wheel to avoid compilation
python -m pip install --user numpy==1.26.3
uvx --python 3.10 mcp-sqlite-memory-bank
```

### Option 4: Use pipx Instead of uvx
```bash
# pipx is more reliable for complex dependencies
pip install --user pipx
pipx install mcp-sqlite-memory-bank==1.6.7
pipx run mcp-sqlite-memory-bank --help
```

## **For MCP Configuration**
Use this in your fresh project's .vscode/mcp.json:

```json
{
  "mcpServers": {
    "sqlite-memory": {
      "command": "uvx",
      "args": ["--python", "3.10", "run", "--spec", "mcp-sqlite-memory-bank==1.6.7", "mcp-sqlite-memory-bank"],
      "env": {}
    }
  }
}
```

## **Verification Commands**
```bash
# Check if installation worked
uvx --python 3.10 run --spec mcp-sqlite-memory-bank==1.6.7 mcp-sqlite-memory-bank --version

# Test MCP server startup
uvx --python 3.10 run --spec mcp-sqlite-memory-bank==1.6.7 mcp-sqlite-memory-bank --help
```

## **Why This Happens**
1. **uvx Caching**: uvx caches dependency resolution, may use old numpy constraints
2. **PyPI Propagation**: CDN/mirror delays in distributing v1.6.7
3. **Source vs Wheel**: uvx sometimes prefers source builds over wheels
4. **Dependency Resolution**: Complex dependency trees can cause resolution conflicts

## **Long-term Solution**
The v1.6.7 fix will work once:
- uvx cache is cleared
- PyPI fully propagates the update
- Fresh dependency resolution occurs

This is why the fix works in our development environment but not in cached uvx environments.
