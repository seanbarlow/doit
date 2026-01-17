"""CLI commands for diagram generation."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from ..models.diagram_models import DiagramType
from ..services.diagram_service import DiagramService

# Create Typer app for diagram subcommands
app = typer.Typer(
    name="diagram",
    help="Generate and validate Mermaid diagrams from specifications",
    add_completion=False,
)

console = Console()


def _resolve_file_path(file: Optional[Path]) -> Optional[Path]:
    """Resolve file path, auto-detecting if not provided.

    Args:
        file: Optional path to spec/plan file

    Returns:
        Resolved path or None if not found
    """
    if file:
        return file.resolve()

    # Try to auto-detect spec.md in current directory or specs/
    cwd = Path.cwd()

    # Check current directory
    if (cwd / "spec.md").exists():
        return cwd / "spec.md"

    # Check for specs/ directory with current feature
    specs_dir = cwd / "specs"
    if specs_dir.exists():
        # Look for most recently modified spec.md
        spec_files = list(specs_dir.glob("*/spec.md"))
        if spec_files:
            return max(spec_files, key=lambda p: p.stat().st_mtime)

    return None


def _parse_diagram_types(type_str: str) -> list[DiagramType]:
    """Parse diagram type string to list of DiagramType.

    Args:
        type_str: Type string (user-journey, er-diagram, architecture, all)

    Returns:
        List of DiagramType values
    """
    if type_str == "all":
        return [DiagramType.USER_JOURNEY, DiagramType.ER_DIAGRAM]

    try:
        return [DiagramType.from_string(type_str)]
    except ValueError:
        return []


@app.command(name="generate")
def generate_command(
    file: Optional[Path] = typer.Argument(
        None,
        help="Path to spec.md or plan.md file",
        exists=False,
    ),
    strict: bool = typer.Option(
        False,
        "--strict",
        "-s",
        help="Fail on validation errors",
    ),
    no_insert: bool = typer.Option(
        False,
        "--no-insert",
        help="Output diagrams without inserting into file",
    ),
    diagram_type: str = typer.Option(
        "all",
        "--type",
        "-t",
        help="Diagram type: user-journey, er-diagram, architecture, all",
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Write diagrams to separate file",
    ),
) -> None:
    """Generate Mermaid diagrams for a specification file.

    If FILE is not provided, auto-detects spec.md in current directory
    or finds the most recently modified spec in specs/.

    Examples:
        doit diagram generate
        doit diagram generate specs/035-feature/spec.md
        doit diagram generate --type er-diagram --strict
        doit diagram generate --no-insert --output diagrams.md
    """
    # Resolve file path
    resolved_path = _resolve_file_path(file)
    if not resolved_path:
        console.print("[red]Error:[/red] No spec file found. Provide a path or run from a spec directory.")
        raise typer.Exit(code=1)

    if not resolved_path.exists():
        console.print(f"[red]Error:[/red] File not found: {resolved_path}")
        raise typer.Exit(code=1)

    # Parse diagram types
    types = _parse_diagram_types(diagram_type)
    if not types and diagram_type != "all":
        console.print(f"[red]Error:[/red] Unknown diagram type: {diagram_type}")
        console.print("Valid types: user-journey, er-diagram, architecture, all")
        raise typer.Exit(code=1)

    console.print(f"Generating diagrams for: [cyan]{resolved_path}[/cyan]")
    console.print()

    # Create service and generate
    service = DiagramService(strict=strict, backup=True)
    result = service.generate(
        file_path=resolved_path,
        diagram_types=types if types else None,
        insert=not no_insert,
    )

    # Handle errors
    if not result.success:
        console.print(f"[red]Error:[/red] {result.error}")
        raise typer.Exit(code=2 if strict else 1)

    # Display results table
    if result.diagrams:
        table = Table(show_header=True, header_style="bold")
        table.add_column("Diagram Type")
        table.add_column("Status")
        table.add_column("Nodes")

        for diagram in result.diagrams:
            status = "[green]✅ Generated[/green]" if diagram.is_valid else "[yellow]⚠️ Generated (warnings)[/yellow]"
            table.add_row(
                diagram.diagram_type.value,
                status,
                str(diagram.node_count),
            )

        console.print(table)
        console.print()

        # Show validation warnings
        for diagram in result.diagrams:
            if diagram.validation and diagram.validation.warnings:
                console.print(f"[yellow]Warnings for {diagram.diagram_type.value}:[/yellow]")
                for warning in diagram.validation.warnings:
                    console.print(f"  • {warning}")
                console.print()

        # Output to file if requested
        if output:
            output_content = []
            for diagram in result.diagrams:
                output_content.append(f"## {diagram.diagram_type.value}\n")
                output_content.append(diagram.wrapped_content)
                output_content.append("\n")

            output.write_text("\n".join(output_content), encoding="utf-8")
            console.print(f"[green]✅[/green] Diagrams written to: {output}")
        elif not no_insert and result.sections_updated:
            console.print(f"[green]✅[/green] Diagrams inserted into {resolved_path.name}")
            console.print(f"   Sections updated: {', '.join(result.sections_updated)}")
        elif no_insert:
            # Print diagram content to stdout
            for diagram in result.diagrams:
                console.print(f"\n[bold]## {diagram.diagram_type.value}[/bold]\n")
                console.print(diagram.wrapped_content)
    else:
        console.print("[yellow]No diagrams generated.[/yellow] Check that the spec has User Stories or Key Entities.")
        raise typer.Exit(code=3)


@app.command(name="validate")
def validate_command(
    file: Optional[Path] = typer.Argument(
        None,
        help="Path to file containing Mermaid diagrams",
        exists=False,
    ),
    strict: bool = typer.Option(
        False,
        "--strict",
        "-s",
        help="Use stricter validation rules",
    ),
) -> None:
    """Validate Mermaid diagrams in a file.

    Checks all Mermaid code blocks in the file for syntax errors.

    Examples:
        doit diagram validate spec.md
        doit diagram validate --strict
    """
    import re

    # Resolve file path
    resolved_path = _resolve_file_path(file)
    if not resolved_path:
        console.print("[red]Error:[/red] No file found to validate.")
        raise typer.Exit(code=2)

    if not resolved_path.exists():
        console.print(f"[red]Error:[/red] File not found: {resolved_path}")
        raise typer.Exit(code=2)

    console.print(f"Validating diagrams in: [cyan]{resolved_path}[/cyan]")
    console.print()

    content = resolved_path.read_text(encoding="utf-8")

    # Find all mermaid code blocks
    mermaid_pattern = re.compile(r"```mermaid\s*\n(.*?)\n```", re.DOTALL)
    matches = list(mermaid_pattern.finditer(content))

    if not matches:
        console.print("[yellow]No Mermaid diagrams found in file.[/yellow]")
        raise typer.Exit(code=0)

    from ..services.mermaid_validator import MermaidValidator

    validator = MermaidValidator()
    has_errors = False

    table = Table(show_header=True, header_style="bold")
    table.add_column("Diagram #")
    table.add_column("Type")
    table.add_column("Status")
    table.add_column("Issues")

    for i, match in enumerate(matches, start=1):
        diagram_content = match.group(1)
        result = validator.validate(diagram_content)

        # Determine type
        if "erDiagram" in diagram_content.lower():
            diagram_type = "ER Diagram"
        elif "flowchart" in diagram_content.lower():
            diagram_type = "Flowchart"
        else:
            diagram_type = "Unknown"

        if result.passed and not result.warnings:
            status = "[green]✅ Valid[/green]"
            issues = "None"
        elif result.passed:
            status = "[yellow]⚠️ Warning[/yellow]"
            issues = f"{result.warning_count} warnings"
        else:
            status = "[red]❌ Invalid[/red]"
            issues = f"{result.error_count} errors"
            has_errors = True

        table.add_row(str(i), diagram_type, status, issues)

    console.print(table)

    # Show detailed errors/warnings
    for i, match in enumerate(matches, start=1):
        diagram_content = match.group(1)
        result = validator.validate(diagram_content)

        if result.errors:
            console.print(f"\n[red]Errors in diagram {i}:[/red]")
            for error in result.errors:
                console.print(f"  • {error}")

        if result.warnings:
            console.print(f"\n[yellow]Warnings in diagram {i}:[/yellow]")
            for warning in result.warnings:
                console.print(f"  • {warning}")

    if has_errors:
        console.print("\n[red]Validation failed.[/red]")
        raise typer.Exit(code=1)
    else:
        console.print("\n[green]All diagrams valid.[/green]")
        raise typer.Exit(code=0)


# Export the app for registration
diagram_app = app
