"""Unit tests for WizardService."""

from datetime import datetime, UTC
from unittest.mock import MagicMock, patch

import pytest
from rich.console import Console

from src.doit_cli.models.wizard_models import (
    ValidationResult,
    WizardCancelledError,
    WizardStep,
    WizardStepError,
)
from src.doit_cli.services.config_backup_service import ConfigBackupService
from src.doit_cli.services.provider_config import ProviderConfig
from src.doit_cli.services.provider_validation_service import ProviderValidationService
from src.doit_cli.services.providers.base import ProviderType
from src.doit_cli.services.wizard_service import WizardService


@pytest.fixture
def mock_console():
    """Create a mock console that suppresses output."""
    console = MagicMock(spec=Console)
    console.print = MagicMock()
    console.status = MagicMock()
    console.status.return_value.__enter__ = MagicMock()
    console.status.return_value.__exit__ = MagicMock()
    return console


@pytest.fixture
def mock_validation_service():
    """Create a mock validation service."""
    return MagicMock(spec=ProviderValidationService)


@pytest.fixture
def mock_backup_service():
    """Create a mock backup service."""
    return MagicMock(spec=ConfigBackupService)


@pytest.fixture
def empty_config():
    """Create an empty (unconfigured) ProviderConfig."""
    return ProviderConfig()


@pytest.fixture
def github_config():
    """Create a configured GitHub ProviderConfig."""
    config = ProviderConfig()
    config.provider = ProviderType.GITHUB
    config.github.auth_method = "gh_cli"
    return config


class TestCollectGitHubConfig:
    """Tests for collect_github_config() - T009, T010, T011."""

    def test_gh_cli_not_installed_shows_instructions(
        self, mock_console, mock_validation_service, mock_backup_service, empty_config
    ):
        """When gh CLI is not installed, show installation instructions."""
        mock_validation_service.check_gh_cli_installed.return_value = False

        wizard = WizardService(
            console=mock_console,
            validation_service=mock_validation_service,
            backup_service=mock_backup_service,
            existing_config=empty_config,
        )

        with patch("src.doit_cli.services.wizard_service.Confirm") as mock_confirm:
            mock_confirm.ask.return_value = False  # Don't retry

            with pytest.raises(WizardStepError) as exc_info:
                wizard.collect_github_config()

        assert exc_info.value.step == WizardStep.GITHUB_CHECK_CLI
        assert "not installed" in exc_info.value.message.lower()

    def test_gh_cli_not_authenticated_shows_instructions(
        self, mock_console, mock_validation_service, mock_backup_service, empty_config
    ):
        """When gh CLI is not authenticated, show auth instructions."""
        mock_validation_service.check_gh_cli_installed.return_value = True
        mock_validation_service.check_gh_cli_authenticated.return_value = (False, "Not logged in")

        wizard = WizardService(
            console=mock_console,
            validation_service=mock_validation_service,
            backup_service=mock_backup_service,
            existing_config=empty_config,
        )

        with patch("src.doit_cli.services.wizard_service.Confirm") as mock_confirm:
            mock_confirm.ask.return_value = False  # Don't retry

            with pytest.raises(WizardStepError) as exc_info:
                wizard.collect_github_config()

        assert exc_info.value.step == WizardStep.GITHUB_CHECK_CLI
        assert "not authenticated" in exc_info.value.message.lower()

    def test_gh_authenticated_returns_config(
        self, mock_console, mock_validation_service, mock_backup_service, empty_config
    ):
        """When gh CLI is authenticated, return config with auth method."""
        mock_validation_service.check_gh_cli_installed.return_value = True
        mock_validation_service.check_gh_cli_authenticated.return_value = (True, "testuser")

        wizard = WizardService(
            console=mock_console,
            validation_service=mock_validation_service,
            backup_service=mock_backup_service,
            existing_config=empty_config,
        )

        with patch("src.doit_cli.services.wizard_service.Confirm") as mock_confirm:
            mock_confirm.ask.return_value = False  # Not enterprise

            config = wizard.collect_github_config()

        assert config["auth_method"] == "gh_cli"
        assert config["enterprise_host"] is None

    def test_github_enterprise_prompts_for_host(
        self, mock_console, mock_validation_service, mock_backup_service, empty_config
    ):
        """When user selects enterprise, prompt for host."""
        mock_validation_service.check_gh_cli_installed.return_value = True
        mock_validation_service.check_gh_cli_authenticated.return_value = (True, "testuser")

        wizard = WizardService(
            console=mock_console,
            validation_service=mock_validation_service,
            backup_service=mock_backup_service,
            existing_config=empty_config,
        )

        with patch("src.doit_cli.services.wizard_service.Confirm") as mock_confirm:
            mock_confirm.ask.return_value = True  # Is enterprise
            with patch("src.doit_cli.services.wizard_service.Prompt") as mock_prompt:
                mock_prompt.ask.return_value = "github.mycompany.com"

                config = wizard.collect_github_config()

        assert config["auth_method"] == "gh_cli"
        assert config["enterprise_host"] == "github.mycompany.com"


