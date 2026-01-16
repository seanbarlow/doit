"""Unit tests for sync services (TemplateReader, PromptTransformer, PromptWriter, DriftDetector)."""

import pytest
from datetime import datetime
from pathlib import Path

from doit_cli.models.sync_models import (
    CommandTemplate,
    OperationType,
    SyncStatusEnum,
)
from doit_cli.services.template_reader import TemplateReader
from doit_cli.services.prompt_transformer import PromptTransformer
from doit_cli.services.prompt_writer import PromptWriter
from doit_cli.services.drift_detector import DriftDetector


class TestTemplateReader:
    """Tests for TemplateReader service."""

    def test_scan_templates_empty_dir_uses_package(self, temp_dir):
        """Test scanning empty directory falls back to package templates."""
        reader = TemplateReader(project_root=temp_dir)
        templates = reader.scan_templates()
        # Should find bundled package templates
        assert len(templates) > 0
        # Should have standard doit commands
        names = [t.name for t in templates]
        assert "doit.checkin" in names or "doit.specit" in names

    def test_scan_templates_missing_dir_uses_package(self, temp_dir):
        """Test scanning missing directory falls back to package templates."""
        reader = TemplateReader(project_root=temp_dir)
        templates = reader.scan_templates()
        # Should find bundled package templates
        assert len(templates) > 0

    def test_scan_templates_finds_commands(self, temp_dir):
        """Test scanning finds command templates."""
        # Create templates directory and sample files
        templates_dir = temp_dir / ".doit/templates/commands"
        templates_dir.mkdir(parents=True)

        (templates_dir / "doit.checkin.md").write_text(
            "---\ndescription: Test command\n---\n## Outline\nTest"
        )
        (templates_dir / "doit.specit.md").write_text(
            "---\ndescription: Another command\n---\n## Outline\nTest"
        )

        reader = TemplateReader(project_root=temp_dir)
        templates = reader.scan_templates()

        assert len(templates) == 2
        names = [t.name for t in templates]
        assert "doit.checkin" in names
        assert "doit.specit" in names

    def test_scan_templates_filter_by_name(self, temp_dir):
        """Test filtering templates by name."""
        templates_dir = temp_dir / ".doit/templates/commands"
        templates_dir.mkdir(parents=True)

        (templates_dir / "doit.checkin.md").write_text("# Test")
        (templates_dir / "doit.specit.md").write_text("# Test")

        reader = TemplateReader(project_root=temp_dir)
        templates = reader.scan_templates(filter_name="doit.checkin")

        assert len(templates) == 1
        assert templates[0].name == "doit.checkin"

    def test_get_template_found(self, temp_dir):
        """Test getting a specific template."""
        templates_dir = temp_dir / ".doit/templates/commands"
        templates_dir.mkdir(parents=True)
        (templates_dir / "doit.checkin.md").write_text("# Test")

        reader = TemplateReader(project_root=temp_dir)
        template = reader.get_template("doit.checkin")

        assert template is not None
        assert template.name == "doit.checkin"

    def test_get_template_not_found(self, temp_dir):
        """Test getting a non-existent template."""
        templates_dir = temp_dir / ".doit/templates/commands"
        templates_dir.mkdir(parents=True)

        reader = TemplateReader(project_root=temp_dir)
        template = reader.get_template("doit.nonexistent")

        assert template is None


class TestPromptTransformer:
    """Tests for PromptTransformer service."""

    def test_strip_yaml_frontmatter(self):
        """Test YAML frontmatter is stripped."""
        transformer = PromptTransformer()
        content = "---\ndescription: Test\n---\n## Outline\nContent"

        result = transformer._strip_yaml_frontmatter(content)

        assert "---" not in result
        assert "description: Test" not in result
        assert "## Outline" in result

    def test_replace_arguments_placeholder(self):
        """Test $ARGUMENTS placeholder is replaced."""
        transformer = PromptTransformer()
        content = "```text\n$ARGUMENTS\n```\nThen use $ARGUMENTS again."

        result = transformer._replace_arguments_placeholder(content)

        assert "$ARGUMENTS" not in result
        assert "user" in result.lower()

    def test_transform_full_template(self, temp_dir):
        """Test full transformation of a template."""
        templates_dir = temp_dir / ".doit/templates/commands"
        templates_dir.mkdir(parents=True)

        template_content = """---
description: Test command description
---

## User Input

```text
$ARGUMENTS
```

## Outline

1. Do something
2. Do something else
"""
        template_path = templates_dir / "doit.test.md"
        template_path.write_text(template_content)

        template = CommandTemplate.from_path(template_path)
        transformer = PromptTransformer()

        result = transformer.transform(template)

        # Check frontmatter removed
        assert "---\ndescription" not in result
        # Check title added
        assert "# Doit Test" in result
        # Check description preserved
        assert "Test command description" in result
        # Check $ARGUMENTS replaced
        assert "$ARGUMENTS" not in result
        # Check outline preserved
        assert "## Outline" in result


