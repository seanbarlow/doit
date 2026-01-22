"""Roadmap item model for representing features and requirements in the roadmap.

This module provides the RoadmapItem dataclass for managing roadmap entries
from both local roadmap file and GitHub epics.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class RoadmapItem:
    """Represents a planned feature or requirement in the roadmap.

    Attributes:
        title: Feature title (e.g., "User authentication")
        priority: Priority level (P1, P2, P3, or P4)
        description: Detailed description of the feature
        rationale: Business rationale for this priority
        feature_branch: Branch reference like [039-feature-name] (optional)
        status: Current status (pending, in-progress, or completed)
        source: Origin of this item (local, github, or merged)
        github_number: Associated GitHub issue number (optional)
        github_url: GitHub issue URL (optional)
        features: List of linked GitHubFeature objects (optional, from GitHub epics)
    """

    title: str
    priority: str
    description: str
    rationale: str = ""
    feature_branch: Optional[str] = None
    status: str = "pending"
    source: str = "local"
    github_number: Optional[int] = None
    github_url: Optional[str] = None
    features: list = None  # List of GitHubFeature objects

    def __post_init__(self):
        """Validate roadmap item after initialization."""
        if not self.title:
            raise ValueError("Roadmap item title cannot be empty")

        if self.priority not in ("P1", "P2", "P3", "P4"):
            raise ValueError(f"Priority must be P1, P2, P3, or P4, got {self.priority}")

        if self.status not in ("pending", "in-progress", "completed"):
            raise ValueError(f"Status must be pending, in-progress, or completed, got {self.status}")

        if self.source not in ("local", "github", "merged"):
            raise ValueError(f"Source must be local, github, or merged, got {self.source}")

        # If github_number is set, github_url should also be set
        if self.github_number is not None and not self.github_url:
            raise ValueError("github_url must be provided when github_number is set")

        # Initialize features as empty list if None
        if self.features is None:
            self.features = []

    @property
    def is_from_github(self) -> bool:
        """Check if this item originated from GitHub.

        Returns:
            True if source is 'github' or 'merged', False otherwise
        """
        return self.source in ("github", "merged")

    @property
    def has_feature_branch(self) -> bool:
        """Check if this item has a feature branch reference.

        Returns:
            True if feature_branch is set, False otherwise
        """
        return self.feature_branch is not None and self.feature_branch != ""

    def get_display_title(self) -> str:
        """Get formatted title for display with GitHub indicator.

        Returns:
            Title with [GitHub #XXX] prefix if from GitHub
        """
        if self.github_number:
            return f"[GitHub #{self.github_number}] {self.title}"
        return self.title

    @classmethod
    def from_github_epic(cls, epic: "GitHubEpic", priority: str) -> "RoadmapItem":  # type: ignore
        """Create RoadmapItem from GitHub epic.

        Args:
            epic: GitHubEpic instance
            priority: Mapped priority (P1-P4)

        Returns:
            RoadmapItem instance with source='github'

        Examples:
            >>> from doit_cli.models.github_epic import GitHubEpic
            >>> epic = GitHubEpic(
            ...     number=577,
            ...     title="[Epic]: Test",
            ...     state="open",
            ...     labels=["epic"],
            ...     body="Description",
            ...     url="https://github.com/owner/repo/issues/577"
            ... )
            >>> item = RoadmapItem.from_github_epic(epic, "P2")
            >>> item.source
            'github'
        """
        # Extract feature branch reference from title if present
        feature_branch = None
        if "[" in epic.title and "]" in epic.title:
            # Try to extract [###-feature-name] pattern
            start = epic.title.find("[")
            end = epic.title.find("]", start)
            if end > start:
                potential_branch = epic.title[start : end + 1]
                if "-" in potential_branch:
                    feature_branch = potential_branch

        return cls(
            title=epic.title,
            priority=priority,
            description=epic.body,
            rationale=f"Synced from GitHub epic #{epic.number}",
            feature_branch=feature_branch,
            status="in-progress" if epic.is_open else "completed",
            source="github",
            github_number=epic.number,
            github_url=epic.url,
            features=epic.features if hasattr(epic, 'features') else [],
        )

    def to_dict(self) -> dict:
        """Convert roadmap item to dictionary for serialization.

        Returns:
            Dictionary representation of the roadmap item
        """
        return {
            "title": self.title,
            "priority": self.priority,
            "description": self.description,
            "rationale": self.rationale,
            "feature_branch": self.feature_branch,
            "status": self.status,
            "source": self.source,
            "github_number": self.github_number,
            "github_url": self.github_url,
        }


# Import at end to avoid circular dependency
from .github_epic import GitHubEpic  # noqa: E402
