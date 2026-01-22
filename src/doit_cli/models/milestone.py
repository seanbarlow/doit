"""Milestone model for GitHub milestone data.

This module defines the Milestone dataclass used to represent GitHub milestones
in the roadmap milestone generation feature.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Milestone:
    """Represents a GitHub milestone.

    Attributes:
        number: GitHub-assigned milestone number (primary key)
        title: Milestone title (e.g., "P1 - Critical")
        description: Milestone description
        state: Either "open" or "closed"
        url: Full GitHub URL to milestone
    """

    number: int
    title: str
    description: str
    state: str  # "open" or "closed"
    url: str

    def __post_init__(self):
        """Validate milestone state."""
        if self.state not in ("open", "closed"):
            raise ValueError(f"Invalid milestone state: {self.state}. Must be 'open' or 'closed'.")

    @property
    def is_open(self) -> bool:
        """Check if milestone is open."""
        return self.state == "open"

    @property
    def is_closed(self) -> bool:
        """Check if milestone is closed."""
        return self.state == "closed"
