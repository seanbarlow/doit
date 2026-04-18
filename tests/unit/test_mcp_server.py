"""Tests for MCP server setup and tool registration."""

import pytest

from doit_cli.mcp import MCP_AVAILABLE
from doit_cli.mcp.server import _get_version, create_server


@pytest.mark.skipif(not MCP_AVAILABLE, reason="mcp package not installed")
class TestMCPServer:
    """Tests for MCP server creation and configuration."""

    def test_create_server_returns_fastmcp_instance(self):
        server = create_server()
        assert server is not None
        assert server.name == "doit"

    def test_server_has_name(self):
        server = create_server()
        assert server.name == "doit"

    def test_get_version_returns_string(self):
        version = _get_version()
        assert isinstance(version, str)
        assert len(version) > 0


@pytest.mark.skipif(not MCP_AVAILABLE, reason="mcp package not installed")
class TestMCPResources:
    """Tests for MCP resource registration."""

    def test_server_creates_without_error(self):
        server = create_server()
        assert server is not None
