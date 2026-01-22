"""CLI commands for git provider management.

This module provides commands for configuring and managing
git provider settings.
"""

from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..models.wizard_models import WizardCancelledError
from ..services.config_backup_service import ConfigBackupService
from ..services.provider_config import ProviderConfig
from ..services.provider_factory import ProviderFactory
from ..services.provider_validation_service import ProviderValidationService
from ..services.providers.base import ProviderType
from ..services.wizard_service import WizardService

app = typer.Typer(
    name="provider",
    help="Git provider management commands",
    no_args_is_help=True,
)

console = Console()


@app.command(name="configure")
def configure_command(
    provider: Optional[str] = typer.Option(
        None,
        "--provider",
        "-p",
        help="Provider to configure: github, azure_devops, gitlab",
    ),
    organization: Optional[str] = typer.Option(
        None,
        "--organization",
        "-o",
        help="Azure DevOps organization name",
    ),
    project: Optional[str] = typer.Option(
        None,
        "--project",
        help="Azure DevOps project name",
    ),
    auto_detect: bool = typer.Option(
        False,
        "--auto-detect",
        "-a",
        help="Auto-detect provider from git remote URL",
    ),
) -> None:
    """Configure the git provider for this project.

    If no options are provided, the command will attempt to auto-detect
    the provider from the git remote URL.

    Examples:
        # Auto-detect provider
        doit provider configure --auto-detect

        # Explicit GitHub
        doit provider configure --provider github

        # Azure DevOps
        doit provider configure --provider azure_devops -o myorg --project myproject
    """
    config = ProviderConfig()

    if provider:
        # Explicit provider specified
        try:
            config.provider = ProviderType(provider.lower())
            config.auto_detected = False
        except ValueError:
            console.print(
                f"[red]Error: Unknown provider '{provider}'[/red]"
            )
            console.print(
                "Valid providers: github, azure_devops, gitlab"
            )
            raise typer.Exit(code=1)

    elif auto_detect or not provider:
        # Auto-detect from git remote
        detected = ProviderFactory.detect_provider()
        if detected:
            config.provider = detected
            config.auto_detected = True
            config.detection_source = "git_remote"
            console.print(
                f"[green]Auto-detected provider: {config.get_provider_display_name()}[/green]"
            )
        else:
            # Interactive selection
            console.print(
                "[yellow]Could not auto-detect provider from git remote.[/yellow]"
            )
            console.print("\nAvailable providers:")
            console.print("  1. GitHub")
            console.print("  2. Azure DevOps")
            console.print("  3. GitLab (stub - not fully implemented)")
            console.print("  4. None (skip provider configuration)")

            choice = typer.prompt(
                "Select provider",
                type=int,
                default=1,
            )

            provider_map = {
                1: ProviderType.GITHUB,
                2: ProviderType.AZURE_DEVOPS,
                3: ProviderType.GITLAB,
            }

            if choice == 4:
                console.print("[yellow]Skipping provider configuration.[/yellow]")
                return

            if choice not in provider_map:
                console.print("[red]Invalid choice[/red]")
                raise typer.Exit(code=1)

            config.provider = provider_map[choice]
            config.auto_detected = False

    # Handle Azure DevOps-specific configuration
    if config.provider == ProviderType.AZURE_DEVOPS:
        if not organization:
            organization = typer.prompt("Azure DevOps organization")
        if not project:
            project = typer.prompt("Azure DevOps project")

        config.azure_devops.organization = organization
        config.azure_devops.project = project

    # Save configuration
    config.save()

    console.print(
        Panel(
            f"[green]Provider configured: {config.get_provider_display_name()}[/green]",
            title="Configuration Saved",
        )
    )

    # Show next steps
    console.print("\n[dim]Next steps:[/dim]")
    if config.provider == ProviderType.GITHUB:
        console.print("  • Ensure you're authenticated: gh auth status")
    elif config.provider == ProviderType.AZURE_DEVOPS:
        console.print("  • Set AZURE_DEVOPS_PAT environment variable with your Personal Access Token")
    elif config.provider == ProviderType.GITLAB:
        console.print("  • [yellow]Note: GitLab support is not fully implemented yet[/yellow]")
        console.print("  • Set GITLAB_TOKEN environment variable when available")


