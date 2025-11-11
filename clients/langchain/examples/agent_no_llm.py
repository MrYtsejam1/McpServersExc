#!/usr/bin/env python3
"""
LangChain MCP Integration - No LLM Required

This example demonstrates how to use MCP servers with LangChain without any LLM.
Perfect for airgapped environments where you want programmatic tool access.

Usage:
    python3 agent_no_llm.py
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_langchain_tools import create_mcp_tools_for_calculator, get_calculator_server_path


async def manual_tool_invocation():
    """
    Demonstrate manual tool invocation without an LLM.
    
    This shows how to use MCP tools through LangChain's tool interface
    for programmatic access, rule-based systems, or custom automation.
    """
    print("=" * 70)
    print("LangChain MCP Integration - Manual Tool Invocation (No LLM)")
    print("=" * 70)
    print()
    
    server_path = get_calculator_server_path()
    print(f"Connecting to MCP server: {server_path}")
    print()
    
    tools = await create_mcp_tools_for_calculator(server_path)
    
    print(f"Loaded {len(tools)} tools:")
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")
    print()
    
    print("-" * 70)
    print("Example 1: Simple Addition")
    print("-" * 70)
    add_tool = next(t for t in tools if t.name == "calculator_add")
    result = await add_tool._arun(a=15, b=27)
    print(f"15 + 27 = {result}")
    print()
    
    print("-" * 70)
    print("Example 2: Chain of Calculations")
    print("-" * 70)
    print("Calculate: (10 + 5) * 3 - 8")
    
    add_tool = next(t for t in tools if t.name == "calculator_add")
    step1 = await add_tool._arun(a=10, b=5)
    print(f"  Step 1: 10 + 5 = {step1}")
    
    multiply_tool = next(t for t in tools if t.name == "calculator_multiply")
    step2 = await multiply_tool._arun(a=float(step1), b=3)
    print(f"  Step 2: {step1} * 3 = {step2}")
    
    subtract_tool = next(t for t in tools if t.name == "calculator_subtract")
    step3 = await subtract_tool._arun(a=float(step2), b=8)
    print(f"  Step 3: {step2} - 8 = {step3}")
    print(f"  Final result: {step3}")
    print()
    
    print("-" * 70)
    print("Example 3: Rule-Based Automation")
    print("-" * 70)
    print("Processing a batch of calculations...")
    
    calculations = [
        ("add", 100, 50),
        ("subtract", 200, 75),
        ("multiply", 12, 8),
        ("divide", 144, 12),
    ]
    
    for operation, a, b in calculations:
        tool = next(t for t in tools if t.name == f"calculator_{operation}")
        result = await tool._arun(a=a, b=b)
        print(f"  {a} {operation} {b} = {result}")
    print()
    
    print("-" * 70)
    print("Example 4: Error Handling")
    print("-" * 70)
    divide_tool = next(t for t in tools if t.name == "calculator_divide")
    result = await divide_tool._arun(a=10, b=0)
    print(f"10 / 0 = {result}")
    print()
    
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print("This example demonstrated:")
    print("  ✓ Loading MCP tools as LangChain tools")
    print("  ✓ Manual tool invocation without an LLM")
    print("  ✓ Chaining multiple tool calls")
    print("  ✓ Rule-based automation")
    print("  ✓ Error handling")
    print()
    print("Use cases for this approach:")
    print("  - Programmatic access to MCP tools")
    print("  - Rule-based automation systems")
    print("  - Testing and validation")
    print("  - Integration with existing Python applications")
    print("  - Airgapped environments without LLM access")
    print()


def main():
    """Main entry point."""
    try:
        asyncio.run(manual_tool_invocation())
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
