"""CLI command for constitution management.

This module provides the constitution command and subcommands
for the doit CLI tool.
"""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..services.cleanup_service import CleanupService

app = typer.Typer(help="Constitution management commands")
console = Console()


@app.callback()
def main() -> None:
    """Constitution management commands.

    Use subcommands to manage the project constitution:

    Examples:
        doit constitution cleanup           # Separate tech-stack from constitution
        doit constitution cleanup --dry-run # Preview what would be changed
    """
    pass


@app.command("cleanup")
def cleanup(
    path: Optional[Path] = typer.Argument(
        None,
        help="Project root directory (default: current directory)",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        "-n",
        help="Preview changes without modifying files",
    ),
    merge: bool = typer.Option(
        False,
        "--merge",
        "-m",
        help="Merge with existing tech-stack.md if it exists",
    ),
    yes: bool = typer.Option(
        False,
        "--yes",
        "-y",
        help="Skip confirmation prompts",
    ),
) -> None:
    """Separate tech-stack content from constitution.md.

    Analyzes constitution.md to identify tech-stack sections (Tech Stack,
    Infrastructure, Deployment) and extracts them to a separate tech-stack.md
    file with proper cross-references.

    A backup of the original constitution.md is created before any changes.

    Examples:
        doit constitution cleanup              # Clean up current project
        doit constitution cleanup --dry-run    # Preview what would change
        doit constitution cleanup --merge      # Merge with existing tech-stack.md
        doit constitution cleanup /path/to/project
    """
    project_root = path or Path.cwd()

    # Validate project directory
    memory_dir = project_root / ".doit" / "memory"
    if not memory_dir.exists():
        console.print(
            f"[red]Error:[/red] No .doit/memory directory found at {project_root}"
        )
        console.print("Run [cyan]doit init[/cyan] to initialize the project first.")
        raise typer.Exit(code=1)

    service = CleanupService(project_root)
    constitution_path = service.constitution_path

    if not constitution_path.exists():
        console.print(
            f"[red]Error:[/red] Constitution not found at {constitution_path}"
        )
        raise typer.Exit(code=1)

    # Analyze content first
    console.print(f"\n[bold]Analyzing[/bold] {constitution_path.relative_to(project_root)}...")
    analysis = service.analyze()

    if not analysis.has_tech_content:
        console.print(
            "\n[green]✓[/green] No tech-stack sections found in constitution.md"
        )
        console.print("Constitution is already clean - no changes needed.")
        raise typer.Exit(code=0)

    # Display what will be changed
    _display_analysis(analysis)

    if dry_run:
        console.print("\n[yellow]Dry run mode[/yellow] - no changes made.")
        raise typer.Exit(code=0)

    # Check for existing tech-stack.md
    if service.tech_stack_path.exists() and not merge:
        console.print(
            f"\n[yellow]Warning:[/yellow] {service.tech_stack_path.name} already exists."
        )
        console.print("Use [cyan]--merge[/cyan] to combine content, or remove the existing file.")
        raise typer.Exit(code=1)

    # Confirm before proceeding
    if not yes:
        console.print()
        confirmed = typer.confirm("Proceed with cleanup?", default=True)
        if not confirmed:
            console.print("[yellow]Cancelled.[/yellow]")
            raise typer.Exit(code=0)

    # Perform cleanup
    console.print("\n[bold]Performing cleanup...[/bold]")
    result = service.cleanup(dry_run=False, merge_existing=merge)

    if result.error_message:
        console.print(f"\n[red]Error:[/red] {result.error_message}")
        raise typer.Exit(code=1)

    # Display results
    _display_result(result, project_root)


def _display_analysis(analysis) -> None:
    """Display analysis results in a formatted table."""
    table = Table(title="Content Analysis", show_header=True, header_style="bold")
    table.add_column("Category", style="cyan")
    table.add_column("Sections")
    table.add_column("Action")

    if analysis.tech_sections:
        sections = ", ".join(analysis.tech_sections.keys())
        table.add_row(
            "Tech Stack",
            sections,
            "[yellow]→ Extract to tech-stack.md[/yellow]",
        )

    if analysis.preserved_sections:
        sections = ", ".join(analysis.preserved_sections.keys())
        table.add_row(
            "Preserved",
            sections,
            "[green]Keep in constitution.md[/green]",
        )

    if analysis.unclear_sections:
        sections = ", ".join(analysis.unclear_sections.keys())
        table.add_row(
            "Unclear",
            sections,
            "[dim]Keep in constitution.md (review manually)[/dim]",
        )

    console.print()
    console.print(table)


def _display_result(result, project_root: Path) -> None:
    """Display cleanup results."""
    console.print()

    if result.backup_path:
        rel_backup = result.backup_path.relative_to(project_root)
        console.print(f"[green]✓[/green] Created backup: {rel_backup}")

    if result.tech_stack_created:
        if result.tech_stack_merged:
            console.print("[green]✓[/green] Merged content into tech-stack.md")
        else:
            console.print("[green]✓[/green] Created tech-stack.md")

    if result.extracted_sections:
        console.print(
            f"[green]✓[/green] Extracted {len(result.extracted_sections)} section(s): "
            f"{', '.join(result.extracted_sections)}"
        )

    if result.preserved_sections:
        console.print(
            f"[green]✓[/green] Preserved {len(result.preserved_sections)} section(s) in constitution.md"
        )

    # Size comparison
    if result.constitution_size_before and result.constitution_size_after:
        reduction = result.constitution_size_before - result.constitution_size_after
        percent = (reduction / result.constitution_size_before) * 100
        console.print(
            f"\n[dim]Constitution size: {result.constitution_size_before} → "
            f"{result.constitution_size_after} bytes ({percent:.1f}% reduction)[/dim]"
        )

    console.print(
        Panel(
            "[green]Constitution cleanup complete![/green]\n\n"
            "Both files now contain cross-references to each other.",
            title="Success",
            border_style="green",
        )
    )
