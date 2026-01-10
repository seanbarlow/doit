"""Integration tests for init command CLI workflows."""

import pytest
from pathlib import Path
from typer.testing import CliRunner

from doit_cli.models.agent import Agent


runner = CliRunner()


class TestInitCommand:
    """Integration tests for init command."""

    def test_init_creates_doit_structure(self, project_dir):
        """Test that init creates .doit structure."""
        from doit_cli.main import app

        result = runner.invoke(app, ["init", str(project_dir), "--yes"])

        assert result.exit_code == 0
        assert (project_dir / ".doit").exists()
        assert (project_dir / ".doit" / "memory").exists()
        assert (project_dir / ".doit" / "templates").exists()
        assert (project_dir / ".doit" / "scripts").exists()

    def test_init_with_claude_agent(self, project_dir):
        """Test init with Claude agent."""
        from doit_cli.main import app

        result = runner.invoke(app, ["init", str(project_dir), "--agent", "claude", "--yes"])

        assert result.exit_code == 0
        assert (project_dir / ".claude" / "commands").exists()

    def test_init_with_copilot_agent(self, project_dir):
        """Test init with Copilot agent."""
        from doit_cli.main import app

        result = runner.invoke(app, ["init", str(project_dir), "--agent", "copilot", "--yes"])

        assert result.exit_code == 0
        assert (project_dir / ".github" / "prompts").exists()

    def test_init_with_both_agents(self, project_dir):
        """Test init with both agents."""
        from doit_cli.main import app

        result = runner.invoke(
            app, ["init", str(project_dir), "--agent", "claude,copilot", "--yes"]
        )

        assert result.exit_code == 0
        assert (project_dir / ".claude" / "commands").exists()
        assert (project_dir / ".github" / "prompts").exists()

    def test_init_invalid_agent(self, project_dir):
        """Test init with invalid agent name."""
        from doit_cli.main import app

        result = runner.invoke(
            app, ["init", str(project_dir), "--agent", "invalid", "--yes"]
        )

        assert result.exit_code == 1
        assert "unknown agent" in result.output.lower()

    def test_init_creates_templates(self, project_dir):
        """Test that init creates command templates."""
        from doit_cli.main import app

        result = runner.invoke(
            app, ["init", str(project_dir), "--agent", "claude", "--yes"]
        )

        assert result.exit_code == 0
        command_dir = project_dir / ".claude" / "commands"

        # Check for some expected template files
        template_files = list(command_dir.glob("doit-*.md"))
        assert len(template_files) > 0

    def test_init_displays_success_message(self, project_dir):
        """Test that init displays success message."""
        from doit_cli.main import app

        result = runner.invoke(
            app, ["init", str(project_dir), "--agent", "claude", "--yes"]
        )

        assert result.exit_code == 0
        # Should show some form of success message
        assert "complete" in result.output.lower() or "success" in result.output.lower()

    def test_init_update_flag(self, project_dir):
        """Test init with --update flag."""
        from doit_cli.main import app

        # First init
        runner.invoke(app, ["init", str(project_dir), "--agent", "claude", "--yes"])

        # Modify a file
        command_dir = project_dir / ".claude" / "commands"
        specit_file = command_dir / "doit-specit.md"
        if specit_file.exists():
            specit_file.write_text("# Modified\n")

        # Run update
        result = runner.invoke(
            app, ["init", str(project_dir), "--agent", "claude", "--update", "--yes"]
        )

        assert result.exit_code == 0

    def test_init_force_flag(self, project_dir):
        """Test init with --force flag."""
        from doit_cli.main import app

        # First init
        runner.invoke(app, ["init", str(project_dir), "--agent", "claude", "--yes"])

        # Run with force
        result = runner.invoke(
            app, ["init", str(project_dir), "--agent", "claude", "--force", "--yes"]
        )

        assert result.exit_code == 0

    def test_init_custom_templates_invalid_path(self, project_dir, temp_dir):
        """Test init with invalid custom templates path."""
        from doit_cli.main import app

        nonexistent = temp_dir / "nonexistent"
        result = runner.invoke(
            app,
            ["init", str(project_dir), "--templates", str(nonexistent), "--yes"],
        )

        assert result.exit_code == 1
        assert "does not exist" in result.output.lower()


class TestInitCommandAutoDetection:
    """Tests for agent auto-detection."""

    def test_autodetect_claude(self, project_dir):
        """Test auto-detection of Claude from existing .claude directory."""
        from doit_cli.main import app

        # Pre-create .claude directory
        (project_dir / ".claude").mkdir()

        result = runner.invoke(app, ["init", str(project_dir), "--yes"])

        assert result.exit_code == 0
        assert "claude" in result.output.lower() or (project_dir / ".claude" / "commands").exists()

    def test_autodetect_copilot(self, project_dir):
        """Test auto-detection of Copilot from existing config."""
        from doit_cli.main import app

        # Pre-create .github/copilot-instructions.md
        github_dir = project_dir / ".github"
        github_dir.mkdir()
        (github_dir / "copilot-instructions.md").write_text("# Instructions\n")

        result = runner.invoke(app, ["init", str(project_dir), "--yes"])

        assert result.exit_code == 0
