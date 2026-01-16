"""Models for spec status dashboard."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

from .validation_models import ValidationResult


class SpecState(str, Enum):
    """Valid specification statuses parsed from spec.md frontmatter.

    Values:
        DRAFT: Initial state, not yet validated by git hooks
        IN_PROGRESS: Active development, validated on commit
        COMPLETE: Implementation finished, pending approval
        APPROVED: Fully approved and merged
        ERROR: Could not parse status from file
    """

    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    APPROVED = "approved"
    ERROR = "error"

    @classmethod
    def from_string(cls, value: str) -> "SpecState":
        """Parse a status string into a SpecState enum.

        Args:
            value: Status string from spec file (e.g., "Draft", "In Progress")

        Returns:
            Corresponding SpecState enum value, or ERROR if not recognized.
        """
        # Normalize: lowercase and replace spaces with underscores
        normalized = value.lower().strip().replace(" ", "_")

        # Map common variations
        mapping = {
            "draft": cls.DRAFT,
            "in_progress": cls.IN_PROGRESS,
            "inprogress": cls.IN_PROGRESS,
            "in-progress": cls.IN_PROGRESS,
            "complete": cls.COMPLETE,
            "completed": cls.COMPLETE,
            "approved": cls.APPROVED,
            "done": cls.APPROVED,
        }

        return mapping.get(normalized, cls.ERROR)

    @property
    def display_name(self) -> str:
        """Human-readable display name for the status."""
        names = {
            SpecState.DRAFT: "Draft",
            SpecState.IN_PROGRESS: "In Progress",
            SpecState.COMPLETE: "Complete",
            SpecState.APPROVED: "Approved",
            SpecState.ERROR: "Error",
        }
        return names.get(self, "Unknown")

    @property
    def emoji(self) -> str:
        """Emoji representation for terminal display."""
        emojis = {
            SpecState.DRAFT: "📝",
            SpecState.IN_PROGRESS: "🔄",
            SpecState.COMPLETE: "✅",
            SpecState.APPROVED: "🏆",
            SpecState.ERROR: "❌",
        }
        return emojis.get(self, "❓")


@dataclass
class SpecStatus:
    """Represents the parsed status of a single specification.

    Attributes:
        name: Spec name derived from directory name (e.g., "032-status-dashboard")
        path: Full path to the spec.md file
        status: Current status (Draft, In Progress, Complete, Approved)
        last_modified: File modification timestamp
        validation_result: Result from SpecValidator (if validated)
        is_blocking: Whether this spec would block commits
        error: Parse error message if spec couldn't be read
    """

    name: str
    path: Path
    status: SpecState
    last_modified: datetime
    validation_result: Optional[ValidationResult] = None
    is_blocking: bool = False
    error: Optional[str] = None

    @property
    def validation_passed(self) -> bool:
        """Check if validation passed (or wasn't run)."""
        if self.validation_result is None:
            return True  # No validation = no failures
        return self.validation_result.error_count == 0

    @property
    def validation_score(self) -> int:
        """Get validation quality score (0-100)."""
        if self.validation_result is None:
            return 100
        return self.validation_result.quality_score


@dataclass
class StatusReport:
    """Aggregated report containing all spec statuses and summary statistics.

    Attributes:
        specs: All parsed spec statuses
        generated_at: Report generation timestamp
        project_root: Root directory of the project
    """

    specs: list[SpecStatus] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.now)
    project_root: Path = field(default_factory=Path.cwd)

    @property
    def total_count(self) -> int:
        """Total number of specs."""
        return len(self.specs)

    @property
    def by_status(self) -> dict[SpecState, int]:
        """Count of specs grouped by status."""
        counts: dict[SpecState, int] = {state: 0 for state in SpecState}
        for spec in self.specs:
            counts[spec.status] = counts.get(spec.status, 0) + 1
        return counts

    @property
    def blocking_count(self) -> int:
        """Number of specs blocking commits."""
        return sum(1 for spec in self.specs if spec.is_blocking)

    @property
    def validation_pass_count(self) -> int:
        """Specs passing validation."""
        return sum(1 for spec in self.specs if spec.validation_passed)

    @property
    def validation_fail_count(self) -> int:
        """Specs failing validation."""
        return sum(1 for spec in self.specs if not spec.validation_passed)

    @property
    def completion_percentage(self) -> float:
        """Percentage of Complete + Approved specs."""
        if self.total_count == 0:
            return 0.0
        complete_count = sum(
            1
            for spec in self.specs
            if spec.status in (SpecState.COMPLETE, SpecState.APPROVED)
        )
        return (complete_count / self.total_count) * 100

    @property
    def is_ready_to_commit(self) -> bool:
        """True if no blocking specs."""
        return self.blocking_count == 0

    @property
    def draft_count(self) -> int:
        """Number of draft specs."""
        return self.by_status.get(SpecState.DRAFT, 0)

    @property
    def in_progress_count(self) -> int:
        """Number of in-progress specs."""
        return self.by_status.get(SpecState.IN_PROGRESS, 0)

    @property
    def complete_count(self) -> int:
        """Number of complete specs."""
        return self.by_status.get(SpecState.COMPLETE, 0)

    @property
    def approved_count(self) -> int:
        """Number of approved specs."""
        return self.by_status.get(SpecState.APPROVED, 0)
