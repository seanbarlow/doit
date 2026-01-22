"""Unit tests for WorkflowEngine class.

Tests the workflow orchestration functionality for guided workflows.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from doit_cli.models.workflow_models import (
    Workflow,
    WorkflowStep,
    WorkflowState,
    WorkflowStatus,
    StepResponse,
    NavigationCommand,
)


class TestWorkflowEngineStart:
    """Tests for WorkflowEngine.start() method."""

    @pytest.fixture
    def engine(self):
        """Create a WorkflowEngine instance."""
        from doit_cli.services.workflow_engine import WorkflowEngine

        return WorkflowEngine()

    @pytest.fixture
    def simple_workflow(self):
        """Create a simple two-step workflow."""
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
                    required=False,
                    order=1,
                    default_value="default",
                ),
            ],
        )

    def test_start_creates_new_state(self, engine, simple_workflow):
        """Test that start creates a new WorkflowState."""
        state = engine.start(simple_workflow)

        assert state is not None
        assert state.workflow_id == simple_workflow.id
        assert state.command_name == simple_workflow.command_name
        assert state.current_step == 0
        assert state.status == WorkflowStatus.PENDING

    def test_start_generates_unique_state_id(self, engine, simple_workflow):
        """Test that state IDs are unique."""
        state1 = engine.start(simple_workflow)
        state2 = engine.start(simple_workflow)

        # State IDs should contain command name and timestamp
        assert simple_workflow.command_name in state1.id
        assert simple_workflow.command_name in state2.id

    def test_start_with_state_manager_checks_for_interrupted(self, engine, simple_workflow):
        """Test that start checks for interrupted state when manager provided."""
        mock_manager = Mock()
        mock_manager.load.return_value = None

        engine.state_manager = mock_manager
        engine.start(simple_workflow)

        mock_manager.load.assert_called_once_with(simple_workflow.command_name)

    def test_start_prompts_resume_for_interrupted_state(self, engine, simple_workflow):
        """Test that user is prompted to resume interrupted workflow."""
        mock_manager = Mock()
        interrupted_state = WorkflowState(
            id="old_state",
            workflow_id=simple_workflow.id,
            command_name=simple_workflow.command_name,
            status=WorkflowStatus.INTERRUPTED,
        )
        mock_manager.load.return_value = interrupted_state

        engine.state_manager = mock_manager

        with patch.object(engine, "_prompt_resume", return_value=True) as mock_prompt:
            state = engine.start(simple_workflow)
            mock_prompt.assert_called_once_with(interrupted_state)
            assert state.id == "old_state"
            assert state.status == WorkflowStatus.RUNNING


class TestWorkflowEngineExecuteStep:
    """Tests for WorkflowEngine.execute_step() method."""

    @pytest.fixture
    def engine(self):
        """Create a WorkflowEngine instance."""
        from doit_cli.services.workflow_engine import WorkflowEngine

        engine = WorkflowEngine()
        # Mock the prompt to avoid actual user input
        engine.prompt = Mock()
        engine.progress = Mock()
        return engine

    @pytest.fixture
    def state(self):
        """Create a workflow state."""
        return WorkflowState(
            id="test_state",
            workflow_id="test-workflow",
            command_name="test",
        )

    @pytest.fixture
    def text_step(self):
        """Create a text input step."""
        return WorkflowStep(
            id="name",
            name="Project Name",
            prompt_text="Enter name:",
            required=True,
            order=0,
        )

    @pytest.fixture
    def choice_step(self):
        """Create a choice step."""
        return WorkflowStep(
            id="framework",
            name="Framework",
            prompt_text="Select framework:",
            required=True,
            order=1,
            options={"react": "React", "vue": "Vue"},
        )

    def test_execute_step_updates_status_to_running(self, engine, state, text_step):
        """Test that first step changes status from pending to running."""
        engine.prompt.prompt.return_value = "test-value"

        updated_state, response = engine.execute_step(state, text_step)

        assert updated_state.status == WorkflowStatus.RUNNING

    def test_execute_step_returns_response(self, engine, state, text_step):
        """Test that execute_step returns the user's response."""
        engine.prompt.prompt.return_value = "my-project"

        updated_state, response = engine.execute_step(state, text_step)

        assert response.step_id == text_step.id
        assert response.value == "my-project"
        assert response.skipped is False

    def test_execute_step_advances_current_step(self, engine, state, text_step):
        """Test that current_step is incremented after execution."""
        engine.prompt.prompt.return_value = "value"
        initial_step = state.current_step

        updated_state, response = engine.execute_step(state, text_step)

        assert updated_state.current_step == initial_step + 1

    def test_execute_step_stores_response_in_state(self, engine, state, text_step):
        """Test that response is stored in state."""
        engine.prompt.prompt.return_value = "stored-value"

        updated_state, response = engine.execute_step(state, text_step)

        assert text_step.id in updated_state.responses
        assert updated_state.responses[text_step.id].value == "stored-value"

    def test_execute_step_uses_choice_prompt_for_options(self, engine, state, choice_step):
        """Test that choice steps use prompt_choice."""
        engine.prompt.prompt_choice.return_value = "react"

        updated_state, response = engine.execute_step(state, choice_step)

        engine.prompt.prompt_choice.assert_called_once()
        assert response.value == "react"

    def test_execute_step_shows_progress(self, engine, state, text_step):
        """Test that progress is displayed."""
        engine.prompt.prompt.return_value = "value"

        engine.execute_step(state, text_step)

        engine.progress.show_step.assert_called_once()
        engine.progress.mark_complete.assert_called_once_with(text_step)


