"""Interactive prompts for guided workflows.

This module provides the InteractivePrompt and ProgressDisplay classes
for collecting user input and showing workflow progress.
"""

import os
import sys
from typing import Callable

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.theme import Theme

from ..models.workflow_models import (
    WorkflowStep,
    ValidationResult,
    NavigationCommand,
)


# =============================================================================
# Theme Configuration
# =============================================================================


WORKFLOW_THEME = Theme({
    "prompt": "bold cyan",
    "prompt.default": "dim",
    "error": "bold red",
    "success": "bold green",
    "warning": "bold yellow",
    "info": "dim",
    "step.current": "bold white",
    "step.completed": "green",
    "step.skipped": "dim",
    "step.pending": "dim white",
})


# =============================================================================
# InteractivePrompt Class
# =============================================================================


class InteractivePrompt:
    """Collects user input for workflow steps.

    This class handles interactive prompting for workflow steps,
    including text input, choice selection, and confirmation dialogs.
    """

    # Environment variable to force non-interactive mode
    NON_INTERACTIVE_ENV_VAR = "DOIT_NON_INTERACTIVE"

    def __init__(
        self,
        console: Console | None = None,
        force_non_interactive: bool = False,
    ):
        """Initialize the prompt handler.

        Args:
            console: Rich console for output. Creates a new one if not provided.
            force_non_interactive: If True, always use non-interactive mode.
        """
        self.console = console or Console(theme=WORKFLOW_THEME)
        self._force_non_interactive = force_non_interactive

    def prompt(
        self,
        step: WorkflowStep,
        validator: "InputValidator | None" = None,
    ) -> str:
        """Prompt user for step input.

        Args:
            step: Step to prompt for
            validator: Optional validator for real-time feedback

        Returns:
            User-provided value

        Raises:
            NavigationCommand: If user types 'back' or 'skip'
            KeyboardInterrupt: If user presses Ctrl+C
        """
        # Non-TTY mode - return default or raise error
        if not self._is_interactive():
            if step.default_value is not None:
                return step.default_value
            if not step.required:
                return ""
            raise ValueError(f"Required step '{step.id}' has no default for non-interactive mode")

        while True:
            # Display the prompt
            self._display_prompt(step)

            # Get input
            value = self._get_input(step)

            # Handle navigation commands
            nav_result = self._check_navigation(value, step)
            if nav_result is not None:
                raise nav_result

            # Handle empty input for optional steps
            if not value and not step.required:
                return step.default_value or ""

            # Validate if validator provided
            if validator:
                from ..services.input_validator import validate_step

                result = validator.validate(value, step, {})
                if not result.passed:
                    self._show_validation_error(result)
                    continue

            return value

    def prompt_choice(
        self,
        step: WorkflowStep,
        options: dict[str, str],
    ) -> str:
        """Prompt user to select from options.

        Args:
            step: Step with choice options
            options: {value: description} mapping

        Returns:
            Selected option value

        Raises:
            NavigationCommand: If user types 'back'
            KeyboardInterrupt: If user presses Ctrl+C
        """
        # Non-TTY mode - return first option or default
        if not self._is_interactive():
            if step.default_value and step.default_value in options:
                return step.default_value
            return list(options.keys())[0]

        while True:
            # Display prompt and options
            self._display_prompt(step)
            self._display_options(options)

            # Get choice
            value = self._get_choice_input(step, options)

            # Handle navigation
            nav_result = self._check_navigation(value, step)
            if nav_result is not None:
                raise nav_result

            # Validate choice
            normalized = value.strip().lower()
            for key in options:
                if key.lower() == normalized:
                    return key

            self._show_invalid_choice(value, options)

    def prompt_confirm(
        self,
        message: str,
        default: bool = True,
    ) -> bool:
        """Prompt for yes/no confirmation.

        Args:
            message: Confirmation prompt
            default: Default if Enter pressed

        Returns:
            True for yes, False for no
        """
        # Non-TTY mode - return default
        if not self._is_interactive():
            return default

        while True:
            default_str = "Y/n" if default else "y/N"
            self.console.print(f"[prompt]{message}[/prompt] [{default_str}] ", end="")

            value = self._get_input(None)

            if not value:
                return default

            normalized = value.strip().lower()
            if normalized in ("y", "yes"):
                return True
            if normalized in ("n", "no"):
                return False

            self._show_invalid_confirm()

    # =========================================================================
    # Internal Methods
    # =========================================================================

    def _is_interactive(self) -> bool:
        """Check if running in an interactive terminal.

        Returns False if:
        - force_non_interactive is True
        - DOIT_NON_INTERACTIVE env var is set to "true", "1", or "yes"
        - stdin is not a TTY
        """
        if self._force_non_interactive:
            return False

        # Check environment variable
        env_value = os.environ.get(self.NON_INTERACTIVE_ENV_VAR, "").lower()
        if env_value in ("true", "1", "yes"):
            return False

        return sys.stdin.isatty()

    def _display_prompt(self, step: WorkflowStep) -> None:
        """Display the prompt text for a step."""
        self.console.print()
        self.console.print(f"[prompt]{step.prompt_text}[/prompt]")

        if step.default_value and not step.options:
            self.console.print(f"[prompt.default](default: {step.default_value})[/prompt.default]")

        if not step.required:
            self.console.print("[info]Type 'skip' to skip this step[/info]")

        self.console.print("[info]Type 'back' to go to previous step[/info]")

    def _display_options(self, options: dict[str, str]) -> None:
        """Display available options for a choice step."""
        self.console.print()
        for key, description in options.items():
            self.console.print(f"  [bold]{key}[/bold]: {description}")
        self.console.print()

    def _get_input(self, step: WorkflowStep | None) -> str:
        """Get raw input from user."""
        try:
            return input("> ").strip()
        except EOFError:
            # Handle piped input ending
            if step and step.default_value:
                return step.default_value
            return ""

    def _get_choice_input(self, step: WorkflowStep, options: dict[str, str]) -> str:
        """Get choice input from user."""
        return self._get_input(step)

    def _check_navigation(
        self,
        value: str,
        step: WorkflowStep,
    ) -> NavigationCommand | None:
        """Check if input is a navigation command."""
        normalized = value.strip().lower()

        if normalized == "back":
            return NavigationCommand("back")

        if normalized == "skip":
            if not step.required:
                return NavigationCommand("skip")
            # For required steps, 'skip' is treated as regular input

        return None

    def _show_validation_error(self, result: ValidationResult) -> None:
        """Display a validation error message."""
        self.console.print()
        self.console.print(f"[error]Error: {result.error_message}[/error]")
        if result.suggestion:
            self.console.print(f"[info]Hint: {result.suggestion}[/info]")
        self.console.print()

    def _show_invalid_choice(self, value: str, options: dict[str, str]) -> None:
        """Display an invalid choice error."""
        valid_options = ", ".join(options.keys())
        self.console.print()
        self.console.print(f"[error]Invalid choice: '{value}'[/error]")
        self.console.print(f"[info]Valid options: {valid_options}[/info]")
        self.console.print()

    def _show_invalid_confirm(self) -> None:
        """Display an invalid confirmation error."""
        self.console.print("[error]Please enter 'y' or 'n'[/error]")


