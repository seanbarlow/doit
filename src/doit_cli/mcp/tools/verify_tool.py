"""MCP tool for project structure verification."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)


def register_verify_tool(mcp: FastMCP) -> None:
    """Register the doit_verify tool with the MCP server."""

    @mcp.tool()
    def doit_verify() -> str:
        """Verify doit project structure completeness.

        Returns:
            JSON with check results indicating which project
            components are present and properly configured.
        """
        from ...models.agent import Agent
        from ...models.project import Project
        from ...services.validator import Validator, VerifyStatus

        project_root = Path.cwd()

        try:
            project = Project(path=project_root)
            validator = Validator(project=project)
        except Exception as e:
            logger.warning("Failed to initialize validator: %s", e)
            return json.dumps(
                {
                    "checks": [],
                    "all_passed": False,
                    "summary": f"Failed to initialize validator: {e}",
                },
                indent=2,
            )

        checks = []

        # Check .doit/ folder
        doit_check = validator.check_doit_folder()
        checks.append(
            {
                "name": doit_check.name,
                "passed": doit_check.status == VerifyStatus.PASS,
                "message": doit_check.message,
            }
        )

        # Check agent directories
        for agent in [Agent.CLAUDE, Agent.COPILOT]:
            agent_check = validator.check_agent_directory(agent)
            checks.append(
                {
                    "name": agent_check.name,
                    "passed": agent_check.status == VerifyStatus.PASS,
                    "message": agent_check.message,
                }
            )

            cmd_check = validator.check_command_files(agent)
            checks.append(
                {
                    "name": cmd_check.name,
                    "passed": cmd_check.status == VerifyStatus.PASS,
                    "message": cmd_check.message,
                }
            )

        all_passed = all(c["passed"] for c in checks)
        passed_count = sum(1 for c in checks if c["passed"])

        return json.dumps(
            {
                "checks": checks,
                "all_passed": all_passed,
                "summary": f"{passed_count}/{len(checks)} checks passed.",
            },
            indent=2,
        )