class TestCollectAzureDevOpsConfig:
    """Tests for collect_azure_devops_config() - T014, T015, T016."""

    def test_prompts_for_organization_and_project(
        self, mock_console, mock_validation_service, mock_backup_service, empty_config
    ):
        """Prompts for organization, project, and PAT."""
        wizard = WizardService(
            console=mock_console,
            validation_service=mock_validation_service,
            backup_service=mock_backup_service,
            existing_config=empty_config,
        )

        with patch("src.doit_cli.services.wizard_service.Prompt") as mock_prompt:
            mock_prompt.ask.side_effect = ["myorg", "myproject", "secret-pat"]

            config = wizard.collect_azure_devops_config()

        assert config["organization"] == "myorg"
        assert config["project"] == "myproject"
        assert config["pat"] == "secret-pat"

    def test_detects_pat_from_environment(
        self, mock_console, mock_validation_service, mock_backup_service, empty_config
    ):
        """When AZURE_DEVOPS_PAT is set, offer to use it."""
        wizard = WizardService(
            console=mock_console,
            validation_service=mock_validation_service,
            backup_service=mock_backup_service,
            existing_config=empty_config,
        )

        with patch.dict("os.environ", {"AZURE_DEVOPS_PAT": "env-pat"}):
            with patch("src.doit_cli.services.wizard_service.Prompt") as mock_prompt:
                mock_prompt.ask.side_effect = ["myorg", "myproject"]
                with patch("src.doit_cli.services.wizard_service.Confirm") as mock_confirm:
                    mock_confirm.ask.return_value = True  # Use env PAT

                    config = wizard.collect_azure_devops_config()

        assert config["pat"] == "env-pat"

    def test_empty_organization_reprompts(
        self, mock_console, mock_validation_service, mock_backup_service, empty_config
    ):
        """Empty organization input causes reprompt."""
        wizard = WizardService(
            console=mock_console,
            validation_service=mock_validation_service,
            backup_service=mock_backup_service,
            existing_config=empty_config,
        )

        with patch("src.doit_cli.services.wizard_service.Prompt") as mock_prompt:
            # First empty, then valid
            mock_prompt.ask.side_effect = ["", "myorg", "myproject", "secret-pat"]

            config = wizard.collect_azure_devops_config()

        assert config["organization"] == "myorg"


