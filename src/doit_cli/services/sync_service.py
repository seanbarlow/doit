"""Memory synchronization service.

This module provides the SyncService class for synchronizing
shared memory files between team members via Git.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional
import uuid

from doit_cli.models.team_models import (
    SharedMemory,
    SyncOperationType,
    SyncStatus,
)
from doit_cli.services.git_utils import (
    GitConflictError,
    GitError,
    add,
    commit,
    fetch,
    get_conflicting_files,
    get_current_branch,
    get_file_last_modified_by,
    get_latest_commit_hash,
    get_status,
    has_remote,
    is_online,
    pull,
    push,
)
from doit_cli.services.team_service import TeamService
from doit_cli.services.access_service import AccessService, AccessAction, AccessDeniedError


class SyncError(Exception):
    """Base exception for sync operations."""

    pass


class NetworkError(SyncError):
    """Network operation failed."""

    pass


class NoRemoteError(SyncError):
    """No Git remote configured."""

    pass


@dataclass
class FileChange:
    """Represents a change to a shared file."""

    path: str
    status: str  # "modified", "added", "deleted", "unchanged"
    local_modified: bool = False
    remote_modified: bool = False


@dataclass
class SyncOperation:
    """Records a sync attempt for audit."""

    id: str
    member_id: str
    operation_type: SyncOperationType
    status: SyncStatus
    files_affected: list[str] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    conflict_id: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "member_id": self.member_id,
            "operation_type": self.operation_type.value,
            "status": self.status.value,
            "files_affected": self.files_affected,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error_message": self.error_message,
            "conflict_id": self.conflict_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SyncOperation":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            member_id=data["member_id"],
            operation_type=SyncOperationType(data["operation_type"]),
            status=SyncStatus(data["status"]),
            files_affected=data.get("files_affected", []),
            started_at=datetime.fromisoformat(data["started_at"]),
            completed_at=datetime.fromisoformat(data["completed_at"])
            if data.get("completed_at")
            else None,
            error_message=data.get("error_message"),
            conflict_id=data.get("conflict_id"),
        )


@dataclass
class SyncResult:
    """Result of a sync operation."""

    success: bool
    pulled_files: list[str] = field(default_factory=list)
    pushed_files: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    error_message: Optional[str] = None
    operation_id: Optional[str] = None


@dataclass
class SyncState:
    """Current sync state from team-sync.json."""

    operations: list[SyncOperation] = field(default_factory=list)
    last_sync: Optional[datetime] = None
    pending_operations: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "operations": [op.to_dict() for op in self.operations[-100:]],  # Keep last 100
            "last_sync": self.last_sync.isoformat() if self.last_sync else None,
            "pending_operations": self.pending_operations,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SyncState":
        """Create from dictionary."""
        return cls(
            operations=[SyncOperation.from_dict(op) for op in data.get("operations", [])],
            last_sync=datetime.fromisoformat(data["last_sync"])
            if data.get("last_sync")
            else None,
            pending_operations=data.get("pending_operations", []),
        )


class SyncService:
    """Manages memory file synchronization via Git.

    This service provides methods for:
    - Syncing shared memory files with remote
    - Detecting conflicts
    - Managing sync state
    """

    def __init__(self, team_service: TeamService, project_root: Path = None):
        """Initialize SyncService.

        Args:
            team_service: TeamService instance
            project_root: Project root directory. Defaults to cwd.
        """
        self.team_service = team_service
        self.project_root = project_root or Path.cwd()
        self._state: Optional[SyncState] = None
        self._access_service = AccessService(self.project_root)

    @property
    def state_path(self) -> Path:
        """Get path to sync state file."""
        return self.project_root / ".doit" / "state" / "team-sync.json"

    @property
    def memory_path(self) -> Path:
        """Get path to memory directory."""
        return self.project_root / ".doit" / "memory"

    def _load_state(self) -> SyncState:
        """Load sync state from file."""
        if self.state_path.exists():
            try:
                with open(self.state_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return SyncState.from_dict(data)
            except (json.JSONDecodeError, KeyError):
                pass
        return SyncState()

    def _save_state(self, state: SyncState) -> None:
        """Save sync state to file."""
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_path, "w", encoding="utf-8") as f:
            json.dump(state.to_dict(), f, indent=2)

    def get_state(self) -> SyncState:
        """Get current sync state."""
        if self._state is None:
            self._state = self._load_state()
        return self._state

    def _record_operation(
        self,
        operation_type: SyncOperationType,
        status: SyncStatus,
        files_affected: list[str] = None,
        error_message: str = None,
        conflict_id: str = None,
    ) -> SyncOperation:
        """Record a sync operation."""
        current_user = self.team_service.get_current_user_email() or "unknown"

        operation = SyncOperation(
            id=str(uuid.uuid4()),
            member_id=current_user,
            operation_type=operation_type,
            status=status,
            files_affected=files_affected or [],
            started_at=datetime.now(),
            completed_at=datetime.now() if status != SyncStatus.IN_PROGRESS else None,
            error_message=error_message,
            conflict_id=conflict_id,
        )

        state = self.get_state()
        state.operations.append(operation)
        if status == SyncStatus.SUCCESS:
            state.last_sync = datetime.now()
        self._save_state(state)

        return operation

    def check_remote(self) -> bool:
        """Check if remote is configured and reachable.

        Returns:
            True if remote is available
        """
        if not has_remote(cwd=self.project_root):
            return False
        return is_online(cwd=self.project_root)

    def get_status(self) -> dict:
        """Get current sync status.

        Returns:
            Dictionary with sync status information
        """
        git_status = get_status(self.project_root)
        state = self.get_state()
        shared_files = self.team_service.get_shared_files()

        # Check each shared file status
        file_statuses = []
        for sf in shared_files:
            file_path = self.memory_path / sf.path
            status = "unknown"

            if not file_path.exists():
                status = "missing"
            elif sf.path in git_status.modified_files:
                status = "modified"
            elif git_status.ahead > 0:
                status = "ahead"
            elif git_status.behind > 0:
                status = "behind"
            else:
                status = "synced"

            file_statuses.append({
                "path": sf.path,
                "status": status,
                "modified_by": sf.modified_by,
                "modified_at": sf.modified_at,
            })

        return {
            "is_online": self.check_remote(),
            "last_sync": state.last_sync,
            "local_ahead": git_status.ahead,
            "local_behind": git_status.behind,
            "is_clean": git_status.is_clean,
            "current_branch": git_status.current_branch,
            "has_remote": git_status.has_remote,
            "files": file_statuses,
        }

    def get_pending_changes(self) -> list[FileChange]:
        """Get list of pending local/remote changes.

        Returns:
            List of FileChange objects
        """
        git_status = get_status(self.project_root)
        shared_files = self.team_service.get_shared_files()
        shared_paths = {sf.path for sf in shared_files}

        changes = []

        # Check modified files
        for modified in git_status.modified_files:
            # Check if it's a shared memory file
            if modified.startswith(".doit/memory/"):
                rel_path = modified.replace(".doit/memory/", "")
                if rel_path in shared_paths:
                    changes.append(FileChange(
                        path=rel_path,
                        status="modified",
                        local_modified=True,
                    ))

        # Check staged files
        for staged in git_status.staged_files:
            if staged.startswith(".doit/memory/"):
                rel_path = staged.replace(".doit/memory/", "")
                if rel_path in shared_paths:
                    # Don't duplicate if already in changes
                    existing = next((c for c in changes if c.path == rel_path), None)
                    if not existing:
                        changes.append(FileChange(
                            path=rel_path,
                            status="staged",
                            local_modified=True,
                        ))

        return changes

    def sync(
        self,
        push_only: bool = False,
        pull_only: bool = False,
        force: bool = False,
    ) -> SyncResult:
        """Synchronize shared memory with remote.

        Args:
            push_only: Only push local changes
            pull_only: Only pull remote changes
            force: Overwrite conflicts without prompting

        Returns:
            SyncResult with operation details

        Raises:
            NoRemoteError: If no remote is configured
            NetworkError: If network is unavailable
            GitConflictError: If conflicts detected (unless force=True)
            AccessDeniedError: If user lacks push permission (for push operations)
        """
        # T024: Check push permission if doing push
        if not pull_only:
            if not self._access_service.can_perform(AccessAction.PUSH):
                raise AccessDeniedError(
                    action="push",
                    required_permission="write",
                    message="You have read-only access. Contact the team owner to enable push permissions.",
                )

        if not has_remote(cwd=self.project_root):
            raise NoRemoteError("No Git remote configured. Push your repository first.")

        if not is_online(cwd=self.project_root):
            raise NetworkError(
                "Cannot reach remote repository. Check your network connection."
            )

        result = SyncResult(success=False)
        shared_files = self.team_service.get_shared_files()
        memory_files = [f".doit/memory/{sf.path}" for sf in shared_files]

        try:
            # Pull first (unless push_only)
            if not push_only:
                try:
                    fetch(cwd=self.project_root)
                    pull_result = pull(cwd=self.project_root)

                    # Check which shared files were updated
                    for sf in shared_files:
                        result.pulled_files.append(sf.path)

                except GitConflictError as e:
                    if force:
                        # Force keep local on conflict
                        from doit_cli.services.git_utils import checkout_ours
                        for conflict_file in e.conflicting_files:
                            checkout_ours([conflict_file], self.project_root)
                            add([conflict_file], self.project_root)
                        commit("Resolved conflicts by keeping local versions", self.project_root)
                    else:
                        result.conflicts = e.conflicting_files
                        self._record_operation(
                            SyncOperationType.PULL,
                            SyncStatus.CONFLICT,
                            files_affected=e.conflicting_files,
                        )
                        return result

            # Push changes (unless pull_only)
            if not pull_only:
                git_status = get_status(self.project_root)

                # Stage memory files that have changes
                files_to_stage = []
                for memory_file in memory_files:
                    rel_path = memory_file
                    if rel_path in git_status.modified_files or rel_path in git_status.untracked_files:
                        files_to_stage.append(rel_path)

                if files_to_stage:
                    add(files_to_stage, self.project_root)
                    commit("Update shared memory files", self.project_root)
                    push(cwd=self.project_root)

                    for f in files_to_stage:
                        rel_path = f.replace(".doit/memory/", "")
                        result.pushed_files.append(rel_path)

            result.success = True
            operation = self._record_operation(
                SyncOperationType.MERGE,
                SyncStatus.SUCCESS,
                files_affected=result.pulled_files + result.pushed_files,
            )
            result.operation_id = operation.id

            # Update shared file metadata
            self._update_shared_file_metadata()

        except GitError as e:
            result.error_message = str(e)
            self._record_operation(
                SyncOperationType.MERGE,
                SyncStatus.ERROR,
                error_message=str(e),
            )

        return result

    def _update_shared_file_metadata(self) -> None:
        """Update shared file metadata after sync."""
        current_user = self.team_service.get_current_user_email() or ""
        current_commit = get_latest_commit_hash(cwd=self.project_root) or ""

        for sf in self.team_service.config.shared_files:
            file_path = self.memory_path / sf.path
            if file_path.exists():
                sf.version = current_commit
                sf.modified_at = datetime.now()
                sf.size_bytes = file_path.stat().st_size

                # Get last modifier
                modifier = get_file_last_modified_by(
                    str(sf.full_path), self.project_root
                )
                if modifier:
                    sf.modified_by = modifier

        self.team_service._save_config()

    def get_sync_history(self, limit: int = 10) -> list[SyncOperation]:
        """Get recent sync operations.

        Args:
            limit: Maximum number of operations to return

        Returns:
            List of recent SyncOperation objects
        """
        state = self.get_state()
        return state.operations[-limit:]

    def queue_offline_operation(self, operation_type: str, files: list[str]) -> None:
        """Queue an operation for when connectivity returns.

        Args:
            operation_type: Type of operation ("push", "pull")
            files: List of affected files
        """
        state = self.get_state()
        state.pending_operations.append({
            "type": operation_type,
            "files": files,
            "queued_at": datetime.now().isoformat(),
        })
        self._save_state(state)

    def process_pending_operations(self) -> list[SyncResult]:
        """Process any queued offline operations.

        Returns:
            List of SyncResult for each processed operation
        """
        results = []
        state = self.get_state()

        for pending in state.pending_operations:
            op_type = pending.get("type")
            if op_type == "push":
                result = self.sync(push_only=True)
            elif op_type == "pull":
                result = self.sync(pull_only=True)
            else:
                result = self.sync()
            results.append(result)

        # Clear processed operations
        state.pending_operations = []
        self._save_state(state)

        return results
