"""Unit tests for ProviderValidationService."""

from unittest.mock import MagicMock, patch

import httpx
import pytest

from src.doit_cli.models.wizard_models import WizardStep
from src.doit_cli.services.provider_validation_service import ProviderValidationService
from src.doit_cli.services.providers.base import ProviderType


class TestValidateGitHub:
    """Tests for validate_github() method - T007."""

    def test_gh_not_installed_returns_failure(self):
        """When gh CLI is not installed, return failed result."""
        service = ProviderValidationService()

        with patch.object(service, "check_gh_cli_installed", return_value=False):
            result = service.validate_github()

        assert not result.success
        assert result.step == WizardStep.GITHUB_CHECK_CLI
        assert "not installed" in result.error_message.lower()
        assert result.suggestion is not None

    def test_gh_not_authenticated_returns_failure(self):
        """When gh CLI is installed but not authenticated, return failed result."""
        service = ProviderValidationService()

        with patch.object(service, "check_gh_cli_installed", return_value=True):
            with patch.object(
                service, "check_gh_cli_authenticated", return_value=(False, "Not logged in")
            ):
                result = service.validate_github()

        assert not result.success
        assert result.step == WizardStep.GITHUB_CHECK_CLI
        assert "not authenticated" in result.error_message.lower()

    def test_gh_authenticated_returns_success(self):
        """When gh CLI is installed and authenticated, return success."""
        service = ProviderValidationService()

        with patch.object(service, "check_gh_cli_installed", return_value=True):
            with patch.object(
                service, "check_gh_cli_authenticated", return_value=(True, "testuser")
            ):
                with patch.object(service, "test_github_repo_access", return_value=True):
                    result = service.validate_github()

        assert result.success
        assert result.step == WizardStep.GITHUB_VALIDATE
        assert result.details["authenticated_user"] == "testuser"
        assert result.details["has_repo_access"] is True

    def test_gh_enterprise_host_passed_to_auth_check(self):
        """Enterprise host is passed to authentication check."""
        service = ProviderValidationService()

        with patch.object(service, "check_gh_cli_installed", return_value=True):
            with patch.object(
                service, "check_gh_cli_authenticated", return_value=(True, "enterpriseuser")
            ) as mock_auth:
                with patch.object(service, "test_github_repo_access", return_value=True):
                    result = service.validate_github(enterprise_host="github.mycompany.com")

        mock_auth.assert_called_once_with("github.mycompany.com")
        assert result.success


class TestValidateAzureDevOps:
    """Tests for validate_azure_devops() method - T012."""

    def test_missing_organization_returns_failure(self):
        """When organization is missing, return failed result."""
        service = ProviderValidationService()

        result = service.validate_azure_devops(
            organization="",
            project="myproject",
            pat="secret-pat",
        )

        assert not result.success
        assert result.step == WizardStep.ADO_VALIDATE
        assert "required" in result.error_message.lower()

    def test_missing_pat_returns_failure(self):
        """When PAT is missing, return failed result."""
        service = ProviderValidationService()

        result = service.validate_azure_devops(
            organization="myorg",
            project="myproject",
            pat="",
        )

        assert not result.success
        assert result.step == WizardStep.ADO_VALIDATE

    def test_invalid_pat_returns_failure(self):
        """When PAT is invalid (401), return failed result with suggestion."""
        service = ProviderValidationService()

        mock_response = MagicMock()
        mock_response.status_code = 401

        with patch("httpx.Client") as mock_client:
            mock_client.return_value.__enter__.return_value.get.return_value = mock_response

            result = service.validate_azure_devops(
                organization="myorg",
                project="myproject",
                pat="invalid-pat",
            )

        assert not result.success
        assert "invalid" in result.error_message.lower()
        assert result.suggestion is not None
        assert "myorg" in result.suggestion

    def test_invalid_organization_returns_failure(self):
        """When organization doesn't exist (non-200/401), return failed result."""
        service = ProviderValidationService()

        mock_response = MagicMock()
        mock_response.status_code = 404

        with patch("httpx.Client") as mock_client:
            mock_client.return_value.__enter__.return_value.get.return_value = mock_response

            result = service.validate_azure_devops(
                organization="nonexistent",
                project="myproject",
                pat="valid-pat",
            )

        assert not result.success
        assert "organization" in result.error_message.lower()

    def test_project_not_found_returns_failure(self):
        """When project doesn't exist, return failed result."""
        service = ProviderValidationService()

        org_response = MagicMock()
        org_response.status_code = 200

        project_response = MagicMock()
        project_response.status_code = 404

        with patch("httpx.Client") as mock_client:
            mock_client.return_value.__enter__.return_value.get.side_effect = [
                org_response,
                project_response,
            ]

            result = service.validate_azure_devops(
                organization="myorg",
                project="nonexistent",
                pat="valid-pat",
            )

        assert not result.success
        assert "project" in result.error_message.lower()
        assert "nonexistent" in result.error_message

    def test_valid_pat_returns_success(self):
        """When PAT is valid, return success with scopes."""
        service = ProviderValidationService()

        org_response = MagicMock()
        org_response.status_code = 200

        project_response = MagicMock()
        project_response.status_code = 200

        with patch("httpx.Client") as mock_client:
            mock_client.return_value.__enter__.return_value.get.side_effect = [
                org_response,
                project_response,
            ]
            with patch.object(
                service, "get_ado_pat_scopes", return_value=["Code (Read)", "Work Items (Read)"]
            ):
                result = service.validate_azure_devops(
                    organization="myorg",
                    project="myproject",
                    pat="valid-pat",
                )

        assert result.success
        assert result.step == WizardStep.ADO_VALIDATE
        assert result.details["organization_accessible"] is True
        assert result.details["project_accessible"] is True
        assert "Code (Read)" in result.details["detected_scopes"]

    def test_timeout_returns_failure(self):
        """When request times out, return failed result with suggestion."""
        service = ProviderValidationService()

        with patch("httpx.Client") as mock_client:
            mock_client.return_value.__enter__.return_value.get.side_effect = (
                httpx.TimeoutException("Connection timed out")
            )

            result = service.validate_azure_devops(
                organization="myorg",
                project="myproject",
                pat="valid-pat",
            )

        assert not result.success
        assert "timed out" in result.error_message.lower()
        assert result.suggestion is not None


