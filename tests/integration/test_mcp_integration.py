"""Integration tests for the MCP server."""

import json

import pytest

from doit_cli.mcp import MCP_AVAILABLE


@pytest.mark.skipif(not MCP_AVAILABLE, reason="mcp package not installed")
class TestMCPServerIntegration:
    """Integration tests verifying full server setup and tool execution."""

    def test_all_tools_registered(self):
        """Verify all 6 tools are registered with the server."""
        from doit_cli.mcp.server import create_server

        server = create_server()
        tools = server._tool_manager._tools
        expected_tools = [
            "doit_validate",
            "doit_status",
            "doit_tasks",
            "doit_context",
            "doit_scaffold",
            "doit_verify",
        ]
        for tool_name in expected_tools:
            assert tool_name in tools, f"Tool {tool_name} not registered"

    def test_all_tools_return_valid_json(self, tmp_path, monkeypatch):
        """Verify all tools return valid JSON responses."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".doit" / "memory").mkdir(parents=True)
        (tmp_path / ".doit" / "templates").mkdir(parents=True)
        (tmp_path / ".doit" / "scripts").mkdir(parents=True)
        (tmp_path / ".doit" / "config").mkdir(parents=True)
        (tmp_path / ".doit" / "logs").mkdir(parents=True)
        (tmp_path / "specs").mkdir()
        (tmp_path / ".doit" / "memory" / "constitution.md").write_text("# Test")

        from doit_cli.mcp.server import create_server

        server = create_server()
        tools = server._tool_manager._tools

        # Test each tool returns valid JSON
        for tool_name in ["doit_validate", "doit_status", "doit_verify"]:
            result = tools[tool_name].fn()
            parsed = json.loads(result)
            assert isinstance(parsed, dict), f"{tool_name} did not return a dict"

        # doit_tasks needs a feature_name
        result = tools["doit_tasks"].fn(feature_name="nonexistent")
        parsed = json.loads(result)
        assert isinstance(parsed, dict)

        # doit_context
        result = tools["doit_context"].fn()
        parsed = json.loads(result)
        assert isinstance(parsed, dict)

    def test_validate_tool_contract_schema(self, tmp_path, monkeypatch):
        """Verify validate tool response matches contract schema."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".doit" / "memory").mkdir(parents=True)
        (tmp_path / "specs").mkdir()

        from doit_cli.mcp.server import create_server

        server = create_server()
        result = json.loads(server._tool_manager._tools["doit_validate"].fn())

        # Verify schema from contracts/mcp-tools.md
        assert "specs" in result
        assert "summary" in result
        assert "total" in result["summary"]
        assert "passed" in result["summary"]
        assert "failed" in result["summary"]
        assert "average_score" in result["summary"]

    def test_verify_tool_contract_schema(self, tmp_path, monkeypatch):
        """Verify verify tool response matches contract schema."""
        monkeypatch.chdir(tmp_path)

        from doit_cli.mcp.server import create_server

        server = create_server()
        result = json.loads(server._tool_manager._tools["doit_verify"].fn())

        assert "checks" in result
        assert "all_passed" in result
        assert "summary" in result
        assert isinstance(result["checks"], list)
        assert isinstance(result["all_passed"], bool)
