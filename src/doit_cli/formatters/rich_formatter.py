"""Rich terminal formatter for status output."""

from datetime import datetime
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..models.status_models import SpecState, SpecStatus, StatusReport
from .base import StatusFormatter


class RichFormatter(StatusFormatter):
    """Formats status as rich terminal output with colors and tables.

    Uses the Rich library to produce attractive terminal output with:
    - Colored status indicators
    - Formatted tables
    - Summary panels
    """

    def __init__(self, console: Optional[Console] = None) -> None:
        """Initialize formatter with optional console.

        Args:
            console: Rich Console instance. Creates new one if not provided.
        """
        self.console = console or Console()

    def format(self, report: StatusReport, verbose: bool = False) -> str:
        """Format the status report as a string.

        Note: For rich terminal output, use format_to_console() instead.
        This method captures the output as a string.

        Args:
            report: The StatusReport to format.
            verbose: Include detailed validation errors.

        Returns:
            Formatted string representation (with ANSI codes).
        """
        # Capture output to string
        from io import StringIO

        string_io = StringIO()
        temp_console = Console(file=string_io, force_terminal=True)

        self._render_to_console(report, verbose, temp_console)

        return string_io.getvalue()

    def format_to_console(self, report: StatusReport, verbose: bool = False) -> None:
        """Format and print directly to console with rich formatting.

        Args:
            report: The StatusReport to format.
            verbose: Include detailed validation errors.
        """
        self._render_to_console(report, verbose, self.console)

    def _render_to_console(
        self, report: StatusReport, verbose: bool, console: Console
    ) -> None:
        """Internal method to render report to a console.

        Args:
            report: The StatusReport to format.
            verbose: Include detailed validation errors.
            console: Console to render to.
        """
        # Header panel
        project_name = report.project_root.name
        generated = report.generated_at.strftime("%Y-%m-%d %H:%M:%S")

        header = f"[bold]📊 Project:[/bold] {project_name}\n"
        header += f"[bold]📅 Generated:[/bold] {generated}"

        console.print(
            Panel(header, title="Spec Status Dashboard", border_style="blue")
        )
        console.print()

        # Specs table
        if report.specs:
            table = self._create_specs_table(report, verbose)
            console.print(table)
            console.print()

            # Summary panel
            summary = self._create_summary_panel(report)
            console.print(summary)
        else:
            console.print(
                "[yellow]No specifications found.[/yellow] "
                "Run 'doit specit' to create one."
            )

    def _create_specs_table(
        self, report: StatusReport, verbose: bool
    ) -> Table:
        """Create the main specs table.

        Args:
            report: The StatusReport containing specs.
            verbose: Include validation error details.

        Returns:
            Rich Table with spec information.
        """
        table = Table(show_header=True, header_style="bold")

        # Columns
        table.add_column("Spec", style="cyan", no_wrap=True)
        table.add_column("Status", justify="center")
        table.add_column("Validation", justify="center")
        table.add_column("Modified", justify="right")

        if verbose:
            table.add_column("Details", style="dim")

        for spec in report.specs:
            # Status with emoji
            status_display = f"{spec.status.emoji} {spec.status.display_name}"
            status_style = self._get_status_style(spec.status)

            # Validation indicator
            if spec.error:
                validation_display = "[red]❌ Error[/red]"
            elif spec.validation_result is None:
                validation_display = "[dim]—[/dim]"
            elif spec.validation_passed:
                validation_display = "[green]✅ Pass[/green]"
            else:
                validation_display = f"[red]❌ Fail ({spec.validation_result.error_count})[/red]"

            # Blocking indicator
            if spec.is_blocking:
                validation_display += " [bold red]⛔[/bold red]"

            # Modified date (relative)
            modified = self._format_relative_date(spec.last_modified)

            # Build row
            row = [
                spec.name,
                f"[{status_style}]{status_display}[/{status_style}]",
                validation_display,
                modified,
            ]

            if verbose:
                details = self._get_spec_details(spec)
                row.append(details)

            table.add_row(*row)

        return table

    def _create_summary_panel(self, report: StatusReport) -> Panel:
        """Create the summary panel with statistics.

        Args:
            report: The StatusReport to summarize.

        Returns:
            Rich Panel with summary statistics.
        """
        # Status counts
        counts = report.by_status
        status_line = (
            f"[dim]Draft:[/dim] {counts.get(SpecState.DRAFT, 0)}  │  "
            f"[dim]In Progress:[/dim] {counts.get(SpecState.IN_PROGRESS, 0)}  │  "
            f"[dim]Complete:[/dim] {counts.get(SpecState.COMPLETE, 0)}  │  "
            f"[dim]Approved:[/dim] {counts.get(SpecState.APPROVED, 0)}"
        )

        # Completion percentage
        completion = f"[bold]Completion:[/bold] {report.completion_percentage:.0f}%"

        # Ready to commit indicator
        if report.is_ready_to_commit:
            ready = "[green]✅ Ready to commit[/green]"
        else:
            ready = f"[red]⛔ {report.blocking_count} spec(s) blocking[/red]"

        summary = f"{status_line}\n{completion}  │  {ready}"

        return Panel(summary, title="Summary", border_style="green" if report.is_ready_to_commit else "red")

    def _get_status_style(self, status: SpecState) -> str:
        """Get Rich style for a status.

        Args:
            status: The SpecState to style.

        Returns:
            Rich style string.
        """
        styles = {
            SpecState.DRAFT: "dim",
            SpecState.IN_PROGRESS: "yellow",
            SpecState.COMPLETE: "green",
            SpecState.APPROVED: "bold green",
            SpecState.ERROR: "red",
        }
        return styles.get(status, "white")

    def _format_relative_date(self, dt: datetime) -> str:
        """Format a datetime as relative time (Today, Yesterday, etc.).

        Args:
            dt: Datetime to format.

        Returns:
            Human-readable relative date string.
        """
        now = datetime.now()
        diff = now - dt

        if diff.days == 0:
            return "Today"
        elif diff.days == 1:
            return "Yesterday"
        elif diff.days < 7:
            return f"{diff.days} days ago"
        else:
            return dt.strftime("%Y-%m-%d")

    def _get_spec_details(self, spec: SpecStatus) -> str:
        """Get detailed information about a spec for verbose mode.

        Args:
            spec: The SpecStatus to describe.

        Returns:
            Details string with validation errors if any.
        """
        if spec.error:
            return spec.error

        if spec.validation_result is None:
            return "Not validated"

        if spec.validation_passed:
            return f"Score: {spec.validation_score}"

        # Show validation errors
        errors = []
        for issue in spec.validation_result.issues[:3]:  # Limit to 3
            errors.append(f"• {issue.message}")

        if len(spec.validation_result.issues) > 3:
            errors.append(f"• ... and {len(spec.validation_result.issues) - 3} more")

        return "\n".join(errors)
