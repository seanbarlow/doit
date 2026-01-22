"""CLI command for team collaboration.

This module provides the team command and subcommands
for team memory sharing, synchronization, and management.
"""

from datetime import datetime
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from doit_cli.models.team_models import TeamPermission, TeamRole
from doit_cli.services.team_config import (
    TeamConfigError,
    TeamConfigValidationError,
    TeamNotInitializedError,
)
from doit_cli.services.team_service import (
    MemberAlreadyExistsError,
    MemberNotFoundError,
    PermissionDeniedError,
    TeamService,
)
from doit_cli.services.sync_service import (
    NetworkError,
    NoRemoteError,
    SyncService,
)
from doit_cli.services.notification_service import NotificationService
from doit_cli.services.access_service import AccessService
from doit_cli.models.team_models import NotificationType

app = typer.Typer(help="Team collaboration commands")
console = Console()


def _get_service() -> TeamService:
    """Get TeamService instance."""
    return TeamService()


def _get_sync_service(team_service: TeamService) -> SyncService:
    """Get SyncService instance."""
    return SyncService(team_service)


def _require_initialized(service: TeamService) -> None:
    """Require team to be initialized."""
    if not service.is_initialized():
        console.print(
            "[red]Error:[/red] Team collaboration not initialized.\n"
            "Run [cyan]doit team init[/cyan] first."
        )
        raise typer.Exit(code=1)


def _format_time_ago(dt: Optional[datetime]) -> str:
    """Format datetime as relative time."""
    if not dt:
        return "Never"

    delta = datetime.now() - dt
    seconds = delta.total_seconds()

    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} min ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    else:
        days = int(seconds / 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"


@app.callback()
def main() -> None:
    """Team collaboration commands.

    Use subcommands to manage team sharing:

    Examples:
        doit team init              # Initialize team collaboration
        doit team add user@email    # Add a team member
        doit team sync              # Sync memory files
        doit team status            # Show sync status
    """
    pass


# =============================================================================
# T010: team init command
# =============================================================================


@app.command("init")
def init_team(
    name: Optional[str] = typer.Option(
        None,
        "--name", "-n",
        help="Team name (defaults to project folder name)",
    ),
    owner: Optional[str] = typer.Option(
        None,
        "--owner", "-o",
        help="Owner email (defaults to git user.email)",
    ),
) -> None:
    """Initialize team collaboration for the project.

    Creates .doit/config/team.yaml with team configuration and
    sets up state files for synchronization.

    Examples:
        doit team init
        doit team init --name "My Team"
        doit team init --owner owner@example.com
    """
    service = _get_service()

    try:
        config = service.init_team(name=name, owner_email=owner)

        console.print()
        console.print("[green]✓ Team collaboration initialized[/green]")
        console.print(f"  Team: [cyan]{config.team.name}[/cyan]")
        console.print(f"  Owner: [cyan]{config.team.owner_id}[/cyan]")
        console.print()
        console.print("[dim]Next steps:[/dim]")
        console.print("  [cyan]doit team add <email>[/cyan]     Add a team member")
        console.print("  [cyan]doit team sync[/cyan]            Sync memory files")

    except TeamConfigValidationError as e:
        console.print(f"[red]Error:[/red] {e}")
        if e.errors:
            for error in e.errors:
                console.print(f"  • {error}")
        raise typer.Exit(code=1)


# =============================================================================
# T011: team add/remove commands
# =============================================================================


@app.command("add")
def add_member(
    email: str = typer.Argument(
        ...,
        help="Member's email address",
    ),
    role: str = typer.Option(
        "member",
        "--role", "-r",
        help="Role: 'owner' or 'member'",
    ),
    permission: str = typer.Option(
        "read-write",
        "--permission", "-p",
        help="Permission: 'read-write' or 'read-only'",
    ),
    no_notify: bool = typer.Option(
        False,
        "--no-notify",
        help="Disable notifications for this member",
    ),
    display_name: Optional[str] = typer.Option(
        None,
        "--name",
        help="Display name for the member",
    ),
) -> None:
    """Add a team member to the project.

    New members get read-write access by default. Use --permission
    to restrict to read-only.

    Examples:
        doit team add user@example.com
        doit team add user@example.com --role owner
        doit team add user@example.com --permission read-only
    """
    service = _get_service()
    _require_initialized(service)

    try:
        # Parse role and permission
        member_role = TeamRole.OWNER if role.lower() == "owner" else TeamRole.MEMBER
        member_perm = (
            TeamPermission.READ_ONLY
            if permission.lower() == "read-only"
            else TeamPermission.READ_WRITE
        )

        member = service.add_member(
            email=email,
            role=member_role,
            permission=member_perm,
            notifications=not no_notify,
            display_name=display_name,
        )

        console.print()
        console.print(f"[green]✓ Added {email} to team[/green]")
        console.print(f"  Role: [cyan]{member.role.value}[/cyan]")
        console.print(f"  Permission: [cyan]{member.permission.value}[/cyan]")
        console.print(f"  Notifications: [cyan]{'enabled' if member.notifications else 'disabled'}[/cyan]")

    except MemberAlreadyExistsError:
        console.print(f"[red]Error:[/red] Member already exists: {email}")
        raise typer.Exit(code=2)
    except TeamConfigValidationError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
    except PermissionDeniedError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=3)