class TestWorkflowEngineNavigation:
    """Tests for back/skip navigation handling."""

    @pytest.fixture
    def engine(self):
        """Create a WorkflowEngine instance."""
        from doit_cli.services.workflow_engine import WorkflowEngine

        engine = WorkflowEngine()
        engine.prompt = Mock()
        engine.progress = Mock()
        return engine

    @pytest.fixture
    def workflow_steps(self):
        """Create multiple workflow steps."""
        return [
            WorkflowStep(
                id="step1",
                name="Step 1",
                prompt_text="Enter 1:",
                required=True,
                order=0,
            ),
            WorkflowStep(
                id="step2",
                name="Step 2",
                prompt_text="Enter 2:",
                required=False,
                order=1,
                default_value="default2",
            ),
            WorkflowStep(
                id="step3",
                name="Step 3",
                prompt_text="Enter 3:",
                required=True,
                order=2,
            ),
        ]

    def test_go_back_decrements_current_step(self, engine, workflow_steps):
        """Test that going back decreases the step index."""
        state = WorkflowState(
            id="test",
            workflow_id="test",
            command_name="test",
            current_step=1,
        )

        nav = NavigationCommand("back")
        updated = engine._handle_navigation(state, nav, workflow_steps)

        assert updated.current_step == 0

    def test_go_back_at_first_step_stays_at_zero(self, engine, workflow_steps):
        """Test that going back at first step doesn't go negative."""
        state = WorkflowState(
            id="test",
            workflow_id="test",
            command_name="test",
            current_step=0,
        )

        nav = NavigationCommand("back")
        updated = engine._handle_navigation(state, nav, workflow_steps)

        assert updated.current_step == 0

    def test_skip_optional_step_uses_default(self, engine, workflow_steps):
        """Test that skipping optional step uses default value."""
        state = WorkflowState(
            id="test",
            workflow_id="test",
            command_name="test",
            current_step=1,  # Optional step
        )

        nav = NavigationCommand("skip")
        updated = engine._handle_navigation(state, nav, workflow_steps)

        assert "step2" in updated.responses
        assert updated.responses["step2"].value == "default2"
        assert updated.responses["step2"].skipped is True

    def test_skip_required_step_fails(self, engine, workflow_steps):
        """Test that skipping required step doesn't advance."""
        state = WorkflowState(
            id="test",
            workflow_id="test",
            command_name="test",
            current_step=0,  # Required step
        )

        nav = NavigationCommand("skip")
        updated = engine._handle_navigation(state, nav, workflow_steps)

        # Should not have advanced
        assert updated.current_step == 0
        assert "step1" not in updated.responses


