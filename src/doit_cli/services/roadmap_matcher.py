"""Roadmap matching service for finding roadmap items by feature name.

This service parses the roadmap markdown file and uses fuzzy matching to find
roadmap items that correspond to user-provided feature names.
"""

import re
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass
from functools import lru_cache

from ..utils.fuzzy_match import (
    find_best_match,
    find_all_matches,
    is_exact_match
)


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


class RoadmapMatcherService:
    """Service for matching feature names to roadmap items."""

    def __init__(self, roadmap_path: Path):
        """Initialize the matcher with roadmap file path.

        Args:
            roadmap_path: Path to roadmap.md file
        """
        self.roadmap_path = roadmap_path

    @lru_cache(maxsize=1)
    def parse_roadmap(self) -> List[RoadmapItem]:
        """Parse roadmap.md file into structured roadmap items.

        This method is cached to avoid repeated file reads.

        Returns:
            List of RoadmapItem objects

        Raises:
            FileNotFoundError: If roadmap file doesn't exist
            ValueError: If roadmap file is malformed
        """
        if not self.roadmap_path.exists():
            raise FileNotFoundError(f"Roadmap file not found: {self.roadmap_path}")

        with open(self.roadmap_path, "r", encoding="utf-8") as f:
            content = f.read()

        items = []

        # Find all markdown tables in the roadmap
        # Table format: | Title | Priority | Branch | GitHub | Status | Category |
        table_pattern = r'\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|'

        for line in content.splitlines():
            # Skip header rows and separator rows
            if line.strip().startswith("|") and "---" not in line and "Title" not in line:
                match = re.match(table_pattern, line)
                if match:
                    title = match.group(1).strip()
                    priority = match.group(2).strip()
                    branch = match.group(3).strip()
                    github = match.group(4).strip()
                    status = match.group(5).strip()
                    category = match.group(6).strip()

                    # Skip if title is empty (malformed row)
                    if not title:
                        continue

                    # Extract GitHub number and URL
                    github_number = None
                    github_url = None
                    if github and github != "":
                        # Format: [#123](url)
                        github_match = re.search(r'\[#(\d+)\]\(([^)]+)\)', github)
                        if github_match:
                            github_number = int(github_match.group(1))
                            github_url = github_match.group(2)

                    try:
                        item = RoadmapItem(
                            title=title,
                            priority=priority,
                            feature_branch=branch,
                            github_number=github_number,
                            github_url=github_url,
                            status=status,
                            category=category if category else None
                        )
                        items.append(item)
                    except ValueError as e:
                        # Skip malformed items but log warning
                        print(f"Warning: Skipping malformed roadmap item: {e}")
                        continue

        if not items:
            raise ValueError(f"No valid roadmap items found in {self.roadmap_path}")

        return items

    def find_best_match(
        self,
        feature_name: str,
        threshold: float = 0.8
    ) -> Optional[MatchResult]:
        """Find the best matching roadmap item for a feature name.

        Args:
            feature_name: User-provided feature name
            threshold: Minimum similarity ratio (0.0 to 1.0), default 0.8

        Returns:
            MatchResult if a match is found with >threshold similarity, None otherwise

        Raises:
            FileNotFoundError: If roadmap file doesn't exist
            ValueError: If roadmap file is malformed
        """
        if not feature_name:
            return None

        # Parse roadmap
        items = self.parse_roadmap()

        # Extract titles for matching
        titles = [item.title for item in items]

        # Check for exact match first
        for item in items:
            if is_exact_match(feature_name, item.title):
                return MatchResult(
                    item=item,
                    similarity_score=1.0,
                    is_exact_match=True
                )

        # Try fuzzy matching
        match = find_best_match(feature_name, titles, threshold=threshold)
        if match:
            matched_title, score = match
            # Find the corresponding item
            for item in items:
                if item.title == matched_title:
                    return MatchResult(
                        item=item,
                        similarity_score=score,
                        is_exact_match=False
                    )

        return None

    def find_all_matches(
        self,
        feature_name: str,
        threshold: float = 0.8
    ) -> List[MatchResult]:
        """Find all roadmap items matching a feature name above the threshold.

        Args:
            feature_name: User-provided feature name
            threshold: Minimum similarity ratio (0.0 to 1.0), default 0.8

        Returns:
            List of MatchResult sorted by similarity score (descending)

        Raises:
            FileNotFoundError: If roadmap file doesn't exist
            ValueError: If roadmap file is malformed or threshold invalid
        """
        if not feature_name:
            return []

        if not 0.0 <= threshold <= 1.0:
            raise ValueError(f"Threshold must be between 0.0 and 1.0, got {threshold}")

        # Parse roadmap
        items = self.parse_roadmap()

        # Extract titles for matching
        titles = [item.title for item in items]

        # Find all fuzzy matches
        matches = find_all_matches(feature_name, titles, threshold=threshold)

        # Convert to MatchResult objects
        results = []
        for matched_title, score in matches:
            for item in items:
                if item.title == matched_title:
                    results.append(MatchResult(
                        item=item,
                        similarity_score=score,
                        is_exact_match=is_exact_match(feature_name, matched_title)
                    ))
                    break

        return results
