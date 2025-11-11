# Exercise 6: File System Server

Build a comprehensive MCP server for browsing directories, reading files, and searching the file system.

## Overview

This exercise demonstrates how to create a production-ready MCP server that interacts with the file system while following security best practices. The server is designed for airgapped environments and includes proper access controls.

## Features

### Tools

1. **list_directory** - List directory contents with detailed metadata
   - Shows file size, permissions, modification time
   - Optional hidden file display
   - Sorted output (directories first, then alphabetically)

2. **read_file** - Read text file contents
   - Automatic encoding detection (UTF-8, Latin-1, CP1252)
   - File size limits for safety
   - Binary file detection
   - Optional line limiting

3. **search_files** - Search for files by pattern
   - Supports wildcards (*, ?)
   - Recursive or non-recursive search
   - Shows file type and size

4. **get_file_info** - Get detailed file/directory metadata
   - Size, permissions, timestamps
   - MIME type detection
   - Symlink resolution

### Resources

- **file://{path}** - Access files as MCP resources

### Security Features

- **Path Restrictions**: Only allows access to configured base paths
- **File Size Limits**: Prevents reading extremely large files
- **Binary Detection**: Warns about binary files
- **Permission Handling**: Gracefully handles access denied errors

## Configuration

### Environment Variables

```bash
# Set allowed base paths (colon-separated)
export FS_ALLOWED_PATHS="/home/user:/tmp:/var/log"

# Set maximum file size (in bytes, default: 10MB)
export FS_MAX_FILE_SIZE=10485760
```

## Testing Without Claude

### Using the Python MCP Client

#### List Tools
```bash
python3 ../../clients/mcp_client_cli.py --exercise 06 --action list-tools
```

#### List Directory
```bash
# List current directory
python3 ../../clients/mcp_client_cli.py --exercise 06 --action call-tool \
  --name list_directory --args '{}'

# List specific directory
python3 ../../clients/mcp_client_cli.py --exercise 06 --action call-tool \
  --name list_directory --args '{"path": "/tmp"}'

# Show hidden files
python3 ../../clients/mcp_client_cli.py --exercise 06 --action call-tool \
  --name list_directory --args '{"path": ".", "show_hidden": true}'
```

#### Read File
```bash
# Read entire file
python3 ../../clients/mcp_client_cli.py --exercise 06 --action call-tool \
  --name read_file --args '{"path": "README.md"}'

# Read first 20 lines
python3 ../../clients/mcp_client_cli.py --exercise 06 --action call-tool \
  --name read_file --args '{"path": "solution.py", "max_lines": 20}'
```

#### Search Files
```bash
# Search for Python files recursively
python3 ../../clients/mcp_client_cli.py --exercise 06 --action call-tool \
  --name search_files --args '{"pattern": "*.py", "directory": "."}'

# Search for markdown files (non-recursive)
python3 ../../clients/mcp_client_cli.py --exercise 06 --action call-tool \
  --name search_files --args '{"pattern": "*.md", "directory": ".", "recursive": false}'
```

#### Get File Info
```bash
python3 ../../clients/mcp_client_cli.py --exercise 06 --action call-tool \
  --name get_file_info --args '{"path": "solution.py"}'
```

### Using LangChain Integration

```python
from clients.langchain.mcp_langchain_tools import create_generic_mcp_tools

# Create tools for the filesystem server
tools = create_generic_mcp_tools("exercises/06-filesystem-server/solution.py")

# Use with your local LLM or manually
for tool in tools:
    print(f"Tool: {tool.name}")
```

## Best Practices Demonstrated

### 1. Security First
```python
# Always validate paths are within allowed base paths
def is_path_allowed(path: Path) -> bool:
    resolved = path.resolve()
    return any(
        resolved == base or resolved.is_relative_to(base)
        for base in ALLOWED_BASE_PATHS
    )
```

### 2. Error Handling
```python
# Gracefully handle permission errors
try:
    stats = entry.stat()
    # ... process stats
except (OSError, PermissionError) as e:
    logger.warning(f"Cannot access {entry}: {e}")
    # Return user-friendly error message
```

