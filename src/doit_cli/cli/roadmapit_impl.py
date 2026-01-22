"""Roadmapit command for managing project roadmap with GitHub integration.

This command provides roadmap management with bidirectional GitHub sync,
allowing users to view GitHub epics alongside local roadmap items.
"""

import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table

from ..models.roadmap import RoadmapItem
from ..models.sync_metadata import SyncMetadata
from ..services.github_service import (
    GitHubService,
    GitHubAuthError,
    GitHubAPIError,
)
from ..services.github_cache_service import GitHubCacheService, CacheError
from ..services.roadmap_merge_service import RoadmapMergeService
from ..utils.github_auth import get_github_config_status, get_repository_name

app = typer.Typer(help="Manage project roadmap with GitHub epic integration")
console = Console()


@app.command()
def show(
    skip_github: bool = typer.Option(
        False,
        "--skip-github",
        help="Skip GitHub synchronization and use only local roadmap data"
    ),
    refresh: bool = typer.Option(
        False,
        "--refresh",
        help="Force refresh from GitHub API, bypassing cache"
    ),
):
    """Display the project roadmap with GitHub epic integration.

    Fetches open GitHub epics and displays them alongside local roadmap items.
    Uses cached data when available to minimize API calls. Supports offline mode.

    Examples:
        # Display roadmap with GitHub sync
        doit roadmapit

        # Skip GitHub and show only local items
        doit roadmapit --skip-github

        # Force refresh from GitHub API
        doit roadmapit --refresh
    """
    try:
        # Load local roadmap items (placeholder - would parse .doit/memory/roadmap.md)
        local_items = _load_local_roadmap()

        github_epics = []
        cache_used = False
        github_available = False

        if not skip_github:
            # Check GitHub configuration
            is_configured, status_message = get_github_config_status()

            if is_configured:
                github_available = True
                github_epics, cache_used = _fetch_github_epics(refresh)
            else:
                console.print(
                    f"[yellow]ℹ GitHub integration unavailable: {status_message}[/yellow]"
                )
                console.print("[yellow]  Showing local roadmap items only[/yellow]\n")

        # Merge local and GitHub items
        if github_epics:
            merge_service = RoadmapMergeService()
            merged_items = merge_service.merge_roadmap_items(local_items, github_epics)
        else:
            merged_items = local_items

        # Display roadmap
        _display_roadmap(merged_items, github_available, cache_used)

        # Show summary
        _display_summary(merged_items, github_available)

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(code=1)


def _fetch_github_epics(refresh: bool):
    """Fetch GitHub epics from API or cache.

    Args:
        refresh: If True, bypass cache and fetch from API

    Returns:
        Tuple of (list of GitHubEpic, cache_used_bool)
    """
    cache_service = GitHubCacheService()
    github_service = GitHubService()

    # Try cache first (unless refresh requested)
    if not refresh and cache_service.is_valid():
        epics = cache_service.get_epics()
        if epics is not None:
            cache_age = cache_service.get_cache_age_minutes()
            console.print(
                f"[dim]Using cached GitHub data ({cache_age:.1f} minutes old)[/dim]\n"
            )
            return epics, True

    # Fetch from GitHub API
    try:
        console.print("[dim]Fetching GitHub epics...[/dim]")
        epics = github_service.fetch_epics(state="open")

        # Fetch features for each epic
        for epic in epics:
            try:
                features = github_service.fetch_features_for_epic(epic.number)
                epic.features = features
            except Exception as e:
                # Log warning but continue with other epics
                console.print(f"[dim yellow]Warning: Failed to fetch features for epic #{epic.number}: {e}[/dim yellow]")
                epic.features = []

        # Save to cache
        repo_url = f"https://github.com/{get_repository_name()}"
        metadata = SyncMetadata.create_new(repo_url)
        cache_service.save_cache(epics, metadata)

        feature_count = sum(len(epic.features) for epic in epics)
        console.print(f"[dim]Found {len(epics)} open epic(s) with {feature_count} linked feature(s) on GitHub[/dim]\n")
        return epics, False

    except GitHubAuthError as e:
        console.print(f"[yellow]⚠ GitHub authentication error: {e}[/yellow]")
        console.print("[yellow]  Checking cache for offline mode...[/yellow]\n")

        # Try to use stale cache
        epics = cache_service.get_epics()
        if epics:
            console.print("[yellow]  Using stale cached data (offline mode)[/yellow]\n")
            return epics, True

        console.print("[yellow]  No cached data available[/yellow]\n")
        return [], False

    except GitHubAPIError as e:
        console.print(f"[yellow]⚠ GitHub API error: {e}[/yellow]")

        # Try to use cache as fallback
        epics = cache_service.get_epics()
        if epics:
            console.print("[yellow]  Using cached data as fallback[/yellow]\n")
            return epics, True

        return [], False

    except CacheError as e:
        console.print(f"[yellow]⚠ Cache error: {e}[/yellow]")
        console.print("[yellow]  Continuing without cache...[/yellow]\n")
        return [], False


