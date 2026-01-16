"""JSON formatter for status output."""

import json
from datetime import datetime
from typing import Any

from ..models.status_models import SpecState, StatusReport
from .base import StatusFormatter


class JsonFormatter(StatusFormatter):
    """Formats status as JSON for machine consumption.

    Produces structured JSON output suitable for parsing by other tools,
    CI/CD systems, or programmatic analysis.
    """

    def format(self, report: StatusReport, verbose: bool = False) -> str:
        """Format the status report as JSON.

        Args:
            report: The StatusReport to format.
            verbose: Include detailed validation errors.

        Returns:
            JSON string representation.
        """
        data = self._build_json_data(report, verbose)
        return json.dumps(data, indent=2, default=self._json_serializer)

    def _build_json_data(self, report: StatusReport, verbose: bool) -> dict[str, Any]:
        """Build the JSON data structure.

        Args:
            report: The StatusReport to convert.
            verbose: Include detailed validation errors.

        Returns:
            Dictionary ready for JSON serialization.
        """
        # Build summary
        summary = {
            "total": report.total_count,
            "by_status": {
                "draft": report.by_status.get(SpecState.DRAFT, 0),
                "in_progress": report.by_status.get(SpecState.IN_PROGRESS, 0),
                "complete": report.by_status.get(SpecState.COMPLETE, 0),
                "approved": report.by_status.get(SpecState.APPROVED, 0),
            },
            "blocking": report.blocking_count,
            "validation_pass": sum(
                1 for s in report.specs if s.validation_passed
            ),
            "validation_fail": sum(
                1 for s in report.specs
                if s.validation_result is not None and not s.validation_passed
            ),
            "completion_percentage": round(report.completion_percentage, 2),
            "ready_to_commit": report.is_ready_to_commit,
        }

        # Build specs list
        specs = []
        for spec in report.specs:
            spec_data = {
                "name": spec.name,
                "path": str(spec.path),
                "status": spec.status.value,
                "last_modified": spec.last_modified.isoformat(),
                "is_blocking": spec.is_blocking,
                "error": spec.error,
            }

            # Add validation info
            if spec.validation_result is not None:
                validation_data = {
                    "passed": spec.validation_passed,
                    "score": spec.validation_score,
                    "error_count": spec.validation_result.error_count,
                    "warning_count": spec.validation_result.warning_count,
                }

                if verbose and spec.validation_result.issues:
                    validation_data["issues"] = [
                        {
                            "rule_id": issue.rule_id,
                            "severity": issue.severity.value,
                            "line": issue.line_number,
                            "message": issue.message,
                            "suggestion": issue.suggestion,
                        }
                        for issue in spec.validation_result.issues
                    ]
                else:
                    validation_data["issues"] = []

                spec_data["validation"] = validation_data
            else:
                spec_data["validation"] = None

            specs.append(spec_data)

        return {
            "generated_at": report.generated_at.isoformat(),
            "project_root": str(report.project_root),
            "summary": summary,
            "specs": specs,
        }

    def _json_serializer(self, obj: Any) -> Any:
        """Custom JSON serializer for non-standard types.

        Args:
            obj: Object to serialize.

        Returns:
            JSON-serializable representation.

        Raises:
            TypeError: If object cannot be serialized.
        """
        if isinstance(obj, datetime):
            return obj.isoformat()
        if hasattr(obj, "__dict__"):
            return obj.__dict__
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
