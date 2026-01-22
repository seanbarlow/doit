"""File watcher service for monitoring memory file changes.

This module provides the FileWatcherService class for monitoring
.doit/memory/ directory changes using the watchdog library.
"""

import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from doit_cli.services.notification_service import NotificationService


@dataclass
class FileChangeEvent:
    """Represents a file change event."""

    path: str  # Relative path from .doit/memory/
    event_type: str  # 'created', 'modified', 'deleted', 'moved'
    timestamp: datetime = field(default_factory=datetime.now)
    is_directory: bool = False

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "path": self.path,
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "is_directory": self.is_directory,
        }


class MemoryFileHandler(FileSystemEventHandler):
    """Handler for file system events in .doit/memory/."""

    def __init__(
        self,
        memory_dir: Path,
        on_change: Callable[[FileChangeEvent], None],
        ignored_patterns: list[str] = None,
    ):
        """Initialize handler.

        Args:
            memory_dir: Path to .doit/memory/ directory
            on_change: Callback for file changes
            ignored_patterns: File patterns to ignore (e.g., ["*.tmp", ".git*"])
        """
        self.memory_dir = memory_dir
        self.on_change = on_change
        self.ignored_patterns = ignored_patterns or [
            "*.tmp",
            "*.swp",
            "*~",
            ".git*",
            "__pycache__",
            "*.pyc",
        ]

    def _should_ignore(self, path: str) -> bool:
        """Check if path should be ignored."""
        from fnmatch import fnmatch

        name = Path(path).name
        for pattern in self.ignored_patterns:
            if fnmatch(name, pattern):
                return True
        return False

    def _get_relative_path(self, src_path: str) -> str:
        """Get path relative to memory directory."""
        try:
            return str(Path(src_path).relative_to(self.memory_dir))
        except ValueError:
            return Path(src_path).name

    def _handle_event(self, event: FileSystemEvent, event_type: str) -> None:
        """Handle a file system event."""
        if self._should_ignore(event.src_path):
            return

        change_event = FileChangeEvent(
            path=self._get_relative_path(event.src_path),
            event_type=event_type,
            timestamp=datetime.now(),
            is_directory=event.is_directory,
        )
        self.on_change(change_event)

    def on_created(self, event: FileSystemEvent) -> None:
        """Handle file/directory creation."""
        self._handle_event(event, "created")

    def on_modified(self, event: FileSystemEvent) -> None:
        """Handle file/directory modification."""
        self._handle_event(event, "modified")

    def on_deleted(self, event: FileSystemEvent) -> None:
        """Handle file/directory deletion."""
        self._handle_event(event, "deleted")

    def on_moved(self, event: FileSystemEvent) -> None:
        """Handle file/directory move."""
        self._handle_event(event, "moved")


