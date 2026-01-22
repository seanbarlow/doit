"""Unit tests for roadmap merge service.

Tests the RoadmapMergeService class that merges local roadmap items with GitHub epics,
testing merge logic with matched items, GitHub-only items, local-only items, and conflicts.
"""

import pytest

from doit_cli.models.github_epic import GitHubEpic
from doit_cli.models.roadmap import RoadmapItem
from doit_cli.services.roadmap_merge_service import RoadmapMergeService


@pytest.fixture
def merge_service():
    """Create a RoadmapMergeService instance for testing."""
    return RoadmapMergeService()


@pytest.fixture
def local_item_with_branch():
    """Create a local roadmap item with feature branch."""
    return RoadmapItem(
        title="Local Feature A",
        priority="P1",
        description="Local description for feature A",
        rationale="Local rationale",
        feature_branch="[039-feature-a]",
        status="in-progress",
        source="local",
    )


@pytest.fixture
def local_item_without_branch():
    """Create a local roadmap item without feature branch."""
    return RoadmapItem(
        title="Local Feature B",
        priority="P2",
        description="Local description for feature B",
        source="local",
    )


@pytest.fixture
def github_epic_matching():
    """Create a GitHub epic matching the branch."""
    return GitHubEpic(
        number=577,
        title="[Epic]: [039-feature-a] GitHub Feature A",
        state="open",
        labels=["epic", "priority:P2"],
        body="GitHub description",
        url="https://github.com/owner/repo/issues/577",
    )


@pytest.fixture
def github_epic_unmatched():
    """Create an unmatched GitHub epic."""
    return GitHubEpic(
        number=578,
        title="[Epic]: Unmatched Feature",
        state="open",
        labels=["epic", "priority:P3"],
        body="Unmatched epic",
        url="https://github.com/owner/repo/issues/578",
    )


class TestMergeRoadmapItems:
    """Tests for merge_roadmap_items method."""

    def test_merge_with_empty_lists(self, merge_service):
        """Test merge with both lists empty."""
        result = merge_service.merge_roadmap_items([], [])
        assert len(result) == 0

    def test_merge_with_only_local_items(
        self, merge_service, local_item_with_branch, local_item_without_branch
    ):
        """Test merge with only local items, no GitHub epics."""
        local_items = [local_item_with_branch, local_item_without_branch]
        result = merge_service.merge_roadmap_items(local_items, [])

        assert len(result) == 2
        assert all(item.source == "local" for item in result)
        # Should be sorted by priority (P1, then P2)
        assert result[0].priority == "P1"
        assert result[1].priority == "P2"

    def test_merge_with_only_github_epics(
        self, merge_service, github_epic_matching, github_epic_unmatched
    ):
        """Test merge with only GitHub epics, no local items."""
        github_epics = [github_epic_matching, github_epic_unmatched]
        result = merge_service.merge_roadmap_items([], github_epics)

        assert len(result) == 2
        assert all(item.source == "github" for item in result)
        assert result[0].github_number == 577
        assert result[1].github_number == 578

    def test_merge_with_matched_items(
        self, merge_service, local_item_with_branch, github_epic_matching
    ):
        """Test merge when local item matches GitHub epic by feature branch."""
        result = merge_service.merge_roadmap_items(
            [local_item_with_branch], [github_epic_matching]
        )

        assert len(result) == 1
        merged_item = result[0]

        # Should preserve local data
        assert merged_item.title == "Local Feature A"
        assert merged_item.priority == "P1"
        assert merged_item.description == "Local description for feature A"
        assert merged_item.status == "in-progress"

        # Should add GitHub metadata
        assert merged_item.github_number == 577
        assert merged_item.github_url == "https://github.com/owner/repo/issues/577"

        # Should mark as merged
        assert merged_item.source == "merged"

    def test_merge_with_unmatched_items(
        self, merge_service, local_item_with_branch, github_epic_unmatched
    ):
        """Test merge when items don't match."""
        result = merge_service.merge_roadmap_items(
            [local_item_with_branch], [github_epic_unmatched]
        )

        assert len(result) == 2

        # Local item should remain unchanged
        local_result = next(item for item in result if item.title == "Local Feature A")
        assert local_result.source == "local"
        assert local_result.github_number is None

        # GitHub epic should be added as new
        github_result = next(item for item in result if "Unmatched" in item.title)
        assert github_result.source == "github"
        assert github_result.github_number == 578

    def test_merge_complex_scenario(
        self,
        merge_service,
        local_item_with_branch,
        local_item_without_branch,
        github_epic_matching,
        github_epic_unmatched,
    ):
        """Test complex merge with multiple matches and non-matches."""
        local_items = [local_item_with_branch, local_item_without_branch]
        github_epics = [github_epic_matching, github_epic_unmatched]

        result = merge_service.merge_roadmap_items(local_items, github_epics)

        assert len(result) == 3

        # Check we have one merged, one local, one github
        sources = [item.source for item in result]
        assert "merged" in sources
        assert "local" in sources
        assert "github" in sources

    def test_merge_sorts_by_priority(self, merge_service):
        """Test merge sorts results by priority."""
        local_p3 = RoadmapItem(
            title="P3 Item", priority="P3", description="Desc", source="local"
        )
        local_p1 = RoadmapItem(
            title="P1 Item", priority="P1", description="Desc", source="local"
        )
        local_p2 = RoadmapItem(
            title="P2 Item", priority="P2", description="Desc", source="local"
        )

        result = merge_service.merge_roadmap_items([local_p3, local_p1, local_p2], [])

        assert result[0].priority == "P1"
        assert result[1].priority == "P2"
        assert result[2].priority == "P3"

    def test_merge_sorts_by_title_within_priority(self, merge_service):
        """Test merge sorts by title within same priority."""
        item_c = RoadmapItem(
            title="C Item", priority="P1", description="Desc", source="local"
        )
        item_a = RoadmapItem(
            title="A Item", priority="P1", description="Desc", source="local"
        )
        item_b = RoadmapItem(
            title="B Item", priority="P1", description="Desc", source="local"
        )

        result = merge_service.merge_roadmap_items([item_c, item_a, item_b], [])

        assert result[0].title == "A Item"
        assert result[1].title == "B Item"
        assert result[2].title == "C Item"

    def test_merge_does_not_duplicate_github_sourced_items(self, merge_service):
        """Test that items with source='github' are not duplicated."""
        # Local item that came from GitHub previously
        github_sourced = RoadmapItem(
            title="Previously synced",
            priority="P1",
            description="Desc",
            source="github",
            github_number=577,
            github_url="https://github.com/owner/repo/issues/577",
        )

        # New GitHub epic with same number
        epic = GitHubEpic(
            number=577,
            title="[Epic]: Previously synced",
            state="open",
            labels=["epic"],
            body="Desc",
            url="https://github.com/owner/repo/issues/577",
        )

        result = merge_service.merge_roadmap_items([github_sourced], [epic])

        # Should only have one item (the new GitHub epic)
        assert len(result) == 1
        assert result[0].github_number == 577

    def test_merge_preserves_local_status_in_matched_items(
        self, merge_service, github_epic_matching
    ):
        """Test that local status is preserved when merging."""
        local_completed = RoadmapItem(
            title="Completed Feature",
            priority="P1",
            description="Done",
            feature_branch="[039-feature-a]",
            status="completed",
            source="local",
        )

        result = merge_service.merge_roadmap_items([local_completed], [github_epic_matching])

        assert len(result) == 1
        assert result[0].status == "completed"
        assert result[0].source == "merged"