class TestPromptWriter:
    """Tests for PromptWriter service."""

    def test_write_prompt_creates_file(self, temp_dir):
        """Test that write_prompt creates a prompt file."""
        # Setup
        templates_dir = temp_dir / ".doit/templates/commands"
        templates_dir.mkdir(parents=True)
        (templates_dir / "doit.test.md").write_text("# Test content")

        prompts_dir = temp_dir / ".github/prompts"

        template = CommandTemplate.from_path(templates_dir / "doit.test.md")
        writer = PromptWriter(project_root=temp_dir)

        # Execute
        operation = writer.write_prompt(template)

        # Verify
        assert operation.success
        assert operation.operation_type == OperationType.CREATED
        assert (prompts_dir / "doit.test.prompt.md").exists()

    def test_write_prompt_skips_up_to_date(self, temp_dir):
        """Test that write_prompt skips files that are up-to-date."""
        # Setup
        templates_dir = temp_dir / ".doit/templates/commands"
        templates_dir.mkdir(parents=True)
        template_path = templates_dir / "doit.test.md"
        template_path.write_text("# Test content")

        prompts_dir = temp_dir / ".github/prompts"
        prompts_dir.mkdir(parents=True)
        prompt_path = prompts_dir / "doit.test.prompt.md"
        prompt_path.write_text("# Already exists")

        # Make prompt newer than template
        import time
        time.sleep(0.01)
        prompt_path.touch()

        template = CommandTemplate.from_path(template_path)
        writer = PromptWriter(project_root=temp_dir)

        # Execute
        operation = writer.write_prompt(template)

        # Verify
        assert operation.success
        assert operation.operation_type == OperationType.SKIPPED

    def test_write_prompts_batch(self, temp_dir):
        """Test writing multiple prompts."""
        # Setup
        templates_dir = temp_dir / ".doit/templates/commands"
        templates_dir.mkdir(parents=True)
        (templates_dir / "doit.cmd1.md").write_text("# Cmd 1")
        (templates_dir / "doit.cmd2.md").write_text("# Cmd 2")

        reader = TemplateReader(project_root=temp_dir)
        writer = PromptWriter(project_root=temp_dir)
        templates = reader.scan_templates()

        # Execute
        result = writer.write_prompts(templates)

        # Verify
        assert result.total_commands == 2
        assert result.synced == 2
        assert result.success


class TestDriftDetector:
    """Tests for DriftDetector service."""

    def test_check_missing_prompt(self, temp_dir):
        """Test detecting missing prompt file."""
        templates_dir = temp_dir / ".doit/templates/commands"
        templates_dir.mkdir(parents=True)
        (templates_dir / "doit.test.md").write_text("# Test")

        template = CommandTemplate.from_path(templates_dir / "doit.test.md")
        detector = DriftDetector(project_root=temp_dir)

        status = detector.check_sync_status(template)

        assert status.status == SyncStatusEnum.MISSING
        assert "exists" in status.reason.lower()

    def test_check_synchronized(self, temp_dir):
        """Test detecting synchronized files."""
        # Create template
        templates_dir = temp_dir / ".doit/templates/commands"
        templates_dir.mkdir(parents=True)
        template_path = templates_dir / "doit.test.md"
        template_path.write_text("# Test")

        # Create prompt (newer than template)
        prompts_dir = temp_dir / ".github/prompts"
        prompts_dir.mkdir(parents=True)
        prompt_path = prompts_dir / "doit.test.prompt.md"

        import time
        time.sleep(0.01)
        prompt_path.write_text("# Generated")

        template = CommandTemplate.from_path(template_path)
        detector = DriftDetector(project_root=temp_dir)

        status = detector.check_sync_status(template)

        assert status.status == SyncStatusEnum.SYNCHRONIZED

    def test_check_out_of_sync(self, temp_dir):
        """Test detecting out-of-sync files."""
        # Create prompt first
        prompts_dir = temp_dir / ".github/prompts"
        prompts_dir.mkdir(parents=True)
        prompt_path = prompts_dir / "doit.test.prompt.md"
        prompt_path.write_text("# Old prompt")

        import time
        time.sleep(0.01)

        # Create template (newer than prompt)
        templates_dir = temp_dir / ".doit/templates/commands"
        templates_dir.mkdir(parents=True)
        template_path = templates_dir / "doit.test.md"
        template_path.write_text("# Updated template")

        template = CommandTemplate.from_path(template_path)
        detector = DriftDetector(project_root=temp_dir)

        status = detector.check_sync_status(template)

        assert status.status == SyncStatusEnum.OUT_OF_SYNC

    def test_is_all_synced(self, temp_dir):
        """Test checking if all templates are synced."""
        templates_dir = temp_dir / ".doit/templates/commands"
        templates_dir.mkdir(parents=True)
        (templates_dir / "doit.test.md").write_text("# Test")

        prompts_dir = temp_dir / ".github/prompts"
        prompts_dir.mkdir(parents=True)

        import time
        time.sleep(0.01)
        (prompts_dir / "doit.test.prompt.md").write_text("# Prompt")

        reader = TemplateReader(project_root=temp_dir)
        detector = DriftDetector(project_root=temp_dir)
        templates = reader.scan_templates()

        assert detector.is_all_synced(templates)
