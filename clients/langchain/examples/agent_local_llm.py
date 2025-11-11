#!/usr/bin/env python3
"""
LangChain MCP Integration - Local LLM Support

This example demonstrates how to use MCP servers with LangChain and a local LLM.
Supports various local inference options including custom API endpoints.

Supports:
  - Custom API endpoints (e.g., qwen3-coder-480b on your inference infrastructure)
  - Ollama (if available)
  - llama.cpp (if available)

Usage:
    python3 agent_local_llm.py --model custom --api-url http://your-inference-server:8000/v1 --model-name qwen3-coder-480b
    
    python3 agent_local_llm.py --model ollama --model-name llama2
    
    python3 agent_local_llm.py --model llamacpp --model-path /path/to/model.gguf
"""

import asyncio
import argparse
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_langchain_tools import create_mcp_tools_for_calculator, get_calculator_server_path


def create_llm_with_custom_api(api_url: str, model_name: str, api_key: Optional[str] = None):
    """
    Create an LLM client for a custom API endpoint.
    
    This works with OpenAI-compatible APIs, including your qwen3-coder-480b
    inference infrastructure.
    """
    try:
        from langchain_openai import ChatOpenAI
    except ImportError:
        print("Error: langchain-openai not installed", file=sys.stderr)
        print("Install with: pip install langchain-openai", file=sys.stderr)
        sys.exit(1)
    
    return ChatOpenAI(
        base_url=api_url,
        api_key=api_key or "not-needed",  # Some local APIs don't require keys
        model=model_name,
        temperature=0,
    )


def create_llm_with_ollama(model_name: str):
    """Create an LLM client for Ollama."""
    try:
        from langchain_community.llms import Ollama
    except ImportError:
        print("Error: langchain-community not installed", file=sys.stderr)
        print("Install with: pip install langchain-community", file=sys.stderr)
        sys.exit(1)
    
    return Ollama(model=model_name, temperature=0)


def create_llm_with_llamacpp(model_path: str):
    """Create an LLM client for llama.cpp."""
    try:
        from langchain_community.llms import LlamaCpp
    except ImportError:
        print("Error: langchain-community not installed", file=sys.stderr)
        print("Install with: pip install langchain-community llama-cpp-python", file=sys.stderr)
        sys.exit(1)
    
    return LlamaCpp(
        model_path=model_path,
        temperature=0,
        max_tokens=2000,
        n_ctx=2048,
    )


async def run_agent_with_llm(llm, tools):
    """
    Run an agent with the given LLM and tools.
    
    This demonstrates how to use MCP tools with a local LLM in LangChain.
    """
    try:
        from langchain.agents import AgentExecutor, create_tool_calling_agent
        from langchain_core.prompts import ChatPromptTemplate
    except ImportError:
        print("Error: Required LangChain packages not installed", file=sys.stderr)
        print("Install with: pip install langchain langchain-core", file=sys.stderr)
        sys.exit(1)
    
    print("=" * 70)
    print("LangChain MCP Integration - Local LLM Agent")
    print("=" * 70)
    print()
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant with access to calculator tools. "
                   "Use the tools to perform calculations when needed."),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    
    print("Creating agent with tools:")
    for tool in tools:
        print(f"  - {tool.name}")
    print()
    
    try:
        agent = create_tool_calling_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    except Exception as e:
        print(f"Note: Tool calling not supported by this model: {e}")
        print("Falling back to ReAct agent...")
        from langchain.agents import create_react_agent
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant with access to calculator tools."),
            ("human", "{input}\n\nThought: {agent_scratchpad}"),
        ])
        
        agent = create_react_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    queries = [
        "What is 15 plus 27?",
        "Calculate (10 + 5) * 3",
        "If I have 100 dollars and spend 35, then multiply the remainder by 2, how much do I have?",
    ]
    
    for i, query in enumerate(queries, 1):
        print("-" * 70)
        print(f"Query {i}: {query}")
        print("-" * 70)
        
        try:
            result = await agent_executor.ainvoke({"input": query})
            print(f"\nResult: {result['output']}")
        except Exception as e:
            print(f"Error processing query: {e}", file=sys.stderr)
        
        print()
    
    print("=" * 70)
    print("Agent execution complete!")
    print("=" * 70)


async def main_async(args):
    """Main async function."""
    server_path = get_calculator_server_path()
    print(f"Connecting to MCP server: {server_path}")
    print()
    
    tools = await create_mcp_tools_for_calculator(server_path)
    print(f"Loaded {len(tools)} MCP tools")
    print()
    
    if args.model == "custom":
        if not args.api_url or not args.model_name:
            print("Error: --api-url and --model-name required for custom model", file=sys.stderr)
            sys.exit(1)
        
        print(f"Using custom API endpoint: {args.api_url}")
        print(f"Model: {args.model_name}")
        llm = create_llm_with_custom_api(args.api_url, args.model_name, args.api_key)
        
    elif args.model == "ollama":
        if not args.model_name:
            print("Error: --model-name required for Ollama", file=sys.stderr)
            sys.exit(1)
        
        print(f"Using Ollama with model: {args.model_name}")
        llm = create_llm_with_ollama(args.model_name)
        
    elif args.model == "llamacpp":
        if not args.model_path:
            print("Error: --model-path required for llama.cpp", file=sys.stderr)
            sys.exit(1)
        
        print(f"Using llama.cpp with model: {args.model_path}")
        llm = create_llm_with_llamacpp(args.model_path)
    
    else:
        print(f"Error: Unknown model type: {args.model}", file=sys.stderr)
        sys.exit(1)
    
    print()
    
    await run_agent_with_llm(llm, tools)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="LangChain MCP Integration with Local LLM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --model custom --api-url http://your-server:8000/v1 --model-name qwen3-coder-480b
  
  %(prog)s --model ollama --model-name llama2
  
  %(prog)s --model llamacpp --model-path /path/to/model.gguf
        """
    )
    
    parser.add_argument(
        "--model",
        required=True,
        choices=["custom", "ollama", "llamacpp"],
        help="Type of local LLM to use"
    )
    
    parser.add_argument(
        "--api-url",
        help="API URL for custom model (e.g., http://localhost:8000/v1)"
    )
    
    parser.add_argument(
        "--model-name",
        help="Model name (for custom API or Ollama)"
    )
    
    parser.add_argument(
        "--model-path",
        help="Path to model file (for llama.cpp)"
    )
    
    parser.add_argument(
        "--api-key",
        help="API key for custom endpoint (if required)"
    )
    
    args = parser.parse_args()
    
    try:
        asyncio.run(main_async(args))
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