class TestReconfigurationFlow:
    """Tests for reconfiguration detection and backup - T018, T019."""

    def test_existing_config_prompts_for_confirmation(
        self, mock_console, mock_validation_service, mock_backup_service, github_config
    ):
        """When existing config found, prompt for confirmation."""
        wizard = WizardService(
            console=mock_console,
            validation_service=mock_validation_service,
            backup_service=mock_backup_service,
            existing_config=github_config,
        )

        with patch("src.doit_cli.services.wizard_service.Confirm") as mock_confirm:
            mock_confirm.ask.return_value = False  # Don't reconfigure

            result = wizard.run()

        assert result.cancelled
        assert not result.success

    def test_force_reconfigure_skips_confirmation(
        self, mock_console, mock_validation_service, mock_backup_service, github_config
    ):
        """With force_reconfigure=True, skip confirmation prompt."""
        wizard = WizardService(
            console=mock_console,
            validation_service=mock_validation_service,
            backup_service=mock_backup_service,
            existing_config=github_config,
        )

        mock_backup = MagicMock()
        mock_backup.backup_id = "20260122_120000"
        mock_backup_service.create_backup.return_value = mock_backup

        with patch.object(wizard, "detect_provider", return_value=(ProviderType.GITHUB, "git_remote")):
            with patch.object(wizard, "select_provider", return_value=ProviderType.GITHUB):
                with patch.object(wizard, "collect_github_config", return_value={"auth_method": "gh_cli"}):
                    validation_result = ValidationResult.passed(
                        WizardStep.GITHUB_VALIDATE,
                        details={"authenticated_user": "testuser", "has_repo_access": True},
                    )
                    mock_validation_service.validate_provider.return_value = validation_result

                    with patch.object(ProviderConfig, "save"):
                        result = wizard.run(force_reconfigure=True)

        # Backup should be created
        mock_backup_service.create_backup.assert_called_once()
        assert result.success

    def test_backup_created_before_reconfiguration(
        self, mock_console, mock_validation_service, mock_backup_service, github_config
    ):
        """Backup is created before making changes during reconfiguration."""
        wizard = WizardService(
            console=mock_console,
            validation_service=mock_validation_service,
            backup_service=mock_backup_service,
            existing_config=github_config,
        )

        mock_backup = MagicMock()
        mock_backup.backup_id = "20260122_120000"
        mock_backup_service.create_backup.return_value = mock_backup

        with patch("src.doit_cli.services.wizard_service.Confirm") as mock_confirm:
            mock_confirm.ask.return_value = True  # Confirm reconfigure

            with patch.object(wizard, "detect_provider", return_value=(ProviderType.GITHUB, "git_remote")):
                with patch.object(wizard, "select_provider", return_value=ProviderType.GITHUB):
                    with patch.object(wizard, "collect_github_config", return_value={"auth_method": "gh_cli"}):
                        validation_result = ValidationResult.passed(
                            WizardStep.GITHUB_VALIDATE,
                            details={"authenticated_user": "testuser", "has_repo_access": True},
                        )
                        mock_validation_service.validate_provider.return_value = validation_result

                        with patch.object(ProviderConfig, "save"):
                            wizard.run()

        # Verify backup was created with correct reason
        mock_backup_service.create_backup.assert_called_once()
        call_args = mock_backup_service.create_backup.call_args
        assert call_args[1]["reason"] == "reconfigure"


class TestCancellationHandling:
    """Tests for wizard cancellation and restore."""

    def test_handle_cancellation_restores_backup(
        self, mock_console, mock_validation_service, mock_backup_service, github_config
    ):
        """When cancelled after backup, restore previous config."""
        wizard = WizardService(
            console=mock_console,
            validation_service=mock_validation_service,
            backup_service=mock_backup_service,
            existing_config=github_config,
        )
        wizard._backup_created = True

        mock_backup = MagicMock()
        mock_backup.backup_id = "20260122_120000"
        mock_backup_service.get_latest_backup.return_value = mock_backup
        mock_backup_service.restore_backup.return_value = github_config

        with patch.object(github_config, "save"):
            wizard.handle_cancellation()

        mock_backup_service.restore_backup.assert_called_once_with("20260122_120000")

    def test_handle_cancellation_without_backup_does_nothing(
        self, mock_console, mock_validation_service, mock_backup_service, empty_config
    ):
        """When cancelled without backup, don't try to restore."""
        wizard = WizardService(
            console=mock_console,
            validation_service=mock_validation_service,
            backup_service=mock_backup_service,
            existing_config=empty_config,
        )
        wizard._backup_created = False

        wizard.handle_cancellation()

        mock_backup_service.restore_backup.assert_not_called()