@app.command("remove")
def remove_member(
    email: str = typer.Argument(
        ...,
        help="Member's email address to remove",
    ),
    force: bool = typer.Option(
        False,
        "--force", "-f",
        help="Skip confirmation prompt",
    ),
) -> None:
    """Remove a team member from the project.

    Examples:
        doit team remove user@example.com
        doit team remove user@example.com --force
    """
    service = _get_service()
    _require_initialized(service)

    # Check if member exists
    member = service.get_member(email)
    if not member:
        console.print(f"[red]Error:[/red] Member not found: {email}")
        raise typer.Exit(code=1)

    # Confirm unless forced
    if not force:
        confirm = typer.confirm(f"Remove {email} from team?")
        if not confirm:
            console.print("Cancelled.")
            raise typer.Exit(code=0)

    try:
        service.remove_member(email)
        console.print(f"[green]✓ Removed {email} from team[/green]")

    except TeamConfigValidationError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=2)
    except PermissionDeniedError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=3)


# =============================================================================
# T012: team list command
# =============================================================================


@app.command("list")
def list_members(
    format: str = typer.Option(
        "table",
        "--format", "-f",
        help="Output format: 'table', 'json', or 'yaml'",
    ),
) -> None:
    """List all team members and their status.

    Examples:
        doit team list
        doit team list --format json
    """
    service = _get_service()
    _require_initialized(service)

    team = service.get_team()
    members = service.list_members()

    if format.lower() == "json":
        import json
        data = {
            "team": team.to_dict(),
            "members": [m.to_dict() for m in members],
        }
        console.print(json.dumps(data, indent=2, default=str))
        return

    if format.lower() == "yaml":
        import yaml
        data = {
            "team": team.to_dict(),
            "members": [m.to_dict() for m in members],
        }
        console.print(yaml.dump(data, default_flow_style=False))
        return

    # Table format
    console.print()
    console.print(f"[bold]Team:[/bold] {team.name}")
    console.print(f"[bold]Owner:[/bold] {team.owner_id}")
    console.print()

    table = Table(show_header=True, header_style="bold")
    table.add_column("Email")
    table.add_column("Role")
    table.add_column("Permission")
    table.add_column("Notifications")
    table.add_column("Last Sync")

    for member in members:
        notify_icon = "✓" if member.notifications else "✗"
        table.add_row(
            member.email,
            member.role.value,
            member.permission.value,
            notify_icon,
            _format_time_ago(member.last_sync),
        )

    console.print(f"[bold]Members ({len(members)}):[/bold]")
    console.print(table)


# =============================================================================
# T013: team sync command
# =============================================================================


