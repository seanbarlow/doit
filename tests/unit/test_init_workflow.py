"""Unit tests for InitWorkflow factory and helpers.

Tests for Feature 031: Init Workflow Integration
"""

import pytest
from pathlib import Path

from doit_cli.cli.init_command import (
    create_init_workflow,
    map_workflow_responses,
)
from doit_cli.models.agent import Agent


class TestCreateInitWorkflow:
    """Test the create_init_workflow factory function."""

    def test_creates_workflow_with_three_steps(self):
        """InitWorkflow must have exactly 3 steps."""
        workflow = create_init_workflow(Path("."))
        assert len(workflow.steps) == 3

    def test_workflow_has_correct_id(self):
        """Workflow must have id 'init-workflow'."""
        workflow = create_init_workflow(Path("."))
        assert workflow.id == "init-workflow"

    def test_workflow_command_name_is_init(self):
        """Workflow command_name must be 'init'."""
        workflow = create_init_workflow(Path("."))
        assert workflow.command_name == "init"

    def test_step_ids_are_unique(self):
        """Step IDs must be unique within workflow."""
        workflow = create_init_workflow(Path("."))
        ids = [s.id for s in workflow.steps]
        assert len(ids) == len(set(ids))

    def test_step_order_is_sequential(self):
        """Steps must have order 0, 1, 2."""
        workflow = create_init_workflow(Path("."))
        orders = sorted([s.order for s in workflow.steps])
        assert orders == [0, 1, 2]

    def test_first_step_is_agent_selection(self):
        """First step (order=0) must be agent selection."""
        workflow = create_init_workflow(Path("."))
        step = workflow.get_step_by_order(0)
        assert step is not None
        assert step.id == "select-agent"
        assert "claude" in step.options
        assert "copilot" in step.options
        assert "both" in step.options

    def test_second_step_is_path_confirmation(self):
        """Second step (order=1) must be path confirmation."""
        workflow = create_init_workflow(Path("."))
        step = workflow.get_step_by_order(1)
        assert step is not None
        assert step.id == "confirm-path"
        assert "yes" in step.options
        assert "no" in step.options

    def test_third_step_is_custom_templates(self):
        """Third step (order=2) must be custom templates."""
        workflow = create_init_workflow(Path("."))
        step = workflow.get_step_by_order(2)
        assert step is not None
        assert step.id == "custom-templates"
        assert step.required is False

    def test_path_included_in_confirm_prompt(self):
        """Path confirmation prompt must include the actual path."""
        test_path = Path("/test/project/path")
        workflow = create_init_workflow(test_path)
        step = workflow.get_step_by_order(1)
        assert "/test/project/path" in step.prompt_text

    def test_agent_selection_has_valid_options(self):
        """Agent step must have claude, copilot, both options."""
        workflow = create_init_workflow(Path("."))
        step = workflow.get_step_by_id("select-agent")
        assert step is not None
        assert set(step.options.keys()) == {"claude", "copilot", "both"}

    def test_optional_step_has_default(self):
        """custom-templates step must have empty default."""
        workflow = create_init_workflow(Path("."))
        step = workflow.get_step_by_id("custom-templates")
        assert step is not None
        assert step.default_value == ""

    def test_required_steps_are_marked_required(self):
        """Agent selection and path confirmation must be required."""
        workflow = create_init_workflow(Path("."))
        agent_step = workflow.get_step_by_id("select-agent")
        path_step = workflow.get_step_by_id("confirm-path")
        assert agent_step.required is True
        assert path_step.required is True


class TestMapWorkflowResponses:
    """Test the map_workflow_responses helper function."""

    def test_maps_claude_agent(self):
        """'claude' response maps to Claude agent."""
        responses = {
            "select-agent": "claude",
            "confirm-path": "yes",
            "custom-templates": "",
        }
        agents, templates = map_workflow_responses(responses)
        assert agents == [Agent.CLAUDE]

    def test_maps_copilot_agent(self):
        """'copilot' response maps to Copilot agent."""
        responses = {
            "select-agent": "copilot",
            "confirm-path": "yes",
            "custom-templates": "",
        }
        agents, templates = map_workflow_responses(responses)
        assert agents == [Agent.COPILOT]

    def test_maps_both_agents(self):
        """'both' response maps to both agents."""
        responses = {
            "select-agent": "both",
            "confirm-path": "yes",
            "custom-templates": "",
        }
        agents, templates = map_workflow_responses(responses)
        assert Agent.CLAUDE in agents
        assert Agent.COPILOT in agents

    def test_empty_template_returns_none(self):
        """Empty template response returns None."""
        responses = {
            "select-agent": "claude",
            "confirm-path": "yes",
            "custom-templates": "",
        }
        agents, templates = map_workflow_responses(responses)
        assert templates is None

    def test_template_path_is_converted(self):
        """Non-empty template response is converted to Path."""
        responses = {
            "select-agent": "claude",
            "confirm-path": "yes",
            "custom-templates": "/custom/templates",
        }
        agents, templates = map_workflow_responses(responses)
        assert templates == Path("/custom/templates")

    def test_confirm_no_raises_exit(self):
        """confirm-path 'no' raises typer.Exit."""
        import typer

        responses = {
            "select-agent": "claude",
            "confirm-path": "no",
            "custom-templates": "",
        }
        with pytest.raises(typer.Exit) as exc_info:
            map_workflow_responses(responses)
        assert exc_info.value.exit_code == 0
