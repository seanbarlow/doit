"""Integration tests for the analytics command."""

import json
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture
def doit_project_with_analytics(tmp_path):
    """Create a doit project with specs for analytics testing."""
    # Create .doit directory
    (tmp_path / ".doit").mkdir()
    (tmp_path / ".doit" / "reports").mkdir()

    # Create specs with varied statuses and dates for analytics
    specs = [
        ("001-complete-spec", "Complete", "2026-01-01"),
        ("002-complete-spec", "Complete", "2026-01-05"),
        ("003-complete-spec", "Complete", "2026-01-10"),
        ("004-in-progress-spec", "In Progress", "2026-01-12"),
        ("005-draft-spec", "Draft", "2026-01-15"),
    ]

    for name, status, created in specs:
        spec_dir = tmp_path / "specs" / name
        spec_dir.mkdir(parents=True)
        spec_content = f"""# Feature Specification: {name}

**Feature Branch**: `{name}`
**Created**: {created}
**Status**: {status}

## Requirements
- Requirement 1

## User Stories

### US1: Basic Feature
As a user, I want to use this feature.

#### Acceptance Criteria
- [ ] AC1: Feature works correctly
"""
        (spec_dir / "spec.md").write_text(spec_content)

    return tmp_path


@pytest.fixture
def empty_doit_project(tmp_path):
    """Create a doit project with no specs."""
    (tmp_path / ".doit").mkdir()
    (tmp_path / "specs").mkdir()
    return tmp_path


@pytest.fixture
def non_doit_project(tmp_path):
    """Create a directory without .doit."""
    return tmp_path


def run_analytics_command(cwd, *args):
    """Run the analytics command and return result."""
    cmd = [sys.executable, "-m", "doit_cli.main", "analytics", *args]
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    return result


class TestAnalyticsShowCommand:
    """Integration tests for analytics show command."""

    def test_show_with_specs(self, doit_project_with_analytics):
        """Test show command displays completion metrics."""
        result = run_analytics_command(doit_project_with_analytics, "show")

        assert result.returncode == 0
        # Should display summary metrics
        assert "Total Specs" in result.stdout or "total" in result.stdout.lower()

    def test_show_empty_project(self, empty_doit_project):
        """Test show command with no specs."""
        result = run_analytics_command(empty_doit_project, "show")

        # Returns 1 when no specs found (informational exit)
        assert result.returncode in [0, 1]
        # Should indicate no specs
        assert "No specifications found" in result.stdout or "0" in result.stdout

    def test_show_json_output(self, doit_project_with_analytics):
        """Test show command with JSON output."""
        result = run_analytics_command(doit_project_with_analytics, "show", "--json")

        assert result.returncode == 0
        # Output should be valid JSON with nested data structure
        response = json.loads(result.stdout)
        assert response.get("success") is True
        data = response.get("data", {})
        assert "total_specs" in data
        assert "by_status" in data
        assert "completion_pct" in data

    def test_show_not_doit_project(self, non_doit_project):
        """Test show command in non-doit directory."""
        result = run_analytics_command(non_doit_project, "show")

        # Should fail
        assert result.returncode != 0


class TestAnalyticsCyclesCommand:
    """Integration tests for analytics cycles command."""

    def test_cycles_with_completed_specs(self, doit_project_with_analytics):
        """Test cycles command shows cycle time statistics."""
        result = run_analytics_command(doit_project_with_analytics, "cycles")

        assert result.returncode == 0
        # Should display statistics or indicate need for data
        # The output depends on whether dates can be inferred
        assert result.stdout  # Should have some output

    def test_cycles_with_days_filter(self, doit_project_with_analytics):
        """Test cycles command with days filter."""
        result = run_analytics_command(
            doit_project_with_analytics, "cycles", "--days", "30"
        )

        assert result.returncode == 0

    def test_cycles_json_output(self, doit_project_with_analytics):
        """Test cycles command with JSON output."""
        result = run_analytics_command(doit_project_with_analytics, "cycles", "--json")

        assert result.returncode == 0
        # Output should be valid JSON
        data = json.loads(result.stdout)
        assert isinstance(data, dict)