### 3. User-Friendly Output
```python
# Format file sizes in human-readable format
def format_size(size: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.1f}{unit}"
        size /= 1024.0
```

### 4. Logging to stderr
```python
# Never use print() - always use logging
logger.info("Starting File System MCP Server")
logger.error(f"Error reading file {path}: {e}")
```

### 5. Type Hints
```python
def list_directory(path: str = ".", show_hidden: bool = False) -> str:
    """Fully typed function signature"""
```

## Common Use Cases

### 1. Code Review Assistant
```bash
# List all Python files in a project
python3 ../../clients/mcp_client_cli.py --exercise 06 --action call-tool \
  --name search_files --args '{"pattern": "*.py", "directory": "../../"}'

# Read specific file for review
python3 ../../clients/mcp_client_cli.py --exercise 06 --action call-tool \
  --name read_file --args '{"path": "../../clients/mcp_client_cli.py"}'
```

### 2. Log Analysis
```bash
# List log directory
python3 ../../clients/mcp_client_cli.py --exercise 06 --action call-tool \
  --name list_directory --args '{"path": "/var/log"}'

# Read recent log entries
python3 ../../clients/mcp_client_cli.py --exercise 06 --action call-tool \
  --name read_file --args '{"path": "/var/log/syslog", "max_lines": 50}'
```

### 3. Documentation Browser
```bash
# Find all markdown documentation
python3 ../../clients/mcp_client_cli.py --exercise 06 --action call-tool \
  --name search_files --args '{"pattern": "*.md", "directory": "../../docs"}'

# Read documentation file
python3 ../../clients/mcp_client_cli.py --exercise 06 --action call-tool \
  --name read_file --args '{"path": "../../docs/airgapped.md"}'
```

## Airgapped Environment Notes

This server works completely offline with no external dependencies beyond the Python standard library and MCP SDK.

**Configuration for airgapped use:**
```bash
# Set allowed paths to your workspace
export FS_ALLOWED_PATHS="/home/user/workspace:/home/user/projects"

# Start the server (via Python MCP client)
python3 ../../clients/mcp_client_cli.py --exercise 06 --action list-tools
```

## Troubleshooting

### "Access denied to path"
- Check that the path is within `FS_ALLOWED_PATHS`
- Verify the path exists and you have read permissions
- Use absolute paths or paths relative to allowed base paths

### "File too large"
- Increase `FS_MAX_FILE_SIZE` environment variable
- Use `max_lines` parameter to read partial content
- Use `get_file_info` to check file size first

### "Unable to decode file"
- File may be binary - use `get_file_info` to check MIME type
- Try a different encoding if you know the file encoding

### Permission Errors
- Ensure you have read permissions on the directory/file
- Check file ownership and permissions with `get_file_info`

## Extension Ideas

1. **File Writing**: Add tools for creating/modifying files
2. **Directory Operations**: Create, delete, move directories
3. **File Watching**: Monitor files for changes
4. **Archive Support**: Read contents of zip/tar files
5. **Git Integration**: Show git status, diffs, etc.
6. **Syntax Highlighting**: Return code with syntax highlighting
7. **File Comparison**: Compare two files side-by-side

## Integration with Qodo Assistant

When using this server with Qodo assistant in your IDE:

1. **Code Navigation**: Use `search_files` to find files, then `read_file` to view them
2. **Documentation**: Use `read_file` to access project documentation
3. **Log Analysis**: Use `list_directory` and `read_file` to analyze logs
4. **File Metadata**: Use `get_file_info` to check file properties

## Next Steps

After completing this exercise:
- Try integrating with LangChain for automated file operations
- Add custom tools for your specific file system needs
- Combine with other MCP servers for comprehensive workflows
- Deploy in your airgapped environment with proper security configuration

## Resources

- [MCP Specification](https://modelcontextprotocol.io/specification)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Python pathlib Documentation](https://docs.python.org/3/library/pathlib.html)
