# Contract: WizardService

**Branch**: `047-provider-config-wizard` | **Date**: 2026-01-22

## Overview

The WizardService manages the interactive configuration wizard flow, handling state transitions, input collection, and orchestrating validation.

## Interface

```python
class WizardService:
    """Manages the provider configuration wizard flow."""

    def __init__(
        self,
        console: Console,
        validation_service: ValidationService,
        config_service: ProviderConfig,
    ) -> None:
        """Initialize wizard with dependencies."""

    def run(self, force_reconfigure: bool = False) -> WizardResult:
        """
        Execute the wizard flow from start to completion.

        Args:
            force_reconfigure: If True, skip confirmation when existing config found

        Returns:
            WizardResult with success status and resulting configuration

        Raises:
            WizardCancelledError: User cancelled the wizard
        """

    def detect_provider(self) -> tuple[ProviderType | None, str | None]:
        """
        Detect provider from git remote URL.

        Returns:
            Tuple of (provider_type, detection_source) or (None, None)
        """

    def select_provider(self, detected: ProviderType | None) -> ProviderType:
        """
        Interactive provider selection with detected provider as default.

        Args:
            detected: Auto-detected provider if any

        Returns:
            Selected ProviderType
        """

    def collect_github_config(self) -> dict[str, Any]:
        """
        Collect GitHub-specific configuration.

        Returns:
            Dict with auth_method and optional enterprise_host

        Raises:
            WizardStepError: gh CLI not installed or not authenticated
        """

    def collect_azure_devops_config(self) -> dict[str, Any]:
        """
        Collect Azure DevOps-specific configuration.

        Returns:
            Dict with organization, project, and auth info
        """

    def collect_gitlab_config(self) -> dict[str, Any]:
        """
        Collect GitLab-specific configuration.

        Returns:
            Dict with host and auth info
        """

    def validate_and_save(
        self,
        provider: ProviderType,
        config_values: dict[str, Any],
    ) -> ValidationResult:
        """
        Validate configuration and save if successful.

        Args:
            provider: The provider type
            config_values: Collected configuration values

        Returns:
            ValidationResult with success status and details
        """

    def display_summary(
        self,
        provider: ProviderType,
        config_values: dict[str, Any],
        validation: ValidationResult,
    ) -> None:
        """Display configuration summary after completion."""

    def handle_cancellation(self) -> None:
        """Handle user cancellation, restore previous state if needed."""
```

## Data Structures

```python
@dataclass
class WizardResult:
    """Result of wizard execution."""
    success: bool
    provider: ProviderType | None
    config: ProviderConfig | None
    cancelled: bool = False
    error_message: str | None = None


class WizardCancelledError(Exception):
    """Raised when user cancels the wizard."""
    pass


class WizardStepError(Exception):
    """Raised when a wizard step fails."""
    def __init__(self, step: WizardStep, message: str, suggestion: str | None = None):
        self.step = step
        self.message = message
        self.suggestion = suggestion
        super().__init__(message)
```

## Method Behaviors

### run()

1. Check for existing configuration
2. If exists and not force_reconfigure, prompt to reconfigure
3. Create backup of existing config if reconfiguring
4. Detect provider from git remote
5. If not detected, show provider selection
6. Collect provider-specific configuration
7. Validate configuration
8. If validation fails, allow retry or save with warning
9. Save configuration
10. Display summary

### detect_provider()

1. Get git remote URL using `git remote get-url origin`
2. Parse URL for provider indicators:
   - `github.com` or `ghe.` → GitHub
   - `dev.azure.com` or `visualstudio.com` → Azure DevOps
   - `gitlab` → GitLab
3. Return (provider_type, "git_remote") or (None, None)

### collect_github_config()

1. Check if `gh` CLI is installed (`which gh`)
2. If not installed:
   - Display installation instructions
   - Link to https://cli.github.com
   - Allow retry or exit
3. Check `gh auth status`
4. If not authenticated:
   - Prompt user to run `gh auth login`
   - Allow retry or exit
5. Ask if using GitHub Enterprise
6. If yes, prompt for enterprise host
7. Return collected values

### collect_azure_devops_config()

1. Prompt for organization name (with validation for non-empty)
2. Prompt for project name (with validation for non-empty)
3. Prompt for PAT with hidden input
4. Display required scopes: Code (Read/Write), Work Items (Read/Write)
5. Link to PAT creation page
6. Return collected values

### collect_gitlab_config()

1. Prompt for GitLab host (default: gitlab.com)
2. Show current implementation status warning
3. Prompt for personal access token with hidden input
4. Display required scopes: api, read_repository
5. Return collected values

### validate_and_save()

1. Call ValidationService.validate_provider()
2. If validation fails:
   - Display error with suggestion
   - Ask: retry, save anyway (with warning), or cancel
3. If save anyway, add warning to config
4. Build ProviderConfig from collected values
5. Save configuration
6. Return ValidationResult

## Error Handling

| Error | Handling |
|-------|----------|
| Git remote not found | Proceed to manual selection |
| gh CLI not installed | Show install instructions, allow retry |
| gh not authenticated | Show auth instructions, allow retry |
| PAT invalid | Show error, allow re-entry |
| Network timeout | Offer to save without validation |
| User Ctrl+C | Restore previous config, exit gracefully |

## UI Patterns

### Progress Display

```
╭─ Provider Configuration Wizard ─╮
│ Step 2 of 4: GitHub Setup       │
╰─────────────────────────────────╯
```

### Input Prompts

```
Organization name: myorg
Project name: myproject
Personal Access Token: ********
```

### Validation Spinner

```
⠋ Validating credentials...
```

### Summary Display

```
╭─ Configuration Complete ─────────────────╮
│ Provider: GitHub                         │
│ Auth Method: gh CLI                      │
│ Authenticated: octocat                   │
│ Repository Access: ✓ Verified            │
╰──────────────────────────────────────────╯
```

## Dependencies

- `ValidationService` - For credential validation
- `ProviderConfig` - For configuration persistence
- `Rich.Console` - For terminal UI
- `Rich.Prompt` - For input collection
- `Rich.Panel` - For step containers
- `Rich.Status` - For spinners
