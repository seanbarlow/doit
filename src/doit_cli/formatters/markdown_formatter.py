"""Markdown formatter for status output."""

from ..models.status_models import SpecState, StatusReport
from .base import StatusFormatter


class MarkdownFormatter(StatusFormatter):
    """Formats status as markdown table for documentation.

    Produces GitHub-flavored markdown output suitable for embedding
    in documentation, README files, or issue descriptions.
    """

    def format(self, report: StatusReport, verbose: bool = False) -> str:
        """Format the status report as markdown.

        Args:
            report: The StatusReport to format.
            verbose: Include detailed validation errors.

        Returns:
            Markdown string representation.
        """
        lines = []

        # Header
        lines.append("# Spec Status Report")
        lines.append("")
        lines.append(f"**Generated**: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Project**: {report.project_root.name}")
        lines.append("")

        # Specifications table
        lines.append("## Specifications")
        lines.append("")

        if report.specs:
            lines.append("| Spec | Status | Validation | Last Modified |")
            lines.append("|------|--------|------------|---------------|")

            for spec in report.specs:
                status_display = f"{spec.status.emoji} {spec.status.display_name}"

                # Validation indicator
                if spec.error:
                    validation = "❌ Error"
                elif spec.validation_result is None:
                    validation = "—"
                elif spec.validation_passed:
                    validation = "✅ Pass"
                else:
                    validation = f"❌ Fail ({spec.validation_result.error_count})"

                if spec.is_blocking:
                    validation += " ⛔"

                modified = spec.last_modified.strftime("%Y-%m-%d")

                lines.append(f"| {spec.name} | {status_display} | {validation} | {modified} |")

            # Add verbose details
            if verbose:
                lines.append("")
                lines.append("### Validation Details")
                lines.append("")
                for spec in report.specs:
                    if spec.validation_result and spec.validation_result.issues:
                        lines.append(f"#### {spec.name}")
                        lines.append("")
                        for issue in spec.validation_result.issues:
                            severity = issue.severity.value.upper()
                            lines.append(f"- **{severity}** (line {issue.line_number}): {issue.message}")
                            if issue.suggestion:
                                lines.append(f"  - Suggestion: {issue.suggestion}")
                        lines.append("")
        else:
            lines.append("*No specifications found.*")
            lines.append("")

        # Summary
        lines.append("## Summary")
        lines.append("")
        lines.append(f"- **Total Specs**: {report.total_count}")
        lines.append(f"- **Draft**: {report.by_status.get(SpecState.DRAFT, 0)}")
        lines.append(f"- **In Progress**: {report.by_status.get(SpecState.IN_PROGRESS, 0)}")
        lines.append(f"- **Complete**: {report.by_status.get(SpecState.COMPLETE, 0)}")
        lines.append(f"- **Approved**: {report.by_status.get(SpecState.APPROVED, 0)}")
        lines.append(f"- **Completion**: {report.completion_percentage:.0f}%")

        if report.is_ready_to_commit:
            lines.append("- **Status**: ✅ Ready to commit")
        else:
            lines.append(f"- **Status**: ⛔ {report.blocking_count} spec(s) blocking")

        lines.append("")

        return "\n".join(lines)
