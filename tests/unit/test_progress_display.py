"""Unit tests for ProgressDisplay class.

Tests the progress visualization functionality for guided workflows.
"""

import pytest
from unittest.mock import Mock, patch
from io import StringIO

from rich.console import Console

from doit_cli.models.workflow_models import (
    WorkflowStep,
    ValidationResult,
)


class TestProgressDisplayShowStep:
    """Tests for ProgressDisplay.show_step() method."""

    @pytest.fixture
    def progress(self):
        """Create a ProgressDisplay instance with captured output."""
        from doit_cli.prompts.interactive import ProgressDisplay

        # Use a string buffer to capture output
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        display = ProgressDisplay(console)
        display._output = output
        return display

    @pytest.fixture
    def step(self):
        """Create a workflow step."""
        return WorkflowStep(
            id="project-name",
            name="Project Name",
            prompt_text="Enter project name:",
            required=True,
            order=0,
        )

    @pytest.fixture
    def optional_step(self):
        """Create an optional step."""
        return WorkflowStep(
            id="description",
            name="Description",
            prompt_text="Enter description:",
            required=False,
            order=1,
            default_value="No description",
        )

    def test_show_step_displays_step_number(self, progress, step):
        """Test that step number is shown (1-indexed)."""
        progress.show_step(step, current=1, total=5)
        output = progress._output.getvalue()
        assert "1" in output and "5" in output

    def test_show_step_displays_step_name(self, progress, step):
        """Test that step name is displayed."""
        progress.show_step(step, current=1, total=5)
        output = progress._output.getvalue()
        assert step.name in output

    def test_show_step_shows_optional_indicator(self, progress, optional_step):
        """Test that optional steps are marked."""
        progress.show_step(optional_step, current=2, total=5)
        output = progress._output.getvalue()
        assert "optional" in output.lower()

    def test_show_step_calculates_percentage(self, progress, step):
        """Test that progress percentage is calculated correctly."""
        # At step 3 of 4 (before completion), should be 50% (2/4 completed)
        progress.show_step(step, current=3, total=4)
        output = progress._output.getvalue()
        assert "50%" in output or "Progress" in output


class TestProgressDisplayMarkComplete:
    """Tests for ProgressDisplay.mark_complete() method."""

    @pytest.fixture
    def progress(self):
        """Create a ProgressDisplay instance."""
        from doit_cli.prompts.interactive import ProgressDisplay

        output = StringIO()
        console = Console(file=output, force_terminal=True)
        display = ProgressDisplay(console)
        display._output = output
        return display

    @pytest.fixture
    def step(self):
        """Create a workflow step."""
        return WorkflowStep(
            id="test",
            name="Test Step",
            prompt_text="Enter:",
            required=True,
            order=0,
        )

    def test_mark_complete_shows_checkmark(self, progress, step):
        """Test that completed step shows checkmark symbol."""
        progress.mark_complete(step)
        output = progress._output.getvalue()
        # Should show checkmark (✓ or similar)
        assert "\u2713" in output or "completed" in output.lower()

    def test_mark_complete_shows_step_name(self, progress, step):
        """Test that completed step name is displayed."""
        progress.mark_complete(step)
        output = progress._output.getvalue()
        assert step.name in output

    def test_mark_complete_tracks_completed_steps(self, progress, step):
        """Test that completed steps are tracked internally."""
        progress.mark_complete(step)
        assert step.id in progress._completed_steps


class TestProgressDisplayMarkSkipped:
    """Tests for ProgressDisplay.mark_skipped() method."""

    @pytest.fixture
    def progress(self):
        """Create a ProgressDisplay instance."""
        from doit_cli.prompts.interactive import ProgressDisplay

        output = StringIO()
        console = Console(file=output, force_terminal=True)
        display = ProgressDisplay(console)
        display._output = output
        return display

    @pytest.fixture
    def optional_step(self):
        """Create an optional step."""
        return WorkflowStep(
            id="optional",
            name="Optional Step",
            prompt_text="Enter:",
            required=False,
            order=0,
            default_value="default",
        )

    def test_mark_skipped_shows_indication(self, progress, optional_step):
        """Test that skipped step shows skip indicator."""
        progress.mark_skipped(optional_step)
        output = progress._output.getvalue()
        assert "skipped" in output.lower()

    def test_mark_skipped_shows_step_name(self, progress, optional_step):
        """Test that skipped step name is displayed."""
        progress.mark_skipped(optional_step)
        output = progress._output.getvalue()
        assert optional_step.name in output

    def test_mark_skipped_tracks_skipped_steps(self, progress, optional_step):
        """Test that skipped steps are tracked internally."""
        progress.mark_skipped(optional_step)
        assert optional_step.id in progress._skipped_steps


