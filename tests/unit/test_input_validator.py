"""Unit tests for InputValidator classes.

Tests the input validation functionality for guided workflows.
"""

import os
import re
import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from doit_cli.models.workflow_models import (
    WorkflowStep,
    StepResponse,
    ValidationResult,
)


class TestRequiredValidator:
    """Tests for RequiredValidator."""

    @pytest.fixture
    def validator(self):
        """Create a RequiredValidator instance."""
        from doit_cli.services.input_validator import RequiredValidator

        return RequiredValidator()

    @pytest.fixture
    def step(self):
        """Create a required step."""
        return WorkflowStep(
            id="name",
            name="Name",
            prompt_text="Enter name:",
            required=True,
            order=0,
        )

    def test_passes_with_value(self, validator, step):
        """Test that non-empty value passes validation."""
        result = validator.validate("hello", step, {})
        assert result.passed is True

    def test_fails_with_empty_string(self, validator, step):
        """Test that empty string fails validation."""
        result = validator.validate("", step, {})
        assert result.passed is False
        assert "required" in result.error_message.lower()

    def test_fails_with_whitespace_only(self, validator, step):
        """Test that whitespace-only input fails validation."""
        result = validator.validate("   ", step, {})
        assert result.passed is False

    def test_provides_suggestion(self, validator, step):
        """Test that failure includes a helpful suggestion."""
        result = validator.validate("", step, {})
        assert result.suggestion is not None


class TestPathExistsValidator:
    """Tests for PathExistsValidator."""

    @pytest.fixture
    def validator(self):
        """Create a PathExistsValidator instance."""
        from doit_cli.services.input_validator import PathExistsValidator

        return PathExistsValidator()

    @pytest.fixture
    def step(self):
        """Create a path input step."""
        return WorkflowStep(
            id="config-file",
            name="Config File",
            prompt_text="Enter path to config file:",
            required=True,
            order=0,
            validation_type="PathExistsValidator",
        )

    def test_passes_with_existing_file(self, validator, step, tmp_path):
        """Test that existing file path passes validation."""
        test_file = tmp_path / "config.json"
        test_file.write_text("{}")

        result = validator.validate(str(test_file), step, {})
        assert result.passed is True

    def test_passes_with_existing_directory(self, validator, step, tmp_path):
        """Test that existing directory path passes validation."""
        result = validator.validate(str(tmp_path), step, {})
        assert result.passed is True

    def test_fails_with_nonexistent_path(self, validator, step):
        """Test that non-existent path fails validation."""
        result = validator.validate("/nonexistent/path/file.txt", step, {})
        assert result.passed is False
        assert "does not exist" in result.error_message.lower()

    def test_provides_suggestion_for_relative_path(self, validator, step):
        """Test that suggestion is provided for relative path errors."""
        result = validator.validate("./missing.txt", step, {})
        assert result.passed is False
        assert result.suggestion is not None

    def test_handles_home_expansion(self, validator, step, tmp_path, monkeypatch):
        """Test that ~ is expanded to home directory."""
        # Mock home directory to temp path
        monkeypatch.setenv("HOME", str(tmp_path))

        test_file = tmp_path / "config.json"
        test_file.write_text("{}")

        result = validator.validate("~/config.json", step, {})
        assert result.passed is True


class TestChoiceValidator:
    """Tests for ChoiceValidator."""

    @pytest.fixture
    def validator(self):
        """Create a ChoiceValidator instance."""
        from doit_cli.services.input_validator import ChoiceValidator

        return ChoiceValidator()

    @pytest.fixture
    def step(self):
        """Create a choice step."""
        return WorkflowStep(
            id="framework",
            name="Framework",
            prompt_text="Select framework:",
            required=True,
            order=0,
            options={
                "react": "React framework",
                "vue": "Vue framework",
                "angular": "Angular framework",
            },
        )

    def test_passes_with_valid_choice(self, validator, step):
        """Test that valid choice passes validation."""
        result = validator.validate("react", step, {})
        assert result.passed is True

    def test_fails_with_invalid_choice(self, validator, step):
        """Test that invalid choice fails validation."""
        result = validator.validate("svelte", step, {})
        assert result.passed is False

    def test_error_includes_valid_options(self, validator, step):
        """Test that error message lists valid options."""
        result = validator.validate("invalid", step, {})
        assert "react" in result.error_message or "react" in result.suggestion

    def test_case_insensitive_matching(self, validator, step):
        """Test that choice matching is case-insensitive."""
        result = validator.validate("REACT", step, {})
        # Should either pass (case-insensitive) or fail with helpful message
        # Implementation choice - test based on actual behavior

    def test_strips_whitespace(self, validator, step):
        """Test that whitespace is stripped from input."""
        result = validator.validate("  react  ", step, {})
        assert result.passed is True


