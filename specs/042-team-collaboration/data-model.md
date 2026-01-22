# Data Model: Team Collaboration Features

**Feature**: 042-team-collaboration
**Date**: 2026-01-22
**Status**: Draft

## Overview

This document defines the data structures for the team collaboration feature. All data is stored in file-based formats (YAML, JSON, Markdown) to align with the constitution's principle of persistent memory in version-controlled files.

## Storage Locations

| Data Type | Location | Format | Git Tracked |
|-----------|----------|--------|-------------|
| Team Configuration | `.doit/config/team.yaml` | YAML | Yes |
| Sync State | `.doit/state/team-sync.json` | JSON | No (local) |
| Notification Queue | `.doit/state/notifications.json` | JSON | No (local) |
| Conflict Archive | `.doit/state/conflicts/` | Markdown | No (local) |
| Shared Memory | `.doit/memory/` | Markdown | Yes |

## Entity Definitions

### Team

Represents a collaborative team working on a doit project.

```yaml
# .doit/config/team.yaml
team:
  id: string          # Unique identifier (auto-generated UUID)
  name: string        # Human-readable team name
  owner_id: string    # Email of team owner
  created_at: string  # ISO 8601 timestamp
  updated_at: string  # ISO 8601 timestamp
```

**Python Model**:
```python
@dataclass
class Team:
    id: str
    name: str
    owner_id: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_yaml(cls, data: dict) -> "Team":
        """Load team from YAML configuration."""
        ...
```

**Constraints**:
- `id` must be unique across all teams (UUID v4)
- `owner_id` must be a valid email format
- `name` must be 1-100 characters

---

### TeamMember

A developer with access to the shared project memory.

```yaml
# Part of .doit/config/team.yaml
members:
  - id: string              # Email address (unique identifier)
    display_name: string    # Optional display name
    role: string           # "owner" | "member"
    permission: string     # "read-write" | "read-only"
    notifications: boolean # Whether to receive notifications
    added_at: string       # ISO 8601 timestamp
    added_by: string       # Email of user who added this member
```

**Python Model**:
```python
@dataclass
class TeamMember:
    id: str  # Email
    display_name: Optional[str]
    role: Literal["owner", "member"]
    permission: Literal["read-write", "read-only"]
    notifications: bool
    added_at: datetime
    added_by: str
    last_sync: Optional[datetime] = None  # Tracked locally
```

**Constraints**:
- `id` must be unique within the team
- `role` must be "owner" or "member"
- `permission` must be "read-write" or "read-only"
- At least one member must have role "owner"

---

### SharedMemory

Tracks synchronized memory files between team members.

```yaml
# Part of .doit/config/team.yaml
shared_files:
  - path: string          # Relative path from .doit/memory/
    version: string       # Git commit hash of last sync
    modified_by: string   # Email of last modifier
    modified_at: string   # ISO 8601 timestamp
    size_bytes: integer   # File size for quota checking
```

**Python Model**:
```python
@dataclass
class SharedMemory:
    path: str  # e.g., "constitution.md", "roadmap.md"
    version: str  # Git commit SHA
    modified_by: str
    modified_at: datetime
    size_bytes: int

    @property
    def full_path(self) -> Path:
        return Path(".doit/memory") / self.path
```

**Default Shared Files**:
- `constitution.md` - Project principles and guidelines
- `roadmap.md` - Active development priorities
- `completed_roadmap.md` - Historical completed items

**Constraints**:
- `path` must be relative (no leading `/`)
- `size_bytes` must not exceed 10MB (10,485,760 bytes)
- Warning issued for files > 1MB

---

### SyncOperation

Records individual sync attempts for audit and debugging.

```json
// .doit/state/team-sync.json
{
  "operations": [
    {
      "id": "uuid",
      "member_id": "user@example.com",
      "operation_type": "push|pull|merge",
      "status": "success|conflict|error",
      "files_affected": ["constitution.md"],
      "started_at": "2026-01-22T10:30:00Z",
      "completed_at": "2026-01-22T10:30:05Z",
      "error_message": null,
      "conflict_id": null
    }
  ],
  "last_sync": "2026-01-22T10:30:05Z",
  "pending_operations": []
}
```

**Python Model**:
```python
@dataclass
class SyncOperation:
    id: str
    member_id: str
    operation_type: Literal["push", "pull", "merge"]
    status: Literal["pending", "in_progress", "success", "conflict", "error"]
    files_affected: list[str]
    started_at: datetime
    completed_at: Optional[datetime]
    error_message: Optional[str]
    conflict_id: Optional[str]
```

**Retention Policy**:
- Keep last 100 operations
- Auto-purge operations older than 30 days
- Always keep operations with status "error" or "conflict"

---

### Notification

Alerts about changes to shared memory files.

```json
// .doit/state/notifications.json
{
  "notifications": [
    {
      "id": "uuid",
      "type": "memory_changed|conflict_detected|member_joined|permission_changed",
      "title": "Roadmap updated",
      "content": "alice@example.com modified roadmap.md",
      "source_member": "alice@example.com",
      "affected_files": ["roadmap.md"],
      "read": false,
      "created_at": "2026-01-22T10:30:00Z",
      "expires_at": "2026-01-29T10:30:00Z"
    }
  ],
  "settings": {
    "enabled": true,
    "batch_interval_minutes": 5,
    "last_batch_sent": "2026-01-22T10:25:00Z"
  }
}
```

