"""CLI command for bug-fix workflow.

This module provides the fixit command and subcommands
for the doit CLI tool.
"""

from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..models.fixit_models import FixPhase
from ..prompts.fixit_prompts import (
    display_workflow_started,
    display_workflow_status,
    prompt_select_issue,
)
from ..services.fixit_service import FixitService, FixitServiceError
from ..services.github_service import GitHubServiceError

app = typer.Typer(help="Bug-fix workflow commands")
console = Console()


@app.callback()
def main() -> None:
    """Bug-fix workflow commands.

    Use subcommands to manage bug-fix workflows:

    Examples:
        doit fixit start 123    # Start workflow for issue #123
        doit fixit start        # Select from open bugs interactively
        doit fixit list         # List all open bugs
        doit fixit status       # Show current workflow status
    """
    pass


@app.command("start")
def start(
    issue_id: Optional[int] = typer.Argument(
        None,
        help="GitHub issue number to fix",
    ),
    resume: bool = typer.Option(
        False, "--resume", "-r", help="Resume existing workflow"
    ),
    manual: bool = typer.Option(
        False, "--manual", "-m", help="Skip automatic investigation"
    ),
    branch: Optional[str] = typer.Option(
        None, "--branch", "-b", help="Custom branch name"
    ),
) -> None:
    """Start or continue a bug-fix workflow.

    If no ISSUE_ID is provided, shows a list of open bugs to select from.
    If a workflow already exists for the issue, use --resume to continue it.

    Examples:
        doit fixit start 123          # Start workflow for issue #123
        doit fixit start              # Select from open bugs
        doit fixit start 123 --resume # Resume existing workflow
    """
    try:
        service = FixitService()
    except GitHubServiceError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=2)

    # Check GitHub availability
    if not service.is_github_available():
        console.print(
            "[yellow]Warning:[/yellow] GitHub API is not available. "
            "Some features may not work."
        )

    # If no issue_id, prompt for selection
    if issue_id is None:
        bugs = service.list_bugs()
        if not bugs:
            console.print("[yellow]No open bugs found.[/yellow]")
            console.print("Use [cyan]doit fixit start <issue_id>[/cyan] to start a workflow.")
            raise typer.Exit(code=0)

        selected = prompt_select_issue(bugs)
        if selected is None:
            console.print("[yellow]No issue selected.[/yellow]")
            raise typer.Exit(code=0)

        issue_id = selected.number

    # Start or resume workflow
    try:
        workflow = service.start_workflow(
            issue_id=issue_id,
            resume=resume,
            manual_branch=branch,
        )

        if resume:
            console.print(
                f"[green]Resumed[/green] workflow for issue [cyan]#{issue_id}[/cyan]"
            )
        else:
            display_workflow_started(workflow, issue_id)

        # Show next steps based on phase
        _show_next_steps(workflow.phase, manual)

    except FixitServiceError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)


@app.command("list")
def list_bugs(
    label: str = typer.Option(
        "bug", "--label", "-l", help="Label to filter by"
    ),
    limit: int = typer.Option(
        20, "--limit", "-n", help="Maximum number of bugs to show"
    ),
    output_format: str = typer.Option(
        "table", "--format", "-f", help="Output format: table, json"
    ),
) -> None:
    """List open bugs from GitHub.

    Shows open issues with the specified label (default: bug).

    Examples:
        doit fixit list              # List bugs
        doit fixit list --label high # List high priority issues
        doit fixit list --limit 10   # Show only 10 bugs
    """
    try:
        service = FixitService()
    except GitHubServiceError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=2)

    bugs = service.list_bugs(label=label, limit=limit)

    if not bugs:
        console.print(f"[yellow]No open issues with label '{label}' found.[/yellow]")
        raise typer.Exit(code=0)

    if output_format == "json":
        import json
        data = [bug.to_dict() for bug in bugs]
        console.print(json.dumps(data, indent=2))
    else:
        table = Table(title=f"Open Issues ({label})")
        table.add_column("#", style="cyan", width=6)
        table.add_column("Title", style="white")
        table.add_column("Labels", style="dim")

        for bug in bugs:
            labels_str = ", ".join(bug.labels) if bug.labels else ""
            table.add_row(str(bug.number), bug.title, labels_str)

        console.print(table)

    console.print(f"\nUse [cyan]doit fixit <issue_id>[/cyan] to start a workflow.")


