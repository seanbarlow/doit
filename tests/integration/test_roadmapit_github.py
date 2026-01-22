"""Integration tests for roadmapit command with GitHub integration.

Tests the end-to-end workflow of roadmapit command with GitHub epic synchronization,
including cache population, offline mode, and merge logic.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from doit_cli.models.github_epic import GitHubEpic
from doit_cli.models.roadmap import RoadmapItem
from doit_cli.models.sync_metadata import SyncMetadata
from doit_cli.services.github_cache_service import GitHubCacheService
from doit_cli.services.github_service import (
    GitHubService,
    GitHubAuthError,
    GitHubAPIError,
)
from doit_cli.services.roadmap_merge_service import RoadmapMergeService


@pytest.fixture
def temp_project_dir(tmp_path):
    """Create a temporary project directory structure."""
    # Create directory structure
    doit_dir = tmp_path / ".doit"
    memory_dir = doit_dir / "memory"
    cache_dir = doit_dir / "cache"

    memory_dir.mkdir(parents=True)
    cache_dir.mkdir(parents=True)

    return tmp_path


@pytest.fixture
def roadmap_file(temp_project_dir):
    """Create a roadmap file with sample data."""
    roadmap_path = temp_project_dir / ".doit" / "memory" / "roadmap.md"

    roadmap_content = """# Project Roadmap

## P1: Critical Priority

### [039-local-feature] Local Feature A
**Status**: in-progress
**Description**: This is a local feature with a branch reference
**Rationale**: Important for MVP

## P2: High Priority

