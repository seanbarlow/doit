"""Cross-reference commands for spec-task traceability."""

import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from ..models.crossref_models import CoverageReport, CoverageStatus
from ..services.crossref_service import CrossReferenceService
from ..services.spec_scanner import NotADoitProjectError

console = Console()

# Create the xref subcommand group
xref_app = typer.Typer(
    name="xref",
    help="Cross-reference commands for spec-task traceability",
    add_completion=False,
)


def _detect_spec_from_branch() -> Optional[str]:
    """Try to detect spec name from current git branch.

    Returns:
        Spec name if branch matches pattern XXX-feature-name, None otherwise.
    """
    import subprocess

    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            branch = result.stdout.strip()
            # Check if branch matches spec pattern (e.g., 033-feature-name)
            if branch and branch[0].isdigit():
                return branch
    except (FileNotFoundError, subprocess.SubprocessError):
        pass
    return None


def _format_coverage_rich(report: CoverageReport, console: Console) -> None:
    """Format coverage report as Rich table."""
    console.print()
    console.print(
        f"[bold]Requirement Coverage: {Path(report.spec_path).parent.name}[/bold]"
    )
    console.print("=" * 50)
    console.print()

    table = Table(show_header=True, header_style="bold")
    table.add_column("Requirement", style="cyan")
    table.add_column("Tasks", justify="right")
    table.add_column("Status")

    for rc in report.requirements:
        status_icon = {
            CoverageStatus.COVERED: "[green]\u2713 Covered[/green]",
            CoverageStatus.PARTIAL: "[yellow]\u25d0 Partial[/yellow]",
            CoverageStatus.UNCOVERED: "[red]\u26a0 Uncovered[/red]",
        }.get(rc.status, "Unknown")

        table.add_row(
            rc.requirement.id,
            str(rc.task_count),
            status_icon,
        )

    console.print(table)
    console.print()

    # Summary
    coverage_color = "green" if report.coverage_percent >= 100 else "yellow"
    if report.coverage_percent < 50:
        coverage_color = "red"

    console.print(
        f"[{coverage_color}]Coverage: {report.coverage_percent:.0f}% "
        f"({report.covered_count}/{report.total_count})[/{coverage_color}]"
    )

    # Show orphaned references if any
    if report.orphaned_references:
        console.print()
        console.print("[red]Orphaned References:[/red]")
        for task, ref_id in report.orphaned_references:
            console.print(f"  - Task at line {task.line_number} references {ref_id}")


def _format_coverage_json(report: CoverageReport) -> str:
    """Format coverage report as JSON."""
    data = {
        "spec": Path(report.spec_path).parent.name,
        "requirements": [
            {
                "id": rc.requirement.id,
                "task_count": rc.task_count,
                "covered": rc.is_covered,
                "status": rc.status.value,
            }
            for rc in report.requirements
        ],
        "coverage_percent": round(report.coverage_percent, 1),
        "covered_count": report.covered_count,
        "total_count": report.total_count,
        "orphaned_references": [
            {"task_line": task.line_number, "reference": ref_id}
            for task, ref_id in report.orphaned_references
        ],
    }
    return json.dumps(data, indent=2)


def _format_coverage_markdown(report: CoverageReport) -> str:
    """Format coverage report as Markdown."""
    lines = [
        f"# Requirement Coverage: {Path(report.spec_path).parent.name}",
        "",
        "| Requirement | Tasks | Status |",
        "|-------------|-------|--------|",
    ]

    for rc in report.requirements:
        status = {
            CoverageStatus.COVERED: "\u2713 Covered",
            CoverageStatus.PARTIAL: "\u25d0 Partial",
            CoverageStatus.UNCOVERED: "\u26a0 Uncovered",
        }.get(rc.status, "Unknown")

        lines.append(f"| {rc.requirement.id} | {rc.task_count} | {status} |")

    lines.extend(
        [
            "",
            f"**Coverage**: {report.coverage_percent:.0f}% "
            f"({report.covered_count}/{report.total_count})",
        ]
    )

    if report.orphaned_references:
        lines.extend(["", "## Orphaned References", ""])
        for task, ref_id in report.orphaned_references:
            lines.append(f"- Task at line {task.line_number} references `{ref_id}`")

    return "\n".join(lines)


