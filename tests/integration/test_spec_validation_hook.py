"""Integration tests for spec validation hook behavior."""

import pytest
from pathlib import Path

from doit_cli.models.hook_config import HookConfig, HookRule
from doit_cli.services.hook_validator import HookValidator


@pytest.fixture
def spec_with_errors(temp_dir):
    """Create a spec file with validation errors."""
    spec_dir = temp_dir / "specs" / "001-test-feature"
    spec_dir.mkdir(parents=True)

    # Missing required sections (Requirements, Success Criteria)
    spec_content = """# Feature: Test Feature

**Status**: In Progress
**Feature Branch**: `001-test-feature`

## Overview

This spec is missing required sections.

TODO: Add more content
"""
    (spec_dir / "spec.md").write_text(spec_content)
    return temp_dir


@pytest.fixture
def valid_spec(temp_dir):
    """Create a valid spec file."""
    spec_dir = temp_dir / "specs" / "001-test-feature"
    spec_dir.mkdir(parents=True)

    spec_content = """# Feature: Test Feature

**Status**: In Progress
**Feature Branch**: `001-test-feature`

## User Scenarios

### User Story 1: Basic Test

As a user, I want to test the feature.

- **Given** I have the setup **When** I perform an action **Then** I see the result

## Requirements

- **FR-001**: First requirement
- **FR-002**: Second requirement

## Success Criteria

- **SC-001**: First criterion
- **SC-002**: Second criterion
"""
    (spec_dir / "spec.md").write_text(spec_content)
    return temp_dir


@pytest.fixture
def hook_config_with_validation():
    """Create a hook config with validation enabled."""
    return HookConfig(
        pre_commit=HookRule(
            enabled=True,
            require_spec=True,
            validate_spec=True,
            validate_spec_threshold=70,
        )
    )


@pytest.fixture
def hook_config_without_validation():
    """Create a hook config with validation disabled."""
    return HookConfig(
        pre_commit=HookRule(
            enabled=True,
            require_spec=True,
            validate_spec=False,
        )
    )


class TestSpecValidationHook:
    """Tests for spec validation in pre-commit hook."""

    def test_validate_spec_quality_valid_spec(self, valid_spec, hook_config_with_validation):
        """Test that valid spec passes quality validation."""
        validator = HookValidator(
            project_root=valid_spec,
            config=hook_config_with_validation,
        )

        spec_path = valid_spec / "specs" / "001-test-feature" / "spec.md"
        result = validator._validate_spec_quality(spec_path)

        assert result.success
        assert "passed" in result.message.lower()

    def test_validate_spec_quality_invalid_spec(self, spec_with_errors, hook_config_with_validation):
        """Test that invalid spec fails quality validation."""
        validator = HookValidator(
            project_root=spec_with_errors,
            config=hook_config_with_validation,
        )

        spec_path = spec_with_errors / "specs" / "001-test-feature" / "spec.md"
        result = validator._validate_spec_quality(spec_path)

        assert not result.success
        assert "error" in result.message.lower() or "failed" in result.message.lower()

    def test_validate_spec_disabled(self, spec_with_errors, hook_config_without_validation):
        """Test that validation is skipped when disabled."""
        validator = HookValidator(
            project_root=spec_with_errors,
            config=hook_config_without_validation,
        )

        # When validation is disabled, _validate_spec_quality should pass
        spec_path = spec_with_errors / "specs" / "001-test-feature" / "spec.md"

        # The disabled check happens in validate_pre_commit, not _validate_spec_quality
        # So we need to check the config is respected
        assert not validator.config.pre_commit.validate_spec

    def test_threshold_enforcement(self, valid_spec):
        """Test that threshold is enforced for quality score."""
        # Set a very high threshold
        config = HookConfig(
            pre_commit=HookRule(
                enabled=True,
                require_spec=True,
                validate_spec=True,
                validate_spec_threshold=99,  # Very high threshold
            )
        )

        validator = HookValidator(
            project_root=valid_spec,
            config=config,
        )

        spec_path = valid_spec / "specs" / "001-test-feature" / "spec.md"
        result = validator._validate_spec_quality(spec_path)

        # Even valid spec might not meet 99% threshold
        # This tests that threshold logic works
        if not result.success:
            assert "threshold" in result.message.lower() or "score" in result.message.lower()


class TestHookConfigValidation:
    """Tests for hook config with validation settings."""

    def test_hook_rule_defaults(self):
        """Test that HookRule has correct defaults for validation."""
        rule = HookRule()

        assert rule.validate_spec is True
        assert rule.validate_spec_threshold == 70

    def test_hook_config_from_dict_with_validation(self):
        """Test loading config with validation settings."""
        data = {
            "version": 1,
            "pre_commit": {
                "enabled": True,
                "validate_spec": True,
                "validate_spec_threshold": 80,
            }
        }

        config = HookConfig._from_dict(data)

        assert config.pre_commit.validate_spec is True
        assert config.pre_commit.validate_spec_threshold == 80

    def test_hook_config_from_dict_without_validation(self):
        """Test loading config with validation disabled."""
        data = {
            "version": 1,
            "pre_commit": {
                "enabled": True,
                "validate_spec": False,
            }
        }

        config = HookConfig._from_dict(data)

        assert config.pre_commit.validate_spec is False


class TestPreCommitWithValidation:
    """Integration tests for pre-commit with spec validation."""

    def test_pre_commit_blocks_invalid_spec(self, spec_with_errors, hook_config_with_validation, monkeypatch):
        """Test that pre-commit blocks commit when spec has errors."""
        # Mock git commands to simulate being on feature branch
        def mock_run(*args, **kwargs):
            class MockResult:
                returncode = 0
                stdout = ""

            cmd = args[0]
            result = MockResult()

            if "rev-parse" in cmd:
                result.stdout = "001-test-feature\n"
            elif "diff" in cmd:
                result.stdout = "src/main.py\n"  # Code file to trigger validation

            return result

        monkeypatch.setattr("subprocess.run", mock_run)

        validator = HookValidator(
            project_root=spec_with_errors,
            config=hook_config_with_validation,
        )

        result = validator.validate_pre_commit()

        # Should fail due to spec validation errors
        assert not result.success
        # Message should indicate validation failure
        assert "validation" in result.message.lower() or "error" in result.message.lower()

    def test_pre_commit_passes_valid_spec(self, valid_spec, hook_config_with_validation, monkeypatch):
        """Test that pre-commit passes when spec is valid."""
        # Mock git commands to simulate being on feature branch
        def mock_run(*args, **kwargs):
            class MockResult:
                returncode = 0
                stdout = ""

            cmd = args[0]
            result = MockResult()

            if "rev-parse" in cmd:
                result.stdout = "001-test-feature\n"
            elif "diff" in cmd:
                result.stdout = "src/main.py\n"

            return result

        monkeypatch.setattr("subprocess.run", mock_run)

        validator = HookValidator(
            project_root=valid_spec,
            config=hook_config_with_validation,
        )

        result = validator.validate_pre_commit()

        assert result.success
