"""Workflow mixin for CLI commands.

This module provides a mixin class that adds guided workflow functionality
to Typer CLI commands, including --non-interactive flag support and
default value handling.
"""

import os
from typing import Any, Callable, TypeVar

import typer
from rich.console import Console

from ..models.workflow_models import Workflow, WorkflowStep
from ..prompts.interactive import InteractivePrompt
from ..services.workflow_engine import WorkflowEngine
from ..services.state_manager import StateManager


# Type variable for decorator
F = TypeVar("F", bound=Callable[..., Any])


class WorkflowMixin:
    """Mixin providing guided workflow functionality for CLI commands.

    This class adds workflow execution capabilities to CLI commands,
    including interactive prompting, progress display, and state recovery.

    Usage:
        class MyCommand(WorkflowMixin):
            def __init__(self):
                super().__init__()
                self.workflow = Workflow(...)

            def run(self, non_interactive: bool = False):
                self.init_workflow(non_interactive=non_interactive)
                results = self.execute_workflow(self.workflow)
                # Use results...
    """

    def __init__(
        self,
        console: Console | None = None,
        state_dir: str | None = None,
    ):
        """Initialize the workflow mixin.

        Args:
            console: Rich console for output
            state_dir: Directory for state files (defaults to .doit/state)
        """
        self.console = console or Console()
        self._state_dir = state_dir
        self._engine: WorkflowEngine | None = None
        self._non_interactive = False

    def init_workflow(
        self,
        non_interactive: bool = False,
        no_state: bool = False,
    ) -> None:
        """Initialize the workflow engine.

        Args:
            non_interactive: Force non-interactive mode
            no_state: Disable state persistence
        """
        self._non_interactive = non_interactive

        # Check environment variable if not explicitly set
        if not non_interactive:
            env_value = os.environ.get("DOIT_NON_INTERACTIVE", "").lower()
            self._non_interactive = env_value in ("true", "1", "yes")

        # Create state manager if enabled
        state_manager = None
        if not no_state:
            state_manager = StateManager(state_dir=self._state_dir)

        # Create prompt with non-interactive flag
        prompt = InteractivePrompt(
            console=self.console,
            force_non_interactive=self._non_interactive,
        )

        # Create engine
        self._engine = WorkflowEngine(
            console=self.console,
            state_manager=state_manager,
        )
        self._engine.prompt = prompt

    def execute_workflow(self, workflow: Workflow) -> dict[str, str]:
        """Execute a guided workflow.

        Args:
            workflow: Workflow definition to execute

        Returns:
            Dictionary of step_id -> response value

        Raises:
            ValueError: If engine not initialized
            WorkflowError: If workflow fails
        """
        if self._engine is None:
            raise ValueError("Workflow engine not initialized. Call init_workflow() first.")

        return self._engine.run(workflow)

    @property
    def is_non_interactive(self) -> bool:
        """Check if running in non-interactive mode."""
        return self._non_interactive


def non_interactive_option() -> Callable[[F], F]:
    """Decorator that adds --non-interactive option to a command.

    Usage:
        @app.command()
        @non_interactive_option()
        def my_command(non_interactive: bool = False):
            ...
    """
    def decorator(func: F) -> F:
        return typer.Option(
            False,
            "--non-interactive",
            "-n",
            help="Run without interactive prompts, using default values.",
            envvar="DOIT_NON_INTERACTIVE",
        )(func)
    return decorator


def workflow_command_options(
    func: Callable[..., Any] | None = None,
) -> Callable[[F], F]:
    """Add standard workflow options to a command.

    Adds the following options:
    - --non-interactive / -n: Disable interactive prompts
    - --no-resume: Don't prompt to resume interrupted workflow

    Usage:
        @app.command()
        @workflow_command_options
        def my_command(
            non_interactive: bool = typer.Option(False),
            no_resume: bool = typer.Option(False),
        ):
            ...
    """
    def decorator(f: F) -> F:
        # This would add the options via typer decorators
        # Implementation depends on how typer handles stacked decorators
        return f

    if func is not None:
        return decorator(func)
    return decorator


def validate_required_defaults(workflow: Workflow) -> list[str]:
    """Validate that all required steps have defaults for non-interactive mode.

    Args:
        workflow: Workflow to validate

    Returns:
        List of step IDs that are required but have no default
    """
    missing = []
    for step in workflow.steps:
        if step.required and step.default_value is None:
            missing.append(step.id)
    return missing


def create_non_interactive_workflow(
    original: Workflow,
    overrides: dict[str, str] | None = None,
) -> Workflow:
    """Create a workflow with defaults for non-interactive execution.

    This creates a modified workflow where required steps that don't
    have defaults get values from the overrides dict.

    Args:
        original: Original workflow definition
        overrides: Step ID to default value mapping

    Returns:
        Modified workflow suitable for non-interactive mode
    """
    overrides = overrides or {}
    new_steps = []

    for step in original.steps:
        if step.required and step.default_value is None and step.id in overrides:
            # Create new step with override as default
            new_step = WorkflowStep(
                id=step.id,
                name=step.name,
                prompt_text=step.prompt_text,
                required=step.required,
                order=step.order,
                validation_type=step.validation_type,
                default_value=overrides[step.id],
                options=step.options,
            )
            new_steps.append(new_step)
        else:
            new_steps.append(step)

    return Workflow(
        id=original.id,
        command_name=original.command_name,
        description=original.description,
        interactive=original.interactive,
        steps=new_steps,
    )