class TestWorkflowEngineComplete:
    """Tests for WorkflowEngine.complete() method."""

    @pytest.fixture
    def engine(self):
        """Create a WorkflowEngine instance."""
        from doit_cli.services.workflow_engine import WorkflowEngine

        engine = WorkflowEngine()
        engine.progress = Mock()
        return engine

    def test_complete_returns_response_dict(self, engine):
        """Test that complete returns step_id -> value mapping."""
        state = WorkflowState(
            id="test",
            workflow_id="test",
            command_name="test",
        )
        state.responses = {
            "step1": StepResponse(step_id="step1", value="value1"),
            "step2": StepResponse(step_id="step2", value="value2"),
        }

        result = engine.complete(state)

        assert result == {"step1": "value1", "step2": "value2"}

    def test_complete_sets_status_to_completed(self, engine):
        """Test that complete sets status to COMPLETED."""
        state = WorkflowState(
            id="test",
            workflow_id="test",
            command_name="test",
            status=WorkflowStatus.RUNNING,
        )

        engine.complete(state)

        assert state.status == WorkflowStatus.COMPLETED

    def test_complete_deletes_state_file(self, engine):
        """Test that state file is deleted on completion."""
        mock_manager = Mock()
        engine.state_manager = mock_manager

        state = WorkflowState(
            id="test",
            workflow_id="test",
            command_name="test",
        )

        engine.complete(state)

        mock_manager.delete.assert_called_once_with(state)

    def test_complete_shows_summary(self, engine):
        """Test that completion summary is shown."""
        state = WorkflowState(
            id="test",
            workflow_id="test",
            command_name="test",
        )
        state.responses = {"step1": StepResponse(step_id="step1", value="v")}

        engine.complete(state)

        engine.progress.show_summary.assert_called_once()


class TestWorkflowEngineCancel:
    """Tests for WorkflowEngine.cancel() method."""

    @pytest.fixture
    def engine(self):
        """Create a WorkflowEngine instance."""
        from doit_cli.services.workflow_engine import WorkflowEngine

        engine = WorkflowEngine()
        engine.progress = Mock()
        return engine

    def test_cancel_sets_status_to_interrupted(self, engine):
        """Test that cancel sets status to INTERRUPTED."""
        state = WorkflowState(
            id="test",
            workflow_id="test",
            command_name="test",
            status=WorkflowStatus.RUNNING,
        )

        engine.cancel(state)

        assert state.status == WorkflowStatus.INTERRUPTED

    def test_cancel_saves_state(self, engine):
        """Test that state is saved for resume."""
        mock_manager = Mock()
        engine.state_manager = mock_manager

        state = WorkflowState(
            id="test",
            workflow_id="test",
            command_name="test",
        )

        engine.cancel(state)

        mock_manager.save.assert_called_once_with(state)

    def test_cancel_shows_interrupted_message(self, engine):
        """Test that interrupted message is shown."""
        state = WorkflowState(
            id="test",
            workflow_id="test",
            command_name="test",
            current_step=2,
        )

        engine.cancel(state)

        engine.progress.show_interrupted.assert_called_once()


class TestWorkflowEngineRun:
    """Tests for WorkflowEngine.run() - full workflow execution."""

    @pytest.fixture
    def engine(self):
        """Create a WorkflowEngine instance."""
        from doit_cli.services.workflow_engine import WorkflowEngine

        engine = WorkflowEngine()
        engine.prompt = Mock()
        engine.progress = Mock()
        return engine

    @pytest.fixture
    def simple_workflow(self):
        """Create a simple workflow."""
        return Workflow(
            id="test-workflow",
            command_name="test",
            description="Test",
            interactive=True,
            steps=[
                WorkflowStep(
                    id="step1",
                    name="Step 1",
                    prompt_text="Enter:",
                    required=True,
                    order=0,
                ),
            ],
        )

    def test_run_executes_all_steps(self, engine, simple_workflow):
        """Test that run executes all steps."""
        engine.prompt.prompt.return_value = "value"

        result = engine.run(simple_workflow)

        assert "step1" in result
        assert result["step1"] == "value"

    def test_run_returns_all_responses(self, engine):
        """Test that run returns all step responses."""
        workflow = Workflow(
            id="test",
            command_name="test",
            description="Test",
            interactive=True,
            steps=[
                WorkflowStep(id="a", name="A", prompt_text="A:", required=True, order=0),
                WorkflowStep(id="b", name="B", prompt_text="B:", required=True, order=1),
            ],
        )

        engine.prompt.prompt.side_effect = ["val_a", "val_b"]

        result = engine.run(workflow)

        assert result == {"a": "val_a", "b": "val_b"}
