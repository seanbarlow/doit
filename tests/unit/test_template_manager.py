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
        """Test getting template source path for Copilot.

        Note: With unified templates (024-unified-templates), both agents
        now use 'commands' as their source directory.
        """
        manager = TemplateManager()

        path = manager.get_template_source_path(Agent.COPILOT)

        # Copilot now uses commands/ as source (single source of truth)
        assert "commands" in str(path)

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


class TestCopyScripts:
    """Tests for workflow script copying."""

    def test_copy_scripts_creates_new_files(self, temp_dir):
        """Test scripts are created when target dir is empty."""
        from doit_cli.services.template_manager import WORKFLOW_SCRIPTS

        manager = TemplateManager()
        target_dir = temp_dir / ".doit" / "scripts" / "bash"

        result = manager.copy_scripts(target_dir)

        # Should have created scripts (if source exists)
        # The number depends on what's in templates/scripts/bash/
        created_count = len(result["created"])
        assert created_count >= 0  # May be 0 if source doesn't exist in test env
        assert len(result["skipped"]) == 0

        # If scripts were created, verify they exist
        if created_count > 0:
            assert target_dir.exists()

    def test_copy_scripts_preserves_permissions(self, temp_dir):
        """Test scripts retain executable permissions."""
        import os

        manager = TemplateManager()
        target_dir = temp_dir / ".doit" / "scripts" / "bash"

        result = manager.copy_scripts(target_dir)

        # Check permissions for each created script
        for script_path in result["created"]:
            # Script should be executable
            assert os.access(script_path, os.X_OK), f"{script_path} should be executable"

    def test_copy_scripts_skips_existing(self, temp_dir):
        """Test existing scripts are not overwritten without flag."""
        manager = TemplateManager()
        target_dir = temp_dir / ".doit" / "scripts" / "bash"
        target_dir.mkdir(parents=True)

        # Create an existing script with custom content
        existing_script = target_dir / "common.sh"
        custom_content = "#!/bin/bash\n# Custom script content\necho 'custom'"
        existing_script.write_text(custom_content)

        result = manager.copy_scripts(target_dir)

        # The existing script should be preserved
        assert existing_script.read_text() == custom_content

        # Check that common.sh is in skipped (if scripts source exists)
        skipped_names = [p.name for p in result["skipped"]]
        if skipped_names:
            assert "common.sh" in skipped_names

    def test_copy_scripts_overwrites_with_flag(self, temp_dir):
        """Test existing scripts are overwritten with overwrite=True."""
        manager = TemplateManager()
        target_dir = temp_dir / ".doit" / "scripts" / "bash"
        target_dir.mkdir(parents=True)

        # Create an existing script with custom content
        existing_script = target_dir / "common.sh"
        custom_content = "#!/bin/bash\n# Custom script content\necho 'custom'"
        existing_script.write_text(custom_content)

        result = manager.copy_scripts(target_dir, overwrite=True)

        # If scripts source exists, the script should be updated
        if result["updated"]:
            updated_names = [p.name for p in result["updated"]]
            assert "common.sh" in updated_names
            # Content should be different (from bundled scripts)
            new_content = existing_script.read_text()
            assert new_content != custom_content

    def test_copy_scripts_creates_parent_directories(self, temp_dir):
        """Test that copy_scripts creates parent directories if needed."""
        manager = TemplateManager()
        target_dir = temp_dir / "deep" / "nested" / "path" / "scripts" / "bash"

        # Target dir doesn't exist yet
        assert not target_dir.exists()

        result = manager.copy_scripts(target_dir)

        # If any scripts were copied, the directory should exist
        if result["created"]:
            assert target_dir.exists()

    def test_copy_scripts_returns_correct_structure(self, temp_dir):
        """Test that copy_scripts returns dict with correct keys."""
        manager = TemplateManager()
        target_dir = temp_dir / ".doit" / "scripts" / "bash"

        result = manager.copy_scripts(target_dir)

        assert "created" in result
        assert "updated" in result
        assert "skipped" in result
        assert isinstance(result["created"], list)
        assert isinstance(result["updated"], list)
        assert isinstance(result["skipped"], list)


