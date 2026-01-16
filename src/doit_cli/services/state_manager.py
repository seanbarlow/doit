"""State manager for workflow persistence.

This module handles saving and loading workflow state for recovery
after interruptions.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Protocol, runtime_checkable

from ..models.workflow_models import (
    WorkflowState,
    WorkflowStatus,
    StateCorruptionError,
)


# =============================================================================
# StateManager Protocol
# =============================================================================


@runtime_checkable
class StateManagerProtocol(Protocol):
    """Protocol defining the StateManager interface."""

    def save(self, state: WorkflowState) -> Path:
        """Save workflow state to file."""
        ...

    def load(self, command_name: str) -> WorkflowState | None:
        """Load most recent state for a command."""
        ...

    def delete(self, state: WorkflowState) -> None:
        """Delete state file after completion."""
        ...

    def list_interrupted(self) -> list[WorkflowState]:
        """List all interrupted workflow states."""
        ...

    def cleanup_stale(self, max_age_days: int = 7) -> int:
        """Remove state files older than threshold."""
        ...


# =============================================================================
# StateManager Implementation
# =============================================================================


class StateManager:
    """Manages workflow state persistence.

    Handles saving workflow state to JSON files for recovery after
    interruptions, loading previous state for resume, and cleanup
    of stale state files.

    State files are stored in `.doit/state/` by default.
    """

    DEFAULT_STATE_DIR = ".doit/state"

    def __init__(self, state_dir: Path | str | None = None):
        """Initialize the state manager.

        Args:
            state_dir: Directory to store state files. Defaults to .doit/state/
        """
        if state_dir is None:
            state_dir = Path.cwd() / self.DEFAULT_STATE_DIR
        self.state_dir = Path(state_dir)

    def save(self, state: WorkflowState) -> Path:
        """Save workflow state to file.

        Args:
            state: State to persist

        Returns:
            Path to saved state file
        """
        self._ensure_state_dir()

        # Generate filename from state ID
        filename = f"{state.id}.json"
        filepath = self.state_dir / filename

        # Serialize state to JSON
        state_data = state.to_dict()

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(state_data, f, indent=2)

        return filepath

    def load(self, command_name: str) -> WorkflowState | None:
        """Load most recent state for a command.

        Args:
            command_name: Command to find state for

        Returns:
            WorkflowState if found, None otherwise
        """
        if not self.state_dir.exists():
            return None

        # Find all state files for this command
        matching_files: list[tuple[Path, datetime]] = []

        for filepath in self.state_dir.glob("*.json"):
            if filepath.name.startswith(f"{command_name}_"):
                try:
                    state = self._load_file(filepath)
                    if state and state.status == WorkflowStatus.INTERRUPTED:
                        matching_files.append((filepath, state.updated_at))
                except (json.JSONDecodeError, KeyError, StateCorruptionError):
                    # Skip corrupted files
                    continue

        if not matching_files:
            return None

        # Return most recent
        matching_files.sort(key=lambda x: x[1], reverse=True)
        return self._load_file(matching_files[0][0])

    def delete(self, state: WorkflowState) -> None:
        """Delete state file after completion.

        Args:
            state: State to delete
        """
        filename = f"{state.id}.json"
        filepath = self.state_dir / filename

        if filepath.exists():
            filepath.unlink()

    def list_interrupted(self) -> list[WorkflowState]:
        """List all interrupted workflow states.

        Returns:
            List of interrupted states
        """
        if not self.state_dir.exists():
            return []

        interrupted: list[WorkflowState] = []

        for filepath in self.state_dir.glob("*.json"):
            try:
                state = self._load_file(filepath)
                if state and state.status == WorkflowStatus.INTERRUPTED:
                    interrupted.append(state)
            except (json.JSONDecodeError, KeyError, StateCorruptionError):
                continue

        # Sort by updated_at descending
        interrupted.sort(key=lambda s: s.updated_at, reverse=True)
        return interrupted

    def cleanup_stale(self, max_age_days: int = 7) -> int:
        """Remove state files older than threshold.

        Args:
            max_age_days: Maximum age before cleanup

        Returns:
            Number of files removed
        """
        if not self.state_dir.exists():
            return 0

        threshold = datetime.now() - timedelta(days=max_age_days)
        removed = 0

        for filepath in self.state_dir.glob("*.json"):
            try:
                state = self._load_file(filepath)
                if state and state.updated_at < threshold:
                    filepath.unlink()
                    removed += 1
            except (json.JSONDecodeError, KeyError, StateCorruptionError):
                # Remove corrupted files too
                filepath.unlink()
                removed += 1

        return removed

    def get_state_path(self, state: WorkflowState) -> Path:
        """Get the file path for a state.

        Args:
            state: Workflow state

        Returns:
            Path to state file
        """
        return self.state_dir / f"{state.id}.json"

    # =========================================================================
    # Internal Methods
    # =========================================================================

    def _ensure_state_dir(self) -> None:
        """Ensure the state directory exists."""
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def _load_file(self, filepath: Path) -> WorkflowState | None:
        """Load a state file.

        Args:
            filepath: Path to state file

        Returns:
            WorkflowState or None if file is invalid

        Raises:
            StateCorruptionError: If file is corrupted
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            return WorkflowState.from_dict(data)
        except json.JSONDecodeError as e:
            raise StateCorruptionError(
                filepath, f"Invalid JSON: {e}"
            )
        except KeyError as e:
            raise StateCorruptionError(
                filepath, f"Missing required field: {e}"
            )
        except Exception as e:
            raise StateCorruptionError(
                filepath, f"Failed to load: {e}"
            )

    # =========================================================================
    # Fixit Workflow State Methods (T013)
    # =========================================================================

    def save_fixit_state(self, state_data: dict, issue_id: int) -> Path:
        """Save fixit workflow state to file.

        Args:
            state_data: Dictionary containing workflow state
            issue_id: GitHub issue number

        Returns:
            Path to saved state file
        """
        self._ensure_state_dir()

        filename = f"fixit-{issue_id}.json"
        filepath = self.state_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(state_data, f, indent=2)

        return filepath

    def load_fixit_state(self, issue_id: int) -> dict | None:
        """Load fixit workflow state for an issue.

        Args:
            issue_id: GitHub issue number

        Returns:
            State dictionary if found, None otherwise
        """
        if not self.state_dir.exists():
            return None

        filename = f"fixit-{issue_id}.json"
        filepath = self.state_dir / filename

        if not filepath.exists():
            return None

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return None

    def delete_fixit_state(self, issue_id: int) -> bool:
        """Delete fixit workflow state for an issue.

        Args:
            issue_id: GitHub issue number

        Returns:
            True if deleted, False if not found
        """
        filename = f"fixit-{issue_id}.json"
        filepath = self.state_dir / filename

        if filepath.exists():
            filepath.unlink()
            return True
        return False

    def list_fixit_states(self) -> list[tuple[int, dict]]:
        """List all fixit workflow states.

        Returns:
            List of (issue_id, state_data) tuples
        """
        if not self.state_dir.exists():
            return []

        states: list[tuple[int, dict]] = []

        for filepath in self.state_dir.glob("fixit-*.json"):
            try:
                # Extract issue ID from filename
                issue_id_str = filepath.stem.replace("fixit-", "")
                issue_id = int(issue_id_str)

                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                states.append((issue_id, data))
            except (ValueError, json.JSONDecodeError, OSError):
                continue

        return states

    def get_active_fixit_workflow(self) -> tuple[int, dict] | None:
        """Get the currently active fixit workflow (most recent non-completed).

        Returns:
            Tuple of (issue_id, state_data) for active workflow, or None
        """
        states = self.list_fixit_states()

        # Filter for non-completed/cancelled workflows
        active_states = [
            (issue_id, data) for issue_id, data in states
            if data.get("workflow", {}).get("phase") not in ["completed", "cancelled"]
        ]

        if not active_states:
            return None

        # Return most recently updated
        active_states.sort(
            key=lambda x: x[1].get("workflow", {}).get("updated_at", ""),
            reverse=True
        )
        return active_states[0]