@app.command(name="status")
def status_command() -> None:
    """Show current provider configuration and status.

    Displays the configured provider, its settings, and
    whether it's currently available.
    """
    config = ProviderConfig.load()

    # Create status table
    table = Table(title="Git Provider Status", show_header=False)
    table.add_column("Property", style="cyan")
    table.add_column("Value")

    # Provider info
    table.add_row("Provider", config.get_provider_display_name())
    table.add_row("Auto-detected", "Yes" if config.auto_detected else "No")

    if config.detection_source:
        table.add_row("Detection source", config.detection_source)

    # Provider-specific info
    if config.provider == ProviderType.AZURE_DEVOPS:
        table.add_row("Organization", config.azure_devops.organization or "[dim]Not set[/dim]")
        table.add_row("Project", config.azure_devops.project or "[dim]Not set[/dim]")

    # Check availability
    if config.provider:
        try:
            provider = ProviderFactory.create(config)
            available = provider.is_available
            table.add_row(
                "Available",
                "[green]✓ Yes[/green]" if available else "[red]✗ No[/red]"
            )
        except Exception as e:
            table.add_row("Available", f"[red]✗ Error: {e}[/red]")
    else:
        table.add_row("Available", "[dim]N/A (no provider configured)[/dim]")

    console.print(table)

    # Show configuration file path
    console.print(
        f"\n[dim]Configuration file: {ProviderConfig.CONFIG_PATH}[/dim]"
    )


@app.command(name="detect")
def detect_command() -> None:
    """Auto-detect the git provider from the repository remote.

    Examines the git remote URL and reports which provider
    would be detected without saving configuration.
    """
    detected = ProviderFactory.detect_provider()

    if detected:
        names = {
            ProviderType.GITHUB: "GitHub",
            ProviderType.AZURE_DEVOPS: "Azure DevOps",
            ProviderType.GITLAB: "GitLab",
        }
        console.print(
            f"[green]Detected provider: {names.get(detected, detected.value)}[/green]"
        )
        console.print(
            "\n[dim]Run 'doit provider configure --auto-detect' to save this configuration.[/dim]"
        )
    else:
        console.print(
            "[yellow]Could not detect provider from git remote URL.[/yellow]"
        )
        console.print(
            "\n[dim]Run 'doit provider configure' to manually select a provider.[/dim]"
        )


@app.command(name="wizard")
def wizard_command(
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Skip confirmation when reconfiguring existing provider",
    ),
) -> None:
    """Interactive wizard to configure git provider authentication.

    Guides you step-by-step through configuring your git provider
    (GitHub, Azure DevOps, or GitLab) with validation and helpful
    error messages.

    Examples:
        # Start the wizard
        doit provider wizard

        # Skip confirmation for existing config
        doit provider wizard --force
    """
    validation_service = ProviderValidationService()
    backup_service = ConfigBackupService()
    existing_config = ProviderConfig.load()

    wizard = WizardService(
        console=console,
        validation_service=validation_service,
        backup_service=backup_service,
        existing_config=existing_config,
    )

    try:
        result = wizard.run(force_reconfigure=force)

        if result.cancelled:
            console.print("\n[yellow]Wizard cancelled.[/yellow]")
            raise typer.Exit(code=0)

        if not result.success:
            console.print(f"\n[red]Configuration failed: {result.error_message}[/red]")
            raise typer.Exit(code=1)

    except WizardCancelledError:
        wizard.handle_cancellation()
        console.print("\n[yellow]Wizard cancelled.[/yellow]")
        raise typer.Exit(code=0)

    except KeyboardInterrupt:
        wizard.handle_cancellation()
        console.print("\n[yellow]Wizard interrupted.[/yellow]")
        raise typer.Exit(code=130)
