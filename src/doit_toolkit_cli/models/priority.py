"""Priority level constants for roadmap priorities.

This module defines the priority level mappings from P1-P4 to their display names
and milestone titles used in the GitHub milestone generation feature.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class Priority:
    """Represents a priority level constant.

    Attributes:
        level: Priority level code (e.g., "P1", "P2", "P3", "P4")
        display_name: Human-readable priority name (e.g., "Critical", "High Priority")
        description: Long-form description from roadmap header
        sort_order: Numeric order for priority (1-4)
    """

    level: str
    display_name: str
    description: str
    sort_order: int

    @property
    def milestone_title(self) -> str:
        """Get the milestone title for this priority.

        Returns:
            Milestone title in format "P1 - Critical"
        """
        return f"{self.level} - {self.display_name}"

    @property
    def milestone_description(self) -> str:
        """Get the auto-generated milestone description.

        Returns:
            Description text for milestone
        """
        return f"Auto-managed by doit. Contains all {self.level} - {self.display_name} roadmap items."


# Priority level constants with mappings
PRIORITIES: Dict[str, Priority] = {
    "P1": Priority(
        level="P1",
        display_name="Critical",
        description="Must Have for MVP",
        sort_order=1
    ),
    "P2": Priority(
        level="P2",
        display_name="High Priority",
        description="Significant Business Value",
        sort_order=2
    ),
    "P3": Priority(
        level="P3",
        display_name="Medium Priority",
        description="Valuable",
        sort_order=3
    ),
    "P4": Priority(
        level="P4",
        display_name="Low Priority",
        description="Nice to Have",
        sort_order=4
    )
}

# Ordered list of priority levels (P1 to P4)
PRIORITY_LEVELS = ["P1", "P2", "P3", "P4"]


def get_priority(level: str) -> Priority:
    """Get Priority object for a given level.

    Args:
        level: Priority level code (e.g., "P1")

    Returns:
        Priority object

    Raises:
        ValueError: If priority level is invalid
    """
    if level not in PRIORITIES:
        raise ValueError(f"Invalid priority level: {level}. Must be one of {PRIORITY_LEVELS}")
    return PRIORITIES[level]


def is_valid_priority(level: str) -> bool:
    """Check if a priority level is valid.

    Args:
        level: Priority level code to validate

    Returns:
        True if valid, False otherwise
    """
    return level in PRIORITIES
