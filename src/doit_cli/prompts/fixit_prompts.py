"""Interactive prompts for fixit workflow.

This module provides Rich-based interactive prompts
for the bug-fix workflow user interactions.
"""

from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.table import Table

from ..models.fixit_models import (
    FixPhase,
    FixPlan,
    FixWorkflow,
    GitHubIssue,
    InvestigationFinding,
)

console = Console()


# =============================================================================
# Issue Selection Prompts
# =============================================================================


def prompt_select_issue(bugs: list[GitHubIssue]) -> Optional[GitHubIssue]:
    """Display bugs and prompt user to select one.

    Args:
        bugs: List of GitHubIssue objects to choose from.

    Returns:
        Selected GitHubIssue or None if cancelled.
    """
    if not bugs:
        return None

    # Display table of bugs
    table = Table(title="Open Bugs", show_header=True)
    table.add_column("#", style="cyan", width=4)
    table.add_column("Issue", style="cyan", width=6)
    table.add_column("Title", style="white")
    table.add_column("Labels", style="dim")

    for idx, bug in enumerate(bugs, 1):
        labels_str = ", ".join(bug.labels[:3]) if bug.labels else ""
        if len(bug.labels) > 3:
            labels_str += "..."
        table.add_row(str(idx), f"#{bug.number}", bug.title[:60], labels_str)

    console.print(table)
    console.print()

    # Prompt for selection
    while True:
        try:
            choice = IntPrompt.ask(
                "Select bug number to fix (or 0 to cancel)",
                default=0,
            )
            if choice == 0:
                return None
            if 1 <= choice <= len(bugs):
                return bugs[choice - 1]
            console.print(f"[red]Please select a number between 1 and {len(bugs)}[/red]")
        except KeyboardInterrupt:
            return None


# =============================================================================
# Workflow Display Functions
# =============================================================================


def display_workflow_started(workflow: FixWorkflow, issue_id: int) -> None:
    """Display confirmation that workflow has started.

    Args:
        workflow: The started FixWorkflow.
        issue_id: GitHub issue number.
    """
    console.print()
    console.print(
        Panel(
            f"[green]Workflow started for issue [cyan]#{issue_id}[/cyan][/green]\n\n"
            f"[dim]Branch:[/dim] [cyan]{workflow.branch_name}[/cyan]\n"
            f"[dim]Phase:[/dim] [yellow]{workflow.phase.value}[/yellow]",
            title="Bug Fix Workflow",
            border_style="green",
        )
    )


def display_workflow_status(workflow: FixWorkflow) -> None:
    """Display detailed workflow status.

    Args:
        workflow: The FixWorkflow to display.
    """
    phase_style = _get_phase_style(workflow.phase)

    # Build phase progress indicator
    phases = [
        FixPhase.INITIALIZED,
        FixPhase.INVESTIGATING,
        FixPhase.PLANNING,
        FixPhase.REVIEWING,
        FixPhase.APPROVED,
        FixPhase.IMPLEMENTING,
        FixPhase.COMPLETED,
    ]

    progress_parts = []
    current_found = False
    for phase in phases:
        if phase == workflow.phase:
            progress_parts.append(f"[{phase_style}]{phase.value}[/{phase_style}]")
            current_found = True
        elif not current_found:
            progress_parts.append(f"[green]{phase.value}[/green]")
        else:
            progress_parts.append(f"[dim]{phase.value}[/dim]")

    progress_line = " → ".join(progress_parts)

    console.print()
    console.print(
        Panel(
            f"[dim]Issue:[/dim] [cyan]#{workflow.issue_id}[/cyan]\n"
            f"[dim]Branch:[/dim] [white]{workflow.branch_name}[/white]\n"
            f"[dim]Started:[/dim] {workflow.started_at.strftime('%Y-%m-%d %H:%M')}\n"
            f"[dim]Updated:[/dim] {workflow.updated_at.strftime('%Y-%m-%d %H:%M')}\n\n"
            f"[dim]Progress:[/dim]\n{progress_line}",
            title=f"Fixit Workflow: {workflow.id}",
            border_style=phase_style,
        )
    )


def display_investigation_findings(findings: list[InvestigationFinding]) -> None:
    """Display investigation findings.

    Args:
        findings: List of findings to display.
    """
    if not findings:
        console.print("[yellow]No findings recorded yet.[/yellow]")
        return

    table = Table(title="Investigation Findings")
    table.add_column("Type", style="cyan", width=15)
    table.add_column("Description", style="white")
    table.add_column("Location", style="dim")

    for finding in findings:
        location = ""
        if finding.file_path:
            location = finding.file_path
            if finding.line_number:
                location += f":{finding.line_number}"

        table.add_row(
            finding.finding_type.value,
            finding.description[:50] + "..." if len(finding.description) > 50 else finding.description,
            location,
        )

    console.print(table)


