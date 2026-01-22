# Contract: ValidationService

**Branch**: `047-provider-config-wizard` | **Date**: 2026-01-22

## Overview

The ValidationService tests authentication credentials and connectivity for each supported git provider.

## Interface

```python
class ValidationService:
    """Validates provider credentials and connectivity."""

    def __init__(self, timeout: float = 10.0) -> None:
        """
        Initialize validation service.

        Args:
            timeout: Timeout in seconds for network operations
        """

    def validate_provider(
        self,
        provider: ProviderType,
        config_values: dict[str, Any],
    ) -> ValidationResult:
        """
        Validate provider credentials and connectivity.

        Args:
            provider: The provider to validate
            config_values: Provider-specific configuration

        Returns:
            ValidationResult with success/failure details
        """

    def validate_github(
        self,
        enterprise_host: str | None = None,
    ) -> ValidationResult:
        """
        Validate GitHub authentication via gh CLI.

        Args:
            enterprise_host: Optional GitHub Enterprise host

        Returns:
            ValidationResult with user info on success
        """

    def validate_azure_devops(
        self,
        organization: str,
        project: str,
        pat: str,
    ) -> ValidationResult:
        """
        Validate Azure DevOps PAT and project access.

        Args:
            organization: Azure DevOps organization name
            project: Project name
            pat: Personal Access Token

        Returns:
            ValidationResult with scope info on success
        """

    def validate_gitlab(
        self,
        host: str,
        token: str,
    ) -> ValidationResult:
        """
        Validate GitLab token and connectivity.

        Args:
            host: GitLab instance host
            token: Personal Access Token

        Returns:
            ValidationResult with user info on success
        """

    def check_gh_cli_installed(self) -> bool:
        """Check if gh CLI is installed and in PATH."""

    def check_gh_cli_authenticated(
        self,
        enterprise_host: str | None = None,
    ) -> tuple[bool, str | None]:
        """
        Check if gh CLI is authenticated.

        Returns:
            Tuple of (is_authenticated, username_or_error)
        """

    def test_github_repo_access(
        self,
        enterprise_host: str | None = None,
    ) -> bool:
        """Test if authenticated user has access to current repository."""

    def get_ado_pat_scopes(
        self,
        organization: str,
        pat: str,
    ) -> list[str] | None:
        """
        Determine PAT scopes by testing specific endpoints.

        Returns:
            List of detected scopes or None if PAT invalid
        """
```

## Data Structures

```python
@dataclass
class ValidationResult:
    """Result of a validation operation."""
    success: bool
    step: WizardStep
    timestamp: datetime
    error_message: str | None = None
    suggestion: str | None = None
    details: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def passed(
        cls,
        step: WizardStep,
        details: dict[str, Any] | None = None,
    ) -> "ValidationResult":
        """Create a successful validation result."""
        return cls(
            success=True,
            step=step,
            timestamp=datetime.now(UTC),
            details=details or {},
        )

    @classmethod
    def failed(
        cls,
        step: WizardStep,
        error: str,
        suggestion: str | None = None,
    ) -> "ValidationResult":
        """Create a failed validation result."""
        return cls(
            success=False,
            step=step,
            timestamp=datetime.now(UTC),
            error_message=error,
            suggestion=suggestion,
        )
```

## Method Behaviors

### validate_github()

1. Check gh CLI installed
2. If not: return failed with install instructions
3. Run `gh auth status` with optional `--hostname` for GHE
4. Parse output for username
5. Test repository access with `gh api user`
6. Return result with details:
   ```python
   {
       "gh_version": "2.42.0",
       "authenticated_user": "octocat",
       "has_repo_access": True,
   }
   ```

### validate_azure_devops()

1. Build auth header: Basic auth with empty user and PAT
2. Test organization access: GET `https://dev.azure.com/{org}/_apis/projects`
3. If 401: return failed "Invalid PAT"
4. If success, test project access: GET `https://dev.azure.com/{org}/{project}/_apis/project`
5. If 404: return failed "Project not found"
6. Test Work Items endpoint to check scope
7. Test Git endpoint to check scope
8. Return result with details:
   ```python
   {
       "organization_accessible": True,
       "project_accessible": True,
       "detected_scopes": ["Code (Read)", "Work Items (Read & Write)"],
       "missing_scopes": ["Code (Write)"],
   }
   ```

### validate_gitlab()

1. Build auth header: `PRIVATE-TOKEN: {token}`
2. Test user endpoint: GET `https://{host}/api/v4/user`
3. If 401: return failed "Invalid token"
4. Parse response for username
5. Return result with details:
   ```python
   {
       "authenticated_user": "johndoe",
       "api_version": "v4",
       "feature_support": "limited",  # Note about stub status
   }
   ```

### check_gh_cli_installed()

1. Run `which gh` (Unix) or `where gh` (Windows)
2. Return True if exit code 0, False otherwise

### check_gh_cli_authenticated()

1. Run `gh auth status`
2. Parse output for "Logged in to github.com as USERNAME"
3. Return (True, username) or (False, error_message)

### get_ado_pat_scopes()

Test specific endpoints to infer PAT scopes:

| Endpoint | Scope Indicator |
|----------|-----------------|
| `/_apis/wit/workitems` | Work Items (Read) |
| `/_apis/wit/workitems/$create` | Work Items (Write) |
| `/_apis/git/repositories` | Code (Read) |
| `/_apis/git/repositories/{id}/refs` | Code (Write) |

## Error Messages

| Scenario | Error | Suggestion |
|----------|-------|------------|
| gh not found | "GitHub CLI (gh) is not installed" | "Install from https://cli.github.com" |
| gh not authed | "GitHub CLI is not authenticated" | "Run 'gh auth login' to authenticate" |
| GHE host invalid | "Could not connect to {host}" | "Verify the enterprise hostname" |
| ADO PAT invalid | "Invalid Personal Access Token" | "Create a new PAT at https://dev.azure.com/{org}/_usersSettings/tokens" |
| ADO project 404 | "Project '{project}' not found in {org}" | "Verify the project name or check permissions" |
| ADO missing scope | "PAT missing required scopes: {scopes}" | "Create a new PAT with Code and Work Items permissions" |
| GitLab token invalid | "Invalid GitLab token" | "Create a new token at https://{host}/-/profile/personal_access_tokens" |
| Network timeout | "Connection timed out" | "Check network connectivity and try again" |

## Timeout Handling

All network operations use the configured timeout (default 10s):

```python
try:
    response = httpx.get(url, timeout=self.timeout, headers=headers)
except httpx.TimeoutException:
    return ValidationResult.failed(
        step=step,
        error="Connection timed out",
        suggestion="Check network connectivity and try again",
    )
```

## Dependencies

- `subprocess` - For gh CLI commands
- `httpx` - For HTTP requests to Azure DevOps and GitLab
- `shutil.which` - For checking gh CLI installation