@app.command("sync")
def sync_memory(
    push_flag: bool = typer.Option(
        False,
        "--push",
        help="Only push local changes",
    ),
    pull_flag: bool = typer.Option(
        False,
        "--pull",
        help="Only pull remote changes",
    ),
    force: bool = typer.Option(
        False,
        "--force", "-f",
        help="Overwrite conflicts without prompting",
    ),
) -> None:
    """Synchronize shared memory files with the team.

    By default, pulls remote changes then pushes local changes.
    Use --push or --pull to sync in only one direction.

    Examples:
        doit team sync
        doit team sync --push
        doit team sync --pull
        doit team sync --force
    """
    service = _get_service()
    _require_initialized(service)
    sync_service = _get_sync_service(service)

    try:
        console.print("[dim]Syncing with team...[/dim]")

        result = sync_service.sync(
            push_only=push_flag,
            pull_only=pull_flag,
            force=force,
        )

        if result.conflicts:
            console.print()
            console.print("[yellow]⚠ Conflicts detected:[/yellow]")
            for conflict in result.conflicts:
                console.print(f"  • {conflict}")
            console.print()
            console.print("Run [cyan]doit team sync --force[/cyan] to keep local versions,")
            console.print("or resolve manually and run [cyan]doit team sync[/cyan] again.")
            raise typer.Exit(code=2)

        if result.success:
            console.print()
            console.print("[green]✓ Synced with team[/green]")

            if result.pulled_files:
                console.print(f"  [dim]↓ Pulled:[/dim] {len(result.pulled_files)} files")
                for f in result.pulled_files[:5]:  # Show first 5
                    console.print(f"    • {f}")
                if len(result.pulled_files) > 5:
                    console.print(f"    [dim]... and {len(result.pulled_files) - 5} more[/dim]")

            if result.pushed_files:
                console.print(f"  [dim]↑ Pushed:[/dim] {len(result.pushed_files)} files")
                for f in result.pushed_files[:5]:
                    console.print(f"    • {f}")
                if len(result.pushed_files) > 5:
                    console.print(f"    [dim]... and {len(result.pushed_files) - 5} more[/dim]")

            if not result.pulled_files and not result.pushed_files:
                console.print("  [dim]Already up to date[/dim]")

            console.print(f"  Last sync: [cyan]just now[/cyan]")
        else:
            console.print(f"[red]Error:[/red] {result.error_message}")
            raise typer.Exit(code=1)

    except NoRemoteError as e:
        console.print(f"[red]Error:[/red] {e}")
        console.print("Push your repository to a remote first.")
        raise typer.Exit(code=1)
    except NetworkError as e:
        console.print(f"[yellow]Warning:[/yellow] {e}")
        console.print("Changes saved locally. They will sync when connectivity returns.")
        raise typer.Exit(code=1)


# =============================================================================
# T014: team status command
# =============================================================================


@app.command("status")
def show_status(
    verbose: bool = typer.Option(
        False,
        "--verbose", "-v",
        help="Show detailed sync history",
    ),
) -> None:
    """Show team sync status and pending notifications.

    Displays current sync state, shared files status, and
    any unread notifications.

    Examples:
        doit team status
        doit team status --verbose
    """
    service = _get_service()
    _require_initialized(service)
    sync_service = _get_sync_service(service)

    team = service.get_team()
    status = sync_service.get_status()

    console.print()
    console.print(f"[bold]Team:[/bold] {team.name}")
    console.print()

    # Sync status
    console.print("[bold]Sync Status:[/bold]")
    if status["is_online"]:
        console.print("  Remote: [green]✓ Connected[/green]")
    else:
        console.print("  Remote: [yellow]✗ Offline[/yellow]")

    if status["local_ahead"] > 0:
        console.print(f"  Local:  [cyan]↑ {status['local_ahead']} ahead[/cyan]")
    elif status["local_behind"] > 0:
        console.print(f"  Local:  [yellow]↓ {status['local_behind']} behind[/yellow]")
    else:
        console.print("  Local:  [green]✓ Up to date[/green]")

    console.print(f"  Last sync: [dim]{_format_time_ago(status['last_sync'])}[/dim]")
    console.print()

    # Shared files
    console.print("[bold]Shared Files:[/bold]")
    file_table = Table(show_header=True, header_style="bold", box=None)
    file_table.add_column("File")
    file_table.add_column("Status")
    file_table.add_column("Modified")

    status_icons = {
        "synced": "[green]✓ Synced[/green]",
        "modified": "[yellow]● Modified[/yellow]",
        "ahead": "[cyan]↑ Ahead[/cyan]",
        "behind": "[yellow]↓ Behind[/yellow]",
        "missing": "[red]✗ Missing[/red]",
        "unknown": "[dim]? Unknown[/dim]",
    }

    for file_info in status["files"]:
        icon = status_icons.get(file_info["status"], file_info["status"])
        modified_str = _format_time_ago(file_info.get("modified_at"))
        file_table.add_row(file_info["path"], icon, modified_str)

    console.print(file_table)
    console.print()

    if verbose:
        # Show sync history
        history = sync_service.get_sync_history(limit=5)
        if history:
            console.print("[bold]Recent Sync History:[/bold]")
            for op in reversed(history):
                status_color = "green" if op.status.value == "success" else "yellow"
                console.print(
                    f"  [{status_color}]{op.status.value}[/{status_color}] "
                    f"{op.operation_type.value} - {_format_time_ago(op.started_at)}"
                )
            console.print()

    # Suggest action
    if not status["is_online"]:
        console.print("[dim]Run 'doit team sync' when online to synchronize.[/dim]")
    elif status["local_behind"] > 0:
        console.print("[dim]Run 'doit team sync' to pull remote changes.[/dim]")
    elif status["local_ahead"] > 0:
        console.print("[dim]Run 'doit team sync' to push local changes.[/dim]")


