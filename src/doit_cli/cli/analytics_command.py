"""Analytics command for spec metrics and reporting.

Provides CLI commands for viewing spec analytics:
- show: Display completion metrics summary (default)
- cycles: Display cycle time statistics
- velocity: Display velocity trends
- spec: Display individual spec metrics
- export: Export analytics report
"""

import json
from datetime import date, datetime
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from ..models.status_models import SpecState
from ..services.analytics_service import AnalyticsService
from ..services.spec_scanner import NotADoitProjectError, SpecNotFoundError

app = typer.Typer(help="Spec analytics and metrics dashboard")
console = Console()


def _get_status_emoji(status: SpecState) -> str:
    """Get emoji for status display."""
    emojis = {
        SpecState.DRAFT: "[dim]📝[/dim]",
        SpecState.IN_PROGRESS: "[yellow]🔄[/yellow]",
        SpecState.COMPLETE: "[green]✅[/green]",
        SpecState.APPROVED: "[cyan]🏆[/cyan]",
        SpecState.ERROR: "[red]❌[/red]",
    }
    return emojis.get(status, "❓")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Spec analytics and metrics dashboard.

    Run without arguments to show completion metrics summary.
    """
    if ctx.invoked_subcommand is None:
        # Default to show command
        show(json_output=False)


@app.command()
def show(
    json_output: bool = typer.Option(
        False, "--json", help="Output as JSON instead of table"
    ),
) -> None:
    """Display completion metrics summary for all specs.

    Shows total specs, status breakdown, and completion percentage.

    Exit codes:
      0 - Success
      1 - No specs found
      2 - Not a doit project
    """
    try:
        service = AnalyticsService()
        summary = service.get_completion_summary()

        if summary["total_specs"] == 0:
            if json_output:
                print(json.dumps({"success": False, "error": "No specs found"}))
            else:
                console.print(
                    "[yellow]No specifications found in specs/ directory.[/yellow]"
                )
            raise typer.Exit(code=1)

        if json_output:
            report = service.generate_report()
            print(json.dumps(report.to_dict(), indent=2))
        else:
            _print_completion_summary(summary)

        raise typer.Exit(code=0)

    except NotADoitProjectError as e:
        if json_output:
            print(json.dumps({"success": False, "error": str(e)}))
        else:
            console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=2)


def _print_completion_summary(summary: dict) -> None:
    """Print completion metrics in Rich tables."""
    console.print()
    console.print("[bold]Spec Analytics[/bold]")
    console.print()

    # Summary table
    summary_table = Table(title="Summary", show_header=True)
    summary_table.add_column("Metric", style="bold")
    summary_table.add_column("Value", justify="right")

    summary_table.add_row("Total Specs", str(summary["total_specs"]))
    summary_table.add_row(
        "Completed",
        str(summary["complete_count"] + summary["approved_count"]),
    )
    summary_table.add_row("In Progress", str(summary["in_progress_count"]))
    summary_table.add_row("Draft", str(summary["draft_count"]))
    summary_table.add_row("Completion %", f"{summary['completion_pct']}%")

    console.print(summary_table)
    console.print()

    # Status breakdown table
    breakdown_table = Table(title="Status Breakdown", show_header=True)
    breakdown_table.add_column("Status")
    breakdown_table.add_column("Count", justify="right")
    breakdown_table.add_column("Percentage", justify="right")

    total = summary["total_specs"]

    status_data = [
        (_get_status_emoji(SpecState.COMPLETE) + " Complete", summary["complete_count"]),
        (_get_status_emoji(SpecState.APPROVED) + " Approved", summary["approved_count"]),
        (_get_status_emoji(SpecState.IN_PROGRESS) + " Progress", summary["in_progress_count"]),
        (_get_status_emoji(SpecState.DRAFT) + " Draft", summary["draft_count"]),
    ]

    for status_name, count in status_data:
        pct = (count / total * 100) if total > 0 else 0
        breakdown_table.add_row(status_name, str(count), f"{pct:.1f}%")

    console.print(breakdown_table)
    console.print()


@app.command()
def cycles(
    days: int = typer.Option(30, "--days", "-d", help="Filter to last N days"),
    since: Optional[str] = typer.Option(
        None, "--since", "-s", help="Filter since date (YYYY-MM-DD)"
    ),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Display cycle time statistics for completed specs.

    Shows average, median, min, max, and standard deviation of cycle times.

    Exit codes:
      0 - Success
      1 - No completed specs in period
      2 - Not a doit project
    """
    try:
        service = AnalyticsService()

        # Parse since date if provided
        since_date: Optional[date] = None
        filter_days: Optional[int] = days

        if since:
            try:
                since_date = datetime.strptime(since, "%Y-%m-%d").date()
                filter_days = None  # since overrides days
            except ValueError:
                console.print(
                    f"[red]Error:[/red] Invalid date format '{since}'. Use YYYY-MM-DD."
                )
                raise typer.Exit(code=2)

        stats, records = service.get_cycle_time_stats(days=filter_days, since=since_date)

        if not records:
            if json_output:
                print(json.dumps({"success": False, "error": "No completed specs in period"}))
            else:
                console.print(
                    "[yellow]No completed specs found in the specified period.[/yellow]"
                )
            raise typer.Exit(code=1)

        if json_output:
            _print_cycles_json(stats, records)
        else:
            _print_cycles_tables(stats, records, days if not since else None, since)

        raise typer.Exit(code=0)

    except NotADoitProjectError as e:
        if json_output:
            print(json.dumps({"success": False, "error": str(e)}))
        else:
            console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=2)


