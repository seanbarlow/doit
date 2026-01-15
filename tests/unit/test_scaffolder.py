"""Unit tests for Scaffolder service."""

import pytest
from pathlib import Path

from doit_cli.models.agent import Agent
from doit_cli.models.project import Project
from doit_cli.services.scaffolder import Scaffolder


class TestScaffolder:
    """Tests for Scaffolder service."""

    def test_create_doit_structure(self, project_dir):
        """Test creating the .doit folder structure."""
        project = Project(path=project_dir)
        scaffolder = Scaffolder(project)

        result = scaffolder.create_doit_structure()

        assert result.success
        assert (project_dir / ".doit").exists()
        assert (project_dir / ".doit" / "memory").exists()
        assert (project_dir / ".doit" / "templates").exists()
        assert (project_dir / ".doit" / "scripts").exists()

    def test_create_doit_structure_idempotent(self, project_dir):
        """Test that create_doit_structure is idempotent."""
        project = Project(path=project_dir)
        scaffolder = Scaffolder(project)

        # Run twice
        result1 = scaffolder.create_doit_structure()
        result2 = scaffolder.create_doit_structure()

        assert result1.success
        assert result2.success
        assert (project_dir / ".doit").exists()

    def test_create_agent_directory_claude(self, initialized_project):
        """Test creating Claude agent directory."""
        scaffolder = Scaffolder(initialized_project)

        scaffolder.create_agent_directory(Agent.CLAUDE)

        expected_dir = initialized_project.path / ".claude" / "commands"
        assert expected_dir.exists()

    def test_create_agent_directory_copilot(self, initialized_project):
        """Test creating Copilot agent directory."""
        scaffolder = Scaffolder(initialized_project)

        scaffolder.create_agent_directory(Agent.COPILOT)

        expected_dir = initialized_project.path / ".github" / "prompts"
        assert expected_dir.exists()

    def test_get_preserved_paths(self, initialized_project):
        """Test getting preserved paths during updates."""
        # Create files in memory directory
        memory_dir = initialized_project.path / ".doit" / "memory"
        (memory_dir / "constitution.md").write_text("# Constitution\n")
        (memory_dir / "roadmap.md").write_text("# Roadmap\n")

        scaffolder = Scaffolder(initialized_project)
        preserved = scaffolder.get_preserved_paths()

        # Memory directory files should be preserved
        assert any("memory" in str(p) for p in preserved)

    def test_should_preserve_memory_files(self, initialized_project):
        """Test that memory files are preserved during updates."""
        memory_dir = initialized_project.path / ".doit" / "memory"
        constitution_file = memory_dir / "constitution.md"
        constitution_file.write_text("# Constitution\n")

        scaffolder = Scaffolder(initialized_project)

        assert scaffolder.should_preserve(constitution_file)

    def test_should_not_preserve_doit_templates(self, claude_project):
        """Test that doit-managed templates are not preserved."""
        command_dir = claude_project.command_directory(Agent.CLAUDE)
        # Claude uses doit.*.md naming convention
        doit_file = command_dir / "doit.specit.md"

        scaffolder = Scaffolder(claude_project)

        assert not scaffolder.should_preserve(doit_file)

    def test_get_files_to_update_claude(self, claude_project):
        """Test getting updatable files for Claude agent."""
        command_dir = claude_project.command_directory(Agent.CLAUDE)
        # Claude uses doit.*.md naming convention
        (command_dir / "doit.planit.md").write_text("# Plan\n")
        (command_dir / "custom-command.md").write_text("# Custom\n")

        scaffolder = Scaffolder(claude_project)
        files_to_update = scaffolder.get_files_to_update(Agent.CLAUDE)

        # Should include doit-managed files only (doit.*.md pattern for Claude)
        file_names = [f.name for f in files_to_update]
        assert "doit.specit.md" in file_names
        assert "doit.planit.md" in file_names
        assert "custom-command.md" not in file_names
