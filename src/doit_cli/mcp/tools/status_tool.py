"""MCP tool for project status reporting."""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)


def register_status_tool(mcp: FastMCP) -> None:
    """Register the doit_status tool with the MCP server."""

    @mcp.tool()
    def doit_status(
        include_roadmap: bool = False,
        status_filter: str | None = None,
        blocking_only: bool = False,
    ) -> str:
        """Get project status including spec states and roadmap.

        Args:
            include_roadmap: Include active roadmap items in response.
            status_filter: Filter by status: draft, in_progress, complete, approved.
            blocking_only: Show only specs blocking commits.

        Returns:
            JSON with spec statuses, summary counts, and optional roadmap data.
        """
        from ...services.status_reporter import StatusReporter

        project_root = Path.cwd()

        try:
            reporter = StatusReporter(project_root=project_root, validate=True)
        except Exception as e:
            logger.warning("Failed to initialize status reporter: %s", e)
            return json.dumps(
                {
                    "error": str(e),
                    "message": "Failed to initialize status reporter. Is this a doit project? Run `doit init` first.",
                },
                indent=2,
            )

        # Map string filter to SpecState enum
        filter_state = None
        if status_filter:
            from ...models.status_models import SpecState

            state_map = {
                "draft": SpecState.DRAFT,
                "in_progress": SpecState.IN_PROGRESS,
                "complete": SpecState.COMPLETE,
                "approved": SpecState.APPROVED,
            }
            filter_state = state_map.get(status_filter.lower())

        report = reporter.generate_report(
            status_filter=filter_state,
            blocking_only=blocking_only,
        )

        specs_data: list[dict[str, object]] = []
        by_status: dict[str, int] = {}
        for spec in report.specs:
            status_val = spec.status.value if hasattr(spec.status, "value") else str(spec.status)
            specs_data.append(
                {
                    "name": spec.name,
                    "status": status_val,
                    "last_modified": spec.last_modified.isoformat() if spec.last_modified else None,
                    "is_blocking": spec.is_blocking,
                    "validation_score": getattr(spec.validation_result, "score", None)
                    if spec.validation_result
                    else None,
                }
            )
            by_status[status_val] = by_status.get(status_val, 0) + 1

        result = {
            "specs": specs_data,
            "summary": {
                "total": len(report.specs),
                "by_status": by_status,
                "blocking_count": report.blocking_count,
            },
        }

        if include_roadmap:
            try:
                from ...services.context_loader import ContextLoader

                loader = ContextLoader(project_root=project_root)
                roadmap_source = loader.load_roadmap()
                if roadmap_source and roadmap_source.content:
                    # Parse roadmap items from content using regex
                    items = []
                    current_priority = None
                    for line in roadmap_source.content.split("\n"):
                        priority_match = re.match(r"^###\s+(P[1-4])\s+-\s+", line)
                        if priority_match:
                            current_priority = priority_match.group(1)
                            continue
                        if current_priority and re.match(r"^- \[[ xX]\] ", line):
                            checked = line[3].lower() == "x"
                            title = line[6:].strip().replace("**", "")
                            items.append(
                                {
                                    "title": title,
                                    "priority": current_priority,
                                    "status": "completed" if checked else "pending",
                                }
                            )
                        if line.startswith("## Deferred") or line.startswith("## Recent"):
                            break
                    result["roadmap"] = items
                else:
                    result["roadmap"] = []
            except Exception as e:
                logger.warning("Failed to load roadmap: %s", e)
                result["roadmap"] = []
                result["roadmap_warning"] = str(e)

        return json.dumps(result, indent=2)
