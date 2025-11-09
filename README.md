# MCP Server Creation Exercise

A comprehensive exercise for learning to build Model Context Protocol (MCP) servers following Anthropic best practices.

## Overview

This repository contains a progressive series of exercises to help you master MCP server development. Each exercise builds on the previous one, introducing new concepts and best practices.

## What is MCP?

Model Context Protocol (MCP) is an open-source standard for connecting AI applications to external systems. Think of MCP like a USB-C port for AI applications - it provides a standardized way to connect AI applications to data sources, tools, and workflows.

## Prerequisites

- Python 3.10 or higher
- Basic understanding of Python and async programming
- Familiarity with AI/LLM concepts
- Claude for Desktop (optional, for testing)

## Setup

### Install uv (Python package manager)

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Restart your terminal after installation.

### Clone and Setup

```bash
git clone https://github.com/MrYtsejam1/McpServersExc.git
cd McpServersExc
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

### Using MCP Inspector
The MCP Inspector is a developer tool for testing servers:

```bash
npx @modelcontextprotocol/inspector uv --directory /path/to/exercise run server.py
```

### Using Claude for Desktop

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