class TestProgressDisplayShowError:
    """Tests for ProgressDisplay.show_error() method."""

    @pytest.fixture
    def progress(self):
        """Create a ProgressDisplay instance."""
        from doit_cli.prompts.interactive import ProgressDisplay

        output = StringIO()
        console = Console(file=output, force_terminal=True)
        display = ProgressDisplay(console)
        display._output = output
        return display

    @pytest.fixture
    def step(self):
        """Create a workflow step."""
        return WorkflowStep(
            id="test",
            name="Test Step",
            prompt_text="Enter:",
            required=True,
            order=0,
        )

    def test_show_error_displays_error_message(self, progress, step):
        """Test that error message is displayed."""
        error = ValidationResult.failure("Value is too short")
        progress.show_error(step, error)
        output = progress._output.getvalue()
        assert "too short" in output

    def test_show_error_displays_suggestion(self, progress, step):
        """Test that suggestion is displayed."""
        error = ValidationResult.failure(
            "Invalid format",
            suggestion="Use format: name@domain.com"
        )
        progress.show_error(step, error)
        output = progress._output.getvalue()
        assert "domain.com" in output

    def test_show_error_includes_step_name(self, progress, step):
        """Test that step name is included in error display."""
        error = ValidationResult.failure("Error message")
        progress.show_error(step, error)
        output = progress._output.getvalue()
        assert step.name in output


class TestProgressDisplayShowSummary:
    """Tests for ProgressDisplay.show_summary() method."""

    @pytest.fixture
    def progress(self):
        """Create a ProgressDisplay instance."""
        from doit_cli.prompts.interactive import ProgressDisplay

        output = StringIO()
        console = Console(file=output, force_terminal=True)
        display = ProgressDisplay(console)
        display._output = output
        return display

    def test_show_summary_displays_complete_message(self, progress):
        """Test that summary shows completion message."""
        progress._completed_steps = ["step1", "step2"]
        progress.show_summary(total_steps=3)
        output = progress._output.getvalue()
        assert "complete" in output.lower()

    def test_show_summary_shows_completed_count(self, progress):
        """Test that summary shows number of completed steps."""
        progress._completed_steps = ["step1", "step2", "step3"]
        progress.show_summary(total_steps=3)
        output = progress._output.getvalue()
        assert "3" in output

    def test_show_summary_shows_skipped_count(self, progress):
        """Test that summary shows skipped steps if any."""
        progress._completed_steps = ["step1", "step3"]
        progress._skipped_steps = ["step2"]
        progress.show_summary(total_steps=3)
        output = progress._output.getvalue()
        assert "skipped" in output.lower() or "1" in output


class TestProgressDisplayShowInterrupted:
    """Tests for ProgressDisplay.show_interrupted() method."""

    @pytest.fixture
    def progress(self):
        """Create a ProgressDisplay instance."""
        from doit_cli.prompts.interactive import ProgressDisplay

        output = StringIO()
        console = Console(file=output, force_terminal=True)
        display = ProgressDisplay(console)
        display._output = output
        return display

    def test_show_interrupted_displays_warning(self, progress):
        """Test that interrupted message shows warning."""
        progress.show_interrupted(current_step=2, total_steps=5)
        output = progress._output.getvalue()
        assert "interrupted" in output.lower()

    def test_show_interrupted_shows_progress(self, progress):
        """Test that current step progress is shown."""
        progress.show_interrupted(current_step=3, total_steps=5)
        output = progress._output.getvalue()
        assert "3" in output and "5" in output

    def test_show_interrupted_mentions_resume(self, progress):
        """Test that resume instructions are provided."""
        progress.show_interrupted(current_step=2, total_steps=5)
        output = progress._output.getvalue()
        assert "resume" in output.lower() or "saved" in output.lower()


class TestProgressDisplayIntegration:
    """Integration tests for ProgressDisplay with real console output."""

    @pytest.fixture
    def progress(self):
        """Create a ProgressDisplay instance."""
        from doit_cli.prompts.interactive import ProgressDisplay

        return ProgressDisplay()

    def test_full_workflow_progress(self, progress, capsys):
        """Test complete workflow progress sequence."""
        steps = [
            WorkflowStep(id="s1", name="Step 1", prompt_text=":", required=True, order=0),
            WorkflowStep(id="s2", name="Step 2", prompt_text=":", required=False, order=1, default_value="d"),
            WorkflowStep(id="s3", name="Step 3", prompt_text=":", required=True, order=2),
        ]

        # Simulate workflow execution
        progress.show_step(steps[0], current=1, total=3)
        progress.mark_complete(steps[0])

        progress.show_step(steps[1], current=2, total=3)
        progress.mark_skipped(steps[1])

        progress.show_step(steps[2], current=3, total=3)
        progress.mark_complete(steps[2])

        progress.show_summary(total_steps=3)

        # Verify tracking
        assert len(progress._completed_steps) == 2
        assert len(progress._skipped_steps) == 1
