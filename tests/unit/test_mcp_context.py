"""Tests for the doit_context MCP tool."""

import json

import pytest

from doit_cli.mcp import MCP_AVAILABLE


@pytest.mark.skipif(not MCP_AVAILABLE, reason="mcp package not installed")
class TestContextTool:
    """Tests for the doit_context tool."""

    def test_context_no_doit_project(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        from mcp.server.fastmcp import FastMCP

        from doit_cli.mcp.tools.context_tool import register_context_tool

        mcp = FastMCP("test")
        register_context_tool(mcp)

        tools = mcp._tool_manager._tools
        context_fn = tools["doit_context"].fn

        result = json.loads(context_fn())
        assert "error" in result or "sources" in result

    def test_context_with_memory_files(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        memory_dir = tmp_path / ".doit" / "memory"
        memory_dir.mkdir(parents=True)
        (memory_dir / "constitution.md").write_text("# Constitution\nTest principles")
        (memory_dir / "tech-stack.md").write_text("# Tech Stack\nPython 3.11+")
        (tmp_path / ".doit" / "config").mkdir(parents=True)

        from mcp.server.fastmcp import FastMCP

        from doit_cli.mcp.tools.context_tool import register_context_tool

        mcp = FastMCP("test")
        register_context_tool(mcp)

        tools = mcp._tool_manager._tools
        context_fn = tools["doit_context"].fn

        result = json.loads(context_fn())
        if "error" not in result:
            assert "sources" in result
            assert "summary" in result
            assert result["summary"]["total_sources"] > 0
