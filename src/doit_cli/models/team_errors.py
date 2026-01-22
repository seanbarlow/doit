"""Error hierarchy for team collaboration features.

This module provides a comprehensive set of exception classes
for handling errors in team collaboration operations.
"""

from typing import Optional


class TeamError(Exception):
    """Base exception for all team collaboration errors.

    All team-related exceptions inherit from this class to allow
    catching any team error with a single except clause.
    """

    def __init__(self, message: str, details: dict = None):
        """Initialize TeamError.

        Args:
            message: Human-readable error message
            details: Optional dictionary with additional context
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message


# =============================================================================
# Configuration Errors
# =============================================================================


class ConfigurationError(TeamError):
    """Base class for configuration-related errors."""

    pass


class TeamNotInitializedError(ConfigurationError):
    """Team collaboration not initialized for this project."""

    def __init__(self, message: str = None):
        super().__init__(
            message or "Team collaboration not initialized. Run 'doit team init' first."
        )


class TeamAlreadyInitializedError(ConfigurationError):
    """Team collaboration already initialized."""

    def __init__(self, message: str = None):
        super().__init__(
            message or "Team collaboration already initialized. Delete .doit/config/team.yaml to reinitialize."
        )


class InvalidConfigurationError(ConfigurationError):
    """Configuration file is invalid or corrupted."""

    def __init__(self, message: str, validation_errors: list[str] = None):
        super().__init__(message, {"validation_errors": validation_errors or []})
        self.validation_errors = validation_errors or []


# =============================================================================
# Member Errors
# =============================================================================


class MemberError(TeamError):
    """Base class for member-related errors."""

    def __init__(self, message: str, email: str = None):
        super().__init__(message, {"email": email} if email else {})
        self.email = email


class MemberNotFoundError(MemberError):
    """Team member not found."""

    def __init__(self, email: str):
        super().__init__(f"Team member not found: {email}", email)


class MemberAlreadyExistsError(MemberError):
    """Team member already exists."""

    def __init__(self, email: str):
        super().__init__(f"Team member already exists: {email}", email)


class InvalidEmailError(MemberError):
    """Email format is invalid."""

    def __init__(self, email: str):
        super().__init__(f"Invalid email format: {email}", email)


class CannotRemoveLastOwnerError(MemberError):
    """Cannot remove the last team owner."""

    def __init__(self, email: str):
        super().__init__(
            f"Cannot remove {email}: they are the last owner. Transfer ownership first.",
            email,
        )


# =============================================================================
# Access Control Errors
# =============================================================================


class AccessError(TeamError):
    """Base class for access control errors."""

    pass


class PermissionDeniedError(AccessError):
    """User lacks permission for the requested action."""

    def __init__(
        self,
        action: str,
        required_permission: str = None,
        message: str = None,
    ):
        msg = message or f"Permission denied for '{action}'"
        if required_permission:
            msg += f". Required: {required_permission}"
        super().__init__(msg, {"action": action, "required": required_permission})
        self.action = action
        self.required_permission = required_permission


class ReadOnlyAccessError(PermissionDeniedError):
    """User has read-only access and cannot modify."""

    def __init__(self, action: str = "write"):
        super().__init__(
            action=action,
            required_permission="read-write",
            message="You have read-only access and cannot push changes. Contact the team owner to update your permissions.",
        )


class OwnerRequiredError(PermissionDeniedError):
    """Action requires owner permission."""

    def __init__(self, action: str):
        super().__init__(
            action=action,
            required_permission="owner",
            message=f"Only team owners can {action}.",
        )


# =============================================================================
# Sync Errors
# =============================================================================


class SyncError(TeamError):
    """Base class for synchronization errors."""

    pass


class NoRemoteConfiguredError(SyncError):
    """No Git remote is configured for sync."""

    def __init__(self):
        super().__init__(
            "No Git remote configured. Push your repository to a remote first."
        )


class NetworkError(SyncError):
    """Network operation failed."""

    def __init__(self, message: str = None):
        super().__init__(
            message or "Cannot reach remote repository. Check your network connection."
        )


class SyncConflictError(SyncError):
    """Sync resulted in conflicts."""

    def __init__(self, conflicting_files: list[str]):
        files_str = ", ".join(conflicting_files[:5])
        if len(conflicting_files) > 5:
            files_str += f" (+{len(conflicting_files) - 5} more)"
        super().__init__(
            f"Sync conflicts detected in: {files_str}",
            {"files": conflicting_files},
        )
        self.conflicting_files = conflicting_files


# =============================================================================
# Conflict Errors
# =============================================================================


class ConflictError(TeamError):
    """Base class for conflict-related errors."""

    pass


class ConflictNotFoundError(ConflictError):
    """Conflict record not found."""

    def __init__(self, conflict_id: str):
        super().__init__(f"Conflict not found: {conflict_id}", {"id": conflict_id})
        self.conflict_id = conflict_id


class ConflictResolutionError(ConflictError):
    """Failed to resolve conflict."""

    def __init__(self, conflict_id: str, reason: str):
        super().__init__(
            f"Failed to resolve conflict {conflict_id}: {reason}",
            {"id": conflict_id, "reason": reason},
        )
        self.conflict_id = conflict_id
        self.reason = reason


# =============================================================================
# Git Errors
# =============================================================================


class GitError(TeamError):
    """Base class for Git operation errors."""

    pass


class GitNotAvailableError(GitError):
    """Git is not installed or not available."""

    def __init__(self):
        super().__init__(
            "Git is not available. Please install Git and try again."
        )


class GitOperationError(GitError):
    """A Git operation failed."""

    def __init__(self, operation: str, stderr: str = None):
        msg = f"Git {operation} failed"
        if stderr:
            msg += f": {stderr}"
        super().__init__(msg, {"operation": operation, "stderr": stderr})
        self.operation = operation
        self.stderr = stderr


# =============================================================================
# File Errors
# =============================================================================


class FileError(TeamError):
    """Base class for file operation errors."""

    pass


class SharedFileNotFoundError(FileError):
    """Shared memory file not found."""

    def __init__(self, path: str):
        super().__init__(f"Shared file not found: {path}", {"path": path})
        self.path = path


class FileTooLargeError(FileError):
    """File exceeds maximum size for sharing."""

    def __init__(self, path: str, size_bytes: int, max_bytes: int):
        size_mb = size_bytes / (1024 * 1024)
        max_mb = max_bytes / (1024 * 1024)
        super().__init__(
            f"File {path} is too large ({size_mb:.1f}MB). Maximum allowed: {max_mb:.1f}MB",
            {"path": path, "size": size_bytes, "max": max_bytes},
        )
        self.path = path
        self.size_bytes = size_bytes
        self.max_bytes = max_bytes


# =============================================================================
# Notification Errors
# =============================================================================


class NotificationError(TeamError):
    """Base class for notification errors."""

    pass


class NotificationNotFoundError(NotificationError):
    """Notification not found."""

    def __init__(self, notification_id: str):
        super().__init__(
            f"Notification not found: {notification_id}",
            {"id": notification_id},
        )
        self.notification_id = notification_id