class TestSelectProvider:
    """Tests for select_provider() method."""

    def test_detected_provider_accepted_by_default(
        self, mock_console, mock_validation_service, mock_backup_service, empty_config
    ):
        """When detected provider is accepted, return it."""
        wizard = WizardService(
            console=mock_console,
            validation_service=mock_validation_service,
            backup_service=mock_backup_service,
            existing_config=empty_config,
        )

        with patch("src.doit_cli.services.wizard_service.Confirm") as mock_confirm:
            mock_confirm.ask.return_value = True  # Accept detected

            result = wizard.select_provider(ProviderType.GITHUB)

        assert result == ProviderType.GITHUB

    def test_manual_selection_when_detected_rejected(
        self, mock_console, mock_validation_service, mock_backup_service, empty_config
    ):
        """When detected provider is rejected, show selection menu."""
        wizard = WizardService(
            console=mock_console,
            validation_service=mock_validation_service,
            backup_service=mock_backup_service,
            existing_config=empty_config,
        )

        with patch("src.doit_cli.services.wizard_service.Confirm") as mock_confirm:
            mock_confirm.ask.return_value = False  # Reject detected
            with patch("src.doit_cli.services.wizard_service.Prompt") as mock_prompt:
                mock_prompt.ask.return_value = "2"  # Azure DevOps

                result = wizard.select_provider(ProviderType.GITHUB)

        assert result == ProviderType.AZURE_DEVOPS

    def test_no_detection_shows_selection_menu(
        self, mock_console, mock_validation_service, mock_backup_service, empty_config
    ):
        """When no provider detected, show selection menu."""
        wizard = WizardService(
            console=mock_console,
            validation_service=mock_validation_service,
            backup_service=mock_backup_service,
            existing_config=empty_config,
        )

        with patch("src.doit_cli.services.wizard_service.Prompt") as mock_prompt:
            mock_prompt.ask.return_value = "3"  # GitLab

            result = wizard.select_provider(None)

        assert result == ProviderType.GITLAB


class TestValidateAndSave:
    """Tests for validate_and_save() method."""

    def test_successful_validation_saves_config(
        self, mock_console, mock_validation_service, mock_backup_service, empty_config
    ):
        """When validation succeeds, save config."""
        wizard = WizardService(
            console=mock_console,
            validation_service=mock_validation_service,
            backup_service=mock_backup_service,
            existing_config=empty_config,
        )
        wizard.state = MagicMock()
        wizard.state.auto_detected = True
        wizard.state.detection_source = "git_remote"

        validation_result = ValidationResult.passed(
            WizardStep.GITHUB_VALIDATE,
            details={"authenticated_user": "testuser"},
        )
        mock_validation_service.validate_provider.return_value = validation_result

        with patch.object(ProviderConfig, "save") as mock_save:
            result = wizard.validate_and_save(
                ProviderType.GITHUB,
                {"auth_method": "gh_cli"},
            )

        assert result.success
        mock_save.assert_called_once()

    def test_failed_validation_offers_options(
        self, mock_console, mock_validation_service, mock_backup_service, empty_config
    ):
        """When validation fails, offer retry/save anyway/cancel options."""
        wizard = WizardService(
            console=mock_console,
            validation_service=mock_validation_service,
            backup_service=mock_backup_service,
            existing_config=empty_config,
        )
        wizard.state = MagicMock()

        validation_result = ValidationResult.failed(
            WizardStep.GITHUB_VALIDATE,
            error="Authentication failed",
        )
        mock_validation_service.validate_provider.return_value = validation_result

        with patch("src.doit_cli.services.wizard_service.Prompt") as mock_prompt:
            mock_prompt.ask.return_value = "3"  # Cancel

            with pytest.raises(WizardCancelledError):
                wizard.validate_and_save(
                    ProviderType.GITHUB,
                    {"auth_method": "gh_cli"},
                )