class TestFindEpicByBranch:
    """Tests for _find_epic_by_branch method."""

    def test_find_epic_exact_match_in_title(self, merge_service):
        """Test finding epic with exact branch match in title."""
        epic = GitHubEpic(
            number=577,
            title="[Epic]: [039-test] Feature",
            state="open",
            labels=["epic"],
            body="Description",
            url="https://github.com/owner/repo/issues/577",
        )

        result = merge_service._find_epic_by_branch([epic], "[039-test]")

        assert result is not None
        assert result.number == 577

    def test_find_epic_normalized_match_in_title(self, merge_service):
        """Test finding epic with normalized branch reference."""
        epic = GitHubEpic(
            number=577,
            title="[Epic]: 039-test Feature",
            state="open",
            labels=["epic"],
            body="Description",
            url="https://github.com/owner/repo/issues/577",
        )

        result = merge_service._find_epic_by_branch([epic], "[039-test]")

        assert result is not None
        assert result.number == 577

    def test_find_epic_match_in_body(self, merge_service):
        """Test finding epic with branch reference in body."""
        epic = GitHubEpic(
            number=577,
            title="[Epic]: Feature",
            state="open",
            labels=["epic"],
            body="This implements [039-test] feature",
            url="https://github.com/owner/repo/issues/577",
        )

        result = merge_service._find_epic_by_branch([epic], "[039-test]")

        assert result is not None
        assert result.number == 577

    def test_find_epic_case_insensitive(self, merge_service):
        """Test finding epic is case-insensitive."""
        epic = GitHubEpic(
            number=577,
            title="[Epic]: [039-TEST] Feature",
            state="open",
            labels=["epic"],
            body="Description",
            url="https://github.com/owner/repo/issues/577",
        )

        result = merge_service._find_epic_by_branch([epic], "[039-test]")

        assert result is not None
        assert result.number == 577

    def test_find_epic_no_match(self, merge_service):
        """Test finding epic returns None when no match."""
        epic = GitHubEpic(
            number=577,
            title="[Epic]: Different Feature",
            state="open",
            labels=["epic"],
            body="No reference here",
            url="https://github.com/owner/repo/issues/577",
        )

        result = merge_service._find_epic_by_branch([epic], "[039-test]")

        assert result is None

    def test_find_epic_with_none_branch(self, merge_service):
        """Test finding epic with None branch returns None."""
        epic = GitHubEpic(
            number=577,
            title="[Epic]: Feature",
            state="open",
            labels=["epic"],
            body="Description",
            url="https://github.com/owner/repo/issues/577",
        )

        result = merge_service._find_epic_by_branch([epic], None)

        assert result is None

    def test_find_epic_in_multiple_epics(self, merge_service):
        """Test finding epic in list with multiple epics."""
        epic1 = GitHubEpic(
            number=100,
            title="[Epic]: Other Feature",
            state="open",
            labels=["epic"],
            body="No match",
            url="https://github.com/owner/repo/issues/100",
        )
        epic2 = GitHubEpic(
            number=200,
            title="[Epic]: [039-test] Target Feature",
            state="open",
            labels=["epic"],
            body="Description",
            url="https://github.com/owner/repo/issues/200",
        )
        epic3 = GitHubEpic(
            number=300,
            title="[Epic]: Another Feature",
            state="open",
            labels=["epic"],
            body="No match",
            url="https://github.com/owner/repo/issues/300",
        )

        result = merge_service._find_epic_by_branch([epic1, epic2, epic3], "[039-test]")

        assert result is not None
        assert result.number == 200


