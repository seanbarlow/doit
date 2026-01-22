"""Integration tests for init workflow.

Tests for Feature 031: Init Workflow Integration
"""

import pytest
from pathlib import Path
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

from doit_cli.main import app


runner = CliRunner()


class TestInitWorkflowIntegration:
    """Integration tests for init command with workflow."""

    def test_non_interactive_skips_prompts(self, tmp_path):
        """doit init . --yes must not show prompts."""
        result = runner.invoke(app, ["init", str(tmp_path), "--yes"])
        assert result.exit_code == 0
        # Non-interactive mode should not show step progress
        assert "Step 1/3" not in result.output
        assert "Step 2/3" not in result.output
        assert "Step 3/3" not in result.output

    def test_non_interactive_creates_structure(self, tmp_path):
        """doit init . --yes must create .doit directory."""
        result = runner.invoke(app, ["init", str(tmp_path), "--yes"])
        assert result.exit_code == 0
        assert (tmp_path / ".doit").exists()

    def test_non_interactive_with_agent_flag(self, tmp_path):
        """doit init . --yes --agent copilot must use specified agent."""
        result = runner.invoke(
            app, ["init", str(tmp_path), "--yes", "--agent", "copilot"]
        )
        assert result.exit_code == 0
        # Should create copilot directory
        assert (tmp_path / ".github" / "prompts").exists()

    def test_non_interactive_with_both_agents(self, tmp_path):
        """doit init . --yes -a claude,copilot must create both."""
        result = runner.invoke(
            app, ["init", str(tmp_path), "--yes", "--agent", "claude,copilot"]
        )
        assert result.exit_code == 0
        assert (tmp_path / ".claude" / "commands").exists()
        assert (tmp_path / ".github" / "prompts").exists()

    @patch("doit_cli.cli.init_command.WorkflowEngine")
    def test_interactive_uses_workflow_engine(self, mock_engine_class, tmp_path):
        """Interactive init must use WorkflowEngine."""
        # Setup mock
        mock_engine = MagicMock()
        mock_engine.run.return_value = {
            "select-agent": "claude",
            "confirm-path": "yes",
            "custom-templates": "",
        }
        mock_engine_class.return_value = mock_engine

        # Run without --yes (interactive)
        result = runner.invoke(app, ["init", str(tmp_path)])

        # Verify WorkflowEngine was used
        mock_engine_class.assert_called_once()
        mock_engine.run.assert_called_once()

    @patch("doit_cli.cli.init_command.WorkflowEngine")
    def test_workflow_responses_map_to_init(self, mock_engine_class, tmp_path):
        """Workflow responses must map correctly to init parameters."""
        # Setup mock to return both agents
        mock_engine = MagicMock()
        mock_engine.run.return_value = {
            "select-agent": "both",
            "confirm-path": "yes",
            "custom-templates": "",
        }
        mock_engine_class.return_value = mock_engine

        result = runner.invoke(app, ["init", str(tmp_path)])

        # Both agent directories should be created
        assert result.exit_code == 0
        assert (tmp_path / ".claude" / "commands").exists()
        assert (tmp_path / ".github" / "prompts").exists()

    @patch("doit_cli.cli.init_command.WorkflowEngine")
    def test_workflow_cancel_exits_gracefully(self, mock_engine_class, tmp_path):
        """confirm-path 'no' must exit with code 0."""
        mock_engine = MagicMock()
        mock_engine.run.return_value = {
            "select-agent": "claude",
            "confirm-path": "no",
            "custom-templates": "",
        }
        mock_engine_class.return_value = mock_engine

        result = runner.invoke(app, ["init", str(tmp_path)])

        # Should exit gracefully
        assert result.exit_code == 0
        assert "cancelled" in result.output.lower()

    @patch("doit_cli.cli.init_command.WorkflowEngine")
    def test_cli_agent_overrides_workflow(self, mock_engine_class, tmp_path):
        """CLI --agent flag must override workflow selection."""
        mock_engine = MagicMock()
        mock_engine.run.return_value = {
            "select-agent": "copilot",  # Workflow selected copilot
            "confirm-path": "yes",
            "custom-templates": "",
        }
        mock_engine_class.return_value = mock_engine

        # CLI specifies claude
        result = runner.invoke(
            app, ["init", str(tmp_path), "--agent", "claude"]
        )

        assert result.exit_code == 0
        # CLI agent should win
        assert (tmp_path / ".claude" / "commands").exists()


class TestInitWorkflowStateRecovery:
    """Tests for workflow state persistence and recovery."""

    @patch("doit_cli.cli.init_command.WorkflowEngine")
    def test_keyboard_interrupt_exits_130(self, mock_engine_class, tmp_path):
        """Ctrl+C during workflow must exit with code 130."""
        mock_engine = MagicMock()
        mock_engine.run.side_effect = KeyboardInterrupt()
        mock_engine_class.return_value = mock_engine

        result = runner.invoke(app, ["init", str(tmp_path)])

        # Should exit with 130 (128 + SIGINT)
        assert result.exit_code == 130


class TestInitWorkflowProgressDisplay:
    """Tests for progress display during workflow."""

    @patch("doit_cli.cli.init_command.WorkflowEngine")
    @patch("doit_cli.cli.init_command.create_init_workflow")
    def test_workflow_created_with_correct_path(
        self, mock_create_workflow, mock_engine_class, tmp_path
    ):
        """create_init_workflow must receive the correct path."""
        from doit_cli.models.workflow_models import Workflow, WorkflowStep

        # Create a minimal valid workflow
        mock_workflow = Workflow(
            id="test",
            command_name="init",
            description="Test",
            interactive=True,
            steps=[
                WorkflowStep(
                    id="test-step",
                    name="Test",
                    prompt_text="Test?",
                    required=True,
                    order=0,
                    default_value="yes",
                    options={"yes": "Yes", "no": "No"},
                )
            ],
        )
        mock_create_workflow.return_value = mock_workflow

        mock_engine = MagicMock()
        mock_engine.run.return_value = {
            "test-step": "yes",
        }
        mock_engine_class.return_value = mock_engine

        runner.invoke(app, ["init", str(tmp_path)])

        # Verify path was passed to workflow factory
        mock_create_workflow.assert_called_once()
        call_args = mock_create_workflow.call_args
        assert str(tmp_path) in str(call_args)
