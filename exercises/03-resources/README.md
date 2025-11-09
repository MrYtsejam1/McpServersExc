# Exercise 3: Resources

## Objective

Learn how to expose file-like data through MCP resources, enabling AI applications to read structured data from your server.

## What You'll Learn

- Resource definition and registration
- Static vs dynamic resources
- Content types and MIME types
- Resource URIs and naming conventions
- Reading and serving file contents

## Background

Resources in MCP are file-like data that clients can read. Unlike tools (which are functions the LLM calls), resources are data sources that the LLM can access. Think of them as a file system that your MCP server exposes.

Common use cases for resources:
- Configuration files
- Documentation
- Database query results
- API responses
- Log files
- Templates

## Setup

```bash
cd exercises/03-resources

# Create virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv add "mcp[cli]"
```

## Task

Create a documentation server that exposes various documentation files as resources:

1. Static resources: Pre-defined documentation files
2. Dynamic resources: Generated content based on parameters
3. List resources: Allow clients to discover available resources

## Implementation Guide

### Step 1: Create sample documentation files

Create a `docs/` directory with sample files:

```bash
mkdir docs
```

Create `docs/getting-started.md`:
```markdown
# Getting Started

Welcome to our API! This guide will help you get started quickly.

## Installation

Install our SDK using pip:
```
pip install our-sdk
```

## Quick Example

```python
from our_sdk import Client

client = Client(api_key="your-key")
result = client.do_something()
```
```

Create `docs/api-reference.md`:
```markdown
# API Reference

## Methods

### client.get_data(id: str)
Retrieves data by ID.

### client.create_item(name: str, value: int)
Creates a new item.
```

### Step 2: Set up the server

Create `docs_server.py`:

```python
from mcp.server.fastmcp import FastMCP
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("documentation")

# Base directory for documentation files
DOCS_DIR = Path(__file__).parent / "docs"
```

### Step 3: Implement static resources

Use the `@mcp.resource()` decorator to expose resources:

```python
@mcp.resource("docs://getting-started")
async def get_getting_started() -> str:
    """Getting started guide for new users."""
    file_path = DOCS_DIR / "getting-started.md"
    return file_path.read_text()


@mcp.resource("docs://api-reference")
async def get_api_reference() -> str:
    """Complete API reference documentation."""
    file_path = DOCS_DIR / "api-reference.md"
    return file_path.read_text()
```

**Resource URI Format:**
- Use a custom scheme (e.g., `docs://`)
- Use descriptive paths
- Keep URIs stable (don't change them)

### Step 4: Implement dynamic resources

Dynamic resources can generate content based on parameters:

```python
@mcp.resource("docs://changelog/{version}")
async def get_changelog(version: str) -> str:
    """Get changelog for a specific version.
    
    Args:
        version: Version number (e.g., "1.0.0")
    """
    # In a real implementation, you might fetch this from a database
    # or generate it from git history
    return f"""# Changelog - Version {version}

## New Features
- Feature A
- Feature B

## Bug Fixes
- Fixed issue #123
- Fixed issue #456

## Breaking Changes
- None
"""
```

### Step 5: Add a tool to list available resources

While FastMCP automatically provides resource listing, you can add a tool to help users discover resources:

```python
@mcp.tool()
async def list_documentation() -> str:
    """List all available documentation resources."""
    resources = [
        "docs://getting-started - Getting started guide",
        "docs://api-reference - API reference documentation",
        "docs://changelog/{version} - Changelog for specific version",
    ]
    return "\n".join(resources)
```

### Step 6: Add the main function

```python
def main():
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()
```

## Testing

### Using MCP Inspector

```bash
npx @modelcontextprotocol/inspector uv --directory /absolute/path/to/03-resources run docs_server.py
```

In the inspector:
1. Click on "Resources" tab
2. You should see your resources listed
3. Click on a resource to view its content

### Using Claude for Desktop

Add to your Claude config:

```json
{
  "mcpServers": {
    "documentation": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/exercises/03-resources",
        "run",
        "docs_server.py"
      ]
    }
  }
}
```

Test with queries like:
- "Show me the getting started documentation"
- "What's in the API reference?"
- "Show me the changelog for version 2.0.0"

## Best Practices

1. **Stable URIs**: Don't change resource URIs once published
2. **Descriptive Names**: Use clear, descriptive resource names
3. **Proper MIME Types**: Set appropriate content types
4. **Error Handling**: Handle missing files gracefully
5. **Documentation**: Document what each resource provides
6. **Caching**: Consider caching for expensive resources

## Verification Checklist

- [ ] Static resources are implemented
- [ ] Dynamic resources with parameters work
- [ ] Resource URIs follow a consistent scheme
- [ ] Documentation files exist and are readable
- [ ] Error handling for missing files
- [ ] No `print()` statements
- [ ] Resources appear in MCP Inspector
- [ ] Resources can be read by clients

## Common Pitfalls

1. **Changing URIs**: Breaking existing integrations
2. **Missing files**: Not handling FileNotFoundError
3. **Large files**: Not considering memory usage
4. **No documentation**: Users don't know what resources exist
5. **Inconsistent naming**: Confusing resource schemes

## Challenge Extensions

Try these additional features:

1. Add a search tool that searches across all documentation
2. Implement resource templates with variable substitution
3. Add support for different output formats (JSON, YAML, etc.)
4. Create a resource that aggregates multiple files
5. Add caching for frequently accessed resources

## Solution

Check `solution.py` for a complete implementation.

## Next Steps

Move on to Exercise 4 to learn about MCP Prompts:

```bash
cd ../04-prompts
cat README.md
```
