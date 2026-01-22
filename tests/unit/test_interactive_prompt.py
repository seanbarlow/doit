"""Unit tests for InteractivePrompt class.

Tests the interactive prompting functionality for guided workflows.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from doit_cli.models.workflow_models import (
    WorkflowStep,
    ValidationResult,
    NavigationCommand,
)


class TestInteractivePrompt:
    """Tests for the InteractivePrompt class."""

    @pytest.fixture
    def prompt(self):
        """Create an InteractivePrompt instance with interactive mode enabled."""
        from doit_cli.prompts.interactive import InteractivePrompt

        p = InteractivePrompt()
        # Patch _is_interactive to return True for testing
        p._is_interactive = lambda: True
        return p

    @pytest.fixture
    def text_step(self):
        """Create a simple text input step."""
        return WorkflowStep(
            id="project-name",
            name="Project Name",
            prompt_text="Enter your project name:",
            required=True,
            order=0,
        )

    @pytest.fixture
    def optional_step(self):
        """Create an optional step with default."""
        return WorkflowStep(
            id="description",
            name="Description",
            prompt_text="Enter description (optional):",
            required=False,
            order=1,
            default_value="No description",
        )

    @pytest.fixture
    def choice_step(self):
        """Create a choice selection step."""
        return WorkflowStep(
            id="framework",
            name="Framework",
            prompt_text="Select your framework:",
            required=True,
            order=2,
            options={
                "react": "React - A JavaScript library for building UIs",
                "vue": "Vue - The progressive JavaScript framework",
                "angular": "Angular - Platform for web applications",
            },
        )

    # =========================================================================
    # prompt() method tests
    # =========================================================================

    def test_prompt_returns_user_input(self, prompt, text_step):
        """Test that prompt returns the user's input."""
        with patch.object(prompt, "_get_input", return_value="my-project"):
            result = prompt.prompt(text_step)
            assert result == "my-project"

    def test_prompt_displays_prompt_text(self, prompt, text_step):
        """Test that prompt shows the step's prompt text."""
        with patch.object(prompt, "_get_input", return_value="test") as mock_input:
            with patch.object(prompt, "_display_prompt") as mock_display:
                prompt.prompt(text_step)
                mock_display.assert_called()

    def test_prompt_back_raises_navigation_command(self, prompt, text_step):
        """Test that typing 'back' raises NavigationCommand."""
        with patch.object(prompt, "_get_input", return_value="back"):
            with pytest.raises(NavigationCommand) as exc_info:
                prompt.prompt(text_step)
            assert exc_info.value.command == "back"

    def test_prompt_skip_raises_navigation_command(self, prompt, optional_step):
        """Test that typing 'skip' raises NavigationCommand for optional steps."""
        with patch.object(prompt, "_get_input", return_value="skip"):
            with pytest.raises(NavigationCommand) as exc_info:
                prompt.prompt(optional_step)
            assert exc_info.value.command == "skip"

    def test_prompt_skip_not_allowed_for_required(self, prompt, text_step):
        """Test that skip is not allowed for required steps."""
        # For required steps, 'skip' should be treated as regular input
        # and validation should fail (tested elsewhere)
        with patch.object(prompt, "_get_input", return_value="skip"):
            # Should not raise NavigationCommand for required steps
            result = prompt.prompt(text_step)
            assert result == "skip"

    def test_prompt_with_validator_shows_error_on_invalid(self, prompt, text_step):
        """Test that validation errors are displayed."""
        validator = Mock()
        validator.validate.return_value = ValidationResult.failure(
            "Name too short", "Use at least 3 characters"
        )

        with patch.object(
            prompt, "_get_input", side_effect=["ab", "abc"]
        ) as mock_input:
            with patch.object(prompt, "_show_validation_error") as mock_error:
                # Second attempt with valid input
                validator.validate.side_effect = [
                    ValidationResult.failure("Name too short"),
                    ValidationResult.success(),
                ]
                result = prompt.prompt(text_step, validator=validator)

                # Should have shown error for first attempt
                mock_error.assert_called_once()
                assert result == "abc"

    def test_prompt_empty_returns_default_for_optional(self, prompt, optional_step):
        """Test that empty input returns default for optional steps."""
        with patch.object(prompt, "_get_input", return_value=""):
            result = prompt.prompt(optional_step)
            assert result == optional_step.default_value

    # =========================================================================
    # prompt_choice() method tests
    # =========================================================================

    def test_prompt_choice_returns_selected_option(self, prompt, choice_step):
        """Test that prompt_choice returns the selected option key."""
        with patch.object(prompt, "_get_choice_input", return_value="react"):
            result = prompt.prompt_choice(choice_step, choice_step.options)
            assert result == "react"

    def test_prompt_choice_displays_options(self, prompt, choice_step):
        """Test that all options are displayed."""
        with patch.object(prompt, "_get_choice_input", return_value="vue"):
            with patch.object(prompt, "_display_options") as mock_display:
                prompt.prompt_choice(choice_step, choice_step.options)
                mock_display.assert_called_once_with(choice_step.options)

    def test_prompt_choice_rejects_invalid_option(self, prompt, choice_step):
        """Test that invalid options are rejected and user is re-prompted."""
        with patch.object(
            prompt, "_get_choice_input", side_effect=["invalid", "react"]
        ):
            with patch.object(prompt, "_show_invalid_choice") as mock_error:
                result = prompt.prompt_choice(choice_step, choice_step.options)
                mock_error.assert_called_once()
                assert result == "react"

    def test_prompt_choice_back_raises_navigation(self, prompt, choice_step):
        """Test that 'back' in choice prompt raises NavigationCommand."""
        with patch.object(prompt, "_get_choice_input", return_value="back"):
            with pytest.raises(NavigationCommand) as exc_info:
                prompt.prompt_choice(choice_step, choice_step.options)
            assert exc_info.value.command == "back"

    # =========================================================================
    # prompt_confirm() method tests
    # =========================================================================

    def test_prompt_confirm_yes_returns_true(self, prompt):
        """Test that 'y' or 'yes' returns True."""
        for answer in ["y", "Y", "yes", "YES", "Yes"]:
            with patch.object(prompt, "_get_input", return_value=answer):
                assert prompt.prompt_confirm("Proceed?") is True

    def test_prompt_confirm_no_returns_false(self, prompt):
        """Test that 'n' or 'no' returns False."""
        for answer in ["n", "N", "no", "NO", "No"]:
            with patch.object(prompt, "_get_input", return_value=answer):
                assert prompt.prompt_confirm("Proceed?") is False

    def test_prompt_confirm_empty_returns_default_true(self, prompt):
        """Test that empty input returns default (True)."""
        with patch.object(prompt, "_get_input", return_value=""):
            assert prompt.prompt_confirm("Proceed?", default=True) is True

    def test_prompt_confirm_empty_returns_default_false(self, prompt):
        """Test that empty input returns default (False)."""
        with patch.object(prompt, "_get_input", return_value=""):
            assert prompt.prompt_confirm("Proceed?", default=False) is False

    def test_prompt_confirm_invalid_reprompts(self, prompt):
        """Test that invalid input causes re-prompt."""
        with patch.object(prompt, "_get_input", side_effect=["maybe", "y"]):
            with patch.object(prompt, "_show_invalid_confirm") as mock_error:
                result = prompt.prompt_confirm("Proceed?")
                mock_error.assert_called_once()
                assert result is True


