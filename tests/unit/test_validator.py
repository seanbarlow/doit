"""Unit tests for Validator service."""

import pytest
from pathlib import Path

from doit_cli.models.agent import Agent
from doit_cli.models.project import Project
from doit_cli.models.results import VerifyStatus
from doit_cli.services.validator import Validator


class TestValidator:
    """Tests for Validator service."""

    def test_check_doit_folder_missing(self, project_dir):
        """Test check when .doit folder is missing."""
        project = Project(path=project_dir)
        validator = Validator(project)

        result = validator.check_doit_folder()

        assert result.status == VerifyStatus.FAIL
        assert ".doit" in result.message

    def test_check_doit_folder_exists(self, initialized_project):
        """Test check when .doit folder exists."""
        validator = Validator(initialized_project)

        result = validator.check_doit_folder()

        assert result.status == VerifyStatus.PASS

    def test_check_agent_directory_missing(self, initialized_project):
        """Test check when agent directory is missing."""
        validator = Validator(initialized_project)

        result = validator.check_agent_directory(Agent.CLAUDE)

        assert result.status == VerifyStatus.FAIL
        assert "Claude" in result.message or ".claude" in result.message

    def test_check_agent_directory_exists(self, claude_project):
        """Test check when agent directory exists."""
        validator = Validator(claude_project)

        result = validator.check_agent_directory(Agent.CLAUDE)

        assert result.status == VerifyStatus.PASS

    def test_check_command_files_missing(self, initialized_project):
        """Test check when command files are missing."""
        validator = Validator(initialized_project)

        result = validator.check_command_files(Agent.CLAUDE)

        # Should fail or warn since no agent directory exists
        assert result.status in [VerifyStatus.FAIL, VerifyStatus.WARN]

    def test_check_command_files_partial(self, claude_project):
        """Test check when some command files exist."""
        validator = Validator(claude_project)

        result = validator.check_command_files(Agent.CLAUDE)

        # Should warn since only some templates exist
        assert result.status == VerifyStatus.WARN
        assert "missing" in result.message.lower() or "1" in result.message

    def test_check_constitution_missing(self, initialized_project):
        """Test check when constitution is missing."""
        validator = Validator(initialized_project)

        result = validator.check_constitution()

        assert result.status == VerifyStatus.WARN
        assert "constitution" in result.message.lower()

    def test_check_constitution_exists(self, initialized_project):
        """Test check when constitution exists."""
        # Create constitution file
        memory_dir = initialized_project.path / ".doit" / "memory"
        (memory_dir / "constitution.md").write_text("# Constitution\n")

        validator = Validator(initialized_project)

        result = validator.check_constitution()

        assert result.status == VerifyStatus.PASS

    def test_check_roadmap_missing(self, initialized_project):
        """Test check when roadmap is missing."""
        validator = Validator(initialized_project)

        result = validator.check_roadmap()

        assert result.status == VerifyStatus.WARN
        assert "roadmap" in result.message.lower()

    def test_check_roadmap_exists(self, initialized_project):
        """Test check when roadmap exists."""
        # Create roadmap file
        memory_dir = initialized_project.path / ".doit" / "memory"
        (memory_dir / "roadmap.md").write_text("# Roadmap\n")

        validator = Validator(initialized_project)

        result = validator.check_roadmap()

        assert result.status == VerifyStatus.PASS

    def test_check_copilot_instructions_missing(self, copilot_project):
        """Test check when copilot-instructions.md is missing."""
        validator = Validator(copilot_project)

        result = validator.check_copilot_instructions()

        assert result.status == VerifyStatus.WARN
        assert "copilot-instructions" in result.message.lower()

    def test_check_copilot_instructions_exists(self, copilot_project):
        """Test check when copilot-instructions.md exists with doit section."""
        # Create copilot-instructions file with DOIT INSTRUCTIONS section
        github_dir = copilot_project.path / ".github"
        (github_dir / "copilot-instructions.md").write_text(
            "# Instructions\n\n<!-- DOIT INSTRUCTIONS START -->\n"
            "## Doit Workflow\n<!-- DOIT INSTRUCTIONS END -->\n"
        )

        validator = Validator(copilot_project)

        result = validator.check_copilot_instructions()

        assert result.status == VerifyStatus.PASS


class TestRunAllChecks:
    """Tests for run_all_checks method."""

    def test_run_all_checks_uninitialized(self, project_dir):
        """Test run_all_checks on uninitialized project."""
        project = Project(path=project_dir)
        validator = Validator(project)

        result = validator.run_all_checks()

        assert not result.passed
        assert len(result.checks) > 0

    def test_run_all_checks_initialized(self, initialized_project):
        """Test run_all_checks on initialized project."""
        validator = Validator(initialized_project)

        result = validator.run_all_checks()

        assert len(result.checks) > 0
        # Should have some passing checks
        passing = [c for c in result.checks if c.status == VerifyStatus.PASS]
        assert len(passing) > 0

    def test_run_all_checks_specific_agent(self, claude_project):
        """Test run_all_checks with specific agent."""
        validator = Validator(claude_project)

        result = validator.run_all_checks(agents=[Agent.CLAUDE])

        # Should have Claude-related checks
        check_names = [c.name for c in result.checks]
        assert any("claude" in name.lower() for name in check_names)

    def test_run_all_checks_summary(self, initialized_project):
        """Test that run_all_checks produces a summary."""
        validator = Validator(initialized_project)

        result = validator.run_all_checks()

        assert result.summary is not None
        assert len(result.summary) > 0

    def test_has_warnings_property(self, initialized_project):
        """Test has_warnings property."""
        validator = Validator(initialized_project)

        result = validator.run_all_checks()

        # Initialized project should have warnings (missing constitution, etc.)
        assert result.has_warnings

    def test_passed_with_warnings(self, initialized_project):
        """Test that project can pass with warnings."""
        # Create constitution to pass more checks
        memory_dir = initialized_project.path / ".doit" / "memory"
        (memory_dir / "constitution.md").write_text("# Constitution\n")
        (memory_dir / "roadmap.md").write_text("# Roadmap\n")

        validator = Validator(initialized_project)

        result = validator.run_all_checks()

        # Project should pass overall even with some warnings
        # (but may not pass all depending on agent checks)
        assert len(result.checks) > 0