# =============================================================================
# T018: team notify commands
# =============================================================================

notify_app = typer.Typer(help="Notification management commands")
app.add_typer(notify_app, name="notify")


def _get_notification_service() -> NotificationService:
    """Get NotificationService instance."""
    return NotificationService()


def _format_notification_type(ntype: NotificationType) -> str:
    """Format notification type with icon."""
    icons = {
        NotificationType.MEMORY_CHANGED: "[blue]📝[/blue]",
        NotificationType.CONFLICT_DETECTED: "[yellow]⚠️[/yellow]",
        NotificationType.MEMBER_JOINED: "[green]👤[/green]",
        NotificationType.PERMISSION_CHANGED: "[cyan]🔐[/cyan]",
    }
    return icons.get(ntype, "")


@notify_app.command("list")
def list_notifications(
    all_notifications: bool = typer.Option(
        False,
        "--all", "-a",
        help="Show all notifications (including read)",
    ),
    notification_type: Optional[str] = typer.Option(
        None,
        "--type", "-t",
        help="Filter by type: memory_changed, conflict_detected, member_joined, permission_changed",
    ),
    limit: int = typer.Option(
        20,
        "--limit", "-l",
        help="Maximum number to show",
    ),
    format: str = typer.Option(
        "table",
        "--format", "-f",
        help="Output format: 'table' or 'json'",
    ),
) -> None:
    """List notifications.

    Shows unread notifications by default. Use --all to see all.

    Examples:
        doit team notify list
        doit team notify list --all
        doit team notify list --type conflict_detected
    """
    service = _get_service()
    _require_initialized(service)

    notif_service = _get_notification_service()

    # Parse notification type filter
    type_filter = None
    if notification_type:
        try:
            type_filter = NotificationType(notification_type)
        except ValueError:
            console.print(f"[red]Error:[/red] Invalid notification type: {notification_type}")
            console.print("Valid types: memory_changed, conflict_detected, member_joined, permission_changed")
            raise typer.Exit(code=1)

    notifications = notif_service.get_notifications(
        unread_only=not all_notifications,
        limit=limit,
        notification_type=type_filter,
    )

    if format.lower() == "json":
        import json
        data = [n.to_dict() for n in notifications]
        console.print(json.dumps(data, indent=2, default=str))
        return

    # Show unread count
    unread_count = notif_service.get_unread_count()

    console.print()
    if unread_count > 0:
        console.print(f"[bold]Notifications[/bold] ([cyan]{unread_count} unread[/cyan])")
    else:
        console.print("[bold]Notifications[/bold] [dim](no unread)[/dim]")
    console.print()

    if not notifications:
        if all_notifications:
            console.print("[dim]No notifications.[/dim]")
        else:
            console.print("[dim]No unread notifications.[/dim]")
            console.print("[dim]Use --all to see read notifications.[/dim]")
        return

    # Table format
    table = Table(show_header=True, header_style="bold", box=None)
    table.add_column("", width=3)  # Read indicator
    table.add_column("Type", width=10)
    table.add_column("Title")
    table.add_column("When", width=12)

    for notif in notifications:
        read_marker = "[dim]✓[/dim]" if notif.read else "[cyan]●[/cyan]"
        type_icon = _format_notification_type(notif.type)
        time_str = _format_time_ago(notif.created_at)

        table.add_row(
            read_marker,
            f"{type_icon} {notif.type.value[:8]}",
            notif.title,
            time_str,
        )

    console.print(table)
    console.print()

    if unread_count > 0:
        console.print(f"[dim]Run 'doit team notify read' to mark all as read.[/dim]")


@notify_app.command("read")
def mark_read(
    notification_id: Optional[str] = typer.Argument(
        None,
        help="Notification ID to mark as read (marks all if not provided)",
    ),
) -> None:
    """Mark notifications as read.

    Without an ID, marks all unread notifications as read.

    Examples:
        doit team notify read             # Mark all as read
        doit team notify read abc123      # Mark specific notification
    """
    service = _get_service()
    _require_initialized(service)

    notif_service = _get_notification_service()

    count = notif_service.mark_read(notification_id)

    if count > 0:
        if notification_id:
            console.print(f"[green]✓ Marked notification as read[/green]")
        else:
            console.print(f"[green]✓ Marked {count} notification{'s' if count != 1 else ''} as read[/green]")
    else:
        if notification_id:
            console.print("[dim]Notification not found or already read.[/dim]")
        else:
            console.print("[dim]No unread notifications.[/dim]")


