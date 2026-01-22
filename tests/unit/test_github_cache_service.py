"""Unit tests for GitHub cache service.

Tests the GitHubCacheService class that manages cached epic data,
testing cache read/write, validation, TTL expiration, and corruption handling.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from doit_cli.models.github_epic import GitHubEpic
from doit_cli.models.sync_metadata import SyncMetadata
from doit_cli.services.github_cache_service import (
    CacheError,
    GitHubCacheService,
)


@pytest.fixture
def temp_cache_path(tmp_path):
    """Create a temporary cache path for testing."""
    return tmp_path / "test_cache" / "github_epics.json"


@pytest.fixture
def cache_service(temp_cache_path):
    """Create a cache service with temp path."""
    return GitHubCacheService(cache_path=temp_cache_path)


@pytest.fixture
def mock_metadata():
    """Create mock sync metadata."""
    return SyncMetadata.create_new("https://github.com/owner/repo", ttl_minutes=30)


@pytest.fixture
def mock_epic():
    """Create mock epic."""
    return GitHubEpic(
        number=577,
        title="[Epic]: Test Epic",
        state="open",
        labels=["epic", "priority:P2"],
        body="Test description",
        url="https://github.com/owner/repo/issues/577",
    )


@pytest.fixture
def valid_cache_data(mock_metadata, mock_epic):
    """Create valid cache data."""
    return {
        "version": "1.0.0",
        "metadata": mock_metadata.to_dict(),
        "epics": [mock_epic.to_dict()],
    }


class TestGitHubCacheServiceInit:
    """Tests for GitHubCacheService initialization."""

    def test_init_with_default_path(self):
        """Test initialization with default cache path."""
        service = GitHubCacheService()
        assert service.cache_path == Path(".doit/cache/github_epics.json")

    def test_init_with_custom_path(self, temp_cache_path):
        """Test initialization with custom cache path."""
        service = GitHubCacheService(cache_path=temp_cache_path)
        assert service.cache_path == temp_cache_path

    def test_init_creates_parent_directory(self, temp_cache_path):
        """Test initialization creates parent directory."""
        assert not temp_cache_path.parent.exists()
        service = GitHubCacheService(cache_path=temp_cache_path)
        assert temp_cache_path.parent.exists()


class TestLoadCache:
    """Tests for load_cache method."""

    def test_load_cache_returns_none_when_file_not_exists(self, cache_service):
        """Test load_cache returns None when cache file doesn't exist."""
        result = cache_service.load_cache()
        assert result is None

    def test_load_cache_success(self, cache_service, valid_cache_data):
        """Test load_cache successfully loads valid cache."""
        # Write cache file
        cache_service.cache_path.write_text(json.dumps(valid_cache_data))

        result = cache_service.load_cache()

        assert result is not None
        assert "metadata" in result
        assert "epics" in result
        assert len(result["epics"]) == 1

    def test_load_cache_raises_on_corrupted_json(self, cache_service):
        """Test load_cache raises CacheError on corrupted JSON."""
        # Write invalid JSON
        cache_service.cache_path.write_text("not valid json {")

        with pytest.raises(CacheError) as exc_info:
            cache_service.load_cache()

        assert "Corrupted cache file" in str(exc_info.value)

    def test_load_cache_raises_on_non_dict_data(self, cache_service):
        """Test load_cache raises CacheError when data is not a dict."""
        # Write list instead of dict
        cache_service.cache_path.write_text(json.dumps([1, 2, 3]))

        with pytest.raises(CacheError) as exc_info:
            cache_service.load_cache()

        assert "must be a dictionary" in str(exc_info.value)

    def test_load_cache_raises_on_missing_metadata_key(self, cache_service):
        """Test load_cache raises CacheError when metadata key is missing."""
        cache_data = {"epics": []}  # Missing metadata
        cache_service.cache_path.write_text(json.dumps(cache_data))

        with pytest.raises(CacheError) as exc_info:
            cache_service.load_cache()

        assert "missing required keys" in str(exc_info.value)

    def test_load_cache_raises_on_missing_epics_key(self, cache_service, mock_metadata):
        """Test load_cache raises CacheError when epics key is missing."""
        cache_data = {"metadata": mock_metadata.to_dict()}  # Missing epics
        cache_service.cache_path.write_text(json.dumps(cache_data))

        with pytest.raises(CacheError) as exc_info:
            cache_service.load_cache()

        assert "missing required keys" in str(exc_info.value)

    def test_load_cache_raises_on_io_error(self, cache_service):
        """Test load_cache raises CacheError on I/O error."""
        # Create file but make it unreadable
        cache_service.cache_path.write_text("{}")
        cache_service.cache_path.chmod(0o000)

        try:
            with pytest.raises(CacheError) as exc_info:
                cache_service.load_cache()

            assert "Failed to read cache file" in str(exc_info.value)
        finally:
            # Restore permissions for cleanup
            cache_service.cache_path.chmod(0o644)


