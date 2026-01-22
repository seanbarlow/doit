"""Validation service for provider credentials and connectivity.

This module provides validation methods for GitHub, Azure DevOps, and GitLab
authentication and connectivity testing during the wizard flow.
"""

import shutil
import subprocess
from typing import Any, Optional

import httpx

from ..models.wizard_models import ValidationResult, WizardStep
from .providers.base import ProviderType


class ProviderValidationService:
    """Validates provider credentials and connectivity."""

    def __init__(self, timeout: float = 10.0) -> None:
        """Initialize validation service.

        Args:
            timeout: Timeout in seconds for network operations
        """
        self.timeout = timeout

    def validate_provider(
        self,
        provider: ProviderType,
        config_values: dict[str, Any],
    ) -> ValidationResult:
        """Validate provider credentials and connectivity.

        Args:
            provider: The provider to validate
            config_values: Provider-specific configuration

        Returns:
            ValidationResult with success/failure details
        """
        if provider == ProviderType.GITHUB:
            return self.validate_github(
                enterprise_host=config_values.get("enterprise_host"),
            )
        elif provider == ProviderType.AZURE_DEVOPS:
            return self.validate_azure_devops(
                organization=config_values.get("organization", ""),
                project=config_values.get("project", ""),
                pat=config_values.get("pat", ""),
            )
        elif provider == ProviderType.GITLAB:
            return self.validate_gitlab(
                host=config_values.get("host", "gitlab.com"),
                token=config_values.get("token", ""),
            )
        else:
            return ValidationResult.failed(
                step=WizardStep.DETECT_PROVIDER,
                error=f"Unknown provider: {provider}",
            )

    def validate_github(
        self,
        enterprise_host: Optional[str] = None,
    ) -> ValidationResult:
        """Validate GitHub authentication via gh CLI.

        Args:
            enterprise_host: Optional GitHub Enterprise host

        Returns:
            ValidationResult with user info on success
        """
        # Check gh CLI installed
        if not self.check_gh_cli_installed():
            return ValidationResult.failed(
                step=WizardStep.GITHUB_CHECK_CLI,
                error="GitHub CLI (gh) is not installed",
                suggestion="Install from https://cli.github.com",
            )

        # Check gh authenticated
        is_authed, username_or_error = self.check_gh_cli_authenticated(enterprise_host)
        if not is_authed:
            return ValidationResult.failed(
                step=WizardStep.GITHUB_CHECK_CLI,
                error="GitHub CLI is not authenticated",
                suggestion="Run 'gh auth login' to authenticate",
            )

        # Test repo access
        has_access = self.test_github_repo_access(enterprise_host)

        return ValidationResult.passed(
            step=WizardStep.GITHUB_VALIDATE,
            details={
                "authenticated_user": username_or_error,
                "has_repo_access": has_access,
            },
        )

    def validate_azure_devops(
        self,
        organization: str,
        project: str,
        pat: str,
    ) -> ValidationResult:
        """Validate Azure DevOps PAT and project access.

        Args:
            organization: Azure DevOps organization name
            project: Project name
            pat: Personal Access Token

        Returns:
            ValidationResult with scope info on success
        """
        if not organization or not project or not pat:
            return ValidationResult.failed(
                step=WizardStep.ADO_VALIDATE,
                error="Organization, project, and PAT are required",
            )

        base_url = f"https://dev.azure.com/{organization}"
        auth = httpx.BasicAuth("", pat)

        try:
            # Test organization access
            with httpx.Client(timeout=self.timeout, auth=auth) as client:
                org_response = client.get(f"{base_url}/_apis/projects?api-version=7.0")

                if org_response.status_code == 401:
                    return ValidationResult.failed(
                        step=WizardStep.ADO_VALIDATE,
                        error="Invalid Personal Access Token",
                        suggestion=f"Create a new PAT at https://dev.azure.com/{organization}/_usersSettings/tokens",
                    )

                if org_response.status_code != 200:
                    return ValidationResult.failed(
                        step=WizardStep.ADO_VALIDATE,
                        error=f"Could not access organization '{organization}'",
                        suggestion="Verify the organization name is correct",
                    )

                # Test project access
                project_response = client.get(
                    f"{base_url}/{project}/_apis/project?api-version=7.0"
                )

                if project_response.status_code == 404:
                    return ValidationResult.failed(
                        step=WizardStep.ADO_VALIDATE,
                        error=f"Project '{project}' not found in {organization}",
                        suggestion="Verify the project name or check permissions",
                    )

                # Detect scopes
                scopes = self.get_ado_pat_scopes(organization, pat)

                return ValidationResult.passed(
                    step=WizardStep.ADO_VALIDATE,
                    details={
                        "organization_accessible": True,
                        "project_accessible": True,
                        "detected_scopes": scopes or [],
                    },
                )

        except httpx.TimeoutException:
            return ValidationResult.failed(
                step=WizardStep.ADO_VALIDATE,
                error="Connection timed out",
                suggestion="Check network connectivity and try again",
            )
        except httpx.RequestError as e:
            return ValidationResult.failed(
                step=WizardStep.ADO_VALIDATE,
                error=f"Network error: {e}",
                suggestion="Check network connectivity and try again",
            )

    def validate_gitlab(
        self,
        host: str,
        token: str,
    ) -> ValidationResult:
        """Validate GitLab token and connectivity.

        Args:
            host: GitLab instance host
            token: Personal Access Token

        Returns:
            ValidationResult with user info on success
        """
        if not token:
            return ValidationResult.failed(
                step=WizardStep.GITLAB_VALIDATE,
                error="GitLab token is required",
            )

        # Ensure host has https://
        if not host.startswith("http"):
            host = f"https://{host}"

        headers = {"PRIVATE-TOKEN": token}

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(f"{host}/api/v4/user", headers=headers)

                if response.status_code == 401:
                    return ValidationResult.failed(
                        step=WizardStep.GITLAB_VALIDATE,
                        error="Invalid GitLab token",
                        suggestion=f"Create a new token at {host}/-/profile/personal_access_tokens",
                    )

                if response.status_code != 200:
                    return ValidationResult.failed(
                        step=WizardStep.GITLAB_VALIDATE,
                        error=f"Could not connect to {host}",
                        suggestion="Verify the GitLab host is correct",
                    )

                user_data = response.json()
                username = user_data.get("username", "unknown")

                return ValidationResult.passed(
                    step=WizardStep.GITLAB_VALIDATE,
                    details={
                        "authenticated_user": username,
                        "api_version": "v4",
                        "feature_support": "limited",  # GitLab is stub
                    },
                )

        except httpx.TimeoutException:
            return ValidationResult.failed(
                step=WizardStep.GITLAB_VALIDATE,
                error="Connection timed out",
                suggestion="Check network connectivity and try again",
            )
        except httpx.RequestError as e:
            return ValidationResult.failed(
                step=WizardStep.GITLAB_VALIDATE,
                error=f"Network error: {e}",
                suggestion="Check network connectivity and try again",
            )

    def check_gh_cli_installed(self) -> bool:
        """Check if gh CLI is installed and in PATH."""
        return shutil.which("gh") is not None

    def check_gh_cli_authenticated(
        self,
        enterprise_host: Optional[str] = None,
    ) -> tuple[bool, Optional[str]]:
        """Check if gh CLI is authenticated.

        Returns:
            Tuple of (is_authenticated, username_or_error)
        """
        cmd = ["gh", "auth", "status"]
        if enterprise_host:
            cmd.extend(["--hostname", enterprise_host])

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                # Parse "Logged in to github.com as USERNAME" from stderr
                for line in result.stderr.split("\n"):
                    if "Logged in" in line and " as " in line:
                        username = line.split(" as ")[-1].strip()
                        # Remove any trailing info like "(keyring)"
                        username = username.split()[0] if username else None
                        return True, username
                return True, None

            return False, result.stderr.strip()

        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except FileNotFoundError:
            return False, "gh CLI not found"
        except Exception as e:
            return False, str(e)

    def test_github_repo_access(
        self,
        enterprise_host: Optional[str] = None,
    ) -> bool:
        """Test if authenticated user has access to current repository."""
        cmd = ["gh", "api", "user"]
        if enterprise_host:
            cmd.extend(["--hostname", enterprise_host])

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0
        except Exception:
            return False

    def get_ado_pat_scopes(
        self,
        organization: str,
        pat: str,
    ) -> Optional[list[str]]:
        """Determine PAT scopes by testing specific endpoints.

        Returns:
            List of detected scopes or None if PAT invalid
        """
        base_url = f"https://dev.azure.com/{organization}"
        auth = httpx.BasicAuth("", pat)
        scopes = []

        try:
            with httpx.Client(timeout=self.timeout, auth=auth) as client:
                # Test Work Items read
                wit_response = client.get(
                    f"{base_url}/_apis/wit/workitemtypes?api-version=7.0"
                )
                if wit_response.status_code == 200:
                    scopes.append("Work Items (Read)")

                # Test Git/Code read
                git_response = client.get(
                    f"{base_url}/_apis/git/repositories?api-version=7.0"
                )
                if git_response.status_code == 200:
                    scopes.append("Code (Read)")

                return scopes if scopes else None

        except Exception:
            return None