**Python Model**:
```python
@dataclass
class Notification:
    id: str
    type: Literal["memory_changed", "conflict_detected", "member_joined", "permission_changed"]
    title: str
    content: str
    source_member: str
    affected_files: list[str]
    read: bool
    created_at: datetime
    expires_at: datetime

    def is_expired(self) -> bool:
        return datetime.now() > self.expires_at
```

**Notification Types**:
| Type | Trigger | Priority |
|------|---------|----------|
| `memory_changed` | Team member pushes changes | Normal |
| `conflict_detected` | Sync detects conflicting changes | High |
| `member_joined` | New member added to team | Low |
| `permission_changed` | Member's access level changed | Normal |

**Batching Rules**:
- Notifications are batched per `batch_interval_minutes` (default: 5)
- High priority notifications bypass batching
- Maximum 10 notifications per batch

---

### ConflictRecord

Archives conflict details for resolution and recovery.

```json
// .doit/state/conflicts/{conflict_id}.json
{
  "id": "uuid",
  "sync_operation_id": "uuid",
  "file_path": "roadmap.md",
  "local_version": {
    "content": "...",
    "modified_by": "alice@example.com",
    "modified_at": "2026-01-22T10:00:00Z",
    "git_commit": "abc123"
  },
  "remote_version": {
    "content": "...",
    "modified_by": "bob@example.com",
    "modified_at": "2026-01-22T10:05:00Z",
    "git_commit": "def456"
  },
  "resolution": null,
  "resolved_by": null,
  "resolved_at": null,
  "created_at": "2026-01-22T10:30:00Z"
}
```

**Python Model**:
```python
@dataclass
class ConflictVersion:
    content: str
    modified_by: str
    modified_at: datetime
    git_commit: str

@dataclass
class ConflictRecord:
    id: str
    sync_operation_id: str
    file_path: str
    local_version: ConflictVersion
    remote_version: ConflictVersion
    resolution: Optional[Literal["keep_local", "keep_remote", "manual_merge"]]
    resolved_by: Optional[str]
    resolved_at: Optional[datetime]
    created_at: datetime

    def archive_rejected_version(self) -> Path:
        """Archive the rejected version to conflicts/ directory."""
        ...
```

**Resolution Options**:
| Resolution | Action | Archive |
|------------|--------|---------|
| `keep_local` | Use local version, discard remote | Remote archived |
| `keep_remote` | Use remote version, discard local | Local archived |
| `manual_merge` | User edits combined result | Both archived |

---

## Complete Configuration Schema

```yaml
# .doit/config/team.yaml - Full Schema

# Team metadata
team:
  id: "550e8400-e29b-41d4-a716-446655440000"
  name: "Project Team"
  owner_id: "owner@example.com"
  created_at: "2026-01-22T10:00:00Z"
  updated_at: "2026-01-22T10:00:00Z"

# Team members
members:
  - id: "owner@example.com"
    display_name: "Alice Owner"
    role: "owner"
    permission: "read-write"
    notifications: true
    added_at: "2026-01-22T10:00:00Z"
    added_by: "owner@example.com"
  - id: "member@example.com"
    display_name: "Bob Member"
    role: "member"
    permission: "read-only"
    notifications: true
    added_at: "2026-01-22T11:00:00Z"
    added_by: "owner@example.com"

# Files to synchronize
shared_files:
  - path: "constitution.md"
    version: "abc123def"
    modified_by: "owner@example.com"
    modified_at: "2026-01-22T10:00:00Z"
    size_bytes: 4096
  - path: "roadmap.md"
    version: "abc123def"
    modified_by: "owner@example.com"
    modified_at: "2026-01-22T10:00:00Z"
    size_bytes: 8192
  - path: "completed_roadmap.md"
    version: "abc123def"
    modified_by: "owner@example.com"
    modified_at: "2026-01-22T10:00:00Z"
    size_bytes: 16384

# Sync settings
sync:
  auto_sync: false              # Automatically sync on file changes
  sync_on_command: true         # Sync before/after doit commands
  conflict_strategy: "prompt"   # prompt | keep-local | keep-remote

# Notification settings
notifications:
  enabled: true
  batch_interval_minutes: 5
  on_sync: true
  on_conflict: true
  on_member_change: false
```

## Validation Rules

### Team Configuration Validation

| Field | Rule | Error Message |
|-------|------|---------------|
| `team.name` | 1-100 characters | "Team name must be 1-100 characters" |
| `team.owner_id` | Valid email format | "Invalid email format for team owner" |
| `members` | At least 1 member | "Team must have at least one member" |
| `members[].id` | Valid email format | "Invalid email format for member" |
| `members[].role` | One must be "owner" | "Team must have at least one owner" |
| `shared_files[].size_bytes` | <= 10MB | "File {path} exceeds maximum size (10MB)" |

### State File Validation

| File | Rule | Recovery Action |
|------|------|-----------------|
| `team-sync.json` | Valid JSON | Create empty state |
| `notifications.json` | Valid JSON | Create empty queue |
| `conflicts/*.json` | Valid JSON | Log warning, skip file |

## Migration Notes

### Initial Setup Migration

When `doit team init` is run:
1. Create `.doit/config/team.yaml` with current user as owner
2. Create `.doit/state/team-sync.json` with empty operations
3. Create `.doit/state/notifications.json` with default settings
4. Add `.doit/state/` to `.gitignore` (if not present)

### Version Compatibility

| Config Version | Changes | Migration |
|----------------|---------|-----------|
| 1.0 | Initial schema | N/A |