@app.command("status")
def status(
    issue_id: Optional[int] = typer.Argument(
        None,
        help="GitHub issue number (or shows active workflow)",
    ),
) -> None:
    """Show status of a fixit workflow.

    If no issue_id is provided, shows the currently active workflow.

    Examples:
        doit fixit status       # Show active workflow
        doit fixit status 123   # Show workflow for issue #123
    """
    try:
        service = FixitService()
    except GitHubServiceError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=2)

    if issue_id is None:
        # Show active workflow
        workflow = service.get_active_workflow()
        if workflow is None:
            console.print("[yellow]No active fixit workflow.[/yellow]")
            console.print("Use [cyan]doit fixit <issue_id>[/cyan] to start one.")
            raise typer.Exit(code=0)
        issue_id = workflow.issue_id
    else:
        workflow = service.get_workflow(issue_id)
        if workflow is None:
            console.print(f"[yellow]No workflow found for issue #{issue_id}.[/yellow]")
            raise typer.Exit(code=1)

    display_workflow_status(workflow)


@app.command("cancel")
def cancel(
    issue_id: Optional[int] = typer.Argument(
        None,
        help="GitHub issue number to cancel",
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Skip confirmation"
    ),
) -> None:
    """Cancel an active fixit workflow.

    Marks the workflow as cancelled. The git branch is not deleted.

    Examples:
        doit fixit cancel       # Cancel active workflow
        doit fixit cancel 123   # Cancel workflow for issue #123
    """
    try:
        service = FixitService()
    except GitHubServiceError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=2)

    if issue_id is None:
        workflow = service.get_active_workflow()
        if workflow is None:
            console.print("[yellow]No active fixit workflow to cancel.[/yellow]")
            raise typer.Exit(code=0)
        issue_id = workflow.issue_id

    # Confirm unless forced
    if not force:
        confirm = typer.confirm(
            f"Cancel workflow for issue #{issue_id}?",
            default=False,
        )
        if not confirm:
            console.print("[yellow]Cancelled.[/yellow]")
            raise typer.Exit(code=0)

    success = service.cancel_workflow(issue_id)
    if success:
        console.print(
            f"[green]Cancelled[/green] workflow for issue [cyan]#{issue_id}[/cyan]"
        )
    else:
        console.print(f"[red]Failed to cancel workflow for issue #{issue_id}.[/red]")
        raise typer.Exit(code=1)


@app.command("workflows")
def list_workflows() -> None:
    """List all fixit workflows.

    Shows all workflows, including completed and cancelled ones.
    """
    try:
        service = FixitService()
    except GitHubServiceError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=2)

    workflows = service.list_workflows()

    if not workflows:
        console.print("[yellow]No fixit workflows found.[/yellow]")
        raise typer.Exit(code=0)

    table = Table(title="Fixit Workflows")
    table.add_column("Issue", style="cyan", width=8)
    table.add_column("Branch", style="white")
    table.add_column("Phase", style="dim")
    table.add_column("Updated", style="dim")

    for issue_id, workflow in workflows:
        phase_style = _get_phase_style(workflow.phase)
        table.add_row(
            f"#{issue_id}",
            workflow.branch_name,
            f"[{phase_style}]{workflow.phase.value}[/{phase_style}]",
            workflow.updated_at.strftime("%Y-%m-%d %H:%M"),
        )

    console.print(table)


