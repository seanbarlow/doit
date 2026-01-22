"""Sync operation models for tracking milestone sync results.

This module defines dataclasses for tracking the results of milestone sync operations,
including counts of created/updated/skipped items and detailed result items.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from enum import Enum


class SyncAction(Enum):
    """Types of sync actions."""

    CREATE_MILESTONE = "create_milestone"
    ASSIGN_EPIC = "assign_epic"
    CLOSE_MILESTONE = "close_milestone"


class SyncStatus(Enum):
    """Status of a sync action."""

    SUCCESS = "success"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class SyncResultItem:
    """Represents a single action taken or skipped during a sync operation.

    Attributes:
        id: Unique result identifier
        operation_id: Foreign key to parent SyncOperation
        action: Type of action (create_milestone, assign_epic, close_milestone)
        target: Milestone title or epic number
        status: Result status (success, skipped, error)
        message: Human-readable status message
    """

    id: str
    operation_id: str
    action: SyncAction
    target: str
    status: SyncStatus
    message: str


@dataclass
class SyncOperation:
    """Represents a single execution of the milestone sync command.

    Attributes:
        id: Timestamp-based identifier (e.g., "sync_20260122_143000")
        started_at: When sync began
        completed_at: When sync finished (None if still running)
        dry_run: True if run with --dry-run flag
        milestones_created: Count of milestones created
        epics_assigned: Count of epics assigned/updated
        errors: Count of errors encountered
        results: List of detailed sync result items
    """

    id: str
    started_at: datetime
    completed_at: datetime | None = None
    dry_run: bool = False
    milestones_created: int = 0
    epics_assigned: int = 0
    errors: int = 0
    results: List[SyncResultItem] = field(default_factory=list)

    @property
    def is_complete(self) -> bool:
        """Check if sync operation is complete."""
        return self.completed_at is not None

    @property
    def duration_seconds(self) -> float | None:
        """Get sync duration in seconds.

        Returns:
            Duration in seconds if complete, None if still running
        """
        if not self.is_complete:
            return None
        return (self.completed_at - self.started_at).total_seconds()

    def add_result(self, action: SyncAction, target: str, status: SyncStatus, message: str) -> None:
        """Add a sync result item.

        Args:
            action: Type of action performed
            target: Target identifier (milestone title or epic number)
            status: Result status
            message: Status message
        """
        result_id = f"{self.id}_result_{len(self.results) + 1}"
        result = SyncResultItem(
            id=result_id,
            operation_id=self.id,
            action=action,
            target=target,
            status=status,
            message=message
        )
        self.results.append(result)

        # Update counters based on action and status
        if status == SyncStatus.SUCCESS:
            if action == SyncAction.CREATE_MILESTONE:
                self.milestones_created += 1
            elif action == SyncAction.ASSIGN_EPIC:
                self.epics_assigned += 1
        elif status == SyncStatus.ERROR:
            self.errors += 1

    def get_summary(self) -> str:
        """Get a summary string of sync operation results.

        Returns:
            Formatted summary string
        """
        lines = []
        lines.append("Sync Summary:")
        lines.append(f"  • Milestones created: {self.milestones_created}")
        lines.append(f"  • Epics assigned: {self.epics_assigned}")
        lines.append(f"  • Errors: {self.errors}")

        if self.dry_run:
            lines.insert(0, "🔍 Dry Run - No changes made")

        if self.duration_seconds is not None:
            lines.append(f"  • Duration: {self.duration_seconds:.2f}s")

        return "\n".join(lines)
