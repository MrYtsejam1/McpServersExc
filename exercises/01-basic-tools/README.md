# Exercise 1: Basic Tool Server

## Objective

Learn the fundamentals of MCP server development by building a simple calculator server that exposes basic mathematical operations as tools.

## What You'll Learn

- How to set up an MCP server using FastMCP
- Tool definition and registration
- Type hints and automatic schema generation
- STDIO transport communication
- Proper logging practices

## Background

MCP servers can expose three types of capabilities:
1. **Tools**: Functions that can be called by the LLM (with user approval)
2. **Resources**: File-like data that can be read by clients
3. **Prompts**: Pre-written templates for specific tasks

This exercise focuses on **tools** - the most common MCP capability.

## Setup

```bash
cd exercises/01-basic-tools

# Create virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv add "mcp[cli]"
```

## Task

Create a calculator server that exposes the following tools:

1. `add` - Add two numbers
2. `subtract` - Subtract two numbers
3. `multiply` - Multiply two numbers
4. `divide` - Divide two numbers (with error handling for division by zero)

## Implementation Guide

### Step 1: Create the server file

Create `calculator.py` with the basic structure:

```python
from mcp.server.fastmcp import FastMCP
import logging

# Configure logging to stderr (NEVER use print() in STDIO servers!)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("calculator")
```

### Step 2: Implement the tools

Use the `@mcp.tool()` decorator to register tools. FastMCP automatically generates schemas from your type hints and docstrings:

```python
@mcp.tool()
async def add(a: float, b: float) -> float:
    """Add two numbers together.
    
    Args:
        a: First number
        b: Second number
    """
    logger.info(f"Adding {a} + {b}")
    return a + b
```

**Important Best Practices:**
- Use descriptive function names (verb_noun format)
- Include comprehensive docstrings
- Use type hints for all parameters and return values
- Use `async def` for all tool functions
- Log to stderr, never stdout

### Step 3: Add the main function

```python
def main():
    # Run the server with STDIO transport
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()
```

### Step 4: Complete the implementation

Now implement the remaining tools (`subtract`, `multiply`, `divide`).

**Challenge**: For the `divide` tool, handle division by zero gracefully by returning an error message instead of raising an exception.

## Testing

### Option 1: Using MCP Inspector

```bash
npx @modelcontextprotocol/inspector uv --directory /absolute/path/to/01-basic-tools run calculator.py
```

### Option 2: Using Claude for Desktop

Add to your Claude config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "calculator": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/exercises/01-basic-tools",
        "run",
        "calculator.py"
      ]
    }
  }
}
```

Restart Claude and test with queries like:
- "What is 15 + 27?"
- "Calculate 144 divided by 12"
- "What's 8 times 7?"

## Verification Checklist

- [ ] All four tools are implemented
- [ ] Type hints are used for all parameters and return values
- [ ] Docstrings explain what each tool does
- [ ] Division by zero is handled gracefully
- [ ] No `print()` statements (use logging instead)
- [ ] Server runs without errors
- [ ] Tools appear in Claude for Desktop or MCP Inspector
- [ ] Tools execute correctly when called

## Common Pitfalls

1. **Using print() instead of logging**: This will corrupt STDIO communication
2. **Forgetting async**: All tool functions must be `async def`
3. **Missing type hints**: FastMCP needs these to generate schemas
4. **Poor error handling**: Always handle edge cases gracefully

## Solution

If you get stuck, check `solution.py` in this directory for a complete implementation.

## Next Steps

Once you've completed this exercise, move on to Exercise 2 to learn about integrating external APIs and more advanced error handling.

```bash
cd ../02-weather-server
cat README.md
```
