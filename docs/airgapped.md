# Airgapped Environment Usage Guide

This guide explains how to use the MCP server exercises in an airgapped (offline) environment where you don't have access to Claude for Desktop or other SaaS-based LLM services.

## Overview

All exercises in this repository can be run completely offline. You can test MCP servers using:
- The included Python MCP client (no external services required)
- LangChain integration with local LLMs (optional)
- Manual tool invocation without any LLM

## Prerequisites

### Python Version
- Python 3.10 or higher

### Required Packages
All dependencies can be mirrored and installed offline. See the "Dependency Mirroring" section below.

## Dependency Mirroring

To prepare dependencies for an airgapped environment:

### On a Connected Machine

1. **Download all dependencies:**
   ```bash
   # Clone the repository
   git clone https://github.com/MrYtsejam1/McpServersExc.git
   cd McpServersExc
   
   # Create a wheelhouse directory
   mkdir wheelhouse
   
   # Download all dependencies
   pip download -r requirements-offline.txt -d wheelhouse
   ```

2. **Transfer the wheelhouse:**
   Transfer the entire `wheelhouse/` directory to your airgapped environment via USB drive, internal network, or approved transfer method.

### In the Airgapped Environment

1. **Install from wheelhouse:**
   ```bash
   cd McpServersExc
   pip install --no-index --find-links wheelhouse -r requirements-offline.txt
   ```

2. **Verify installation:**
   ```bash
   python3 -c "import mcp, fastmcp, httpx; print('All packages installed successfully')"
   ```

## Testing MCP Servers Offline

### Using the Python MCP Client

The included Python MCP client (`clients/mcp_client_cli.py`) allows you to test all exercises without any external services:

#### List Available Tools
```bash
python3 clients/mcp_client_cli.py --exercise 01 --action list-tools
```

#### Call a Tool
```bash
python3 clients/mcp_client_cli.py --exercise 01 --action call-tool --name add --args '{"a": 5, "b": 3}'
```

#### List Resources
```bash
python3 clients/mcp_client_cli.py --exercise 03 --action list-resources
```

#### Read a Resource
```bash
python3 clients/mcp_client_cli.py --exercise 03 --action read-resource --uri "docs://getting-started"
```

#### List Prompts
```bash
python3 clients/mcp_client_cli.py --exercise 04 --action list-prompts
```

#### Get a Prompt
```bash
python3 clients/mcp_client_cli.py --exercise 04 --action get-prompt --name review_pull_request --args '{"language": "Python", "pr_description": "Add new feature"}'
```

### Exercise-Specific Offline Usage

#### Exercise 1: Basic Tools (Calculator)
Works completely offline with no modifications needed.

```bash
# Test the calculator
python3 clients/mcp_client_cli.py --exercise 01 --action call-tool --name add --args '{"a": 10, "b": 20}'
python3 clients/mcp_client_cli.py --exercise 01 --action call-tool --name multiply --args '{"a": 7, "b": 6}'
```

#### Exercise 2: Weather Server (Offline Mode)
This exercise normally calls external APIs, but includes an offline mode using local JSON fixtures.

**Enable offline mode:**
```bash
export MCP_OFFLINE=1
```

**Test with offline data:**
```bash
MCP_OFFLINE=1 python3 clients/mcp_client_cli.py --exercise 02 --action call-tool --name get_alerts --args '{"state": "CA"}'
MCP_OFFLINE=1 python3 clients/mcp_client_cli.py --exercise 02 --action call-tool --name get_forecast --args '{"latitude": 39.7456, "longitude": -97.0892}'
```

The offline mode uses pre-recorded API responses from `exercises/02-weather-server/data/weather/` directory.

#### Exercise 3: Resources (Documentation Server)
Works completely offline with no modifications needed.

```bash
# List all documentation resources
python3 clients/mcp_client_cli.py --exercise 03 --action list-resources

# Read specific documentation
python3 clients/mcp_client_cli.py --exercise 03 --action read-resource --uri "docs://getting-started"
python3 clients/mcp_client_cli.py --exercise 03 --action read-resource --uri "docs://api-reference"
```

#### Exercise 4: Prompts (Code Review Assistant)
Works completely offline with no modifications needed.

```bash
# List available prompts
python3 clients/mcp_client_cli.py --exercise 04 --action list-prompts

# Get a code review prompt
python3 clients/mcp_client_cli.py --exercise 04 --action get-prompt --name review_pull_request --args '{"language": "Python", "pr_description": "Add authentication"}'
```

