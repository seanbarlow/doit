"""Conflict detection and resolution service.

This module provides the ConflictService class for detecting,
resolving, and archiving merge conflicts in shared memory files.
"""

import json
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional
import uuid

from doit_cli.models.team_models import (
    ConflictRecord,
    ConflictResolution,
    ConflictVersion,
)
from doit_cli.services.git_utils import (
    checkout_ours,
    checkout_theirs,
    get_conflicting_files,
    get_latest_commit_hash,
    run_git_command,
)


class ConflictError(Exception):
    """Base exception for conflict operations."""

    pass


class ConflictNotFoundError(ConflictError):
    """Conflict record not found."""

    pass


@dataclass
class ConflictState:
    """State of active conflicts."""

    active_conflicts: list[ConflictRecord] = field(default_factory=list)
    resolved_count: int = 0

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "active_conflicts": [c.to_dict() for c in self.active_conflicts],
            "resolved_count": self.resolved_count,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ConflictState":
        """Create from dictionary."""
        return cls(
            active_conflicts=[
                ConflictRecord.from_dict(c) for c in data.get("active_conflicts", [])
            ],
            resolved_count=data.get("resolved_count", 0),
        )


class ConflictService:
    """Manages conflict detection and resolution.

    This service provides methods for:
    - Detecting conflicts during sync
    - Resolving conflicts with different strategies
    - Archiving conflict records for audit
    - Managing conflict state
    """

    def __init__(self, project_root: Path = None):
        """Initialize ConflictService.

        Args:
            project_root: Project root directory. Defaults to cwd.
        """
        self.project_root = project_root or Path.cwd()
        self._state: Optional[ConflictState] = None

    @property
    def state_path(self) -> Path:
        """Get path to conflict state file."""
        return self.project_root / ".doit" / "state" / "conflicts.json"

    @property
    def archive_dir(self) -> Path:
        """Get path to conflict archive directory."""
        return self.project_root / ".doit" / "state" / "conflicts"

    @property
    def memory_path(self) -> Path:
        """Get path to memory directory."""
        return self.project_root / ".doit" / "memory"

    def _load_state(self) -> ConflictState:
        """Load conflict state from file."""
        if self.state_path.exists():
            try:
                with open(self.state_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return ConflictState.from_dict(data)
            except (json.JSONDecodeError, KeyError):
                pass
        return ConflictState()

    def _save_state(self, state: ConflictState) -> None:
        """Save conflict state to file."""
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_path, "w", encoding="utf-8") as f:
            json.dump(state.to_dict(), f, indent=2)

    def get_state(self) -> ConflictState:
        """Get current conflict state."""
        if self._state is None:
            self._state = self._load_state()
        return self._state

    def detect_conflicts(self, sync_operation_id: str = None) -> list[ConflictRecord]:
        """Detect conflicts in working directory.

        Args:
            sync_operation_id: ID of current sync operation (for tracking)

        Returns:
            List of ConflictRecord objects for detected conflicts
        """
        conflicts = []
        op_id = sync_operation_id or str(uuid.uuid4())

        # Get list of conflicting files from Git
        try:
            conflicting_files = get_conflicting_files(self.project_root)
        except Exception:
            conflicting_files = []

        for conflict_path in conflicting_files:
            # Only track conflicts in memory directory
            if not conflict_path.startswith(".doit/memory/"):
                continue

            rel_path = conflict_path.replace(".doit/memory/", "")

            try:
                # Get local version (ours)
                local_content = self._get_version_content(conflict_path, "ours")
                local_version = ConflictVersion(
                    content=local_content,
                    modified_by=self._get_current_user(),
                    modified_at=datetime.now(),
                    git_commit=get_latest_commit_hash(cwd=self.project_root) or "",
                )

                # Get remote version (theirs)
                remote_content = self._get_version_content(conflict_path, "theirs")
                remote_version = ConflictVersion(
                    content=remote_content,
                    modified_by="remote",  # Will be updated if we can get the info
                    modified_at=datetime.now(),
                    git_commit="",
                )

                # Create conflict record
                conflict = ConflictRecord.create(
                    sync_operation_id=op_id,
                    file_path=rel_path,
                    local_version=local_version,
                    remote_version=remote_version,
                )
                conflicts.append(conflict)

            except Exception:
                # If we can't read the conflict, skip it
                continue

        # Store conflicts in state
        if conflicts:
            state = self.get_state()
            state.active_conflicts.extend(conflicts)
            self._save_state(state)
            self._state = state

        return conflicts

    def _get_version_content(self, file_path: str, version: str) -> str:
        """Get content of a specific version during merge conflict.

        Args:
            file_path: Path to conflicting file
            version: "ours" for local, "theirs" for remote

        Returns:
            Content of the specified version
        """
        try:
            if version == "ours":
                result = run_git_command(
                    ["show", f":2:{file_path}"],
                    cwd=self.project_root,
                )
            else:
                result = run_git_command(
                    ["show", f":3:{file_path}"],
                    cwd=self.project_root,
                )
            return result.stdout
        except Exception:
            # Fall back to reading file with conflict markers
            full_path = self.project_root / file_path
            if full_path.exists():
                return full_path.read_text(encoding="utf-8")
            return ""

    def _get_current_user(self) -> str:
        """Get current user email from Git config."""
        try:
            result = run_git_command(
                ["config", "user.email"],
                cwd=self.project_root,
            )
            return result.stdout.strip()
        except Exception:
            return "unknown"

    def get_active_conflicts(self) -> list[ConflictRecord]:
        """Get list of unresolved conflicts.

        Returns:
            List of active ConflictRecord objects
        """
        state = self.get_state()
        return [c for c in state.active_conflicts if c.resolution is None]

    def get_conflict(self, conflict_id: str) -> Optional[ConflictRecord]:
        """Get a specific conflict by ID.

        Args:
            conflict_id: Conflict ID

        Returns:
            ConflictRecord or None if not found
        """
        state = self.get_state()
        for conflict in state.active_conflicts:
            if conflict.id == conflict_id:
                return conflict
        return None

    def resolve_conflict(
        self,
        conflict_id: str,
        resolution: ConflictResolution,
        resolved_by: str = None,
    ) -> ConflictRecord:
        """Resolve a conflict.

        Args:
            conflict_id: ID of conflict to resolve
            resolution: Resolution strategy to use
            resolved_by: Email of person resolving (defaults to current user)

        Returns:
            Updated ConflictRecord

        Raises:
            ConflictNotFoundError: If conflict not found
        """
        conflict = self.get_conflict(conflict_id)
        if not conflict:
            raise ConflictNotFoundError(f"Conflict not found: {conflict_id}")

        resolver = resolved_by or self._get_current_user()
        full_path = self.memory_path / conflict.file_path
        git_path = f".doit/memory/{conflict.file_path}"

        try:
            if resolution == ConflictResolution.KEEP_LOCAL:
                # Keep local version
                checkout_ours([git_path], self.project_root)
                full_path.write_text(
                    conflict.local_version.content, encoding="utf-8"
                )

            elif resolution == ConflictResolution.KEEP_REMOTE:
                # Keep remote version
                checkout_theirs([git_path], self.project_root)
                full_path.write_text(
                    conflict.remote_version.content, encoding="utf-8"
                )

            elif resolution == ConflictResolution.MANUAL_MERGE:
                # User will manually edit the file
                # Just mark as resolved, don't change content
                pass

            # Mark conflict as resolved
            conflict.resolve(resolution, resolver)

            # Update state
            state = self.get_state()
            state.resolved_count += 1
            self._save_state(state)
            self._state = state

            # Archive the conflict
            self._archive_conflict(conflict)

        except Exception as e:
            raise ConflictError(f"Failed to resolve conflict: {e}")

        return conflict

    def resolve_all(
        self,
        resolution: ConflictResolution,
        resolved_by: str = None,
    ) -> list[ConflictRecord]:
        """Resolve all active conflicts with the same strategy.

        Args:
            resolution: Resolution strategy to use
            resolved_by: Email of person resolving

        Returns:
            List of resolved ConflictRecord objects
        """
        resolved = []
        for conflict in self.get_active_conflicts():
            try:
                resolved_conflict = self.resolve_conflict(
                    conflict.id, resolution, resolved_by
                )
                resolved.append(resolved_conflict)
            except ConflictError:
                continue
        return resolved

    def _archive_conflict(self, conflict: ConflictRecord) -> Path:
        """Archive a resolved conflict to the conflicts directory.

        Args:
            conflict: Resolved ConflictRecord

        Returns:
            Path to archived conflict file
        """
        self.archive_dir.mkdir(parents=True, exist_ok=True)

        # Create archive file
        archive_path = self.archive_dir / f"{conflict.id}.json"

        with open(archive_path, "w", encoding="utf-8") as f:
            json.dump(conflict.to_dict(), f, indent=2)

        # Remove from active conflicts
        state = self.get_state()
        state.active_conflicts = [
            c for c in state.active_conflicts if c.id != conflict.id
        ]
        self._save_state(state)
        self._state = state

        return archive_path

    def get_archived_conflicts(self, limit: int = 50) -> list[ConflictRecord]:
        """Get list of archived (resolved) conflicts.

        Args:
            limit: Maximum number to return

        Returns:
            List of archived ConflictRecord objects (newest first)
        """
        if not self.archive_dir.exists():
            return []

        conflicts = []
        archive_files = sorted(
            self.archive_dir.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        for archive_file in archive_files[:limit]:
            try:
                with open(archive_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                conflict = ConflictRecord.from_dict(data)
                conflicts.append(conflict)
            except (json.JSONDecodeError, KeyError):
                continue

        return conflicts

    def clear_active_conflicts(self) -> int:
        """Clear all active conflicts without resolving.

        Returns:
            Number of conflicts cleared
        """
        state = self.get_state()
        count = len(state.active_conflicts)
        state.active_conflicts = []
        self._save_state(state)
        self._state = state
        return count

    def get_conflict_diff(self, conflict: ConflictRecord) -> list[str]:
        """Get a diff between local and remote versions.

        Args:
            conflict: ConflictRecord to diff

        Returns:
            List of diff lines
        """
        import difflib

        local_lines = conflict.local_version.content.splitlines(keepends=True)
        remote_lines = conflict.remote_version.content.splitlines(keepends=True)

        diff = list(difflib.unified_diff(
            remote_lines,
            local_lines,
            fromfile=f"{conflict.file_path} (remote)",
            tofile=f"{conflict.file_path} (local)",
        ))

        return diff

    def get_side_by_side_diff(
        self, conflict: ConflictRecord, context_lines: int = 3
    ) -> list[tuple[str, str]]:
        """Get side-by-side diff of local and remote versions.

        Args:
            conflict: ConflictRecord to diff
            context_lines: Number of context lines around changes

        Returns:
            List of (local_line, remote_line) tuples
        """
        import difflib

        local_lines = conflict.local_version.content.splitlines()
        remote_lines = conflict.remote_version.content.splitlines()

        # Use SequenceMatcher for side-by-side comparison
        matcher = difflib.SequenceMatcher(None, remote_lines, local_lines)

        result = []
        for opcode, i1, i2, j1, j2 in matcher.get_opcodes():
            if opcode == "equal":
                for i in range(i2 - i1):
                    result.append((local_lines[j1 + i], remote_lines[i1 + i]))
            elif opcode == "replace":
                max_len = max(i2 - i1, j2 - j1)
                for i in range(max_len):
                    local = local_lines[j1 + i] if j1 + i < j2 else ""
                    remote = remote_lines[i1 + i] if i1 + i < i2 else ""
                    result.append((local, remote))
            elif opcode == "insert":
                for i in range(j2 - j1):
                    result.append((local_lines[j1 + i], ""))
            elif opcode == "delete":
                for i in range(i2 - i1):
                    result.append(("", remote_lines[i1 + i]))

        return result
