"""Integration tests for validate command."""

import json
import pytest
from pathlib import Path
from typer.testing import CliRunner

from doit_cli.main import app


runner = CliRunner()


@pytest.fixture
def valid_spec_dir(temp_dir):
    """Create a directory with a valid spec file."""
    spec_dir = temp_dir / "specs" / "001-test-feature"
    spec_dir.mkdir(parents=True)

    spec_content = """# Feature: Test Feature

**Status**: Approved
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
def invalid_spec_dir(temp_dir):
    """Create a directory with an invalid spec file."""
    spec_dir = temp_dir / "specs" / "002-invalid-feature"
    spec_dir.mkdir(parents=True)

    spec_content = """# Feature: Invalid Feature

**Status**: Approved
**Feature Branch**: `invalid-format`

## Overview

Missing required sections.

TODO: Complete this spec
[NEEDS CLARIFICATION] What should this do?
"""

    (spec_dir / "spec.md").write_text(spec_content)
    return temp_dir


@pytest.fixture
def mixed_specs_dir(temp_dir, valid_spec_dir, invalid_spec_dir):
    """Create a directory with both valid and invalid specs."""
    return temp_dir


class TestValidateCommand:
    """Tests for validate command."""

    def test_validate_valid_spec_file(self, valid_spec_dir):
        """Test validating a valid spec file."""
        spec_file = valid_spec_dir / "specs" / "001-test-feature" / "spec.md"

        result = runner.invoke(app, ["validate", str(spec_file)])

        assert result.exit_code == 0
        assert "Quality Score" in result.output

    def test_validate_valid_spec_directory(self, valid_spec_dir):
        """Test validating a valid spec directory."""
        spec_dir = valid_spec_dir / "specs" / "001-test-feature"

        result = runner.invoke(app, ["validate", str(spec_dir)])

        assert result.exit_code == 0
        assert "Quality Score" in result.output

    def test_validate_invalid_spec_file(self, invalid_spec_dir):
        """Test validating an invalid spec file."""
        spec_file = invalid_spec_dir / "specs" / "002-invalid-feature" / "spec.md"

        result = runner.invoke(app, ["validate", str(spec_file)])

        # Should exit with error code due to errors
        assert result.exit_code == 1
        # Should show errors
        assert "ERRORS" in result.output or "error" in result.output.lower()

    def test_validate_all_specs(self, valid_spec_dir, monkeypatch):
        """Test validating all specs in a directory."""
        monkeypatch.chdir(valid_spec_dir)

        result = runner.invoke(app, ["validate", "--all"])

        assert "Spec Validation Summary" in result.output or "Quality Score" in result.output

    def test_validate_json_output(self, valid_spec_dir):
        """Test JSON output format."""
        spec_file = valid_spec_dir / "specs" / "001-test-feature" / "spec.md"

        result = runner.invoke(app, ["validate", str(spec_file), "--json"])

        # Should be valid JSON
        output = json.loads(result.output)
        assert "spec_path" in output
        assert "status" in output
        assert "quality_score" in output

    def test_validate_json_output_all(self, valid_spec_dir, monkeypatch):
        """Test JSON output format for all specs."""
        monkeypatch.chdir(valid_spec_dir)

        result = runner.invoke(app, ["validate", "--all", "--json"])

        # Should be valid JSON with summary
        output = json.loads(result.output)
        assert "summary" in output
        assert "results" in output

    def test_validate_verbose_output(self, valid_spec_dir, monkeypatch):
        """Test verbose output mode."""
        monkeypatch.chdir(valid_spec_dir)

        result = runner.invoke(app, ["validate", "--all", "--verbose"])

        assert result.exit_code == 0

    def test_validate_nonexistent_path(self, temp_dir):
        """Test validating nonexistent path."""
        result = runner.invoke(app, ["validate", str(temp_dir / "nonexistent")])

        assert result.exit_code == 1
        assert "not found" in result.output.lower() or "Error" in result.output

    def test_validate_non_markdown_file(self, temp_dir):
        """Test validating non-markdown file."""
        txt_file = temp_dir / "test.txt"
        txt_file.write_text("Not a markdown file")

        result = runner.invoke(app, ["validate", str(txt_file)])

        assert result.exit_code == 1
        assert "markdown" in result.output.lower() or "Error" in result.output

    def test_validate_empty_specs_directory(self, temp_dir, monkeypatch):
        """Test validating empty specs directory."""
        monkeypatch.chdir(temp_dir)

        result = runner.invoke(app, ["validate", "--all"])

        assert result.exit_code == 1
        assert "No spec files found" in result.output


class TestValidateCommandScoring:
    """Tests for validate command scoring behavior."""

    def test_valid_spec_high_score(self, valid_spec_dir):
        """Test that valid spec gets high quality score."""
        spec_file = valid_spec_dir / "specs" / "001-test-feature" / "spec.md"

        result = runner.invoke(app, ["validate", str(spec_file), "--json"])

        output = json.loads(result.output)
        assert output["quality_score"] >= 70

    def test_invalid_spec_low_score(self, invalid_spec_dir):
        """Test that invalid spec gets lower quality score due to issues."""
        spec_file = invalid_spec_dir / "specs" / "002-invalid-feature" / "spec.md"

        result = runner.invoke(app, ["validate", str(spec_file), "--json"])

        output = json.loads(result.output)
        # Invalid spec should have score < 100 due to missing sections
        assert output["quality_score"] < 100
        # Should have errors detected
        assert output["error_count"] >= 2

    def test_status_pass_for_valid(self, valid_spec_dir):
        """Test PASS status for valid spec."""
        spec_file = valid_spec_dir / "specs" / "001-test-feature" / "spec.md"

        result = runner.invoke(app, ["validate", str(spec_file), "--json"])

        output = json.loads(result.output)
        assert output["status"] == "pass"

    def test_status_fail_for_invalid(self, invalid_spec_dir):
        """Test FAIL status for invalid spec."""
        spec_file = invalid_spec_dir / "specs" / "002-invalid-feature" / "spec.md"

        result = runner.invoke(app, ["validate", str(spec_file), "--json"])

        output = json.loads(result.output)
        assert output["status"] == "fail"
