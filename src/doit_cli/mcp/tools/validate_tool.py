"""MCP tool for spec validation."""

import json
import logging
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)


def register_validate_tool(mcp: FastMCP) -> None:
    """Register the doit_validate tool with the MCP server."""

    @mcp.tool()
    def doit_validate(spec_path: Optional[str] = None) -> str:
        """Validate specification files against quality rules.

        Args:
            spec_path: Path to a specific spec file to validate.
                      If omitted, validates all specs in the project.

        Returns:
            JSON with validation results including severity, line numbers,
            and recommendations for each spec.
        """
        from ...services.validation_service import ValidationService

        project_root = Path.cwd()
        service = ValidationService(project_root=project_root)

        try:
            if spec_path:
                path = Path(spec_path)
                if not path.is_absolute():
                    path = project_root / path
                results = [service.validate_file(path)]
            else:
                results = service.validate_all()
        except Exception as e:
            logger.error("Validation failed: %s", e)
            return json.dumps({
                "specs": [],
                "summary": {"total": 0, "passed": 0, "warned": 0, "failed": 0, "average_score": 0},
                "error": str(e),
            }, indent=2)

        summary = service.get_summary(results)

        specs_data = []
        for result in results:
            issues = []
            for issue in getattr(result, "issues", []):
                issues.append({
                    "severity": getattr(issue, "severity", "info"),
                    "line": getattr(issue, "line_number", 0),
                    "message": getattr(issue, "message", str(issue)),
                    "recommendation": getattr(issue, "recommendation", ""),
                })
            specs_data.append({
                "name": getattr(result, "spec_name", str(getattr(result, "path", "unknown"))),
                "path": str(getattr(result, "path", "")),
                "passed": getattr(result, "passed", len(issues) == 0),
                "score": getattr(result, "score", 0),
                "issues": issues,
            })

        return json.dumps({
            "specs": specs_data,
            "summary": {
                "total": summary.get("total_specs", len(results)),
                "passed": summary.get("passed", 0),
                "warned": summary.get("warned", 0),
                "failed": summary.get("failed", 0),
                "average_score": summary.get("average_score", 0),
            },
        }, indent=2)
