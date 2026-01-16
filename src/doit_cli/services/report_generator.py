"""Report generator for validation results."""

import json
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

from ..models.validation_models import Severity, ValidationResult, ValidationStatus


class ReportGenerator:
    """Generates validation reports in human-readable and JSON formats."""

    def __init__(self, console: Optional[Console] = None) -> None:
        """Initialize report generator.

        Args:
            console: Rich console for output. Creates new one if None.
        """
        self.console = console or Console()

    def display_result(self, result: ValidationResult) -> None:
        """Display a single validation result with rich formatting.

        Args:
            result: The validation result to display.
        """
        spec_name = Path(result.spec_path).parent.name
        self.console.print()
        self.console.print(f"[bold]Validating:[/bold] {result.spec_path}")
        self.console.print()

        if not result.issues:
            self.console.print("[green]No issues found[/green]")
        else:
            # Group issues by severity
            errors = [i for i in result.issues if i.severity == Severity.ERROR]
            warnings = [i for i in result.issues if i.severity == Severity.WARNING]
            infos = [i for i in result.issues if i.severity == Severity.INFO]

            # Display errors
            if errors:
                self._display_issue_group("ERRORS", errors, "red")

            # Display warnings
            if warnings:
                self._display_issue_group("WARNINGS", warnings, "yellow")

            # Display info
            if infos:
                self._display_issue_group("INFO", infos, "blue")

        # Display summary line
        self.console.print()
        self.console.print("━" * 50)
        self._display_summary_line(result)

    def _display_issue_group(
        self,
        title: str,
        issues: list,
        color: str,
    ) -> None:
        """Display a group of issues with tree formatting.

        Args:
            title: Group title (e.g., "ERRORS").
            issues: List of issues to display.
            color: Color for the group.
        """
        tree = Tree(f"[{color}]{title} ({len(issues)})[/{color}]")

        for i, issue in enumerate(issues):
            is_last = i == len(issues) - 1
            prefix = "└─" if is_last else "├─"

            line_info = f"Line {issue.line_number}: " if issue.line_number > 0 else ""
            tree.add(f"[{color}]{line_info}{issue.message}[/{color}]")

            if issue.suggestion:
                # Add suggestion as child
                tree.add(f"   [dim]Suggestion: {issue.suggestion}[/dim]")

        self.console.print(tree)

    def _display_summary_line(self, result: ValidationResult) -> None:
        """Display the summary line with score and status.

        Args:
            result: The validation result.
        """
        # Determine status color
        status_colors = {
            ValidationStatus.PASS: "green",
            ValidationStatus.WARN: "yellow",
            ValidationStatus.FAIL: "red",
        }
        color = status_colors.get(result.status, "white")

        # Build status text
        parts = []
        if result.error_count > 0:
            parts.append(f"{result.error_count} error{'s' if result.error_count != 1 else ''}")
        if result.warning_count > 0:
            parts.append(f"{result.warning_count} warning{'s' if result.warning_count != 1 else ''}")
        if result.info_count > 0:
            parts.append(f"{result.info_count} info")

        status_detail = ", ".join(parts) if parts else "no issues"

        self.console.print(
            f"[bold]Quality Score:[/bold] {result.quality_score}/100"
        )
        self.console.print(
            f"[bold]Status:[/bold] [{color}]{result.status.value.upper()}[/{color}] ({status_detail})"
        )

    def display_summary(
        self,
        results: list[ValidationResult],
        summary: dict,
    ) -> None:
        """Display summary table for multiple validation results.

        Args:
            results: List of validation results.
            summary: Summary statistics from ValidationService.get_summary().
        """
        self.console.print()
        self.console.print("[bold]Spec Validation Summary[/bold]")
        self.console.print()

        if not results:
            self.console.print("[yellow]No spec files found to validate[/yellow]")
            return

        # Create table
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Spec", style="dim")
        table.add_column("Score", justify="center")
        table.add_column("Status", justify="center")
        table.add_column("Errors", justify="center")
        table.add_column("Warnings", justify="center")

        for result in results:
            # Get spec name from path
            spec_name = Path(result.spec_path).parent.name

            # Determine status color
            status_colors = {
                ValidationStatus.PASS: "green",
                ValidationStatus.WARN: "yellow",
                ValidationStatus.FAIL: "red",
            }
            color = status_colors.get(result.status, "white")

            table.add_row(
                spec_name,
                str(result.quality_score),
                f"[{color}]{result.status.value.upper()}[/{color}]",
                str(result.error_count),
                str(result.warning_count),
            )

        self.console.print(table)

        # Display summary line
        self.console.print()
        self.console.print("━" * 50)
        self.console.print(
            f"[bold]Total:[/bold] {summary['total_specs']} specs | "
            f"[green]Passed: {summary['passed']}[/green] | "
            f"[yellow]Warned: {summary['warned']}[/yellow] | "
            f"[red]Failed: {summary['failed']}[/red] | "
            f"Avg Score: {summary['average_score']}"
        )

    def to_json(self, result: ValidationResult) -> str:
        """Convert single validation result to JSON string.

        Args:
            result: The validation result.

        Returns:
            JSON string representation.
        """
        output = {
            "spec_path": result.spec_path,
            "status": result.status.value,
            "quality_score": result.quality_score,
            "error_count": result.error_count,
            "warning_count": result.warning_count,
            "info_count": result.info_count,
            "issues": [
                {
                    "rule_id": issue.rule_id,
                    "severity": issue.severity.value,
                    "line_number": issue.line_number,
                    "message": issue.message,
                    "suggestion": issue.suggestion,
                }
                for issue in result.issues
            ],
            "validated_at": result.validated_at.isoformat(),
        }
        return json.dumps(output, indent=2)

    def to_json_summary(
        self,
        results: list[ValidationResult],
        summary: dict,
    ) -> str:
        """Convert multiple results to JSON summary string.

        Args:
            results: List of validation results.
            summary: Summary statistics.

        Returns:
            JSON string representation.
        """
        output = {
            "summary": {
                "total_specs": summary["total_specs"],
                "passed": summary["passed"],
                "warned": summary["warned"],
                "failed": summary["failed"],
                "average_score": summary["average_score"],
            },
            "results": [
                {
                    "spec_path": result.spec_path,
                    "status": result.status.value,
                    "quality_score": result.quality_score,
                    "error_count": result.error_count,
                    "warning_count": result.warning_count,
                    "info_count": result.info_count,
                    "issues": [
                        {
                            "rule_id": issue.rule_id,
                            "severity": issue.severity.value,
                            "line_number": issue.line_number,
                            "message": issue.message,
                            "suggestion": issue.suggestion,
                        }
                        for issue in result.issues
                    ],
                }
                for result in results
            ],
        }
        return json.dumps(output, indent=2)