#### Exercise 5: Complete Server (Task Management)
Works completely offline with no modifications needed.

```bash
# Create a task
python3 clients/mcp_client_cli.py --exercise 05 --action call-tool --name create_task --args '{"title": "Review code", "description": "Review PR #123"}'

# List all tasks
python3 clients/mcp_client_cli.py --exercise 05 --action call-tool --name list_tasks --args '{}'

# Read tasks resource
python3 clients/mcp_client_cli.py --exercise 05 --action read-resource --uri "tasks://all"
```

## LangChain Integration (No SaaS Required)

### Option 1: Manual Tool Invocation (No LLM)

Use LangChain's tool interface without any LLM for programmatic access:

```bash
python3 clients/langchain/examples/agent_no_llm.py
```

This example shows how to:
- Connect to MCP servers through LangChain
- Invoke tools programmatically
- Build rule-based automation without LLMs

### Option 2: Local LLM Integration (Optional)

If you have a local LLM available in your airgapped environment, you can integrate it:

**With Ollama:**
```bash
# Requires Ollama installed and running locally
python3 clients/langchain/examples/agent_local_llm.py --model ollama --model-name llama2
```

**With llama.cpp:**
```bash
# Requires llama-cpp-python installed and a model file
python3 clients/langchain/examples/agent_local_llm.py --model llamacpp --model-path /path/to/model.gguf
```

See `clients/langchain/examples/README.md` for detailed setup instructions.

## Building Custom Clients

You can build your own MCP client for your specific use case. Here's a minimal example:

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run_client():
    server_params = StdioServerParameters(
        command="python3",
        args=["exercises/01-basic-tools/solution.py"],
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            print(f"Available tools: {[tool.name for tool in tools.tools]}")
            
            # Call a tool
            result = await session.call_tool("add", {"a": 5, "b": 3})
            print(f"Result: {result.content}")

asyncio.run(run_client())
```

## Troubleshooting

### Import Errors
If you see `ModuleNotFoundError`, ensure all dependencies are installed:
```bash
pip list | grep -E "mcp|fastmcp|httpx|pydantic"
```

### Exercise 2 Network Errors in Offline Mode
Make sure to set the `MCP_OFFLINE=1` environment variable:
```bash
export MCP_OFFLINE=1
# or
MCP_OFFLINE=1 python3 clients/mcp_client_cli.py --exercise 02 ...
```

### Permission Errors
Ensure Python scripts are executable:
```bash
chmod +x clients/mcp_client_cli.py
chmod +x clients/langchain/examples/*.py
```

### Server Won't Start
Check that you're using Python 3.10 or higher:
```bash
python3 --version
```

## Best Practices for Airgapped Environments

1. **Test Dependency Installation:** Before deploying to production, test the wheelhouse installation on a clean airgapped test machine.

2. **Version Pinning:** The `requirements-offline.txt` file pins exact versions to ensure reproducible installations.

3. **Documentation:** Keep a copy of this documentation and all exercise READMEs in your airgapped environment.

4. **Logging:** All servers log to stderr. Redirect logs to files for debugging:
   ```bash
   python3 exercises/01-basic-tools/solution.py 2> server.log
   ```

5. **No Print Statements:** Never use `print()` in MCP servers (it corrupts STDIO transport). Always use the logging module.

6. **Testing:** Use the Python MCP client for comprehensive testing before integrating with your own applications.

## Integration with Qodo Assistant

If you're using Qodo assistant in your IDE, you can:

1. **Use MCP servers as code generation context:** The documentation and examples in these exercises can inform Qodo's suggestions.

2. **Test generated code:** Use the Python MCP client to test any MCP server code that Qodo generates.

3. **Reference patterns:** Use the solution files as reference implementations when asking Qodo to generate MCP server code.

## Additional Resources

- **MCP Specification:** See `docs/mcp-spec-offline.md` (if available) or the specification is embedded in the `mcp` package documentation
- **Python SDK Documentation:** Use `python3 -c "import mcp; help(mcp)"` to view offline documentation
- **FastMCP Documentation:** Use `python3 -c "import fastmcp; help(fastmcp)"` to view offline documentation

## Support

For issues specific to airgapped environments, check:
1. The exercise-specific README files
2. The `clients/` directory examples
3. The troubleshooting section above

Remember: All exercises are designed to work completely offline once dependencies are installed!