class TestSaveCache:
    """Tests for save_cache method."""

    def test_save_cache_success(self, cache_service, mock_epic, mock_metadata):
        """Test save_cache successfully writes cache."""
        cache_service.save_cache([mock_epic], mock_metadata)

        assert cache_service.cache_path.exists()

        # Verify content
        with open(cache_service.cache_path) as f:
            cache_data = json.load(f)

        assert cache_data["version"] == "1.0.0"
        assert "metadata" in cache_data
        assert "epics" in cache_data
        assert len(cache_data["epics"]) == 1
        assert cache_data["epics"][0]["number"] == 577

    def test_save_cache_empty_epics_list(self, cache_service, mock_metadata):
        """Test save_cache with empty epics list."""
        cache_service.save_cache([], mock_metadata)

        with open(cache_service.cache_path) as f:
            cache_data = json.load(f)

        assert cache_data["epics"] == []

    def test_save_cache_multiple_epics(self, cache_service, mock_metadata):
        """Test save_cache with multiple epics."""
        epic1 = GitHubEpic(
            number=1, title="Epic 1", state="open", labels=["epic"],
            body="Desc 1", url="https://github.com/owner/repo/issues/1"
        )
        epic2 = GitHubEpic(
            number=2, title="Epic 2", state="open", labels=["epic"],
            body="Desc 2", url="https://github.com/owner/repo/issues/2"
        )

        cache_service.save_cache([epic1, epic2], mock_metadata)

        with open(cache_service.cache_path) as f:
            cache_data = json.load(f)

        assert len(cache_data["epics"]) == 2

    def test_save_cache_overwrites_existing(
        self, cache_service, mock_epic, mock_metadata
    ):
        """Test save_cache overwrites existing cache."""
        # Write initial cache
        cache_service.save_cache([mock_epic], mock_metadata)

        # Overwrite with empty list
        new_metadata = SyncMetadata.create_new("https://github.com/owner/repo")
        cache_service.save_cache([], new_metadata)

        with open(cache_service.cache_path) as f:
            cache_data = json.load(f)

        assert len(cache_data["epics"]) == 0

    def test_save_cache_atomic_write(self, cache_service, mock_epic, mock_metadata):
        """Test save_cache uses atomic write (temp file then rename)."""
        temp_path = cache_service.cache_path.with_suffix(".tmp")

        # Ensure temp file doesn't exist before
        assert not temp_path.exists()

        cache_service.save_cache([mock_epic], mock_metadata)

        # Temp file should be cleaned up after atomic rename
        assert not temp_path.exists()
        assert cache_service.cache_path.exists()

    def test_save_cache_raises_on_io_error(self, cache_service, mock_epic, mock_metadata):
        """Test save_cache raises CacheError on I/O error."""
        # Make parent directory read-only
        cache_service.cache_path.parent.chmod(0o444)

        try:
            with pytest.raises(CacheError) as exc_info:
                cache_service.save_cache([mock_epic], mock_metadata)

            assert "Failed to write cache file" in str(exc_info.value)
        finally:
            # Restore permissions
            cache_service.cache_path.parent.chmod(0o755)


