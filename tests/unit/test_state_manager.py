"""Unit tests for StateManager class.

Tests the state persistence functionality for workflow recovery.
"""

import json
import pytest
from datetime import datetime, timedelta
from pathlib import Path

from doit_cli.models.workflow_models import (
    WorkflowState,
    WorkflowStatus,
    StepResponse,
    StateCorruptionError,
)


class TestStateManagerSave:
    """Tests for StateManager.save() method."""

    @pytest.fixture
    def manager(self, tmp_path):
        """Create a StateManager with temp directory."""
        from doit_cli.services.state_manager import StateManager

        return StateManager(state_dir=tmp_path / ".doit/state")

    @pytest.fixture
    def state(self):
        """Create a workflow state."""
        state = WorkflowState(
            id="test_20260115_120000",
            workflow_id="test-workflow",
            command_name="test",
            current_step=2,
            status=WorkflowStatus.INTERRUPTED,
        )
        state.responses["step1"] = StepResponse(
            step_id="step1",
            value="value1",
        )
        return state

    def test_save_creates_state_dir(self, manager, state):
        """Test that save creates state directory if needed."""
        assert not manager.state_dir.exists()

        manager.save(state)

        assert manager.state_dir.exists()

    def test_save_creates_json_file(self, manager, state):
        """Test that save creates a JSON file."""
        filepath = manager.save(state)

        assert filepath.exists()
        assert filepath.suffix == ".json"

    def test_save_uses_state_id_as_filename(self, manager, state):
        """Test that filename is based on state ID."""
        filepath = manager.save(state)

        assert filepath.name == f"{state.id}.json"

    def test_save_writes_valid_json(self, manager, state):
        """Test that saved file contains valid JSON."""
        filepath = manager.save(state)

        with open(filepath) as f:
            data = json.load(f)

        assert data["id"] == state.id
        assert data["workflow_id"] == state.workflow_id
        assert data["command_name"] == state.command_name
        assert data["current_step"] == state.current_step
        assert data["status"] == "interrupted"

    def test_save_includes_responses(self, manager, state):
        """Test that responses are saved."""
        filepath = manager.save(state)

        with open(filepath) as f:
            data = json.load(f)

        assert "step1" in data["responses"]
        assert data["responses"]["step1"]["value"] == "value1"


class TestStateManagerLoad:
    """Tests for StateManager.load() method."""

    @pytest.fixture
    def manager(self, tmp_path):
        """Create a StateManager with temp directory."""
        from doit_cli.services.state_manager import StateManager

        return StateManager(state_dir=tmp_path / ".doit/state")

    def test_load_returns_none_if_no_dir(self, manager):
        """Test that load returns None if state dir doesn't exist."""
        result = manager.load("test")
        assert result is None

    def test_load_returns_none_if_no_matching_files(self, manager, tmp_path):
        """Test that load returns None if no matching state files."""
        manager.state_dir.mkdir(parents=True)

        # Create a file for different command
        other_state = WorkflowState(
            id="other_20260115_120000",
            workflow_id="other-workflow",
            command_name="other",
            status=WorkflowStatus.INTERRUPTED,
        )
        manager.save(other_state)

        result = manager.load("test")
        assert result is None

    def test_load_returns_most_recent(self, manager):
        """Test that load returns most recent interrupted state."""
        # Create older state
        old_state = WorkflowState(
            id="test_20260115_100000",
            workflow_id="test-workflow",
            command_name="test",
            status=WorkflowStatus.INTERRUPTED,
            updated_at=datetime(2026, 1, 15, 10, 0, 0),
        )
        manager.save(old_state)

        # Create newer state
        new_state = WorkflowState(
            id="test_20260115_120000",
            workflow_id="test-workflow",
            command_name="test",
            status=WorkflowStatus.INTERRUPTED,
            updated_at=datetime(2026, 1, 15, 12, 0, 0),
        )
        manager.save(new_state)

        result = manager.load("test")

        assert result is not None
        assert result.id == new_state.id

    def test_load_ignores_completed_states(self, manager):
        """Test that completed states are not loaded."""
        completed = WorkflowState(
            id="test_20260115_120000",
            workflow_id="test-workflow",
            command_name="test",
            status=WorkflowStatus.COMPLETED,
        )
        manager.save(completed)

        result = manager.load("test")
        assert result is None

    def test_load_restores_responses(self, manager):
        """Test that responses are restored correctly."""
        state = WorkflowState(
            id="test_20260115_120000",
            workflow_id="test-workflow",
            command_name="test",
            status=WorkflowStatus.INTERRUPTED,
        )
        state.responses["step1"] = StepResponse(
            step_id="step1",
            value="test-value",
            skipped=False,
        )
        manager.save(state)

        result = manager.load("test")

        assert result is not None
        assert "step1" in result.responses
        assert result.responses["step1"].value == "test-value"


