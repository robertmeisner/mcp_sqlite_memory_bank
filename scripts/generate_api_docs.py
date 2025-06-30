#!/usr/bin/env python3
"""
C03 - Automated API Documentation Generation

Generates comprehensive API documentation from MCP tool docstrings and function signatures.
This script provides automated documentation generation for the SQLite Memory Bank MCP server.
"""

import ast
import inspect
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import re
from datetime import datetime


class MCPDocumentationGenerator:
    """Automated API documentation generator for MCP tools."""
    
    def __init__(self, src_path: str = "src/mcp_sqlite_memory_bank"):
        self.src_path = Path(src_path)
        self.tools_path = self.src_path / "tools"
        self.output_path = Path("docs/generated")
        self.output_path.mkdir(parents=True, exist_ok=True)
        
    def extract_tool_info(self, module_path: Path) -> List[Dict[str, Any]]:
        """Extract MCP tool information from a Python module."""
        tools = []
        
        try:
            # Read the source code
            content = module_path.read_text(encoding='utf-8')
            tree = ast.parse(content)
            
            # Find all function definitions with @mcp.tool decorator
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check for @mcp.tool decorator
                    has_mcp_decorator = False
                    for decorator in node.decorator_list:
                        # Check for @mcp.tool (attribute access)
                        if (isinstance(decorator, ast.Attribute) and 
                            isinstance(decorator.value, ast.Name) and
                            decorator.value.id == 'mcp' and
                            decorator.attr == 'tool'):
                            has_mcp_decorator = True
                            break
                        # Check for @mcp.tool() (function call)
                        elif (isinstance(decorator, ast.Call) and
                              isinstance(decorator.func, ast.Attribute) and
                              isinstance(decorator.func.value, ast.Name) and
                              decorator.func.value.id == 'mcp' and
                              decorator.func.attr == 'tool'):
                            has_mcp_decorator = True
                            break
                    
                    if has_mcp_decorator:
                        tool_info = self._extract_function_details(node, content)
                        tool_info['module'] = module_path.stem
                        tool_info['file_path'] = str(module_path.relative_to(self.src_path))
                        tools.append(tool_info)
                        
        except Exception as e:
            print(f"Error processing {module_path}: {e}")
            
        return tools
    
    def _extract_function_details(self, node: ast.FunctionDef, content: str) -> Dict[str, Any]:
        """Extract detailed information about a function."""
        # Get docstring
        docstring = ast.get_docstring(node) or "No description available"
        
        # Parse docstring for structured information
        parsed_doc = self._parse_docstring(docstring)
        
        # Extract function signature
        args = []
        for arg in node.args.args:
            arg_info = {'name': arg.arg}
            # Try to get type annotation
            if arg.annotation:
                arg_info['type'] = self._get_type_string(arg.annotation)
            args.append(arg_info)
            
        # Extract return type
        return_type = None
        if node.returns:
            return_type = self._get_type_string(node.returns)
            
        return {
            'name': node.name,
            'docstring': docstring,
            'description': parsed_doc.get('description', ''),
            'args': args,
            'return_type': return_type,
            'examples': parsed_doc.get('examples', []),
            'usage': parsed_doc.get('usage', ''),
            'line_number': node.lineno
        }
    
    def _parse_docstring(self, docstring: str) -> Dict[str, Any]:
        """Parse structured information from docstring."""
        lines = docstring.split('\n')
        
        # Extract description (first paragraph)
        description_lines = []
        for line in lines:
            line = line.strip()
            if not line:
                break
            description_lines.append(line)
        description = ' '.join(description_lines)
        
        # Extract examples
        examples = []
        in_example = False
        example_lines = []
        
        for line in lines:
            if 'Example' in line and '>>>' in line:
                in_example = True
                example_lines = [line.strip()]
            elif in_example:
                if line.strip().startswith('>>>') or line.strip().startswith('{'):
                    example_lines.append(line.strip())
                elif not line.strip():
                    if example_lines:
                        examples.append('\n'.join(example_lines))
                        example_lines = []
                    in_example = False
                else:
                    example_lines.append(line.strip())
        
        if example_lines:
            examples.append('\n'.join(example_lines))
            
        return {
            'description': description,
            'examples': examples
        }
    
    def _get_type_string(self, annotation) -> str:
        """Convert AST type annotation to string."""
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Constant):
            return str(annotation.value)
        elif isinstance(annotation, ast.Attribute):
            return f"{self._get_type_string(annotation.value)}.{annotation.attr}"
        elif isinstance(annotation, ast.Subscript):
            return f"{self._get_type_string(annotation.value)}[{self._get_type_string(annotation.slice)}]"
        else:
            return "Any"
    
    def generate_markdown_docs(self, tools: List[Dict[str, Any]]) -> str:
        """Generate Markdown API documentation."""
        doc_lines = [
            "# SQLite Memory Bank API Reference",
            "",
            "*Auto-generated from source code*",
            "",
            "This document provides comprehensive API reference for all MCP tools in the SQLite Memory Bank.",
            "",
            "## Tool Categories",
            ""
        ]
        
        # Group tools by module
        tools_by_module = {}
        for tool in tools:
            module = tool['module']
            if module not in tools_by_module:
                tools_by_module[module] = []
            tools_by_module[module].append(tool)
        
        # Generate table of contents
        doc_lines.append("### Table of Contents")
        doc_lines.append("")
        
        for module, module_tools in tools_by_module.items():
            doc_lines.append(f"- **{module.title()}** ({len(module_tools)} tools)")
            for tool in module_tools:
                doc_lines.append(f"  - [{tool['name']}](#{tool['name'].replace('_', '-')})")
        doc_lines.append("")
        
        # Generate detailed documentation for each module
        for module, module_tools in tools_by_module.items():
            # Get module file path from first tool in module
            module_file_path = module_tools[0]['file_path'] if module_tools else "Unknown"
            doc_lines.extend([
                f"## {module.title()} Tools",
                "",
                f"*Module: `{module_file_path}`*",
                ""
            ])
            
            for tool in module_tools:
                doc_lines.extend(self._generate_tool_docs(tool))
                doc_lines.append("")
        
        return '\n'.join(doc_lines)
    
    def _generate_tool_docs(self, tool: Dict[str, Any]) -> List[str]:
        """Generate documentation for a single tool."""
        lines = [
            f"### `{tool['name']}`",
            "",
            tool['description'] or "No description available",
            ""
        ]
        
        # Function signature
        args_str = ", ".join([
            f"{arg['name']}: {arg.get('type', 'Any')}"
            for arg in tool['args']
        ])
        return_type = tool.get('return_type', 'ToolResponse')
        
        lines.extend([
            "**Signature:**",
            "```python",
            f"def {tool['name']}({args_str}) -> {return_type}:",
            "```",
            ""
        ])
        
        # Parameters
        if tool['args']:
            lines.extend([
                "**Parameters:**",
                ""
            ])
            for arg in tool['args']:
                arg_type = arg.get('type', 'Any')
                lines.append(f"- `{arg['name']}` ({arg_type}): Parameter description")
            lines.append("")
        
        # Examples
        if tool['examples']:
            lines.extend([
                "**Examples:**",
                ""
            ])
            for example in tool['examples']:
                lines.extend([
                    "```python",
                    example,
                    "```",
                    ""
                ])
        
        # Source location
        lines.extend([
            f"*Source: {tool['file_path']}:{tool['line_number']}*",
            "",
            "---",
            ""
        ])
        
        return lines
    
    def generate_json_api_spec(self, tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate JSON API specification."""
        api_spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "SQLite Memory Bank MCP API",
                "description": "MCP tools for intelligent memory management",
                "version": "1.4.3",
                "generated": "auto-generated"
            },
            "servers": [
                {
                    "url": "mcp://sqlite-memory-bank",
                    "description": "MCP Server"
                }
            ],
            "paths": {},
            "components": {
                "schemas": {
                    "ToolResponse": {
                        "type": "object",
                        "properties": {
                            "success": {"type": "boolean"},
                            "error": {"type": "string"},
                            "category": {"type": "string"},
                            "details": {"type": "object"}
                        }
                    }
                }
            }
        }
        
        # Add each tool as a path
        for tool in tools:
            tool_path = f"/tools/{tool['name']}"
            api_spec["paths"][tool_path] = {
                "post": {
                    "summary": tool['description'],
                    "description": tool['docstring'],
                    "operationId": tool['name'],
                    "tags": [tool['module']],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": self._generate_request_schema(tool['args'])
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Successful operation",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ToolResponse"}
                                }
                            }
                        }
                    }
                }
            }
        
        return api_spec
    
    def _generate_request_schema(self, args: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate JSON schema for request parameters."""
        properties = {}
        required = []
        
        for arg in args:
            arg_type = arg.get('type', 'string')
            
            # Map Python types to JSON schema types
            if 'str' in arg_type or 'String' in arg_type:
                schema_type = "string"
            elif 'int' in arg_type or 'Integer' in arg_type:
                schema_type = "integer"
            elif 'bool' in arg_type or 'Boolean' in arg_type:
                schema_type = "boolean"
            elif 'List' in arg_type:
                schema_type = "array"
            elif 'Dict' in arg_type:
                schema_type = "object"
            else:
                schema_type = "string"
            
            properties[arg['name']] = {"type": schema_type}
            
            # Assume all args are required unless Optional
            if 'Optional' not in arg_type:
                required.append(arg['name'])
        
        return {
            "type": "object",
            "properties": properties,
            "required": required
        }
    
    def run(self) -> None:
        """Generate all documentation formats."""
        print("🔄 Starting automated API documentation generation...")
        
        all_tools = []
        
        # Process server.py file where MCP tools are registered
        server_file = self.src_path / "server.py"
        if server_file.exists():
            print(f"  📄 Processing {server_file.name}...")
            tools = self.extract_tool_info(server_file)
            all_tools.extend(tools)
            print(f"    Found {len(tools)} MCP tools")
        
        # Process all Python files in tools directory
        for tool_file in self.tools_path.glob("*.py"):
            if tool_file.name.startswith("__"):
                continue
                
            print(f"  📄 Processing {tool_file.name}...")
            tools = self.extract_tool_info(tool_file)
            all_tools.extend(tools)
            print(f"    Found {len(tools)} MCP tools")
        
        print(f"📊 Total MCP tools discovered: {len(all_tools)}")
        
        # Generate Markdown documentation
        print("📝 Generating Markdown API reference...")
        markdown_docs = self.generate_markdown_docs(all_tools)
        markdown_path = self.output_path / "api_reference.md"
        markdown_path.write_text(markdown_docs, encoding='utf-8')
        print(f"  ✅ Markdown docs: {markdown_path}")
        
        # Generate JSON API specification
        print("🔧 Generating JSON API specification...")
        json_spec = self.generate_json_api_spec(all_tools)
        json_path = self.output_path / "api_spec.json"
        json_path.write_text(json.dumps(json_spec, indent=2), encoding='utf-8')
        print(f"  ✅ JSON API spec: {json_path}")
        
        # Generate tool summary
        print("📋 Generating tool summary...")
        summary = {
            "total_tools": len(all_tools),
            "tools_by_module": {
                module: len([t for t in all_tools if t['module'] == module])
                for module in set(tool['module'] for tool in all_tools)
            },
            "generated_at": "auto-generated",
            "tools": [
                {
                    "name": tool['name'],
                    "module": tool['module'],
                    "description": tool['description'][:100] + "..." if len(tool['description']) > 100 else tool['description']
                }
                for tool in all_tools
            ]
        }
        
        summary_path = self.output_path / "tools_summary.json"
        summary_path.write_text(json.dumps(summary, indent=2), encoding='utf-8')
        print(f"  ✅ Tools summary: {summary_path}")
        
        print("✅ Automated API documentation generation completed!")
        print(f"📁 Output directory: {self.output_path.absolute()}")


if __name__ == "__main__":
    generator = MCPDocumentationGenerator()
    generator.run()