class TestAnalyticsVelocityCommand:
    """Integration tests for analytics velocity command.

    Note: Without git history, completion dates are inferred as today,
    so velocity tests may show 'insufficient data' in test environments.
    This is expected behavior.
    """

    def test_velocity_command_runs(self, doit_project_with_analytics):
        """Test velocity command runs without error."""
        result = run_analytics_command(doit_project_with_analytics, "velocity")

        # Returns 0 on success, 1 on insufficient data (both valid)
        assert result.returncode in [0, 1]
        # Should have some output
        assert result.stdout

    def test_velocity_with_weeks_filter(self, doit_project_with_analytics):
        """Test velocity command with weeks filter."""
        result = run_analytics_command(
            doit_project_with_analytics, "velocity", "--weeks", "4"
        )

        # Returns 0 on success, 1 on insufficient data
        assert result.returncode in [0, 1]
        assert result.stdout

    def test_velocity_json_format(self, doit_project_with_analytics):
        """Test velocity command with JSON format."""
        result = run_analytics_command(
            doit_project_with_analytics, "velocity", "--format", "json"
        )

        # Returns 0 on success, 1 on insufficient data
        assert result.returncode in [0, 1]
        # Output should be valid JSON
        data = json.loads(result.stdout)
        # Either a list of velocity data or an error object
        assert isinstance(data, (list, dict))

    def test_velocity_csv_format(self, doit_project_with_analytics):
        """Test velocity command with CSV format."""
        result = run_analytics_command(
            doit_project_with_analytics, "velocity", "--format", "csv"
        )

        # Returns 0 on success, 1 on insufficient data
        assert result.returncode in [0, 1]
        assert result.stdout


class TestAnalyticsSpecCommand:
    """Integration tests for analytics spec command."""

    def test_spec_existing(self, doit_project_with_analytics):
        """Test spec command with existing spec."""
        result = run_analytics_command(
            doit_project_with_analytics, "spec", "001-complete-spec"
        )

        assert result.returncode == 0
        assert "001-complete-spec" in result.stdout

    def test_spec_not_found(self, doit_project_with_analytics):
        """Test spec command with non-existent spec."""
        result = run_analytics_command(
            doit_project_with_analytics, "spec", "999-nonexistent"
        )

        assert result.returncode == 1
        assert "not found" in result.stdout.lower() or "error" in result.stdout.lower()

    def test_spec_json_output(self, doit_project_with_analytics):
        """Test spec command with JSON output."""
        result = run_analytics_command(
            doit_project_with_analytics, "spec", "001-complete-spec", "--json"
        )

        assert result.returncode == 0
        response = json.loads(result.stdout)
        assert response.get("success") is True
        spec = response.get("spec", {})
        assert "name" in spec
        assert spec["name"] == "001-complete-spec"
        assert "status" in spec
        assert "created_at" in spec


class TestAnalyticsExportCommand:
    """Integration tests for analytics export command."""

    def test_export_markdown(self, doit_project_with_analytics):
        """Test export command creates markdown file."""
        result = run_analytics_command(
            doit_project_with_analytics, "export", "--format", "markdown"
        )

        assert result.returncode == 0
        # Should indicate file was created
        assert "Exported" in result.stdout or ".md" in result.stdout

        # Check file was created in .doit/reports/
        reports_dir = doit_project_with_analytics / ".doit" / "reports"
        md_files = list(reports_dir.glob("*.md"))
        assert len(md_files) >= 1

    def test_export_json(self, doit_project_with_analytics):
        """Test export command creates JSON file."""
        result = run_analytics_command(
            doit_project_with_analytics, "export", "--format", "json"
        )

        assert result.returncode == 0
        # Should indicate file was created
        assert "Exported" in result.stdout or ".json" in result.stdout

        # Check file was created in .doit/reports/
        reports_dir = doit_project_with_analytics / ".doit" / "reports"
        json_files = list(reports_dir.glob("*.json"))
        assert len(json_files) >= 1

    def test_export_custom_output(self, doit_project_with_analytics, tmp_path):
        """Test export command with custom output path."""
        output_file = tmp_path / "custom-report.md"
        result = run_analytics_command(
            doit_project_with_analytics,
            "export",
            "--format",
            "markdown",
            "--output",
            str(output_file),
        )

        assert result.returncode == 0
        assert output_file.exists()

        content = output_file.read_text()
        assert "Analytics Report" in content or "Spec" in content


class TestAnalyticsDefaultCommand:
    """Test default behavior when running analytics without subcommand."""

    def test_analytics_default_shows_help_or_summary(self, doit_project_with_analytics):
        """Test running just 'doit analytics' works."""
        result = run_analytics_command(doit_project_with_analytics)

        # Should either show help or default to show command
        assert result.returncode == 0


class TestAnalyticsExitCodes:
    """Test exit codes are correct."""

    def test_exit_code_0_success(self, doit_project_with_analytics):
        """Test exit code 0 on success."""
        result = run_analytics_command(doit_project_with_analytics, "show")
        assert result.returncode == 0

    def test_exit_code_1_not_found(self, doit_project_with_analytics):
        """Test exit code 1 when spec not found."""
        result = run_analytics_command(
            doit_project_with_analytics, "spec", "nonexistent"
        )
        assert result.returncode == 1

    def test_exit_code_2_error(self, non_doit_project):
        """Test exit code 2 on error (not a doit project)."""
        result = run_analytics_command(non_doit_project, "show")
        assert result.returncode == 2