class TestStateManagerDelete:
    """Tests for StateManager.delete() method."""

    @pytest.fixture
    def manager(self, tmp_path):
        """Create a StateManager with temp directory."""
        from doit_cli.services.state_manager import StateManager

        return StateManager(state_dir=tmp_path / ".doit/state")

    def test_delete_removes_state_file(self, manager):
        """Test that delete removes the state file."""
        state = WorkflowState(
            id="test_20260115_120000",
            workflow_id="test-workflow",
            command_name="test",
            status=WorkflowStatus.INTERRUPTED,
        )
        filepath = manager.save(state)

        assert filepath.exists()

        manager.delete(state)

        assert not filepath.exists()

    def test_delete_handles_nonexistent_file(self, manager):
        """Test that delete doesn't error on nonexistent file."""
        state = WorkflowState(
            id="nonexistent",
            workflow_id="test-workflow",
            command_name="test",
        )

        # Should not raise
        manager.delete(state)


class TestStateManagerListInterrupted:
    """Tests for StateManager.list_interrupted() method."""

    @pytest.fixture
    def manager(self, tmp_path):
        """Create a StateManager with temp directory."""
        from doit_cli.services.state_manager import StateManager

        return StateManager(state_dir=tmp_path / ".doit/state")

    def test_list_returns_empty_if_no_dir(self, manager):
        """Test that list returns empty if no state dir."""
        result = manager.list_interrupted()
        assert result == []

    def test_list_returns_only_interrupted(self, manager):
        """Test that only interrupted states are returned."""
        interrupted = WorkflowState(
            id="test1",
            workflow_id="test-workflow",
            command_name="test",
            status=WorkflowStatus.INTERRUPTED,
        )
        completed = WorkflowState(
            id="test2",
            workflow_id="test-workflow",
            command_name="test",
            status=WorkflowStatus.COMPLETED,
        )

        manager.save(interrupted)
        manager.save(completed)

        result = manager.list_interrupted()

        assert len(result) == 1
        assert result[0].id == "test1"

    def test_list_returns_sorted_by_updated(self, manager):
        """Test that list is sorted by updated_at descending."""
        older = WorkflowState(
            id="older",
            workflow_id="test-workflow",
            command_name="test",
            status=WorkflowStatus.INTERRUPTED,
            updated_at=datetime(2026, 1, 15, 10, 0, 0),
        )
        newer = WorkflowState(
            id="newer",
            workflow_id="test-workflow",
            command_name="test",
            status=WorkflowStatus.INTERRUPTED,
            updated_at=datetime(2026, 1, 15, 12, 0, 0),
        )

        manager.save(older)
        manager.save(newer)

        result = manager.list_interrupted()

        assert result[0].id == "newer"
        assert result[1].id == "older"


