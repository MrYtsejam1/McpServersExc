#!/usr/bin/env python3
"""
File System MCP Server

A comprehensive MCP server for browsing directories, reading files, and searching.
Designed for airgapped environments with security best practices.

Features:
- List directory contents with detailed metadata
- Read file contents with encoding detection
- Search files by name pattern
- Get file metadata (size, modified time, permissions)
- Resource interface for common file types
- Security: Restricted to configured base paths only

Usage:
    python3 solution.py

Test with Python MCP client:
    python3 ../../clients/mcp_client_cli.py --exercise 06 --action list-tools
    python3 ../../clients/mcp_client_cli.py --exercise 06 --action call-tool --name list_directory --args '{"path": "."}'
"""

import os
import logging
from pathlib import Path
from typing import Any, Optional
from datetime import datetime
import mimetypes
import stat

from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("filesystem")

ALLOWED_BASE_PATHS = os.getenv("FS_ALLOWED_PATHS", str(Path.home())).split(":")
ALLOWED_BASE_PATHS = [Path(p).resolve() for p in ALLOWED_BASE_PATHS]

MAX_FILE_SIZE = int(os.getenv("FS_MAX_FILE_SIZE", 10 * 1024 * 1024))


def is_path_allowed(path: Path) -> bool:
    """Check if a path is within allowed base paths."""
    try:
        resolved = path.resolve()
        return any(
            resolved == base or resolved.is_relative_to(base)
            for base in ALLOWED_BASE_PATHS
        )
    except (ValueError, OSError):
        return False


def format_size(size: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.1f}{unit}"
        size /= 1024.0
    return f"{size:.1f}PB"


def format_permissions(mode: int) -> str:
    """Format file permissions in rwx format."""
    perms = []
    for who in ['USR', 'GRP', 'OTH']:
        for what in ['R', 'W', 'X']:
            if mode & getattr(stat, f'S_I{what}{who}'):
                perms.append(what.lower())
            else:
                perms.append('-')
    return ''.join(perms)


