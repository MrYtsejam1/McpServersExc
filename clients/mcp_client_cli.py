#!/usr/bin/env python3
"""
Standalone MCP Client CLI

A command-line client for testing MCP servers without requiring Claude for Desktop
or any external services. Works completely offline.

Usage:
    python3 mcp_client_cli.py --exercise 01 --action list-tools
    python3 mcp_client_cli.py --exercise 01 --action call-tool --name add --args '{"a": 5, "b": 3}'
    python3 mcp_client_cli.py --exercise 03 --action list-resources
    python3 mcp_client_cli.py --exercise 03 --action read-resource --uri "docs://getting-started"
    
    python3 mcp_client_cli.py --exercise 02 --action call-tool --name get_alerts --args '{"state": "CA"}' --offline
"""

import asyncio
import argparse
import json
import sys
import os
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


EXERCISES = {
    "01": "exercises/01-basic-tools/solution.py",
    "02": "exercises/02-weather-server/solution.py",
    "03": "exercises/03-resources/solution.py",
    "04": "exercises/04-prompts/solution.py",
    "05": "exercises/05-complete-server/solution.py",
}


async def list_tools(session: ClientSession) -> None:
    """List all available tools from the MCP server."""
    result = await session.list_tools()
    
    if not result.tools:
        print("No tools available")
        return
    
    print(f"\nAvailable Tools ({len(result.tools)}):")
    print("=" * 60)
    for tool in result.tools:
        print(f"\n{tool.name}")
        if tool.description:
            print(f"  Description: {tool.description}")
        if hasattr(tool, 'inputSchema') and tool.inputSchema:
            schema = tool.inputSchema
            if isinstance(schema, dict) and 'properties' in schema:
                print(f"  Parameters:")
                for param_name, param_info in schema['properties'].items():
                    param_type = param_info.get('type', 'any')
                    param_desc = param_info.get('description', '')
                    required = param_name in schema.get('required', [])
                    req_str = " (required)" if required else ""
                    print(f"    - {param_name}: {param_type}{req_str}")
                    if param_desc:
                        print(f"      {param_desc}")


async def call_tool(session: ClientSession, name: str, args: dict[str, Any]) -> None:
    """Call a specific tool with the given arguments."""
    try:
        result = await session.call_tool(name, args)
        
        print(f"\nTool: {name}")
        print("=" * 60)
        print("\nResult:")
        
        if hasattr(result, 'content') and result.content:
            for item in result.content:
                if hasattr(item, 'text'):
                    print(item.text)
                else:
                    print(item)
        else:
            print(result)
            
    except Exception as e:
        print(f"Error calling tool: {e}", file=sys.stderr)
        sys.exit(1)


async def list_resources(session: ClientSession) -> None:
    """List all available resources from the MCP server."""
    result = await session.list_resources()
    
    if not result.resources:
        print("No resources available")
        return
    
    print(f"\nAvailable Resources ({len(result.resources)}):")
    print("=" * 60)
    for resource in result.resources:
        print(f"\n{resource.uri}")
        if resource.name:
            print(f"  Name: {resource.name}")
        if resource.description:
            print(f"  Description: {resource.description}")
        if hasattr(resource, 'mimeType') and resource.mimeType:
            print(f"  MIME Type: {resource.mimeType}")


async def read_resource(session: ClientSession, uri: str) -> None:
    """Read a specific resource by URI."""
    try:
        result = await session.read_resource(uri)
        
        print(f"\nResource: {uri}")
        print("=" * 60)
        print("\nContent:")
        
        if hasattr(result, 'contents') and result.contents:
            for item in result.contents:
                if hasattr(item, 'text'):
                    print(item.text)
                elif hasattr(item, 'blob'):
                    print(f"[Binary data: {len(item.blob)} bytes]")
                else:
                    print(item)
        else:
            print(result)
            
    except Exception as e:
        print(f"Error reading resource: {e}", file=sys.stderr)
        sys.exit(1)


async def list_prompts(session: ClientSession) -> None:
    """List all available prompts from the MCP server."""
    result = await session.list_prompts()
    
    if not result.prompts:
        print("No prompts available")
        return
    
    print(f"\nAvailable Prompts ({len(result.prompts)}):")
    print("=" * 60)
    for prompt in result.prompts:
        print(f"\n{prompt.name}")
        if prompt.description:
            print(f"  Description: {prompt.description}")
        if hasattr(prompt, 'arguments') and prompt.arguments:
            print(f"  Arguments:")
            for arg in prompt.arguments:
                required = arg.required if hasattr(arg, 'required') else False
                req_str = " (required)" if required else ""
                print(f"    - {arg.name}{req_str}")
                if hasattr(arg, 'description') and arg.description:
                    print(f"      {arg.description}")