def _print_cycles_json(stats, records) -> None:
    """Print cycle time data as JSON."""
    output = {
        "success": True,
        "cycle_stats": {
            "average_days": stats.average_days,
            "median_days": stats.median_days,
            "min_days": stats.min_days,
            "max_days": stats.max_days,
            "std_dev_days": stats.std_dev_days,
            "sample_count": stats.sample_count,
        },
        "recent_completions": [
            {
                "name": r.feature_name,
                "completed": r.end_date.isoformat(),
                "cycle_days": r.days_to_complete,
            }
            for r in records[:10]
        ],
    }
    print(json.dumps(output, indent=2))


def _print_cycles_tables(stats, records, days: Optional[int], since: Optional[str]) -> None:
    """Print cycle time data in Rich tables."""
    console.print()

    # Title with filter info
    if since:
        title = f"Cycle Time Analysis (since {since})"
    else:
        title = f"Cycle Time Analysis (last {days} days)"

    console.print(f"[bold]{title}[/bold]")
    console.print()

    # Statistics table
    stats_table = Table(
        title=f"Statistics (N={stats.sample_count} completed specs)",
        show_header=True,
    )
    stats_table.add_column("Metric", style="bold")
    stats_table.add_column("Value", justify="right")

    stats_table.add_row("Average", f"{stats.average_days} days")
    stats_table.add_row("Median", f"{stats.median_days} days")
    stats_table.add_row("Minimum", f"{stats.min_days} day{'s' if stats.min_days != 1 else ''}")
    stats_table.add_row("Maximum", f"{stats.max_days} days")
    stats_table.add_row("Std Deviation", f"{stats.std_dev_days} days")

    console.print(stats_table)
    console.print()

    # Recent completions table (top 10)
    recent_table = Table(title="Recent Completions", show_header=True)
    recent_table.add_column("Spec")
    recent_table.add_column("Completed", justify="center")
    recent_table.add_column("Cycle Time", justify="right")

    for record in records[:10]:
        recent_table.add_row(
            record.feature_name,
            record.end_date.isoformat(),
            f"{record.days_to_complete} days",
        )

    console.print(recent_table)
    console.print()


@app.command()
def velocity(
    weeks: int = typer.Option(8, "--weeks", "-w", help="Number of weeks to display"),
    format_type: str = typer.Option(
        "table", "--format", "-f", help="Output format: table, json, csv"
    ),
) -> None:
    """Display velocity trends over time.

    Shows specs completed per week with visual indicators.

    Exit codes:
      0 - Success
      1 - Insufficient data (< 2 weeks)
      2 - Not a doit project
    """
    try:
        service = AnalyticsService()
        velocity_data = service.get_velocity_data(weeks=weeks)

        if len(velocity_data) < 2:
            if format_type == "json":
                print(json.dumps({"success": False, "error": "Insufficient data"}))
            else:
                console.print(
                    "[yellow]Insufficient data for velocity trends. "
                    "Need at least 2 weeks of history.[/yellow]"
                )
                if velocity_data:
                    console.print(f"Available data points: {len(velocity_data)}")
            raise typer.Exit(code=1)

        if format_type == "json":
            _print_velocity_json(velocity_data)
        elif format_type == "csv":
            _print_velocity_csv(velocity_data)
        else:
            _print_velocity_table(velocity_data, weeks)

        raise typer.Exit(code=0)

    except NotADoitProjectError as e:
        if format_type == "json":
            print(json.dumps({"success": False, "error": str(e)}))
        else:
            console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=2)


