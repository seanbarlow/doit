"""Update command for updating doit project templates and commands."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from ..models.agent import Agent
from .init_command import display_init_result, parse_agent_string, run_init

console = Console()


def update_command(
    path: Annotated[
        Path,
        typer.Argument(default=..., help="Project directory path (use '.' for current directory)"),
    ] = Path(),
    agent: Annotated[
        str | None,
        typer.Option("--agent", "-a", help="Target agent(s): claude, copilot, or claude,copilot"),
    ] = None,
    force: Annotated[
        bool, typer.Option("--force", "-f", help="Overwrite all files including memory files")
    ] = False,
    yes: Annotated[bool, typer.Option("--yes", "-y", help="Skip confirmation prompts")] = True,
) -> None:
    """Update doit templates and commands to the latest version.

    This is a convenience wrapper for 'doit init --update'. It updates
    command templates for all configured agents while preserving
    user-customized files (constitution, roadmap, etc.).

    Use --force to also overwrite memory files.

    Examples:
        doit update                      # Update current directory
        doit update . --agent claude     # Update Claude only
        doit update . --force            # Force overwrite everything
    """
    agents = None
    if agent:
        try:
            agents = parse_agent_string(agent)
        except typer.BadParameter as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1) from e

    result = run_init(
        path=path,
        agents=agents,
        update=True,
        force=force,
        yes=yes,
    )
    display_init_result(result, agents or result.project.agents or [Agent.CLAUDE])
    if not result.success:
        raise typer.Exit(1)
