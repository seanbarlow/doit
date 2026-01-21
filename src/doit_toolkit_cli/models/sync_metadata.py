"""Sync metadata model for tracking GitHub synchronization state.

This module provides the SyncMetadata dataclass for managing cache validation
and synchronization tracking between GitHub and local roadmap.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional


@dataclass
class SyncMetadata:
    """Tracks synchronization state between GitHub and local roadmap.

    Attributes:
        repo_url: GitHub repository URL (e.g., "https://github.com/owner/repo")
        last_sync: Timestamp of last successful sync
        ttl_minutes: Cache time-to-live in minutes (default: 30)
        cache_version: Cache format version for migrations (default: "1.0.0")
    """

    repo_url: str
    last_sync: datetime
    ttl_minutes: int = 30
    cache_version: str = "1.0.0"

    def __post_init__(self):
        """Validate metadata after initialization."""
        if not self.repo_url or "github.com" not in self.repo_url:
            raise ValueError(f"Invalid GitHub repository URL: {self.repo_url}")

        if self.ttl_minutes <= 0:
            raise ValueError(f"TTL must be positive, got {self.ttl_minutes}")

        if not self.cache_version:
            raise ValueError("Cache version cannot be empty")

    @property
    def is_valid(self) -> bool:
        """Check if the cache is still valid based on TTL.

        Returns:
            True if cache has not expired, False otherwise

        Examples:
            >>> from datetime import datetime, timedelta
            >>> metadata = SyncMetadata(
            ...     repo_url="https://github.com/owner/repo",
            ...     last_sync=datetime.now(),
            ...     ttl_minutes=30
            ... )
            >>> metadata.is_valid
            True
        """
        if not self.last_sync:
            return False

        ttl_delta = timedelta(minutes=self.ttl_minutes)
        return datetime.now() - self.last_sync < ttl_delta

    @property
    def expires_at(self) -> datetime:
        """Calculate when the cache will expire.

        Returns:
            Expiration datetime
        """
        return self.last_sync + timedelta(minutes=self.ttl_minutes)

    @property
    def age_minutes(self) -> float:
        """Calculate cache age in minutes.

        Returns:
            Number of minutes since last sync
        """
        return (datetime.now() - self.last_sync).total_seconds() / 60

    def to_dict(self) -> dict:
        """Convert metadata to dictionary for JSON serialization.

        Returns:
            Dictionary representation of the metadata
        """
        return {
            "repo_url": self.repo_url,
            "last_sync": self.last_sync.isoformat(),
            "ttl_minutes": self.ttl_minutes,
            "cache_version": self.cache_version,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SyncMetadata":
        """Create SyncMetadata from dictionary.

        Args:
            data: Dictionary with metadata fields

        Returns:
            SyncMetadata instance

        Examples:
            >>> data = {
            ...     "repo_url": "https://github.com/owner/repo",
            ...     "last_sync": "2026-01-21T15:30:00",
            ...     "ttl_minutes": 30,
            ...     "cache_version": "1.0.0"
            ... }
            >>> metadata = SyncMetadata.from_dict(data)
            >>> metadata.repo_url
            'https://github.com/owner/repo'
        """
        # Parse timestamp
        last_sync = datetime.fromisoformat(data["last_sync"])

        return cls(
            repo_url=data["repo_url"],
            last_sync=last_sync,
            ttl_minutes=data.get("ttl_minutes", 30),
            cache_version=data.get("cache_version", "1.0.0"),
        )

    @classmethod
    def create_new(cls, repo_url: str, ttl_minutes: int = 30) -> "SyncMetadata":
        """Create new metadata with current timestamp.

        Args:
            repo_url: GitHub repository URL
            ttl_minutes: Cache TTL in minutes (default: 30)

        Returns:
            New SyncMetadata instance with current time

        Examples:
            >>> metadata = SyncMetadata.create_new("https://github.com/owner/repo")
            >>> metadata.is_valid
            True
        """
        return cls(
            repo_url=repo_url,
            last_sync=datetime.now(),
            ttl_minutes=ttl_minutes,
        )
