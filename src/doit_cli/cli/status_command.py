"""Status command for displaying spec status dashboard."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from ..exit_codes import ExitCode
from ..formatters.json_formatter import JsonFormatter
from ..formatters.markdown_formatter import MarkdownFormatter
from ..formatters.rich_formatter import RichFormatter
from ..models.status_models import SpecState
from ..services.spec_scanner import NotADoitProjectError
from ..services.status_reporter import StatusReporter
from .output import OutputFormat, format_option, resolve_format

console = Console()

# Valid status filter values
VALID_STATUSES = ["draft", "in-progress", "complete", "approved"]

_STATUS_FORMATS = (OutputFormat.RICH, OutputFormat.JSON, OutputFormat.MARKDOWN)


def status_command(
    status_filter: str | None = typer.Option(
        None,
        "--status",
        "-s",
        help="Filter by status (draft, in-progress, complete, approved)",
    ),
    blocking: bool = typer.Option(False, "--blocking", "-b", help="Show only blocking specs"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed validation errors"),
    recent: int | None = typer.Option(
        None, "--recent", "-r", help="Show specs modified in last N days"
    ),
    output_format: str = format_option(
        default=OutputFormat.RICH,
        allowed=_STATUS_FORMATS,
    ),
    output_file: Path | None = typer.Option(None, "--output", "-o", help="Write report to file"),
) -> None:
    """Display status of all specifications in the project.

    Shows a dashboard of all specs with their status, validation results,
    and commit blocking indicators.

    Exit codes (see doit_cli.exit_codes.ExitCode):
      0 (SUCCESS)          — no blocking specs
      1 (FAILURE)          — blocking specs exist
      2 (VALIDATION_ERROR) — invalid options or not a doit project
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
                raise typer.Exit(code=ExitCode.VALIDATION_ERROR)
            spec_state_filter = SpecState.from_string(status_lower)

        fmt = resolve_format(output_format, _STATUS_FORMATS)

        # Initialize reporter
        reporter = StatusReporter()

        # Generate report with filters
        report = reporter.generate_report(
            status_filter=spec_state_filter,
            blocking_only=blocking,
            recent_days=recent,
        )

        # Select formatter based on format option.
        # The three concrete classes share a StatusFormatter protocol; mypy
        # narrows `formatter` to JsonFormatter after the first branch unless
        # we annotate the union explicitly.
        formatter: JsonFormatter | MarkdownFormatter | RichFormatter
        if fmt is OutputFormat.JSON:
            formatter = JsonFormatter()
        elif fmt is OutputFormat.MARKDOWN:
            formatter = MarkdownFormatter()
        else:
            formatter = RichFormatter(console)

        # Generate formatted output
        output_str = formatter.format(report, verbose=verbose)

        # Handle output destination
        if output_file:
            output_file.write_text(output_str)
            console.print(f"[green]Report written to {output_file}[/green]")
        elif fmt is OutputFormat.RICH:
            # Rich formatter should print directly for better terminal rendering
            RichFormatter(console).format_to_console(report, verbose=verbose)
        else:
            # JSON and Markdown output to stdout - use print() for raw output
            print(output_str)

        # Determine exit code based on blocking status
        if report.blocking_count > 0:
            raise typer.Exit(code=ExitCode.FAILURE)
        raise typer.Exit(code=ExitCode.SUCCESS)

    except NotADoitProjectError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=ExitCode.VALIDATION_ERROR) from e
