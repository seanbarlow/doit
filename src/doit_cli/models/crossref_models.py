"""Models for cross-reference support between specs and tasks."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class CoverageStatus(str, Enum):
    """Coverage status for a requirement."""

    UNCOVERED = "uncovered"
    PARTIAL = "partial"
    COVERED = "covered"


@dataclass
class Requirement:
    """A functional requirement extracted from spec.md.

    Attributes:
        id: Requirement ID in FR-XXX format (e.g., FR-001)
        spec_path: Path to the spec.md file containing this requirement
        description: Full requirement text
        line_number: Line number in spec.md where requirement is defined
    """

    id: str
    spec_path: str
    description: str
    line_number: int


@dataclass
class TaskReference:
    """A cross-reference from a task to a requirement.

    Attributes:
        requirement_id: The FR-XXX ID being referenced
        position: Order in the reference list (0-indexed)
    """

    requirement_id: str
    position: int = 0


@dataclass
class Task:
    """An implementation task extracted from tasks.md.

    Attributes:
        id: Auto-generated hash of normalized description
        tasks_file: Path to the tasks.md file containing this task
        description: Task text (without references)
        completed: Checkbox state (True if [x] or [X])
        line_number: Line number in tasks.md
        references: List of FR-XXX references found in this task
    """

    id: str
    tasks_file: str
    description: str
    completed: bool
    line_number: int
    references: list[TaskReference] = field(default_factory=list)

    @property
    def requirement_ids(self) -> list[str]:
        """Get list of requirement IDs this task references."""
        return [ref.requirement_id for ref in self.references]


@dataclass
class CrossReference:
    """A link between a task and a requirement.

    Attributes:
        requirement_id: FK to Requirement.id (FR-XXX format)
        task_id: FK to Task.id
        position: Order when multiple refs in same task (0-indexed)
    """

    requirement_id: str
    task_id: str
    position: int = 0

    @property
    def id(self) -> str:
        """Composite key for the cross-reference."""
        return f"{self.requirement_id}:{self.task_id}"


@dataclass
class RequirementCoverage:
    """Coverage information for a single requirement.

    Attributes:
        requirement: The requirement being tracked
        tasks: List of tasks that implement this requirement
        status: Coverage status (uncovered, partial, covered)
    """

    requirement: Requirement
    tasks: list[Task] = field(default_factory=list)

    @property
    def task_count(self) -> int:
        """Number of tasks implementing this requirement."""
        return len(self.tasks)

    @property
    def completed_count(self) -> int:
        """Number of completed tasks implementing this requirement."""
        return sum(1 for t in self.tasks if t.completed)

    @property
    def status(self) -> CoverageStatus:
        """Derive coverage status from task states."""
        if not self.tasks:
            return CoverageStatus.UNCOVERED
        if all(t.completed for t in self.tasks):
            return CoverageStatus.COVERED
        return CoverageStatus.PARTIAL

    @property
    def is_covered(self) -> bool:
        """Whether this requirement has at least one linked task."""
        return len(self.tasks) > 0


@dataclass
class CoverageReport:
    """Aggregate coverage report for a specification.

    Attributes:
        spec_path: Path to the spec.md file
        requirements: List of RequirementCoverage objects
        orphaned_references: Task references to non-existent requirements
    """

    spec_path: str
    requirements: list[RequirementCoverage] = field(default_factory=list)
    orphaned_references: list[tuple[Task, str]] = field(default_factory=list)

    @property
    def total_count(self) -> int:
        """Total number of requirements."""
        return len(self.requirements)

    @property
    def covered_count(self) -> int:
        """Number of requirements with at least one linked task."""
        return sum(1 for r in self.requirements if r.is_covered)

    @property
    def uncovered_count(self) -> int:
        """Number of requirements with no linked tasks."""
        return self.total_count - self.covered_count

    @property
    def coverage_percent(self) -> float:
        """Coverage percentage (0-100)."""
        if self.total_count == 0:
            return 100.0
        return (self.covered_count / self.total_count) * 100

    @property
    def is_fully_covered(self) -> bool:
        """Whether all requirements have at least one linked task."""
        return self.covered_count == self.total_count

    def get_uncovered_requirements(self) -> list[Requirement]:
        """Get list of requirements with no linked tasks."""
        return [rc.requirement for rc in self.requirements if not rc.is_covered]

    def get_requirement_coverage(
        self, requirement_id: str
    ) -> Optional[RequirementCoverage]:
        """Get coverage info for a specific requirement."""
        for rc in self.requirements:
            if rc.requirement.id == requirement_id:
                return rc
        return None