def _load_local_roadmap() -> list[RoadmapItem]:
    """Load roadmap items from local .doit/memory/roadmap.md file.

    Returns:
        List of RoadmapItem instances from local file

    Note:
        This is a placeholder implementation. Full parsing of roadmap.md
        would be implemented here in production.
    """
    # TODO: Implement full roadmap.md parser
    # For now, return empty list (GitHub epics will be shown)
    return []


def _display_roadmap(
    items: list[RoadmapItem],
    github_available: bool,
    cache_used: bool
):
    """Display merged roadmap items in a formatted table.

    Args:
        items: List of merged roadmap items
        github_available: Whether GitHub integration was available
        cache_used: Whether cached data was used
    """
    if not items:
        console.print("[yellow]No roadmap items found[/yellow]")
        return

    # Group by priority
    by_priority = {}
    for item in items:
        if item.priority not in by_priority:
            by_priority[item.priority] = []
        by_priority[item.priority].append(item)

    # Display each priority section
    for priority in ["P1", "P2", "P3", "P4"]:
        if priority not in by_priority:
            continue

        priority_items = by_priority[priority]

        # Create table
        table = Table(
            title=f"\n{priority} - {_get_priority_name(priority)}",
            show_header=True,
            header_style="bold cyan"
        )
        table.add_column("Title", style="white", no_wrap=False)
        table.add_column("Source", style="dim", width=10)
        table.add_column("Status", style="green", width=12)

        for item in priority_items:
            source_icon = _get_source_icon(item.source)
            status_str = item.status
            if item.github_url:
                title = f"{item.title}\n[dim]{item.github_url}[/dim]"
            else:
                title = item.title

            table.add_row(title, source_icon, status_str)

            # Display linked features as sub-items
            if item.features:
                for feature in item.features:
                    feature_title = f"  ↳ {feature.title}"
                    if feature.url:
                        feature_title += f"\n    [dim]{feature.url}[/dim]"
                    feature_status = "open" if feature.is_open else "closed"
                    table.add_row(feature_title, "[dim]Feature[/dim]", feature_status)

        console.print(table)


def _display_summary(items: list[RoadmapItem], github_available: bool):
    """Display summary statistics.

    Args:
        items: List of roadmap items
        github_available: Whether GitHub integration was available
    """
    console.print("\n[bold]Summary:[/bold]")
    console.print(f"  Total items: {len(items)}")

    # Count by source
    sources = {}
    for item in items:
        sources[item.source] = sources.get(item.source, 0) + 1

    if "local" in sources:
        console.print(f"  Local items: {sources['local']}")
    if "github" in sources:
        console.print(f"  GitHub epics: {sources['github']}")
    if "merged" in sources:
        console.print(f"  Merged items: {sources['merged']}")

    if github_available:
        console.print("\n[dim]GitHub integration: ✓ Active[/dim]")
    else:
        console.print("\n[dim]GitHub integration: ✗ Unavailable[/dim]")


def _get_priority_name(priority: str) -> str:
    """Get human-readable priority name.

    Args:
        priority: Priority code (P1-P4)

    Returns:
        Human-readable name
    """
    names = {
        "P1": "Critical (Must Have for MVP)",
        "P2": "High Priority (Significant Business Value)",
        "P3": "Medium Priority (Valuable)",
        "P4": "Low Priority (Nice to Have)",
    }
    return names.get(priority, "Unknown Priority")


def _get_source_icon(source: str) -> str:
    """Get icon for item source.

    Args:
        source: Source type (local, github, merged)

    Returns:
        Icon string
    """
    icons = {
        "local": "📝 Local",
        "github": "🔗 GitHub",
        "merged": "🔄 Merged",
    }
    return icons.get(source, source)


