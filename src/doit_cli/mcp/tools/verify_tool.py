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

    @mcp.tool()
    def doit_verify_memory(project_root: str | None = None) -> str:
        """Validate a project's ``.doit/memory/*.md`` against the memory contract.

        Surfaces the same errors and warnings that ``doit verify-memory`` does:
        frontmatter shape (id, name, kind, phase, icon, tagline, dependencies),
        required headings in ``constitution.md`` and ``roadmap.md``, and the
        column order + priority values of the ``## Open Questions`` table.

        Args:
            project_root: Project directory to validate. Defaults to the
                process cwd so the caller can simply invoke the tool from
                inside a project.

        Returns:
            JSON with keys ``issues`` (list of
            ``{file, severity, message, line, field}``),
            ``placeholder_files``, ``error_count``, ``warning_count``,
            and ``all_passed``.
        """
        from ...services.memory_validator import validate_project

        root = Path(project_root) if project_root else Path.cwd()

        try:
            report = validate_project(root)
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("memory validator crashed: %s", exc)
            return json.dumps(
                {
                    "issues": [],
                    "placeholder_files": [],
                    "error_count": 0,
                    "warning_count": 0,
                    "all_passed": False,
                    "error": f"memory validator crashed: {exc}",
                },
                indent=2,
            )

        payload = report.to_dict()
        payload["all_passed"] = not report.has_errors()
        payload["project_root"] = str(root)
        return json.dumps(payload, indent=2)
