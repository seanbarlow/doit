"""GitHub cache service for managing cached epic data.

This service handles reading, writing, and validating cached GitHub epic data
to minimize API calls and support offline mode.
"""

import json
from pathlib import Path
from typing import List, Optional

from ..models.github_epic import GitHubEpic
from ..models.sync_metadata import SyncMetadata


class CacheError(Exception):
    """Base exception for cache-related errors."""

    pass


class GitHubCacheService:
    """Service for managing GitHub epic cache.

    Handles reading and writing epic data to a JSON cache file with
    TTL-based validation and corruption handling.
    """

    def __init__(self, cache_path: Optional[Path] = None):
        """Initialize cache service.

        Args:
            cache_path: Path to cache file. Default: .doit/cache/github_epics.json
        """
        if cache_path is None:
            cache_path = Path(".doit/cache/github_epics.json")

        self.cache_path = cache_path
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)

    def load_cache(self) -> Optional[dict]:
        """Load cache data from file.

        Returns:
            Dictionary with 'metadata' and 'epics' keys, or None if cache doesn't exist

        Examples:
            >>> service = GitHubCacheService()
            >>> cache = service.load_cache()
            >>> cache is None or 'metadata' in cache
            True
        """
        if not self.cache_path.exists():
            return None

        try:
            with open(self.cache_path, "r") as f:
                cache_data = json.load(f)

            # Validate cache structure
            if not isinstance(cache_data, dict):
                raise CacheError("Cache data must be a dictionary")

            if "metadata" not in cache_data or "epics" not in cache_data:
                raise CacheError("Cache missing required keys: metadata, epics")

            return cache_data

        except json.JSONDecodeError as e:
            raise CacheError(f"Corrupted cache file: {e}")
        except IOError as e:
            raise CacheError(f"Failed to read cache file: {e}")

    def save_cache(self, epics: List[GitHubEpic], metadata: SyncMetadata) -> None:
        """Save epics and metadata to cache file.

        Args:
            epics: List of GitHubEpic instances to cache
            metadata: Sync metadata to store

        Raises:
            CacheError: If cache cannot be written

        Examples:
            >>> from datetime import datetime
            >>> service = GitHubCacheService()
            >>> metadata = SyncMetadata.create_new("https://github.com/owner/repo")
            >>> service.save_cache([], metadata)
        """
        try:
            cache_data = {
                "version": "1.0.0",
                "metadata": metadata.to_dict(),
                "epics": [epic.to_dict() for epic in epics],
            }

            # Write atomically by writing to temp file then renaming
            temp_path = self.cache_path.with_suffix(".tmp")

            with open(temp_path, "w") as f:
                json.dump(cache_data, f, indent=2)

            # Atomic rename
            temp_path.replace(self.cache_path)

        except IOError as e:
            raise CacheError(f"Failed to write cache file: {e}")

    def is_valid(self) -> bool:
        """Check if cache exists and is still valid based on TTL.

        Returns:
            True if cache is valid, False otherwise

        Examples:
            >>> service = GitHubCacheService()
            >>> service.is_valid()
            False  # If no cache exists
        """
        try:
            cache_data = self.load_cache()
            if cache_data is None:
                return False

            metadata = SyncMetadata.from_dict(cache_data["metadata"])
            return metadata.is_valid

        except (CacheError, KeyError, ValueError):
            return False

    def get_epics(self) -> Optional[List[GitHubEpic]]:
        """Get epics from cache if valid.

        Returns:
            List of GitHubEpic instances, or None if cache is invalid

        Examples:
            >>> service = GitHubCacheService()
            >>> epics = service.get_epics()
            >>> epics is None or isinstance(epics, list)
            True
        """
        if not self.is_valid():
            return None

        try:
            cache_data = self.load_cache()
            if cache_data is None:
                return None

            epics = []
            for epic_data in cache_data["epics"]:
                try:
                    epic = GitHubEpic.from_gh_json(epic_data)
                    epics.append(epic)
                except (ValueError, KeyError) as e:
                    print(f"Warning: Skipping corrupted epic in cache: {e}")
                    continue

            return epics

        except CacheError:
            return None

    def get_metadata(self) -> Optional[SyncMetadata]:
        """Get sync metadata from cache.

        Returns:
            SyncMetadata instance, or None if cache doesn't exist

        Examples:
            >>> service = GitHubCacheService()
            >>> metadata = service.get_metadata()
            >>> metadata is None or isinstance(metadata, SyncMetadata)
            True
        """
        try:
            cache_data = self.load_cache()
            if cache_data is None:
                return None

            return SyncMetadata.from_dict(cache_data["metadata"])

        except (CacheError, KeyError, ValueError):
            return None

    def invalidate(self) -> None:
        """Invalidate (delete) the cache file.

        Examples:
            >>> service = GitHubCacheService()
            >>> service.invalidate()
        """
        if self.cache_path.exists():
            try:
                self.cache_path.unlink()
            except IOError as e:
                raise CacheError(f"Failed to delete cache file: {e}")

    def get_cache_age_minutes(self) -> Optional[float]:
        """Get cache age in minutes.

        Returns:
            Number of minutes since last sync, or None if no cache exists

        Examples:
            >>> service = GitHubCacheService()
            >>> age = service.get_cache_age_minutes()
            >>> age is None or age >= 0
            True
        """
        metadata = self.get_metadata()
        if metadata is None:
            return None

        return metadata.age_minutes
