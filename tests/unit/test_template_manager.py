"""Unit tests for TemplateManager service."""

import pytest
from pathlib import Path

from doit_cli.models.agent import Agent
from doit_cli.models.template import DOIT_COMMANDS
from doit_cli.services.template_manager import TemplateManager


class TestTemplateManager:
    """Tests for TemplateManager service."""

    def test_init_default_source(self):
        """Test initialization with default bundled source."""
        manager = TemplateManager()

        assert manager.custom_source is None

    def test_init_custom_source(self, temp_dir):
        """Test initialization with custom source."""
        manager = TemplateManager(custom_source=temp_dir)

        assert manager.custom_source == temp_dir

    def test_get_template_source_path_claude(self):
        """Test getting template source path for Claude."""
        manager = TemplateManager()

        path = manager.get_template_source_path(Agent.CLAUDE)

        assert "commands" in str(path)

    def test_get_template_source_path_copilot(self):
        """Test getting template source path for Copilot."""
        manager = TemplateManager()

        path = manager.get_template_source_path(Agent.COPILOT)

        assert "prompts" in str(path)

    def test_get_template_source_path_custom(self, temp_dir):
        """Test getting template source path with custom source."""
        manager = TemplateManager(custom_source=temp_dir)

        claude_path = manager.get_template_source_path(Agent.CLAUDE)
        copilot_path = manager.get_template_source_path(Agent.COPILOT)

        assert str(claude_path).startswith(str(temp_dir))
        assert str(copilot_path).startswith(str(temp_dir))

    def test_get_bundled_templates_returns_list(self):
        """Test that get_bundled_templates returns a list."""
        manager = TemplateManager()

        templates = manager.get_bundled_templates(Agent.CLAUDE)

        assert isinstance(templates, list)

    def test_validate_template_source_missing_source(self, temp_dir):
        """Test validation when source directory doesn't exist."""
        manager = TemplateManager(custom_source=temp_dir / "nonexistent")

        result = manager.validate_template_source(Agent.CLAUDE)

        assert not result["valid"]
        assert not result["source_exists"]
        assert len(result["missing"]) == len(DOIT_COMMANDS)

    def test_validate_custom_source_nonexistent(self, temp_dir):
        """Test validation of nonexistent custom source."""
        manager = TemplateManager(custom_source=temp_dir / "nonexistent")

        result = manager.validate_custom_source()

        assert not result["valid"]
        assert "does not exist" in result.get("error", "")

    def test_validate_custom_source_not_directory(self, temp_dir):
        """Test validation when custom source is not a directory."""
        file_path = temp_dir / "file.txt"
        file_path.write_text("content")

        manager = TemplateManager(custom_source=file_path)

        result = manager.validate_custom_source()

        assert not result["valid"]
        assert "not a directory" in result.get("error", "")

    def test_validate_custom_source_empty_directory(self, temp_dir):
        """Test validation of empty custom source directory."""
        empty_dir = temp_dir / "empty"
        empty_dir.mkdir()

        manager = TemplateManager(custom_source=empty_dir)

        result = manager.validate_custom_source()

        # Empty directory should be invalid (no templates found)
        assert not result["valid"]

    def test_copy_templates_creates_files(self, temp_dir):
        """Test that copy_templates creates target files."""
        manager = TemplateManager()
        target_dir = temp_dir / "target"
        target_dir.mkdir()

        result = manager.copy_templates_for_agent(
            agent=Agent.CLAUDE,
            target_dir=target_dir,
        )

        # Should have created some files
        created = result["created"]
        assert len(created) > 0

    def test_copy_templates_skips_existing(self, temp_dir):
        """Test that copy_templates skips existing files by default."""
        manager = TemplateManager()
        target_dir = temp_dir / "target"
        target_dir.mkdir()

        # Copy first time
        manager.copy_templates_for_agent(Agent.CLAUDE, target_dir)

        # Copy second time - should skip existing
        result = manager.copy_templates_for_agent(Agent.CLAUDE, target_dir)

        assert len(result["skipped"]) > 0
        assert len(result["created"]) == 0

    def test_copy_templates_overwrites_when_requested(self, temp_dir):
        """Test that copy_templates overwrites when overwrite=True."""
        manager = TemplateManager()
        target_dir = temp_dir / "target"
        target_dir.mkdir()

        # Copy first time
        manager.copy_templates_for_agent(Agent.CLAUDE, target_dir)

        # Copy second time with overwrite
        result = manager.copy_templates_for_agent(
            Agent.CLAUDE, target_dir, overwrite=True
        )

        assert len(result["updated"]) > 0
        assert len(result["skipped"]) == 0


class TestCopilotInstructions:
    """Tests for copilot-instructions.md management."""

    def test_create_copilot_instructions_new_file(self, temp_dir):
        """Test creating new copilot-instructions.md."""
        manager = TemplateManager()
        target_path = temp_dir / ".github" / "copilot-instructions.md"

        result = manager.create_copilot_instructions(target_path)

        assert result is True
        assert target_path.exists()
        content = target_path.read_text()
        assert "DOIT INSTRUCTIONS START" in content
        assert "doit-specit" in content

    def test_create_copilot_instructions_append_to_existing(self, temp_dir):
        """Test appending doit section to existing file."""
        manager = TemplateManager()
        target_path = temp_dir / "copilot-instructions.md"

        # Create existing file
        target_path.write_text("# Existing Instructions\n\nSome content.\n")

        result = manager.create_copilot_instructions(target_path)

        assert result is True
        content = target_path.read_text()
        assert "Existing Instructions" in content
        assert "DOIT INSTRUCTIONS START" in content

    def test_create_copilot_instructions_update_existing_section(self, temp_dir):
        """Test updating existing doit section."""
        manager = TemplateManager()
        target_path = temp_dir / "copilot-instructions.md"

        # Create file with existing doit section
        initial_content = f"""# Instructions

{TemplateManager.COPILOT_SECTION_START}
Old content
{TemplateManager.COPILOT_SECTION_END}

Other content.
"""
        target_path.write_text(initial_content)

        result = manager.create_copilot_instructions(target_path)

        assert result is True
        content = target_path.read_text()
        assert "Old content" not in content
        assert "doit-specit" in content
        assert "Other content" in content

    def test_create_copilot_instructions_update_only_skips_nonexistent(self, temp_dir):
        """Test update_only=True skips if file doesn't exist."""
        manager = TemplateManager()
        target_path = temp_dir / "copilot-instructions.md"

        result = manager.create_copilot_instructions(target_path, update_only=True)

        assert result is False
        assert not target_path.exists()
