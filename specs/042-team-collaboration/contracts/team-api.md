# API Contract: Team Collaboration

**Feature**: 042-team-collaboration
**Date**: 2026-01-22
**Status**: Draft

## CLI Commands

### `doit team init`

Initialize team collaboration for the current project.

**Usage**:
```bash
doit team init [OPTIONS]
```

**Options**:
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--name` | string | Project folder name | Team name |
| `--owner` | string | Git user email | Owner email address |

**Behavior**:
1. Check if `.doit/config/team.yaml` exists (error if already initialized)
2. Get owner email from `--owner` or `git config user.email`
3. Create team configuration with owner as first member
4. Create state files in `.doit/state/`
5. Display success message with next steps

**Output**:
```
✓ Team collaboration initialized
  Team: "My Project Team"
  Owner: alice@example.com

Next steps:
  doit team add <email>     Add a team member
  doit team sync            Sync memory files
```

**Exit Codes**:
| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Already initialized |
| 2 | Git not configured |

---

### `doit team add <email>`

Add a team member to the project.

**Usage**:
```bash
doit team add <email> [OPTIONS]
```

**Arguments**:
| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `email` | string | Yes | Member's email address |

**Options**:
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--role` | choice | member | Role: `owner` or `member` |
| `--permission` | choice | read-write | Access: `read-write` or `read-only` |
| `--no-notify` | flag | false | Don't enable notifications for this member |

**Behavior**:
1. Validate email format
2. Check if member already exists (error if duplicate)
3. Verify current user has owner role
4. Add member to team configuration
5. Commit configuration change

**Output**:
```
✓ Added alice@example.com to team
  Role: member
  Permission: read-write
  Notifications: enabled
```

**Exit Codes**:
| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Invalid email |
| 2 | Member already exists |
| 3 | Permission denied (not owner) |

---

### `doit team remove <email>`

Remove a team member from the project.

**Usage**:
```bash
doit team remove <email> [OPTIONS]
```

**Options**:
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--force` | flag | false | Skip confirmation prompt |

**Behavior**:
1. Verify member exists
2. Verify current user has owner role
3. Prevent removing last owner
4. Prompt for confirmation (unless `--force`)
5. Remove member from configuration
6. Commit configuration change

**Output**:
```
Remove alice@example.com from team? [y/N]: y
✓ Removed alice@example.com from team
```

**Exit Codes**:
| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Member not found |
| 2 | Cannot remove last owner |
| 3 | Permission denied |

---

### `doit team list`

List all team members and their status.

**Usage**:
```bash
doit team list [OPTIONS]
```

**Options**:
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--format` | choice | table | Output format: `table`, `json`, `yaml` |

**Output (table)**:
```
Team: My Project Team
Owner: alice@example.com

Members (3):
┌─────────────────────┬────────┬────────────┬───────────────┬─────────────┐
│ Email               │ Role   │ Permission │ Notifications │ Last Sync   │
├─────────────────────┼────────┼────────────┼───────────────┼─────────────┤
│ alice@example.com   │ owner  │ read-write │ ✓             │ 2 min ago   │
│ bob@example.com     │ member │ read-write │ ✓             │ 1 hour ago  │
│ carol@example.com   │ member │ read-only  │ ✗             │ Never       │
└─────────────────────┴────────┴────────────┴───────────────┴─────────────┘
```

**Exit Codes**:
| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Team not initialized |

---

### `doit team sync`

Synchronize shared memory files with the team.

**Usage**:
```bash
doit team sync [OPTIONS]
```

**Options**:
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--push` | flag | false | Only push local changes |
| `--pull` | flag | false | Only pull remote changes |
| `--force` | flag | false | Overwrite conflicts without prompting |

**Behavior**:
1. Fetch remote changes from origin
2. Compare local and remote memory files
3. If no conflicts: merge automatically
4. If conflicts: prompt for resolution (unless `--force`)
5. Push merged changes to remote
6. Update sync state

**Output (success)**:
```
✓ Synced with team
  ↓ Pulled: 2 files (roadmap.md, constitution.md)
  ↑ Pushed: 1 file (completed_roadmap.md)
  Last sync: just now
```

**Output (conflict)**:
```
⚠ Conflict detected in roadmap.md

Local version (you, 10 minutes ago):
  - Added: Task management feature

Remote version (bob@example.com, 5 minutes ago):
  - Added: API refactoring feature

