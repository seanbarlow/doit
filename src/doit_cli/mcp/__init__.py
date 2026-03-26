"""MCP (Model Context Protocol) server for doit operations.

Exposes doit tools (validate, status, tasks, context, scaffold, verify)
as MCP tools accessible by AI assistants like Claude Code and GitHub Copilot.

Requires the 'mcp' optional dependency: pip install doit-toolkit-cli[mcp]
"""

try:
    from mcp.server.fastmcp import FastMCP  # noqa: F401

    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
