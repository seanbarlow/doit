"""Data models for team collaboration features.

This module contains all data models, enums, and dataclasses
for the doit team collaboration workflow.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Literal, Optional
import uuid


# =============================================================================
# Enums
# =============================================================================


class TeamRole(str, Enum):
    """Role of a team member."""

    OWNER = "owner"
    MEMBER = "member"


class TeamPermission(str, Enum):
    """Permission level for a team member."""

    READ_WRITE = "read-write"
    READ_ONLY = "read-only"


class SyncStatus(str, Enum):
    """Status of a sync operation."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    CONFLICT = "conflict"
    ERROR = "error"


class SyncOperationType(str, Enum):
    """Type of sync operation."""

    PUSH = "push"
    PULL = "pull"
    MERGE = "merge"


class ConflictResolution(str, Enum):
    """Resolution strategy for conflicts."""

    KEEP_LOCAL = "keep_local"
    KEEP_REMOTE = "keep_remote"
    MANUAL_MERGE = "manual_merge"


class NotificationType(str, Enum):
    """Type of notification."""

    MEMORY_CHANGED = "memory_changed"
    CONFLICT_DETECTED = "conflict_detected"
    MEMBER_JOINED = "member_joined"
    PERMISSION_CHANGED = "permission_changed"


# =============================================================================
# Core Models (T003-T005)
# =============================================================================


