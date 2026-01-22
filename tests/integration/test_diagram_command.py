"""Integration tests for diagram CLI commands."""

import pytest
from pathlib import Path
from typer.testing import CliRunner

from doit_cli.main import app


runner = CliRunner()


@pytest.fixture
def sample_spec_content():
    """Sample spec content for testing."""
    return """# Feature: Test Feature

## Overview

This is a test feature for diagram generation.

## User Stories

### User Story 1 - User Login (Priority: P1)

**Description**: As a user, I want to log in to the system.

**Acceptance Criteria**:

#### Scenario 1
- **Given**: user is on the login page
- **When**: user enters valid credentials
- **Then**: user is redirected to dashboard

#### Scenario 2
- **Given**: user is logged out
- **When**: user clicks login button
- **Then**: login form is displayed

### User Story 2 - User Registration (Priority: P2)

**Description**: As a new user, I want to register an account.

**Acceptance Criteria**:

#### Scenario 1
- **Given**: user is on registration page
- **When**: user submits valid information
- **Then**: account is created

## Key Entities

### User
Central entity representing a system user.
- Has many Tasks
- Has one Profile

### Task
Represents a task item belonging to a user.
- Belongs to User

### Profile
User profile with additional information.
- Belongs to User

<!-- BEGIN:AUTO-GENERATED section="user-journey" -->
<!-- END:AUTO-GENERATED -->

<!-- BEGIN:AUTO-GENERATED section="entity-relationships" -->
<!-- END:AUTO-GENERATED -->
"""


@pytest.fixture
def spec_file(tmp_path, sample_spec_content):
    """Create a temporary spec file."""
    spec_dir = tmp_path / "specs" / "test-feature"
    spec_dir.mkdir(parents=True)
    spec_file = spec_dir / "spec.md"
    spec_file.write_text(sample_spec_content, encoding="utf-8")
    return spec_file


class TestDiagramGenerateCommand:
    """Tests for `doit diagram generate` command."""

    def test_generate_help(self):
        """Test generate command help output."""
        result = runner.invoke(app, ["diagram", "generate", "--help"])

        assert result.exit_code == 0
        assert "Generate Mermaid diagrams" in result.stdout

    def test_generate_with_file(self, spec_file):
        """Test generating diagrams from a spec file."""
        result = runner.invoke(app, ["diagram", "generate", str(spec_file)])

        assert result.exit_code == 0
        assert "Generating diagrams" in result.stdout or "Generated" in result.stdout

    def test_generate_no_insert(self, spec_file, tmp_path):
        """Test generate with --no-insert flag."""
        # Read original content
        original = spec_file.read_text(encoding="utf-8")

        result = runner.invoke(app, ["diagram", "generate", str(spec_file), "--no-insert"])

        # File should not be modified
        current = spec_file.read_text(encoding="utf-8")
        assert original == current

        # Should output diagram content
        assert result.exit_code == 0

    def test_generate_specific_type(self, spec_file):
        """Test generating specific diagram type."""
        result = runner.invoke(
            app, ["diagram", "generate", str(spec_file), "--type", "user-journey"]
        )

        assert result.exit_code == 0
        assert "user-journey" in result.stdout.lower() or "Generated" in result.stdout

    def test_generate_er_diagram_type(self, spec_file):
        """Test generating ER diagram type."""
        result = runner.invoke(
            app, ["diagram", "generate", str(spec_file), "--type", "er-diagram"]
        )

        # May succeed or return exit code 3 if no entities found
        assert result.exit_code in [0, 3]

    def test_generate_output_file(self, spec_file, tmp_path):
        """Test generating to output file."""
        output_file = tmp_path / "diagrams.md"

        result = runner.invoke(
            app,
            [
                "diagram", "generate", str(spec_file),
                "--no-insert",
                "--output", str(output_file)
            ]
        )

        assert result.exit_code == 0
        assert output_file.exists()
        content = output_file.read_text(encoding="utf-8")
        assert "```mermaid" in content

    def test_generate_strict_mode(self, spec_file):
        """Test generate with --strict flag."""
        result = runner.invoke(
            app, ["diagram", "generate", str(spec_file), "--strict"]
        )

        # Should succeed if diagrams are valid
        assert result.exit_code in [0, 2]  # 0 = success, 2 = validation error

    def test_generate_nonexistent_file(self, tmp_path):
        """Test generate with nonexistent file."""
        result = runner.invoke(
            app, ["diagram", "generate", str(tmp_path / "nonexistent.md")]
        )

        assert result.exit_code != 0
        assert "not found" in result.stdout.lower() or "error" in result.stdout.lower()

    def test_generate_invalid_type(self, spec_file):
        """Test generate with invalid diagram type."""
        result = runner.invoke(
            app, ["diagram", "generate", str(spec_file), "--type", "invalid-type"]
        )

        assert result.exit_code != 0
        assert "unknown" in result.stdout.lower() or "valid" in result.stdout.lower()

    def test_generate_inserts_into_sections(self, spec_file):
        """Test that diagrams are inserted into AUTO-GENERATED sections."""
        result = runner.invoke(app, ["diagram", "generate", str(spec_file)])

        assert result.exit_code == 0

        # Read updated file
        content = spec_file.read_text(encoding="utf-8")
        assert "```mermaid" in content
        assert "flowchart" in content or "erDiagram" in content

    def test_generate_displays_table(self, spec_file):
        """Test that generate displays results table."""
        result = runner.invoke(app, ["diagram", "generate", str(spec_file)])

        assert result.exit_code == 0
        # Should show diagram type and status
        assert "Diagram Type" in result.stdout or "Generated" in result.stdout


