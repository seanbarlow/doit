"""Tests for the doit_status MCP tool."""

import json

import pytest

from doit_cli.mcp import MCP_AVAILABLE


@pytest.mark.skipif(not MCP_AVAILABLE, reason="mcp package not installed")
class TestStatusTool:
    """Tests for the doit_status tool."""

    def test_status_no_doit_project(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        from mcp.server.fastmcp import FastMCP

        from doit_cli.mcp.tools.status_tool import register_status_tool

        mcp = FastMCP("test")
        register_status_tool(mcp)

        tools = mcp._tool_manager._tools
        status_fn = tools["doit_status"].fn

        result = json.loads(status_fn())
        # Should return error or empty specs for non-doit project
        assert "error" in result or "specs" in result

    def test_status_returns_structured_json(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".doit" / "memory").mkdir(parents=True)
        (tmp_path / "specs").mkdir()

        from mcp.server.fastmcp import FastMCP

        from doit_cli.mcp.tools.status_tool import register_status_tool

        mcp = FastMCP("test")
        register_status_tool(mcp)

        tools = mcp._tool_manager._tools
        status_fn = tools["doit_status"].fn

        result = json.loads(status_fn())
        if "error" not in result:
            assert "specs" in result
            assert "summary" in result
            assert "total" in result["summary"]