How would you like to resolve?
  [1] Keep my version
  [2] Keep their version
  [3] Merge manually

Choice [1-3]:
```

**Exit Codes**:
| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Network error |
| 2 | Conflict unresolved |
| 3 | Permission denied |

---

### `doit team status`

Show team sync status and pending notifications.

**Usage**:
```bash
doit team status [OPTIONS]
```

**Options**:
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--verbose` | flag | false | Show detailed sync history |

**Output**:
```
Team: My Project Team

Sync Status:
  Local:  ✓ Up to date
  Remote: 2 changes pending

Shared Files:
┌──────────────────────┬──────────────┬─────────────┐
│ File                 │ Status       │ Modified    │
├──────────────────────┼──────────────┼─────────────┤
│ constitution.md      │ ✓ Synced     │ 2 days ago  │
│ roadmap.md           │ ↓ Behind     │ 1 hour ago  │
│ completed_roadmap.md │ ↑ Ahead      │ 5 min ago   │
└──────────────────────┴──────────────┴─────────────┘

Notifications (2 unread):
  • bob@example.com updated roadmap.md (1 hour ago)
  • carol@example.com joined the team (yesterday)

Run 'doit team sync' to synchronize.
```

**Exit Codes**:
| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Team not initialized |

---

### `doit team notify`

Manage notification settings and view notifications.

**Usage**:
```bash
doit team notify [SUBCOMMAND] [OPTIONS]
```

**Subcommands**:

#### `doit team notify list`
List all notifications.

```bash
doit team notify list [--unread] [--all]
```

#### `doit team notify read [id]`
Mark notification(s) as read.

```bash
doit team notify read           # Mark all as read
doit team notify read <id>      # Mark specific as read
```

#### `doit team notify config`
Configure notification settings.

```bash
doit team notify config [OPTIONS]
  --enable              Enable notifications
  --disable             Disable notifications
  --interval <minutes>  Set batch interval (default: 5)
```

**Output (list)**:
```
Notifications (3 total, 2 unread):

[1] 🔴 bob@example.com updated roadmap.md
    1 hour ago • memory_changed

[2] 🔴 Conflict detected in constitution.md
    30 minutes ago • conflict_detected

[3] ⚪ carol@example.com joined the team
    yesterday • member_joined
```

---

### `doit team config`

View or update team configuration.

**Usage**:
```bash
doit team config [KEY] [VALUE]
```

**Examples**:
```bash
doit team config                           # Show all config
doit team config sync.auto_sync            # Show specific setting
doit team config sync.auto_sync true       # Set specific setting
```

**Configurable Settings**:
| Key | Type | Description |
|-----|------|-------------|
| `team.name` | string | Team display name |
| `sync.auto_sync` | bool | Auto-sync on file changes |
| `sync.sync_on_command` | bool | Sync before/after commands |
| `sync.conflict_strategy` | string | Default conflict resolution |
| `notifications.enabled` | bool | Enable/disable notifications |
| `notifications.batch_interval_minutes` | int | Notification batching interval |

---

## Service Interfaces

### TeamService

Core service for team management operations.

```python
class TeamService:
    """Manages team configuration and membership."""

    def __init__(self, config_path: Path = None):
        """Initialize with config path (defaults to .doit/config/team.yaml)."""
        ...

    def init_team(self, name: str, owner_email: str) -> Team:
        """Initialize team collaboration for the project."""
        ...

    def get_team(self) -> Team:
        """Get current team configuration."""
        ...

    def add_member(
        self,
        email: str,
        role: str = "member",
        permission: str = "read-write",
        notifications: bool = True
    ) -> TeamMember:
        """Add a member to the team."""
        ...

    def remove_member(self, email: str) -> None:
        """Remove a member from the team."""
        ...

    def update_member(self, email: str, **kwargs) -> TeamMember:
        """Update member settings."""
        ...

    def list_members(self) -> list[TeamMember]:
        """List all team members."""
        ...

    def get_current_user(self) -> TeamMember:
        """Get the current user's membership."""
        ...

    def check_permission(self, email: str, action: str) -> bool:
        """Check if member has permission for action."""
        ...
```

---

### SyncService

Handles synchronization of shared memory files.

