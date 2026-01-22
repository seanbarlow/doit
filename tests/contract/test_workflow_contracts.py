"""Contract tests for workflow API compliance.

These tests verify that implementations conform to the defined protocols.
"""

import pytest
from typing import Protocol

from doit_cli.models.workflow_models import (
    Workflow,
    WorkflowStep,
    WorkflowState,
    WorkflowStatus,
    StepResponse,
    ValidationResult,
)


class TestWorkflowEngineContract:
    """Tests verifying WorkflowEngine API compliance."""

    @pytest.fixture
    def engine(self):
        """Create a WorkflowEngine instance."""
        from doit_cli.services.workflow_engine import WorkflowEngine

        return WorkflowEngine()

    @pytest.fixture
    def workflow(self):
        """Create a minimal workflow."""
        return Workflow(
            id="contract-test",
            command_name="test",
            description="Contract test workflow",
            interactive=True,
            steps=[
                WorkflowStep(
                    id="step1",
                    name="Step 1",
                    prompt_text="Enter:",
                    required=False,
                    order=0,
                    default_value="default",
                ),
            ],
        )

    def test_start_returns_workflow_state(self, engine, workflow):
        """Contract: start() must return a WorkflowState."""
        state = engine.start(workflow)

        assert isinstance(state, WorkflowState)

    def test_start_sets_workflow_id(self, engine, workflow):
        """Contract: start() must set workflow_id in state."""
        state = engine.start(workflow)

        assert state.workflow_id == workflow.id

    def test_start_sets_command_name(self, engine, workflow):
        """Contract: start() must set command_name in state."""
        state = engine.start(workflow)

        assert state.command_name == workflow.command_name

    def test_start_sets_status_pending(self, engine, workflow):
        """Contract: start() must set initial status to PENDING."""
        state = engine.start(workflow)

        assert state.status == WorkflowStatus.PENDING

    def test_complete_returns_response_dict(self, engine, workflow):
        """Contract: complete() must return dict of step_id -> value."""
        state = WorkflowState(
            id="test",
            workflow_id=workflow.id,
            command_name=workflow.command_name,
        )
        state.responses["step1"] = StepResponse(
            step_id="step1",
            value="test-value",
        )

        result = engine.complete(state)

        assert isinstance(result, dict)
        assert "step1" in result
        assert result["step1"] == "test-value"

    def test_complete_sets_status_completed(self, engine, workflow):
        """Contract: complete() must set status to COMPLETED."""
        state = WorkflowState(
            id="test",
            workflow_id=workflow.id,
            command_name=workflow.command_name,
        )

        engine.complete(state)

        assert state.status == WorkflowStatus.COMPLETED

    def test_cancel_sets_status_interrupted(self, engine, workflow):
        """Contract: cancel() must set status to INTERRUPTED."""
        state = WorkflowState(
            id="test",
            workflow_id=workflow.id,
            command_name=workflow.command_name,
        )

        engine.cancel(state)

        assert state.status == WorkflowStatus.INTERRUPTED


class TestStateManagerContract:
    """Tests verifying StateManager API compliance."""

    @pytest.fixture
    def manager(self, tmp_path):
        """Create a StateManager instance."""
        from doit_cli.services.state_manager import StateManager

        return StateManager(state_dir=tmp_path / ".doit/state")

    def test_save_returns_path(self, manager):
        """Contract: save() must return Path to saved file."""
        from pathlib import Path

        state = WorkflowState(
            id="test_state",
            workflow_id="test-workflow",
            command_name="test",
        )

        result = manager.save(state)

        assert isinstance(result, Path)
        assert result.exists()

    def test_load_returns_state_or_none(self, manager):
        """Contract: load() must return WorkflowState or None."""
        # No existing state
        result = manager.load("nonexistent")
        assert result is None

        # With existing state
        state = WorkflowState(
            id="test_state",
            workflow_id="test-workflow",
            command_name="test",
            status=WorkflowStatus.INTERRUPTED,
        )
        manager.save(state)

        result = manager.load("test")
        assert isinstance(result, WorkflowState)

    def test_list_interrupted_returns_list(self, manager):
        """Contract: list_interrupted() must return list of WorkflowState."""
        result = manager.list_interrupted()

        assert isinstance(result, list)

    def test_cleanup_stale_returns_count(self, manager):
        """Contract: cleanup_stale() must return count of removed files."""
        result = manager.cleanup_stale()

        assert isinstance(result, int)
        assert result >= 0


class TestInputValidatorContract:
    """Tests verifying InputValidator API compliance."""

    @pytest.fixture
    def step(self):
        """Create a test step."""
        return WorkflowStep(
            id="test",
            name="Test",
            prompt_text="Enter:",
            required=True,
            order=0,
        )

    def test_required_validator_returns_validation_result(self, step):
        """Contract: validate() must return ValidationResult."""
        from doit_cli.services.input_validator import RequiredValidator

        validator = RequiredValidator()
        result = validator.validate("value", step, {})

        assert isinstance(result, ValidationResult)
        assert hasattr(result, "passed")
        assert hasattr(result, "error_message")
        assert hasattr(result, "suggestion")

    def test_path_exists_validator_returns_validation_result(self, step):
        """Contract: PathExistsValidator.validate() must return ValidationResult."""
        from doit_cli.services.input_validator import PathExistsValidator

        validator = PathExistsValidator()
        result = validator.validate("/some/path", step, {})

        assert isinstance(result, ValidationResult)

    def test_choice_validator_returns_validation_result(self):
        """Contract: ChoiceValidator.validate() must return ValidationResult."""
        from doit_cli.services.input_validator import ChoiceValidator

        step = WorkflowStep(
            id="choice",
            name="Choice",
            prompt_text="Select:",
            required=True,
            order=0,
            options={"a": "A", "b": "B"},
        )

        validator = ChoiceValidator()
        result = validator.validate("a", step, {})

        assert isinstance(result, ValidationResult)

    def test_pattern_validator_returns_validation_result(self, step):
        """Contract: PatternValidator.validate() must return ValidationResult."""
        from doit_cli.services.input_validator import PatternValidator

        validator = PatternValidator(pattern=r"^\w+$")
        result = validator.validate("test", step, {})

        assert isinstance(result, ValidationResult)


