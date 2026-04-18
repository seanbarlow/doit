"""Data models for the provider configuration wizard.

This module contains enums, dataclasses, and exceptions used by the
wizard service to manage state, track validation results, and handle
configuration flow.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from ..services.providers.base import ProviderType


class WizardStep(str, Enum):
    """Wizard step identifiers."""

    # Detection and selection
    DETECT_PROVIDER = "detect_provider"
    SELECT_PROVIDER = "select_provider"

    # GitHub flow
    GITHUB_CHECK_CLI = "github_check_cli"
    GITHUB_ENTERPRISE = "github_enterprise"
    GITHUB_VALIDATE = "github_validate"

    # Azure DevOps flow
    ADO_ORGANIZATION = "ado_organization"
    ADO_PROJECT = "ado_project"
    ADO_PAT = "ado_pat"
    ADO_VALIDATE = "ado_validate"

    # GitLab flow
    GITLAB_HOST = "gitlab_host"
    GITLAB_TOKEN = "gitlab_token"
    GITLAB_VALIDATE = "gitlab_validate"

    # Common completion steps
    CONFIRM = "confirm"
    COMPLETE = "complete"


@dataclass
class ValidationResult:
    """Result of a validation operation."""

    step: WizardStep
    success: bool
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    error_message: str | None = None
    suggestion: str | None = None
    details: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def passed(
        cls,
        step: WizardStep,
        details: dict[str, Any] | None = None,
    ) -> ValidationResult:
        """Create a successful validation result."""
        return cls(
            step=step,
            success=True,
            details=details or {},
        )

    @classmethod
    def failed(
        cls,
        step: WizardStep,
        error: str,
        suggestion: str | None = None,
    ) -> ValidationResult:
        """Create a failed validation result."""
        return cls(
            step=step,
            success=False,
            error_message=error,
            suggestion=suggestion,
        )


@dataclass
class WizardState:
    """Tracks wizard progress, collected values, and validation results."""

    current_step: WizardStep
    provider_type: ProviderType | None = None
    auto_detected: bool = False
    detection_source: str | None = None
    collected_values: dict[str, Any] = field(default_factory=dict)
    validation_results: list[ValidationResult] = field(default_factory=list)
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def add_validation(self, result: ValidationResult) -> None:
        """Add a validation result to the state."""
        self.validation_results.append(result)

    def get_last_validation(self) -> ValidationResult | None:
        """Get the most recent validation result."""
        return self.validation_results[-1] if self.validation_results else None

    def is_validation_successful(self) -> bool:
        """Check if all validations have passed."""
        return all(v.success for v in self.validation_results)


@dataclass
class WizardResult:
    """Result of wizard execution."""

    success: bool
    provider: ProviderType | None = None
    cancelled: bool = False
    error_message: str | None = None

    @classmethod
    def completed(cls, provider: ProviderType) -> WizardResult:
        """Create a successful completion result."""
        return cls(success=True, provider=provider)

    @classmethod
    def canceled(cls) -> WizardResult:
        """Create a cancellation result."""
        return cls(success=False, cancelled=True)

    @classmethod
    def error(cls, message: str) -> WizardResult:
        """Create an error result."""
        return cls(success=False, error_message=message)


@dataclass
class ConfigBackup:
    """A stored configuration backup."""

    backup_id: str  # Format: YYYYMMDD_HHMMSS
    created_at: datetime
    reason: str
    config_data: dict[str, Any]

    @classmethod
    def create(
        cls,
        reason: str,
        config_data: dict[str, Any],
    ) -> ConfigBackup:
        """Create a new backup with auto-generated ID."""
        now = datetime.now(UTC)
        # Include microseconds for uniqueness in rapid succession
        backup_id = now.strftime("%Y%m%d_%H%M%S") + f"_{now.microsecond:06d}"
        return cls(
            backup_id=backup_id,
            created_at=now,
            reason=reason,
            config_data=config_data,
        )


class WizardCancelledError(Exception):
    """Raised when user cancels the wizard."""

    pass


class WizardStepError(Exception):
    """Raised when a wizard step fails."""

    def __init__(
        self,
        step: WizardStep,
        message: str,
        suggestion: str | None = None,
    ):
        self.step = step
        self.message = message
        self.suggestion = suggestion
        super().__init__(message)


class BackupNotFoundError(Exception):
    """Raised when a requested backup doesn't exist."""

    def __init__(self, backup_id: str):
        self.backup_id = backup_id
        super().__init__(f"Backup '{backup_id}' not found")
