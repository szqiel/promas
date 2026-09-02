# Promas Integration Examples

This folder contains copy-pasteable configuration files, scripts, and guides to integrate Promas across different AI agents, IDEs, and LLM frameworks:

| Target Platform / Framework | Directory | Description |
| :--- | :--- | :--- |
| **Claude Desktop** | [`examples/claude_desktop/`](claude_desktop/) | Config file & guide for Claude Desktop on macOS / Windows / Linux. |
| **Cursor IDE** | [`examples/cursor/`](cursor/) | `mcp.json` config and prompt examples for Cursor Composer & Agent. |
| **LangChain** | [`examples/langchain_agent/`](langchain_agent/) | Structured `@tool` wrapper and ReAct agent example. |
| **OpenAI API** | [`examples/openai_agent/`](openai_agent/) | Native OpenAI Function / Tool Calling implementation script. |

---

## Running Promas MCP Server Directly

You can start the FastMCP server with:

```bash
# Via CLI command (after pip install promas or pip install -e .)
promas-mcp

# Or via Python module
python -m promas.server.mcp_server

# Or via Docker
docker run -i --rm promas
```