class TestCreateMergedItem:
    """Tests for _create_merged_item method."""

    def test_create_merged_item_preserves_local_data(self, merge_service):
        """Test that merged item preserves all local data."""
        local = RoadmapItem(
            title="Local Title",
            priority="P1",
            description="Local description",
            rationale="Local rationale",
            feature_branch="[039-test]",
            status="in-progress",
            source="local",
        )

        epic = GitHubEpic(
            number=577,
            title="[Epic]: GitHub Title",
            state="open",
            labels=["epic", "priority:P2"],
            body="GitHub description",
            url="https://github.com/owner/repo/issues/577",
        )

        result = merge_service._create_merged_item(local, epic)

        # Preserve local data
        assert result.title == "Local Title"
        assert result.priority == "P1"
        assert result.description == "Local description"
        assert result.rationale == "Local rationale"
        assert result.feature_branch == "[039-test]"
        assert result.status == "in-progress"

    def test_create_merged_item_adds_github_metadata(self, merge_service):
        """Test that merged item includes GitHub metadata."""
        local = RoadmapItem(
            title="Title",
            priority="P1",
            description="Desc",
            feature_branch="[039-test]",
            source="local",
        )

        epic = GitHubEpic(
            number=577,
            title="[Epic]: Test",
            state="open",
            labels=["epic"],
            body="Test",
            url="https://github.com/owner/repo/issues/577",
        )

        result = merge_service._create_merged_item(local, epic)

        # Add GitHub metadata
        assert result.github_number == 577
        assert result.github_url == "https://github.com/owner/repo/issues/577"

    def test_create_merged_item_sets_source_to_merged(self, merge_service):
        """Test that merged item has source='merged'."""
        local = RoadmapItem(
            title="Title",
            priority="P1",
            description="Desc",
            source="local",
        )

        epic = GitHubEpic(
            number=577,
            title="[Epic]: Test",
            state="open",
            labels=["epic"],
            body="Test",
            url="https://github.com/owner/repo/issues/577",
        )

        result = merge_service._create_merged_item(local, epic)

        assert result.source == "merged"


class TestPrioritySortKey:
    """Tests for _priority_sort_key method."""

    def test_priority_sort_key_p1(self, merge_service):
        """Test sort key for P1."""
        assert merge_service._priority_sort_key("P1") == 1

    def test_priority_sort_key_p2(self, merge_service):
        """Test sort key for P2."""
        assert merge_service._priority_sort_key("P2") == 2

    def test_priority_sort_key_p3(self, merge_service):
        """Test sort key for P3."""
        assert merge_service._priority_sort_key("P3") == 3

    def test_priority_sort_key_p4(self, merge_service):
        """Test sort key for P4."""
        assert merge_service._priority_sort_key("P4") == 4

    def test_priority_sort_key_unknown(self, merge_service):
        """Test sort key for unknown priority."""
        assert merge_service._priority_sort_key("P5") == 5
        assert merge_service._priority_sort_key("invalid") == 5

    def test_priority_ordering(self, merge_service):
        """Test that priorities are ordered correctly."""
        priorities = ["P4", "P1", "P3", "P2", "unknown"]
        sorted_priorities = sorted(
            priorities, key=lambda p: merge_service._priority_sort_key(p)
        )

        assert sorted_priorities == ["P1", "P2", "P3", "P4", "unknown"]
