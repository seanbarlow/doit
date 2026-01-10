"""Verify command for checking doit project setup."""

import json
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..models.agent import Agent
from ..models.project import Project
from ..models.results import VerifyResult, VerifyStatus
from ..services.validator import Validator


console = Console()

# Type aliases for CLI options
JsonFlag = Annotated[
    bool,
    typer.Option(
        "--json", "-j",
        help="Output results as JSON"
    )
]

AgentOption = Annotated[
    Optional[str],
    typer.Option(
        "--agent", "-a",
        help="Specific agent to check: claude, copilot, or both"
    )
]


def parse_agent_string(agent_str: str) -> list[Agent]:
    """Parse agent string into list of Agent enums.

    Args:
        agent_str: Comma-separated agent names

    Returns:
        List of Agent enums
    """
    agents = []
    for name in agent_str.lower().split(","):
        name = name.strip()
        if name == "claude":
            agents.append(Agent.CLAUDE)
        elif name == "copilot":
            agents.append(Agent.COPILOT)
        else:
            raise typer.BadParameter(
                f"Unknown agent: {name}. Use 'claude', 'copilot', or 'claude,copilot'"
            )
    return agents


def get_status_style(status: VerifyStatus) -> str:
    """Get rich style for verification status."""
    if status == VerifyStatus.PASS:
        return "green"
    elif status == VerifyStatus.WARN:
        return "yellow"
    else:  # FAIL
        return "red"


def get_status_symbol(status: VerifyStatus) -> str:
    """Get symbol for verification status."""
    if status == VerifyStatus.PASS:
        return "✓"
    elif status == VerifyStatus.WARN:
        return "!"
    else:  # FAIL
        return "✗"


def display_verify_result(result: VerifyResult) -> None:
    """Display verification result with rich formatting.

    Args:
        result: The verification result to display
    """
    # Create table
    table = Table(
        show_header=True,
        header_style="bold cyan",
        title="Project Verification Results",
    )
    table.add_column("Status", width=8, justify="center")
    table.add_column("Check", width=20)
    table.add_column("Message")

    for check in result.checks:
        style = get_status_style(check.status)
        symbol = get_status_symbol(check.status)
        status_text = f"[{style}]{symbol} {check.status.value.upper()}[/{style}]"

        table.add_row(
            status_text,
            check.name,
            check.message,
        )

    console.print()
    console.print(table)

    # Summary
    console.print()
    console.print(f"[bold]Summary:[/bold] {result.summary}")

    # Show suggestions if there are warnings or failures
    suggestions = [
        c.suggestion for c in result.checks
        if c.suggestion and c.status != VerifyStatus.PASS
    ]

    if suggestions:
        console.print()
        console.print(
            Panel(
                "\n".join(f"• {s}" for s in suggestions),
                title="[yellow]Suggestions[/yellow]",
                border_style="yellow",
            )
        )

    # Final status
    console.print()
    if result.passed:
        if result.has_warnings:
            console.print("[yellow]Project setup complete with warnings[/yellow]")
        else:
            console.print("[bold green]Project setup verified successfully[/bold green]")
    else:
        console.print("[bold red]Project setup has issues that need attention[/bold red]")


def display_json_result(result: VerifyResult) -> None:
    """Display verification result as JSON.

    Args:
        result: The verification result to display
    """
    output = result.to_dict()
    console.print(json.dumps(output, indent=2, default=str))


def verify_command(
    path: Annotated[
        Path,
        typer.Argument(
            default=...,
            help="Project directory path (use '.' for current directory)"
        )
    ] = Path("."),
    agent: AgentOption = None,
    json_output: JsonFlag = False,
) -> None:
    """Verify doit project setup and report status.

    Checks for:
    - .doit/ folder structure
    - Agent command directories
    - Command template files
    - Project constitution and roadmap
    - Copilot-specific configuration (if applicable)

    Examples:
        doit verify .                    # Verify current directory
        doit verify . --agent claude     # Check only Claude setup
        doit verify . --json             # Output as JSON
    """
    # Parse agent string if provided
    agents = None
    if agent:
        try:
            agents = parse_agent_string(agent)
        except typer.BadParameter as e:
            if json_output:
                console.print(json.dumps({"error": str(e)}))
            else:
                console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

    # Create project and validator
    project = Project(path=path.resolve())
    validator = Validator(project)

    # Run verification
    result = validator.run_all_checks(agents=agents)

    # Display results
    if json_output:
        display_json_result(result)
    else:
        display_verify_result(result)

    # Exit with appropriate code
    if not result.passed:
        raise typer.Exit(1)