class TestIsValid:
    """Tests for is_valid method."""

    def test_is_valid_returns_false_when_no_cache(self, cache_service):
        """Test is_valid returns False when cache doesn't exist."""
        assert cache_service.is_valid() is False

    def test_is_valid_returns_true_for_fresh_cache(
        self, cache_service, mock_epic, mock_metadata
    ):
        """Test is_valid returns True for fresh cache within TTL."""
        cache_service.save_cache([mock_epic], mock_metadata)
        assert cache_service.is_valid() is True

    def test_is_valid_returns_false_for_expired_cache(
        self, cache_service, mock_epic
    ):
        """Test is_valid returns False for expired cache."""
        # Create metadata with old timestamp
        old_time = datetime.now() - timedelta(minutes=60)
        expired_metadata = SyncMetadata(
            repo_url="https://github.com/owner/repo",
            last_sync=old_time,
            ttl_minutes=30,
        )

        cache_service.save_cache([mock_epic], expired_metadata)
        assert cache_service.is_valid() is False

    def test_is_valid_returns_false_on_corrupted_cache(self, cache_service):
        """Test is_valid returns False when cache is corrupted."""
        cache_service.cache_path.write_text("corrupted json")
        assert cache_service.is_valid() is False

    def test_is_valid_returns_false_on_missing_metadata(
        self, cache_service, mock_epic
    ):
        """Test is_valid returns False when metadata is missing."""
        cache_data = {"version": "1.0.0", "epics": [mock_epic.to_dict()]}
        cache_service.cache_path.write_text(json.dumps(cache_data))
        assert cache_service.is_valid() is False


class TestGetEpics:
    """Tests for get_epics method."""

    def test_get_epics_returns_none_when_no_cache(self, cache_service):
        """Test get_epics returns None when cache doesn't exist."""
        assert cache_service.get_epics() is None

    def test_get_epics_returns_epics_for_valid_cache(
        self, cache_service, mock_metadata
    ):
        """Test get_epics returns epics for valid cache."""
        # Create epic data in GitHub API format (with label objects)
        epic_data = {
            "number": 577,
            "title": "[Epic]: Test Epic",
            "state": "open",
            "labels": [{"name": "epic"}, {"name": "priority:P2"}],
            "body": "Test description",
            "url": "https://github.com/owner/repo/issues/577",
        }

        cache_data = {
            "version": "1.0.0",
            "metadata": mock_metadata.to_dict(),
            "epics": [epic_data],
        }

        cache_service.cache_path.write_text(json.dumps(cache_data))

        epics = cache_service.get_epics()

        assert epics is not None
        assert len(epics) == 1
        assert isinstance(epics[0], GitHubEpic)
        assert epics[0].number == 577

    def test_get_epics_returns_none_for_expired_cache(self, cache_service, mock_epic):
        """Test get_epics returns None for expired cache."""
        old_time = datetime.now() - timedelta(minutes=60)
        expired_metadata = SyncMetadata(
            repo_url="https://github.com/owner/repo",
            last_sync=old_time,
            ttl_minutes=30,
        )

        cache_service.save_cache([mock_epic], expired_metadata)

        assert cache_service.get_epics() is None

    def test_get_epics_returns_empty_list_when_no_epics(
        self, cache_service, mock_metadata
    ):
        """Test get_epics returns empty list when cache has no epics."""
        cache_service.save_cache([], mock_metadata)

        epics = cache_service.get_epics()

        assert epics is not None
        assert len(epics) == 0

    def test_get_epics_skips_corrupted_epics(
        self, cache_service, mock_metadata, capsys
    ):
        """Test get_epics skips corrupted epics and continues."""
        # Create valid epic
        valid_epic = {
            "number": 577,
            "title": "Valid Epic",
            "state": "open",
            "labels": [{"name": "epic"}],
            "body": "Description",
            "url": "https://github.com/owner/repo/issues/577",
        }

        # Create corrupted epic (missing required fields)
        corrupted_epic = {"number": 999}

        cache_data = {
            "version": "1.0.0",
            "metadata": mock_metadata.to_dict(),
            "epics": [corrupted_epic, valid_epic],
        }

        cache_service.cache_path.write_text(json.dumps(cache_data))

        epics = cache_service.get_epics()

        # Should skip corrupted and return only valid
        assert epics is not None
        assert len(epics) == 1
        assert epics[0].number == 577

        # Verify warning was printed
        captured = capsys.readouterr()
        assert "Warning" in captured.out
        assert "corrupted epic" in captured.out

    def test_get_epics_returns_none_on_cache_error(self, cache_service):
        """Test get_epics returns None when cache is corrupted."""
        cache_service.cache_path.write_text("not valid json")

        assert cache_service.get_epics() is None


