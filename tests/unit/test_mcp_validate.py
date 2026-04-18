"""Tests for the doit_validate MCP tool."""

import json

import pytest

from doit_cli.mcp import MCP_AVAILABLE


@pytest.mark.skipif(not MCP_AVAILABLE, reason="mcp package not installed")
class TestValidateTool:
    """Tests for the doit_validate tool."""

    def test_validate_all_with_no_specs(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".doit" / "memory").mkdir(parents=True)
        (tmp_path / "specs").mkdir()

        from mcp.server.fastmcp import FastMCP

        from doit_cli.mcp.tools.validate_tool import register_validate_tool

        mcp = FastMCP("test")
        register_validate_tool(mcp)

        # Get the registered tool function
        tools = mcp._tool_manager._tools
        validate_fn = tools["doit_validate"].fn

        result = json.loads(validate_fn())
        assert "specs" in result
        assert "summary" in result

    def test_validate_returns_structured_json(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".doit" / "memory").mkdir(parents=True)
        (tmp_path / "specs").mkdir()

        from mcp.server.fastmcp import FastMCP

        from doit_cli.mcp.tools.validate_tool import register_validate_tool

        mcp = FastMCP("test")
        register_validate_tool(mcp)

        tools = mcp._tool_manager._tools
        validate_fn = tools["doit_validate"].fn

        result = json.loads(validate_fn())
        assert isinstance(result["specs"], list)
        assert "total" in result["summary"]
        assert "passed" in result["summary"]
        assert "failed" in result["summary"]