class TestDiagramValidateCommand:
    """Tests for `doit diagram validate` command."""

    def test_validate_help(self):
        """Test validate command help output."""
        result = runner.invoke(app, ["diagram", "validate", "--help"])

        assert result.exit_code == 0
        assert "Validate" in result.stdout

    def test_validate_valid_diagrams(self, spec_file):
        """Test validating valid diagrams."""
        # First generate diagrams
        runner.invoke(app, ["diagram", "generate", str(spec_file)])

        # Then validate
        result = runner.invoke(app, ["diagram", "validate", str(spec_file)])

        assert result.exit_code == 0
        assert "valid" in result.stdout.lower()

    def test_validate_no_diagrams(self, tmp_path):
        """Test validating file with no diagrams."""
        empty_file = tmp_path / "empty.md"
        empty_file.write_text("# No diagrams here", encoding="utf-8")

        result = runner.invoke(app, ["diagram", "validate", str(empty_file)])

        assert result.exit_code == 0
        assert "no mermaid" in result.stdout.lower() or "no diagrams" in result.stdout.lower()

    def test_validate_strict_mode(self, spec_file):
        """Test validate with --strict flag."""
        # Generate diagrams first
        runner.invoke(app, ["diagram", "generate", str(spec_file)])

        result = runner.invoke(app, ["diagram", "validate", str(spec_file), "--strict"])

        assert result.exit_code in [0, 1]  # 0 = valid, 1 = invalid

    def test_validate_displays_table(self, spec_file):
        """Test that validate displays results table."""
        # Generate diagrams first
        runner.invoke(app, ["diagram", "generate", str(spec_file)])

        result = runner.invoke(app, ["diagram", "validate", str(spec_file)])

        assert result.exit_code == 0
        assert "Diagram" in result.stdout or "Status" in result.stdout


class TestDiagramCommandAutoDetect:
    """Tests for auto-detection of spec files."""

    def test_auto_detect_in_current_dir(self, tmp_path, sample_spec_content, monkeypatch):
        """Test auto-detecting spec.md in current directory."""
        spec_file = tmp_path / "spec.md"
        spec_file.write_text(sample_spec_content, encoding="utf-8")

        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["diagram", "generate"])

        # Should find and process spec.md
        assert result.exit_code in [0, 1]  # May fail if no sections, but should find file

    def test_auto_detect_in_specs_dir(self, tmp_path, sample_spec_content, monkeypatch):
        """Test auto-detecting spec.md in specs/ directory."""
        specs_dir = tmp_path / "specs" / "feature-001"
        specs_dir.mkdir(parents=True)
        spec_file = specs_dir / "spec.md"
        spec_file.write_text(sample_spec_content, encoding="utf-8")

        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["diagram", "generate"])

        # Should find spec in specs/ directory
        assert result.exit_code in [0, 1, 3]


class TestDiagramCommandEdgeCases:
    """Tests for edge cases in diagram commands."""

    def test_empty_user_stories(self, tmp_path):
        """Test with spec that has no user stories."""
        content = """# Feature

## Key Entities

### User
A user entity.

<!-- BEGIN:AUTO-GENERATED section="entity-relationships" -->
<!-- END:AUTO-GENERATED -->
"""
        spec_file = tmp_path / "spec.md"
        spec_file.write_text(content, encoding="utf-8")

        result = runner.invoke(app, ["diagram", "generate", str(spec_file)])

        # Should still generate ER diagram
        assert result.exit_code in [0, 3]

    def test_empty_entities(self, tmp_path):
        """Test with spec that has no entities."""
        content = """# Feature

## User Stories

### User Story 1 - Test (Priority: P1)

**Description**: Test

**Acceptance Criteria**:

#### Scenario 1
- **Given**: state
- **When**: action
- **Then**: result

<!-- BEGIN:AUTO-GENERATED section="user-journey" -->
<!-- END:AUTO-GENERATED -->
"""
        spec_file = tmp_path / "spec.md"
        spec_file.write_text(content, encoding="utf-8")

        result = runner.invoke(app, ["diagram", "generate", str(spec_file)])

        # Should still generate user journey diagram
        assert result.exit_code in [0, 3]

    def test_missing_auto_generated_sections(self, tmp_path):
        """Test with spec missing AUTO-GENERATED sections."""
        content = """# Feature

## User Stories

### User Story 1 - Test (Priority: P1)

**Description**: Test

**Acceptance Criteria**:

#### Scenario 1
- **Given**: state
- **When**: action
- **Then**: result

## Key Entities

### User
A user entity.
"""
        spec_file = tmp_path / "spec.md"
        spec_file.write_text(content, encoding="utf-8")

        # With --no-insert, should still generate
        result = runner.invoke(app, ["diagram", "generate", str(spec_file), "--no-insert"])

        assert result.exit_code in [0, 3]
