"""MCP tool for task listing and querying."""

from __future__ import annotations

import json
import logging
import subprocess
from pathlib import Path

from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)


def register_tasks_tool(mcp: FastMCP) -> None:
    """Register the doit_tasks tool with the MCP server."""

    @mcp.tool()
    def doit_tasks(
        feature_name: str | None = None,
        include_dependencies: bool = False,
    ) -> str:
        """List tasks from a feature's tasks.md with completion status.

        Args:
            feature_name: Feature name (e.g., "055-mcp-server").
                         Auto-detected from current git branch if omitted.
            include_dependencies: Include task dependency relationships.

        Returns:
            JSON with task list including IDs, status, priorities,
            and completion percentage.
        """
        from ...services.task_parser import TaskParser

        project_root = Path.cwd()

        # Auto-detect feature from git branch
        if not feature_name:
            try:
                result = subprocess.run(
                    ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    cwd=str(project_root),
                )
                if result.returncode == 0:
                    feature_name = result.stdout.strip()
            except subprocess.TimeoutExpired:
                logger.debug("Git branch detection timed out")
            except FileNotFoundError:
                logger.debug("Git not found on PATH")
            except OSError as e:
                logger.debug("Git branch detection failed: %s", e)

        if not feature_name:
            return json.dumps(
                {
                    "error": "Could not determine feature name",
                    "message": "Provide feature_name parameter or run from a feature branch.",
                },
                indent=2,
            )

        tasks_path = project_root / "specs" / feature_name / "tasks.md"
        if not tasks_path.exists():
            return json.dumps(
                {
                    "tasks": [],
                    "summary": {
                        "total": 0,
                        "completed": 0,
                        "pending": 0,
                        "completion_percentage": 0.0,
                    },
                    "message": f"No tasks.md found at {tasks_path}. Run `/doit.taskit` to generate tasks.",
                },
                indent=2,
            )

        parser = TaskParser(tasks_path=tasks_path)
        tasks = parser.parse()

        tasks_data = []
        completed = 0
        for task in tasks:
            is_complete = getattr(task, "completed", False)
            if is_complete:
                completed += 1
            task_entry = {
                "id": getattr(task, "id", ""),
                "description": getattr(task, "description", str(task)),
                "completed": is_complete,
                "priority": getattr(task, "priority", None),
                "requirement_refs": [
                    ref.id if hasattr(ref, "id") else str(ref)
                    for ref in getattr(task, "references", [])
                ],
            }
            if include_dependencies:
                task_entry["dependencies"] = getattr(task, "dependencies", [])
            tasks_data.append(task_entry)

        total = len(tasks_data)
        completion_pct = round(completed / total * 100, 1) if total > 0 else 0.0

        return json.dumps(
            {
                "tasks": tasks_data,
                "summary": {
                    "total": total,
                    "completed": completed,
                    "pending": total - completed,
                    "completion_percentage": completion_pct,
                },
            },
            indent=2,
        )
