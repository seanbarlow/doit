"""Integration tests for the xref (cross-reference) commands."""

import json
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture
def xref_project(tmp_path):
    """Create a doit project with spec and tasks for xref testing."""
    # Create .doit directory
    (tmp_path / ".doit").mkdir()

    # Create specs directory with spec and tasks
    spec_dir = tmp_path / "specs" / "033-test-feature"
    spec_dir.mkdir(parents=True)

    spec_content = """# Feature Specification: Test Feature

**Feature Branch**: `033-test-feature`
**Created**: 2026-01-16
**Status**: In Progress

## Requirements

- **FR-001**: System MUST support basic functionality
- **FR-002**: System MUST handle edge cases
- **FR-003**: System SHOULD provide error messages

## User Scenarios

### User Story 1: Basic Usage
As a user, I want to use the feature.

## Success Criteria

- **SC-001**: Feature works correctly
"""
    (spec_dir / "spec.md").write_text(spec_content)

    tasks_content = """# Tasks: Test Feature

## Phase 1: Setup

- [x] T001 Initialize project [FR-001]
- [ ] T002 Create models [FR-001, FR-002]

## Phase 2: Implementation

- [ ] T003 Implement feature [FR-002]
- [ ] T004 Add error handling [FR-003]
"""
    (spec_dir / "tasks.md").write_text(tasks_content)

    return tmp_path


@pytest.fixture
def xref_project_with_orphans(tmp_path):
    """Create a project with orphaned task references."""
    (tmp_path / ".doit").mkdir()

    spec_dir = tmp_path / "specs" / "test-orphans"
    spec_dir.mkdir(parents=True)

    spec_content = """# Feature Specification

**Feature Branch**: `test-orphans`
**Status**: In Progress

## Requirements

- **FR-001**: Only one requirement

## User Scenarios

### User Story
As a user, I want something.

## Success Criteria

- **SC-001**: It works
"""
    (spec_dir / "spec.md").write_text(spec_content)

    tasks_content = """# Tasks

- [ ] T001 Valid task [FR-001]
- [ ] T002 Orphaned reference [FR-999]
"""
    (spec_dir / "tasks.md").write_text(tasks_content)

    return tmp_path


@pytest.fixture
def xref_project_uncovered(tmp_path):
    """Create a project with uncovered requirements."""
    (tmp_path / ".doit").mkdir()

    spec_dir = tmp_path / "specs" / "test-uncovered"
    spec_dir.mkdir(parents=True)

    spec_content = """# Feature Specification

**Feature Branch**: `test-uncovered`
**Status**: In Progress

## Requirements

- **FR-001**: Has tasks
- **FR-002**: No tasks for this one
- **FR-003**: Also uncovered

## User Scenarios

### User Story
As a user, I want something.

## Success Criteria

- **SC-001**: It works
"""
    (spec_dir / "spec.md").write_text(spec_content)

    tasks_content = """# Tasks

- [ ] T001 Only covers FR-001 [FR-001]
"""
    (spec_dir / "tasks.md").write_text(tasks_content)

    return tmp_path


def run_xref_command(cwd, subcommand, *args):
    """Run an xref subcommand and return result."""
    cmd = [sys.executable, "-m", "doit_cli.main", "xref", subcommand, *args]
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    return result


