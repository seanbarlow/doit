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

        # Check for some expected template files (doit.*.md pattern)
        template_files = list(command_dir.glob("doit.*.md"))
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


class TestInitScriptsCopy:
    """Tests for workflow scripts copy during init."""

    def test_init_copies_scripts(self, project_dir):
        """Test doit init copies all 5 scripts."""
        import os
        from doit_cli.main import app
        from doit_cli.services.template_manager import WORKFLOW_SCRIPTS

        result = runner.invoke(
            app, ["init", str(project_dir), "--agent", "claude", "--yes"]
        )

        assert result.exit_code == 0
        scripts_dir = project_dir / ".doit" / "scripts" / "bash"
        assert scripts_dir.exists()

        # Check all 5 scripts exist
        for script_name in WORKFLOW_SCRIPTS:
            script_path = scripts_dir / script_name
            assert script_path.exists(), f"Script {script_name} should exist"

    def test_init_scripts_are_executable(self, project_dir):
        """Test initialized scripts have execute permission."""
        import os
        from doit_cli.main import app
        from doit_cli.services.template_manager import WORKFLOW_SCRIPTS

        runner.invoke(
            app, ["init", str(project_dir), "--agent", "claude", "--yes"]
        )

        scripts_dir = project_dir / ".doit" / "scripts" / "bash"
        for script_name in WORKFLOW_SCRIPTS:
            script_path = scripts_dir / script_name
            if script_path.exists():
                assert os.access(script_path, os.X_OK), f"{script_name} should be executable"

    def test_init_scripts_not_overwritten_by_default(self, project_dir):
        """Test existing scripts are not overwritten without flag."""
        from doit_cli.main import app

        # First init
        runner.invoke(
            app, ["init", str(project_dir), "--agent", "claude", "--yes"]
        )

        # Modify a script
        scripts_dir = project_dir / ".doit" / "scripts" / "bash"
        common_sh = scripts_dir / "common.sh"
        custom_content = "#!/bin/bash\n# Custom modification\n"
        common_sh.write_text(custom_content)

        # Second init without force/update
        runner.invoke(
            app, ["init", str(project_dir), "--agent", "claude", "--yes"]
        )

        # Script should be preserved
        assert common_sh.read_text() == custom_content

    def test_init_scripts_overwritten_with_force(self, project_dir):
        """Test scripts are overwritten with --force flag."""
        from doit_cli.main import app

        # First init
        runner.invoke(
            app, ["init", str(project_dir), "--agent", "claude", "--yes"]
        )

        # Modify a script
        scripts_dir = project_dir / ".doit" / "scripts" / "bash"
        common_sh = scripts_dir / "common.sh"
        custom_content = "#!/bin/bash\n# Custom modification\n"
        common_sh.write_text(custom_content)

        # Init with force
        runner.invoke(
            app, ["init", str(project_dir), "--agent", "claude", "--force", "--yes"]
        )

        # Script should be replaced (not equal to custom content)
        assert common_sh.read_text() != custom_content


class TestInitMemoryFilesPreservation:
    """Tests for memory file preservation during init --update (Issue #542)."""

    def test_update_preserves_memory_files(self, project_dir):
        """Test that --update does NOT overwrite existing memory files.

        Memory files (constitution.md, roadmap.md, completed_roadmap.md) contain
        user-customized project content and should only be overwritten with --force.
        """
        from doit_cli.main import app

        # First init
        runner.invoke(
            app, ["init", str(project_dir), "--agent", "claude", "--yes"]
        )

        # Customize memory files
        memory_dir = project_dir / ".doit" / "memory"
        constitution_file = memory_dir / "constitution.md"
        roadmap_file = memory_dir / "roadmap.md"

        custom_constitution = "# My Custom Constitution\n\nThis is my project's constitution.\n"
        custom_roadmap = "# My Custom Roadmap\n\n## Phase 1\n- Feature A\n"

        constitution_file.write_text(custom_constitution)
        roadmap_file.write_text(custom_roadmap)

        # Run init with --update flag
        result = runner.invoke(
            app, ["init", str(project_dir), "--agent", "claude", "--update", "--yes"]
        )

        assert result.exit_code == 0

        # Memory files should be preserved (not overwritten)
        assert constitution_file.read_text() == custom_constitution, \
            "constitution.md should NOT be overwritten by --update"
        assert roadmap_file.read_text() == custom_roadmap, \
            "roadmap.md should NOT be overwritten by --update"

    def test_force_overwrites_memory_files(self, project_dir):
        """Test that --force DOES overwrite existing memory files."""
        from doit_cli.main import app

        # First init
        runner.invoke(
            app, ["init", str(project_dir), "--agent", "claude", "--yes"]
        )

        # Customize memory files
        memory_dir = project_dir / ".doit" / "memory"
        constitution_file = memory_dir / "constitution.md"

        custom_constitution = "# My Custom Constitution\n\nThis is my project's constitution.\n"
        constitution_file.write_text(custom_constitution)

        # Run init with --force flag
        result = runner.invoke(
            app, ["init", str(project_dir), "--agent", "claude", "--force", "--yes"]
        )

        assert result.exit_code == 0

        # Memory files SHOULD be overwritten with --force
        assert constitution_file.read_text() != custom_constitution, \
            "constitution.md SHOULD be overwritten by --force"

    def test_update_still_updates_command_templates(self, project_dir):
        """Test that --update still updates command templates even while preserving memory."""
        from doit_cli.main import app

        # First init
        runner.invoke(
            app, ["init", str(project_dir), "--agent", "claude", "--yes"]
        )

        # Modify a command template
        command_dir = project_dir / ".claude" / "commands"
        template_files = list(command_dir.glob("doit.*.md"))
        if template_files:
            test_template = template_files[0]
            custom_content = "# Custom Command Template\n"
            test_template.write_text(custom_content, encoding="utf-8")

            # Customize a memory file too
            memory_dir = project_dir / ".doit" / "memory"
            constitution_file = memory_dir / "constitution.md"
            custom_constitution = "# My Custom Constitution\n"
            constitution_file.write_text(custom_constitution, encoding="utf-8")

            # Run update
            result = runner.invoke(
                app, ["init", str(project_dir), "--agent", "claude", "--update", "--yes"]
            )

            assert result.exit_code == 0

            # Command template SHOULD be updated
            assert test_template.read_text(encoding="utf-8") != custom_content, \
                "Command templates should be updated with --update"

            # Memory file should be preserved
            assert constitution_file.read_text(encoding="utf-8") == custom_constitution, \
                "Memory files should be preserved with --update"


