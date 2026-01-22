"""Roadmap merge service for combining local and GitHub roadmap items.

This service implements smart merging logic to combine local roadmap items
with GitHub epics, matching by feature branch reference and preserving local data.
"""

from typing import List, Optional

from ..models.github_epic import GitHubEpic
from ..models.roadmap import RoadmapItem
from ..utils.priority_mapper import map_labels_to_priority


class RoadmapMergeService:
    """Service for merging local roadmap items with GitHub epics.

    Implements the smart merge strategy:
    1. Match items by feature branch reference
    2. For matches: preserve local data, enrich with GitHub metadata
    3. For GitHub-only items: add as new with source=github
    4. For local-only items: preserve as-is with source=local
    5. Never delete local items
    """

    def merge_roadmap_items(
        self, local_items: List[RoadmapItem], github_epics: List[GitHubEpic]
    ) -> List[RoadmapItem]:
        """Merge local roadmap items with GitHub epics.

        Args:
            local_items: List of roadmap items from local roadmap file
            github_epics: List of epics fetched from GitHub

        Returns:
            Merged list of roadmap items sorted by priority

        Examples:
            >>> local = [RoadmapItem(
            ...     title="Feature A",
            ...     priority="P1",
            ...     description="Local item",
            ...     feature_branch="[039-feature-a]"
            ... )]
            >>> epics = []
            >>> service = RoadmapMergeService()
            >>> merged = service.merge_roadmap_items(local, epics)
            >>> len(merged)
            1
            >>> merged[0].source
            'local'
        """
        merged = []
        matched_github = set()

        # Pass 1: Match and merge by feature branch reference
        for local_item in local_items:
            if local_item.has_feature_branch:
                # Look for matching GitHub epic
                github_epic = self._find_epic_by_branch(github_epics, local_item.feature_branch)

                if github_epic:
                    # Merge: local data + GitHub metadata
                    merged_item = self._create_merged_item(local_item, github_epic)
                    merged.append(merged_item)
                    matched_github.add(github_epic.number)
                    continue

            # No match: preserve local item
            if local_item.source != "github":  # Don't duplicate GitHub-sourced items
                local_item.source = "local"
                merged.append(local_item)

        # Pass 2: Add unmatched GitHub epics
        for epic in github_epics:
            if epic.number not in matched_github:
                priority = map_labels_to_priority(epic.labels)
                github_item = RoadmapItem.from_github_epic(epic, priority)
                merged.append(github_item)

        # Sort by priority (P1 > P2 > P3 > P4) then by title
        return sorted(merged, key=lambda x: (self._priority_sort_key(x.priority), x.title))

    def _find_epic_by_branch(
        self, epics: List[GitHubEpic], feature_branch: Optional[str]
    ) -> Optional[GitHubEpic]:
        """Find GitHub epic matching the feature branch reference.

        Args:
            epics: List of GitHub epics to search
            feature_branch: Feature branch reference like [039-feature-name]

        Returns:
            Matching GitHubEpic or None if not found

        Examples:
            >>> epics = [GitHubEpic(
            ...     number=577,
            ...     title="[Epic]: [039-test] Feature",
            ...     state="open",
            ...     labels=["epic"],
            ...     body="Test",
            ...     url="https://github.com/owner/repo/issues/577"
            ... )]
            >>> service = RoadmapMergeService()
            >>> epic = service._find_epic_by_branch(epics, "[039-test]")
            >>> epic.number if epic else None
            577
        """
        if not feature_branch:
            return None

        # Normalize feature branch (remove brackets for comparison)
        normalized_branch = feature_branch.strip("[]").lower()

        for epic in epics:
            # Check if epic title or body contains the feature branch reference
            if feature_branch.lower() in epic.title.lower():
                return epic
            if normalized_branch in epic.title.lower().replace("[", "").replace("]", ""):
                return epic
            if feature_branch.lower() in epic.body.lower():
                return epic

        return None

    def _create_merged_item(
        self, local_item: RoadmapItem, github_epic: GitHubEpic
    ) -> RoadmapItem:
        """Create merged roadmap item from local and GitHub data.

        Prioritizes local data (user edits) while enriching with GitHub metadata.

        Args:
            local_item: Local roadmap item
            github_epic: Matching GitHub epic

        Returns:
            Merged RoadmapItem with source='merged'

        Examples:
            >>> local = RoadmapItem(
            ...     title="Feature A",
            ...     priority="P1",
            ...     description="Local desc",
            ...     feature_branch="[039-test]"
            ... )
            >>> epic = GitHubEpic(
            ...     number=577,
            ...     title="[Epic]: Test",
            ...     state="open",
            ...     labels=["epic"],
            ...     body="GitHub desc",
            ...     url="https://github.com/owner/repo/issues/577"
            ... )
            >>> service = RoadmapMergeService()
            >>> merged = service._create_merged_item(local, epic)
            >>> merged.source
            'merged'
        """
        # Create new item with local data preserved
        return RoadmapItem(
            title=local_item.title,  # Preserve local title
            priority=local_item.priority,  # Preserve local priority
            description=local_item.description,  # Preserve local description
            rationale=local_item.rationale,  # Preserve local rationale
            feature_branch=local_item.feature_branch,
            status=local_item.status,  # Preserve local status
            source="merged",  # Mark as merged
            github_number=github_epic.number,  # Add GitHub metadata
            github_url=github_epic.url,  # Add GitHub URL
            features=github_epic.features if hasattr(github_epic, 'features') else [],  # Add linked features
        )

    def _priority_sort_key(self, priority: str) -> int:
        """Convert priority string to sort key.

        Args:
            priority: Priority string (P1, P2, P3, or P4)

        Returns:
            Integer sort key (1-4)

        Examples:
            >>> service = RoadmapMergeService()
            >>> service._priority_sort_key("P1")
            1
            >>> service._priority_sort_key("P4")
            4
        """
        priority_order = {"P1": 1, "P2": 2, "P3": 3, "P4": 4}
        return priority_order.get(priority, 5)  # Unknown priorities go last
