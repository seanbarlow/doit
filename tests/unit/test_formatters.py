"""Unit tests for status formatters."""

import json
import pytest
from datetime import datetime
from pathlib import Path

from doit_cli.formatters.json_formatter import JsonFormatter
from doit_cli.formatters.markdown_formatter import MarkdownFormatter
from doit_cli.formatters.rich_formatter import RichFormatter
from doit_cli.models.status_models import SpecState, SpecStatus, StatusReport
from doit_cli.models.validation_models import (
    ValidationResult,
    ValidationIssue,
    Severity,
)


@pytest.fixture
def sample_report() -> StatusReport:
    """Create a sample report for testing."""
    specs = [
        SpecStatus(
            name="001-feature-a",
            path=Path("specs/001-feature-a/spec.md"),
            status=SpecState.DRAFT,
            last_modified=datetime(2026, 1, 16, 10, 0, 0),
            is_blocking=False,
        ),
        SpecStatus(
            name="002-feature-b",
            path=Path("specs/002-feature-b/spec.md"),
            status=SpecState.COMPLETE,
            last_modified=datetime(2026, 1, 15, 10, 0, 0),
            is_blocking=False,
        ),
    ]
    return StatusReport(
        specs=specs,
        generated_at=datetime(2026, 1, 16, 14, 30, 0),
        project_root=Path("/test/project"),
    )


@pytest.fixture
def report_with_validation() -> StatusReport:
    """Create a sample report with validation results."""
    specs = [
        SpecStatus(
            name="001-passing",
            path=Path("specs/001-passing/spec.md"),
            status=SpecState.COMPLETE,
            last_modified=datetime(2026, 1, 16, 10, 0, 0),
            validation_result=ValidationResult(
                spec_path="specs/001-passing/spec.md",
                issues=[],
                quality_score=100,
            ),
            is_blocking=False,
        ),
        SpecStatus(
            name="002-failing",
            path=Path("specs/002-failing/spec.md"),
            status=SpecState.IN_PROGRESS,
            last_modified=datetime(2026, 1, 15, 10, 0, 0),
            validation_result=ValidationResult(
                spec_path="specs/002-failing/spec.md",
                issues=[
                    ValidationIssue(
                        rule_id="missing-requirements",
                        severity=Severity.ERROR,
                        line_number=10,
                        message="Missing requirements section",
                        suggestion="Add a ## Requirements section",
                    ),
                    ValidationIssue(
                        rule_id="weak-acceptance",
                        severity=Severity.WARNING,
                        line_number=20,
                        message="Acceptance criteria not specific",
                    ),
                ],
                quality_score=60,
            ),
            is_blocking=True,
        ),
    ]
    return StatusReport(
        specs=specs,
        generated_at=datetime(2026, 1, 16, 14, 30, 0),
        project_root=Path("/test/project"),
    )


class TestJsonFormatter:
    """Tests for JsonFormatter."""

    def test_format_returns_valid_json(self, sample_report):
        """Test that output is valid JSON."""
        formatter = JsonFormatter()
        result = formatter.format(sample_report)

        # Should not raise
        data = json.loads(result)
        assert isinstance(data, dict)

    def test_format_contains_required_fields(self, sample_report):
        """Test that output contains all required fields."""
        formatter = JsonFormatter()
        result = formatter.format(sample_report)
        data = json.loads(result)

        assert "generated_at" in data
        assert "project_root" in data
        assert "summary" in data
        assert "specs" in data

    def test_format_summary_structure(self, sample_report):
        """Test summary field structure."""
        formatter = JsonFormatter()
        result = formatter.format(sample_report)
        data = json.loads(result)

        summary = data["summary"]
        assert summary["total"] == 2
        assert "by_status" in summary
        assert summary["by_status"]["draft"] == 1
        assert summary["by_status"]["complete"] == 1
        assert "completion_percentage" in summary
        assert "ready_to_commit" in summary

    def test_format_spec_structure(self, sample_report):
        """Test individual spec structure."""
        formatter = JsonFormatter()
        result = formatter.format(sample_report)
        data = json.loads(result)

        spec = data["specs"][0]
        assert spec["name"] == "001-feature-a"
        assert spec["status"] == "draft"
        assert "path" in spec
        assert "last_modified" in spec
        assert "is_blocking" in spec

    def test_format_with_validation(self, report_with_validation):
        """Test output includes validation data."""
        formatter = JsonFormatter()
        result = formatter.format(report_with_validation)
        data = json.loads(result)

        passing_spec = data["specs"][0]
        assert passing_spec["validation"]["passed"] is True
        assert passing_spec["validation"]["score"] == 100

        failing_spec = data["specs"][1]
        assert failing_spec["validation"]["passed"] is False
        assert failing_spec["validation"]["error_count"] == 1

    def test_format_verbose_includes_issues(self, report_with_validation):
        """Test verbose mode includes validation issues."""
        formatter = JsonFormatter()
        result = formatter.format(report_with_validation, verbose=True)
        data = json.loads(result)

        failing_spec = data["specs"][1]
        issues = failing_spec["validation"]["issues"]
        assert len(issues) == 2
        assert issues[0]["rule_id"] == "missing-requirements"
        assert issues[0]["message"] == "Missing requirements section"


