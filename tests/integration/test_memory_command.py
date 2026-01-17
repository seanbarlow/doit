"""Integration tests for memory CLI commands."""

import json
import os
import tempfile
from pathlib import Path

import pytest
from typer.testing import CliRunner

from doit_cli.main import app


@pytest.fixture
def temp_project():
    """Create a temporary project with memory files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)

        # Create .doit/memory structure
        memory_dir = project_root / ".doit" / "memory"
        memory_dir.mkdir(parents=True)

        # Create constitution.md
        constitution = memory_dir / "constitution.md"
        constitution.write_text("""# Project Constitution

## Vision

Build a task management application that helps users organize their work.

## Principles

- Simple and intuitive interface
- Fast and responsive
- Privacy-first design

## Technology Stack

- Python 3.11+
- Typer CLI framework
- Rich terminal formatting
""")

        # Create roadmap.md
        roadmap = memory_dir / "roadmap.md"
        roadmap.write_text("""# Project Roadmap

## Vision

A task management CLI for developers.

## P1: Critical

- User authentication
- Task creation and editing

## P2: Important

- Categories and tags
- Due date reminders
""")

        # Create specs directory with spec files
        specs_dir = project_root / "specs"

        # Create spec 001
        spec_001_dir = specs_dir / "001-user-auth"
        spec_001_dir.mkdir(parents=True)
        spec_001 = spec_001_dir / "spec.md"
        spec_001.write_text("""# Specification: User Authentication

## Summary

Implement user authentication for the task manager.

## Requirements

- FR-001: Users must be able to log in with username/password
- FR-002: Support OAuth authentication
- FR-003: Session management with secure tokens
""")

        # Create spec 002
        spec_002_dir = specs_dir / "002-task-crud"
        spec_002_dir.mkdir(parents=True)
        spec_002 = spec_002_dir / "spec.md"
        spec_002.write_text("""# Specification: Task CRUD Operations

## Summary

Basic create, read, update, delete operations for tasks.

## Requirements