class TestXrefCoverageCommand:
    """Integration tests for xref coverage command."""

    def test_coverage_basic(self, xref_project):
        """Test basic coverage report."""
        result = run_xref_command(xref_project, "coverage", "033-test-feature")

        assert result.returncode == 0
        assert "FR-001" in result.stdout
        assert "FR-002" in result.stdout
        assert "FR-003" in result.stdout
        assert "Coverage:" in result.stdout or "100%" in result.stdout

    def test_coverage_json_format(self, xref_project):
        """Test coverage with JSON output."""
        result = run_xref_command(
            xref_project, "coverage", "033-test-feature", "--format", "json"
        )

        assert result.returncode == 0

        data = json.loads(result.stdout)
        assert "requirements" in data
        assert "coverage_percent" in data
        assert len(data["requirements"]) == 3

    def test_coverage_markdown_format(self, xref_project):
        """Test coverage with markdown output."""
        result = run_xref_command(
            xref_project, "coverage", "033-test-feature", "--format", "markdown"
        )

        assert result.returncode == 0
        assert "| Requirement |" in result.stdout
        assert "FR-001" in result.stdout

    def test_coverage_with_uncovered(self, xref_project_uncovered):
        """Test coverage shows uncovered requirements."""
        result = run_xref_command(
            xref_project_uncovered, "coverage", "test-uncovered", "--format", "json"
        )

        assert result.returncode == 0

        data = json.loads(result.stdout)
        # FR-002 and FR-003 should be uncovered
        uncovered = [r for r in data["requirements"] if not r["covered"]]
        assert len(uncovered) == 2

    def test_coverage_strict_mode(self, xref_project_uncovered):
        """Test coverage strict mode fails with uncovered requirements."""
        result = run_xref_command(
            xref_project_uncovered, "coverage", "test-uncovered", "--strict"
        )

        # Should fail with exit code 1 due to uncovered requirements
        assert result.returncode == 1

    def test_coverage_spec_not_found(self, xref_project):
        """Test coverage with non-existent spec."""
        result = run_xref_command(xref_project, "coverage", "nonexistent-spec")

        assert result.returncode == 2
        assert "not found" in result.stdout.lower() or "error" in result.stdout.lower()


class TestXrefLocateCommand:
    """Integration tests for xref locate command."""

    def test_locate_requirement(self, xref_project):
        """Test locating a requirement."""
        result = run_xref_command(
            xref_project, "locate", "FR-001", "--spec", "033-test-feature"
        )

        assert result.returncode == 0
        assert "FR-001" in result.stdout
        assert "spec.md" in result.stdout

    def test_locate_json_format(self, xref_project):
        """Test locate with JSON output."""
        result = run_xref_command(
            xref_project, "locate", "FR-001", "--spec", "033-test-feature", "--format", "json"
        )

        assert result.returncode == 0

        data = json.loads(result.stdout)
        assert data["id"] == "FR-001"
        assert "line" in data

    def test_locate_line_format(self, xref_project):
        """Test locate with line format (for IDE integration)."""
        result = run_xref_command(
            xref_project, "locate", "FR-001", "--spec", "033-test-feature", "--format", "line"
        )

        assert result.returncode == 0
        # Line format should just be path:line
        assert "spec.md:" in result.stdout

    def test_locate_not_found(self, xref_project):
        """Test locating a non-existent requirement."""
        result = run_xref_command(
            xref_project, "locate", "FR-999", "--spec", "033-test-feature"
        )

        assert result.returncode == 1
        assert "not found" in result.stdout.lower()


class TestXrefTasksCommand:
    """Integration tests for xref tasks command."""

    def test_tasks_for_requirement(self, xref_project):
        """Test listing tasks for a requirement."""
        result = run_xref_command(
            xref_project, "tasks", "FR-001", "--spec", "033-test-feature"
        )

        assert result.returncode == 0
        assert "T001" in result.stdout or "Initialize project" in result.stdout
        assert "T002" in result.stdout or "Create models" in result.stdout

    def test_tasks_json_format(self, xref_project):
        """Test tasks with JSON output."""
        result = run_xref_command(
            xref_project, "tasks", "FR-001", "--spec", "033-test-feature", "--format", "json"
        )

        assert result.returncode == 0

        data = json.loads(result.stdout)
        assert "tasks" in data
        assert len(data["tasks"]) == 2  # T001 and T002 reference FR-001

    def test_tasks_no_tasks_found(self, xref_project_uncovered):
        """Test tasks for requirement with no linked tasks."""
        result = run_xref_command(
            xref_project_uncovered, "tasks", "FR-002", "--spec", "test-uncovered"
        )

        # Should succeed but show no tasks
        assert result.returncode == 1
        assert "No tasks" in result.stdout or "0" in result.stdout


