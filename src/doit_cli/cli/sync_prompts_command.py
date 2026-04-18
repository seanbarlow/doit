"""Sync-prompts command for synchronizing agent commands with doit command templates."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from ..exit_codes import ExitCode
from ..models.agent import Agent
from ..models.sync_models import FileOperation, OperationType, SyncResult
from ..services.command_writer import CommandWriter
from ..services.prompt_writer import PromptWriter
from ..services.skill_reader import SkillReader
from ..services.skill_writer import SkillWriter
from ..services.template_reader import TemplateReader

console = Console()

# Type aliases for CLI options
JsonFlag = Annotated[bool, typer.Option("--json", "-j", help="Output results as JSON")]

CheckFlag = Annotated[
    bool, typer.Option("--check", "-c", help="Check sync status without making changes")
]

ForceFlag = Annotated[
    bool, typer.Option("--force", "-f", help="Force sync even if files are up-to-date")
]

AgentOption = Annotated[
    str | None,
    typer.Option("--agent", "-a", help="Target agent(s): copilot (default), claude, or both"),
]

SkillsOption = Annotated[
    bool,
    typer.Option(
        "--skills/--no-skills",
        help=(
            "When targeting Claude, also write Agent-Skills-format directories "
            "to .claude/skills/. Defaults to on so new projects get the April "
            "2026 layout; pass --no-skills to keep only the legacy .claude/commands/ "
            "output."
        ),
    ),
]

def parse_sync_agents(agent_str: str | None) -> list[Agent]:
    """Parse agent string for sync command.

    Defaults to Copilot-only for backward compatibility.

    Args:
        agent_str: Agent string from CLI option.

    Returns:
        List of target agents.

    Raises:
        typer.BadParameter: If invalid agent name provided.
    """
    if not agent_str:
        return [Agent.COPILOT]

    agents = []
    for name in agent_str.lower().split(","):
        name = name.strip()
        if name == "claude":
            agents.append(Agent.CLAUDE)
        elif name == "copilot":
            agents.append(Agent.COPILOT)
        elif name == "both":
            return [Agent.CLAUDE, Agent.COPILOT]
        else:
            raise typer.BadParameter(f"Unknown agent: {name}. Use 'copilot', 'claude', or 'both'")

    return agents


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


def display_sync_result(result: SyncResult, title: str = "Prompt Synchronization Results") -> None:
    """Display sync result with rich formatting.

    Args:
        result: The sync result to display.
        title: Table title.
    """
    if not result.operations:
        console.print("[yellow]No command templates found to sync.[/yellow]")
        return

    # Create table
    table = Table(
        show_header=True,
        header_style="bold cyan",
        title=title,
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
            console.print("[bold green]Commands synchronized successfully[/bold green]")
        else:
            console.print("[green]All commands are up-to-date[/green]")
    else:
        console.print("[bold red]Some commands failed to sync[/bold red]")


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


def _merge_results(results: list[SyncResult]) -> SyncResult:
    """Merge multiple SyncResult objects into one.

    Args:
        results: List of SyncResult objects.

    Returns:
        Combined SyncResult.
    """
    merged = SyncResult()
    for r in results:
        merged.total_commands += r.total_commands
        for op in r.operations:
            merged.add_operation(op)
    return merged


def _check_agent_status(
    templates,
    writer,
    get_path_fn,
) -> SyncResult:
    """Check sync status for a specific agent without making changes.

    Args:
        templates: List of command templates.
        writer: Writer instance (PromptWriter or CommandWriter).
        get_path_fn: Function to get target path from template.

    Returns:
        SyncResult with status information.
    """
    result = SyncResult(total_commands=len(templates))
    for template in templates:
        target_path = get_path_fn(template)

        if not target_path.exists():
            result.add_operation(
                FileOperation(
                    file_path=str(target_path),
                    operation_type=OperationType.FAILED,
                    success=False,
                    message="Missing - needs sync",
                )
            )
        else:
            target_mtime = target_path.stat().st_mtime
            template_mtime = template.modified_at.timestamp()

            if target_mtime < template_mtime:
                result.add_operation(
                    FileOperation(
                        file_path=str(target_path),
                        operation_type=OperationType.UPDATED,
                        success=True,
                        message="Out-of-sync - needs update",
                    )
                )
            else:
                result.add_operation(
                    FileOperation(
                        file_path=str(target_path),
                        operation_type=OperationType.SKIPPED,
                        success=True,
                        message="Up-to-date",
                    )
                )
    return result


def _sync_skills(
    project_root: Path,
    *,
    command_name: str | None,
    force: bool,
    check_only: bool,
) -> SyncResult:
    """Write bundled Agent-Skills-format skills to the project's .claude/skills/.

    Returns a SyncResult describing the per-skill outcome (CREATED for
    first-time writes, UPDATED when the directory already exists, SKIPPED
    in check mode or when the target is up-to-date in a future tighter
    implementation).
    """
    reader = SkillReader()
    skills = reader.scan_bundled_skills()

    if command_name:
        skills = [s for s in skills if s.name == command_name]

    result = SyncResult(total_commands=len(skills))
    writer = SkillWriter(project_root=project_root)

    for skill in skills:
        target_dir = writer.skills_dir / skill.directory.name
        if check_only:
            op_type = OperationType.SKIPPED if target_dir.exists() else OperationType.FAILED
            result.add_operation(
                FileOperation(
                    file_path=str(target_dir),
                    operation_type=op_type,
                    success=target_dir.exists(),
                    message="Present" if target_dir.exists() else "Missing — needs sync",
                )
            )
            continue

        if target_dir.exists() and not force:
            result.add_operation(
                FileOperation(
                    file_path=str(target_dir),
                    operation_type=OperationType.SKIPPED,
                    success=True,
                    message="Already present (use --force to overwrite)",
                )
            )
            continue

        write_result = writer.write_skill(skill, overwrite=True)
        result.add_operation(
            FileOperation(
                file_path=str(write_result.target_dir),
                operation_type=(
                    OperationType.UPDATED
                    if write_result.was_overwrite
                    else OperationType.CREATED
                ),
                success=True,
                message=f"Wrote {len(write_result.files_written)} files",
            )
        )

    return result


def sync_prompts_command(
    command_name: Annotated[
        str | None, typer.Argument(help="Specific command to sync (e.g., 'doit.checkin')")
    ] = None,
    agent: AgentOption = None,
    skills: SkillsOption = True,
    check: CheckFlag = False,
    force: ForceFlag = False,
    json_output: JsonFlag = False,
    path: Annotated[Path, typer.Option("--path", "-p", help="Project directory path")] = Path(),
) -> None:
    """Synchronize agent commands with doit command templates.

    Reads command templates from .doit/templates/commands/ and generates
    corresponding files for the specified agent(s). Defaults to Copilot only.

    For Copilot: writes to .github/prompts/ as doit.<name>.prompt.md
    For Claude: writes to .claude/commands/ as doit.<name>.md

    Examples:
        doit sync-prompts                          # Sync Copilot prompts
        doit sync-prompts --agent claude           # Sync Claude commands
        doit sync-prompts --agent both             # Sync both agents
        doit sync-prompts doit.checkin             # Sync specific command
        doit sync-prompts --check                  # Check sync status only
        doit sync-prompts --force                  # Force re-sync all
        doit sync-prompts --json                   # Output as JSON
    """
    project_root = path.resolve()

    # Parse target agents
    try:
        target_agents = parse_sync_agents(agent)
    except typer.BadParameter as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=ExitCode.FAILURE) from e

    # Initialize services
    reader = TemplateReader(project_root=project_root)
    prompt_writer = PromptWriter(project_root=project_root)
    command_writer = CommandWriter(project_root=project_root)

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
        raise typer.Exit(code=ExitCode.FAILURE)

    all_results = []

    for target_agent in target_agents:
        if check:
            # Check mode - report status without making changes
            if target_agent == Agent.COPILOT:
                result = _check_agent_status(
                    templates, prompt_writer, prompt_writer.get_prompt_path
                )
            else:
                result = _check_agent_status(
                    templates, command_writer, command_writer.get_command_path
                )
        else:
            # Perform actual sync
            if target_agent == Agent.COPILOT:
                result = prompt_writer.write_prompts(templates, force=force)
            else:
                result = command_writer.write_commands(templates, force=force)

        if not json_output and len(target_agents) > 1:
            display_sync_result(result, title=f"{target_agent.display_name} Sync Results")

        all_results.append(result)

        # When syncing Claude, also write Agent-Skills-format directories
        # to .claude/skills/ unless the caller opted out with --no-skills.
        if target_agent == Agent.CLAUDE and skills:
            skill_result = _sync_skills(
                project_root,
                command_name=command_name,
                force=force,
                check_only=check,
            )
            if not json_output and len(target_agents) > 1:
                display_sync_result(skill_result, title="Claude Skills Sync Results")
            all_results.append(skill_result)

    # Display combined results. We merge whenever the loop produced more
    # than one SyncResult — that happens either with multi-agent sync or
    # with single-Claude-plus-skills sync.
    if len(all_results) == 1:
        combined = all_results[0]
    else:
        combined = _merge_results(all_results)

    if json_output:
        display_json_result(combined)
    else:
        display_sync_result(combined)

    # Exit with appropriate code
    if not combined.success:
        raise typer.Exit(code=ExitCode.FAILURE)
