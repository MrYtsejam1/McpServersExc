# MCP Server Creation Exercise

A comprehensive exercise for learning to build Model Context Protocol (MCP) servers following Anthropic best practices.

## 🚀 Works Without Claude for Desktop!

**All exercises work completely offline using the included Python MCP client and LangChain integration.** Claude for Desktop is optional - you can test and use all MCP servers in airgapped environments without any external services.

## Overview

This repository contains a progressive series of exercises to help you master MCP server development. Each exercise builds on the previous one, introducing new concepts and best practices.

## What is MCP?

Model Context Protocol (MCP) is an open-source standard for connecting AI applications to external systems. Think of MCP like a USB-C port for AI applications - it provides a standardized way to connect AI applications to data sources, tools, and workflows.

## Prerequisites

- Python 3.10 or higher
- Basic understanding of Python and async programming
- Familiarity with AI/LLM concepts
- **Claude for Desktop is OPTIONAL** - use the included Python client instead

## Quick Start (No Claude Required)

```bash
# 1. Clone the repository
git clone https://github.com/MrYtsejam1/McpServersExc.git
cd McpServersExc

# 2. Install dependencies
pip install -r requirements-offline.txt

# 3. Test the calculator server
python3 clients/mcp_client_cli.py --exercise 01 --action list-tools
python3 clients/mcp_client_cli.py --exercise 01 --action call-tool --name add --args '{"a": 15, "b": 27}'
```

**For airgapped environments:** See [docs/airgapped.md](docs/airgapped.md) for complete offline installation and usage instructions.

## Setup

### Standard Installation

```bash
# Clone the repository
git clone https://github.com/MrYtsejam1/McpServersExc.git
cd McpServersExc

# Install dependencies
pip install -r requirements-offline.txt
```

### Optional: Install uv (Python package manager)

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Exercise Structure

This exercise is organized into progressive levels:

### Level 1: Basic Tool Server
Learn the fundamentals by building a simple calculator server with basic tools.
- Location: `exercises/01-basic-tools/`
- Concepts: Tool definition, FastMCP basics, STDIO transport

### Level 2: Advanced Tools with External APIs
Build a weather server that integrates with external APIs.
- Location: `exercises/02-weather-server/`
- Concepts: Async operations, API integration, error handling

### Level 3: Resources
Create a server that exposes file-like resources.
- Location: `exercises/03-resources/`
- Concepts: Resource definitions, content types, dynamic resources

### Level 4: Prompts
Implement pre-written prompt templates.
- Location: `exercises/04-prompts/`
- Concepts: Prompt templates, arguments, use cases

### Level 5: Complete Server
Build a comprehensive server combining all concepts.
- Location: `exercises/05-complete-server/`
- Concepts: Integration, best practices, production patterns

## Best Practices

### Logging
- **NEVER** use `print()` in STDIO-based servers - it corrupts JSON-RPC messages
- Always use logging libraries that write to stderr
- HTTP-based servers can use standard output

### Tool Naming
- Follow the format: `verb_noun` (e.g., `get_weather`, `create_document`)
- Use lowercase with underscores
- Be descriptive and specific

### Error Handling
- Always handle API failures gracefully
- Return meaningful error messages
- Use proper async/await patterns

### Type Safety
- Use Python type hints for all functions
- Leverage FastMCP's automatic schema generation
- Document parameters in docstrings

### Security
- Never expose sensitive credentials
- Validate all inputs
- Use environment variables for configuration

## Testing Your Servers

### Using the Python MCP Client (Recommended for Airgapped Environments)

The included Python client works completely offline without any external dependencies:

```bash
# List available tools
python3 clients/mcp_client_cli.py --exercise 01 --action list-tools

# Call a tool
python3 clients/mcp_client_cli.py --exercise 01 --action call-tool --name add --args '{"a": 5, "b": 3}'

# List resources
python3 clients/mcp_client_cli.py --exercise 03 --action list-resources

# Read a resource
python3 clients/mcp_client_cli.py --exercise 03 --action read-resource --uri "docs://getting-started"

# Test offline mode (for weather server)
python3 clients/mcp_client_cli.py --exercise 02 --action call-tool --name get_alerts --args '{"state": "CA"}' --offline
```

### Using LangChain Integration

Integrate MCP servers with your local LLM (e.g., qwen3-coder-480b):

```bash
# Manual tool invocation (no LLM required)
python3 clients/langchain/examples/agent_no_llm.py

# With local LLM
python3 clients/langchain/examples/agent_local_llm.py \
  --model custom \
  --api-url http://your-inference-server:8000/v1 \
  --model-name qwen3-coder-480b
```

See [clients/langchain/examples/README.md](clients/langchain/examples/README.md) for more details.

### Alternative: Using MCP Inspector (Requires npm)

The MCP Inspector is a browser-based developer tool:

```bash
npx @modelcontextprotocol/inspector uv --directory /path/to/exercise run server.py
```

### Alternative: Using Claude for Desktop (Optional)

1. Install Claude for Desktop from https://claude.ai/download
2. Configure your server in `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows)

Example configuration:
```json
{
  "mcpServers": {
    "my-server": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/exercise",
        "run",
        "server.py"
      ]
    }
  }
}
```

3. Restart Claude for Desktop
4. Look for the tools icon to verify your server is connected

## Getting Started

Start with Exercise 1:

```bash
cd exercises/01-basic-tools
cat README.md
```

Follow the instructions in each exercise's README to progress through the learning path.

## Resources

- [Official MCP Documentation](https://modelcontextprotocol.io)
- [MCP Specification](https://modelcontextprotocol.io/specification/2025-06-18)
- [Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Example Servers](https://modelcontextprotocol.io/examples)

## Troubleshooting

### Server not appearing in Claude for Desktop
- Verify the absolute path in your config
- Check that `uv` is in your PATH (run `which uv` or `where uv`)
- Restart Claude for Desktop
- Check Claude's logs for errors

### Import errors
- Ensure you're using Python 3.10+
- Verify virtual environment is activated
- Run `uv sync` to install dependencies

### STDIO communication errors
- Remove all `print()` statements
- Use logging to stderr instead
- Check for syntax errors in your code

## Contributing

Found an issue or want to improve the exercises? Pull requests are welcome!

## License

MIT License - feel free to use this for learning and teaching.
