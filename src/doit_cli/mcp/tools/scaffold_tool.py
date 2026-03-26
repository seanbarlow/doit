"""MCP tool for project scaffolding."""

import json
import logging
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)


def register_scaffold_tool(mcp: FastMCP) -> None:
    """Register the doit_scaffold tool with the MCP server."""

    @mcp.tool()
    def doit_scaffold(tech_stack: Optional[str] = None) -> str:
        """Create doit project directory structure.

        Args:
            tech_stack: Tech stack override (e.g., "python-fastapi").
                       Uses constitution tech stack if omitted.

        Returns:
            JSON with created directories, files, and summary.
        """
        from ...models.project import Project
        from ...services.scaffolder import Scaffolder

        project_root = Path.cwd()

        try:
            project = Project(path=project_root)
            scaffolder = Scaffolder(project=project)
            scaffolder.create_doit_structure()

            return json.dumps({
                "created_dirs": [str(d) for d in scaffolder.created_directories],
                "created_files": [str(f) for f in scaffolder.created_files],
                "skipped": [],
                "summary": f"Created {len(scaffolder.created_directories)} directories and {len(scaffolder.created_files)} files.",
            }, indent=2)
        except PermissionError as e:
            logger.error("Permission denied during scaffold: %s", e)
            return json.dumps({
                "error": str(e),
                "message": "Permission denied. Check directory permissions.",
            }, indent=2)
        except Exception as e:
            logger.error("Scaffold failed: %s", e)
            return json.dumps({
                "error": str(e),
                "message": "Failed to scaffold project structure.",
            }, indent=2)
