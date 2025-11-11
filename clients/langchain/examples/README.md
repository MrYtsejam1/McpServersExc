# LangChain MCP Integration Examples

This directory contains examples of integrating MCP servers with LangChain in airgapped environments.

## Overview

These examples demonstrate how to use MCP servers with LangChain without requiring Claude for Desktop or any SaaS-based LLM services. Perfect for airgapped environments.

## Examples

### 1. Manual Tool Invocation (No LLM)

**File:** `agent_no_llm.py`

Demonstrates programmatic access to MCP tools through LangChain without any LLM. Perfect for:
- Rule-based automation
- Testing and validation
- Integration with existing Python applications
- Environments where no LLM is available

**Usage:**
```bash
python3 agent_no_llm.py
```

**What it demonstrates:**
- Loading MCP tools as LangChain tools
- Manual tool invocation
- Chaining multiple tool calls
- Error handling
- Batch processing

### 2. Local LLM Integration

**File:** `agent_local_llm.py`

Demonstrates using MCP tools with a local LLM through LangChain. Supports:
- Custom API endpoints (e.g., qwen3-coder-480b)
- Ollama
- llama.cpp

**Usage with qwen3-coder-480b:**
```bash
python3 agent_local_llm.py \
  --model custom \
  --api-url http://your-inference-server:8000/v1 \
  --model-name qwen3-coder-480b
```

**Usage with Ollama:**
```bash
python3 agent_local_llm.py \
  --model ollama \
  --model-name llama2
```

**Usage with llama.cpp:**
```bash
python3 agent_local_llm.py \
  --model llamacpp \
  --model-path /path/to/model.gguf
```

## Installation

### Core Dependencies

```bash
pip install langchain langchain-core mcp
```

### Optional Dependencies

For custom API endpoints (OpenAI-compatible):
```bash
pip install langchain-openai
```

For Ollama:
```bash
pip install langchain-community
```

For llama.cpp:
```bash
pip install langchain-community llama-cpp-python
```

### Airgapped Installation

See `docs/airgapped.md` for instructions on installing dependencies in an airgapped environment.

## Using with qwen3-coder-480b

If you have qwen3-coder-480b running on your inference infrastructure, you can use it with the `agent_local_llm.py` example:

1. **Ensure your inference server is running** and accessible from your airgapped environment

2. **Verify the API endpoint** is OpenAI-compatible (most modern inference servers support this)

3. **Run the example:**
   ```bash
   python3 agent_local_llm.py \
     --model custom \
     --api-url http://your-inference-server:8000/v1 \
     --model-name qwen3-coder-480b
   ```

4. **Optional: Add API key** if your server requires authentication:
   ```bash
   python3 agent_local_llm.py \
     --model custom \
     --api-url http://your-inference-server:8000/v1 \
     --model-name qwen3-coder-480b \
     --api-key your-api-key
   ```

## Architecture

The integration works as follows:

```
┌─────────────────┐
│   LangChain     │
│     Agent       │
└────────┬────────┘
         │
         │ Uses tools
         ▼
┌─────────────────┐
│  LangChain Tool │
│    Wrappers     │
└────────┬────────┘
         │
         │ Calls via MCP protocol
         ▼
┌─────────────────┐
│   MCP Server    │
│  (STDIO-based)  │
└─────────────────┘
```

## Customization

### Adding More MCP Servers

To use other MCP servers (weather, tasks, etc.), modify the tool creation functions in `mcp_langchain_tools.py`:

```python
async def create_weather_tools(server_path: str) -> list[BaseTool]:
    """Create LangChain tools from the weather MCP server."""
    # Similar to create_mcp_tools_for_calculator
    # but for the weather server
    pass
```

### Creating Typed Tool Wrappers

For better type safety and IDE support, create typed wrappers like the calculator tools:

```python
class WeatherAlertsTool(BaseTool):
    name: str = "weather_alerts"
    description: str = "Get weather alerts for a US state"
    mcp_session: Any = Field(exclude=True)
    
    class InputSchema(BaseModel):
        state: str = Field(description="Two-letter US state code")
    
    args_schema: Type[BaseModel] = InputSchema
    
    async def _arun(self, state: str) -> str:
        result = await self.mcp_session.call_tool("get_alerts", {"state": state})
        # Process result...
```

## Troubleshooting

### Import Errors

If you see `ModuleNotFoundError`, ensure all required packages are installed:
```bash
pip list | grep -E "langchain|mcp"
```

### Connection Errors

If the MCP server fails to start:
1. Verify the server path is correct
2. Check that Python 3.10+ is available
3. Ensure all MCP server dependencies are installed

### LLM Errors

If the local LLM fails:
1. Verify the API endpoint is accessible
2. Check that the model name is correct
3. Ensure the API is OpenAI-compatible
4. Try the `agent_no_llm.py` example first to verify MCP integration works

### Tool Calling Not Supported

Some models don't support tool calling. The code will automatically fall back to ReAct agent mode, which works with any LLM that can follow instructions.

## Best Practices

1. **Test without LLM first:** Use `agent_no_llm.py` to verify MCP integration works before adding LLM complexity

2. **Use typed wrappers:** Create typed tool wrappers for better error messages and IDE support

3. **Handle errors gracefully:** MCP tools can fail; always handle exceptions

4. **Manage connections:** In production, properly manage MCP server lifecycle (start/stop)

5. **Monitor performance:** Local LLMs can be slow; consider caching or batching

## Additional Resources

- Main documentation: `../../README.md`
- Airgapped usage: `../../docs/airgapped.md`
- MCP specification: https://modelcontextprotocol.io
- LangChain documentation: https://python.langchain.com
