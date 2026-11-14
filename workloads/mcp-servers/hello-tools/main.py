"""AgentCore MCP server: expose independent tools using streamable HTTP."""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("hello-tools", stateless_http=True, host="0.0.0.0", port=8000)


@mcp.tool()
def greet(name: str = "world") -> str:
    """Return a greeting without invoking an LLM."""
    return f"Hello, {name}!"


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
