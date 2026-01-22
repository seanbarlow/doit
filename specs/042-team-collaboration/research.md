# Research: Team Collaboration Features

**Feature**: 042-team-collaboration
**Date**: 2026-01-22
**Status**: Complete

## Research Questions

### 1. Synchronization Mechanism

**Question**: How should memory files be synchronized between team members?

**Decision**: Use Git as the synchronization mechanism

**Rationale**:
- Git is already required for doit projects (version control of specs, memory)
- Aligns with constitution principle II (Persistent Memory in version-controlled files)
- No external service dependencies - works with any Git provider
- Built-in conflict detection via merge conflicts
- Supports offline work with later sync

**Alternatives Considered**:

| Alternative | Why Rejected |
|-------------|--------------|
| Custom sync service | Requires external infrastructure, violates constitution (no cloud dependencies) |
| Cloud storage (S3, GCS) | External dependency, authentication complexity, cost |
| Real-time sync (Firebase) | Overkill for use case, always-online requirement |
| P2P sync (Syncthing) | Complex setup, unreliable for teams |

### 2. Notification Delivery

**Question**: How should team members be notified of changes?

**Decision**: Local file watching + digest notifications after sync

**Rationale**:
- No external push notification service required
- Works offline (notifications queued until sync)
- Simple implementation using `watchdog` library
- User controls notification frequency via configuration

**Alternatives Considered**:

| Alternative | Why Rejected |
|-------------|--------------|
| Push notifications via service | External dependency, requires server infrastructure |
| Email notifications | Requires email service configuration, may be blocked |
| Slack/Teams integration | Out of scope per spec, external dependency |
| GitHub webhooks | Only works with GitHub, requires public endpoint |

### 3. Conflict Resolution Strategy

**Question**: How should conflicts in memory files be handled?

**Decision**: Three-option resolution: keep local, keep remote, or manual merge

**Rationale**:
- Matches familiar Git conflict resolution patterns
- Gives users clear control over resolution
- Supports both quick resolution and careful merging
- Archives rejected versions for recovery

**Implementation Approach**:
1. Detect conflict via Git merge status
2. Parse both versions of conflicting file
3. Present side-by-side diff with options
4. User selects resolution strategy
5. Apply resolution and commit

### 4. Team Configuration Storage

**Question**: Where should team configuration be stored?

**Decision**: `.doit/config/team.yaml` file

**Rationale**:
- Consistent with existing doit config patterns (hooks.yaml)
- Version-controllable with the project
- Human-readable and editable
- Supports team-level and user-level settings

**Configuration Schema**:
```yaml
team:
  name: "Project Team"
  owner: "user@example.com"

members:
  - id: "user1@example.com"
    role: "owner"
    permission: "read-write"
    notifications: true
  - id: "user2@example.com"
    role: "member"
    permission: "read-only"
    notifications: true

sync:
  auto_sync: false
  sync_on_command: true
  conflict_strategy: "prompt"  # prompt | keep-local | keep-remote

notifications:
  enabled: true
  batch_interval_minutes: 5
  on_sync: true
  on_conflict: true
```

### 5. Access Control Enforcement

**Question**: How should read/write permissions be enforced?

**Decision**: Advisory access control enforced at CLI level

**Rationale**:
- Cannot truly enforce file-system level access (users can edit directly)
- CLI enforcement provides clear feedback on permission violations
- Documented as advisory rather than security boundary
- Sufficient for team coordination use cases

**Implementation**:
- Check permission before push operations
- Reject unauthorized modifications with clear error
- Log permission violations for audit
- Document that direct file edits bypass access control

### 6. Offline Behavior

**Question**: How should the system behave without network connectivity?

**Decision**: Full offline operation with sync queue

**Rationale**:
- Developers often work offline (flights, remote locations)
- Local changes must never be lost
- Sync should be automatic when connectivity returns

**Implementation**:
- All operations work locally first
- Sync operations queued when offline
- Automatic retry when connectivity detected
- Clear UI indication of sync status

## Technology Research

### watchdog Library

**Purpose**: File system monitoring for change notifications

**Key Findings**:
- Cross-platform support (macOS, Linux, Windows)
- Event-based API for efficient monitoring
- Supports recursive directory watching
- Low resource usage for small file sets

**Usage Pattern**:
```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class MemoryChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('.md'):
            self.queue_notification(event.src_path)
```

### Git Programmatic Access

**Purpose**: Sync operations via Git commands

**Key Findings**:
- Use subprocess for Git commands (no Python wrapper needed)
- Check for Git availability before operations
- Parse conflict markers for resolution UI
- Handle authentication via existing Git config

**Commands Used**:
- `git fetch origin` - Get remote changes
- `git merge origin/main --no-commit` - Attempt merge
- `git status --porcelain` - Detect conflicts
- `git checkout --ours/--theirs` - Resolve conflicts
- `git add` / `git commit` / `git push` - Complete sync

## Dependencies

### New Dependencies Required

| Dependency | Version | Purpose | Justification |
|------------|---------|---------|---------------|
| watchdog | >=3.0.0 | File monitoring | Cross-platform, event-based, low overhead |

### Existing Dependencies Used

| Dependency | Purpose in Feature |
|------------|-------------------|
| Typer | CLI command structure |
| Rich | Conflict resolution UI, notifications display |
| PyYAML | Team configuration file parsing |

## Risk Analysis

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Git conflicts too complex for users | Medium | High | Provide clear UI with preview of both versions |
| Notification fatigue | Low | Medium | Batching, configurable frequency, easy disable |
| Performance with large memory files | Low | Low | Warn on files >1MB, reject >10MB |
| Network timeouts during sync | Medium | Low | Retry logic, clear timeout messages |

## Open Questions Resolved

All NEEDS CLARIFICATION items from spec have been resolved:

1. ✅ Sync mechanism: Git-based
2. ✅ Notification delivery: Local file watching + digest
3. ✅ Conflict resolution: Three-option with archive
4. ✅ Configuration storage: team.yaml
5. ✅ Access control: Advisory enforcement at CLI level
6. ✅ Offline behavior: Full offline with sync queue
