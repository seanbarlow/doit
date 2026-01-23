"""Wizard service for interactive provider configuration.

This module provides a step-by-step wizard for configuring git provider
authentication and settings.
"""

import os
import subprocess
from datetime import datetime, UTC
from typing import Any, Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from ..models.wizard_models import (
    ValidationResult,
    WizardCancelledError,
    WizardResult,
    WizardState,
    WizardStep,
    WizardStepError,
)
from .config_backup_service import ConfigBackupService
from .provider_config import ProviderConfig
from .provider_factory import ProviderFactory
from .provider_validation_service import ProviderValidationService
from .providers.base import ProviderType

# Version of the wizard (for tracking)
WIZARD_VERSION = "0.1.12"


class WizardService:
    """Manages the provider configuration wizard flow."""

    def __init__(
        self,
        console: Console,
        validation_service: Optional[ProviderValidationService] = None,
        backup_service: Optional[ConfigBackupService] = None,
        existing_config: Optional[ProviderConfig] = None,
    ) -> None:
        """Initialize wizard with dependencies.

        Args:
            console: Rich console for output
            validation_service: Service for validating credentials
            backup_service: Service for config backups
            existing_config: Existing provider configuration
        """
        self.console = console
        self.validation = validation_service or ProviderValidationService()
        self.backup = backup_service or ConfigBackupService()
        self.existing_config = existing_config or ProviderConfig.load()
        self.state: Optional[WizardState] = None
        self._backup_created = False

    def run(self, force_reconfigure: bool = False) -> WizardResult:
        """Execute the wizard flow from start to completion.

        Args:
            force_reconfigure: If True, skip confirmation when existing config found

        Returns:
            WizardResult with success status and resulting configuration

        Raises:
            WizardCancelledError: User cancelled the wizard
        """
        self._display_header()

        # Initialize state
        self.state = WizardState(current_step=WizardStep.DETECT_PROVIDER)

        # Check for existing configuration
        if self.existing_config.is_configured():
            if not force_reconfigure:
                if not self._confirm_reconfigure():
                    return WizardResult.canceled()

            # Create backup before changes (always, whether forced or confirmed)
            backup = self.backup.create_backup(
                self.existing_config,
                reason="reconfigure",
            )
            self._backup_created = True
            self.console.print(f"[dim]Backup created: {backup.backup_id}[/dim]\n")

        # Detect or select provider
        detected, source = self.detect_provider()
        self.state.auto_detected = detected is not None
        self.state.detection_source = source

        provider = self.select_provider(detected)
        self.state.provider_type = provider

        # Collect provider-specific configuration
        try:
            if provider == ProviderType.GITHUB:
                config_values = self.collect_github_config()
            elif provider == ProviderType.AZURE_DEVOPS:
                config_values = self.collect_azure_devops_config()
            elif provider == ProviderType.GITLAB:
                config_values = self.collect_gitlab_config()
            else:
                return WizardResult.error(f"Unsupported provider: {provider}")

            self.state.collected_values = config_values

        except WizardStepError as e:
            self.console.print(f"[red]Error: {e.message}[/red]")
            if e.suggestion:
                self.console.print(f"[yellow]Suggestion: {e.suggestion}[/yellow]")
            return WizardResult.error(e.message)

        # Validate and save
        result = self.validate_and_save(provider, config_values)

        if result.success:
            self.display_summary(provider, config_values, result)
            return WizardResult.completed(provider)
        else:
            return WizardResult.error(result.error_message or "Validation failed")

    def detect_provider(self) -> tuple[Optional[ProviderType], Optional[str]]:
        """Detect provider from git remote URL.

        Returns:
            Tuple of (provider_type, detection_source) or (None, None)
        """
        detected = ProviderFactory.detect_provider()
        if detected:
            self.console.print(
                f"[green]Detected provider: {self._provider_name(detected)}[/green]\n"
            )
            return detected, "git_remote"

        self.console.print(
            "[yellow]Could not auto-detect provider from git remote.[/yellow]\n"
        )
        return None, None

    def select_provider(self, detected: Optional[ProviderType]) -> ProviderType:
        """Interactive provider selection with detected provider as default.

        Args:
            detected: Auto-detected provider if any

        Returns:
            Selected ProviderType
        """
        if detected:
            use_detected = Confirm.ask(
                f"Use detected provider ({self._provider_name(detected)})?",
                default=True,
            )
            if use_detected:
                return detected

        self.console.print("\n[bold]Available providers:[/bold]")
        self.console.print("  1. GitHub")
        self.console.print("  2. Azure DevOps")
        self.console.print("  3. GitLab [dim](limited support)[/dim]")

        choice = Prompt.ask(
            "Select provider",
            choices=["1", "2", "3"],
            default="1",
        )

        provider_map = {
            "1": ProviderType.GITHUB,
            "2": ProviderType.AZURE_DEVOPS,
            "3": ProviderType.GITLAB,
        }

        return provider_map[choice]

    def collect_github_config(self) -> dict[str, Any]:
        """Collect GitHub-specific configuration.

        Returns:
            Dict with auth_method and optional enterprise_host

        Raises:
            WizardStepError: gh CLI not installed or not authenticated
        """
        self.console.print(
            Panel("[bold]GitHub Configuration[/bold]", expand=False)
        )

        # Check gh CLI installed
        if not self.validation.check_gh_cli_installed():
            self.console.print("[red]GitHub CLI (gh) is not installed.[/red]")
            self.console.print(
                "\n[yellow]To install gh CLI:[/yellow]\n"
                "  • macOS: brew install gh\n"
                "  • Linux: https://github.com/cli/cli/blob/trunk/docs/install_linux.md\n"
                "  • Windows: winget install --id GitHub.cli\n"
                "\nOr visit: https://cli.github.com"
            )

            retry = Confirm.ask("\nRetry after installing?", default=True)
            if retry and self.validation.check_gh_cli_installed():
                pass  # Continue
            else:
                raise WizardStepError(
                    step=WizardStep.GITHUB_CHECK_CLI,
                    message="GitHub CLI (gh) is not installed",
                    suggestion="Install from https://cli.github.com",
                )

        # Check gh authenticated
        is_authed, username = self.validation.check_gh_cli_authenticated()
        if not is_authed:
            self.console.print("[red]GitHub CLI is not authenticated.[/red]")
            self.console.print(
                "\n[yellow]Run this command to authenticate:[/yellow]\n"
                "  gh auth login"
            )

            retry = Confirm.ask("\nRetry after authenticating?", default=True)
            if retry:
                is_authed, username = self.validation.check_gh_cli_authenticated()

            if not is_authed:
                raise WizardStepError(
                    step=WizardStep.GITHUB_CHECK_CLI,
                    message="GitHub CLI is not authenticated",
                    suggestion="Run 'gh auth login' to authenticate",
                )

        self.console.print(f"[green]Authenticated as: {username}[/green]\n")

        # GitHub Enterprise?
        enterprise_host = None
        is_enterprise = Confirm.ask("Are you using GitHub Enterprise?", default=False)
        if is_enterprise:
            enterprise_host = Prompt.ask("GitHub Enterprise host (e.g., github.mycompany.com)")

        return {
            "auth_method": "gh_cli",
            "enterprise_host": enterprise_host,
        }

    def collect_azure_devops_config(self) -> dict[str, Any]:
        """Collect Azure DevOps-specific configuration.

        Returns:
            Dict with organization, project, and auth info
        """
        self.console.print(
            Panel("[bold]Azure DevOps Configuration[/bold]", expand=False)
        )

        # Check for PAT in environment
        pat_from_env = os.environ.get("AZURE_DEVOPS_PAT")
        if pat_from_env:
            self.console.print(
                "[green]Found AZURE_DEVOPS_PAT environment variable[/green]\n"
            )

        # Organization
        organization = Prompt.ask("Organization name")
        while not organization.strip():
            self.console.print("[red]Organization name is required[/red]")
            organization = Prompt.ask("Organization name")

        # Project
        project = Prompt.ask("Project name")
        while not project.strip():
            self.console.print("[red]Project name is required[/red]")
            project = Prompt.ask("Project name")

        # PAT
        if pat_from_env:
            use_env_pat = Confirm.ask(
                "Use PAT from AZURE_DEVOPS_PAT environment variable?",
                default=True,
            )
            if use_env_pat:
                pat = pat_from_env
            else:
                pat = Prompt.ask("Personal Access Token", password=True)
        else:
            self.console.print(
                "\n[dim]Required PAT scopes: Code (Read & Write), Work Items (Read & Write)[/dim]"
            )
            self.console.print(
                f"[dim]Create PAT at: https://dev.azure.com/{organization}/_usersSettings/tokens[/dim]\n"
            )
            pat = Prompt.ask("Personal Access Token", password=True)

        return {
            "organization": organization.strip(),
            "project": project.strip(),
            "pat": pat,
            "api_version": "7.0",
        }

    def collect_gitlab_config(self) -> dict[str, Any]:
        """Collect GitLab-specific configuration.

        Returns:
            Dict with host and auth info
        """
        self.console.print(
            Panel("[bold]GitLab Configuration[/bold]", expand=False)
        )

        self.console.print(
            "[yellow]Note: GitLab support is currently limited (stub implementation).[/yellow]\n"
        )

        # Host
        host = Prompt.ask("GitLab host", default="gitlab.com")

        # Token
        self.console.print(
            "\n[dim]Required token scopes: api, read_repository[/dim]"
        )
        if "gitlab.com" in host:
            self.console.print(
                "[dim]Create token at: https://gitlab.com/-/profile/personal_access_tokens[/dim]\n"
            )
        else:
            self.console.print(
                f"[dim]Create token at: https://{host}/-/profile/personal_access_tokens[/dim]\n"
            )

        token = Prompt.ask("Personal Access Token", password=True)

        return {
            "host": host,
            "token": token,
        }

    def validate_and_save(
        self,
        provider: ProviderType,
        config_values: dict[str, Any],
    ) -> ValidationResult:
        """Validate configuration and save if successful.

        Args:
            provider: The provider type
            config_values: Collected configuration values

        Returns:
            ValidationResult with success status and details
        """
        self.console.print("\n")

        with self.console.status("[bold]Validating credentials...[/bold]"):
            result = self.validation.validate_provider(provider, config_values)

        if self.state:
            self.state.add_validation(result)

        if not result.success:
            self.console.print(f"[red]Validation failed: {result.error_message}[/red]")
            if result.suggestion:
                self.console.print(f"[yellow]{result.suggestion}[/yellow]")

            # Offer options
            self.console.print("\n[bold]Options:[/bold]")
            self.console.print("  1. Retry validation")
            self.console.print("  2. Save anyway (not recommended)")
            self.console.print("  3. Cancel")

            choice = Prompt.ask("Select option", choices=["1", "2", "3"], default="1")

            if choice == "1":
                return self.validate_and_save(provider, config_values)
            elif choice == "3":
                raise WizardCancelledError()
            # choice == "2": continue to save

        # Build and save ProviderConfig
        config = self._build_config(provider, config_values, result)
        config.save()

        self.console.print("[green]Configuration saved successfully![/green]")

        return result

    def display_summary(
        self,
        provider: ProviderType,
        config_values: dict[str, Any],
        validation: ValidationResult,
    ) -> None:
        """Display configuration summary after completion."""
        table = Table(show_header=False, box=None)
        table.add_column("Property", style="cyan")
        table.add_column("Value")

        table.add_row("Provider", self._provider_name(provider))

        if provider == ProviderType.GITHUB:
            table.add_row("Auth Method", "gh CLI")
            if config_values.get("enterprise_host"):
                table.add_row("Enterprise Host", config_values["enterprise_host"])
            if validation.details.get("authenticated_user"):
                table.add_row("Authenticated", validation.details["authenticated_user"])
            has_access = validation.details.get("has_repo_access", False)
            table.add_row(
                "Repository Access",
                "[green]✓ Verified[/green]" if has_access else "[yellow]Not verified[/yellow]",
            )

        elif provider == ProviderType.AZURE_DEVOPS:
            table.add_row("Organization", config_values.get("organization", ""))
            table.add_row("Project", config_values.get("project", ""))
            table.add_row("Auth Method", "PAT")
            scopes = validation.details.get("detected_scopes", [])
            if scopes:
                table.add_row("Detected Scopes", ", ".join(scopes))

        elif provider == ProviderType.GITLAB:
            table.add_row("Host", config_values.get("host", "gitlab.com"))
            if validation.details.get("authenticated_user"):
                table.add_row("Authenticated", validation.details["authenticated_user"])
            table.add_row("Feature Support", "[yellow]Limited[/yellow]")

        self.console.print(
            Panel(table, title="[bold green]Configuration Complete[/bold green]")
        )

    def handle_cancellation(self) -> None:
        """Handle user cancellation, restore previous state if needed."""
        if self._backup_created:
            latest = self.backup.get_latest_backup()
            if latest:
                try:
                    config = self.backup.restore_backup(latest.backup_id)
                    config.save()
                    self.console.print(
                        "[dim]Previous configuration restored from backup.[/dim]"
                    )
                except Exception:
                    pass

    def _display_header(self) -> None:
        """Display wizard header."""
        self.console.print(
            Panel(
                "[bold]Git Provider Configuration Wizard[/bold]\n\n"
                "This wizard will guide you through configuring your git provider.",
                title="Welcome",
            )
        )
        self.console.print()

    def _confirm_reconfigure(self) -> bool:
        """Ask user to confirm reconfiguration."""
        current_provider = self.existing_config.get_provider_display_name()
        self.console.print(
            f"[yellow]Existing configuration found: {current_provider}[/yellow]\n"
        )
        return Confirm.ask("Do you want to reconfigure?", default=False)

    def _provider_name(self, provider: ProviderType) -> str:
        """Get display name for provider."""
        names = {
            ProviderType.GITHUB: "GitHub",
            ProviderType.AZURE_DEVOPS: "Azure DevOps",
            ProviderType.GITLAB: "GitLab",
        }
        return names.get(provider, provider.value)

    def _build_config(
        self,
        provider: ProviderType,
        config_values: dict[str, Any],
        validation: ValidationResult,
    ) -> ProviderConfig:
        """Build ProviderConfig from collected values."""
        config = ProviderConfig()
        config.provider = provider
        config.auto_detected = self.state.auto_detected if self.state else False
        config.detection_source = self.state.detection_source if self.state else None
        config.validated_at = datetime.now(UTC) if validation.success else None
        config.configured_by = "wizard"
        config.wizard_version = WIZARD_VERSION

        if provider == ProviderType.GITHUB:
            config.github.auth_method = config_values.get("auth_method", "gh_cli")
            config.github.enterprise_host = config_values.get("enterprise_host")

        elif provider == ProviderType.AZURE_DEVOPS:
            config.azure_devops.organization = config_values.get("organization", "")
            config.azure_devops.project = config_values.get("project", "")
            config.azure_devops.auth_method = "pat"
            config.azure_devops.api_version = config_values.get("api_version", "7.0")

        elif provider == ProviderType.GITLAB:
            config.gitlab.host = config_values.get("host", "gitlab.com")
            config.gitlab.auth_method = "token"

        return config
