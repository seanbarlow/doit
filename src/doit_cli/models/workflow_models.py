"""Data models and exceptions for the guided workflow system.

This module contains dataclasses for workflow definitions, state management,
and validation results, along with the exception hierarchy for workflow errors.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Literal


# =============================================================================
# Enums
# =============================================================================


class WorkflowStatus(str, Enum):
    """Status of a workflow execution."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    INTERRUPTED = "interrupted"


# =============================================================================
# Core Dataclasses (T003)
# =============================================================================


@dataclass
class WorkflowStep:
    """Defines a single step in a guided workflow.

    Attributes:
        id: Step identifier (e.g., "select-ai-tool")
        name: Display name shown in progress
        prompt_text: Question or instruction for user
        required: Whether step must be completed
        order: Sequence position (0-indexed)
        validation_type: Validator class name (e.g., "PathExistsValidator")
        default_value: Value used when skipped or non-interactive
        options: For choice steps: {key: description} mapping
    """

    id: str
    name: str
    prompt_text: str
    required: bool
    order: int
    validation_type: str | None = None
    default_value: str | None = None
    options: dict[str, str] | None = None

    def __post_init__(self) -> None:
        """Validate step configuration."""
        if not self.required and self.default_value is None:
            raise ValueError(
                f"Optional step '{self.id}' must have a default_value"
            )


@dataclass
class Workflow:
    """Defines a guided workflow for a specific command.

    Attributes:
        id: Unique identifier (e.g., "init-workflow")
        command_name: CLI command this workflow belongs to
        description: Human-readable workflow description
        interactive: Whether this workflow prompts for input
        steps: Ordered list of workflow steps
    """

    id: str
    command_name: str
    description: str
    interactive: bool
    steps: list[WorkflowStep] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate workflow configuration."""
        if not self.steps:
            raise ValueError(f"Workflow '{self.id}' must have at least one step")

        # Validate step order uniqueness
        orders = [s.order for s in self.steps]
        if len(orders) != len(set(orders)):
            raise ValueError(f"Workflow '{self.id}' has duplicate step orders")

        # Validate step ID uniqueness
        ids = [s.id for s in self.steps]
        if len(ids) != len(set(ids)):
            raise ValueError(f"Workflow '{self.id}' has duplicate step IDs")

    def get_step_by_id(self, step_id: str) -> WorkflowStep | None:
        """Get a step by its ID."""
        for step in self.steps:
            if step.id == step_id:
                return step
        return None

    def get_step_by_order(self, order: int) -> WorkflowStep | None:
        """Get a step by its order index."""
        for step in self.steps:
            if step.order == order:
                return step
        return None


# =============================================================================
# State Dataclasses (T004)
# =============================================================================


@dataclass
class StepResponse:
    """Records a user's response to a workflow step.

    Attributes:
        step_id: Which step this responds to
        value: User-provided or default value
        skipped: Whether step was skipped
        responded_at: When response was captured
    """

    step_id: str
    value: str
    skipped: bool = False
    responded_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "step_id": self.step_id,
            "value": self.value,
            "skipped": self.skipped,
            "responded_at": self.responded_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "StepResponse":
        """Create from dictionary (JSON deserialization)."""
        return cls(
            step_id=data["step_id"],
            value=data["value"],
            skipped=data.get("skipped", False),
            responded_at=datetime.fromisoformat(data["responded_at"]),
        )


@dataclass
class WorkflowState:
    """Persists workflow progress for recovery.

    Attributes:
        id: Unique state identifier
        workflow_id: Which workflow is running
        command_name: Command being executed
        current_step: Index of current step
        total_steps: Total number of steps in workflow
        status: Current workflow status
        created_at: When workflow started
        updated_at: Last state update
        responses: step_id -> StepResponse mapping
    """

    id: str
    workflow_id: str
    command_name: str
    current_step: int = 0
    total_steps: int = 0
    status: WorkflowStatus = WorkflowStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    responses: dict[str, StepResponse] = field(default_factory=dict)

    def get_response(self, step_id: str) -> StepResponse | None:
        """Get response for a specific step."""
        return self.responses.get(step_id)

    def set_response(self, response: StepResponse) -> None:
        """Set or update a step response."""
        self.responses[response.step_id] = response
        self.updated_at = datetime.now()

    def advance_step(self) -> None:
        """Move to the next step."""
        self.current_step += 1
        self.updated_at = datetime.now()

    def go_back(self) -> bool:
        """Go back to previous step. Returns False if already at first step."""
        if self.current_step > 0:
            self.current_step -= 1
            self.updated_at = datetime.now()
            return True
        return False

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "workflow_id": self.workflow_id,
            "command_name": self.command_name,
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "responses": {
                step_id: resp.to_dict()
                for step_id, resp in self.responses.items()
            },
        }

    @classmethod
    def from_dict(cls, data: dict) -> "WorkflowState":
        """Create from dictionary (JSON deserialization)."""
        responses = {
            step_id: StepResponse.from_dict(resp_data)
            for step_id, resp_data in data.get("responses", {}).items()
        }
        return cls(
            id=data["id"],
            workflow_id=data["workflow_id"],
            command_name=data["command_name"],
            current_step=data.get("current_step", 0),
            total_steps=data.get("total_steps", 0),
            status=WorkflowStatus(data.get("status", "pending")),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            responses=responses,
        )


# =============================================================================
# Validation Result
# =============================================================================


@dataclass
class ValidationResult:
    """Result of validating a step input.

    Attributes:
        passed: Whether validation passed
        error_message: Error description if failed
        suggestion: Guidance for fixing the error
    """

    passed: bool
    error_message: str | None = None
    suggestion: str | None = None

    @classmethod
    def success(cls) -> "ValidationResult":
        """Create a successful validation result."""
        return cls(passed=True)

    @classmethod
    def failure(
        cls, error_message: str, suggestion: str | None = None
    ) -> "ValidationResult":
        """Create a failed validation result."""
        return cls(passed=False, error_message=error_message, suggestion=suggestion)


# =============================================================================
# Exception Hierarchy (T005)
# =============================================================================


class WorkflowError(Exception):
    """Base exception for workflow errors."""

    pass


class ValidationError(WorkflowError):
    """Input validation failed.

    Attributes:
        result: The validation result containing error details
    """

    def __init__(self, result: ValidationResult, message: str | None = None) -> None:
        self.result = result
        msg = message or result.error_message or "Validation failed"
        super().__init__(msg)


class NavigationCommand(WorkflowError):
    """User requested navigation (not an error).

    This exception is used for flow control when user types 'back' or 'skip'.

    Attributes:
        command: The navigation command ("back" or "skip")
    """

    def __init__(self, command: Literal["back", "skip"]) -> None:
        self.command = command
        super().__init__(f"Navigation: {command}")


class StateCorruptionError(WorkflowError):
    """State file is corrupted or invalid.

    Attributes:
        state_path: Path to the corrupted state file
    """

    def __init__(self, state_path: Path, message: str | None = None) -> None:
        self.state_path = state_path
        msg = message or f"State file corrupted: {state_path}"
        super().__init__(msg)
