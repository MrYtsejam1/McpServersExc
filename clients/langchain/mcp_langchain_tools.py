"""
LangChain Integration for MCP Servers

This module provides integration between MCP servers and LangChain, allowing you to
use MCP tools as LangChain Tools in your agents and chains.

Works completely offline - no SaaS services required.
"""

import asyncio
from typing import Any, Optional, Type
from pathlib import Path

from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPToolWrapper(BaseTool):
    """Wrapper that exposes an MCP tool as a LangChain Tool."""
    
    name: str
    description: str
    mcp_session: Any = Field(exclude=True)
    mcp_tool_name: str
    args_schema: Optional[Type[BaseModel]] = None
    
    class Config:
        arbitrary_types_allowed = True
    
    def _run(self, **kwargs: Any) -> str:
        """Synchronous wrapper around async MCP tool call."""
        return asyncio.run(self._arun(**kwargs))
    
    async def _arun(self, **kwargs: Any) -> str:
        """Call the MCP tool asynchronously."""
        try:
            result = await self.mcp_session.call_tool(self.mcp_tool_name, kwargs)
            
            if hasattr(result, 'content') and result.content:
                texts = []
                for item in result.content:
                    if hasattr(item, 'text'):
                        texts.append(item.text)
                    else:
                        texts.append(str(item))
                return "\n".join(texts)
            else:
                return str(result)
                
        except Exception as e:
            return f"Error calling MCP tool: {e}"


class CalculatorAddTool(BaseTool):
    """LangChain tool for adding two numbers using MCP calculator server."""
    
    name: str = "calculator_add"
    description: str = "Add two numbers together. Input should be two numbers 'a' and 'b'."
    mcp_session: Any = Field(exclude=True)
    
    class Config:
        arbitrary_types_allowed = True
    
    class InputSchema(BaseModel):
        a: float = Field(description="First number")
        b: float = Field(description="Second number")
    
    args_schema: Type[BaseModel] = InputSchema
    
    def _run(self, a: float, b: float) -> str:
        """Synchronous wrapper."""
        return asyncio.run(self._arun(a, b))
    
    async def _arun(self, a: float, b: float) -> str:
        """Add two numbers using MCP server."""
        try:
            result = await self.mcp_session.call_tool("add", {"a": a, "b": b})
            if hasattr(result, 'content') and result.content:
                return result.content[0].text
            return str(result)
        except Exception as e:
            return f"Error: {e}"


class CalculatorSubtractTool(BaseTool):
    """LangChain tool for subtracting two numbers using MCP calculator server."""
    
    name: str = "calculator_subtract"
    description: str = "Subtract b from a. Input should be two numbers 'a' and 'b'."
    mcp_session: Any = Field(exclude=True)
    
    class Config:
        arbitrary_types_allowed = True
    
    class InputSchema(BaseModel):
        a: float = Field(description="Number to subtract from")
        b: float = Field(description="Number to subtract")
    
    args_schema: Type[BaseModel] = InputSchema
    
    def _run(self, a: float, b: float) -> str:
        """Synchronous wrapper."""
        return asyncio.run(self._arun(a, b))
    
    async def _arun(self, a: float, b: float) -> str:
        """Subtract two numbers using MCP server."""
        try:
            result = await self.mcp_session.call_tool("subtract", {"a": a, "b": b})
            if hasattr(result, 'content') and result.content:
                return result.content[0].text
            return str(result)
        except Exception as e:
            return f"Error: {e}"


class CalculatorMultiplyTool(BaseTool):
    """LangChain tool for multiplying two numbers using MCP calculator server."""
    
    name: str = "calculator_multiply"
    description: str = "Multiply two numbers together. Input should be two numbers 'a' and 'b'."
    mcp_session: Any = Field(exclude=True)
    
    class Config:
        arbitrary_types_allowed = True
    
    class InputSchema(BaseModel):
        a: float = Field(description="First number")
        b: float = Field(description="Second number")
    
    args_schema: Type[BaseModel] = InputSchema
    
    def _run(self, a: float, b: float) -> str:
        """Synchronous wrapper."""
        return asyncio.run(self._arun(a, b))
    
    async def _arun(self, a: float, b: float) -> str:
        """Multiply two numbers using MCP server."""
        try:
            result = await self.mcp_session.call_tool("multiply", {"a": a, "b": b})
            if hasattr(result, 'content') and result.content:
                return result.content[0].text
            return str(result)
        except Exception as e:
            return f"Error: {e}"


class CalculatorDivideTool(BaseTool):
    """LangChain tool for dividing two numbers using MCP calculator server."""
    
    name: str = "calculator_divide"
    description: str = "Divide a by b. Input should be two numbers 'a' and 'b'. Returns error if b is zero."
    mcp_session: Any = Field(exclude=True)
    
    class Config:
        arbitrary_types_allowed = True
    
    class InputSchema(BaseModel):
        a: float = Field(description="Numerator")
        b: float = Field(description="Denominator (cannot be zero)")
    
    args_schema: Type[BaseModel] = InputSchema
    
    def _run(self, a: float, b: float) -> str:
        """Synchronous wrapper."""
        return asyncio.run(self._arun(a, b))
    
    async def _arun(self, a: float, b: float) -> str:
        """Divide two numbers using MCP server."""
        try:
            result = await self.mcp_session.call_tool("divide", {"a": a, "b": b})
            if hasattr(result, 'content') and result.content:
                return result.content[0].text
            return str(result)
        except Exception as e:
            return f"Error: {e}"


async def create_mcp_tools_for_calculator(server_path: str) -> list[BaseTool]:
    """
    Create LangChain tools from the MCP calculator server.
    
    Args:
        server_path: Path to the MCP server Python file
        
    Returns:
        List of LangChain BaseTool instances
    """
    server_params = StdioServerParameters(
        command="python3",
        args=[server_path],
        env=None,
    )
    
    read, write = await stdio_client(server_params).__aenter__()
    session = await ClientSession(read, write).__aenter__()
    await session.initialize()
    
    tools = [
        CalculatorAddTool(mcp_session=session),
        CalculatorSubtractTool(mcp_session=session),
        CalculatorMultiplyTool(mcp_session=session),
        CalculatorDivideTool(mcp_session=session),
    ]
    
    return tools


async def create_generic_mcp_tools(server_path: str) -> list[BaseTool]:
    """
    Create generic LangChain tools from any MCP server.
    
    This creates a generic wrapper for each tool. For production use,
    consider creating typed wrappers like the calculator tools above.
    
    Args:
        server_path: Path to the MCP server Python file
        
    Returns:
        List of LangChain BaseTool instances
    """
    server_params = StdioServerParameters(
        command="python3",
        args=[server_path],
        env=None,
    )
    
    read, write = await stdio_client(server_params).__aenter__()
    session = await ClientSession(read, write).__aenter__()
    await session.initialize()
    
    tools_result = await session.list_tools()
    
    langchain_tools = []
    for mcp_tool in tools_result.tools:
        tool = MCPToolWrapper(
            name=mcp_tool.name,
            description=mcp_tool.description or f"MCP tool: {mcp_tool.name}",
            mcp_session=session,
            mcp_tool_name=mcp_tool.name,
        )
        langchain_tools.append(tool)
    
    return langchain_tools


def get_calculator_server_path() -> str:
    """Get the path to the calculator server."""
    repo_root = Path(__file__).parent.parent.parent
    return str(repo_root / "exercises" / "01-basic-tools" / "solution.py")
