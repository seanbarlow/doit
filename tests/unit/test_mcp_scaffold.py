"""Tests for the doit_scaffold and doit_verify MCP tools."""

import json
import pytest
from pathlib import Path

from doit_cli.mcp import MCP_AVAILABLE


@pytest.mark.skipif(not MCP_AVAILABLE, reason="mcp package not installed")
class TestScaffoldTool:
    """Tests for the doit_scaffold tool."""

    def test_scaffold_returns_json(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        from doit_cli.mcp.tools.scaffold_tool import register_scaffold_tool
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register_scaffold_tool(mcp)

        tools = mcp._tool_manager._tools
        scaffold_fn = tools["doit_scaffold"].fn

        result = json.loads(scaffold_fn())
        assert "summary" in result
        # Should have either created dirs or an error
        assert "created_dirs" in result or "error" in result


@pytest.mark.skipif(not MCP_AVAILABLE, reason="mcp package not installed")
class TestVerifyTool:
    """Tests for the doit_verify tool."""

    def test_verify_no_doit_folder(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        from doit_cli.mcp.tools.verify_tool import register_verify_tool
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register_verify_tool(mcp)

        tools = mcp._tool_manager._tools
        verify_fn = tools["doit_verify"].fn

        result = json.loads(verify_fn())
        assert "checks" in result
        assert "all_passed" in result

    def test_verify_with_doit_structure(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        # Create minimal doit structure
        (tmp_path / ".doit" / "memory").mkdir(parents=True)
        (tmp_path / ".doit" / "templates").mkdir(parents=True)
        (tmp_path / ".doit" / "scripts").mkdir(parents=True)
        (tmp_path / ".doit" / "config").mkdir(parents=True)
        (tmp_path / ".doit" / "logs").mkdir(parents=True)

        from doit_cli.mcp.tools.verify_tool import register_verify_tool
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register_verify_tool(mcp)

        tools = mcp._tool_manager._tools
        verify_fn = tools["doit_verify"].fn

        result = json.loads(verify_fn())
        assert "checks" in result
        assert isinstance(result["checks"], list)
        assert "summary" in result