class TestGetMetadata:
    """Tests for get_metadata method."""

    def test_get_metadata_returns_none_when_no_cache(self, cache_service):
        """Test get_metadata returns None when cache doesn't exist."""
        assert cache_service.get_metadata() is None

    def test_get_metadata_returns_metadata_for_valid_cache(
        self, cache_service, mock_epic, mock_metadata
    ):
        """Test get_metadata returns metadata for valid cache."""
        cache_service.save_cache([mock_epic], mock_metadata)

        metadata = cache_service.get_metadata()

        assert metadata is not None
        assert isinstance(metadata, SyncMetadata)
        assert metadata.repo_url == "https://github.com/owner/repo"
        assert metadata.ttl_minutes == 30

    def test_get_metadata_returns_none_on_corrupted_cache(self, cache_service):
        """Test get_metadata returns None for corrupted cache."""
        cache_service.cache_path.write_text("corrupted")

        assert cache_service.get_metadata() is None

    def test_get_metadata_returns_none_on_missing_metadata_key(
        self, cache_service, mock_epic
    ):
        """Test get_metadata returns None when metadata key is missing."""
        cache_data = {"version": "1.0.0", "epics": [mock_epic.to_dict()]}
        cache_service.cache_path.write_text(json.dumps(cache_data))

        assert cache_service.get_metadata() is None


class TestInvalidate:
    """Tests for invalidate method."""

    def test_invalidate_deletes_cache_file(
        self, cache_service, mock_epic, mock_metadata
    ):
        """Test invalidate deletes the cache file."""
        cache_service.save_cache([mock_epic], mock_metadata)
        assert cache_service.cache_path.exists()

        cache_service.invalidate()

        assert not cache_service.cache_path.exists()

    def test_invalidate_does_nothing_when_no_cache(self, cache_service):
        """Test invalidate doesn't raise error when cache doesn't exist."""
        assert not cache_service.cache_path.exists()

        # Should not raise
        cache_service.invalidate()

        assert not cache_service.cache_path.exists()

    def test_invalidate_raises_on_io_error(self, cache_service, mock_epic, mock_metadata):
        """Test invalidate raises CacheError on I/O error."""
        cache_service.save_cache([mock_epic], mock_metadata)

        # Make file undeletable
        cache_service.cache_path.chmod(0o000)
        cache_service.cache_path.parent.chmod(0o555)

        try:
            with pytest.raises(CacheError) as exc_info:
                cache_service.invalidate()

            assert "Failed to delete cache file" in str(exc_info.value)
        finally:
            # Restore permissions
            cache_service.cache_path.chmod(0o644)
            cache_service.cache_path.parent.chmod(0o755)


class TestGetCacheAgeMinutes:
    """Tests for get_cache_age_minutes method."""

    def test_get_cache_age_returns_none_when_no_cache(self, cache_service):
        """Test get_cache_age_minutes returns None when cache doesn't exist."""
        assert cache_service.get_cache_age_minutes() is None

    def test_get_cache_age_returns_age_for_valid_cache(
        self, cache_service, mock_epic, mock_metadata
    ):
        """Test get_cache_age_minutes returns age for valid cache."""
        cache_service.save_cache([mock_epic], mock_metadata)

        age = cache_service.get_cache_age_minutes()

        assert age is not None
        assert age >= 0
        assert age < 1  # Should be very recent (less than 1 minute)

    def test_get_cache_age_returns_correct_age_for_old_cache(
        self, cache_service, mock_epic
    ):
        """Test get_cache_age_minutes returns correct age for old cache."""
        # Create metadata 45 minutes old
        old_time = datetime.now() - timedelta(minutes=45)
        old_metadata = SyncMetadata(
            repo_url="https://github.com/owner/repo",
            last_sync=old_time,
            ttl_minutes=30,
        )

        cache_service.save_cache([mock_epic], old_metadata)

        age = cache_service.get_cache_age_minutes()

        assert age is not None
        assert 44 <= age <= 46  # Around 45 minutes (with small tolerance)

    def test_get_cache_age_returns_none_on_corrupted_cache(self, cache_service):
        """Test get_cache_age_minutes returns None for corrupted cache."""
        cache_service.cache_path.write_text("corrupted")

        assert cache_service.get_cache_age_minutes() is None
