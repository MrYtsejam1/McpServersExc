from mcp.server.fastmcp import FastMCP
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("documentation")

DOCS_DIR = Path(__file__).parent / "docs"


@mcp.resource("docs://getting-started")
async def get_getting_started() -> str:
    """Getting started guide for new users."""
    file_path = DOCS_DIR / "getting-started.md"
    try:
        return file_path.read_text()
    except FileNotFoundError:
        return "Error: Getting started guide not found."


@mcp.resource("docs://api-reference")
async def get_api_reference() -> str:
    """Complete API reference documentation."""
    file_path = DOCS_DIR / "api-reference.md"
    try:
        return file_path.read_text()
    except FileNotFoundError:
        return "Error: API reference not found."


@mcp.resource("docs://changelog/{version}")
async def get_changelog(version: str) -> str:
    """Get changelog for a specific version.
    
    Args:
        version: Version number (e.g., "1.0.0")
    """
    logger.info(f"Fetching changelog for version {version}")
    
    return f"""# Changelog - Version {version}

- Feature A: Enhanced performance
- Feature B: New API endpoints
- Feature C: Improved error handling

- Fixed issue #123: Memory leak in data processing
- Fixed issue #456: Incorrect timestamp formatting
- Fixed issue #789: Race condition in async operations

- None

- Old API v1 endpoints will be removed in version {version}.0

Thank you to all contributors who made this release possible!
"""


@mcp.resource("docs://faq")
async def get_faq() -> str:
    """Frequently asked questions."""
    return """# Frequently Asked Questions

A: Sign up at our website and navigate to the API section in your dashboard.

A: Free tier: 100 requests/hour. Pro tier: 10,000 requests/hour.

A: Please open an issue on our GitHub repository or contact support.

A: Yes! Install it with: pip install our-sdk

A: We currently support US, EU, and Asia-Pacific regions.
"""


@mcp.tool()
async def list_documentation() -> str:
    """List all available documentation resources."""
    resources = [
        "docs://getting-started - Getting started guide for new users",
        "docs://api-reference - Complete API reference documentation",
        "docs://changelog/{version} - Changelog for specific version (e.g., 1.0.0)",
        "docs://faq - Frequently asked questions",
    ]
    return "\n".join(resources)


@mcp.tool()
async def search_docs(query: str) -> str:
    """Search across all documentation.
    
    Args:
        query: Search term to look for
    """
    logger.info(f"Searching documentation for: {query}")
    
    results = []
    query_lower = query.lower()
    
    getting_started = await get_getting_started()
    if query_lower in getting_started.lower():
        results.append("docs://getting-started - Found in Getting Started guide")
    
    api_ref = await get_api_reference()
    if query_lower in api_ref.lower():
        results.append("docs://api-reference - Found in API Reference")
    
    faq = await get_faq()
    if query_lower in faq.lower():
        results.append("docs://faq - Found in FAQ")
    
    if not results:
        return f"No results found for '{query}'"
    
    return "Search results:\n" + "\n".join(results)


def main():
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()