@app.command()
def add(
    item: str = typer.Argument(..., help="Roadmap item title to add"),
    priority: str = typer.Option(
        "P3",
        "--priority",
        "-p",
        help="Priority level (P1, P2, P3, or P4)"
    ),
    description: str = typer.Option(
        "",
        "--description",
        "-d",
        help="Detailed description of the roadmap item"
    ),
    skip_github: bool = typer.Option(
        False,
        "--skip-github",
        help="Skip creating GitHub epic"
    ),
):
    """Add a new item to the roadmap.

    Creates a GitHub epic if GitHub is configured, otherwise just displays
    a message with the item details.

    Examples:
        doit roadmapit add "New authentication feature"
        doit roadmapit add "User dashboard" --priority P1 --description "Dashboard for users"
        doit roadmapit add "Nice to have feature" --skip-github
    """
    try:
        # Validate priority
        if priority not in ("P1", "P2", "P3", "P4"):
            console.print(f"[red]✗ Invalid priority: {priority}. Must be P1, P2, P3, or P4[/red]")
            raise typer.Exit(code=1)

        console.print(f"\n[bold]Adding roadmap item:[/bold]")
        console.print(f"  Title: {item}")
        console.print(f"  Priority: {priority}")
        if description:
            console.print(f"  Description: {description}")

        # Check if we should create GitHub epic
        if not skip_github:
            is_configured, status_message = get_github_config_status()

            if is_configured:
                console.print(f"\n[dim]Creating GitHub epic...[/dim]")

                try:
                    github_service = GitHubService()

                    # Format title with Epic prefix if not already present
                    epic_title = item if item.startswith("[Epic]:") else f"[Epic]: {item}"
                    epic_body = description or f"Roadmap item created via doit roadmapit add"

                    # Create the epic
                    epic = github_service.create_epic(
                        title=epic_title,
                        body=epic_body,
                        priority=priority
                    )

                    console.print(f"\n[green]✓ Created GitHub epic #{epic.number}[/green]")
                    console.print(f"  URL: {epic.url}")
                    console.print(f"\n[dim]Next steps:[/dim]")
                    console.print(f"  1. The epic is now live on GitHub")
                    console.print(f"  2. Run 'doit roadmapit' to see it in your roadmap")
                    console.print(f"  3. Add feature issues and link them with 'Part of Epic #{epic.number}' in the description")

                except GitHubAuthError as e:
                    console.print(f"\n[yellow]⚠ GitHub authentication error: {e}[/yellow]")
                    console.print(f"[yellow]  Item not created on GitHub[/yellow]")
                    console.print(f"\n[dim]Note: You can manually create the epic on GitHub with:[/dim]")
                    console.print(f"  Title: {item}")
                    console.print(f"  Labels: epic, priority:{priority}")
                    raise typer.Exit(code=1)

                except GitHubAPIError as e:
                    console.print(f"\n[yellow]⚠ GitHub API error: {e}[/yellow]")
                    console.print(f"[yellow]  Item not created on GitHub[/yellow]")
                    raise typer.Exit(code=1)

            else:
                console.print(f"\n[yellow]ℹ GitHub integration unavailable: {status_message}[/yellow]")
                console.print(f"[yellow]  Epic not created on GitHub[/yellow]")
                console.print(f"\n[dim]To create this epic on GitHub:[/dim]")
                console.print(f"  1. Configure GitHub CLI authentication")
                console.print(f"  2. Run this command again")
        else:
            console.print(f"\n[dim]Skipped GitHub epic creation (--skip-github flag)[/dim]")
            console.print(f"\n[dim]To create this epic on GitHub later:[/dim]")
            console.print(f"  Run: doit roadmapit add \"{item}\" --priority {priority}")

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(code=1)


@app.command(name="sync-milestones")
def sync_milestones(
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Preview changes without executing them"
    ),
):
    """Sync roadmap priorities to GitHub milestones.

    Automatically creates GitHub milestones for each roadmap priority level (P1-P4)
    if they don't exist. Provides GitHub-native view of roadmap priorities.

    Examples:
        # Sync priorities to GitHub milestones
        doit roadmapit sync-milestones

        # Preview changes without executing
        doit roadmapit sync-milestones --dry-run
    """
    try:
        from datetime import datetime
        from ..models.sync_operation import SyncOperation
        from ..services.milestone_service import MilestoneService

        if dry_run:
            console.print("\n🔍 [bold yellow]DRY RUN - No changes will be made[/bold yellow]\n")
        else:
            console.print("\n🚀 [bold]Syncing roadmap priorities to GitHub milestones...[/bold]\n")

        # Create sync operation
        sync_id = f"sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        sync_op = SyncOperation(
            id=sync_id,
            started_at=datetime.now(),
            dry_run=dry_run
        )

        # Initialize services
        github_service = GitHubService()
        milestone_service = MilestoneService(github_service, dry_run=dry_run)

        # Create missing milestones
        console.print("[bold]Creating missing priority milestones...[/bold]")
        all_milestones = milestone_service.create_missing_milestones(sync_op)

        # Extract epic references from roadmap
        console.print("\n[bold]Assigning epics to priority milestones...[/bold]")
        epic_by_priority = milestone_service.extract_epic_references()

        # Assign epics to their corresponding milestones
        milestone_service.assign_epics_to_milestones(epic_by_priority, all_milestones, sync_op)

        # Mark sync as complete
        sync_op.completed_at = datetime.now()

        # Display summary
        console.print(f"\n{sync_op.get_summary()}")

        if sync_op.milestones_created > 0:
            console.print(f"\n[green]✓ Sync complete![/green]")
            # Get repo name for URL
            repo_name = get_repository_name()
            if repo_name:
                console.print(f"\nView milestones: https://github.com/{repo_name}/milestones")
        else:
            console.print(f"\n[dim]All priority milestones already exist.[/dim]")

    except GitHubAuthError as e:
        console.print(f"\n[red]✗ GitHub Authentication Error:[/red] {e}")
        console.print("\n[dim]Run: gh auth login[/dim]")
        raise typer.Exit(code=1)
    except GitHubAPIError as e:
        console.print(f"\n[red]✗ GitHub API Error:[/red] {e}")
        raise typer.Exit(code=1)
    except FileNotFoundError as e:
        console.print(f"\n[red]✗ File Not Found:[/red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"\n[red]✗ Error:[/red] {e}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
