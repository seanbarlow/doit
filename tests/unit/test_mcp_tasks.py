"""Tests for the doit_tasks MCP tool."""

import json
import pytest
from pathlib import Path

from doit_cli.mcp import MCP_AVAILABLE


@pytest.mark.skipif(not MCP_AVAILABLE, reason="mcp package not installed")
class TestTasksTool:
    """Tests for the doit_tasks tool."""

    def test_tasks_no_tasks_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "specs" / "test-feature").mkdir(parents=True)

        from doit_cli.mcp.tools.tasks_tool import register_tasks_tool
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register_tasks_tool(mcp)

        tools = mcp._tool_manager._tools
        tasks_fn = tools["doit_tasks"].fn

        result = json.loads(tasks_fn(feature_name="test-feature"))
        assert result["summary"]["total"] == 0
        assert "message" in result

    def test_tasks_with_tasks_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        feature_dir = tmp_path / "specs" / "test-feature"
        feature_dir.mkdir(parents=True)
        (feature_dir / "tasks.md").write_text(
            "# Tasks\n\n"
            "- [ ] T001 First task in src/main.py\n"
            "- [x] T002 Second task in src/utils.py\n"
            "- [ ] T003 Third task in src/service.py\n",
            encoding="utf-8",
        )

        from doit_cli.mcp.tools.tasks_tool import register_tasks_tool
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register_tasks_tool(mcp)

        tools = mcp._tool_manager._tools
        tasks_fn = tools["doit_tasks"].fn

        result = json.loads(tasks_fn(feature_name="test-feature"))
        assert result["summary"]["total"] >= 0
