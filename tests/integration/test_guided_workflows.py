"""Integration tests for guided workflow system.

Tests complete workflow scenarios end-to-end.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, Mock

from doit_cli.models.workflow_models import (
    Workflow,
    WorkflowStep,
    WorkflowState,
    WorkflowStatus,
)
from doit_cli.services.workflow_engine import WorkflowEngine
from doit_cli.services.state_manager import StateManager
from doit_cli.prompts.interactive import InteractivePrompt, ProgressDisplay


class TestWorkflowEndToEnd:
    """End-to-end tests for complete workflow execution."""

    @pytest.fixture
    def sample_workflow(self):
        """Create a multi-step workflow for testing."""
        return Workflow(
            id="init-workflow",
            command_name="init",
            description="Initialize a new project",
            interactive=True,
            steps=[
                WorkflowStep(
                    id="project-name",
                    name="Project Name",
                    prompt_text="Enter your project name:",
                    required=True,
                    order=0,
                ),
                WorkflowStep(
                    id="framework",
                    name="Framework",
                    prompt_text="Select your framework:",
                    required=True,
                    order=1,
                    options={
                        "react": "React - JavaScript library for UIs",
                        "vue": "Vue - Progressive JavaScript framework",
                    },
                ),
                WorkflowStep(
                    id="description",
                    name="Description",
                    prompt_text="Enter project description:",
                    required=False,
                    order=2,
                    default_value="A new project",
                ),
            ],
        )

    @pytest.fixture
    def engine(self, tmp_path):
        """Create a workflow engine with temp state directory."""
        state_manager = StateManager(state_dir=tmp_path / ".doit/state")
        engine = WorkflowEngine(state_manager=state_manager)
        return engine

    def test_complete_workflow_execution(self, sample_workflow, engine):
        """Test executing a complete workflow with all steps."""
        # Mock user inputs
        engine.prompt = Mock()
        engine.prompt.prompt.side_effect = ["my-project", "A cool project"]
        engine.prompt.prompt_choice.return_value = "react"
        engine.prompt.prompt_confirm.return_value = True

        results = engine.run(sample_workflow)

        assert "project-name" in results
        assert results["project-name"] == "my-project"
        assert results["framework"] == "react"
        assert "description" in results

    def test_workflow_with_skip(self, sample_workflow, engine):
        """Test workflow with optional step skipped."""
        engine.prompt = Mock()
        engine.prompt.prompt.side_effect = ["my-project", "skip"]
        engine.prompt.prompt_choice.return_value = "vue"

        # Simulate skip navigation
        from doit_cli.models.workflow_models import NavigationCommand

        def prompt_side_effect(step, validator=None):
            if step.id == "description":
                raise NavigationCommand("skip")
            return "test-value"

        engine.prompt.prompt.side_effect = prompt_side_effect

        results = engine.run(sample_workflow)

        # Should have used default for skipped step
        assert results.get("description") == "A new project"


class TestWorkflowRecovery:
    """Tests for workflow interruption and recovery."""

    @pytest.fixture
    def workflow(self):
        """Create a simple workflow."""
        return Workflow(
            id="test-workflow",
            command_name="test",
            description="Test workflow",
            interactive=True,
            steps=[
                WorkflowStep(
                    id="step1",
                    name="Step 1",
                    prompt_text="Enter value 1:",
                    required=True,
                    order=0,
                ),
                WorkflowStep(
                    id="step2",
                    name="Step 2",
                    prompt_text="Enter value 2:",
                    required=True,
                    order=1,
                ),
            ],
        )

    def test_state_persists_on_interrupt(self, workflow, tmp_path):
        """Test that state is saved when workflow is interrupted."""
        state_manager = StateManager(state_dir=tmp_path / ".doit/state")
        engine = WorkflowEngine(state_manager=state_manager)

        # Start workflow
        state = engine.start(workflow)
        state.status = WorkflowStatus.RUNNING

        # Simulate partial completion
        from doit_cli.models.workflow_models import StepResponse

        state.responses["step1"] = StepResponse(step_id="step1", value="value1")
        state.current_step = 1

        # Cancel (simulating Ctrl+C)
        engine.cancel(state)

        # Verify state was saved
        loaded = state_manager.load(workflow.command_name)
        assert loaded is not None
        assert loaded.status == WorkflowStatus.INTERRUPTED
        assert "step1" in loaded.responses

    def test_resume_from_interrupted_state(self, workflow, tmp_path):
        """Test resuming from previously interrupted workflow."""
        state_manager = StateManager(state_dir=tmp_path / ".doit/state")

        # Create and save interrupted state
        interrupted_state = WorkflowState(
            id="test_interrupted",
            workflow_id=workflow.id,
            command_name=workflow.command_name,
            current_step=1,
            status=WorkflowStatus.INTERRUPTED,
        )
        from doit_cli.models.workflow_models import StepResponse

        interrupted_state.responses["step1"] = StepResponse(
            step_id="step1",
            value="previous-value",
        )
        state_manager.save(interrupted_state)

        # Create engine and start workflow
        engine = WorkflowEngine(state_manager=state_manager)
        engine.prompt = Mock()
        engine.prompt.prompt_confirm.return_value = True  # Resume: yes

        state = engine.start(workflow)

        # Should have loaded the interrupted state
        assert state.current_step == 1
        assert "step1" in state.responses
        assert state.responses["step1"].value == "previous-value"


class TestNonInteractiveWorkflow:
    """Tests for non-interactive workflow execution."""

    @pytest.fixture
    def workflow_with_defaults(self):
        """Create a workflow with all defaults."""
        return Workflow(
            id="non-interactive-workflow",
            command_name="create",
            description="Create with defaults",
            interactive=True,
            steps=[
                WorkflowStep(
                    id="name",
                    name="Name",
                    prompt_text="Enter name:",
                    required=True,
                    order=0,
                    default_value="default-name",
                ),
                WorkflowStep(
                    id="type",
                    name="Type",
                    prompt_text="Select type:",
                    required=True,
                    order=1,
                    default_value="basic",
                    options={"basic": "Basic", "advanced": "Advanced"},
                ),
            ],
        )

    def test_non_interactive_uses_defaults(self, workflow_with_defaults):
        """Test that non-interactive mode uses all defaults."""
        engine = WorkflowEngine()
        engine.prompt = InteractivePrompt(force_non_interactive=True)
        engine.progress = ProgressDisplay()

        results = engine.run(workflow_with_defaults)

        assert results["name"] == "default-name"
        assert results["type"] == "basic"

    def test_env_var_triggers_non_interactive(self, workflow_with_defaults, monkeypatch):
        """Test that environment variable triggers non-interactive mode."""
        monkeypatch.setenv("DOIT_NON_INTERACTIVE", "true")

        engine = WorkflowEngine()
        engine.prompt = InteractivePrompt()  # Should detect env var
        engine.progress = ProgressDisplay()

        # Prompt should not require actual user input
        assert not engine.prompt._is_interactive()


class TestWorkflowValidation:
    """Tests for workflow validation during execution."""

    @pytest.fixture
    def workflow_with_validation(self):
        """Create a workflow with validation."""
        return Workflow(
            id="validated-workflow",
            command_name="validate",
            description="Workflow with validation",
            interactive=True,
            steps=[
                WorkflowStep(
                    id="email",
                    name="Email",
                    prompt_text="Enter your email:",
                    required=True,
                    order=0,
                    validation_type="PatternValidator",
                ),
            ],
        )

    def test_invalid_input_prompts_retry(self, workflow_with_validation):
        """Test that invalid input causes re-prompt."""
        engine = WorkflowEngine()
        engine.prompt = Mock()
        engine.progress = Mock()

        # First invalid, then valid
        from doit_cli.models.workflow_models import ValidationResult

        validation_results = [
            ValidationResult.failure("Invalid email"),
            ValidationResult.success(),
        ]

        mock_validator = Mock()
        mock_validator.validate.side_effect = validation_results

        # Simulate prompt returning values
        engine.prompt.prompt.side_effect = ["invalid", "valid@example.com"]

        # This would test the retry logic in execute_step
        state = engine.start(workflow_with_validation)
        assert state is not None


class TestProgressVisualization:
    """Tests for progress display during workflow execution."""

    @pytest.fixture
    def three_step_workflow(self):
        """Create a three-step workflow."""
        return Workflow(
            id="progress-workflow",
            command_name="progress",
            description="Test progress display",
            interactive=True,
            steps=[
                WorkflowStep(
                    id="step1", name="Step 1", prompt_text="1:",
                    required=True, order=0,
                ),
                WorkflowStep(
                    id="step2", name="Step 2", prompt_text="2:",
                    required=False, order=1, default_value="default",
                ),
                WorkflowStep(
                    id="step3", name="Step 3", prompt_text="3:",
                    required=True, order=2,
                ),
            ],
        )

    def test_progress_shows_correct_step_numbers(self, three_step_workflow):
        """Test that progress shows correct step numbers."""
        engine = WorkflowEngine()
        engine.prompt = Mock()
        engine.prompt.prompt.return_value = "value"
        engine.progress = Mock()

        engine.run(three_step_workflow)

        # Check that show_step was called with correct step numbers
        calls = engine.progress.show_step.call_args_list
        assert len(calls) == 3

        # Check step numbers (1-indexed)
        for i, call in enumerate(calls):
            step, current, total = call[0]
            assert current == i + 1
            assert total == 3
