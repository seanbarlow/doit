"""Integration tests for sync-prompts command."""

import pytest
from pathlib import Path
from typer.testing import CliRunner

from doit_cli.main import app


runner = CliRunner()


class TestSyncPromptsCommand:
    """Integration tests for the sync-prompts CLI command."""

    def test_sync_prompts_uses_package_templates(self, temp_dir):
        """Test sync-prompts uses package templates when project templates don't exist."""
        result = runner.invoke(app, ["sync-prompts", "--path", str(temp_dir)])

        # Should succeed using bundled package templates
        assert result.exit_code == 0
        # Should have synced the bundled templates (at least some of the 11 commands)
        assert "synced" in result.stdout.lower() or "CREATED" in result.stdout

    def test_sync_prompts_creates_files(self, temp_dir):
        """Test sync-prompts creates prompt files."""
        # Setup templates directory
        templates_dir = temp_dir / ".doit/templates/commands"
        templates_dir.mkdir(parents=True)

        (templates_dir / "doit.test1.md").write_text(
            "---\ndescription: Test 1\n---\n## Outline\nStep 1"
        )
        (templates_dir / "doit.test2.md").write_text(
            "---\ndescription: Test 2\n---\n## Outline\nStep 2"
        )

        # Run command
        result = runner.invoke(app, ["sync-prompts", "--path", str(temp_dir)])

        # Verify
        assert result.exit_code == 0
        assert "CREATED" in result.stdout

        prompts_dir = temp_dir / ".github/prompts"
        assert (prompts_dir / "doit.test1.prompt.md").exists()
        assert (prompts_dir / "doit.test2.prompt.md").exists()

    def test_sync_prompts_check_mode(self, temp_dir):
        """Test sync-prompts --check mode."""
        # Setup
        templates_dir = temp_dir / ".doit/templates/commands"
        templates_dir.mkdir(parents=True)
        (templates_dir / "doit.test.md").write_text("# Test")

        prompts_dir = temp_dir / ".github/prompts"
        prompts_dir.mkdir(parents=True)

        import time
        time.sleep(0.01)
        (prompts_dir / "doit.test.prompt.md").write_text("# Prompt")

        # Run check mode
        result = runner.invoke(app, ["sync-prompts", "--check", "--path", str(temp_dir)])

        # Verify - should show up-to-date
        assert result.exit_code == 0
        assert "Up-to-date" in result.stdout or "SKIPPED" in result.stdout

    def test_sync_prompts_single_command(self, temp_dir):
        """Test syncing a single command."""
        # Setup
        templates_dir = temp_dir / ".doit/templates/commands"
        templates_dir.mkdir(parents=True)
        (templates_dir / "doit.cmd1.md").write_text("# Cmd 1")
        (templates_dir / "doit.cmd2.md").write_text("# Cmd 2")

        # Run for single command
        result = runner.invoke(
            app, ["sync-prompts", "doit.cmd1", "--path", str(temp_dir)]
        )

        # Verify only cmd1 was synced
        assert result.exit_code == 0
        assert "1 commands" in result.stdout

        prompts_dir = temp_dir / ".github/prompts"
        assert (prompts_dir / "doit.cmd1.prompt.md").exists()
        assert not (prompts_dir / "doit.cmd2.prompt.md").exists()

    def test_sync_prompts_force_mode(self, temp_dir):
        """Test sync-prompts --force mode."""
        # Setup with existing prompt
        templates_dir = temp_dir / ".doit/templates/commands"
        templates_dir.mkdir(parents=True)
        (templates_dir / "doit.test.md").write_text("# Template")

        prompts_dir = temp_dir / ".github/prompts"
        prompts_dir.mkdir(parents=True)

        import time
        time.sleep(0.01)
        (prompts_dir / "doit.test.prompt.md").write_text("# Old prompt")

        # First run without force - should skip
        result1 = runner.invoke(app, ["sync-prompts", "--path", str(temp_dir)])
        assert "SKIPPED" in result1.stdout

        # Run with force - should update
        result2 = runner.invoke(app, ["sync-prompts", "--force", "--path", str(temp_dir)])
        assert result2.exit_code == 0
        # With force, it should create/update even if up-to-date
        assert "CREATED" in result2.stdout or "UPDATED" in result2.stdout

    def test_sync_prompts_json_output(self, temp_dir):
        """Test sync-prompts --json output."""
        # Setup
        templates_dir = temp_dir / ".doit/templates/commands"
        templates_dir.mkdir(parents=True)
        (templates_dir / "doit.test.md").write_text("# Test")

        # Run with JSON output
        result = runner.invoke(app, ["sync-prompts", "--json", "--path", str(temp_dir)])

        # Verify JSON output
        assert result.exit_code == 0
        import json
        output = json.loads(result.stdout)
        assert "total_commands" in output
        assert "operations" in output
        assert output["total_commands"] == 1

    def test_sync_prompts_content_transformation(self, temp_dir):
        """Test that content is properly transformed."""
        # Setup with YAML frontmatter and $ARGUMENTS
        templates_dir = temp_dir / ".doit/templates/commands"
        templates_dir.mkdir(parents=True)

        template_content = """---
description: Test description
---

## User Input

```text
$ARGUMENTS
```

## Outline

1. Step one
"""
        (templates_dir / "doit.test.md").write_text(template_content)

        # Run sync
        result = runner.invoke(app, ["sync-prompts", "--path", str(temp_dir)])
        assert result.exit_code == 0

        # Verify transformation
        prompt_path = temp_dir / ".github/prompts/doit.test.prompt.md"
        prompt_content = prompt_path.read_text()

        # YAML frontmatter should be stripped
        assert "---\ndescription" not in prompt_content
        # $ARGUMENTS should be replaced
        assert "$ARGUMENTS" not in prompt_content
        # Description should be preserved
        assert "Test description" in prompt_content
        # Outline should be preserved
        assert "## Outline" in prompt_content

    def test_sync_prompts_nonexistent_command(self, temp_dir):
        """Test syncing a non-existent command."""
        # Setup
        templates_dir = temp_dir / ".doit/templates/commands"
        templates_dir.mkdir(parents=True)
        (templates_dir / "doit.exists.md").write_text("# Exists")

        # Try to sync non-existent command
        result = runner.invoke(
            app, ["sync-prompts", "doit.nonexistent", "--path", str(temp_dir)]
        )

        assert result.exit_code == 1
        assert "not found" in result.stdout.lower()