async def get_prompt(session: ClientSession, name: str, args: dict[str, Any]) -> None:
    """Get a specific prompt with the given arguments."""
    try:
        result = await session.get_prompt(name, args)
        
        print(f"\nPrompt: {name}")
        print("=" * 60)
        print("\nMessages:")
        
        if hasattr(result, 'messages') and result.messages:
            for msg in result.messages:
                role = msg.role if hasattr(msg, 'role') else 'unknown'
                print(f"\n[{role.upper()}]")
                if hasattr(msg, 'content'):
                    if hasattr(msg.content, 'text'):
                        print(msg.content.text)
                    else:
                        print(msg.content)
        else:
            print(result)
            
    except Exception as e:
        print(f"Error getting prompt: {e}", file=sys.stderr)
        sys.exit(1)


async def run_client(exercise: str, action: str, offline: bool = False, **kwargs) -> None:
    """Run the MCP client with the specified exercise and action."""
    if exercise not in EXERCISES:
        print(f"Error: Unknown exercise '{exercise}'", file=sys.stderr)
        print(f"Available exercises: {', '.join(EXERCISES.keys())}", file=sys.stderr)
        sys.exit(1)
    
    repo_root = Path(__file__).parent.parent
    server_path = repo_root / EXERCISES[exercise]
    
    if not server_path.exists():
        print(f"Error: Server file not found: {server_path}", file=sys.stderr)
        sys.exit(1)
    
    server_env = dict(os.environ)
    if offline:
        server_env["MCP_OFFLINE"] = "1"
        print(f"Running in OFFLINE mode (MCP_OFFLINE=1)", file=sys.stderr)
    
    server_params = StdioServerParameters(
        command="python3",
        args=[str(server_path)],
        env=server_env,
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                if action == "list-tools":
                    await list_tools(session)
                elif action == "call-tool":
                    if 'name' not in kwargs or 'args' not in kwargs:
                        print("Error: --name and --args required for call-tool", file=sys.stderr)
                        sys.exit(1)
                    await call_tool(session, kwargs['name'], kwargs['args'])
                elif action == "list-resources":
                    await list_resources(session)
                elif action == "read-resource":
                    if 'uri' not in kwargs:
                        print("Error: --uri required for read-resource", file=sys.stderr)
                        sys.exit(1)
                    await read_resource(session, kwargs['uri'])
                elif action == "list-prompts":
                    await list_prompts(session)
                elif action == "get-prompt":
                    if 'name' not in kwargs or 'args' not in kwargs:
                        print("Error: --name and --args required for get-prompt", file=sys.stderr)
                        sys.exit(1)
                    await get_prompt(session, kwargs['name'], kwargs['args'])
                else:
                    print(f"Error: Unknown action '{action}'", file=sys.stderr)
                    print("Available actions: list-tools, call-tool, list-resources, read-resource, list-prompts, get-prompt", file=sys.stderr)
                    sys.exit(1)
                    
    except Exception as e:
        print(f"Error connecting to server: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Standalone MCP Client for testing MCP servers offline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --exercise 01 --action list-tools
  
  %(prog)s --exercise 01 --action call-tool --name add --args '{"a": 5, "b": 3}'
  
  %(prog)s --exercise 03 --action list-resources
  
  %(prog)s --exercise 03 --action read-resource --uri "docs://getting-started"
  
  %(prog)s --exercise 04 --action list-prompts
  
  %(prog)s --exercise 04 --action get-prompt --name review_pull_request --args '{"language": "Python"}'
  
  %(prog)s --exercise 02 --action call-tool --name get_alerts --args '{"state": "CA"}' --offline
        """
    )
    
    parser.add_argument(
        "--exercise",
        required=True,
        choices=list(EXERCISES.keys()),
        help="Exercise number (01-05)"
    )
    
    parser.add_argument(
        "--action",
        required=True,
        choices=["list-tools", "call-tool", "list-resources", "read-resource", "list-prompts", "get-prompt"],
        help="Action to perform"
    )
    
    parser.add_argument(
        "--name",
        help="Tool or prompt name (for call-tool and get-prompt actions)"
    )
    
    parser.add_argument(
        "--args",
        help="JSON string of arguments (for call-tool and get-prompt actions)"
    )
    
    parser.add_argument(
        "--uri",
        help="Resource URI (for read-resource action)"
    )
    
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Run in offline mode (sets MCP_OFFLINE=1 for the server)"
    )
    
    args = parser.parse_args()
    
    kwargs = {}
    if args.name:
        kwargs['name'] = args.name
    if args.uri:
        kwargs['uri'] = args.uri
    if args.args:
        try:
            kwargs['args'] = json.loads(args.args)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in --args: {e}", file=sys.stderr)
            sys.exit(1)
    
    asyncio.run(run_client(args.exercise, args.action, offline=args.offline, **kwargs))


if __name__ == "__main__":
    main()