@xref_app.command(name="coverage")
def coverage_command(
    spec_name: Optional[str] = typer.Argument(
        None, help="Spec directory name (default: auto-detect from branch)"
    ),
    output_format: str = typer.Option(
        "rich", "--format", "-f", help="Output format: rich, json, markdown"
    ),
    strict: bool = typer.Option(
        False, "--strict", "-s", help="Treat uncovered requirements as errors"
    ),
    output_file: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Write output to file"
    ),
) -> None:
    """Generate a coverage report showing requirement-to-task mapping.

    Shows which requirements have implementing tasks and identifies
    any uncovered requirements or orphaned task references.

    Exit codes:
      0 - All requirements covered
      1 - Uncovered requirements (with --strict) or errors
      2 - Spec not found or invalid
    """
    try:
        # Auto-detect spec from branch if not provided
        if not spec_name:
            spec_name = _detect_spec_from_branch()
            if not spec_name:
                console.print(
                    "[red]Error:[/red] Could not detect spec. "
                    "Please provide spec name or run from a feature branch."
                )
                raise typer.Exit(code=2)

        # Validate format
        valid_formats = ["rich", "json", "markdown"]
        if output_format not in valid_formats:
            console.print(
                f"[red]Error:[/red] Invalid format '{output_format}'. "
                f"Valid: {', '.join(valid_formats)}"
            )
            raise typer.Exit(code=2)

        # Get coverage report
        service = CrossReferenceService()
        try:
            report = service.get_coverage(spec_name=spec_name)
        except FileNotFoundError as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(code=2)

        # Format output
        if output_format == "json":
            output_str = _format_coverage_json(report)
        elif output_format == "markdown":
            output_str = _format_coverage_markdown(report)
        else:
            output_str = None  # Rich output handled separately

        # Write to file or stdout
        if output_file:
            if output_format == "rich":
                # For rich format to file, use markdown instead
                output_str = _format_coverage_markdown(report)
            output_file.write_text(output_str)
            console.print(f"[green]Report written to {output_file}[/green]")
        elif output_format == "rich":
            _format_coverage_rich(report, console)
        else:
            print(output_str)

        # Determine exit code
        has_orphaned = len(report.orphaned_references) > 0
        has_uncovered = report.uncovered_count > 0

        if has_orphaned:
            raise typer.Exit(code=1)
        if strict and has_uncovered:
            raise typer.Exit(code=1)

        raise typer.Exit(code=0)

    except NotADoitProjectError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=2)


@xref_app.command(name="locate")
def locate_command(
    requirement_id: str = typer.Argument(..., help="Requirement ID (e.g., FR-001)"),
    spec: Optional[str] = typer.Option(
        None, "--spec", "-s", help="Spec name or path (default: auto-detect)"
    ),
    output_format: str = typer.Option(
        "rich", "--format", "-f", help="Output format: rich, json, line"
    ),
) -> None:
    """Find the definition of a requirement in spec.md.

    Exit codes:
      0 - Requirement found
      1 - Requirement not found
      2 - Spec file not found
    """
    try:
        # Determine spec name
        spec_name = spec or _detect_spec_from_branch()
        if not spec_name:
            console.print(
                "[red]Error:[/red] Could not detect spec. "
                "Please provide --spec or run from a feature branch."
            )
            raise typer.Exit(code=2)

        # Validate format
        valid_formats = ["rich", "json", "line"]
        if output_format not in valid_formats:
            console.print(
                f"[red]Error:[/red] Invalid format '{output_format}'. "
                f"Valid: {', '.join(valid_formats)}"
            )
            raise typer.Exit(code=2)

        # Find requirement
        service = CrossReferenceService()
        try:
            req = service.locate_requirement(requirement_id, spec_name=spec_name)
        except (FileNotFoundError, ValueError) as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(code=2)

        if req is None:
            console.print(
                f"[yellow]Requirement {requirement_id} not found in spec.[/yellow]"
            )
            raise typer.Exit(code=1)

        # Format output
        if output_format == "json":
            data = {
                "id": req.id,
                "description": req.description,
                "file": req.spec_path,
                "line": req.line_number,
            }
            print(json.dumps(data, indent=2))
        elif output_format == "line":
            # Just file:line for IDE integration
            print(f"{req.spec_path}:{req.line_number}")
        else:
            # Rich format
            console.print(f"[cyan]{req.id}[/cyan]: {req.description}")
            console.print(f"Location: [dim]{req.spec_path}:{req.line_number}[/dim]")

        raise typer.Exit(code=0)

    except NotADoitProjectError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=2)