class FileWatcherService:
    """Monitors .doit/memory/ for file changes.

    This service:
    - Watches the .doit/memory/ directory for changes
    - Debounces rapid changes to avoid notification spam
    - Triggers notifications via NotificationService
    - Runs in a background thread
    """

    DEBOUNCE_SECONDS = 2.0  # Wait 2 seconds after last change before notifying

    def __init__(
        self,
        project_root: Path = None,
        notification_service: NotificationService = None,
        current_user: str = None,
    ):
        """Initialize FileWatcherService.

        Args:
            project_root: Project root directory. Defaults to cwd.
            notification_service: Service for creating notifications
            current_user: Email of current user (to filter out self-changes)
        """
        self.project_root = project_root or Path.cwd()
        self.notification_service = notification_service or NotificationService(
            self.project_root
        )
        self.current_user = current_user or ""

        self._observer: Optional[Observer] = None
        self._is_running = False
        self._pending_changes: list[FileChangeEvent] = []
        self._last_change_time: Optional[datetime] = None
        self._debounce_timer: Optional[threading.Timer] = None
        self._lock = threading.Lock()
        self._on_change_callbacks: list[Callable[[list[FileChangeEvent]], None]] = []

    @property
    def memory_dir(self) -> Path:
        """Get path to memory directory."""
        return self.project_root / ".doit" / "memory"

    @property
    def is_running(self) -> bool:
        """Check if watcher is running."""
        return self._is_running

    def add_change_callback(
        self, callback: Callable[[list[FileChangeEvent]], None]
    ) -> None:
        """Add a callback for batched change notifications.

        Args:
            callback: Function called with list of change events
        """
        self._on_change_callbacks.append(callback)

    def _on_file_change(self, event: FileChangeEvent) -> None:
        """Handle a single file change event."""
        with self._lock:
            self._pending_changes.append(event)
            self._last_change_time = datetime.now()

            # Cancel existing timer
            if self._debounce_timer:
                self._debounce_timer.cancel()

            # Start new debounce timer
            self._debounce_timer = threading.Timer(
                self.DEBOUNCE_SECONDS, self._process_pending_changes
            )
            self._debounce_timer.start()

    def _process_pending_changes(self) -> None:
        """Process accumulated changes after debounce period."""
        with self._lock:
            if not self._pending_changes:
                return

            changes = self._pending_changes.copy()
            self._pending_changes.clear()

        # Deduplicate changes for the same file
        seen_paths = {}
        for change in changes:
            key = change.path
            # Keep the latest event for each path
            seen_paths[key] = change

        unique_changes = list(seen_paths.values())

        # Call registered callbacks
        for callback in self._on_change_callbacks:
            try:
                callback(unique_changes)
            except Exception:
                pass  # Don't let callback errors stop processing

        # Create notification if there are file changes
        if unique_changes:
            self._create_change_notification(unique_changes)

    def _create_change_notification(self, changes: list[FileChangeEvent]) -> None:
        """Create notification for file changes."""
        # Filter to just file changes (not directories)
        file_changes = [c for c in changes if not c.is_directory]

        if not file_changes:
            return

        affected_files = [c.path for c in file_changes]

        # Try to create notification (may be disabled by settings)
        self.notification_service.notify_memory_changed(
            source_member=self.current_user or "unknown",
            affected_files=affected_files,
        )

    def start(self) -> bool:
        """Start watching for file changes.

        Returns:
            True if started successfully, False if already running or error
        """
        if self._is_running:
            return False

        # Ensure memory directory exists
        if not self.memory_dir.exists():
            self.memory_dir.mkdir(parents=True, exist_ok=True)

        try:
            handler = MemoryFileHandler(
                memory_dir=self.memory_dir,
                on_change=self._on_file_change,
            )

            self._observer = Observer()
            self._observer.schedule(handler, str(self.memory_dir), recursive=True)
            self._observer.start()
            self._is_running = True
            return True

        except Exception:
            self._is_running = False
            return False

    def stop(self) -> None:
        """Stop watching for file changes."""
        if not self._is_running:
            return

        # Cancel debounce timer
        if self._debounce_timer:
            self._debounce_timer.cancel()
            self._debounce_timer = None

        # Process any remaining changes
        if self._pending_changes:
            self._process_pending_changes()

        # Stop observer
        if self._observer:
            self._observer.stop()
            self._observer.join(timeout=5.0)
            self._observer = None

        self._is_running = False

    def wait(self, timeout: float = None) -> None:
        """Wait for watcher to stop.

        Args:
            timeout: Maximum seconds to wait (None = forever)
        """
        if self._observer:
            self._observer.join(timeout=timeout)


class FileWatcherManager:
    """Singleton manager for file watcher instances.

    Use this to get a shared watcher instance across the application.
    """

    _instance: Optional["FileWatcherManager"] = None
    _watcher: Optional[FileWatcherService] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_watcher(
        self,
        project_root: Path = None,
        notification_service: NotificationService = None,
        current_user: str = None,
    ) -> FileWatcherService:
        """Get or create the file watcher instance.

        Args:
            project_root: Project root directory
            notification_service: Notification service instance
            current_user: Current user email

        Returns:
            FileWatcherService instance
        """
        if self._watcher is None:
            self._watcher = FileWatcherService(
                project_root=project_root,
                notification_service=notification_service,
                current_user=current_user,
            )
        return self._watcher

    def stop_watcher(self) -> None:
        """Stop and clear the watcher instance."""
        if self._watcher:
            self._watcher.stop()
            self._watcher = None
