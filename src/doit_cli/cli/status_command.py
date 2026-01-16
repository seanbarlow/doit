"""Status command for displaying spec status dashboard."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from ..formatters.json_formatter import JsonFormatter
from ..formatters.markdown_formatter import MarkdownFormatter
from ..formatters.rich_formatter import RichFormatter
from ..models.status_models import SpecState
from ..services.spec_scanner import NotADoitProjectError
from ..services.status_reporter import StatusReporter

console = Console()

# Valid status filter values
VALID_STATUSES = ["draft", "in-progress", "complete", "approved"]


def status_command(
    status_filter: Optional[str] = typer.Option(
        None,
        "--status",
        "-s",
        help="Filter by status (draft, in-progress, complete, approved)",
    ),
    blocking: bool = typer.Option(
        False, "--blocking", "-b", help="Show only blocking specs"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show detailed validation errors"
    ),
    recent: Optional[int] = typer.Option(
        None, "--recent", "-r", help="Show specs modified in last N days"
    ),
    output_format: str = typer.Option(
        "rich", "--format", "-f", help="Output format: rich, json, markdown"
    ),
    output_file: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Write report to file"
    ),
) -> None:
    """Display status of all specifications in the project.

    Shows a dashboard of all specs with their status, validation results,
    and commit blocking indicators.

    Exit codes:
      0 - Success, no blocking specs
      1 - Success, but blocking specs exist
      2 - Error (not a doit project, invalid options)
    """
    try:
        # Validate status filter
        spec_state_filter = None
        if status_filter:
            status_lower = status_filter.lower()
            if status_lower not in VALID_STATUSES:
                console.print(
                    f"[red]Error:[/red] Invalid status '{status_filter}'. "
                    f"Valid: {', '.join(VALID_STATUSES)}"
                )
                raise typer.Exit(code=2)
            spec_state_filter = SpecState.from_string(status_lower)

        # Validate format
        valid_formats = ["rich", "json", "markdown"]
        if output_format not in valid_formats:
            console.print(
                f"[red]Error:[/red] Invalid format '{output_format}'. "
                f"Valid: {', '.join(valid_formats)}"
            )
            raise typer.Exit(code=2)

        # Initialize reporter
        reporter = StatusReporter()

        # Generate report with filters
        report = reporter.generate_report(
            status_filter=spec_state_filter,
            blocking_only=blocking,
            recent_days=recent,
        )

        # Select formatter based on format option
        if output_format == "json":
            formatter = JsonFormatter()
        elif output_format == "markdown":
            formatter = MarkdownFormatter()
        else:
            formatter = RichFormatter(console)

        # Generate formatted output
        output_str = formatter.format(report, verbose=verbose)

        # Handle output destination
        if output_file:
            output_file.write_text(output_str)
            console.print(f"[green]Report written to {output_file}[/green]")
        elif output_format == "rich":
            # Rich formatter should print directly for better terminal rendering
            RichFormatter(console).format_to_console(report, verbose=verbose)
        else:
            # JSON and Markdown output to stdout - use print() for raw output
            print(output_str)

        # Determine exit code based on blocking status
        if report.blocking_count > 0:
            raise typer.Exit(code=1)
        else:
            raise typer.Exit(code=0)

    except NotADoitProjectError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=2)
