"""GitHub Epic model for representing GitHub issues labeled as 'epic'.

This module provides the GitHubEpic dataclass for storing and managing
GitHub epic issue data fetched from the GitHub API.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class GitHubEpic:
    """Represents a GitHub issue labeled as 'epic'.

    Attributes:
        number: GitHub issue number (unique identifier)
        title: Issue title
        state: Issue state (open or closed)
        labels: List of label names attached to the issue
        body: Issue description/body text
        url: GitHub issue URL
        created_at: When the issue was created
        updated_at: When the issue was last updated
        features: List of linked feature issues (populated by service layer)
    """

    number: int
    title: str
    state: str
    labels: List[str]
    body: str
    url: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    features: List["GitHubFeature"] = field(default_factory=list)  # type: ignore

    def __post_init__(self):
        """Validate epic data after initialization."""
        if self.number <= 0:
            raise ValueError(f"Epic number must be positive, got {self.number}")

        if self.state not in ("open", "closed"):
            raise ValueError(f"Epic state must be 'open' or 'closed', got {self.state}")

        if not self.url or "github.com" not in self.url:
            raise ValueError(f"Invalid GitHub URL: {self.url}")

    @property
    def is_open(self) -> bool:
        """Check if the epic is currently open.

        Returns:
            True if epic state is 'open', False otherwise
        """
        return self.state == "open"

    @property
    def has_epic_label(self) -> bool:
        """Check if the issue has the 'epic' label.

        Returns:
            True if 'epic' label is present, False otherwise
        """
        return "epic" in (label.lower() for label in self.labels)

    def get_priority_labels(self) -> List[str]:
        """Extract priority-related labels from the epic.

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
    def from_gh_json(cls, data: dict) -> "GitHubEpic":
        """Create GitHubEpic from GitHub CLI JSON response.

        Args:
            data: Dictionary from gh issue list --json output

        Returns:
            GitHubEpic instance

        Examples:
            >>> json_data = {
            ...     "number": 577,
            ...     "title": "[Epic]: Test",
            ...     "state": "open",
            ...     "labels": [{"name": "epic"}],
            ...     "body": "Description",
            ...     "url": "https://github.com/owner/repo/issues/577",
            ...     "createdAt": "2026-01-21T10:00:00Z",
            ...     "updatedAt": "2026-01-21T15:30:00Z"
            ... }
            >>> epic = GitHubEpic.from_gh_json(json_data)
            >>> epic.number
            577
        """
        # Extract label names from label objects
        label_names = [label.get("name", "") for label in data.get("labels", [])]

        # Parse timestamps
        created_at = None
        if data.get("createdAt"):
            try:
                created_at = datetime.fromisoformat(data["createdAt"].replace("Z", "+00:00"))
            except ValueError:
                pass

        updated_at = None
        if data.get("updatedAt"):
            try:
                updated_at = datetime.fromisoformat(data["updatedAt"].replace("Z", "+00:00"))
            except ValueError:
                pass

        return cls(
            number=data["number"],
            title=data["title"],
            state=data.get("state", "open"),
            labels=label_names,
            body=data.get("body", ""),
            url=data["url"],
            created_at=created_at,
            updated_at=updated_at,
        )

    def to_dict(self) -> dict:
        """Convert epic to dictionary for serialization.

        Returns:
            Dictionary representation of the epic in GitHub API format
        """
        return {
            "number": self.number,
            "title": self.title,
            "state": self.state,
            "labels": [{"name": label} for label in self.labels],  # Convert to GitHub API format
            "body": self.body,
            "url": self.url,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
            "features": [f.to_dict() for f in self.features] if hasattr(self.features[0] if self.features else None, "to_dict") else [],
        }


# Import here to avoid circular dependency
from .github_feature import GitHubFeature  # noqa: E402
