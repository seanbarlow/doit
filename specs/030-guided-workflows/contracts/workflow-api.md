# Workflow API Contract

**Feature**: 030-guided-workflows
**Date**: 2026-01-15
**Type**: Internal Python API (not HTTP)

## Overview

This document defines the internal API contracts for the guided workflow system. These are Python interfaces that components must implement.

---

## WorkflowEngine

Core orchestrator for guided workflows.

### Interface

```python
class WorkflowEngine(Protocol):
    """Orchestrates guided workflow execution."""

    def start(self, workflow: Workflow) -> WorkflowState:
        """Start a new workflow or resume interrupted one.

        Args:
            workflow: Workflow definition to execute

        Returns:
            Initial or resumed WorkflowState

        Raises:
            WorkflowError: If workflow cannot be started
        """
        ...

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
            ValidationError: If step input is invalid
            KeyboardInterrupt: If user cancels
        """
        ...

    def complete(self, state: WorkflowState) -> dict:
        """Complete workflow and return collected responses.

        Args:
            state: Final workflow state

        Returns:
            Dictionary of step_id -> response value
        """
        ...

    def cancel(self, state: WorkflowState) -> None:
        """Cancel workflow and save state for resume.

        Args:
            state: Current workflow state
        """
        ...
```

### Behavior Contract

| Scenario | Input | Expected Output |
|----------|-------|-----------------|
| Start new workflow | Fresh workflow | State with status=pending |
| Resume interrupted | Workflow with saved state | State loaded from file |
| Execute required step | User provides value | State updated, response saved |
| Execute optional step | User skips | Step marked skipped, default used |
| Navigate back | User types 'back' | Previous step re-prompted |
| Complete workflow | All required steps done | Responses returned, state deleted |
| Cancel workflow | Ctrl+C pressed | State saved, exit code 1 |

---

## StateManager

Handles workflow state persistence.

### Interface

```python
class StateManager(Protocol):
    """Manages workflow state persistence."""

    def save(self, state: WorkflowState) -> Path:
        """Save workflow state to file.

        Args:
            state: State to persist

        Returns:
            Path to saved state file
        """
        ...

    def load(self, command_name: str) -> WorkflowState | None:
        """Load most recent state for a command.

        Args:
            command_name: Command to find state for

        Returns:
            WorkflowState if found, None otherwise
        """
        ...

    def delete(self, state: WorkflowState) -> None:
        """Delete state file after completion.

        Args:
            state: State to delete
        """
        ...

    def list_interrupted(self) -> list[WorkflowState]:
        """List all interrupted workflow states.

        Returns:
            List of interrupted states
        """
        ...

    def cleanup_stale(self, max_age_days: int = 7) -> int:
        """Remove state files older than threshold.

        Args:
            max_age_days: Maximum age before cleanup

        Returns:
            Number of files removed
        """
        ...
```

### State File Format

```json
{
  "id": "init_20260115_143022",
  "workflow_id": "init-workflow",
  "command_name": "init",
  "current_step": 2,
  "status": "interrupted",
  "created_at": "2026-01-15T14:30:22Z",
  "updated_at": "2026-01-15T14:31:45Z",
  "responses": {
    "select-ai-tool": {
      "value": "claude",
      "skipped": false,
      "responded_at": "2026-01-15T14:30:35Z"
    },
    "select-script-type": {
      "value": "bash",
      "skipped": false,
      "responded_at": "2026-01-15T14:31:02Z"
    }
  }
}
```

---

## InputValidator

Validates step inputs in real-time.

### Interface

```python
class InputValidator(Protocol):
    """Base protocol for step validators."""

    def validate(
        self,
        value: str,
        step: WorkflowStep,
        context: dict[str, StepResponse],
    ) -> ValidationResult:
        """Validate a step input value.

        Args:
            value: User-provided input
            step: Step being validated
            context: Previous step responses

        Returns:
            ValidationResult with pass/fail and messages
        """
        ...
```

### Built-in Validators

| Validator | Purpose | Error Message Pattern |
|-----------|---------|----------------------|
| `RequiredValidator` | Non-empty value | "This field is required" |
| `PathExistsValidator` | File/dir exists | "Path does not exist: {path}" |
| `ChoiceValidator` | Value in options | "Invalid choice. Options: {options}" |
| `PatternValidator` | Regex match | "Value must match pattern: {pattern}" |
| `ConflictValidator` | No conflicts with context | "Conflicts with {step}: {reason}" |

---

## InteractivePrompt

Handles user input collection.

### Interface

```python
class InteractivePrompt(Protocol):
    """Collects user input for workflow steps."""

    def prompt(
        self,
        step: WorkflowStep,
        validator: InputValidator | None = None,
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
        ...

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
        """
        ...

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
        ...
```

### Navigation Commands

| Input | Action |
|-------|--------|
| `back` | Return to previous step |
| `skip` | Skip current optional step |
| Enter (empty) | Accept default value or skip if optional |
| Ctrl+C | Cancel workflow, save state |
| Escape | Cancel current prompt (if in selection) |

---

## ProgressDisplay

Shows workflow progress to user.

### Interface

```python
class ProgressDisplay(Protocol):
    """Displays workflow progress."""

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
        ...

    def mark_complete(self, step: WorkflowStep) -> None:
        """Mark step as completed in display."""
        ...

    def mark_skipped(self, step: WorkflowStep) -> None:
        """Mark step as skipped in display."""
        ...

    def show_error(
        self,
        step: WorkflowStep,
        error: ValidationResult,
    ) -> None:
        """Show validation error with suggestion."""
        ...
```

### Display Format

```
Step 2 of 5: Select Script Type

  ✓ Select AI Tool: claude
  ▶ Select Script Type
    Configure Project Name
    Set Output Directory
    Confirm Settings

Use arrow keys to select, Enter to confirm, 'back' to go back.
```

---

## Error Handling

### Exception Hierarchy

```python
class WorkflowError(Exception):
    """Base exception for workflow errors."""
    pass

class ValidationError(WorkflowError):
    """Input validation failed."""
    result: ValidationResult

class NavigationCommand(WorkflowError):
    """User requested navigation (not an error)."""
    command: Literal["back", "skip"]

class StateCorruptionError(WorkflowError):
    """State file is corrupted or invalid."""
    state_path: Path
```

### Error Responses

| Error | User Message | Exit Code |
|-------|--------------|-----------|
| ValidationError | Show error + suggestion | (continue) |
| NavigationCommand | Execute navigation | (continue) |
| StateCorruptionError | "State file corrupted. Starting fresh." | (continue) |
| KeyboardInterrupt | "Workflow interrupted. Progress saved." | 1 |
| WorkflowError | Error message | 1 |
