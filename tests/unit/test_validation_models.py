"""Unit tests for validation models."""

import pytest
from datetime import datetime

from doit_cli.models.validation_models import (
    Severity,
    ValidationConfig,
    ValidationIssue,
    ValidationResult,
    ValidationRule,
    ValidationStatus,
)


class TestSeverity:
    """Tests for Severity enum."""

    def test_severity_values(self):
        """Test severity enum values."""
        assert Severity.ERROR.value == "error"
        assert Severity.WARNING.value == "warning"
        assert Severity.INFO.value == "info"


class TestValidationStatus:
    """Tests for ValidationStatus enum."""

    def test_status_values(self):
        """Test status enum values."""
        assert ValidationStatus.PASS.value == "pass"
        assert ValidationStatus.WARN.value == "warn"
        assert ValidationStatus.FAIL.value == "fail"


class TestValidationRule:
    """Tests for ValidationRule dataclass."""

    def test_create_rule(self):
        """Test creating a validation rule."""
        rule = ValidationRule(
            id="test-rule",
            name="Test Rule",
            description="A test rule",
            severity=Severity.WARNING,
            category="test",
            pattern=r"test.*pattern",
        )

        assert rule.id == "test-rule"
        assert rule.name == "Test Rule"
        assert rule.severity == Severity.WARNING
        assert rule.enabled is True
        assert rule.builtin is True

    def test_rule_defaults(self):
        """Test rule default values."""
        rule = ValidationRule(
            id="test",
            name="Test",
            description="Test",
            severity=Severity.INFO,
            category="test",
        )

        assert rule.pattern is None
        assert rule.enabled is True
        assert rule.builtin is True


class TestValidationIssue:
    """Tests for ValidationIssue dataclass."""

    def test_create_issue(self):
        """Test creating a validation issue."""
        issue = ValidationIssue(
            rule_id="test-rule",
            severity=Severity.ERROR,
            line_number=10,
            message="Test error message",
            suggestion="Fix the issue",
        )

        assert issue.rule_id == "test-rule"
        assert issue.severity == Severity.ERROR
        assert issue.line_number == 10
        assert issue.message == "Test error message"
        assert issue.suggestion == "Fix the issue"

    def test_issue_without_suggestion(self):
        """Test issue can be created without suggestion."""
        issue = ValidationIssue(
            rule_id="test",
            severity=Severity.INFO,
            line_number=1,
            message="Info message",
        )

        assert issue.suggestion is None


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_create_empty_result(self):
        """Test creating an empty validation result."""
        result = ValidationResult(
            spec_path="/path/to/spec.md",
            validated_at=datetime.now(),
        )

        assert result.spec_path == "/path/to/spec.md"
        assert result.issues == []
        assert result.quality_score == 100

    def test_add_issue(self):
        """Test adding an issue to result."""
        result = ValidationResult(
            spec_path="/path/to/spec.md",
            validated_at=datetime.now(),
        )

        issue = ValidationIssue(
            rule_id="test",
            severity=Severity.ERROR,
            line_number=1,
            message="Error",
        )

        result.add_issue(issue)

        assert len(result.issues) == 1
        assert result.issues[0] == issue

    def test_error_count(self):
        """Test error count calculation."""
        result = ValidationResult(
            spec_path="/path/to/spec.md",
            issues=[
                ValidationIssue("r1", Severity.ERROR, 1, "E1"),
                ValidationIssue("r2", Severity.ERROR, 2, "E2"),
                ValidationIssue("r3", Severity.WARNING, 3, "W1"),
            ],
            validated_at=datetime.now(),
        )

        assert result.error_count == 2

    def test_warning_count(self):
        """Test warning count calculation."""
        result = ValidationResult(
            spec_path="/path/to/spec.md",
            issues=[
                ValidationIssue("r1", Severity.ERROR, 1, "E1"),
                ValidationIssue("r2", Severity.WARNING, 2, "W1"),
                ValidationIssue("r3", Severity.WARNING, 3, "W2"),
            ],
            validated_at=datetime.now(),
        )

        assert result.warning_count == 2

    def test_info_count(self):
        """Test info count calculation."""
        result = ValidationResult(
            spec_path="/path/to/spec.md",
            issues=[
                ValidationIssue("r1", Severity.INFO, 1, "I1"),
                ValidationIssue("r2", Severity.INFO, 2, "I2"),
                ValidationIssue("r3", Severity.INFO, 3, "I3"),
            ],
            validated_at=datetime.now(),
        )

        assert result.info_count == 3

    def test_status_pass(self):
        """Test status is PASS when no errors or warnings."""
        result = ValidationResult(
            spec_path="/path/to/spec.md",
            quality_score=100,
            validated_at=datetime.now(),
        )

        assert result.status == ValidationStatus.PASS

    def test_status_warn(self):
        """Test status is WARN when warnings but no errors."""
        result = ValidationResult(
            spec_path="/path/to/spec.md",
            issues=[
                ValidationIssue("r1", Severity.WARNING, 1, "W1"),
            ],
            quality_score=75,
            validated_at=datetime.now(),
        )

        assert result.status == ValidationStatus.WARN

    def test_status_fail(self):
        """Test status is FAIL when errors present."""
        result = ValidationResult(
            spec_path="/path/to/spec.md",
            issues=[
                ValidationIssue("r1", Severity.ERROR, 1, "E1"),
            ],
            quality_score=50,
            validated_at=datetime.now(),
        )

        assert result.status == ValidationStatus.FAIL


class TestValidationConfig:
    """Tests for ValidationConfig dataclass."""

    def test_default_config(self):
        """Test creating default configuration."""
        config = ValidationConfig.default()

        assert config.disabled_rules == []
        assert config.overrides == []
        assert config.custom_rules == []

    def test_config_with_disabled_rules(self):
        """Test config with disabled rules."""
        config = ValidationConfig(
            disabled_rules=["rule-1", "rule-2"],
            overrides=[],
            custom_rules=[],
        )

        assert len(config.disabled_rules) == 2
        assert "rule-1" in config.disabled_rules