### Local Feature B
**Status**: pending
**Description**: Local feature without branch
**Rationale**: Needed for completeness
"""

    roadmap_path.write_text(roadmap_content)
    return roadmap_path


@pytest.fixture
def cache_service(temp_project_dir):
    """Create a cache service with temp directory."""
    cache_path = temp_project_dir / ".doit" / "cache" / "github_epics.json"
    return GitHubCacheService(cache_path=cache_path)


@pytest.fixture
def mock_github_epics():
    """Create mock GitHub epics."""
    return [
        GitHubEpic(
            number=577,
            title="[Epic]: [039-local-feature] GitHub Feature A",
            state="open",
            labels=["epic", "priority:P1"],
            body="GitHub description for feature A",
            url="https://github.com/owner/repo/issues/577",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        ),
        GitHubEpic(
            number=578,
            title="[Epic]: GitHub Only Feature",
            state="open",
            labels=["epic", "priority:P3"],
            body="Feature only in GitHub",
            url="https://github.com/owner/repo/issues/578",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        ),
    ]


class TestRoadmapitGitHubIntegration:
    """Integration tests for roadmapit command with GitHub."""

    @patch("doit_cli.services.github_service.is_gh_authenticated")
    @patch("doit_cli.services.github_service.has_gh_cli")
    @patch("subprocess.run")
    def test_full_cycle_with_github_sync(
        self,
        mock_run,
        mock_has_cli,
        mock_is_auth,
        cache_service,
        mock_github_epics,
        temp_project_dir,
    ):
        """Test full cycle: fetch from GitHub, cache, merge with local items."""
        # Setup mocks
        mock_has_cli.return_value = True
        mock_is_auth.return_value = True

        # Mock GitHub API response
        github_response = [
            {
                "number": 577,
                "title": "[Epic]: [039-local-feature] GitHub Feature A",
                "state": "open",
                "labels": [{"name": "epic"}, {"name": "priority:P1"}],
                "body": "GitHub description for feature A",
                "url": "https://github.com/owner/repo/issues/577",
                "createdAt": "2026-01-21T10:00:00Z",
                "updatedAt": "2026-01-21T15:30:00Z",
            },
            {
                "number": 578,
                "title": "[Epic]: GitHub Only Feature",
                "state": "open",
                "labels": [{"name": "epic"}, {"name": "priority:P3"}],
                "body": "Feature only in GitHub",
                "url": "https://github.com/owner/repo/issues/578",
                "createdAt": "2026-01-21T09:00:00Z",
                "updatedAt": "2026-01-21T14:00:00Z",
            },
        ]

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps(github_response),
            stderr="",
        )

        # Step 1: Fetch epics from GitHub
        github_service = GitHubService()
        epics = github_service.fetch_epics()

        assert len(epics) == 2
        assert epics[0].number == 577
        assert epics[1].number == 578

        # Step 2: Save to cache
        metadata = SyncMetadata.create_new(
            "https://github.com/owner/repo",
            ttl_minutes=30
        )
        cache_service.save_cache(epics, metadata)

        # Verify cache was created
        assert cache_service.cache_path.exists()
        assert cache_service.is_valid()

        # Step 3: Load from cache
        cached_epics = cache_service.get_epics()
        assert cached_epics is not None
        assert len(cached_epics) == 2

        # Step 4: Create local roadmap items
        local_items = [
            RoadmapItem(
                title="Local Feature A",
                priority="P1",
                description="This is a local feature with a branch reference",
                rationale="Important for MVP",
                feature_branch="[039-local-feature]",
                status="in-progress",
                source="local",
            ),
            RoadmapItem(
                title="Local Feature B",
                priority="P2",
                description="Local feature without branch",
                rationale="Needed for completeness",
                status="pending",
                source="local",
            ),
        ]

        # Step 5: Merge local items with GitHub epics
        merge_service = RoadmapMergeService()
        merged_items = merge_service.merge_roadmap_items(local_items, cached_epics)

        # Verify merge results
        assert len(merged_items) == 3  # 1 merged + 1 local-only + 1 github-only

        # Find merged item (matched by branch)
        merged_item = next(
            item for item in merged_items
            if item.source == "merged" and "[039-local-feature]" in (item.feature_branch or "")
        )
        assert merged_item.title == "Local Feature A"  # Preserves local title
        assert merged_item.github_number == 577  # Has GitHub metadata
        assert merged_item.status == "in-progress"  # Preserves local status

        # Find local-only item
        local_only = next(item for item in merged_items if item.title == "Local Feature B")
        assert local_only.source == "local"
        assert local_only.github_number is None

        # Find GitHub-only item
        github_only = next(item for item in merged_items if "GitHub Only" in item.title)
        assert github_only.source == "github"
        assert github_only.github_number == 578

    def test_offline_mode_with_valid_cache(
        self, cache_service, mock_github_epics
    ):
        """Test offline mode uses valid cache when GitHub is unavailable."""
        # Setup: Create valid cache
        metadata = SyncMetadata.create_new(
            "https://github.com/owner/repo",
            ttl_minutes=30
        )
        cache_service.save_cache(mock_github_epics, metadata)

        # Verify cache is valid
        assert cache_service.is_valid()

        # Simulate offline mode: GitHub service not available
        # In real usage, this would be caught by try/except and fall back to cache
        cached_epics = cache_service.get_epics()

        assert cached_epics is not None
        assert len(cached_epics) == 2
        assert cached_epics[0].number == 577
        assert cached_epics[1].number == 578

        # Verify cache metadata
        cached_metadata = cache_service.get_metadata()
        assert cached_metadata is not None
        assert cached_metadata.repo_url == "https://github.com/owner/repo"
        assert cached_metadata.is_valid

    def test_offline_mode_with_expired_cache(
        self, cache_service, mock_github_epics
    ):
        """Test offline mode with expired cache returns None."""
        # Create expired cache (60 minutes old, TTL is 30)
        old_time = datetime.now() - timedelta(minutes=60)
        expired_metadata = SyncMetadata(
            repo_url="https://github.com/owner/repo",
            last_sync=old_time,
            ttl_minutes=30,
        )
        cache_service.save_cache(mock_github_epics, expired_metadata)

        # Verify cache is expired
        assert not cache_service.is_valid()

        # Try to get epics from expired cache
        cached_epics = cache_service.get_epics()

        # Should return None because cache is expired
        assert cached_epics is None

    def test_cache_refresh_with_flag(
        self, cache_service, mock_github_epics
    ):
        """Test --refresh flag invalidates cache and forces fresh fetch."""
        # Create valid cache
        metadata = SyncMetadata.create_new(
            "https://github.com/owner/repo",
            ttl_minutes=30
        )
        cache_service.save_cache(mock_github_epics, metadata)

        # Verify cache exists and is valid
        assert cache_service.cache_path.exists()
        assert cache_service.is_valid()

        # Simulate --refresh flag: invalidate cache
        cache_service.invalidate()

        # Verify cache was deleted
        assert not cache_service.cache_path.exists()
        assert not cache_service.is_valid()

        # After invalidation, would fetch fresh from GitHub
        # (tested separately in GitHub service tests)

    @patch("doit_cli.services.github_service.is_gh_authenticated")
    @patch("doit_cli.services.github_service.has_gh_cli")
    @patch("subprocess.run")
    def test_github_rate_limit_fallback_to_cache(
        self,
        mock_run,
        mock_has_cli,
        mock_is_auth,
        cache_service,
        mock_github_epics,
    ):
        """Test fallback to cache when GitHub rate limit is hit."""
        mock_has_cli.return_value = True
        mock_is_auth.return_value = True

        # Setup: Create valid cache
        metadata = SyncMetadata.create_new(
            "https://github.com/owner/repo",
            ttl_minutes=30
        )
        cache_service.save_cache(mock_github_epics, metadata)

        # Simulate rate limit error from GitHub
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="API rate limit exceeded",
        )

        # Try to fetch from GitHub (will fail with rate limit)
        github_service = GitHubService()
        try:
            github_service.fetch_epics()
            assert False, "Should have raised GitHubAPIError"
        except Exception as e:
            assert "rate limit" in str(e).lower()

        # Fallback to cache
        cached_epics = cache_service.get_epics()

        assert cached_epics is not None
        assert len(cached_epics) == 2

    def test_merge_preserves_local_priorities(
        self, mock_github_epics
    ):
        """Test that merge preserves local priority over GitHub priority."""
        # Local item with P1 priority
        local_items = [
            RoadmapItem(
                title="Feature",
                priority="P1",
                description="Local description",
                feature_branch="[039-local-feature]",
                source="local",
            ),
        ]

        # GitHub epic with same branch but P3 priority
        github_epics = [
            GitHubEpic(
                number=577,
                title="[Epic]: [039-local-feature] Feature",
                state="open",
                labels=["epic", "priority:P3"],
                body="GitHub description",
                url="https://github.com/owner/repo/issues/577",
            ),
        ]

        merge_service = RoadmapMergeService()
        merged = merge_service.merge_roadmap_items(local_items, github_epics)

        # Should preserve local P1 priority, not GitHub's P3
        assert len(merged) == 1
        assert merged[0].priority == "P1"
        assert merged[0].source == "merged"

    def test_merge_sorts_by_priority(self):
        """Test that merged results are sorted by priority."""
        local_items = [
            RoadmapItem(
                title="P3 Item",
                priority="P3",
                description="Desc",
                source="local",
            ),
            RoadmapItem(
                title="P1 Item",
                priority="P1",
                description="Desc",
                source="local",
            ),
        ]

        github_epics = [
            GitHubEpic(
                number=578,
                title="[Epic]: P2 Item",
                state="open",
                labels=["epic", "priority:P2"],
                body="Desc",
                url="https://github.com/owner/repo/issues/578",
            ),
        ]

        merge_service = RoadmapMergeService()
        merged = merge_service.merge_roadmap_items(local_items, github_epics)

        # Should be sorted P1, P2, P3
        assert merged[0].priority == "P1"
        assert merged[1].priority == "P2"
        assert merged[2].priority == "P3"

    def test_cache_age_tracking(self, cache_service, mock_github_epics):
        """Test that cache age is tracked correctly."""
        metadata = SyncMetadata.create_new(
            "https://github.com/owner/repo",
            ttl_minutes=30
        )
        cache_service.save_cache(mock_github_epics, metadata)

        # Get cache age
        age = cache_service.get_cache_age_minutes()

        assert age is not None
        assert age >= 0
        assert age < 1  # Should be very recent

    @patch("doit_cli.services.github_service.is_gh_authenticated")
    @patch("doit_cli.services.github_service.has_gh_cli")
    def test_skip_github_flag(self, mock_has_cli, mock_is_auth):
        """Test --skip-github flag bypasses GitHub API calls."""
        mock_has_cli.return_value = True
        mock_is_auth.return_value = True

        # When --skip-github is used, GitHub service should not be called
        # Instead, only local items should be used

        local_items = [
            RoadmapItem(
                title="Local Only",
                priority="P1",
                description="Local item",
                source="local",
            ),
        ]

        # Merge with empty GitHub list (simulating --skip-github)
        merge_service = RoadmapMergeService()
        merged = merge_service.merge_roadmap_items(local_items, [])

        assert len(merged) == 1
        assert merged[0].source == "local"

    def test_empty_roadmap_with_github_epics(self, mock_github_epics):
        """Test syncing GitHub epics when local roadmap is empty."""
        merge_service = RoadmapMergeService()
        merged = merge_service.merge_roadmap_items([], mock_github_epics)

        # All items should be from GitHub
        assert len(merged) == 2
        assert all(item.source == "github" for item in merged)
        assert merged[0].github_number in [577, 578]
        assert merged[1].github_number in [577, 578]

    def test_cache_corruption_handling(self, cache_service):
        """Test handling of corrupted cache file."""
        # Write corrupted JSON to cache
        cache_service.cache_path.write_text("corrupted json {")

        # Should return None for corrupted cache
        assert not cache_service.is_valid()
        assert cache_service.get_epics() is None
        assert cache_service.get_metadata() is None

    def test_multiple_sync_cycles(
        self, cache_service, mock_github_epics
    ):
        """Test multiple sync cycles maintain data consistency."""
        # First sync
        metadata1 = SyncMetadata.create_new(
            "https://github.com/owner/repo",
            ttl_minutes=30
        )
        cache_service.save_cache(mock_github_epics, metadata1)

        cached1 = cache_service.get_epics()
        assert len(cached1) == 2

        # Second sync with updated epic
        updated_epics = [
            GitHubEpic(
                number=577,
                title="[Epic]: [039-local-feature] Updated Feature A",
                state="open",
                labels=["epic", "priority:P1"],
                body="Updated description",
                url="https://github.com/owner/repo/issues/577",
            ),
            GitHubEpic(
                number=578,
                title="[Epic]: GitHub Only Feature",
                state="closed",  # Changed to closed
                labels=["epic", "priority:P3"],
                body="Feature only in GitHub",
                url="https://github.com/owner/repo/issues/578",
            ),
        ]

        metadata2 = SyncMetadata.create_new(
            "https://github.com/owner/repo",
            ttl_minutes=30
        )
        cache_service.save_cache(updated_epics, metadata2)

        cached2 = cache_service.get_epics()
        assert len(cached2) == 2
        assert cached2[0].title == "[Epic]: [039-local-feature] Updated Feature A"
        assert cached2[1].state == "closed"


class TestRoadmapitPerformance:
    """Performance tests for roadmapit GitHub integration."""

    @patch("doit_cli.services.github_service.is_gh_authenticated")
    @patch("doit_cli.services.github_service.has_gh_cli")
    @patch("subprocess.run")
    def test_sync_performance_with_50_epics(
        self,
        mock_run,
        mock_has_cli,
        mock_is_auth,
        cache_service,
    ):
        """Test sync performance with 50 epics (per spec requirement)."""
        import time

        mock_has_cli.return_value = True
        mock_is_auth.return_value = True

        # Create 50 mock epics
        epics_data = []
        for i in range(50):
            epics_data.append({
                "number": i + 1,
                "title": f"[Epic]: Feature {i + 1}",
                "state": "open",
                "labels": [{"name": "epic"}, {"name": "priority:P2"}],
                "body": f"Description {i + 1}",
                "url": f"https://github.com/owner/repo/issues/{i + 1}",
                "createdAt": "2026-01-21T10:00:00Z",
                "updatedAt": "2026-01-21T15:30:00Z",
            })

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps(epics_data),
            stderr="",
        )

        # Measure fetch time
        start_time = time.time()
        github_service = GitHubService()
        epics = github_service.fetch_epics()
        fetch_time = time.time() - start_time

        assert len(epics) == 50
        # Per spec: should complete in <5 seconds
        assert fetch_time < 5.0, f"Fetch took {fetch_time:.2f}s, should be <5s"

        # Measure cache save time
        start_time = time.time()
        metadata = SyncMetadata.create_new(
            "https://github.com/owner/repo",
            ttl_minutes=30
        )
        cache_service.save_cache(epics, metadata)
        save_time = time.time() - start_time

        # Cache save should be fast (<1 second)
        assert save_time < 1.0, f"Cache save took {save_time:.2f}s, should be <1s"

        # Measure cache load time
        start_time = time.time()
        cached_epics = cache_service.get_epics()
        load_time = time.time() - start_time

        assert len(cached_epics) == 50
        # Per spec: cached mode should be <2 seconds
        assert load_time < 2.0, f"Cache load took {load_time:.2f}s, should be <2s"

    @patch("doit_cli.services.github_service.is_gh_authenticated")
    @patch("doit_cli.services.github_service.has_gh_cli")
    @patch("subprocess.run")
    def test_epic_with_linked_features(
        self, mock_run, mock_has_cli, mock_is_auth, cache_service
    ):
        """Test that epic with linked features displays correctly (User Story 2)."""
        from doit_cli.models.github_feature import GitHubFeature

        mock_has_cli.return_value = True
        mock_is_auth.return_value = True

        # Prepare epic data (without features embedded yet)
        epic_data = {
            "number": 577,
            "title": "[Epic]: [039-test] Feature A",
            "state": "open",
            "labels": [{"name": "epic"}, {"name": "priority:P1"}],
            "body": "Epic description",
            "url": "https://github.com/owner/repo/issues/577",
            "createdAt": "2026-01-21T10:00:00Z",
            "updatedAt": "2026-01-21T15:30:00Z",
        }

        # Prepare features data
        feature_dicts = [
            {
                "number": 578,
                "title": "[Feature]: Sub-feature 1",
                "state": "open",
                "labels": [{"name": "feature"}],
                "url": "https://github.com/owner/repo/issues/578",
            },
            {
                "number": 579,
                "title": "[Feature]: Sub-feature 2",
                "state": "closed",
                "labels": [{"name": "feature"}],
                "url": "https://github.com/owner/repo/issues/579",
            },
        ]

        # Mock GitHub API responses
        def mock_run_side_effect(cmd, *args, **kwargs):
            # cmd is a list like ['gh', 'issue', 'list', ...]
            if isinstance(cmd, list):
                if "issue" in cmd and "list" in cmd and "--search" in cmd:
                    # Fetch features for epic (has --search flag)
                    return MagicMock(
                        returncode=0,
                        stdout=json.dumps(feature_dicts),
                        stderr="",
                    )
                elif "issue" in cmd and "list" in cmd:
                    # Fetch epics (no --search flag)
                    return MagicMock(
                        returncode=0,
                        stdout=json.dumps([epic_data]),
                        stderr="",
                    )
            return MagicMock(returncode=1, stdout="", stderr="Unknown command")

        mock_run.side_effect = mock_run_side_effect

        # Fetch and merge
        github_service = GitHubService()
        epics = github_service.fetch_epics()

        # Fetch features for each epic
        for e in epics:
            e.features = github_service.fetch_features_for_epic(e.number)

        # Create roadmap items
        merge_service = RoadmapMergeService()
        local_items = []
        merged = merge_service.merge_roadmap_items(local_items, epics)

        # Verify epic has features
        assert len(merged) == 1
        assert merged[0].github_number == 577
        assert len(merged[0].features) == 2

        # Verify features
        assert merged[0].features[0].number == 578
        assert merged[0].features[0].title == "[Feature]: Sub-feature 1"
        assert merged[0].features[0].is_open
        assert merged[0].features[1].number == 579
        assert merged[0].features[1].title == "[Feature]: Sub-feature 2"
        assert not merged[0].features[1].is_open

    def test_merge_performance_with_large_datasets(self):
        """Test merge performance with large number of items."""
        import time

        # Create 30 local items
        local_items = []
        for i in range(30):
            local_items.append(
                RoadmapItem(
                    title=f"Local Feature {i}",
                    priority="P2",
                    description=f"Description {i}",
                    source="local",
                )
            )

        # Create 50 GitHub epics
        github_epics = []
        for i in range(50):
            github_epics.append(
                GitHubEpic(
                    number=i + 1,
                    title=f"[Epic]: GitHub Feature {i}",
                    state="open",
                    labels=["epic", "priority:P3"],
                    body=f"Description {i}",
                    url=f"https://github.com/owner/repo/issues/{i + 1}",
                )
            )

        # Measure merge time
        start_time = time.time()
        merge_service = RoadmapMergeService()
        merged = merge_service.merge_roadmap_items(local_items, github_epics)
        merge_time = time.time() - start_time

        assert len(merged) == 80  # 30 local + 50 github
        # Merge should be very fast
        assert merge_time < 0.5, f"Merge took {merge_time:.2f}s, should be <0.5s"


class TestRoadmapitAddCommand:
    """Integration tests for roadmapit add command (User Story 3)."""

    @patch("doit_cli.services.github_service.is_gh_authenticated")
    @patch("doit_cli.services.github_service.has_gh_cli")
    @patch("subprocess.run")
    def test_add_creates_github_epic(
        self, mock_run, mock_has_cli, mock_is_auth
    ):
        """Test that roadmapit add creates a GitHub epic (User Story 3)."""
        mock_has_cli.return_value = True
        mock_is_auth.return_value = True

        # Mock successful epic creation
        epic_url = "https://github.com/owner/repo/issues/999"
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=epic_url,
            stderr="",
        )

        # Create epic via service (this is what the add command calls)
        github_service = GitHubService()
        epic = github_service.create_epic(
            title="[Epic]: New Feature X",
            body="Test feature",
            priority="P2"
        )

        # Verify epic was created correctly
        assert epic.number == 999
        assert epic.title == "[Epic]: New Feature X"
        assert epic.state == "open"
        assert epic.url == epic_url
        assert "epic" in epic.labels
        assert "priority:P2" in epic.labels

        # Verify gh CLI was called with correct arguments
        # Note: called twice - once for auth check in __init__, once for create_epic
        assert mock_run.call_count == 2
        # Get the create_epic call (second call)
        call_args = mock_run.call_args_list[1][0][0]
        assert call_args[0] == "gh"
        assert call_args[1] == "issue"
        assert call_args[2] == "create"
        assert "--title" in call_args
        assert "[Epic]: New Feature X" in call_args
        assert "--body" in call_args
        assert "Test feature" in call_args
        assert "--label" in call_args
        label_idx = call_args.index("--label") + 1
        labels = call_args[label_idx]
        assert "epic" in labels
        assert "priority:P2" in labels

    @patch("doit_cli.services.github_service.is_gh_authenticated")
    @patch("doit_cli.services.github_service.has_gh_cli")
    def test_add_handles_github_not_configured(
        self, mock_has_cli, mock_is_auth
    ):
        """Test that add command handles GitHub not configured gracefully."""
        mock_has_cli.return_value = False
        mock_is_auth.return_value = False

        github_service = GitHubService()

        # Should raise GitHubAuthError
        with pytest.raises(GitHubAuthError) as exc_info:
            github_service.create_epic(
                title="[Epic]: Test",
                body="Test",
                priority="P2"
            )

        assert "not installed" in str(exc_info.value).lower()

    @patch("doit_cli.services.github_service.is_gh_authenticated")
    @patch("doit_cli.services.github_service.has_gh_cli")
    @patch("subprocess.run")
    def test_add_handles_api_error(
        self, mock_run, mock_has_cli, mock_is_auth
    ):
        """Test that add command handles GitHub API errors gracefully."""
        mock_has_cli.return_value = True
        mock_is_auth.return_value = True

        # Mock API error
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="HTTP 500: Internal Server Error",
        )

        github_service = GitHubService()

        # Should raise GitHubAPIError
        with pytest.raises(GitHubAPIError) as exc_info:
            github_service.create_epic(
                title="[Epic]: Test",
                body="Test",
                priority="P2"
            )

        assert "Failed to create epic" in str(exc_info.value)

    @patch("doit_cli.services.github_service.is_gh_authenticated")
    @patch("doit_cli.services.github_service.has_gh_cli")
    @patch("subprocess.run")
    def test_add_with_custom_priority(
        self, mock_run, mock_has_cli, mock_is_auth
    ):
        """Test that add command respects custom priority levels."""
        mock_has_cli.return_value = True
        mock_is_auth.return_value = True

        epic_url = "https://github.com/owner/repo/issues/888"
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=epic_url,
            stderr="",
        )

        github_service = GitHubService()

        # Test each priority level
        for priority in ["P1", "P2", "P3", "P4"]:
            mock_run.reset_mock()

            epic = github_service.create_epic(
                title=f"[Epic]: {priority} Feature",
                body="Test",
                priority=priority
            )

            # Verify priority label was used
            call_args = mock_run.call_args[0][0]
            label_idx = call_args.index("--label") + 1
            labels = call_args[label_idx]
            assert f"priority:{priority}" in labels

    @patch("doit_cli.services.github_service.is_gh_authenticated")
    @patch("doit_cli.services.github_service.has_gh_cli")
    @patch("subprocess.run")
    def test_add_with_additional_labels(
        self, mock_run, mock_has_cli, mock_is_auth
    ):
        """Test that add command can include additional labels."""
        mock_has_cli.return_value = True
        mock_is_auth.return_value = True

        epic_url = "https://github.com/owner/repo/issues/777"
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=epic_url,
            stderr="",
        )

        github_service = GitHubService()
        epic = github_service.create_epic(
            title="[Epic]: Feature with Labels",
            body="Test",
            priority="P2",
            labels=["enhancement", "needs-review"]
        )

        # Verify all labels were included
        call_args = mock_run.call_args[0][0]
        label_idx = call_args.index("--label") + 1
        labels = call_args[label_idx]
        assert "epic" in labels
        assert "priority:P2" in labels
        assert "enhancement" in labels
        assert "needs-review" in labels
