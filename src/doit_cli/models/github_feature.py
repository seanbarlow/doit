"""GitHub Feature model for representing feature issues linked to epics.

This module provides the GitHubFeature dataclass for storing GitHub feature
issues that are part of an epic.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class GitHubFeature:
    """Represents a GitHub issue labeled as 'feature' that belongs to an epic.

    Attributes:
        number: GitHub issue number
        title: Issue title
        state: Issue state (open or closed)
        labels: List of label names attached to the issue
        epic_number: Parent epic issue number
        url: GitHub issue URL
    """

    number: int
    title: str
    state: str
    labels: List[str]
    epic_number: int
    url: str

    def __post_init__(self):
        """Validate feature data after initialization."""
        if self.number <= 0:
            raise ValueError(f"Feature number must be positive, got {self.number}")

        if self.epic_number <= 0:
            raise ValueError(f"Epic number must be positive, got {self.epic_number}")

        if self.state not in ("open", "closed"):
            raise ValueError(f"Feature state must be 'open' or 'closed', got {self.state}")

        if not self.url or "github.com" not in self.url:
            raise ValueError(f"Invalid GitHub URL: {self.url}")

    @property
    def is_open(self) -> bool:
        """Check if the feature is currently open.

        Returns:
            True if feature state is 'open', False otherwise
        """
        return self.state == "open"

    def get_priority_labels(self) -> List[str]:
        """Extract priority-related labels from the feature.

        Returns:
            List of labels that contain 'priority' or are priority keywords
        """
        priority_keywords = {"priority", "p1", "p2", "p3", "p4", "critical", "high", "medium", "low"}
        return [
            label
            for label in self.labels
            if any(keyword in label.lower() for keyword in priority_keywords)
        ]

    @classmethod
    def from_gh_json(cls, data: dict, epic_number: int) -> "GitHubFeature":
        """Create GitHubFeature from GitHub CLI JSON response.

        Args:
            data: Dictionary from gh issue list --json output
            epic_number: Parent epic issue number

        Returns:
            GitHubFeature instance

        Examples:
            >>> json_data = {
            ...     "number": 578,
            ...     "title": "[Feature]: Test",
            ...     "state": "open",
            ...     "labels": [{"name": "feature"}],
            ...     "url": "https://github.com/owner/repo/issues/578"
            ... }
            >>> feature = GitHubFeature.from_gh_json(json_data, 577)
            >>> feature.epic_number
            577
        """
        # Extract label names from label objects
        label_names = [label.get("name", "") for label in data.get("labels", [])]

        return cls(
            number=data["number"],
            title=data["title"],
            state=data.get("state", "open"),
            labels=label_names,
            epic_number=epic_number,
            url=data["url"],
        )

    def to_dict(self) -> dict:
        """Convert feature to dictionary for serialization.

        Returns:
            Dictionary representation of the feature
        """
        return {
            "number": self.number,
            "title": self.title,
            "state": self.state,
            "labels": self.labels,
            "epic_number": self.epic_number,
            "url": self.url,
        }
