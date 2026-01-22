"""Unit tests for non-interactive mode.

Tests the non-interactive mode functionality for CI/CD automation.
"""

import os
import pytest
from unittest.mock import Mock, patch

from doit_cli.models.workflow_models import (
    Workflow,
    WorkflowStep,
)


class TestInteractivePromptNonInteractive:
    """Tests for InteractivePrompt non-interactive mode."""

    @pytest.fixture
    def required_step(self):
        """Create a required step without default."""
        return WorkflowStep(
            id="required",
            name="Required Step",
            prompt_text="Enter value:",
            required=True,
            order=0,
        )

    @pytest.fixture
    def optional_step(self):
        """Create an optional step with default."""
        return WorkflowStep(
            id="optional",
            name="Optional Step",
            prompt_text="Enter optional value:",
            required=False,
            order=1,
            default_value="default-value",
        )

    def test_force_non_interactive_flag(self, optional_step):
        """Test that force_non_interactive flag works."""
        from doit_cli.prompts.interactive import InteractivePrompt

        prompt = InteractivePrompt(force_non_interactive=True)

        result = prompt.prompt(optional_step)

        assert result == optional_step.default_value

    def test_env_var_forces_non_interactive(self, optional_step, monkeypatch):
        """Test that DOIT_NON_INTERACTIVE env var forces non-interactive."""
        from doit_cli.prompts.interactive import InteractivePrompt

        monkeypatch.setenv("DOIT_NON_INTERACTIVE", "true")
        prompt = InteractivePrompt()

        result = prompt.prompt(optional_step)

        assert result == optional_step.default_value

    def test_env_var_true_values(self, optional_step, monkeypatch):
        """Test various true values for env var."""
        from doit_cli.prompts.interactive import InteractivePrompt

        for value in ["true", "TRUE", "True", "1", "yes", "YES", "Yes"]:
            monkeypatch.setenv("DOIT_NON_INTERACTIVE", value)
            prompt = InteractivePrompt()

            # Should use default without prompting
            assert not prompt._is_interactive()

    def test_env_var_false_values(self, optional_step, monkeypatch):
        """Test that other values don't trigger non-interactive."""
        from doit_cli.prompts.interactive import InteractivePrompt

        for value in ["false", "0", "no", "", "anything"]:
            monkeypatch.setenv("DOIT_NON_INTERACTIVE", value)
            prompt = InteractivePrompt()

            # With patched isatty returning True, should be interactive
            with patch("sys.stdin.isatty", return_value=True):
                assert prompt._is_interactive()

    def test_non_interactive_required_no_default_raises(self, required_step):
        """Test that required step without default raises in non-interactive mode."""
        from doit_cli.prompts.interactive import InteractivePrompt

        prompt = InteractivePrompt(force_non_interactive=True)

        with pytest.raises(ValueError) as exc_info:
            prompt.prompt(required_step)

        assert "required" in str(exc_info.value).lower() or "default" in str(exc_info.value).lower()

    def test_non_interactive_choice_uses_default(self):
        """Test that choice prompts use default in non-interactive mode."""
        from doit_cli.prompts.interactive import InteractivePrompt

        step = WorkflowStep(
            id="choice",
            name="Choice Step",
            prompt_text="Select:",
            required=True,
            order=0,
            default_value="option1",
            options={"option1": "First", "option2": "Second"},
        )

        prompt = InteractivePrompt(force_non_interactive=True)
        result = prompt.prompt_choice(step, step.options)

        assert result == "option1"

    def test_non_interactive_confirm_uses_default(self):
        """Test that confirmation prompts use default in non-interactive mode."""
        from doit_cli.prompts.interactive import InteractivePrompt

        prompt = InteractivePrompt(force_non_interactive=True)

        assert prompt.prompt_confirm("Continue?", default=True) is True
        assert prompt.prompt_confirm("Continue?", default=False) is False


class TestWorkflowMixin:
    """Tests for WorkflowMixin class."""

    @pytest.fixture
    def simple_workflow(self):
        """Create a simple workflow with defaults."""
        return Workflow(
            id="test-workflow",
            command_name="test",
            description="Test workflow",
            interactive=True,
            steps=[
                WorkflowStep(
                    id="step1",
                    name="Step 1",
                    prompt_text="Enter:",
                    required=False,
                    order=0,
                    default_value="default1",
                ),
            ],
        )

    def test_init_workflow_non_interactive(self, simple_workflow):
        """Test initializing workflow in non-interactive mode."""
        from doit_cli.cli.workflow_mixin import WorkflowMixin

        mixin = WorkflowMixin()
        mixin.init_workflow(non_interactive=True)

        assert mixin.is_non_interactive is True

    def test_init_workflow_from_env(self, simple_workflow, monkeypatch):
        """Test initializing workflow with env var."""
        from doit_cli.cli.workflow_mixin import WorkflowMixin

        monkeypatch.setenv("DOIT_NON_INTERACTIVE", "true")
        mixin = WorkflowMixin()
        mixin.init_workflow()

        assert mixin.is_non_interactive is True

    def test_execute_workflow_without_init_raises(self, simple_workflow):
        """Test that executing without init raises error."""
        from doit_cli.cli.workflow_mixin import WorkflowMixin

        mixin = WorkflowMixin()

        with pytest.raises(ValueError):
            mixin.execute_workflow(simple_workflow)


