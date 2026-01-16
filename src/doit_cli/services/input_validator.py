"""Input validators for workflow steps.

This module provides validators for step inputs with real-time feedback.
"""

import os
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Protocol, runtime_checkable

from ..models.workflow_models import (
    WorkflowStep,
    StepResponse,
    ValidationResult,
)


# =============================================================================
# Validator Protocol and Base Class
# =============================================================================


@runtime_checkable
class InputValidator(Protocol):
    """Protocol for step validators."""

    def validate(
        self,
        value: str,
        step: WorkflowStep,
        context: dict[str, StepResponse],
    ) -> ValidationResult:
        """Validate a step input value.

        Args:
            value: User-provided input
            step: Step being validated
            context: Previous step responses

        Returns:
            ValidationResult with pass/fail and messages
        """
        ...


class BaseValidator(ABC):
    """Abstract base class for validators with common functionality."""

    @abstractmethod
    def validate(
        self,
        value: str,
        step: WorkflowStep,
        context: dict[str, StepResponse],
    ) -> ValidationResult:
        """Validate the input value."""
        ...


# =============================================================================
# Built-in Validators
# =============================================================================


class RequiredValidator(BaseValidator):
    """Validates that a value is non-empty."""

    def validate(
        self,
        value: str,
        step: WorkflowStep,
        context: dict[str, StepResponse],
    ) -> ValidationResult:
        """Check that value is not empty or whitespace-only."""
        if not value or not value.strip():
            return ValidationResult.failure(
                error_message="This field is required",
                suggestion="Please enter a value",
            )
        return ValidationResult.success()


class PathExistsValidator(BaseValidator):
    """Validates that a file or directory path exists."""

    def __init__(self, must_be_file: bool = False, must_be_dir: bool = False):
        """Initialize the validator.

        Args:
            must_be_file: If True, path must be a file (not directory)
            must_be_dir: If True, path must be a directory (not file)
        """
        self.must_be_file = must_be_file
        self.must_be_dir = must_be_dir

    def validate(
        self,
        value: str,
        step: WorkflowStep,
        context: dict[str, StepResponse],
    ) -> ValidationResult:
        """Check that the path exists."""
        if not value:
            return ValidationResult.failure(
                error_message="Path is required",
                suggestion="Enter a valid file or directory path",
            )

        # Expand ~ to home directory
        path = Path(os.path.expanduser(value))

        if not path.exists():
            return ValidationResult.failure(
                error_message=f"Path does not exist: {value}",
                suggestion="Check the path and try again. Use absolute paths for reliability.",
            )

        if self.must_be_file and not path.is_file():
            return ValidationResult.failure(
                error_message=f"Path is not a file: {value}",
                suggestion="Please provide a path to a file, not a directory",
            )

        if self.must_be_dir and not path.is_dir():
            return ValidationResult.failure(
                error_message=f"Path is not a directory: {value}",
                suggestion="Please provide a path to a directory, not a file",
            )

        return ValidationResult.success()


class ChoiceValidator(BaseValidator):
    """Validates that a value is one of the allowed options."""

    def __init__(self, case_sensitive: bool = False):
        """Initialize the validator.

        Args:
            case_sensitive: Whether to match case-sensitively
        """
        self.case_sensitive = case_sensitive

    def validate(
        self,
        value: str,
        step: WorkflowStep,
        context: dict[str, StepResponse],
    ) -> ValidationResult:
        """Check that value is one of the step's options."""
        if not step.options:
            return ValidationResult.failure(
                error_message="No options defined for this step",
                suggestion="This step is misconfigured",
            )

        # Normalize input
        normalized_value = value.strip()
        if not self.case_sensitive:
            normalized_value = normalized_value.lower()

        # Check against options
        for option_key in step.options:
            compare_key = option_key if self.case_sensitive else option_key.lower()
            if normalized_value == compare_key:
                return ValidationResult.success()

        # Build helpful error message
        valid_options = ", ".join(step.options.keys())
        return ValidationResult.failure(
            error_message=f"Invalid choice: '{value}'",
            suggestion=f"Valid options are: {valid_options}",
        )


class PatternValidator(BaseValidator):
    """Validates that a value matches a regex pattern."""

    def __init__(self, pattern: str, description: str | None = None):
        """Initialize the validator.

        Args:
            pattern: Regex pattern to match
            description: Human-readable description of expected format
        """
        self.pattern = pattern
        self.regex = re.compile(pattern)
        self.description = description

    def validate(
        self,
        value: str,
        step: WorkflowStep,
        context: dict[str, StepResponse],
    ) -> ValidationResult:
        """Check that value matches the pattern."""
        if self.regex.match(value):
            return ValidationResult.success()

        suggestion = self.description or f"Value must match pattern: {self.pattern}"
        return ValidationResult.failure(
            error_message="Invalid format",
            suggestion=suggestion,
        )


# =============================================================================
# Validator Registry
# =============================================================================


_VALIDATORS: dict[str, type[BaseValidator]] = {
    "RequiredValidator": RequiredValidator,
    "PathExistsValidator": PathExistsValidator,
    "ChoiceValidator": ChoiceValidator,
    "PatternValidator": PatternValidator,
}


def register_validator(name: str, validator_class: type[BaseValidator]) -> None:
    """Register a custom validator class.

    Args:
        name: Name to register the validator under
        validator_class: The validator class to register
    """
    _VALIDATORS[name] = validator_class


def get_validator(name: str) -> BaseValidator | None:
    """Get a validator instance by name.

    Args:
        name: Name of the validator type

    Returns:
        Validator instance or None if not found
    """
    validator_class = _VALIDATORS.get(name)
    if validator_class:
        return validator_class()
    return None


def get_validator_class(name: str) -> type[BaseValidator] | None:
    """Get a validator class by name.

    Args:
        name: Name of the validator type

    Returns:
        Validator class or None if not found
    """
    return _VALIDATORS.get(name)


# =============================================================================
# Utility Functions
# =============================================================================


def chain_validators(
    validators: list[BaseValidator],
    value: str,
    step: WorkflowStep,
    context: dict[str, StepResponse],
) -> ValidationResult:
    """Run multiple validators in sequence, stopping at first failure.

    Args:
        validators: List of validators to run
        value: Value to validate
        step: Current workflow step
        context: Previous step responses

    Returns:
        First failing ValidationResult or success if all pass
    """
    for validator in validators:
        result = validator.validate(value, step, context)
        if not result.passed:
            return result
    return ValidationResult.success()


def validate_step(
    value: str,
    step: WorkflowStep,
    context: dict[str, StepResponse],
) -> ValidationResult:
    """Validate a step input using the step's configured validator.

    Args:
        value: Value to validate
        step: Workflow step with validation_type
        context: Previous step responses

    Returns:
        ValidationResult from the step's validator
    """
    # Required validation for required steps
    if step.required:
        required_validator = RequiredValidator()
        result = required_validator.validate(value, step, context)
        if not result.passed:
            return result

    # Choice validation for steps with options
    if step.options:
        choice_validator = ChoiceValidator()
        result = choice_validator.validate(value, step, context)
        if not result.passed:
            return result

    # Custom validator if specified
    if step.validation_type:
        validator = get_validator(step.validation_type)
        if validator:
            return validator.validate(value, step, context)

    return ValidationResult.success()