@dataclass
class Team:
    """Represents a collaborative team working on a doit project.

    Stored in .doit/config/team.yaml under the 'team' key.
    """

    id: str
    name: str
    owner_id: str  # Email of team owner
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def create(cls, name: str, owner_email: str) -> "Team":
        """Create a new team with a generated UUID."""
        return cls(
            id=str(uuid.uuid4()),
            name=name,
            owner_id=owner_email,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for YAML serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "owner_id": self.owner_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Team":
        """Create Team from dictionary (YAML data)."""
        return cls(
            id=data["id"],
            name=data["name"],
            owner_id=data["owner_id"],
            created_at=datetime.fromisoformat(data["created_at"])
            if isinstance(data.get("created_at"), str)
            else data.get("created_at", datetime.now()),
            updated_at=datetime.fromisoformat(data["updated_at"])
            if isinstance(data.get("updated_at"), str)
            else data.get("updated_at", datetime.now()),
        )


@dataclass
class TeamMember:
    """A developer with access to the shared project memory.

    Stored in .doit/config/team.yaml under the 'members' list.
    """

    id: str  # Email address (unique identifier)
    role: TeamRole
    permission: TeamPermission
    notifications: bool = True
    display_name: Optional[str] = None
    added_at: datetime = field(default_factory=datetime.now)
    added_by: str = ""
    last_sync: Optional[datetime] = None  # Tracked locally in state

    @classmethod
    def create(
        cls,
        email: str,
        role: TeamRole = TeamRole.MEMBER,
        permission: TeamPermission = TeamPermission.READ_WRITE,
        added_by: str = "",
        display_name: Optional[str] = None,
        notifications: bool = True,
    ) -> "TeamMember":
        """Create a new team member."""
        return cls(
            id=email,
            role=role,
            permission=permission,
            notifications=notifications,
            display_name=display_name,
            added_at=datetime.now(),
            added_by=added_by,
            last_sync=None,
        )

    @property
    def email(self) -> str:
        """Alias for id (email is the identifier)."""
        return self.id

    @property
    def is_owner(self) -> bool:
        """Check if member has owner role."""
        return self.role == TeamRole.OWNER

    @property
    def can_write(self) -> bool:
        """Check if member has write permission."""
        return self.permission == TeamPermission.READ_WRITE

    def to_dict(self) -> dict:
        """Convert to dictionary for YAML serialization."""
        result = {
            "id": self.id,
            "role": self.role.value,
            "permission": self.permission.value,
            "notifications": self.notifications,
            "added_at": self.added_at.isoformat(),
            "added_by": self.added_by,
        }
        if self.display_name:
            result["display_name"] = self.display_name
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "TeamMember":
        """Create TeamMember from dictionary (YAML data)."""
        return cls(
            id=data["id"],
            role=TeamRole(data["role"]),
            permission=TeamPermission(data["permission"]),
            notifications=data.get("notifications", True),
            display_name=data.get("display_name"),
            added_at=datetime.fromisoformat(data["added_at"])
            if isinstance(data.get("added_at"), str)
            else data.get("added_at", datetime.now()),
            added_by=data.get("added_by", ""),
            last_sync=datetime.fromisoformat(data["last_sync"])
            if data.get("last_sync") and isinstance(data["last_sync"], str)
            else None,
        )


@dataclass
class SharedMemory:
    """Tracks synchronized memory files between team members.

    Stored in .doit/config/team.yaml under the 'shared_files' list.
    """

    path: str  # Relative path from .doit/memory/ (e.g., "constitution.md")
    version: str  # Git commit hash of last sync
    modified_by: str  # Email of last modifier
    modified_at: datetime
    size_bytes: int = 0

    # Default shared files
    DEFAULT_FILES = ["constitution.md", "roadmap.md", "completed_roadmap.md"]

    @property
    def full_path(self) -> Path:
        """Get full path relative to project root."""
        return Path(".doit/memory") / self.path

    @classmethod
    def create(
        cls,
        path: str,
        modified_by: str,
        version: str = "",
        size_bytes: int = 0,
    ) -> "SharedMemory":
        """Create a new shared memory entry."""
        return cls(
            path=path,
            version=version,
            modified_by=modified_by,
            modified_at=datetime.now(),
            size_bytes=size_bytes,
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for YAML serialization."""
        return {
            "path": self.path,
            "version": self.version,
            "modified_by": self.modified_by,
            "modified_at": self.modified_at.isoformat(),
            "size_bytes": self.size_bytes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SharedMemory":
        """Create SharedMemory from dictionary (YAML data)."""
        return cls(
            path=data["path"],
            version=data.get("version", ""),
            modified_by=data.get("modified_by", ""),
            modified_at=datetime.fromisoformat(data["modified_at"])
            if isinstance(data.get("modified_at"), str)
            else data.get("modified_at", datetime.now()),
            size_bytes=data.get("size_bytes", 0),
        )


# =============================================================================
# Configuration Models
# =============================================================================


@dataclass
class SyncSettings:
    """Synchronization settings for team collaboration."""

    auto_sync: bool = False  # Automatically sync on file changes
    sync_on_command: bool = True  # Sync before/after doit commands
    conflict_strategy: str = "prompt"  # prompt | keep-local | keep-remote

    def to_dict(self) -> dict:
        """Convert to dictionary for YAML serialization."""
        return {
            "auto_sync": self.auto_sync,
            "sync_on_command": self.sync_on_command,
            "conflict_strategy": self.conflict_strategy,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SyncSettings":
        """Create SyncSettings from dictionary."""
        return cls(
            auto_sync=data.get("auto_sync", False),
            sync_on_command=data.get("sync_on_command", True),
            conflict_strategy=data.get("conflict_strategy", "prompt"),
        )


@dataclass
class NotificationSettings:
    """Notification settings for team collaboration."""

    enabled: bool = True
    batch_interval_minutes: int = 5
    on_sync: bool = True
    on_conflict: bool = True
    on_member_change: bool = False

    def to_dict(self) -> dict:
        """Convert to dictionary for YAML serialization."""
        return {
            "enabled": self.enabled,
            "batch_interval_minutes": self.batch_interval_minutes,
            "on_sync": self.on_sync,
            "on_conflict": self.on_conflict,
            "on_member_change": self.on_member_change,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "NotificationSettings":
        """Create NotificationSettings from dictionary."""
        return cls(
            enabled=data.get("enabled", True),
            batch_interval_minutes=data.get("batch_interval_minutes", 5),
            on_sync=data.get("on_sync", True),
            on_conflict=data.get("on_conflict", True),
            on_member_change=data.get("on_member_change", False),
        )


@dataclass
class TeamConfig:
    """Complete team configuration from team.yaml."""

    team: Team
    members: list[TeamMember] = field(default_factory=list)
    shared_files: list[SharedMemory] = field(default_factory=list)
    sync: SyncSettings = field(default_factory=SyncSettings)
    notifications: NotificationSettings = field(default_factory=NotificationSettings)

    def get_member(self, email: str) -> Optional[TeamMember]:
        """Find a member by email."""
        for member in self.members:
            if member.id == email:
                return member
        return None

    def has_member(self, email: str) -> bool:
        """Check if a member exists."""
        return self.get_member(email) is not None

    def get_owners(self) -> list[TeamMember]:
        """Get all members with owner role."""
        return [m for m in self.members if m.is_owner]

    def to_dict(self) -> dict:
        """Convert to dictionary for YAML serialization."""
        return {
            "team": self.team.to_dict(),
            "members": [m.to_dict() for m in self.members],
            "shared_files": [f.to_dict() for f in self.shared_files],
            "sync": self.sync.to_dict(),
            "notifications": self.notifications.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TeamConfig":
        """Create TeamConfig from dictionary (YAML data)."""
        return cls(
            team=Team.from_dict(data["team"]),
            members=[TeamMember.from_dict(m) for m in data.get("members", [])],
            shared_files=[SharedMemory.from_dict(f) for f in data.get("shared_files", [])],
            sync=SyncSettings.from_dict(data.get("sync", {})),
            notifications=NotificationSettings.from_dict(data.get("notifications", {})),
        )


# =============================================================================
# Notification Models (T015)
# =============================================================================


@dataclass
class Notification:
    """An alert about changes to shared memory files.

    Stored in .doit/state/notifications.json.
    """

    id: str
    type: NotificationType
    title: str
    content: str
    source_member: str  # Email of who triggered this
    affected_files: list[str] = field(default_factory=list)
    read: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None

    @classmethod
    def create(
        cls,
        notification_type: NotificationType,
        title: str,
        content: str,
        source_member: str,
        affected_files: list[str] = None,
        expires_days: int = 7,
    ) -> "Notification":
        """Create a new notification."""
        from datetime import timedelta

        return cls(
            id=str(uuid.uuid4()),
            type=notification_type,
            title=title,
            content=content,
            source_member=source_member,
            affected_files=affected_files or [],
            read=False,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=expires_days),
        )

    def is_expired(self) -> bool:
        """Check if notification has expired."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "type": self.type.value,
            "title": self.title,
            "content": self.content,
            "source_member": self.source_member,
            "affected_files": self.affected_files,
            "read": self.read,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Notification":
        """Create Notification from dictionary."""
        return cls(
            id=data["id"],
            type=NotificationType(data["type"]),
            title=data["title"],
            content=data["content"],
            source_member=data["source_member"],
            affected_files=data.get("affected_files", []),
            read=data.get("read", False),
            created_at=datetime.fromisoformat(data["created_at"])
            if isinstance(data.get("created_at"), str)
            else datetime.now(),
            expires_at=datetime.fromisoformat(data["expires_at"])
            if data.get("expires_at") and isinstance(data["expires_at"], str)
            else None,
        )


# =============================================================================
# Conflict Models (T019)
# =============================================================================


@dataclass
class ConflictVersion:
    """One side of a conflict (local or remote)."""

    content: str
    modified_by: str
    modified_at: datetime
    git_commit: str

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "content": self.content,
            "modified_by": self.modified_by,
            "modified_at": self.modified_at.isoformat(),
            "git_commit": self.git_commit,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ConflictVersion":
        """Create ConflictVersion from dictionary."""
        return cls(
            content=data["content"],
            modified_by=data["modified_by"],
            modified_at=datetime.fromisoformat(data["modified_at"])
            if isinstance(data.get("modified_at"), str)
            else datetime.now(),
            git_commit=data.get("git_commit", ""),
        )


@dataclass
class ConflictRecord:
    """Archives conflict details for resolution and recovery.

    Stored in .doit/state/conflicts/{conflict_id}.json.
    """

    id: str
    sync_operation_id: str
    file_path: str
    local_version: ConflictVersion
    remote_version: ConflictVersion
    resolution: Optional[ConflictResolution] = None
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def create(
        cls,
        sync_operation_id: str,
        file_path: str,
        local_version: ConflictVersion,
        remote_version: ConflictVersion,
    ) -> "ConflictRecord":
        """Create a new conflict record."""
        return cls(
            id=str(uuid.uuid4()),
            sync_operation_id=sync_operation_id,
            file_path=file_path,
            local_version=local_version,
            remote_version=remote_version,
            created_at=datetime.now(),
        )

    def resolve(self, resolution: ConflictResolution, resolved_by: str) -> None:
        """Mark conflict as resolved."""
        self.resolution = resolution
        self.resolved_by = resolved_by
        self.resolved_at = datetime.now()

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "sync_operation_id": self.sync_operation_id,
            "file_path": self.file_path,
            "local_version": self.local_version.to_dict(),
            "remote_version": self.remote_version.to_dict(),
            "resolution": self.resolution.value if self.resolution else None,
            "resolved_by": self.resolved_by,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ConflictRecord":
        """Create ConflictRecord from dictionary."""
        return cls(
            id=data["id"],
            sync_operation_id=data["sync_operation_id"],
            file_path=data["file_path"],
            local_version=ConflictVersion.from_dict(data["local_version"]),
            remote_version=ConflictVersion.from_dict(data["remote_version"]),
            resolution=ConflictResolution(data["resolution"])
            if data.get("resolution")
            else None,
            resolved_by=data.get("resolved_by"),
            resolved_at=datetime.fromisoformat(data["resolved_at"])
            if data.get("resolved_at") and isinstance(data["resolved_at"], str)
            else None,
            created_at=datetime.fromisoformat(data["created_at"])
            if isinstance(data.get("created_at"), str)
            else datetime.now(),
        )