class TestInitTechStackCreation:
    """Tests for tech-stack.md creation during init (Feature #046)."""

    def test_init_creates_both_constitution_and_tech_stack(self, project_dir):
        """Test that init creates both constitution.md and tech-stack.md."""
        from doit_cli.main import app

        result = runner.invoke(
            app, ["init", str(project_dir), "--agent", "claude", "--yes"]
        )

        assert result.exit_code == 0

        memory_dir = project_dir / ".doit" / "memory"
        constitution_file = memory_dir / "constitution.md"
        tech_stack_file = memory_dir / "tech-stack.md"

        assert constitution_file.exists(), "constitution.md should be created"
        assert tech_stack_file.exists(), "tech-stack.md should be created"

    def test_constitution_has_cross_reference_to_tech_stack(self, project_dir):
        """Test that constitution.md contains cross-reference to tech-stack.md."""
        from doit_cli.main import app

        runner.invoke(
            app, ["init", str(project_dir), "--agent", "claude", "--yes"]
        )

        memory_dir = project_dir / ".doit" / "memory"
        constitution_file = memory_dir / "constitution.md"
        content = constitution_file.read_text()

        # Check for cross-reference
        assert "tech-stack.md" in content, \
            "constitution.md should reference tech-stack.md"
        assert "See also" in content, \
            "constitution.md should have 'See also' cross-reference"

    def test_tech_stack_has_cross_reference_to_constitution(self, project_dir):
        """Test that tech-stack.md contains cross-reference to constitution.md."""
        from doit_cli.main import app

        runner.invoke(
            app, ["init", str(project_dir), "--agent", "claude", "--yes"]
        )

        memory_dir = project_dir / ".doit" / "memory"
        tech_stack_file = memory_dir / "tech-stack.md"
        content = tech_stack_file.read_text()

        # Check for cross-reference
        assert "constitution.md" in content, \
            "tech-stack.md should reference constitution.md"
        assert "See also" in content, \
            "tech-stack.md should have 'See also' cross-reference"

    def test_tech_stack_has_required_sections(self, project_dir):
        """Test that tech-stack.md contains required sections."""
        from doit_cli.main import app

        runner.invoke(
            app, ["init", str(project_dir), "--agent", "claude", "--yes"]
        )

        memory_dir = project_dir / ".doit" / "memory"
        tech_stack_file = memory_dir / "tech-stack.md"
        content = tech_stack_file.read_text()

        # Check for required sections
        assert "## Tech Stack" in content, "tech-stack.md should have Tech Stack section"
        assert "### Languages" in content, "tech-stack.md should have Languages section"
        assert "### Frameworks" in content, "tech-stack.md should have Frameworks section"
        assert "## Infrastructure" in content, "tech-stack.md should have Infrastructure section"
        assert "## Deployment" in content, "tech-stack.md should have Deployment section"

    def test_constitution_does_not_have_tech_sections(self, project_dir):
        """Test that constitution.md does NOT contain tech stack sections."""
        from doit_cli.main import app

        runner.invoke(
            app, ["init", str(project_dir), "--agent", "claude", "--yes"]
        )

        memory_dir = project_dir / ".doit" / "memory"
        constitution_file = memory_dir / "constitution.md"
        content = constitution_file.read_text()

        # Constitution should NOT have tech-related H2 sections
        assert "## Tech Stack" not in content, \
            "constitution.md should NOT have Tech Stack H2 section"
        assert "## Infrastructure" not in content, \
            "constitution.md should NOT have Infrastructure H2 section"
        assert "## Deployment" not in content, \
            "constitution.md should NOT have Deployment H2 section"

    def test_update_preserves_tech_stack(self, project_dir):
        """Test that --update preserves customized tech-stack.md."""
        from doit_cli.main import app

        # First init
        runner.invoke(
            app, ["init", str(project_dir), "--agent", "claude", "--yes"]
        )

        # Customize tech-stack.md
        memory_dir = project_dir / ".doit" / "memory"
        tech_stack_file = memory_dir / "tech-stack.md"
        custom_tech_stack = "# My Tech Stack\n\n## Languages\nPython 3.11+\n"
        tech_stack_file.write_text(custom_tech_stack)

        # Run init with --update
        result = runner.invoke(
            app, ["init", str(project_dir), "--agent", "claude", "--update", "--yes"]
        )

        assert result.exit_code == 0

        # tech-stack.md should be preserved
        assert tech_stack_file.read_text() == custom_tech_stack, \
            "tech-stack.md should NOT be overwritten by --update"
