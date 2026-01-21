"""
Service Contract: Roadmap Matcher

Purpose: Match user-provided feature names to roadmap items using fuzzy matching.
"""

from typing import Protocol, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class RoadmapItem:
    """Represents a single item in the roadmap."""

    title: str
    priority: str  # P1, P2, P3, P4
    feature_branch: str  # [###-feature-name]
    github_number: Optional[int]
    github_url: Optional[str]
    status: str  # Planned, In Progress, Complete, Deferred
    category: Optional[str]

    def __post_init__(self):
        """Validate roadmap item fields."""
        if not self.title:
            raise ValueError("Title cannot be empty")
        if self.priority not in ["P1", "P2", "P3", "P4"]:
            raise ValueError(f"Invalid priority: {self.priority}")
        if self.github_number is not None and self.github_number <= 0:
            raise ValueError(f"Invalid GitHub number: {self.github_number}")


@dataclass
class MatchResult:
    """Result of a roadmap item match operation."""

    item: RoadmapItem
    similarity_score: float  # 0.0 to 1.0
    is_exact_match: bool


class RoadmapMatcherService(Protocol):
    """
    Service for matching feature names to roadmap items.

    This service provides fuzzy matching capabilities to find roadmap items
    that correspond to user-provided feature names.
    """

    def find_best_match(
        self, feature_name: str, roadmap_path: Path
    ) -> Optional[MatchResult]:
        """
        Find the best matching roadmap item for a feature name.

        Args:
            feature_name: User-provided feature name
            roadmap_path: Path to roadmap.md file

        Returns:
            MatchResult if a match is found with >80% similarity, None otherwise

        Raises:
            FileNotFoundError: If roadmap file doesn't exist
            ValueError: If roadmap file is malformed
        """
        ...

    def find_all_matches(
        self, feature_name: str, roadmap_path: Path, threshold: float = 0.8
    ) -> list[MatchResult]:
        """
        Find all roadmap items matching a feature name above the threshold.

        Args:
            feature_name: User-provided feature name
            roadmap_path: Path to roadmap.md file
            threshold: Minimum similarity score (0.0 to 1.0), default 0.8

        Returns:
            List of MatchResult sorted by similarity score (descending)

        Raises:
            FileNotFoundError: If roadmap file doesn't exist
            ValueError: If roadmap file is malformed or threshold invalid
        """
        ...

    def parse_roadmap(self, roadmap_path: Path) -> list[RoadmapItem]:
        """
        Parse roadmap.md file into structured roadmap items.

        Args:
            roadmap_path: Path to roadmap.md file

        Returns:
            List of RoadmapItem objects

        Raises:
            FileNotFoundError: If roadmap file doesn't exist
            ValueError: If roadmap file is malformed
        """
        ...


# Example Usage

"""
# Initialize service
matcher = RoadmapMatcherServiceImpl()

# Find best match
result = matcher.find_best_match(
    feature_name="GitHub Issue Linking",
    roadmap_path=Path(".doit/memory/roadmap.md")
)

if result:
    print(f"Matched: {result.item.title} (score: {result.similarity_score:.2f})")
    if result.item.github_number:
        print(f"GitHub Epic: #{result.item.github_number}")
else:
    print("No matching roadmap item found")

# Find all matches above threshold
matches = matcher.find_all_matches(
    feature_name="GitHub Issue Linking",
    roadmap_path=Path(".doit/memory/roadmap.md"),
    threshold=0.8
)

if len(matches) > 1:
    print("Multiple matches found:")
    for match in matches:
        print(f"  - {match.item.title} ({match.similarity_score:.0%})")
"""
