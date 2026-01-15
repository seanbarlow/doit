"""CLI commands for Git hook management."""

import sys

import typer
from rich.console import Console

from ..services.hook_manager import HookManager
from ..services.hook_validator import HookValidator

console = Console()

# Create the hooks command group
hooks_app = typer.Typer(
    name="hooks",
    help="Manage Git hooks for workflow enforcement.",
    no_args_is_help=True,
)


@hooks_app.command("install")
def install_hooks(
    backup: bool = typer.Option(
        False, "--backup", "-b", help="Backup existing hooks before installing"
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Overwrite existing hooks without prompting"
    ),
) -> None:
    """Install pre-commit and pre-push Git hooks."""
    manager = HookManager()

    # Check if in git repo
    if not manager.is_git_repo():
        console.print("[red]Error: Not a Git repository.[/red]")
        console.print("Run 'git init' first to initialize a Git repository.")
        raise typer.Exit(1)

    try:
        installed, skipped = manager.install_hooks(backup=backup, force=force)

        if installed:
            console.print("[green]Successfully installed hooks:[/green]")
            for hook in installed:
                console.print(f"  - {hook}")

        if skipped:
            console.print("\n[yellow]Skipped hooks (already exist):[/yellow]")
            for hook in skipped:
                console.print(f"  - {hook}")
            console.print("\nUse --backup to backup existing hooks, or --force to overwrite.")

        if not installed and not skipped:
            console.print("[yellow]No hooks to install.[/yellow]")

    except RuntimeError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@hooks_app.command("uninstall")
def uninstall_hooks() -> None:
    """Remove installed Git hooks."""
    manager = HookManager()

    removed = manager.uninstall_hooks()

    if removed:
        console.print("[green]Successfully removed hooks:[/green]")
        for hook in removed:
            console.print(f"  - {hook}")
    else:
        console.print("[yellow]No doit hooks found to remove.[/yellow]")


@hooks_app.command("status")
def hooks_status() -> None:
    """Show current hook installation and configuration status."""
    from ..models.hook_config import HookConfig

    manager = HookManager()
    config = HookConfig.load_default()

    console.print("[bold]Git Hooks Status[/bold]")
    console.print("=" * 40)

    if not manager.is_git_repo():
        console.print("[red]Not a Git repository[/red]")
        raise typer.Exit(1)

    installed = manager.get_installed_hooks()

    console.print("\n[bold]Installed Hooks:[/bold]")
    if installed:
        for hook in installed:
            console.print(f"  [green]\u2713[/green] {hook}")
    else:
        console.print("  [dim]No doit hooks installed[/dim]")

    # Show configuration
    config_path = HookConfig.get_default_config_path()
    console.print(f"\n[bold]Configuration:[/bold] {config_path}")

    pre_commit_status = "[green]enabled[/green]" if config.pre_commit.enabled else "[red]disabled[/red]"
    pre_push_status = "[green]enabled[/green]" if config.pre_push.enabled else "[red]disabled[/red]"
    bypass_status = "[green]enabled[/green]" if config.logging.log_bypasses else "[red]disabled[/red]"

    console.print(f"  Pre-commit validation: {pre_commit_status}")
    console.print(f"  Pre-push validation:   {pre_push_status}")
    console.print(f"  Bypass logging:        {bypass_status}")

    # Show exempt branches
    if config.pre_commit.exempt_branches:
        console.print(f"\n[bold]Exempt Branches:[/bold] {', '.join(config.pre_commit.exempt_branches)}")

    # Show exempt paths
    if config.pre_commit.exempt_paths:
        console.print(f"[bold]Exempt Paths:[/bold] {', '.join(config.pre_commit.exempt_paths)}")

    console.print("\n[dim]Use 'doit hooks install' to install hooks[/dim]")


@hooks_app.command("restore")
def restore_hooks(
    timestamp: str = typer.Option(
        None, "--timestamp", "-t", help="Specific backup timestamp to restore"
    ),
) -> None:
    """Restore previously backed up hooks."""
    manager = HookManager()

    try:
        restored = manager.restore_hooks(timestamp=timestamp)

        if restored:
            console.print("[green]Successfully restored hooks:[/green]")
            for hook in restored:
                console.print(f"  - {hook}")
        else:
            console.print("[yellow]No hooks were restored.[/yellow]")

    except RuntimeError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@hooks_app.command("validate")
def validate_hook(
    hook_type: str = typer.Argument(
        ..., help="Type of hook to validate (pre-commit or pre-push)"
    ),
) -> None:
    """Validate workflow compliance for the specified hook type."""
    valid_types = ["pre-commit", "pre-push"]
    if hook_type not in valid_types:
        console.print(f"[red]Invalid hook type: {hook_type}[/red]")
        console.print(f"Valid types: {', '.join(valid_types)}")
        raise typer.Exit(1)

    validator = HookValidator()

    if hook_type == "pre-commit":
        result = validator.validate_pre_commit()
    else:
        result = validator.validate_pre_push()

    if result.success:
        # Silent success for normal workflow
        sys.exit(0)
    else:
        # Show error and suggestion
        console.print(f"[red]\u2717 {hook_type.title().replace('-', '-')} validation failed[/red]")
        console.print()
        console.print(result.message)
        if result.suggestion:
            console.print()
            console.print(f"[dim]{result.suggestion}[/dim]")
        sys.exit(1)


@hooks_app.command("report")
def hooks_report() -> None:
    """Show bypass audit log report."""
    validator = HookValidator()
    events = validator.get_bypass_report()

    console.print("[bold]Hook Bypass Report[/bold]")
    console.print("=" * 40)

    if not events:
        console.print("\n[dim]No bypass events recorded.[/dim]")
        console.print("[dim]Bypass events are logged when --no-verify is used.[/dim]")
        return

    console.print(f"\n[bold]Total bypasses:[/bold] {len(events)}")
    console.print()

    for event in events:
        timestamp = event.get("timestamp", "Unknown")
        hook = event.get("hook", "Unknown")
        branch = event.get("branch", "Unknown")
        user = event.get("user", "Unknown")
        commit = event.get("commit", "")

        line = f"[dim]{timestamp}[/dim] | [yellow]{hook}[/yellow] | branch: {branch}"
        if commit:
            line += f" | commit: {commit}"
        if user:
            line += f" | user: {user}"

        console.print(line)
