"""CLI command for constitution management.

This module provides the constitution command and subcommands
for the doit CLI tool.
"""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..exit_codes import ExitCode
from ..services.cleanup_service import CleanupService
from ..services.constitution_enricher import (
    EnrichmentAction,
    enrich_constitution,
)

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
    path: Path | None = typer.Argument(
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
        console.print(f"[red]Error:[/red] No .doit/memory directory found at {project_root}")
        console.print("Run [cyan]doit init[/cyan] to initialize the project first.")
        raise typer.Exit(code=ExitCode.FAILURE)

    service = CleanupService(project_root)
    constitution_path = service.constitution_path

    if not constitution_path.exists():
        console.print(f"[red]Error:[/red] Constitution not found at {constitution_path}")
        raise typer.Exit(code=ExitCode.FAILURE)

    # Analyze content first
    console.print(f"\n[bold]Analyzing[/bold] {constitution_path.relative_to(project_root)}...")
    analysis = service.analyze()

    if not analysis.has_tech_content:
        console.print("\n[green]✓[/green] No tech-stack sections found in constitution.md")
        console.print("Constitution is already clean - no changes needed.")
        raise typer.Exit(code=ExitCode.SUCCESS)

    # Display what will be changed
    _display_analysis(analysis)

    if dry_run:
        console.print("\n[yellow]Dry run mode[/yellow] - no changes made.")
        raise typer.Exit(code=ExitCode.SUCCESS)

    # Check for existing tech-stack.md
    if service.tech_stack_path.exists() and not merge:
        console.print(f"\n[yellow]Warning:[/yellow] {service.tech_stack_path.name} already exists.")
        console.print("Use [cyan]--merge[/cyan] to combine content, or remove the existing file.")
        raise typer.Exit(code=ExitCode.FAILURE)

    # Confirm before proceeding
    if not yes:
        console.print()
        confirmed = typer.confirm("Proceed with cleanup?", default=True)
        if not confirmed:
            console.print("[yellow]Cancelled.[/yellow]")
            raise typer.Exit(code=ExitCode.SUCCESS)

    # Perform cleanup
    console.print("\n[bold]Performing cleanup...[/bold]")
    result = service.cleanup(dry_run=False, merge_existing=merge)

    if result.error_message:
        console.print(f"\n[red]Error:[/red] {result.error_message}")
        raise typer.Exit(code=ExitCode.FAILURE)

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


@app.command("enrich")
def enrich(
    path: Path | None = typer.Argument(
        None,
        help="Project root directory (default: current directory)",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        "-j",
        help="Emit the enrichment result as JSON",
    ),
) -> None:
    """Infer real values for placeholder frontmatter in constitution.md.

    Reads ``.doit/memory/constitution.md``, detects fields whose values
    still match the placeholder sentinels written by ``doit update`` /
    ``doit init``, and replaces each with a concrete value inferred from
    the constitution body and the project directory name.

    This is a deterministic, LLM-free first pass. The
    ``/doit.constitution`` skill can invoke it as a pre-step and then
    prompt the user about any remaining unresolved fields.

    The body (every byte after the closing ``---\\n``) is preserved
    byte-for-byte.

    Exit codes:
      0 = success (ENRICHED or NO_OP)
      1 = enrichment is partial — some fields remain as placeholders
      2 = validation / file error

    Examples:
        doit constitution enrich
        doit constitution enrich /path/to/project
        doit constitution enrich --json
    """

    project_root = path or Path.cwd()
    target = project_root / ".doit" / "memory" / "constitution.md"

    result = enrich_constitution(target)

    if json_output:
        typer.echo(
            json.dumps(
                {
                    "path": str(result.path),
                    "action": result.action.value,
                    "enriched_fields": list(result.enriched_fields),
                    "unresolved_fields": list(result.unresolved_fields),
                    "error": str(result.error) if result.error else None,
                },
                indent=2,
            )
        )
    else:
        if result.action is EnrichmentAction.NO_OP:
            console.print(
                "[green]Nothing to enrich:[/green] no placeholder frontmatter "
                "detected in .doit/memory/constitution.md."
            )
        elif result.action is EnrichmentAction.ERROR:
            console.print(
                f"[red]Enrichment failed:[/red] {result.error}"
            )
        else:
            table = Table(
                show_header=True,
                header_style="bold cyan",
                title="Constitution enrichment",
            )
            table.add_column("Status", width=10)
            table.add_column("Field", width=16)
            table.add_column("Note")
            for key in result.enriched_fields:
                table.add_row(
                    "[green]✓ filled[/green]",
                    key,
                    "replaced placeholder with inferred value",
                )
            for key in result.unresolved_fields:
                table.add_row(
                    "[yellow]! unresolved[/yellow]",
                    key,
                    "low-confidence inference; placeholder retained",
                )
            console.print(table)
            if result.unresolved_fields:
                console.print(
                    "[yellow]Unresolved fields need human input:[/yellow] "
                    + ", ".join(result.unresolved_fields)
                )

    if result.action is EnrichmentAction.ERROR:
        raise typer.Exit(code=ExitCode.VALIDATION_ERROR)
    if result.action is EnrichmentAction.PARTIAL:
        raise typer.Exit(code=ExitCode.FAILURE)