def display_fix_plan(plan: FixPlan) -> None:
    """Display fix plan details.

    Args:
        plan: The FixPlan to display.
    """
    # Status style
    status_styles = {
        "draft": "dim",
        "pending_review": "yellow",
        "revision_needed": "red",
        "approved": "green",
    }
    status_style = status_styles.get(plan.status.value, "white")

    # Risk level style
    risk_styles = {
        "low": "green",
        "medium": "yellow",
        "high": "red",
    }
    risk_style = risk_styles.get(plan.risk_level.value, "white")

    # Build plan content
    content = (
        f"[dim]Plan ID:[/dim] {plan.id}\n"
        f"[dim]Status:[/dim] [{status_style}]{plan.status.value}[/{status_style}]\n"
        f"[dim]Risk Level:[/dim] [{risk_style}]{plan.risk_level.value}[/{risk_style}]\n\n"
        f"[cyan]Root Cause:[/cyan]\n{plan.root_cause}\n\n"
        f"[cyan]Proposed Solution:[/cyan]\n{plan.proposed_solution}"
    )

    console.print(
        Panel(
            content,
            title="Fix Plan",
            border_style=status_style,
        )
    )

    # Display affected files
    if plan.affected_files:
        table = Table(title="Affected Files")
        table.add_column("File", style="cyan")
        table.add_column("Change", style="dim", width=10)
        table.add_column("Description", style="white")

        for fc in plan.affected_files:
            table.add_row(
                fc.file_path,
                fc.change_type.value,
                fc.description[:50] + "..." if len(fc.description) > 50 else fc.description,
            )

        console.print(table)


# =============================================================================
# Confirmation Prompts
# =============================================================================


def confirm_start_workflow(issue: GitHubIssue) -> bool:
    """Confirm starting a workflow for an issue.

    Args:
        issue: The GitHub issue.

    Returns:
        True if confirmed, False otherwise.
    """
    console.print()
    console.print(
        Panel(
            f"[cyan]#{issue.number}[/cyan] {issue.title}\n\n"
            f"[dim]{issue.body[:200]}{'...' if len(issue.body) > 200 else ''}[/dim]",
            title="Issue Details",
            border_style="cyan",
        )
    )
    console.print()

    return Confirm.ask("Start fix workflow for this issue?", default=True)


def confirm_cancel_workflow(issue_id: int) -> bool:
    """Confirm cancelling a workflow.

    Args:
        issue_id: GitHub issue number.

    Returns:
        True if confirmed, False otherwise.
    """
    return Confirm.ask(
        f"[yellow]Cancel workflow for issue #{issue_id}?[/yellow]",
        default=False,
    )


def confirm_complete_workflow(issue_id: int, close_issue: bool = True) -> bool:
    """Confirm completing a workflow.

    Args:
        issue_id: GitHub issue number.
        close_issue: Whether the issue will be closed.

    Returns:
        True if confirmed, False otherwise.
    """
    msg = f"Complete workflow for issue #{issue_id}?"
    if close_issue:
        msg += " (Issue will be closed)"

    return Confirm.ask(msg, default=True)


# =============================================================================
# Input Prompts
# =============================================================================


def prompt_branch_name(default: str) -> str:
    """Prompt for custom branch name.

    Args:
        default: Default branch name.

    Returns:
        Branch name (custom or default).
    """
    return Prompt.ask("Branch name", default=default)


def prompt_finding_description() -> str:
    """Prompt for a finding description.

    Returns:
        Finding description.
    """
    return Prompt.ask("Describe the finding")


def prompt_root_cause() -> str:
    """Prompt for root cause description.

    Returns:
        Root cause description.
    """
    return Prompt.ask("Describe the root cause")


# =============================================================================
# Helper Functions
# =============================================================================


def _get_phase_style(phase: FixPhase) -> str:
    """Get Rich style for a phase."""
    styles = {
        FixPhase.INITIALIZED: "dim",
        FixPhase.INVESTIGATING: "yellow",
        FixPhase.PLANNING: "yellow",
        FixPhase.REVIEWING: "cyan",
        FixPhase.APPROVED: "green",
        FixPhase.IMPLEMENTING: "blue",
        FixPhase.COMPLETED: "green bold",
        FixPhase.CANCELLED: "red dim",
    }
    return styles.get(phase, "white")