def _print_velocity_json(velocity_data) -> None:
    """Print velocity data as JSON."""
    output = {
        "success": True,
        "velocity": [
            {
                "week": v.week_key,
                "completed": v.specs_completed,
                "specs": v.spec_names,
            }
            for v in velocity_data
        ],
    }
    print(json.dumps(output, indent=2))


def _print_velocity_csv(velocity_data) -> None:
    """Print velocity data as CSV."""
    print("week,completed")
    for v in velocity_data:
        print(f"{v.week_key},{v.specs_completed}")


def _print_velocity_table(velocity_data, weeks: int) -> None:
    """Print velocity data in Rich table with bar visualization."""
    console.print()
    console.print(f"[bold]Velocity Trends (last {weeks} weeks)[/bold]")
    console.print()

    # Find max for bar scaling
    max_completed = max((v.specs_completed for v in velocity_data), default=1)

    velocity_table = Table(show_header=True)
    velocity_table.add_column("Week", style="bold")
    velocity_table.add_column("Completed", justify="right")
    velocity_table.add_column("Trend", min_width=35)

    for v in velocity_data:
        # Create bar visualization
        bar_width = int((v.specs_completed / max_completed) * 30) if max_completed > 0 else 0
        bar = "█" * bar_width

        velocity_table.add_row(
            v.week_key,
            str(v.specs_completed),
            f"[green]{bar}[/green]",
        )

    console.print(velocity_table)

    # Calculate and show average
    total = sum(v.specs_completed for v in velocity_data)
    avg = total / len(velocity_data) if velocity_data else 0
    console.print()
    console.print(f"Average: {avg:.1f} specs/week")
    console.print()