@notify_app.command("clear")
def clear_notifications(
    force: bool = typer.Option(
        False,
        "--force", "-f",
        help="Skip confirmation prompt",
    ),
) -> None:
    """Clear all notifications.

    Examples:
        doit team notify clear
        doit team notify clear --force
    """
    service = _get_service()
    _require_initialized(service)

    notif_service = _get_notification_service()

    # Get current count
    state = notif_service.get_state()
    count = len(state.notifications)

    if count == 0:
        console.print("[dim]No notifications to clear.[/dim]")
        return

    if not force:
        confirm = typer.confirm(f"Clear all {count} notifications?")
        if not confirm:
            console.print("Cancelled.")
            raise typer.Exit(code=0)

    cleared = notif_service.clear_all()
    console.print(f"[green]✓ Cleared {cleared} notification{'s' if cleared != 1 else ''}[/green]")


@notify_app.command("config")
def configure_notifications(
    enabled: Optional[bool] = typer.Option(
        None,
        "--enabled/--disabled",
        help="Enable or disable notifications",
    ),
    batch_interval: Optional[int] = typer.Option(
        None,
        "--batch-interval",
        help="Batch interval in minutes (0 = immediate)",
    ),
    on_sync: Optional[bool] = typer.Option(
        None,
        "--on-sync/--no-on-sync",
        help="Notify on sync events",
    ),
    on_conflict: Optional[bool] = typer.Option(
        None,
        "--on-conflict/--no-on-conflict",
        help="Notify on conflicts",
    ),
    on_member_change: Optional[bool] = typer.Option(
        None,
        "--on-member-change/--no-on-member-change",
        help="Notify on member changes",
    ),
) -> None:
    """View or update notification settings.

    Without options, shows current settings.

    Examples:
        doit team notify config                    # Show settings
        doit team notify config --disabled         # Disable notifications
        doit team notify config --batch-interval 10
        doit team notify config --on-conflict
    """
    service = _get_service()
    _require_initialized(service)

    notif_service = _get_notification_service()

    # If any options provided, update settings
    has_updates = any([
        enabled is not None,
        batch_interval is not None,
        on_sync is not None,
        on_conflict is not None,
        on_member_change is not None,
    ])

    if has_updates:
        settings = notif_service.update_settings(
            enabled=enabled,
            batch_interval_minutes=batch_interval,
            on_sync=on_sync,
            on_conflict=on_conflict,
            on_member_change=on_member_change,
        )
        console.print("[green]✓ Settings updated[/green]")
        console.print()
    else:
        settings = notif_service.get_settings()

    # Display current settings
    console.print("[bold]Notification Settings:[/bold]")
    console.print()

    status_icon = "[green]✓ Enabled[/green]" if settings.enabled else "[yellow]✗ Disabled[/yellow]"
    console.print(f"  Status: {status_icon}")
    console.print(f"  Batch interval: [cyan]{settings.batch_interval_minutes}[/cyan] minutes")
    console.print()

    console.print("[bold]Notify on:[/bold]")
    console.print(f"  Sync events: {'[green]✓[/green]' if settings.on_sync else '[dim]✗[/dim]'}")
    console.print(f"  Conflicts: {'[green]✓[/green]' if settings.on_conflict else '[dim]✗[/dim]'}")
    console.print(f"  Member changes: {'[green]✓[/green]' if settings.on_member_change else '[dim]✗[/dim]'}")


# =============================================================================
# T021: team conflict commands
# =============================================================================

conflict_app = typer.Typer(help="Conflict resolution commands")
app.add_typer(conflict_app, name="conflict")


def _get_conflict_service():
    """Get ConflictService instance."""
    from doit_cli.services.conflict_service import ConflictService
    return ConflictService()