class TestMarkdownFormatter:
    """Tests for MarkdownFormatter."""

    def test_format_returns_string(self, sample_report):
        """Test that output is a string."""
        formatter = MarkdownFormatter()
        result = formatter.format(sample_report)

        assert isinstance(result, str)

    def test_format_contains_header(self, sample_report):
        """Test that output contains header."""
        formatter = MarkdownFormatter()
        result = formatter.format(sample_report)

        assert "# Spec Status Report" in result
        assert "**Generated**:" in result
        assert "**Project**:" in result

    def test_format_contains_specs_table(self, sample_report):
        """Test that output contains specs table."""
        formatter = MarkdownFormatter()
        result = formatter.format(sample_report)

        assert "## Specifications" in result
        assert "| Spec | Status | Validation | Last Modified |" in result
        assert "|------|--------|------------|---------------|" in result
        assert "001-feature-a" in result
        assert "002-feature-b" in result

    def test_format_contains_summary(self, sample_report):
        """Test that output contains summary."""
        formatter = MarkdownFormatter()
        result = formatter.format(sample_report)

        assert "## Summary" in result
        assert "**Total Specs**: 2" in result
        assert "**Draft**: 1" in result
        assert "**Complete**: 1" in result
        assert "**Completion**:" in result

    def test_format_status_emojis(self, sample_report):
        """Test that status includes emojis."""
        formatter = MarkdownFormatter()
        result = formatter.format(sample_report)

        assert "📝" in result  # Draft emoji
        assert "✅" in result  # Complete emoji

    def test_format_blocking_indicator(self, report_with_validation):
        """Test that blocking specs show indicator."""
        formatter = MarkdownFormatter()
        result = formatter.format(report_with_validation)

        assert "⛔" in result  # Blocking indicator

    def test_format_verbose_includes_details(self, report_with_validation):
        """Test verbose mode includes validation details."""
        formatter = MarkdownFormatter()
        result = formatter.format(report_with_validation, verbose=True)

        assert "### Validation Details" in result
        assert "Missing requirements section" in result

    def test_format_empty_report(self):
        """Test formatting empty report."""
        formatter = MarkdownFormatter()
        report = StatusReport(
            specs=[],
            generated_at=datetime.now(),
            project_root=Path("/test"),
        )
        result = formatter.format(report)

        assert "*No specifications found.*" in result


class TestRichFormatter:
    """Tests for RichFormatter."""

    def test_format_returns_string(self, sample_report):
        """Test that format returns a string."""
        formatter = RichFormatter()
        result = formatter.format(sample_report)

        assert isinstance(result, str)

    def test_format_contains_spec_names(self, sample_report):
        """Test that output contains spec names."""
        formatter = RichFormatter()
        result = formatter.format(sample_report)

        assert "001-feature-a" in result
        assert "002-feature-b" in result

    def test_format_contains_status(self, sample_report):
        """Test that output contains status display."""
        formatter = RichFormatter()
        result = formatter.format(sample_report)

        assert "Draft" in result
        assert "Complete" in result

    def test_format_with_blocking(self, report_with_validation):
        """Test that blocking indicator appears."""
        formatter = RichFormatter()
        result = formatter.format(report_with_validation)

        # Should have blocking indicator (⛔) somewhere
        assert "blocking" in result.lower() or "⛔" in result

    def test_format_verbose_includes_details(self, report_with_validation):
        """Test verbose mode includes validation details."""
        formatter = RichFormatter()
        result = formatter.format(report_with_validation, verbose=True)

        # Should include validation error details (may be word-wrapped by Rich)
        # Check for key parts of the message that won't be split
        assert "requirements" in result.lower() or "Score:" in result