@app.command()
def spec(
    spec_name: str = typer.Argument(..., help="Spec directory name"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Display detailed metrics for a specific spec.

    Shows status, dates, cycle time, and phase timeline.

    Exit codes:
      0 - Success
      1 - Spec not found
      2 - Not a doit project
    """
    try:
        service = AnalyticsService()

        try:
            metadata = service.get_spec_details(spec_name)
        except SpecNotFoundError:
            # Try to find similar specs
            available = service.list_all_spec_names()
            matches = [n for n in available if spec_name.lower() in n.lower()]

            if json_output:
                print(json.dumps({
                    "success": False,
                    "error": f"Spec '{spec_name}' not found",
                    "suggestions": matches[:5] if matches else available[:5],
                }))
            else:
                console.print(f"[red]Error:[/red] Spec '{spec_name}' not found.")
                if matches:
                    console.print("\nDid you mean:")
                    for m in matches[:5]:
                        console.print(f"  - {m}")
                else:
                    console.print("\nAvailable specs:")
                    for a in available[:5]:
                        console.print(f"  - {a}")
            raise typer.Exit(code=1)

        if json_output:
            _print_spec_json(metadata)
        else:
            _print_spec_details(metadata)

        raise typer.Exit(code=0)

    except NotADoitProjectError as e:
        if json_output:
            print(json.dumps({"success": False, "error": str(e)}))
        else:
            console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=2)


def _print_spec_json(metadata) -> None:
    """Print spec details as JSON."""
    output = {
        "success": True,
        "spec": {
            "name": metadata.name,
            "status": metadata.status.display_name,
            "created_at": metadata.created_at.isoformat() if metadata.created_at else None,
            "completed_at": metadata.completed_at.isoformat() if metadata.completed_at else None,
            "cycle_time_days": metadata.cycle_time_days,
            "current_phase": metadata.current_phase,
            "days_in_progress": metadata.days_in_progress,
            "path": str(metadata.path) if metadata.path else None,
        },
    }
    print(json.dumps(output, indent=2))


def _print_spec_details(metadata) -> None:
    """Print spec details in Rich tables."""
    console.print()
    console.print(f"[bold]Spec Details: {metadata.name}[/bold]")
    console.print()

    # Details table
    details_table = Table(show_header=True)
    details_table.add_column("Field", style="bold")
    details_table.add_column("Value")

    status_display = f"{_get_status_emoji(metadata.status)} {metadata.status.display_name}"
    details_table.add_row("Status", status_display)
    details_table.add_row(
        "Created",
        metadata.created_at.isoformat() if metadata.created_at else "Unknown",
    )
    details_table.add_row(
        "Completed",
        metadata.completed_at.isoformat() if metadata.completed_at else "-",
    )

    if metadata.cycle_time_days is not None:
        details_table.add_row("Cycle Time", f"{metadata.cycle_time_days} days")
    elif metadata.days_in_progress > 0:
        details_table.add_row("Days In Progress", str(metadata.days_in_progress))

    details_table.add_row("Current Phase", metadata.current_phase)
    details_table.add_row("Path", str(metadata.path) if metadata.path else "-")

    console.print(details_table)
    console.print()

    # Timeline table (if we have dates)
    if metadata.created_at:
        timeline_table = Table(title="Timeline", show_header=True)
        timeline_table.add_column("Date")
        timeline_table.add_column("Event")

        timeline_table.add_row(
            metadata.created_at.isoformat(),
            "Spec created (Draft)",
        )

        if metadata.status in (SpecState.IN_PROGRESS, SpecState.COMPLETE, SpecState.APPROVED):
            # Estimate start date (not precise, but helpful)
            timeline_table.add_row("-", "Started (In Progress)")

        if metadata.completed_at:
            timeline_table.add_row(
                metadata.completed_at.isoformat(),
                "Completed",
            )

        console.print(timeline_table)
        console.print()


@app.command()
def export(
    format_type: str = typer.Option(
        "markdown", "--format", "-f", help="Export format: markdown, json"
    ),
    output_path: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Output file path"
    ),
) -> None:
    """Export analytics report to file.

    Creates a report in .doit/reports/ by default.

    Exit codes:
      0 - Success
      1 - Export failed
      2 - Not a doit project
    """
    try:
        service = AnalyticsService()
        report = service.generate_report()

        # Determine output path
        if output_path is None:
            reports_dir = service.project_root / ".doit" / "reports"
            reports_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y-%m-%d")
            ext = "json" if format_type == "json" else "md"
            output_path = reports_dir / f"analytics-{timestamp}.{ext}"

        # Generate content
        if format_type == "json":
            content = json.dumps(report.to_dict(), indent=2)
        else:
            content = _generate_markdown_report(report)

        # Write file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")

        console.print(f"[green]✓[/green] Analytics report exported to {output_path}")
        raise typer.Exit(code=0)

    except NotADoitProjectError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=2)
    except (OSError, IOError) as e:
        console.print(f"[red]Error:[/red] Failed to export report: {e}")
        raise typer.Exit(code=1)


def _generate_markdown_report(report) -> str:
    """Generate markdown content for analytics report."""
    lines = [
        f"# Analytics Report - {report.project_root.name}",
        "",
        f"Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Summary",
        "",
        f"- Total Specs: {report.total_specs}",
        f"- Completion Rate: {report.completion_pct}%",
    ]

    if report.cycle_stats:
        lines.append(f"- Average Cycle Time: {report.cycle_stats.average_days} days")

    lines.extend([
        "",
        "## Status Breakdown",
        "",
        "| Status | Count |",
        "|--------|-------|",
    ])

    for status, count in report.by_status.items():
        lines.append(f"| {status.display_name} | {count} |")

    if report.cycle_stats:
        lines.extend([
            "",
            "## Cycle Time Statistics",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| Average | {report.cycle_stats.average_days} days |",
            f"| Median | {report.cycle_stats.median_days} days |",
            f"| Min | {report.cycle_stats.min_days} days |",
            f"| Max | {report.cycle_stats.max_days} days |",
            f"| Sample Size | {report.cycle_stats.sample_count} |",
        ])

    if report.velocity:
        lines.extend([
            "",
            "## Velocity Trends",
            "",
            "| Week | Completed |",
            "|------|-----------|",
        ])
        for v in report.velocity[:12]:
            lines.append(f"| {v.week_key} | {v.specs_completed} |")

    return "\n".join(lines)