@conflict_app.command("list")
def list_conflicts(
    all_conflicts: bool = typer.Option(
        False,
        "--all", "-a",
        help="Show resolved conflicts too",
    ),
    format: str = typer.Option(
        "table",
        "--format", "-f",
        help="Output format: 'table' or 'json'",
    ),
) -> None:
    """List conflicts.

    Shows active conflicts by default.

    Examples:
        doit team conflict list
        doit team conflict list --all
    """
    service = _get_service()
    _require_initialized(service)

    conflict_service = _get_conflict_service()

    active = conflict_service.get_active_conflicts()

    if format.lower() == "json":
        import json
        data = {"active": [c.to_dict() for c in active]}
        if all_conflicts:
            archived = conflict_service.get_archived_conflicts()
            data["resolved"] = [c.to_dict() for c in archived]
        console.print(json.dumps(data, indent=2, default=str))
        return

    console.print()

    if active:
        console.print(f"[bold]Active Conflicts[/bold] ([yellow]{len(active)} unresolved[/yellow])")
        console.print()

        table = Table(show_header=True, header_style="bold", box=None)
        table.add_column("ID", width=8)
        table.add_column("File")
        table.add_column("Created")

        for conflict in active:
            conflict_id = conflict.id[:8]
            time_str = _format_time_ago(conflict.created_at)
            table.add_row(conflict_id, conflict.file_path, time_str)

        console.print(table)
        console.print()
        console.print("[dim]Run 'doit team conflict show <id>' to view details.[/dim]")
        console.print("[dim]Run 'doit team conflict resolve <id>' to resolve.[/dim]")
    else:
        console.print("[green]No active conflicts.[/green]")

    if all_conflicts:
        console.print()
        archived = conflict_service.get_archived_conflicts(limit=10)
        if archived:
            console.print(f"[bold]Recently Resolved[/bold] ({len(archived)})")
            console.print()

            table = Table(show_header=True, header_style="bold", box=None)
            table.add_column("File")
            table.add_column("Resolution")
            table.add_column("Resolved")

            for conflict in archived:
                resolution = conflict.resolution.value if conflict.resolution else "unknown"
                time_str = _format_time_ago(conflict.resolved_at)
                table.add_row(conflict.file_path, resolution, time_str)

            console.print(table)


@conflict_app.command("show")
def show_conflict(
    conflict_id: str = typer.Argument(
        ...,
        help="Conflict ID (or prefix)",
    ),
    diff: bool = typer.Option(
        False,
        "--diff", "-d",
        help="Show unified diff",
    ),
) -> None:
    """Show details of a specific conflict.

    Examples:
        doit team conflict show abc123
        doit team conflict show abc123 --diff
    """
    service = _get_service()
    _require_initialized(service)

    conflict_service = _get_conflict_service()

    # Find conflict by ID prefix
    active = conflict_service.get_active_conflicts()
    conflict = None
    for c in active:
        if c.id.startswith(conflict_id):
            conflict = c
            break

    if not conflict:
        console.print(f"[red]Error:[/red] Conflict not found: {conflict_id}")
        raise typer.Exit(code=1)

    console.print()
    console.print(f"[bold]Conflict:[/bold] {conflict.file_path}")
    console.print(f"[dim]ID: {conflict.id}[/dim]")
    console.print(f"[dim]Created: {_format_time_ago(conflict.created_at)}[/dim]")
    console.print()

    if diff:
        console.print("[bold]Diff (remote → local):[/bold]")
        console.print()
        diff_lines = conflict_service.get_conflict_diff(conflict)
        for line in diff_lines:
            if line.startswith("+"):
                console.print(f"[green]{line.rstrip()}[/green]")
            elif line.startswith("-"):
                console.print(f"[red]{line.rstrip()}[/red]")
            elif line.startswith("@@"):
                console.print(f"[cyan]{line.rstrip()}[/cyan]")
            else:
                console.print(line.rstrip())
    else:
        # Side by side summary
        from rich.columns import Columns
        from rich.panel import Panel

        local_preview = conflict.local_version.content[:500]
        if len(conflict.local_version.content) > 500:
            local_preview += "\n[dim]... (truncated)[/dim]"

        remote_preview = conflict.remote_version.content[:500]
        if len(conflict.remote_version.content) > 500:
            remote_preview += "\n[dim]... (truncated)[/dim]"

        local_panel = Panel(
            local_preview,
            title="[cyan]Local (yours)[/cyan]",
            border_style="cyan",
        )
        remote_panel = Panel(
            remote_preview,
            title="[yellow]Remote (theirs)[/yellow]",
            border_style="yellow",
        )

        console.print(Columns([local_panel, remote_panel]))

    console.print()
    console.print("[bold]Resolution options:[/bold]")
    console.print("  [cyan]doit team conflict resolve {id} --keep-local[/cyan]   Keep your version")
    console.print("  [cyan]doit team conflict resolve {id} --keep-remote[/cyan]  Keep their version")
    console.print("  [cyan]doit team conflict resolve {id} --manual[/cyan]       Resolve manually")