class TestStateManagerCleanupStale:
    """Tests for StateManager.cleanup_stale() method."""

    @pytest.fixture
    def manager(self, tmp_path):
        """Create a StateManager with temp directory."""
        from doit_cli.services.state_manager import StateManager

        return StateManager(state_dir=tmp_path / ".doit/state")

    def test_cleanup_returns_zero_if_no_dir(self, manager):
        """Test that cleanup returns 0 if no state dir."""
        result = manager.cleanup_stale()
        assert result == 0

    def test_cleanup_removes_old_files(self, manager):
        """Test that files older than threshold are removed."""
        old_state = WorkflowState(
            id="old",
            workflow_id="test-workflow",
            command_name="test",
            status=WorkflowStatus.INTERRUPTED,
            updated_at=datetime.now() - timedelta(days=10),
        )
        manager.save(old_state)

        removed = manager.cleanup_stale(max_age_days=7)

        assert removed == 1
        assert not (manager.state_dir / "old.json").exists()

    def test_cleanup_keeps_recent_files(self, manager):
        """Test that recent files are kept."""
        recent_state = WorkflowState(
            id="recent",
            workflow_id="test-workflow",
            command_name="test",
            status=WorkflowStatus.INTERRUPTED,
            updated_at=datetime.now() - timedelta(days=1),
        )
        manager.save(recent_state)

        removed = manager.cleanup_stale(max_age_days=7)

        assert removed == 0
        assert (manager.state_dir / "recent.json").exists()

    def test_cleanup_removes_corrupted_files(self, manager):
        """Test that corrupted files are also removed."""
        manager.state_dir.mkdir(parents=True)

        # Create a corrupted file
        corrupted = manager.state_dir / "corrupted.json"
        corrupted.write_text("not valid json")

        removed = manager.cleanup_stale()

        assert removed == 1
        assert not corrupted.exists()


class TestStateManagerGetStatePath:
    """Tests for StateManager.get_state_path() method."""

    @pytest.fixture
    def manager(self, tmp_path):
        """Create a StateManager with temp directory."""
        from doit_cli.services.state_manager import StateManager

        return StateManager(state_dir=tmp_path / ".doit/state")

    def test_get_state_path_returns_correct_path(self, manager):
        """Test that get_state_path returns correct path."""
        state = WorkflowState(
            id="test_state",
            workflow_id="test-workflow",
            command_name="test",
        )

        path = manager.get_state_path(state)

        assert path == manager.state_dir / "test_state.json"


class TestStateManagerCorruptionHandling:
    """Tests for handling corrupted state files."""

    @pytest.fixture
    def manager(self, tmp_path):
        """Create a StateManager with temp directory."""
        from doit_cli.services.state_manager import StateManager

        return StateManager(state_dir=tmp_path / ".doit/state")

    def test_load_skips_corrupted_files(self, manager):
        """Test that corrupted files are skipped during load."""
        manager.state_dir.mkdir(parents=True)

        # Create a corrupted file
        corrupted = manager.state_dir / "test_corrupted.json"
        corrupted.write_text("not valid json")

        # Create a valid file
        valid_state = WorkflowState(
            id="test_valid",
            workflow_id="test-workflow",
            command_name="test",
            status=WorkflowStatus.INTERRUPTED,
        )
        manager.save(valid_state)

        # Should load the valid state without error
        result = manager.load("test")
        assert result is not None
        assert result.id == "test_valid"

    def test_list_skips_corrupted_files(self, manager):
        """Test that list_interrupted skips corrupted files."""
        manager.state_dir.mkdir(parents=True)

        # Create a corrupted file
        corrupted = manager.state_dir / "corrupted.json"
        corrupted.write_text("{invalid}")

        # Create a valid file
        valid_state = WorkflowState(
            id="valid",
            workflow_id="test-workflow",
            command_name="test",
            status=WorkflowStatus.INTERRUPTED,
        )
        manager.save(valid_state)

        result = manager.list_interrupted()

        assert len(result) == 1
        assert result[0].id == "valid"
