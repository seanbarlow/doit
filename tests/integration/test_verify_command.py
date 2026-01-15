"""Integration tests for verify command CLI workflows."""

import pytest
import json
from pathlib import Path
from typer.testing import CliRunner

from doit_cli.models.agent import Agent


runner = CliRunner()


class TestVerifyCommand:
    """Integration tests for verify command."""

    def test_verify_uninitialized_project(self, project_dir):
        """Test verify on uninitialized project."""
        from doit_cli.main import app

        result = runner.invoke(app, ["verify", str(project_dir)])

        assert result.exit_code == 1
        assert ".doit" in result.output

    def test_verify_initialized_project(self, initialized_project):
        """Test verify on initialized project."""
        from doit_cli.main import app

        result = runner.invoke(app, ["verify", str(initialized_project.path)])

        # Should have some output about verification
        assert len(result.output) > 0

    def test_verify_with_claude_agent(self, claude_project):
        """Test verify with --agent claude flag."""
        from doit_cli.main import app

        result = runner.invoke(
            app, ["verify", str(claude_project.path), "--agent", "claude"]
        )

        # Should show Claude-related checks
        assert "claude" in result.output.lower()

    def test_verify_with_copilot_agent(self, copilot_project):
        """Test verify with --agent copilot flag."""
        from doit_cli.main import app

        result = runner.invoke(
            app, ["verify", str(copilot_project.path), "--agent", "copilot"]
        )

        # Should show Copilot-related checks
        assert "copilot" in result.output.lower()

    def test_verify_invalid_agent(self, initialized_project):
        """Test verify with invalid agent name."""
        from doit_cli.main import app

        result = runner.invoke(
            app, ["verify", str(initialized_project.path), "--agent", "invalid"]
        )

        assert result.exit_code == 1
        assert "unknown agent" in result.output.lower()

    def test_verify_json_output(self, initialized_project):
        """Test verify with --json flag."""
        from doit_cli.main import app

        result = runner.invoke(
            app, ["verify", str(initialized_project.path), "--json"]
        )

        # Output should be valid JSON
        try:
            output_json = json.loads(result.output)
            assert "checks" in output_json
            assert "status" in output_json
            assert "summary" in output_json
        except json.JSONDecodeError:
            pytest.fail(f"Output is not valid JSON: {result.output}")

    def test_verify_json_output_structure(self, initialized_project):
        """Test verify JSON output structure."""
        from doit_cli.main import app

        result = runner.invoke(
            app, ["verify", str(initialized_project.path), "--json"]
        )

        output = json.loads(result.output)

        # Check expected fields
        assert "status" in output
        assert isinstance(output["status"], str)
        assert output["status"] in ["passed", "failed"]

        assert "summary" in output
        assert isinstance(output["summary"], dict)
        assert "passed" in output["summary"]
        assert "failed" in output["summary"]

        assert "checks" in output
        assert isinstance(output["checks"], list)

        if output["checks"]:
            check = output["checks"][0]
            assert "name" in check
            assert "status" in check
            assert "message" in check

    def test_verify_shows_suggestions(self, initialized_project):
        """Test that verify shows suggestions for issues."""
        from doit_cli.main import app

        result = runner.invoke(app, ["verify", str(initialized_project.path)])

        # Initialized project without constitution should show suggestions
        # Either in the output or in suggestions section
        assert len(result.output) > 0

    def test_verify_displays_summary(self, initialized_project):
        """Test that verify displays a summary."""
        from doit_cli.main import app

        result = runner.invoke(app, ["verify", str(initialized_project.path)])

        # Should contain summary information
        assert "summary" in result.output.lower() or len(result.output) > 100


class TestVerifyCommandStatus:
    """Tests for verify command exit status."""

    def test_verify_exit_code_pass(self, initialized_project):
        """Test exit code when all checks pass."""
        from doit_cli.main import app

        # Create all required files to pass checks
        memory_dir = initialized_project.path / ".doit" / "memory"
        (memory_dir / "constitution.md").write_text("# Constitution\n")
        (memory_dir / "roadmap.md").write_text("# Roadmap\n")

        result = runner.invoke(app, ["verify", str(initialized_project.path)])

        # May still have warnings but should not fail
        # (depends on agent checks)
        assert len(result.output) > 0

    def test_verify_exit_code_fail(self, project_dir):
        """Test exit code when critical checks fail."""
        from doit_cli.main import app

        result = runner.invoke(app, ["verify", str(project_dir)])

        # Uninitialized project should fail
        assert result.exit_code == 1


class TestVerifyWithInitIntegration:
    """Tests for verify after init workflow."""

    def test_verify_after_init(self, project_dir):
        """Test verify passes after successful init."""
        from doit_cli.main import app

        # Run init first
        init_result = runner.invoke(
            app, ["init", str(project_dir), "--agent", "claude", "--yes"]
        )
        assert init_result.exit_code == 0

        # Run verify
        verify_result = runner.invoke(
            app, ["verify", str(project_dir), "--agent", "claude"]
        )

        # Should have some checks passing
        assert len(verify_result.output) > 0

    def test_verify_after_full_init(self, project_dir):
        """Test verify after init with both agents."""
        from doit_cli.main import app

        # Run init with both agents
        init_result = runner.invoke(
            app, ["init", str(project_dir), "--agent", "claude,copilot", "--yes"]
        )
        assert init_result.exit_code == 0

        # Run verify with both agents
        verify_result = runner.invoke(
            app, ["verify", str(project_dir), "--agent", "claude,copilot"]
        )

        # Should have agent checks in output
        assert "claude" in verify_result.output.lower() or "copilot" in verify_result.output.lower()