@mcp.tool()
def list_directory(path: str = ".", show_hidden: bool = False) -> str:
    """
    List contents of a directory with detailed metadata.
    
    Args:
        path: Directory path to list (default: current directory)
        show_hidden: Include hidden files (starting with .)
    
    Returns:
        Formatted directory listing with file details
    """
    try:
        dir_path = Path(path).expanduser()
        
        if not is_path_allowed(dir_path):
            return f"Error: Access denied to path: {path}"
        
        if not dir_path.exists():
            return f"Error: Path does not exist: {path}"
        
        if not dir_path.is_dir():
            return f"Error: Path is not a directory: {path}"
        
        entries = []
        for entry in sorted(dir_path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
            if not show_hidden and entry.name.startswith('.'):
                continue
            
            try:
                stats = entry.stat()
                size = format_size(stats.st_size) if entry.is_file() else "-"
                modified = datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M')
                perms = format_permissions(stats.st_mode)
                entry_type = "DIR" if entry.is_dir() else "FILE"
                
                entries.append(f"{perms} {entry_type:4} {size:>10} {modified} {entry.name}")
            except (OSError, PermissionError) as e:
                logger.warning(f"Cannot access {entry}: {e}")
                entries.append(f"????????? ???? ?????????? ?????????? {entry.name} (access denied)")
        
        if not entries:
            return f"Directory is empty: {dir_path}"
        
        header = f"Directory: {dir_path.resolve()}\n"
        header += f"Total entries: {len(entries)}\n"
        header += "-" * 80 + "\n"
        header += f"{'PERMS':<9} {'TYPE':<4} {'SIZE':>10} {'MODIFIED':<16} {'NAME'}\n"
        header += "-" * 80
        
        return header + "\n" + "\n".join(entries)
        
    except Exception as e:
        logger.error(f"Error listing directory {path}: {e}")
        return f"Error: {str(e)}"


@mcp.tool()
def read_file(path: str, max_lines: Optional[int] = None) -> str:
    """
    Read contents of a text file.
    
    Args:
        path: File path to read
        max_lines: Maximum number of lines to read (optional)
    
    Returns:
        File contents as text
    """
    try:
        file_path = Path(path).expanduser()
        
        if not is_path_allowed(file_path):
            return f"Error: Access denied to path: {path}"
        
        if not file_path.exists():
            return f"Error: File does not exist: {path}"
        
        if not file_path.is_file():
            return f"Error: Path is not a file: {path}"
        
        file_size = file_path.stat().st_size
        if file_size > MAX_FILE_SIZE:
            return f"Error: File too large ({format_size(file_size)}). Maximum size: {format_size(MAX_FILE_SIZE)}"
        
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type and not mime_type.startswith('text/'):
            return f"Error: File appears to be binary ({mime_type}). Use get_file_info for metadata."
        
        encodings = ['utf-8', 'latin-1', 'cp1252']
        content = None
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    if max_lines:
                        lines = []
                        for i, line in enumerate(f):
                            if i >= max_lines:
                                lines.append(f"\n... (truncated, showing first {max_lines} lines)")
                                break
                            lines.append(line.rstrip('\n'))
                        content = '\n'.join(lines)
                    else:
                        content = f.read()
                break
            except UnicodeDecodeError:
                continue
        
        if content is None:
            return f"Error: Unable to decode file with common encodings"
        
        header = f"File: {file_path.resolve()}\n"
        header += f"Size: {format_size(file_size)}\n"
        header += f"Lines: {content.count(chr(10)) + 1}\n"
        header += "-" * 80 + "\n"
        
        return header + content
        
    except Exception as e:
        logger.error(f"Error reading file {path}: {e}")
        return f"Error: {str(e)}"


@mcp.tool()
def search_files(pattern: str, directory: str = ".", recursive: bool = True) -> str:
    """
    Search for files matching a pattern.
    
    Args:
        pattern: Filename pattern to search for (supports wildcards: *, ?)
        directory: Directory to search in (default: current directory)
        recursive: Search subdirectories recursively
    
    Returns:
        List of matching file paths
    """
    try:
        search_dir = Path(directory).expanduser()
        
        if not is_path_allowed(search_dir):
            return f"Error: Access denied to path: {directory}"
        
        if not search_dir.exists():
            return f"Error: Directory does not exist: {directory}"
        
        if not search_dir.is_dir():
            return f"Error: Path is not a directory: {directory}"
        
        matches = []
        
        if recursive:
            iterator = search_dir.rglob(pattern)
        else:
            iterator = search_dir.glob(pattern)
        
        for match in iterator:
            if is_path_allowed(match):
                try:
                    stats = match.stat()
                    size = format_size(stats.st_size) if match.is_file() else "-"
                    entry_type = "DIR" if match.is_dir() else "FILE"
                    rel_path = match.relative_to(search_dir)
                    matches.append(f"{entry_type:4} {size:>10} {rel_path}")
                except (OSError, PermissionError):
                    continue
        
        if not matches:
            return f"No files found matching pattern '{pattern}' in {search_dir}"
        
        header = f"Search results for '{pattern}' in {search_dir.resolve()}\n"
        header += f"Found {len(matches)} matches\n"
        header += "-" * 80 + "\n"
        header += f"{'TYPE':<4} {'SIZE':>10} {'PATH'}\n"
        header += "-" * 80
        
        return header + "\n" + "\n".join(sorted(matches))
        
    except Exception as e:
        logger.error(f"Error searching files with pattern {pattern}: {e}")
        return f"Error: {str(e)}"


@mcp.tool()
def get_file_info(path: str) -> str:
    """
    Get detailed metadata about a file or directory.
    
    Args:
        path: Path to file or directory
    
    Returns:
        Detailed file/directory information
    """
    try:
        file_path = Path(path).expanduser()
        
        if not is_path_allowed(file_path):
            return f"Error: Access denied to path: {path}"
        
        if not file_path.exists():
            return f"Error: Path does not exist: {path}"
        
        stats = file_path.stat()
        
        info = []
        info.append(f"Path: {file_path.resolve()}")
        info.append(f"Name: {file_path.name}")
        info.append(f"Type: {'Directory' if file_path.is_dir() else 'File'}")
        
        if file_path.is_file():
            info.append(f"Size: {format_size(stats.st_size)} ({stats.st_size:,} bytes)")
            mime_type, encoding = mimetypes.guess_type(str(file_path))
            if mime_type:
                info.append(f"MIME Type: {mime_type}")
            if encoding:
                info.append(f"Encoding: {encoding}")
        
        info.append(f"Permissions: {format_permissions(stats.st_mode)} ({oct(stats.st_mode)[-3:]})")
        info.append(f"Owner UID: {stats.st_uid}")
        info.append(f"Group GID: {stats.st_gid}")
        info.append(f"Created: {datetime.fromtimestamp(stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S')}")
        info.append(f"Modified: {datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")
        info.append(f"Accessed: {datetime.fromtimestamp(stats.st_atime).strftime('%Y-%m-%d %H:%M:%S')}")
        
        if file_path.is_symlink():
            info.append(f"Symlink Target: {file_path.readlink()}")
        
        return "\n".join(info)
        
    except Exception as e:
        logger.error(f"Error getting file info for {path}: {e}")
        return f"Error: {str(e)}"


@mcp.resource("file://{path}")
def read_file_resource(path: str) -> str:
    """
    Resource interface for reading files.
    Allows files to be accessed as MCP resources.
    """
    return read_file(path)


if __name__ == "__main__":
    logger.info("Starting File System MCP Server")
    logger.info(f"Allowed base paths: {[str(p) for p in ALLOWED_BASE_PATHS]}")
    logger.info(f"Max file size: {format_size(MAX_FILE_SIZE)}")
    mcp.run()