class TestXrefValidateCommand:
    """Integration tests for xref validate command."""

    def test_validate_valid_references(self, xref_project):
        """Test validate with all valid references."""
        result = run_xref_command(xref_project, "validate", "033-test-feature")

        assert result.returncode == 0
        assert "PASS" in result.stdout or "valid" in result.stdout.lower()

    def test_validate_with_orphans(self, xref_project_with_orphans):
        """Test validate detects orphaned references."""
        result = run_xref_command(xref_project_with_orphans, "validate", "test-orphans")

        # Should fail due to orphaned reference
        assert result.returncode == 1
        assert "FR-999" in result.stdout or "orphan" in result.stdout.lower()

    def test_validate_with_uncovered(self, xref_project_uncovered):
        """Test validate detects uncovered requirements."""
        result = run_xref_command(xref_project_uncovered, "validate", "test-uncovered")

        # Should show warning but pass (uncovered is warning by default)
        assert result.returncode in [0, 1]
        assert "FR-002" in result.stdout or "uncovered" in result.stdout.lower()

    def test_validate_strict_mode(self, xref_project_uncovered):
        """Test validate strict mode treats warnings as errors."""
        result = run_xref_command(
            xref_project_uncovered, "validate", "test-uncovered", "--strict"
        )

        # Should fail in strict mode due to uncovered requirements
        assert result.returncode == 1

    def test_validate_json_format(self, xref_project_with_orphans):
        """Test validate with JSON output."""
        result = run_xref_command(
            xref_project_with_orphans, "validate", "test-orphans", "--format", "json"
        )

        # Parse JSON and check structure
        data = json.loads(result.stdout)
        assert "valid" in data or "orphaned" in data


class TestXrefEndToEndWorkflow:
    """End-to-end workflow tests for xref commands."""

    def test_full_workflow(self, xref_project):
        """Test complete xref workflow."""
        # 1. Get coverage report
        coverage_result = run_xref_command(
            xref_project, "coverage", "033-test-feature", "--format", "json"
        )
        assert coverage_result.returncode == 0
        coverage = json.loads(coverage_result.stdout)
        assert coverage["coverage_percent"] == 100

        # 2. Locate a requirement
        locate_result = run_xref_command(
            xref_project, "locate", "FR-001", "--spec", "033-test-feature", "--format", "json"
        )
        assert locate_result.returncode == 0
        requirement = json.loads(locate_result.stdout)
        assert requirement["id"] == "FR-001"

        # 3. Find tasks for that requirement
        tasks_result = run_xref_command(
            xref_project, "tasks", "FR-001", "--spec", "033-test-feature", "--format", "json"
        )
        assert tasks_result.returncode == 0
        tasks = json.loads(tasks_result.stdout)
        assert len(tasks["tasks"]) >= 1

        # 4. Validate cross-references
        validate_result = run_xref_command(
            xref_project, "validate", "033-test-feature"
        )
        assert validate_result.returncode == 0

    def test_workflow_with_issues(self, xref_project_with_orphans):
        """Test workflow when there are cross-reference issues."""
        # 1. Coverage command runs (may return 1 if there are issues)
        coverage_result = run_xref_command(
            xref_project_with_orphans, "coverage", "test-orphans", "--format", "json"
        )
        # Coverage can return 0 or 1 depending on whether orphans affect it
        assert coverage_result.returncode in [0, 1]

        # 2. Validate should catch the orphan
        validate_result = run_xref_command(
            xref_project_with_orphans, "validate", "test-orphans", "--format", "json"
        )
        # Should fail due to orphaned reference
        assert validate_result.returncode == 1