class TestValidateGitLab:
    """Tests for validate_gitlab() method - T020."""

    def test_missing_token_returns_failure(self):
        """When token is missing, return failed result."""
        service = ProviderValidationService()

        result = service.validate_gitlab(host="gitlab.com", token="")

        assert not result.success
        assert result.step == WizardStep.GITLAB_VALIDATE
        assert "required" in result.error_message.lower()

    def test_invalid_token_returns_failure(self):
        """When token is invalid (401), return failed result."""
        service = ProviderValidationService()

        mock_response = MagicMock()
        mock_response.status_code = 401

        with patch("httpx.Client") as mock_client:
            mock_client.return_value.__enter__.return_value.get.return_value = mock_response

            result = service.validate_gitlab(host="gitlab.com", token="invalid-token")

        assert not result.success
        assert "invalid" in result.error_message.lower()
        assert result.suggestion is not None

    def test_valid_token_returns_success(self):
        """When token is valid, return success with user info."""
        service = ProviderValidationService()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"username": "testuser"}

        with patch("httpx.Client") as mock_client:
            mock_client.return_value.__enter__.return_value.get.return_value = mock_response

            result = service.validate_gitlab(host="gitlab.com", token="valid-token")

        assert result.success
        assert result.step == WizardStep.GITLAB_VALIDATE
        assert result.details["authenticated_user"] == "testuser"
        assert result.details["feature_support"] == "limited"

    def test_host_without_https_is_normalized(self):
        """Host without https:// prefix is normalized."""
        service = ProviderValidationService()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"username": "testuser"}

        with patch("httpx.Client") as mock_client:
            mock_instance = mock_client.return_value.__enter__.return_value
            mock_instance.get.return_value = mock_response

            result = service.validate_gitlab(host="gitlab.mycompany.com", token="valid-token")

        # Verify https:// was added
        call_args = mock_instance.get.call_args
        assert "https://gitlab.mycompany.com" in call_args[0][0]
        assert result.success


class TestValidateProvider:
    """Tests for validate_provider() dispatch method."""

    def test_github_dispatches_to_validate_github(self):
        """GitHub provider type calls validate_github."""
        service = ProviderValidationService()

        with patch.object(service, "validate_github") as mock_validate:
            mock_validate.return_value = MagicMock(success=True)

            service.validate_provider(
                ProviderType.GITHUB,
                {"enterprise_host": "github.mycompany.com"},
            )

        mock_validate.assert_called_once_with(enterprise_host="github.mycompany.com")

    def test_azure_devops_dispatches_to_validate_azure_devops(self):
        """Azure DevOps provider type calls validate_azure_devops."""
        service = ProviderValidationService()

        with patch.object(service, "validate_azure_devops") as mock_validate:
            mock_validate.return_value = MagicMock(success=True)

            service.validate_provider(
                ProviderType.AZURE_DEVOPS,
                {"organization": "myorg", "project": "myproject", "pat": "secret"},
            )

        mock_validate.assert_called_once_with(
            organization="myorg",
            project="myproject",
            pat="secret",
        )

    def test_gitlab_dispatches_to_validate_gitlab(self):
        """GitLab provider type calls validate_gitlab."""
        service = ProviderValidationService()

        with patch.object(service, "validate_gitlab") as mock_validate:
            mock_validate.return_value = MagicMock(success=True)

            service.validate_provider(
                ProviderType.GITLAB,
                {"host": "gitlab.com", "token": "secret"},
            )

        mock_validate.assert_called_once_with(
            host="gitlab.com",
            token="secret",
        )


class TestCheckGhCli:
    """Tests for gh CLI helper methods."""

    def test_check_gh_cli_installed_returns_true_when_found(self):
        """When gh is in PATH, return True."""
        service = ProviderValidationService()

        with patch("shutil.which", return_value="/usr/local/bin/gh"):
            result = service.check_gh_cli_installed()

        assert result is True

    def test_check_gh_cli_installed_returns_false_when_not_found(self):
        """When gh is not in PATH, return False."""
        service = ProviderValidationService()

        with patch("shutil.which", return_value=None):
            result = service.check_gh_cli_installed()

        assert result is False
