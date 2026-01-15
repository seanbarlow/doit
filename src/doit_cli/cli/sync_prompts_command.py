"""Sync-prompts command for synchronizing GitHub Copilot prompts with doit commands."""

import json
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.table import Table

from ..models.sync_models import OperationType, SyncResult
from ..services.prompt_writer import PromptWriter
from ..services.template_reader import TemplateReader


console = Console()

# Type aliases for CLI options
JsonFlag = Annotated[
    bool,
    typer.Option(
        "--json", "-j",
        help="Output results as JSON"
    )
]

CheckFlag = Annotated[
    bool,
    typer.Option(
        "--check", "-c",
        help="Check sync status without making changes"
    )
]

ForceFlag = Annotated[
    bool,
    typer.Option(
        "--force", "-f",
        help="Force sync even if files are up-to-date"
    )
]


def get_operation_style(operation_type: OperationType) -> str:
    """Get rich style for operation type."""
    styles = {
        OperationType.CREATED: "green",
        OperationType.UPDATED: "yellow",
        OperationType.SKIPPED: "dim",
        OperationType.FAILED: "red",
    }
    return styles.get(operation_type, "white")


def get_operation_symbol(operation_type: OperationType) -> str:
    """Get symbol for operation type."""
    symbols = {
        OperationType.CREATED: "+",
        OperationType.UPDATED: "~",
        OperationType.SKIPPED: "-",
        OperationType.FAILED: "✗",
    }
    return symbols.get(operation_type, "?")


def display_sync_result(result: SyncResult) -> None:
    """Display sync result with rich formatting.

    Args:
        result: The sync result to display.
    """
    if not result.operations:
        console.print("[yellow]No command templates found to sync.[/yellow]")
        return

    # Create table
    table = Table(
        show_header=True,
        header_style="bold cyan",
        title="Prompt Synchronization Results",
    )
    table.add_column("Status", width=10, justify="center")
    table.add_column("File", width=40)
    table.add_column("Message")

    for op in result.operations:
        style = get_operation_style(op.operation_type)
        symbol = get_operation_symbol(op.operation_type)
        status_text = f"[{style}]{symbol} {op.operation_type.value.upper()}[/{style}]"

        # Show just the filename, not full path
        filename = Path(op.file_path).name

        table.add_row(
            status_text,
            filename,
            op.message,
        )

    console.print()
    console.print(table)

    # Summary
    console.print()
    console.print(
        f"[bold]Summary:[/bold] "
        f"{result.total_commands} commands, "
        f"[green]{result.synced} synced[/green], "
        f"[dim]{result.skipped} skipped[/dim], "
        f"[red]{result.failed} failed[/red]"
    )

    # Final status
    console.print()
    if result.success:
        if result.synced > 0:
            console.print("[bold green]Prompts synchronized successfully[/bold green]")
        else:
            console.print("[green]All prompts are up-to-date[/green]")
    else:
        console.print("[bold red]Some prompts failed to sync[/bold red]")


def display_json_result(result: SyncResult) -> None:
    """Display sync result as JSON.

    Args:
        result: The sync result to display.
    """
    output = {
        "total_commands": result.total_commands,
        "synced": result.synced,
        "skipped": result.skipped,
        "failed": result.failed,
        "success": result.success,
        "operations": [
            {
                "file_path": op.file_path,
                "operation_type": op.operation_type.value,
                "success": op.success,
                "message": op.message,
            }
            for op in result.operations
        ],
    }
    # Use print() instead of console.print() to avoid Rich's line wrapping
    print(json.dumps(output, indent=2))


def sync_prompts_command(
    command_name: Annotated[
        Optional[str],
        typer.Argument(
            help="Specific command to sync (e.g., 'doit.checkin')"
        )
    ] = None,
    check: CheckFlag = False,
    force: ForceFlag = False,
    json_output: JsonFlag = False,
    path: Annotated[
        Path,
        typer.Option(
            "--path", "-p",
            help="Project directory path"
        )
    ] = Path("."),
) -> None:
    """Synchronize GitHub Copilot prompts with doit command templates.

    Reads command templates from .doit/templates/commands/ and generates
    corresponding prompt files in .github/prompts/ with naming convention
    doit.<name>.prompt.md.

    Examples:
        doit sync-prompts                     # Sync all commands
        doit sync-prompts doit.checkin        # Sync specific command
        doit sync-prompts --check             # Check sync status only
        doit sync-prompts --force             # Force re-sync all
        doit sync-prompts --json              # Output as JSON
    """
    project_root = path.resolve()

    # Initialize services
    reader = TemplateReader(project_root=project_root)
    writer = PromptWriter(project_root=project_root)

    # Read templates
    templates = reader.scan_templates(filter_name=command_name)

    if not templates:
        if command_name:
            msg = f"Command template '{command_name}' not found"
        else:
            msg = "No command templates found in .doit/templates/commands/"

        if json_output:
            console.print(json.dumps({"error": msg}))
        else:
            console.print(f"[red]Error:[/red] {msg}")
        raise typer.Exit(1)

    # Check mode - just report status without making changes
    if check:
        result = SyncResult(total_commands=len(templates))
        for template in templates:
            prompt_path = writer.get_prompt_path(template)

            if not prompt_path.exists():
                from ..models.sync_models import FileOperation
                result.add_operation(FileOperation(
                    file_path=str(prompt_path),
                    operation_type=OperationType.FAILED,
                    success=False,
                    message="Missing - needs sync",
                ))
            else:
                prompt_mtime = prompt_path.stat().st_mtime
                template_mtime = template.modified_at.timestamp()

                if prompt_mtime < template_mtime:
                    from ..models.sync_models import FileOperation
                    result.add_operation(FileOperation(
                        file_path=str(prompt_path),
                        operation_type=OperationType.UPDATED,
                        success=True,
                        message="Out-of-sync - needs update",
                    ))
                else:
                    from ..models.sync_models import FileOperation
                    result.add_operation(FileOperation(
                        file_path=str(prompt_path),
                        operation_type=OperationType.SKIPPED,
                        success=True,
                        message="Up-to-date",
                    ))
    else:
        # Perform actual sync
        result = writer.write_prompts(templates, force=force)

    # Display results
    if json_output:
        display_json_result(result)
    else:
        display_sync_result(result)

    # Exit with appropriate code
    if not result.success:
        raise typer.Exit(1)