@xref_app.command(name="tasks")
def tasks_command(
    requirement_id: str = typer.Argument(..., help="Requirement ID (e.g., FR-001)"),
    spec: Optional[str] = typer.Option(
        None, "--spec", "-s", help="Spec name (default: auto-detect)"
    ),
    output_format: str = typer.Option(
        "rich", "--format", "-f", help="Output format: rich, json, markdown"
    ),
) -> None:
    """List all tasks that implement a specific requirement.

    Exit codes:
      0 - Tasks found
      1 - No tasks found for requirement
      2 - Requirement or spec not found
    """
    try:
        # Determine spec name
        spec_name = spec or _detect_spec_from_branch()
        if not spec_name:
            console.print(
                "[red]Error:[/red] Could not detect spec. "
                "Please provide --spec or run from a feature branch."
            )
            raise typer.Exit(code=2)

        # Validate format
        valid_formats = ["rich", "json", "markdown"]
        if output_format not in valid_formats:
            console.print(
                f"[red]Error:[/red] Invalid format '{output_format}'. "
                f"Valid: {', '.join(valid_formats)}"
            )
            raise typer.Exit(code=2)

        # Get tasks
        service = CrossReferenceService()
        try:
            tasks = service.get_tasks_for_requirement(requirement_id, spec_name=spec_name)
        except (FileNotFoundError, ValueError) as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(code=2)

        if not tasks:
            console.print(
                f"[yellow]No tasks found implementing {requirement_id}[/yellow]"
            )
            raise typer.Exit(code=1)

        # Format output
        if output_format == "json":
            data = {
                "requirement_id": requirement_id,
                "tasks": [
                    {
                        "line": t.line_number,
                        "completed": t.completed,
                        "description": t.description,
                    }
                    for t in tasks
                ],
                "count": len(tasks),
                "completed_count": sum(1 for t in tasks if t.completed),
            }
            print(json.dumps(data, indent=2))
        elif output_format == "markdown":
            lines = [
                f"# Tasks implementing {requirement_id}",
                "",
                "| Line | Status | Description |",
                "|------|--------|-------------|",
            ]
            for t in tasks:
                status = "[x]" if t.completed else "[ ]"
                lines.append(f"| {t.line_number} | {status} | {t.description} |")

            completed = sum(1 for t in tasks if t.completed)
            lines.extend(
                ["", f"Found {len(tasks)} tasks ({completed} complete, {len(tasks) - completed} pending)"]
            )
            print("\n".join(lines))
        else:
            # Rich format
            console.print(f"\n[bold]Tasks implementing {requirement_id}:[/bold]\n")

            table = Table(show_header=True, header_style="bold")
            table.add_column("Line", justify="right")
            table.add_column("Status")
            table.add_column("Description")

            for t in tasks:
                status = "[green][x][/green]" if t.completed else "[ ]"
                table.add_row(str(t.line_number), status, t.description)

            console.print(table)

            completed = sum(1 for t in tasks if t.completed)
            console.print(
                f"\nFound {len(tasks)} tasks ({completed} complete, {len(tasks) - completed} pending)"
            )

        raise typer.Exit(code=0)

    except NotADoitProjectError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=2)


