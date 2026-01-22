# Quickstart: Git Provider Configuration Wizard

**Branch**: `047-provider-config-wizard` | **Date**: 2026-01-22 | **Spec**: [spec.md](spec.md)

## Development Setup

### Prerequisites

```bash
# Clone and setup
cd /path/to/doit
pip install -e ".[dev]"

# Verify installation
doit --version
doit provider --help
```

### Running Tests

```bash
# All tests
pytest tests/

# Wizard-specific tests
pytest tests/unit/services/test_wizard_service.py
pytest tests/unit/services/test_validation_service.py
pytest tests/integration/test_provider_wizard.py

# With coverage
pytest tests/ --cov=doit_cli.services.wizard_service --cov-report=term-missing
```

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     CLI Layer                                │
│  provider_command.py                                         │
│    └── wizard subcommand                                     │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                   Service Layer                              │
│  ┌─────────────────┐  ┌──────────────────┐  ┌────────────┐  │
│  │ WizardService   │──│ ValidationService │  │ Backup     │  │
│  │                 │  │                   │  │ Service    │  │
│  └────────┬────────┘  └─────────┬────────┘  └─────┬──────┘  │
│           │                     │                  │         │
└───────────┼─────────────────────┼──────────────────┼─────────┘
            │                     │                  │
┌───────────▼─────────────────────▼──────────────────▼─────────┐
│                    Data Layer                                 │
│  ┌─────────────────┐  ┌──────────────────┐                   │
│  │ ProviderConfig  │  │ ConfigBackup     │                   │
│  │ provider.yaml   │  │ provider_backup  │                   │
│  └─────────────────┘  └──────────────────┘                   │
└──────────────────────────────────────────────────────────────┘
```

## Key Files

| File | Purpose |
|------|---------|
| `src/doit_cli/cli/provider_command.py` | CLI entry point, wizard subcommand |
| `src/doit_cli/services/wizard_service.py` | Wizard state machine and flow (NEW) |
| `src/doit_cli/services/validation_service.py` | Credential validation (NEW) |
| `src/doit_cli/services/backup_service.py` | Config backup management (NEW) |
| `src/doit_cli/services/provider_config.py` | Configuration persistence (EXTEND) |
| `src/doit_cli/models/wizard_models.py` | Wizard data structures (NEW) |

## Implementation Checklist

### Phase 1: Core Models

- [ ] Create `wizard_models.py` with:
  - [ ] `WizardStep` enum
  - [ ] `WizardState` dataclass
  - [ ] `ValidationResult` dataclass
  - [ ] `WizardResult` dataclass
  - [ ] `WizardCancelledError` exception
  - [ ] `WizardStepError` exception

### Phase 2: Validation Service

- [ ] Create `validation_service.py` with:
  - [ ] `check_gh_cli_installed()` method
  - [ ] `check_gh_cli_authenticated()` method
  - [ ] `validate_github()` method
  - [ ] `validate_azure_devops()` method
  - [ ] `validate_gitlab()` method
  - [ ] `test_github_repo_access()` method
  - [ ] `get_ado_pat_scopes()` method

### Phase 3: Backup Service

- [ ] Create `backup_service.py` with:
  - [ ] `create_backup()` method
  - [ ] `list_backups()` method
  - [ ] `restore_backup()` method
  - [ ] `prune_old_backups()` method

### Phase 4: Wizard Service

- [ ] Create `wizard_service.py` with:
  - [ ] `run()` main flow
  - [ ] `detect_provider()` method
  - [ ] `select_provider()` UI
  - [ ] `collect_github_config()` flow
  - [ ] `collect_azure_devops_config()` flow
  - [ ] `collect_gitlab_config()` flow
  - [ ] `validate_and_save()` method
  - [ ] `display_summary()` method
  - [ ] `handle_cancellation()` method

### Phase 5: CLI Integration

- [ ] Add `wizard` subcommand to `provider_command.py`
- [ ] Add `--force` flag for reconfiguration
- [ ] Wire up service dependencies

### Phase 6: Testing

- [ ] Unit tests for ValidationService
- [ ] Unit tests for BackupService
- [ ] Unit tests for WizardService (mocked I/O)
- [ ] Integration tests for full wizard flow

## Code Snippets

### Adding the wizard command

```python
# src/doit_cli/cli/provider_command.py

from ..services.wizard_service import WizardService
from ..services.validation_service import ValidationService
from ..services.backup_service import ConfigBackupService

@app.command(name="wizard")
def wizard_command(
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force reconfiguration without confirmation",
    ),
) -> None:
    """Interactive wizard to configure git provider."""
    validation_service = ValidationService()
    backup_service = ConfigBackupService()
    config = ProviderConfig.load()

    wizard = WizardService(
        console=console,
        validation_service=validation_service,
        backup_service=backup_service,
        existing_config=config,
    )

    try:
        result = wizard.run(force_reconfigure=force)
        if result.success:
            console.print("[green]Configuration complete![/green]")
        elif result.cancelled:
            console.print("[yellow]Wizard cancelled[/yellow]")
            raise typer.Exit(code=0)
    except KeyboardInterrupt:
        wizard.handle_cancellation()
        console.print("\n[yellow]Wizard cancelled[/yellow]")
        raise typer.Exit(code=0)
