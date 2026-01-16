"""Workflow engine for orchestrating guided workflows.

This module provides the WorkflowEngine class that manages workflow execution,
step navigation, state persistence, and user input collection.
"""

import signal
from datetime import datetime
from typing import Protocol, runtime_checkable

from rich.console import Console

from ..models.workflow_models import (
    Workflow,
    WorkflowStep,
    WorkflowState,
    WorkflowStatus,
    StepResponse,
    ValidationResult,
    WorkflowError,
    NavigationCommand,
)
from ..prompts.interactive import InteractivePrompt, ProgressDisplay
from .input_validator import validate_step, get_validator


# =============================================================================
# WorkflowEngine Protocol
# =============================================================================


@runtime_checkable
class WorkflowEngineProtocol(Protocol):
    """Protocol defining the WorkflowEngine interface."""

    def start(self, workflow: Workflow) -> WorkflowState:
        """Start a new workflow or resume interrupted one."""
        ...

    def execute_step(
        self,
        state: WorkflowState,
        step: WorkflowStep,
    ) -> tuple[WorkflowState, StepResponse]:
        """Execute a single workflow step."""
        ...

    def complete(self, state: WorkflowState) -> dict:
        """Complete workflow and return collected responses."""
        ...

    def cancel(self, state: WorkflowState) -> None:
        """Cancel workflow and save state for resume."""
        ...


# =============================================================================
# WorkflowEngine Implementation
# =============================================================================