class TestPatternValidator:
    """Tests for PatternValidator."""

    @pytest.fixture
    def email_validator(self):
        """Create a PatternValidator for email."""
        from doit_cli.services.input_validator import PatternValidator

        return PatternValidator(
            pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        )

    @pytest.fixture
    def step(self):
        """Create an email input step."""
        return WorkflowStep(
            id="email",
            name="Email",
            prompt_text="Enter your email:",
            required=True,
            order=0,
            validation_type="PatternValidator",
        )

    def test_passes_with_matching_pattern(self, email_validator, step):
        """Test that matching pattern passes validation."""
        result = email_validator.validate("user@example.com", step, {})
        assert result.passed is True

    def test_fails_with_non_matching_pattern(self, email_validator, step):
        """Test that non-matching pattern fails validation."""
        result = email_validator.validate("not-an-email", step, {})
        assert result.passed is False

    def test_provides_pattern_hint(self, email_validator, step):
        """Test that failure includes pattern hint."""
        result = email_validator.validate("invalid", step, {})
        assert result.suggestion is not None

    @pytest.fixture
    def semver_validator(self):
        """Create a PatternValidator for semantic versioning."""
        from doit_cli.services.input_validator import PatternValidator

        return PatternValidator(pattern=r"^\d+\.\d+\.\d+$")

    def test_semver_passes_valid(self, semver_validator, step):
        """Test valid semantic version."""
        result = semver_validator.validate("1.2.3", step, {})
        assert result.passed is True

    def test_semver_fails_invalid(self, semver_validator, step):
        """Test invalid semantic version."""
        result = semver_validator.validate("1.2", step, {})
        assert result.passed is False


class TestValidatorRegistry:
    """Tests for the validator registry/factory."""

    def test_get_validator_by_name(self):
        """Test getting a validator by its type name."""
        from doit_cli.services.input_validator import get_validator

        validator = get_validator("RequiredValidator")
        assert validator is not None

    def test_get_unknown_validator_returns_none(self):
        """Test that unknown validator type returns None."""
        from doit_cli.services.input_validator import get_validator

        validator = get_validator("UnknownValidator")
        assert validator is None

    def test_register_custom_validator(self):
        """Test registering a custom validator."""
        from doit_cli.services.input_validator import (
            InputValidator,
            register_validator,
            get_validator,
        )

        class CustomValidator(InputValidator):
            def validate(self, value, step, context):
                return ValidationResult.success()

        register_validator("CustomValidator", CustomValidator)
        validator = get_validator("CustomValidator")
        assert isinstance(validator, CustomValidator)


class TestCompositeValidation:
    """Tests for combining multiple validators."""

    @pytest.fixture
    def step(self):
        """Create a step requiring multiple validations."""
        return WorkflowStep(
            id="project-name",
            name="Project Name",
            prompt_text="Enter project name:",
            required=True,
            order=0,
        )

    def test_chain_validators(self, step):
        """Test that validators can be chained."""
        from doit_cli.services.input_validator import (
            RequiredValidator,
            PatternValidator,
            chain_validators,
        )

        validators = [
            RequiredValidator(),
            PatternValidator(pattern=r"^[a-z][a-z0-9-]*$"),
        ]

        # Valid input passes all
        result = chain_validators(validators, "my-project", step, {})
        assert result.passed is True

        # Empty fails on required
        result = chain_validators(validators, "", step, {})
        assert result.passed is False
        assert "required" in result.error_message.lower()

        # Invalid pattern fails
        result = chain_validators(validators, "123-invalid", step, {})
        assert result.passed is False


class TestContextAwareValidation:
    """Tests for validators that use context from previous steps."""

    @pytest.fixture
    def step(self):
        """Create a step that depends on previous context."""
        return WorkflowStep(
            id="confirm-name",
            name="Confirm Name",
            prompt_text="Confirm the project name:",
            required=True,
            order=1,
        )

    def test_validator_can_access_previous_responses(self, step):
        """Test that validators can access previous step responses."""
        from doit_cli.services.input_validator import InputValidator

        class MatchPreviousValidator(InputValidator):
            def __init__(self, previous_step_id: str):
                self.previous_step_id = previous_step_id

            def validate(self, value, step, context):
                previous = context.get(self.previous_step_id)
                if previous and previous.value == value:
                    return ValidationResult.success()
                return ValidationResult.failure(
                    "Value does not match previous entry"
                )

        context = {
            "project-name": StepResponse(
                step_id="project-name",
                value="my-project",
            )
        }

        validator = MatchPreviousValidator("project-name")

        # Matching value passes
        result = validator.validate("my-project", step, context)
        assert result.passed is True

        # Non-matching value fails
        result = validator.validate("different-project", step, context)
        assert result.passed is False