@conflict_app.command("resolve")
def resolve_conflict(
    conflict_id: str = typer.Argument(
        ...,
        help="Conflict ID (or prefix), or 'all' to resolve all",
    ),
    keep_local: bool = typer.Option(
        False,
        "--keep-local", "--ours",
        help="Keep local version",
    ),
    keep_remote: bool = typer.Option(
        False,
        "--keep-remote", "--theirs",
        help="Keep remote version",
    ),
    manual: bool = typer.Option(
        False,
        "--manual", "-m",
        help="Mark as manually resolved",
    ),
) -> None:
    """Resolve a conflict.

    You must specify one resolution strategy.

    Examples:
        doit team conflict resolve abc123 --keep-local
        doit team conflict resolve abc123 --keep-remote
        doit team conflict resolve all --keep-local
    """
    from doit_cli.models.team_models import ConflictResolution
    from doit_cli.services.conflict_service import ConflictNotFoundError

    service = _get_service()
    _require_initialized(service)

    # Determine resolution strategy
    if sum([keep_local, keep_remote, manual]) != 1:
        console.print("[red]Error:[/red] Specify exactly one resolution: --keep-local, --keep-remote, or --manual")
        raise typer.Exit(code=1)

    if keep_local:
        resolution = ConflictResolution.KEEP_LOCAL
        strategy_name = "keep local"
    elif keep_remote:
        resolution = ConflictResolution.KEEP_REMOTE
        strategy_name = "keep remote"
    else:
        resolution = ConflictResolution.MANUAL_MERGE
        strategy_name = "manual merge"

    conflict_service = _get_conflict_service()

    # Handle 'all' case
    if conflict_id.lower() == "all":
        active = conflict_service.get_active_conflicts()
        if not active:
            console.print("[dim]No active conflicts to resolve.[/dim]")
            return

        resolved = conflict_service.resolve_all(resolution)
        console.print(f"[green]✓ Resolved {len(resolved)} conflict(s) with {strategy_name}[/green]")
        return

    # Find specific conflict
    active = conflict_service.get_active_conflicts()
    conflict = None
    for c in active:
        if c.id.startswith(conflict_id):
            conflict = c
            break

    if not conflict:
        console.print(f"[red]Error:[/red] Conflict not found: {conflict_id}")
        raise typer.Exit(code=1)

    try:
        resolved = conflict_service.resolve_conflict(conflict.id, resolution)
        console.print(f"[green]✓ Resolved {resolved.file_path} with {strategy_name}[/green]")

        if resolution == ConflictResolution.MANUAL_MERGE:
            console.print()
            console.print(f"[dim]Edit the file manually, then run:[/dim]")
            console.print(f"[cyan]  git add .doit/memory/{resolved.file_path}[/cyan]")

    except ConflictNotFoundError:
        console.print(f"[red]Error:[/red] Conflict not found: {conflict_id}")
        raise typer.Exit(code=1)


@conflict_app.command("clear")
def clear_conflicts(
    force: bool = typer.Option(
        False,
        "--force", "-f",
        help="Skip confirmation prompt",
    ),
) -> None:
    """Clear all active conflicts without resolving.

    WARNING: This discards conflict tracking without resolving files.

    Examples:
        doit team conflict clear --force
    """
    service = _get_service()
    _require_initialized(service)

    conflict_service = _get_conflict_service()

    active = conflict_service.get_active_conflicts()
    if not active:
        console.print("[dim]No active conflicts to clear.[/dim]")
        return

    if not force:
        console.print(f"[yellow]Warning:[/yellow] This will clear {len(active)} conflict(s) without resolving them.")
        confirm = typer.confirm("Continue?")
        if not confirm:
            console.print("Cancelled.")
            raise typer.Exit(code=0)

    count = conflict_service.clear_active_conflicts()
    console.print(f"[green]✓ Cleared {count} conflict(s)[/green]")


# =============================================================================
# T025: team config command
# =============================================================================