class TestInteractivePromptIntegration:
    """Integration tests for InteractivePrompt with real terminal simulation."""

    @pytest.fixture
    def prompt(self):
        """Create an InteractivePrompt instance with interactive mode enabled."""
        from doit_cli.prompts.interactive import InteractivePrompt

        p = InteractivePrompt()
        # Patch _is_interactive to return True for testing
        p._is_interactive = lambda: True
        return p

    def test_non_tty_uses_defaults(self):
        """Test that non-TTY environments use defaults automatically."""
        from doit_cli.prompts.interactive import InteractivePrompt

        # Create a fresh prompt without interactive mode override
        prompt = InteractivePrompt()
        step = WorkflowStep(
            id="test",
            name="Test",
            prompt_text="Enter value:",
            required=False,
            order=0,
            default_value="default",
        )

        with patch("sys.stdin.isatty", return_value=False):
            result = prompt.prompt(step)
            assert result == "default"

    def test_keyboard_interrupt_handled(self, prompt):
        """Test that Ctrl+C is properly raised."""
        step = WorkflowStep(
            id="test",
            name="Test",
            prompt_text="Enter value:",
            required=True,
            order=0,
        )

        with patch.object(prompt, "_get_input", side_effect=KeyboardInterrupt):
            with pytest.raises(KeyboardInterrupt):
                prompt.prompt(step)
