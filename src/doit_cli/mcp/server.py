"""MCP server for doit operations.

Registers all doit tools and resources with FastMCP for AI assistant access.
"""

from __future__ import annotations

import importlib.metadata
import logging
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from .tools.context_tool import register_context_tool
from .tools.scaffold_tool import register_scaffold_tool
from .tools.status_tool import register_status_tool
from .tools.tasks_tool import register_tasks_tool
from .tools.validate_tool import register_validate_tool
from .tools.verify_tool import register_verify_tool

logger = logging.getLogger(__name__)


def _get_version() -> str:
    """Get the doit-toolkit-cli package version."""
    try:
        return importlib.metadata.version("doit-toolkit-cli")
    except importlib.metadata.PackageNotFoundError:
        return "0.0.0-dev"


def create_server() -> FastMCP:
    """Create and configure the doit MCP server.

    Returns:
        Configured FastMCP server with all tools and resources registered.
    """
    mcp = FastMCP("doit")

    # Register all tools
    register_validate_tool(mcp)
    register_status_tool(mcp)
    register_tasks_tool(mcp)
    register_context_tool(mcp)
    register_scaffold_tool(mcp)
    register_verify_tool(mcp)

    # Register project memory as resources
    _register_resources(mcp)

    return mcp


def _register_resources(mcp: FastMCP) -> None:
    """Register project memory files as MCP resources."""

    @mcp.resource("doit://memory/constitution")
    def get_constitution() -> str:
        """Project constitution - principles, tech stack, and governance."""
        path = Path.cwd() / ".doit" / "memory" / "constitution.md"
        if not path.exists():
            raise FileNotFoundError(
                f"Constitution not found at {path}. Run `doit init` to create one."
            )
        return path.read_text(encoding="utf-8")

    @mcp.resource("doit://memory/roadmap")
    def get_roadmap() -> str:
        """Project roadmap - prioritized features and requirements."""
        path = Path.cwd() / ".doit" / "memory" / "roadmap.md"
        if not path.exists():
            raise FileNotFoundError(
                f"Roadmap not found at {path}. Run `/doit.roadmapit` to create one."
            )
        return path.read_text(encoding="utf-8")

    @mcp.resource("doit://memory/tech-stack")
    def get_tech_stack() -> str:
        """Tech stack decisions - languages, frameworks, and infrastructure."""
        path = Path.cwd() / ".doit" / "memory" / "tech-stack.md"
        if not path.exists():
            raise FileNotFoundError(
                f"Tech stack not found at {path}. Run `/doit.constitution` to create one."
            )
        return path.read_text(encoding="utf-8")