# =============================================================================
# ProgressDisplay Class
# =============================================================================


class ProgressDisplay:
    """Displays workflow progress to the user.

    Shows the current step, completed steps, and overall progress
    through a multi-step workflow.
    """

    def __init__(self, console: Console | None = None):
        """Initialize the progress display.

        Args:
            console: Rich console for output. Creates a new one if not provided.
        """
        self.console = console or Console(theme=WORKFLOW_THEME)
        self._completed_steps: list[str] = []
        self._skipped_steps: list[str] = []

    def show_step(
        self,
        step: WorkflowStep,
        current: int,
        total: int,
    ) -> None:
        """Show current step indicator.

        Args:
            step: Current step
            current: Current step number (1-indexed)
            total: Total step count
        """
        percentage = int((current - 1) / total * 100) if total > 0 else 0

        header = f"Step {current} of {total}: {step.name}"
        if not step.required:
            header += " (optional)"

        self.console.print()
        self.console.rule(f"[step.current]{header}[/step.current]")

        # Show progress percentage
        self.console.print(f"[info]Progress: {percentage}% complete[/info]")

    def mark_complete(self, step: WorkflowStep) -> None:
        """Mark step as completed in display."""
        self._completed_steps.append(step.id)
        self.console.print(f"[success]\u2713 {step.name} completed[/success]")

    def mark_skipped(self, step: WorkflowStep) -> None:
        """Mark step as skipped in display."""
        self._skipped_steps.append(step.id)
        self.console.print(f"[step.skipped]- {step.name} skipped[/step.skipped]")

    def show_error(
        self,
        step: WorkflowStep,
        error: ValidationResult,
    ) -> None:
        """Show validation error with suggestion."""
        self.console.print()
        self.console.print(Panel(
            f"[error]{error.error_message}[/error]\n\n"
            f"[info]{error.suggestion or 'Please try again.'}[/info]",
            title=f"Validation Error: {step.name}",
            border_style="red",
        ))

    def show_summary(self, total_steps: int) -> None:
        """Show final summary of workflow progress."""
        completed = len(self._completed_steps)
        skipped = len(self._skipped_steps)

        self.console.print()
        self.console.rule("[success]Workflow Complete[/success]")
        self.console.print(f"[success]Completed: {completed} steps[/success]")
        if skipped > 0:
            self.console.print(f"[step.skipped]Skipped: {skipped} steps[/step.skipped]")
        self.console.print()

    def show_interrupted(self, current_step: int, total_steps: int) -> None:
        """Show message when workflow is interrupted."""
        self.console.print()
        self.console.print(
            f"[warning]Workflow interrupted at step {current_step} of {total_steps}[/warning]"
        )
        self.console.print("[info]Progress has been saved. Run the command again to resume.[/info]")
        self.console.print()