@app.command("investigate")
def investigate(
    issue_id: Optional[int] = typer.Argument(
        None,
        help="GitHub issue number (or uses active workflow)",
    ),
    add_finding: Optional[str] = typer.Option(
        None, "--add-finding", "-a", help="Add a finding to the investigation"
    ),
    finding_type: str = typer.Option(
        "hypothesis", "--type", "-t", help="Finding type: hypothesis, confirmed_cause, affected_file, reproduction_step"
    ),
    checkpoint: Optional[str] = typer.Option(
        None, "--checkpoint", "-c", help="Complete a checkpoint by ID"
    ),
    done: bool = typer.Option(
        False, "--done", "-d", help="Mark investigation complete"
    ),
) -> None:
    """Manage investigation for a fixit workflow.

    Start, add findings, complete checkpoints, or finish investigation.

    Examples:
        doit fixit investigate              # Start/view investigation
        doit fixit investigate -a "Found null check missing" -t hypothesis
        doit fixit investigate -c cp-1      # Complete checkpoint
        doit fixit investigate --done       # Finish investigation
    """
    from ..models.fixit_models import FindingType
    from ..prompts.fixit_prompts import display_investigation_findings

    try:
        service = FixitService()
    except GitHubServiceError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=2)

    # Get issue_id from active workflow if not provided
    if issue_id is None:
        workflow = service.get_active_workflow()
        if workflow is None:
            console.print("[yellow]No active fixit workflow.[/yellow]")
            raise typer.Exit(code=0)
        issue_id = workflow.issue_id

    # Handle --done flag
    if done:
        success = service.complete_investigation(issue_id)
        if success:
            console.print(
                f"[green]Investigation complete![/green] "
                f"Run [cyan]doit fixit plan[/cyan] to create a fix plan."
            )
        else:
            console.print(
                "[red]Cannot complete investigation.[/red] "
                "Add a confirmed_cause finding first."
            )
            raise typer.Exit(code=1)
        return

    # Handle --checkpoint flag
    if checkpoint:
        success = service.complete_checkpoint(issue_id, checkpoint)
        if success:
            console.print(f"[green]Checkpoint {checkpoint} completed.[/green]")
        else:
            console.print(f"[red]Checkpoint {checkpoint} not found.[/red]")
            raise typer.Exit(code=1)
        return

    # Handle --add-finding flag
    if add_finding:
        try:
            ft = FindingType(finding_type)
        except ValueError:
            console.print(f"[red]Invalid finding type: {finding_type}[/red]")
            raise typer.Exit(code=1)

        finding = service.add_finding(
            issue_id=issue_id,
            finding_type=ft,
            description=add_finding,
        )
        if finding:
            console.print(f"[green]Finding added:[/green] {finding.description}")
        else:
            console.print("[red]Failed to add finding.[/red] Start investigation first.")
            raise typer.Exit(code=1)
        return

    # Default: start or show investigation
    plan = service.get_investigation_plan(issue_id)
    if plan is None:
        # Start investigation
        plan = service.start_investigation(issue_id)
        if plan is None:
            console.print(f"[red]No workflow found for issue #{issue_id}.[/red]")
            raise typer.Exit(code=1)
        console.print("[green]Investigation started![/green]")
        console.print()

    # Display investigation status
    console.print(Panel(
        f"[dim]Keywords:[/dim] {', '.join(plan.keywords[:5]) if plan.keywords else 'none'}\n\n"
        "[dim]Checkpoints:[/dim]",
        title=f"Investigation Plan: {plan.id}",
        border_style="yellow",
    ))

    # Show checkpoints
    for cp in plan.checkpoints:
        status = "[green]✓[/green]" if cp.completed else "[dim]○[/dim]"
        console.print(f"  {status} {cp.title} [dim]({cp.id})[/dim]")

    console.print()
    display_investigation_findings(plan.findings)

    console.print(
        "\n[dim]Use --add-finding to add findings, --checkpoint to complete steps, --done when ready.[/dim]"
    )


@app.command("plan")
def plan(
    issue_id: Optional[int] = typer.Argument(
        None,
        help="GitHub issue number (or uses active workflow)",
    ),
    generate: bool = typer.Option(
        False, "--generate", "-g", help="Generate fix plan from investigation"
    ),
    submit: bool = typer.Option(
        False, "--submit", "-s", help="Submit plan for review"
    ),
) -> None:
    """Create or view a fix plan for a workflow.

    Generate a fix plan from investigation findings, or view existing plan.

    Examples:
        doit fixit plan              # View current fix plan
        doit fixit plan --generate   # Generate plan from findings
        doit fixit plan --submit     # Submit plan for review
    """
    from ..prompts.fixit_prompts import display_fix_plan

    try:
        service = FixitService()
    except GitHubServiceError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=2)

    # Get issue_id from active workflow if not provided
    if issue_id is None:
        workflow = service.get_active_workflow()
        if workflow is None:
            console.print("[yellow]No active fixit workflow.[/yellow]")
            raise typer.Exit(code=0)
        issue_id = workflow.issue_id

    # Handle --generate flag
    if generate:
        plan_obj = service.generate_fix_plan(issue_id)
        if plan_obj is None:
            console.print(
                "[red]Cannot generate fix plan.[/red] "
                "Complete investigation with a confirmed_cause finding first."
            )
            raise typer.Exit(code=1)
        console.print("[green]Fix plan generated![/green]")
        display_fix_plan(plan_obj)
        console.print(
            "\n[dim]Run [cyan]doit fixit plan --submit[/cyan] when ready for review.[/dim]"
        )
        return

    # Handle --submit flag
    if submit:
        success = service.submit_for_review(issue_id)
        if success:
            console.print(
                "[green]Plan submitted for review![/green] "
                "Run [cyan]doit fixit review[/cyan] to approve."
            )
        else:
            console.print("[red]No fix plan found to submit.[/red]")
            raise typer.Exit(code=1)
        return

    # Default: view existing plan
    plan_obj = service.get_fix_plan(issue_id)
    if plan_obj is None:
        console.print(
            "[yellow]No fix plan found.[/yellow] "
            "Run [cyan]doit fixit plan --generate[/cyan] to create one."
        )
        raise typer.Exit(code=0)

    display_fix_plan(plan_obj)


