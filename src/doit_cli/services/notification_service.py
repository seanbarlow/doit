"""Notification service for team collaboration.

This module provides the NotificationService class for managing
change notifications between team members.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from doit_cli.models.team_models import (
    Notification,
    NotificationSettings,
    NotificationType,
)


@dataclass
class NotificationState:
    """State stored in notifications.json."""

    notifications: list[Notification] = field(default_factory=list)
    settings: NotificationSettings = field(default_factory=NotificationSettings)
    last_batch_sent: Optional[datetime] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "notifications": [n.to_dict() for n in self.notifications],
            "settings": self.settings.to_dict(),
            "last_batch_sent": self.last_batch_sent.isoformat()
            if self.last_batch_sent
            else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "NotificationState":
        """Create from dictionary."""
        return cls(
            notifications=[
                Notification.from_dict(n) for n in data.get("notifications", [])
            ],
            settings=NotificationSettings.from_dict(data.get("settings", {})),
            last_batch_sent=datetime.fromisoformat(data["last_batch_sent"])
            if data.get("last_batch_sent")
            else None,
        )


class NotificationService:
    """Manages team change notifications.

    This service provides methods for:
    - Creating notifications
    - Retrieving and filtering notifications
    - Marking notifications as read
    - Batching notifications
    - Managing notification settings
    """

    MAX_NOTIFICATIONS = 100  # Keep last 100 notifications
    MAX_BATCH_SIZE = 10  # Maximum notifications per batch

    def __init__(self, project_root: Path = None):
        """Initialize NotificationService.

        Args:
            project_root: Project root directory. Defaults to cwd.
        """
        self.project_root = project_root or Path.cwd()
        self._state: Optional[NotificationState] = None

    @property
    def state_path(self) -> Path:
        """Get path to notifications state file."""
        return self.project_root / ".doit" / "state" / "notifications.json"

    def _load_state(self) -> NotificationState:
        """Load notification state from file."""
        if self.state_path.exists():
            try:
                with open(self.state_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return NotificationState.from_dict(data)
            except (json.JSONDecodeError, KeyError):
                pass
        return NotificationState()

    def _save_state(self, state: NotificationState) -> None:
        """Save notification state to file."""
        self.state_path.parent.mkdir(parents=True, exist_ok=True)

        # Prune old notifications
        state.notifications = self._prune_notifications(state.notifications)

        with open(self.state_path, "w", encoding="utf-8") as f:
            json.dump(state.to_dict(), f, indent=2)

    def _prune_notifications(
        self, notifications: list[Notification]
    ) -> list[Notification]:
        """Remove expired and excess notifications."""
        # Remove expired
        active = [n for n in notifications if not n.is_expired()]

        # Keep only last MAX_NOTIFICATIONS
        if len(active) > self.MAX_NOTIFICATIONS:
            active = active[-self.MAX_NOTIFICATIONS :]

        return active

    def get_state(self) -> NotificationState:
        """Get current notification state."""
        if self._state is None:
            self._state = self._load_state()
        return self._state

    def create_notification(
        self,
        notification_type: NotificationType,
        title: str,
        content: str,
        source_member: str,
        affected_files: list[str] = None,
    ) -> Notification:
        """Create a new notification.

        Args:
            notification_type: Type of notification
            title: Short title
            content: Detailed content
            source_member: Email of who triggered this
            affected_files: List of affected file paths

        Returns:
            Created Notification
        """
        notification = Notification.create(
            notification_type=notification_type,
            title=title,
            content=content,
            source_member=source_member,
            affected_files=affected_files,
        )

        state = self.get_state()
        state.notifications.append(notification)
        self._save_state(state)
        self._state = state

        return notification

    def get_notifications(
        self,
        unread_only: bool = False,
        limit: int = 50,
        notification_type: NotificationType = None,
    ) -> list[Notification]:
        """Get notifications.

        Args:
            unread_only: Only return unread notifications
            limit: Maximum number to return
            notification_type: Filter by type

        Returns:
            List of Notification objects (newest first)
        """
        state = self.get_state()
        notifications = state.notifications.copy()

        # Filter by unread
        if unread_only:
            notifications = [n for n in notifications if not n.read]

        # Filter by type
        if notification_type:
            notifications = [n for n in notifications if n.type == notification_type]

        # Sort by created_at descending (newest first)
        notifications.sort(key=lambda n: n.created_at, reverse=True)

        # Limit
        return notifications[:limit]

    def get_unread_count(self) -> int:
        """Get count of unread notifications."""
        state = self.get_state()
        return sum(1 for n in state.notifications if not n.read)

    def mark_read(self, notification_id: str = None) -> int:
        """Mark notification(s) as read.

        Args:
            notification_id: Specific ID to mark, or None for all

        Returns:
            Number of notifications marked as read
        """
        state = self.get_state()
        count = 0

        for notification in state.notifications:
            if notification_id is None or notification.id == notification_id:
                if not notification.read:
                    notification.read = True
                    count += 1

        if count > 0:
            self._save_state(state)
            self._state = state

        return count

    def get_settings(self) -> NotificationSettings:
        """Get notification settings."""
        return self.get_state().settings

    def update_settings(
        self,
        enabled: bool = None,
        batch_interval_minutes: int = None,
        on_sync: bool = None,
        on_conflict: bool = None,
        on_member_change: bool = None,
    ) -> NotificationSettings:
        """Update notification settings.

        Args:
            enabled: Enable/disable notifications
            batch_interval_minutes: Batching interval
            on_sync: Notify on sync events
            on_conflict: Notify on conflicts
            on_member_change: Notify on member changes

        Returns:
            Updated NotificationSettings
        """
        state = self.get_state()
        settings = state.settings

        if enabled is not None:
            settings.enabled = enabled
        if batch_interval_minutes is not None:
            settings.batch_interval_minutes = batch_interval_minutes
        if on_sync is not None:
            settings.on_sync = on_sync
        if on_conflict is not None:
            settings.on_conflict = on_conflict
        if on_member_change is not None:
            settings.on_member_change = on_member_change

        self._save_state(state)
        self._state = state

        return settings

    def should_batch(self) -> bool:
        """Check if notifications should be batched (interval not elapsed)."""
        state = self.get_state()

        if not state.settings.enabled:
            return True  # Always batch if disabled

        if state.last_batch_sent is None:
            return False  # First notification, don't batch

        elapsed = datetime.now() - state.last_batch_sent
        interval = timedelta(minutes=state.settings.batch_interval_minutes)

        return elapsed < interval

    def process_batch(self) -> list[Notification]:
        """Process and return batched notifications for display.

        Returns:
            List of notifications to display
        """
        state = self.get_state()

        if not state.settings.enabled:
            return []

        # Get unread notifications
        unread = [n for n in state.notifications if not n.read]

        if not unread:
            return []

        # Limit to batch size
        batch = unread[-self.MAX_BATCH_SIZE :]

        # Update last batch sent
        state.last_batch_sent = datetime.now()
        self._save_state(state)
        self._state = state

        return batch

    def clear_all(self) -> int:
        """Clear all notifications.

        Returns:
            Number of notifications cleared
        """
        state = self.get_state()
        count = len(state.notifications)
        state.notifications = []
        self._save_state(state)
        self._state = state
        return count

    # Convenience methods for creating specific notification types

    def notify_memory_changed(
        self,
        source_member: str,
        affected_files: list[str],
    ) -> Optional[Notification]:
        """Create a memory changed notification."""
        settings = self.get_settings()
        if not settings.enabled or not settings.on_sync:
            return None

        files_str = ", ".join(affected_files[:3])
        if len(affected_files) > 3:
            files_str += f" (+{len(affected_files) - 3} more)"

        return self.create_notification(
            notification_type=NotificationType.MEMORY_CHANGED,
            title=f"{source_member} updated memory files",
            content=f"Modified: {files_str}",
            source_member=source_member,
            affected_files=affected_files,
        )

    def notify_conflict_detected(
        self,
        source_member: str,
        affected_files: list[str],
    ) -> Optional[Notification]:
        """Create a conflict detected notification."""
        settings = self.get_settings()
        if not settings.enabled or not settings.on_conflict:
            return None

        files_str = ", ".join(affected_files)

        return self.create_notification(
            notification_type=NotificationType.CONFLICT_DETECTED,
            title="Sync conflict detected",
            content=f"Conflicts in: {files_str}. Run 'doit team sync' to resolve.",
            source_member=source_member,
            affected_files=affected_files,
        )

    def notify_member_joined(
        self,
        new_member_email: str,
        added_by: str,
    ) -> Optional[Notification]:
        """Create a member joined notification."""
        settings = self.get_settings()
        if not settings.enabled or not settings.on_member_change:
            return None

        return self.create_notification(
            notification_type=NotificationType.MEMBER_JOINED,
            title=f"{new_member_email} joined the team",
            content=f"Added by {added_by}",
            source_member=added_by,
        )

    def notify_permission_changed(
        self,
        member_email: str,
        changed_by: str,
        new_permission: str,
    ) -> Optional[Notification]:
        """Create a permission changed notification."""
        settings = self.get_settings()
        if not settings.enabled or not settings.on_member_change:
            return None

        return self.create_notification(
            notification_type=NotificationType.PERMISSION_CHANGED,
            title=f"Permission changed for {member_email}",
            content=f"New permission: {new_permission}. Changed by {changed_by}",
            source_member=changed_by,
        )