@xref_app.command(name="validate")
def validate_command(
    spec_name: Optional[str] = typer.Argument(
        None, help="Spec directory name (default: auto-detect from branch)"
    ),
    strict: bool = typer.Option(
        False, "--strict", "-s", help="Treat warnings as errors"
    ),
    output_format: str = typer.Option(
        "rich", "--format", "-f", help="Output format: rich, json"
    ),
) -> None:
    """Validate cross-reference integrity between spec and tasks.

    Checks for:
    - Orphaned task references (tasks referencing non-existent requirements)
    - Uncovered requirements (requirements with no linked tasks)

    Exit codes:
      0 - All cross-references valid
      1 - Validation errors found
      2 - Files not found
    """
    try:
        # Auto-detect spec from branch if not provided
        if not spec_name:
            spec_name = _detect_spec_from_branch()
            if not spec_name:
                console.print(
                    "[red]Error:[/red] Could not detect spec. "
                    "Please provide spec name or run from a feature branch."
                )
                raise typer.Exit(code=2)

        # Validate format
        valid_formats = ["rich", "json"]
        if output_format not in valid_formats:
            console.print(
                f"[red]Error:[/red] Invalid format '{output_format}'. "
                f"Valid: {', '.join(valid_formats)}"
            )
            raise typer.Exit(code=2)

        # Validate references
        service = CrossReferenceService()
        try:
            uncovered, orphaned = service.validate_references(spec_name=spec_name)
            report = service.get_coverage(spec_name=spec_name)
        except FileNotFoundError as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(code=2)

        # Count issues
        error_count = len(orphaned)  # Orphaned references are always errors
        warning_count = len(uncovered)  # Uncovered are warnings (errors in strict)

        if strict:
            error_count += warning_count
            warning_count = 0

        # Format output
        if output_format == "json":
            data = {
                "spec": spec_name,
                "valid": error_count == 0 and warning_count == 0,
                "errors": error_count,
                "warnings": warning_count,
                "orphaned_references": [
                    {"task_line": t.line_number, "reference": ref}
                    for t, ref in orphaned
                ],
                "uncovered_requirements": uncovered,
            }
            print(json.dumps(data, indent=2))
        else:
            # Rich format
            console.print(f"\n[bold]Cross-Reference Validation: {spec_name}[/bold]")
            console.print("=" * 50)
            console.print()

            # Show results
            if not orphaned:
                console.print(
                    f"[green]\u2713[/green] All {report.total_count} requirement "
                    "references are valid"
                )
            else:
                console.print("[red]\u2717 Orphaned References:[/red]")
                for task, ref_id in orphaned:
                    console.print(
                        f"  - Task at line {task.line_number} references "
                        f"non-existent {ref_id}"
                    )

            if uncovered:
                severity = "[red]\u2717" if strict else "[yellow]\u26a0"
                console.print(
                    f"\n{severity} {len(uncovered)} requirements have no linked tasks: "
                    f"{', '.join(uncovered)}[/]"
                )
            elif report.total_count > 0:
                console.print(
                    f"[green]\u2713[/green] All requirements have linked tasks"
                )

            # Summary
            console.print()
            if error_count == 0 and warning_count == 0:
                console.print("[green]Validation: PASS[/green]")
            elif error_count > 0:
                console.print(
                    f"[red]Validation: FAIL ({error_count} errors, "
                    f"{warning_count} warnings)[/red]"
                )
            else:
                console.print(
                    f"[yellow]Validation: WARN (0 errors, "
                    f"{warning_count} warnings)[/yellow]"
                )

        # Determine exit code
        if error_count > 0:
            raise typer.Exit(code=1)

        raise typer.Exit(code=0)

    except NotADoitProjectError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=2)