class WorkflowEngine:
    """Orchestrates guided workflow execution.

    Manages the full lifecycle of a workflow including:
    - Starting new workflows or resuming interrupted ones
    - Executing individual steps with validation
    - Handling navigation (back/skip)
    - State persistence for recovery
    - Progress display
    """

    def __init__(
        self,
        console: Console | None = None,
        state_manager: "StateManager | None" = None,
    ):
        """Initialize the workflow engine.

        Args:
            console: Rich console for output
            state_manager: Optional state manager for persistence
        """
        self.console = console or Console()
        self.state_manager = state_manager
        self.prompt = InteractivePrompt(console)
        self.progress = ProgressDisplay(console)
        self._interrupted = False

    def start(self, workflow: Workflow) -> WorkflowState:
        """Start a new workflow or resume interrupted one.

        Args:
            workflow: Workflow definition to execute

        Returns:
            Initial or resumed WorkflowState

        Raises:
            WorkflowError: If workflow cannot be started
        """
        # Check for existing interrupted state
        if self.state_manager:
            existing_state = self.state_manager.load(workflow.command_name)
            if existing_state and existing_state.status == WorkflowStatus.INTERRUPTED:
                if self._prompt_resume(existing_state):
                    existing_state.status = WorkflowStatus.RUNNING
                    return existing_state
                else:
                    # User chose to start fresh
                    self.state_manager.delete(existing_state)

        # Create new state
        state = WorkflowState(
            id=self._generate_state_id(workflow.command_name),
            workflow_id=workflow.id,
            command_name=workflow.command_name,
            current_step=0,
            total_steps=len(workflow.steps),
            status=WorkflowStatus.PENDING,
        )

        return state

    def execute_step(
        self,
        state: WorkflowState,
        step: WorkflowStep,
    ) -> tuple[WorkflowState, StepResponse]:
        """Execute a single workflow step.

        Args:
            state: Current workflow state
            step: Step to execute

        Returns:
            Updated state and step response

        Raises:
            NavigationCommand: If user navigates back/skip
            KeyboardInterrupt: If user cancels
        """
        # Update status to running
        if state.status == WorkflowStatus.PENDING:
            state.status = WorkflowStatus.RUNNING

        # Get validator if specified
        validator = None
        if step.validation_type:
            validator = get_validator(step.validation_type)

        # Show progress
        total_steps = self._count_steps(state)
        self.progress.show_step(step, state.current_step + 1, total_steps)

        # Get input based on step type
        if step.options:
            value = self.prompt.prompt_choice(step, step.options)
        else:
            value = self.prompt.prompt(step, validator)

        # Create response
        response = StepResponse(
            step_id=step.id,
            value=value,
            skipped=False,
        )

        # Update state
        state.set_response(response)
        state.advance_step()

        # Show completion
        self.progress.mark_complete(step)

        return state, response

    def run(
        self,
        workflow: Workflow,
        initial_responses: dict[str, str] | None = None,
    ) -> dict:
        """Run a complete workflow from start to finish.

        Args:
            workflow: Workflow to execute
            initial_responses: Optional pre-populated responses to skip steps.
                Maps step_id -> value. Steps with initial responses will be
                skipped and use the provided value.

        Returns:
            Dictionary of step_id -> response value

        Raises:
            WorkflowError: If workflow fails
            KeyboardInterrupt: If user cancels
        """
        # Setup interrupt handler
        self._setup_interrupt_handler()

        state = self.start(workflow)

        # Sort steps by order
        steps = sorted(workflow.steps, key=lambda s: s.order)

        # Pre-populate state with initial responses (Fix MT-007)
        if initial_responses:
            for step_id, value in initial_responses.items():
                state.responses[step_id] = StepResponse(
                    step_id=step_id,
                    value=value,
                    skipped=False,
                )

        try:
            while state.current_step < len(steps):
                if self._interrupted:
                    self._handle_interrupt(state)
                    raise KeyboardInterrupt

                step = steps[state.current_step]

                # Skip steps that already have responses (Fix MT-007)
                if step.id in state.responses:
                    self.console.print(
                        f"[dim]Skipping {step.name} (provided via CLI)[/dim]"
                    )
                    state.current_step += 1
                    continue

                try:
                    state, response = self.execute_step(state, step)
                except NavigationCommand as nav:
                    state = self._handle_navigation(state, nav, steps)

                # Save state after each step (if state manager available)
                if self.state_manager:
                    self.state_manager.save(state)

            # Complete workflow
            return self.complete(state)

        except KeyboardInterrupt:
            self.cancel(state)
            raise

    def complete(self, state: WorkflowState) -> dict:
        """Complete workflow and return collected responses.

        Args:
            state: Final workflow state

        Returns:
            Dictionary of step_id -> response value
        """
        state.status = WorkflowStatus.COMPLETED

        # Delete state file on success
        if self.state_manager:
            self.state_manager.delete(state)

        # Show summary
        self.progress.show_summary(len(state.responses))

        # Return responses as simple dict
        return {
            step_id: resp.value
            for step_id, resp in state.responses.items()
        }

    def cancel(self, state: WorkflowState) -> None:
        """Cancel workflow and save state for resume.

        Args:
            state: Current workflow state
        """
        state.status = WorkflowStatus.INTERRUPTED

        # Save state for resume
        if self.state_manager:
            self.state_manager.save(state)

        # Show interrupted message
        total_steps = self._count_steps(state)
        self.progress.show_interrupted(state.current_step + 1, total_steps)

    # =========================================================================
    # Navigation Handling (T011)
    # =========================================================================

    def _handle_navigation(
        self,
        state: WorkflowState,
        nav: NavigationCommand,
        steps: list[WorkflowStep],
    ) -> WorkflowState:
        """Handle navigation commands (back/skip).

        Args:
            state: Current workflow state
            nav: Navigation command
            steps: List of workflow steps

        Returns:
            Updated workflow state
        """
        if nav.command == "back":
            return self._go_back(state, steps)
        elif nav.command == "skip":
            return self._skip_step(state, steps)
        return state

    def _go_back(
        self,
        state: WorkflowState,
        steps: list[WorkflowStep],
    ) -> WorkflowState:
        """Go back to the previous step.

        Args:
            state: Current workflow state
            steps: List of workflow steps

        Returns:
            Updated state with decreased step index
        """
        if state.current_step > 0:
            state.go_back()
            self.console.print("[info]Going back to previous step...[/info]")
        else:
            self.console.print("[warning]Already at first step[/warning]")
        return state

    def _skip_step(
        self,
        state: WorkflowState,
        steps: list[WorkflowStep],
    ) -> WorkflowState:
        """Skip the current optional step.

        Args:
            state: Current workflow state
            steps: List of workflow steps

        Returns:
            Updated state with step skipped
        """
        step = steps[state.current_step]

        if step.required:
            self.console.print("[error]Cannot skip required step[/error]")
            return state

        # Create skip response with default value
        response = StepResponse(
            step_id=step.id,
            value=step.default_value or "",
            skipped=True,
        )

        state.set_response(response)
        state.advance_step()
        self.progress.mark_skipped(step)

        return state

    # =========================================================================
    # Internal Methods
    # =========================================================================

    def _generate_state_id(self, command_name: str) -> str:
        """Generate a unique state ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{command_name}_{timestamp}"

    def _count_steps(self, state: WorkflowState) -> int:
        """Get total step count from state."""
        if state.total_steps > 0:
            return state.total_steps
        # Fallback for backwards compatibility
        return max(len(state.responses) + 1, state.current_step + 1)

    def _prompt_resume(self, state: WorkflowState) -> bool:
        """Prompt user to resume interrupted workflow."""
        self.console.print()
        self.console.print(
            f"[warning]Found interrupted workflow from "
            f"{state.updated_at.strftime('%Y-%m-%d %H:%M')}[/warning]"
        )
        self.console.print(
            f"[info]Progress: {len(state.responses)} steps completed[/info]"
        )
        return self.prompt.prompt_confirm("Resume where you left off?", default=True)

    def _setup_interrupt_handler(self) -> None:
        """Setup signal handler for Ctrl+C."""
        def handler(signum, frame):
            self._interrupted = True

        signal.signal(signal.SIGINT, handler)

    def _handle_interrupt(self, state: WorkflowState) -> None:
        """Handle interrupt signal."""
        self._interrupted = False
        self.cancel(state)