```python
class SyncService:
    """Manages memory file synchronization via Git."""

    def __init__(self, team_service: TeamService):
        """Initialize with team service."""
        ...

    def sync(
        self,
        push_only: bool = False,
        pull_only: bool = False,
        force: bool = False
    ) -> SyncResult:
        """Synchronize shared memory with remote."""
        ...

    def get_status(self) -> SyncStatus:
        """Get current sync status."""
        ...

    def get_pending_changes(self) -> list[FileChange]:
        """Get list of pending local/remote changes."""
        ...

    def detect_conflicts(self) -> list[ConflictRecord]:
        """Detect conflicts between local and remote."""
        ...

    def resolve_conflict(
        self,
        conflict: ConflictRecord,
        resolution: str  # keep_local | keep_remote | manual_merge
    ) -> None:
        """Resolve a detected conflict."""
        ...

    def get_sync_history(self, limit: int = 10) -> list[SyncOperation]:
        """Get recent sync operations."""
        ...
```

**SyncResult**:
```python
@dataclass
class SyncResult:
    success: bool
    pulled_files: list[str]
    pushed_files: list[str]
    conflicts: list[ConflictRecord]
    error_message: Optional[str]
```

**SyncStatus**:
```python
@dataclass
class SyncStatus:
    local_ahead: int      # Files with local changes
    local_behind: int     # Files with remote changes
    last_sync: Optional[datetime]
    is_online: bool
```

---

### NotificationService

Manages notifications for team changes.

```python
class NotificationService:
    """Manages team change notifications."""

    def __init__(self, state_path: Path = None):
        """Initialize with state path (defaults to .doit/state/)."""
        ...

    def create_notification(
        self,
        type: str,
        title: str,
        content: str,
        source_member: str,
        affected_files: list[str] = None
    ) -> Notification:
        """Create a new notification."""
        ...

    def get_notifications(
        self,
        unread_only: bool = False,
        limit: int = 50
    ) -> list[Notification]:
        """Get notifications for current user."""
        ...

    def mark_read(self, notification_id: str = None) -> None:
        """Mark notification(s) as read. If no ID, marks all."""
        ...

    def get_settings(self) -> NotificationSettings:
        """Get notification settings."""
        ...

    def update_settings(self, **kwargs) -> None:
        """Update notification settings."""
        ...

    def process_batch(self) -> None:
        """Process and display batched notifications."""
        ...
```

---

### FileWatcherService

Monitors memory files for changes (optional background service).

```python
class FileWatcherService:
    """Watches memory files for changes using watchdog."""

    def __init__(
        self,
        memory_path: Path,
        notification_service: NotificationService
    ):
        """Initialize file watcher."""
        ...

    def start(self) -> None:
        """Start watching for file changes."""
        ...

    def stop(self) -> None:
        """Stop watching for file changes."""
        ...

    def on_file_changed(self, path: Path) -> None:
        """Handle file change event."""
        ...
```

---

## Error Handling

### Error Types

```python
class TeamError(Exception):
    """Base exception for team operations."""
    pass

class TeamNotInitializedError(TeamError):
    """Team collaboration not initialized."""
    pass

class MemberNotFoundError(TeamError):
    """Team member not found."""
    pass

class PermissionDeniedError(TeamError):
    """User lacks permission for operation."""
    pass

class SyncConflictError(TeamError):
    """Sync conflict requires resolution."""
    conflicts: list[ConflictRecord]

class NetworkError(TeamError):
    """Network operation failed."""
    pass
```

### Error Messages

| Error | CLI Message |
|-------|-------------|
| `TeamNotInitializedError` | "Team collaboration not initialized. Run 'doit team init' first." |
| `MemberNotFoundError` | "Member '{email}' not found in team." |
| `PermissionDeniedError` | "Permission denied. This action requires owner role." |
| `SyncConflictError` | "Sync conflict detected. Run 'doit team sync' to resolve." |
| `NetworkError` | "Network error: {details}. Changes saved locally." |

---

## Integration Points

### With Existing Commands

| Command | Integration |
|---------|-------------|
| `doit init` | Optionally initialize team collaboration |
| `doit specit` | Sync before reading context |
| `doit checkin` | Sync after committing changes |
| `doit roadmapit` | Sync roadmap before/after updates |

### With Git Hooks

Team sync can be integrated with existing git hooks:

```yaml
# .doit/config/hooks.yaml
hooks:
  post-commit:
    - name: team-sync
      command: doit team sync --push
      enabled: true
  pre-push:
    - name: team-sync-check
      command: doit team status --check
      enabled: true
```