@app.command("review")
def review(
    issue_id: Optional[int] = typer.Argument(
        None,
        help="GitHub issue number (or uses active workflow)",
    ),
    approve: bool = typer.Option(
        False, "--approve", "-a", help="Approve the fix plan"
    ),
) -> None:
    """Review and approve a fix plan.

    View the fix plan and optionally approve it for implementation.

    Examples:
        doit fixit review           # View plan for review
        doit fixit review --approve # Approve the plan
    """
    from ..prompts.fixit_prompts import display_fix_plan

    try:
        service = FixitService()
    except GitHubServiceError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=2)

    # Get issue_id from active workflow if not provided
    if issue_id is None:
        workflow = service.get_active_workflow()
        if workflow is None:
            console.print("[yellow]No active fixit workflow.[/yellow]")
            raise typer.Exit(code=0)
        issue_id = workflow.issue_id

    # Get fix plan
    plan_obj = service.get_fix_plan(issue_id)
    if plan_obj is None:
        console.print(
            "[yellow]No fix plan found.[/yellow] "
            "Run [cyan]doit fixit plan --generate[/cyan] first."
        )
        raise typer.Exit(code=0)

    # Display plan
    display_fix_plan(plan_obj)
    console.print()

    # Handle --approve flag
    if approve:
        success = service.approve_plan(issue_id)
        if success:
            console.print(
                Panel(
                    "[green]Plan approved![/green]\n\n"
                    "Ready to implement the fix.\n"
                    "Run [cyan]doit implementit[/cyan] to execute the tasks.",
                    title="Approved",
                    border_style="green",
                )
            )
        else:
            console.print("[red]Failed to approve plan.[/red]")
            raise typer.Exit(code=1)
        return

    # Prompt for action
    console.print(
        "\n[dim]Use --approve to approve this plan, or edit and resubmit.[/dim]"
    )


# =============================================================================
# Helper Functions
# =============================================================================


def _show_next_steps(phase: FixPhase, manual: bool = False) -> None:
    """Display next steps based on current phase."""
    console.print()

    if phase == FixPhase.INVESTIGATING:
        if manual:
            console.print(
                Panel(
                    "[cyan]Manual mode enabled.[/cyan]\n\n"
                    "1. Investigate the issue manually\n"
                    "2. Create a fix plan with [cyan]doit fixit plan[/cyan]\n"
                    "3. Implement the fix using [cyan]doit implementit[/cyan]",
                    title="Next Steps",
                    border_style="dim",
                )
            )
        else:
            console.print(
                Panel(
                    "The AI will help investigate the issue.\n\n"
                    "Run [cyan]doit fixit investigate[/cyan] to start the investigation.",
                    title="Next Steps",
                    border_style="dim",
                )
            )
    elif phase == FixPhase.PLANNING:
        console.print(
            Panel(
                "Investigation complete. Ready to create a fix plan.\n\n"
                "Run [cyan]doit fixit plan[/cyan] to generate a fix plan.",
                title="Next Steps",
                border_style="dim",
            )
        )
    elif phase == FixPhase.REVIEWING:
        console.print(
            Panel(
                "Fix plan is ready for review.\n\n"
                "Run [cyan]doit fixit review[/cyan] to review and approve.",
                title="Next Steps",
                border_style="dim",
            )
        )
    elif phase == FixPhase.APPROVED:
        console.print(
            Panel(
                "Fix plan approved! Ready to implement.\n\n"
                "Run [cyan]doit implementit[/cyan] to execute the tasks.",
                title="Next Steps",
                border_style="dim",
            )
        )


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
