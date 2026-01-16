"""Integration tests for the status command."""

import json
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture
def doit_project(tmp_path):
    """Create a minimal doit project structure."""
    # Create .doit directory
    (tmp_path / ".doit").mkdir()

    # Create specs directory with sample specs
    specs = {
        "001-draft-spec": "Draft",
        "002-in-progress-spec": "In Progress",
        "003-complete-spec": "Complete",
    }

    for name, status in specs.items():
        spec_dir = tmp_path / "specs" / name
        spec_dir.mkdir(parents=True)
        spec_content = f"""# Feature Specification: {name}

**Feature Branch**: `{name}`
**Created**: 2026-01-16
**Status**: {status}

## Requirements
- Requirement 1

## User Stories

### US1: Basic Feature
As a user, I want to use this feature so that I can accomplish my goals.

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


def run_status_command(cwd, *args):
    """Run the status command and return result."""
    cmd = [sys.executable, "-m", "doit_cli.main", "status", *args]
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    return result


class TestStatusCommandIntegration:
    """Integration tests for status command."""

    def test_status_with_specs(self, doit_project):
        """Test status command with specs present."""
        result = run_status_command(doit_project)

        # Command should succeed (exit 0 or 1)
        assert result.returncode in [0, 1]

        # Output should contain spec names
        assert "001-draft-spec" in result.stdout
        assert "002-in-progress-spec" in result.stdout
        assert "003-complete-spec" in result.stdout

    def test_status_empty_project(self, empty_doit_project):
        """Test status command with no specs."""
        result = run_status_command(empty_doit_project)

        # Command should succeed
        assert result.returncode == 0

        # Output should indicate no specs
        assert "No specifications found" in result.stdout

    def test_status_not_doit_project(self, non_doit_project):
        """Test status command in non-doit directory."""
        result = run_status_command(non_doit_project)

        # Command should fail with exit code 2
        assert result.returncode == 2

        # Output should indicate error
        assert "Not a doit project" in result.stdout or "Error" in result.stdout

    def test_status_format_json(self, doit_project):
        """Test status command with JSON output."""
        result = run_status_command(doit_project, "--format", "json")

        assert result.returncode in [0, 1]

        # Output should be valid JSON
        data = json.loads(result.stdout)
        assert "specs" in data
        assert "summary" in data
        assert len(data["specs"]) == 3

    def test_status_format_markdown(self, doit_project):
        """Test status command with markdown output."""
        result = run_status_command(doit_project, "--format", "markdown")

        assert result.returncode in [0, 1]

        # Output should contain markdown elements
        assert "# Spec Status Report" in result.stdout
        assert "| Spec | Status |" in result.stdout

    def test_status_filter_by_status(self, doit_project):
        """Test status command with status filter."""
        result = run_status_command(doit_project, "--status", "draft", "--format", "json")

        assert result.returncode in [0, 1]

        data = json.loads(result.stdout)
        assert len(data["specs"]) == 1
        assert data["specs"][0]["name"] == "001-draft-spec"

    def test_status_invalid_status_filter(self, doit_project):
        """Test status command with invalid status filter."""
        result = run_status_command(doit_project, "--status", "invalid")

        # Should fail with exit code 2
        assert result.returncode == 2
        assert "Invalid status" in result.stdout

    def test_status_invalid_format(self, doit_project):
        """Test status command with invalid format."""
        result = run_status_command(doit_project, "--format", "invalid")

        # Should fail with exit code 2
        assert result.returncode == 2
        assert "Invalid format" in result.stdout

    def test_status_output_to_file(self, doit_project, tmp_path):
        """Test status command with file output."""
        output_file = tmp_path / "report.json"
        result = run_status_command(
            doit_project, "--format", "json", "--output", str(output_file)
        )

        assert result.returncode in [0, 1]
        assert output_file.exists()

        # File should contain valid JSON
        data = json.loads(output_file.read_text())
        assert "specs" in data

    def test_status_verbose_mode(self, doit_project):
        """Test status command in verbose mode."""
        result = run_status_command(doit_project, "--verbose", "--format", "json")

        assert result.returncode in [0, 1]

        # With verbose, validation issues should be included
        data = json.loads(result.stdout)
        for spec in data["specs"]:
            if spec.get("validation"):
                assert "issues" in spec["validation"]


class TestStatusExitCodes:
    """Test exit codes are correct."""

    def test_exit_code_0_or_1_with_specs(self, doit_project):
        """Test exit code is 0 (no blockers) or 1 (blockers) with specs."""
        result = run_status_command(doit_project)

        # Exit code depends on validation results
        # 0 = no blocking, 1 = blocking specs exist
        assert result.returncode in [0, 1]

    def test_exit_code_0_empty_project(self, empty_doit_project):
        """Test exit code 0 when no specs (no blockers possible)."""
        result = run_status_command(empty_doit_project)

        # No specs means no blockers
        assert result.returncode == 0

    def test_exit_code_2_error(self, non_doit_project):
        """Test exit code 2 on error."""
        result = run_status_command(non_doit_project)

        assert result.returncode == 2