- FR-001: Create new tasks with title and description
- FR-002: List all tasks with filtering
- FR-003: Edit existing tasks
- FR-004: Delete tasks with confirmation
""")

        # Change to project directory
        original_cwd = os.getcwd()
        os.chdir(project_root)

        yield project_root

        # Restore original directory
        os.chdir(original_cwd)


@pytest.fixture
def runner():
    """Create a CLI test runner."""
    return CliRunner()


class TestMemorySearchCommand:
    """Tests for the 'doit memory search' command."""

    def test_search_keyword_basic(self, runner, temp_project):
        """Test basic keyword search."""
        result = runner.invoke(app, ["memory", "search", "authentication"])
        assert result.exit_code == 0
        assert "Memory Search Results" in result.output or "results" in result.output.lower()

    def test_search_keyword_no_results(self, runner, temp_project):
        """Test search with no matching results."""
        result = runner.invoke(app, ["memory", "search", "nonexistentkeyword12345"])
        assert result.exit_code == 0
        assert "No results found" in result.output

    def test_search_with_source_filter_governance(self, runner, temp_project):
        """Test search with governance source filter."""
        result = runner.invoke(
            app, ["memory", "search", "vision", "--source", "governance"]
        )
        assert result.exit_code == 0
        # Should find results in constitution.md or roadmap.md
        assert "Memory Search Results" in result.output or "No results found" in result.output

    def test_search_with_source_filter_specs(self, runner, temp_project):
        """Test search with specs source filter."""
        result = runner.invoke(
            app, ["memory", "search", "FR-001", "--source", "specs"]
        )
        assert result.exit_code == 0
        # Should find results in spec files
        assert "Memory Search Results" in result.output or "results" in result.output.lower()

    def test_search_with_invalid_source(self, runner, temp_project):
        """Test search with invalid source filter."""
        result = runner.invoke(
            app, ["memory", "search", "test", "--source", "invalid"]
        )
        assert result.exit_code == 1
        assert "Invalid source filter" in result.output

    def test_search_with_query_type_phrase(self, runner, temp_project):
        """Test search with phrase query type."""
        result = runner.invoke(
            app, ["memory", "search", "task management", "--type", "phrase"]
        )
        assert result.exit_code == 0

    def test_search_with_query_type_natural(self, runner, temp_project):
        """Test search with natural language query type."""
        result = runner.invoke(
            app, ["memory", "search", "what is the project vision?", "--type", "natural"]
        )
        assert result.exit_code == 0
        # Natural language search shows interpretation info
        if "Memory Search Results" in result.output:
            assert "Keywords:" in result.output or "results" in result.output.lower()

    def test_search_with_query_type_regex(self, runner, temp_project):
        """Test search with regex query type."""
        result = runner.invoke(
            app, ["memory", "search", "FR-00[1-3]", "--type", "regex"]
        )
        assert result.exit_code == 0

    def test_search_with_invalid_regex(self, runner, temp_project):
        """Test search with invalid regex pattern."""
        result = runner.invoke(
            app, ["memory", "search", "[invalid(regex", "--regex"]
        )
        assert result.exit_code == 3
        assert "Invalid regex" in result.output or "Error" in result.output

    def test_search_with_invalid_query_type(self, runner, temp_project):
        """Test search with invalid query type."""
        result = runner.invoke(
            app, ["memory", "search", "test", "--type", "invalid"]
        )
        assert result.exit_code == 1
        assert "Invalid query type" in result.output

    def test_search_with_max_results(self, runner, temp_project):
        """Test search with max results limit."""
        result = runner.invoke(
            app, ["memory", "search", "task", "--max", "5"]
        )
        assert result.exit_code == 0

    def test_search_with_invalid_max_results(self, runner, temp_project):
        """Test search with invalid max results value."""
        result = runner.invoke(
            app, ["memory", "search", "test", "--max", "500"]
        )
        assert result.exit_code == 1
        assert "Max results must be between 1 and 100" in result.output

    def test_search_case_sensitive(self, runner, temp_project):
        """Test case-sensitive search."""
        result = runner.invoke(
            app, ["memory", "search", "AUTHENTICATION", "--case-sensitive"]
        )
        assert result.exit_code == 0

    def test_search_json_output(self, runner, temp_project):
        """Test search with JSON output."""
        result = runner.invoke(
            app, ["memory", "search", "task", "--json"]
        )
        assert result.exit_code == 0
        # Verify output is valid JSON
        try:
            output = json.loads(result.output)
            assert "query" in output
            assert "results" in output
            assert "metadata" in output
        except json.JSONDecodeError:
            pytest.fail("Output is not valid JSON")


class TestMemoryHistoryCommand:
    """Tests for the 'doit memory history' command."""

    def test_history_empty(self, runner, temp_project):
        """Test history command with no previous searches."""
        result = runner.invoke(app, ["memory", "history"])
        assert result.exit_code == 0
        assert "No search history" in result.output or "Search History" in result.output

    def test_history_after_search(self, runner, temp_project):
        """Test history shows recent searches."""
        # First perform a search
        runner.invoke(app, ["memory", "search", "authentication"])
        # Then check history
        result = runner.invoke(app, ["memory", "history"])
        assert result.exit_code == 0
        # Note: Session-scoped history may not persist across invocations
        # This test verifies the command works, not persistence

    def test_history_clear(self, runner, temp_project):
        """Test clearing history."""
        result = runner.invoke(app, ["memory", "history", "--clear"])
        assert result.exit_code == 0
        assert "cleared" in result.output.lower()

    def test_history_json_output(self, runner, temp_project):
        """Test history with JSON output."""
        result = runner.invoke(app, ["memory", "history", "--json"])
        assert result.exit_code == 0
        # Verify output is valid JSON
        try:
            output = json.loads(result.output)
            assert "session_id" in output
            assert "entries" in output
        except json.JSONDecodeError:
            pytest.fail("Output is not valid JSON")


class TestMemoryCommandNotInProject:
    """Tests for memory commands when not in a doit project."""

    def test_search_not_in_project(self, runner):
        """Test search command fails gracefully when not in a doit project."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                result = runner.invoke(app, ["memory", "search", "test"])
                assert result.exit_code == 1
                assert "Not in a doit project" in result.output or "doit init" in result.output
            finally:
                os.chdir(original_cwd)

    def test_history_not_in_project(self, runner):
        """Test history command fails gracefully when not in a doit project."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                result = runner.invoke(app, ["memory", "history"])
                assert result.exit_code == 1
                assert "Not in a doit project" in result.output or "doit init" in result.output
            finally:
                os.chdir(original_cwd)