@app.command("config")
def team_config(
    format: str = typer.Option(
        "table",
        "--format", "-f",
        help="Output format: 'table', 'json', or 'yaml'",
    ),
    auto_sync: Optional[bool] = typer.Option(
        None,
        "--auto-sync/--no-auto-sync",
        help="Enable/disable automatic sync on file changes",
    ),
    sync_on_command: Optional[bool] = typer.Option(
        None,
        "--sync-on-command/--no-sync-on-command",
        help="Enable/disable sync before/after doit commands",
    ),
    conflict_strategy: Optional[str] = typer.Option(
        None,
        "--conflict-strategy",
        help="Conflict strategy: 'prompt', 'keep-local', or 'keep-remote'",
    ),
) -> None:
    """View or update team configuration settings.

    Without options, displays current settings.

    Examples:
        doit team config
        doit team config --format json
        doit team config --auto-sync
        doit team config --conflict-strategy keep-local
    """
    from doit_cli.services.access_service import AccessService, AccessDeniedError

    service = _get_service()
    _require_initialized(service)

    # Check if updating settings
    has_updates = any([
        auto_sync is not None,
        sync_on_command is not None,
        conflict_strategy is not None,
    ])

    if has_updates:
        # Require owner permission to change settings
        access_service = AccessService()
        if not access_service.check_manage_permission():
            console.print("[red]Error:[/red] Only team owners can modify settings.")
            raise typer.Exit(code=3)

        config = service.config

        if auto_sync is not None:
            config.sync.auto_sync = auto_sync
        if sync_on_command is not None:
            config.sync.sync_on_command = sync_on_command
        if conflict_strategy is not None:
            if conflict_strategy not in ["prompt", "keep-local", "keep-remote"]:
                console.print(f"[red]Error:[/red] Invalid conflict strategy: {conflict_strategy}")
                console.print("Valid options: prompt, keep-local, keep-remote")
                raise typer.Exit(code=1)
            config.sync.conflict_strategy = conflict_strategy

        service._save_config()
        console.print("[green]✓ Settings updated[/green]")
        console.print()

    # Display current configuration
    config = service.config
    team = config.team

    if format.lower() == "json":
        import json
        data = config.to_dict()
        console.print(json.dumps(data, indent=2, default=str))
        return

    if format.lower() == "yaml":
        import yaml
        data = config.to_dict()
        console.print(yaml.dump(data, default_flow_style=False))
        return

    # Table format
    console.print()
    console.print("[bold]Team Configuration[/bold]")
    console.print()

    # Team info
    console.print("[bold]Team:[/bold]")
    console.print(f"  Name: [cyan]{team.name}[/cyan]")
    console.print(f"  Owner: [cyan]{team.owner_id}[/cyan]")
    console.print(f"  ID: [dim]{team.id}[/dim]")
    console.print(f"  Created: [dim]{_format_time_ago(team.created_at)}[/dim]")
    console.print()

    # Member summary
    members = config.members
    owners = [m for m in members if m.is_owner]
    writers = [m for m in members if m.can_write and not m.is_owner]
    readers = [m for m in members if not m.can_write]

    console.print("[bold]Members:[/bold]")
    console.print(f"  Total: [cyan]{len(members)}[/cyan]")
    console.print(f"  Owners: [cyan]{len(owners)}[/cyan]")
    console.print(f"  Read-write: [cyan]{len(writers)}[/cyan]")
    console.print(f"  Read-only: [cyan]{len(readers)}[/cyan]")
    console.print()

    # Sync settings
    sync = config.sync
    console.print("[bold]Sync Settings:[/bold]")
    console.print(f"  Auto sync: {'[green]✓ Enabled[/green]' if sync.auto_sync else '[dim]✗ Disabled[/dim]'}")
    console.print(f"  Sync on command: {'[green]✓ Enabled[/green]' if sync.sync_on_command else '[dim]✗ Disabled[/dim]'}")
    console.print(f"  Conflict strategy: [cyan]{sync.conflict_strategy}[/cyan]")
    console.print()

    # Shared files
    shared = config.shared_files
    console.print("[bold]Shared Files:[/bold]")
    if shared:
        for sf in shared:
            console.print(f"  • {sf.path}")
    else:
        console.print("  [dim]No shared files configured[/dim]")
    console.print()

    # Show current user permissions
    access_service = AccessService()
    context = access_service.get_access_context()

    console.print("[bold]Your Access:[/bold]")
    if context.is_member:
        console.print(f"  Email: [cyan]{context.user_email}[/cyan]")
        console.print(f"  Level: [cyan]{context.permission_level}[/cyan]")
        console.print(f"  Can push: {'[green]✓[/green]' if context.can_write else '[red]✗[/red]'}")
        console.print(f"  Can manage: {'[green]✓[/green]' if context.is_owner else '[red]✗[/red]'}")
    else:
        console.print(f"  [yellow]Not a team member[/yellow]")
        console.print(f"  [dim]Email: {context.user_email or 'unknown'}[/dim]")