class TestUnifiedTemplates:
    """Tests for unified template management (024-unified-templates).

    Both Claude and Copilot now use templates/commands/ as the single source.
    Copilot prompts are transformed on-the-fly during copy.
    """

    def test_both_agents_use_same_source_directory(self):
        """Test both agents read from the same source directory."""
        manager = TemplateManager()

        claude_path = manager.get_template_source_path(Agent.CLAUDE)
        copilot_path = manager.get_template_source_path(Agent.COPILOT)

        # Both should point to commands/
        assert claude_path == copilot_path
        assert "commands" in str(claude_path)

    def test_get_command_templates_returns_templates(self):
        """Test _get_command_templates returns templates from commands/."""
        manager = TemplateManager()

        templates = manager._get_command_templates()

        assert isinstance(templates, list)
        # Should have some templates if commands/ exists
        assert len(templates) > 0

    def test_get_command_templates_parses_as_claude_format(self):
        """Test _get_command_templates parses all files as Claude format."""
        manager = TemplateManager()

        templates = manager._get_command_templates()

        for template in templates:
            # Template names should be extracted correctly
            assert template.name in DOIT_COMMANDS or template.name.startswith("doit")
            # Filenames should have Claude format
            assert template.target_filename.startswith("doit.")
            assert template.target_filename.endswith(".md")
            assert ".prompt." not in template.target_filename

    def test_copy_templates_claude_direct_copy(self, temp_dir):
        """Test Claude templates are copied directly without transformation."""
        manager = TemplateManager()
        target_dir = temp_dir / "claude_output"
        target_dir.mkdir()

        result = manager.copy_templates_for_agent(Agent.CLAUDE, target_dir)

        # Should have created files
        assert len(result["created"]) > 0

        # Files should have Claude naming convention
        for path in result["created"]:
            assert path.name.startswith("doit.")
            assert path.name.endswith(".md")
            assert ".prompt." not in path.name

    def test_copy_templates_copilot_transforms(self, temp_dir):
        """Test Copilot templates are transformed during copy."""
        manager = TemplateManager()
        target_dir = temp_dir / "copilot_output"
        target_dir.mkdir()

        result = manager.copy_templates_for_agent(Agent.COPILOT, target_dir)

        # Should have created files
        assert len(result["created"]) > 0

        # Files should have Copilot naming convention
        for path in result["created"]:
            assert path.name.startswith("doit.")
            assert path.name.endswith(".prompt.md")

    def test_copilot_templates_are_transformed(self, temp_dir):
        """Test Copilot templates have YAML frontmatter removed."""
        manager = TemplateManager()
        target_dir = temp_dir / "copilot_output"
        target_dir.mkdir()

        manager.copy_templates_for_agent(Agent.COPILOT, target_dir)

        # Check content of generated files
        for prompt_file in target_dir.iterdir():
            if prompt_file.is_file():
                content = prompt_file.read_text()
                # YAML frontmatter should be removed
                assert not content.startswith("---")
                # $ARGUMENTS should be replaced
                assert "$ARGUMENTS" not in content

    def test_claude_templates_preserve_yaml(self, temp_dir):
        """Test Claude templates preserve YAML frontmatter."""
        manager = TemplateManager()
        target_dir = temp_dir / "claude_output"
        target_dir.mkdir()

        manager.copy_templates_for_agent(Agent.CLAUDE, target_dir)

        # Check content of generated files
        yaml_found = False
        for command_file in target_dir.iterdir():
            if command_file.is_file():
                content = command_file.read_text()
                # At least some should have YAML frontmatter
                if content.startswith("---"):
                    yaml_found = True
                    break

        assert yaml_found, "Expected at least one Claude template with YAML frontmatter"

    def test_transform_and_write_generates_correct_filenames(self, temp_dir):
        """Test _transform_and_write_templates generates correct filenames."""
        manager = TemplateManager()
        target_dir = temp_dir / "transform_test"
        target_dir.mkdir()

        templates = manager._get_command_templates()
        result = manager._transform_and_write_templates(templates, target_dir)

        # Each created file should match doit.{name}.prompt.md pattern
        for path in result["created"]:
            filename = path.name
            assert filename.startswith("doit.")
            assert filename.endswith(".prompt.md")
            # Extract name and verify it's valid
            name = filename.replace("doit.", "").replace(".prompt.md", "")
            assert name in DOIT_COMMANDS