class TestInteractivePromptContract:
    """Tests verifying InteractivePrompt API compliance."""

    @pytest.fixture
    def prompt(self):
        """Create an InteractivePrompt in non-interactive mode."""
        from doit_cli.prompts.interactive import InteractivePrompt

        return InteractivePrompt(force_non_interactive=True)

    @pytest.fixture
    def step(self):
        """Create a test step with default."""
        return WorkflowStep(
            id="test",
            name="Test",
            prompt_text="Enter:",
            required=False,
            order=0,
            default_value="default",
        )

    @pytest.fixture
    def choice_step(self):
        """Create a choice step."""
        return WorkflowStep(
            id="choice",
            name="Choice",
            prompt_text="Select:",
            required=True,
            order=0,
            default_value="a",
            options={"a": "Option A", "b": "Option B"},
        )

    def test_prompt_returns_string(self, prompt, step):
        """Contract: prompt() must return string."""
        result = prompt.prompt(step)

        assert isinstance(result, str)

    def test_prompt_choice_returns_string(self, prompt, choice_step):
        """Contract: prompt_choice() must return string."""
        result = prompt.prompt_choice(choice_step, choice_step.options)

        assert isinstance(result, str)

    def test_prompt_confirm_returns_bool(self, prompt):
        """Contract: prompt_confirm() must return bool."""
        result = prompt.prompt_confirm("Continue?", default=True)

        assert isinstance(result, bool)


class TestProgressDisplayContract:
    """Tests verifying ProgressDisplay API compliance."""

    @pytest.fixture
    def display(self):
        """Create a ProgressDisplay instance."""
        from doit_cli.prompts.interactive import ProgressDisplay

        return ProgressDisplay()

    @pytest.fixture
    def step(self):
        """Create a test step."""
        return WorkflowStep(
            id="test",
            name="Test Step",
            prompt_text="Enter:",
            required=True,
            order=0,
        )

    def test_show_step_accepts_correct_params(self, display, step):
        """Contract: show_step() must accept step, current, total."""
        # Should not raise
        display.show_step(step, current=1, total=5)

    def test_mark_complete_accepts_step(self, display, step):
        """Contract: mark_complete() must accept step."""
        # Should not raise
        display.mark_complete(step)

    def test_mark_skipped_accepts_step(self, display, step):
        """Contract: mark_skipped() must accept step."""
        # Should not raise
        display.mark_skipped(step)

    def test_show_error_accepts_step_and_result(self, display, step):
        """Contract: show_error() must accept step and ValidationResult."""
        error = ValidationResult.failure("Error message")

        # Should not raise
        display.show_error(step, error)


class TestDataModelContracts:
    """Tests verifying data model contracts."""

    def test_workflow_step_required_default_constraint(self):
        """Contract: Optional steps must have default_value."""
        # This should raise ValueError
        with pytest.raises(ValueError):
            WorkflowStep(
                id="invalid",
                name="Invalid",
                prompt_text="Enter:",
                required=False,  # Optional
                order=0,
                # Missing default_value
            )

    def test_workflow_requires_at_least_one_step(self):
        """Contract: Workflow must have at least one step."""
        with pytest.raises(ValueError):
            Workflow(
                id="empty",
                command_name="test",
                description="Empty workflow",
                interactive=True,
                steps=[],  # Empty
            )

    def test_workflow_step_orders_must_be_unique(self):
        """Contract: Step orders must be unique within workflow."""
        with pytest.raises(ValueError):
            Workflow(
                id="duplicate-order",
                command_name="test",
                description="Duplicate order",
                interactive=True,
                steps=[
                    WorkflowStep(
                        id="step1", name="Step 1", prompt_text="1:",
                        required=True, order=0,
                    ),
                    WorkflowStep(
                        id="step2", name="Step 2", prompt_text="2:",
                        required=True, order=0,  # Same order!
                    ),
                ],
            )

    def test_workflow_step_ids_must_be_unique(self):
        """Contract: Step IDs must be unique within workflow."""
        with pytest.raises(ValueError):
            Workflow(
                id="duplicate-id",
                command_name="test",
                description="Duplicate ID",
                interactive=True,
                steps=[
                    WorkflowStep(
                        id="same-id", name="Step 1", prompt_text="1:",
                        required=True, order=0,
                    ),
                    WorkflowStep(
                        id="same-id", name="Step 2", prompt_text="2:",
                        required=True, order=1,
                    ),
                ],
            )

    def test_workflow_state_serialization(self):
        """Contract: WorkflowState must be serializable and deserializable."""
        original = WorkflowState(
            id="test",
            workflow_id="workflow",
            command_name="cmd",
            current_step=2,
            status=WorkflowStatus.INTERRUPTED,
        )
        original.responses["step1"] = StepResponse(
            step_id="step1",
            value="value1",
        )

        # Serialize and deserialize
        data = original.to_dict()
        restored = WorkflowState.from_dict(data)

        assert restored.id == original.id
        assert restored.workflow_id == original.workflow_id
        assert restored.current_step == original.current_step
        assert restored.status == original.status
        assert "step1" in restored.responses