```

### Validation service example

```python
# src/doit_cli/services/validation_service.py

import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime, UTC
from typing import Any

import httpx


@dataclass
class ValidationResult:
    success: bool
    step: str
    timestamp: datetime
    error_message: str | None = None
    suggestion: str | None = None
    details: dict[str, Any] | None = None


class ValidationService:
    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout

    def check_gh_cli_installed(self) -> bool:
        return shutil.which("gh") is not None

    def check_gh_cli_authenticated(
        self, enterprise_host: str | None = None
    ) -> tuple[bool, str | None]:
        cmd = ["gh", "auth", "status"]
        if enterprise_host:
            cmd.extend(["--hostname", enterprise_host])

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                # Parse "Logged in to github.com as USERNAME"
                for line in result.stderr.split("\n"):
                    if "Logged in" in line and " as " in line:
                        username = line.split(" as ")[-1].strip()
                        return True, username
                return True, None
            return False, result.stderr
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except FileNotFoundError:
            return False, "gh CLI not found"
```

### Wizard service flow example

```python
# src/doit_cli/services/wizard_service.py

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

from ..services.providers.base import ProviderType
from .validation_service import ValidationService


class WizardService:
    def __init__(
        self,
        console: Console,
        validation_service: ValidationService,
        backup_service: ConfigBackupService,
        existing_config: ProviderConfig,
    ):
        self.console = console
        self.validation = validation_service
        self.backup = backup_service
        self.existing_config = existing_config

    def run(self, force_reconfigure: bool = False) -> WizardResult:
        self._display_header()

        # Check for existing config
        if self.existing_config.is_configured() and not force_reconfigure:
            if not self._confirm_reconfigure():
                return WizardResult(success=False, cancelled=True)

            self.backup.create_backup(
                self.existing_config, reason="reconfigure"
            )

        # Detect or select provider
        detected, source = self.detect_provider()
        provider = self.select_provider(detected)

        # Collect provider-specific config
        if provider == ProviderType.GITHUB:
            config_values = self.collect_github_config()
        elif provider == ProviderType.AZURE_DEVOPS:
            config_values = self.collect_azure_devops_config()
        elif provider == ProviderType.GITLAB:
            config_values = self.collect_gitlab_config()

        # Validate and save
        result = self.validate_and_save(provider, config_values)

        if result.success:
            self.display_summary(provider, config_values, result)

        return WizardResult(
            success=result.success,
            provider=provider,
            config=self.existing_config,
        )

    def _display_header(self):
        self.console.print(
            Panel(
                "[bold]Git Provider Configuration Wizard[/bold]\n\n"
                "This wizard will guide you through configuring your git provider.",
                title="Welcome",
            )
        )
```

## Testing Examples

### Unit test for validation

```python
# tests/unit/services/test_validation_service.py

import pytest
from unittest.mock import patch, MagicMock
from doit_cli.services.validation_service import ValidationService


class TestValidationService:
    def test_check_gh_cli_installed_when_present(self):
        with patch("shutil.which", return_value="/usr/bin/gh"):
            service = ValidationService()
            assert service.check_gh_cli_installed() is True

    def test_check_gh_cli_installed_when_missing(self):
        with patch("shutil.which", return_value=None):
            service = ValidationService()
            assert service.check_gh_cli_installed() is False

    def test_validate_azure_devops_invalid_pat(self):
        with patch("httpx.Client") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_client.return_value.__enter__.return_value.get.return_value = mock_response

            service = ValidationService()
            result = service.validate_azure_devops(
                organization="myorg",
                project="myproject",
                pat="invalid-pat",
            )

            assert result.success is False
            assert "Invalid" in result.error_message
```

### Integration test for wizard

```python
# tests/integration/test_provider_wizard.py

import pytest
from typer.testing import CliRunner
from doit_cli.cli.main import app


@pytest.fixture
def runner():
    return CliRunner()


class TestProviderWizard:
    def test_wizard_detects_github_from_remote(self, runner, tmp_path, monkeypatch):
        # Setup git repo with GitHub remote
        monkeypatch.chdir(tmp_path)
        # ... setup git remote ...

        result = runner.invoke(app, ["provider", "wizard"], input="n\n")
        assert "GitHub" in result.output

    def test_wizard_cancellation_preserves_config(self, runner, tmp_path):
        # ... test that Ctrl+C doesn't corrupt config ...
        pass
```

## References

- [Spec](spec.md) - Feature requirements
- [Research](research.md) - Technical analysis
- [Data Model](data-model.md) - Entity definitions
- [Contracts](contracts/) - Service interfaces