class TestValidateRequiredDefaults:
    """Tests for validate_required_defaults function."""

    def test_returns_empty_when_all_have_defaults(self):
        """Test that no issues found when all required have defaults."""
        from doit_cli.cli.workflow_mixin import validate_required_defaults

        workflow = Workflow(
            id="test",
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
                    default_value="default",
                ),
            ],
        )

        missing = validate_required_defaults(workflow)
        assert missing == []

    def test_returns_missing_required_without_default(self):
        """Test that required steps without defaults are flagged."""
        from doit_cli.cli.workflow_mixin import validate_required_defaults

        workflow = Workflow(
            id="test",
            command_name="test",
            description="Test",
            interactive=True,
            steps=[
                WorkflowStep(
                    id="required-no-default",
                    name="Step 1",
                    prompt_text="Enter:",
                    required=True,
                    order=0,
                ),
                WorkflowStep(
                    id="required-with-default",
                    name="Step 2",
                    prompt_text="Enter:",
                    required=True,
                    order=1,
                    default_value="has-default",
                ),
                WorkflowStep(
                    id="optional",
                    name="Step 3",
                    prompt_text="Enter:",
                    required=False,
                    order=2,
                    default_value="optional-default",
                ),
            ],
        )

        missing = validate_required_defaults(workflow)
        assert missing == ["required-no-default"]


class TestCreateNonInteractiveWorkflow:
    """Tests for create_non_interactive_workflow function."""

    def test_applies_overrides_to_required_steps(self):
        """Test that overrides are applied to required steps without defaults."""
        from doit_cli.cli.workflow_mixin import create_non_interactive_workflow

        original = Workflow(
            id="test",
            command_name="test",
            description="Test",
            interactive=True,
            steps=[
                WorkflowStep(
                    id="needs-override",
                    name="Step 1",
                    prompt_text="Enter:",
                    required=True,
                    order=0,
                ),
            ],
        )

        overrides = {"needs-override": "provided-value"}
        modified = create_non_interactive_workflow(original, overrides)

        assert modified.steps[0].default_value == "provided-value"

    def test_preserves_existing_defaults(self):
        """Test that existing defaults are preserved."""
        from doit_cli.cli.workflow_mixin import create_non_interactive_workflow

        original = Workflow(
            id="test",
            command_name="test",
            description="Test",
            interactive=True,
            steps=[
                WorkflowStep(
                    id="has-default",
                    name="Step 1",
                    prompt_text="Enter:",
                    required=True,
                    order=0,
                    default_value="original-default",
                ),
            ],
        )

        overrides = {"has-default": "override-value"}
        modified = create_non_interactive_workflow(original, overrides)

        # Should keep original default since it already has one
        assert modified.steps[0].default_value == "original-default"

    def test_preserves_workflow_metadata(self):
        """Test that workflow metadata is preserved."""
        from doit_cli.cli.workflow_mixin import create_non_interactive_workflow

        original = Workflow(
            id="test-id",
            command_name="test-cmd",
            description="Test description",
            interactive=True,
            steps=[
                WorkflowStep(
                    id="step",
                    name="Step",
                    prompt_text="Enter:",
                    required=False,
                    order=0,
                    default_value="default",
                ),
            ],
        )

        modified = create_non_interactive_workflow(original, {})

        assert modified.id == original.id
        assert modified.command_name == original.command_name
        assert modified.description == original.description
        assert modified.interactive == original.interactive


class TestTTYDetection:
    """Tests for TTY detection in non-interactive mode."""

    def test_non_tty_stdin_uses_non_interactive(self):
        """Test that non-TTY stdin triggers non-interactive mode."""
        from doit_cli.prompts.interactive import InteractivePrompt

        with patch("sys.stdin.isatty", return_value=False):
            prompt = InteractivePrompt()
            assert not prompt._is_interactive()

    def test_tty_stdin_is_interactive(self):
        """Test that TTY stdin allows interactive mode."""
        from doit_cli.prompts.interactive import InteractivePrompt

        with patch("sys.stdin.isatty", return_value=True):
            prompt = InteractivePrompt()
            assert prompt._is_interactive()

    def test_force_flag_overrides_tty(self):
        """Test that force flag overrides TTY detection."""
        from doit_cli.prompts.interactive import InteractivePrompt

        with patch("sys.stdin.isatty", return_value=True):
            prompt = InteractivePrompt(force_non_interactive=True)
            assert not prompt._is_interactive()
