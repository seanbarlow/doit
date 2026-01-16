"""Unit tests for StatusReporter service."""

import pytest
from datetime import datetime, timedelta
from pathlib import Path

from doit_cli.models.status_models import SpecState, SpecStatus, StatusReport
from doit_cli.services.status_reporter import StatusReporter


class TestStatusReporterFilters:
    """Tests for StatusReporter filter methods."""

    @pytest.fixture
    def sample_specs(self) -> list[SpecStatus]:
        """Create a sample list of specs for testing."""
        now = datetime.now()
        return [
            SpecStatus(
                name="001-draft-spec",
                path=Path("specs/001-draft-spec/spec.md"),
                status=SpecState.DRAFT,
                last_modified=now - timedelta(days=1),
                is_blocking=False,
            ),
            SpecStatus(
                name="002-in-progress-blocking",
                path=Path("specs/002-in-progress-blocking/spec.md"),
                status=SpecState.IN_PROGRESS,
                last_modified=now - timedelta(days=2),
                is_blocking=True,
            ),
            SpecStatus(
                name="003-complete-spec",
                path=Path("specs/003-complete-spec/spec.md"),
                status=SpecState.COMPLETE,
                last_modified=now - timedelta(days=10),
                is_blocking=False,
            ),
            SpecStatus(
                name="004-approved-spec",
                path=Path("specs/004-approved-spec/spec.md"),
                status=SpecState.APPROVED,
                last_modified=now - timedelta(days=30),
                is_blocking=False,
            ),
            SpecStatus(
                name="005-draft-blocking",
                path=Path("specs/005-draft-blocking/spec.md"),
                status=SpecState.DRAFT,
                last_modified=now,
                is_blocking=True,
            ),
        ]

    def test_filter_by_status_draft(self, sample_specs):
        """Test filtering by draft status."""
        reporter = StatusReporter.__new__(StatusReporter)
        result = reporter.filter_by_status(sample_specs, SpecState.DRAFT)

        assert len(result) == 2
        assert all(s.status == SpecState.DRAFT for s in result)

    def test_filter_by_status_in_progress(self, sample_specs):
        """Test filtering by in progress status."""
        reporter = StatusReporter.__new__(StatusReporter)
        result = reporter.filter_by_status(sample_specs, SpecState.IN_PROGRESS)

        assert len(result) == 1
        assert result[0].name == "002-in-progress-blocking"

    def test_filter_by_status_complete(self, sample_specs):
        """Test filtering by complete status."""
        reporter = StatusReporter.__new__(StatusReporter)
        result = reporter.filter_by_status(sample_specs, SpecState.COMPLETE)

        assert len(result) == 1
        assert result[0].name == "003-complete-spec"

    def test_filter_by_status_approved(self, sample_specs):
        """Test filtering by approved status."""
        reporter = StatusReporter.__new__(StatusReporter)
        result = reporter.filter_by_status(sample_specs, SpecState.APPROVED)

        assert len(result) == 1
        assert result[0].name == "004-approved-spec"

    def test_filter_blocking(self, sample_specs):
        """Test filtering for blocking specs only."""
        reporter = StatusReporter.__new__(StatusReporter)
        result = reporter.filter_blocking(sample_specs)

        assert len(result) == 2
        assert all(s.is_blocking for s in result)
        names = [s.name for s in result]
        assert "002-in-progress-blocking" in names
        assert "005-draft-blocking" in names

    def test_filter_recent_7_days(self, sample_specs):
        """Test filtering for specs modified in last 7 days."""
        reporter = StatusReporter.__new__(StatusReporter)
        result = reporter.filter_recent(sample_specs, days=7)

        assert len(result) == 3
        names = [s.name for s in result]
        assert "001-draft-spec" in names  # 1 day ago
        assert "002-in-progress-blocking" in names  # 2 days ago
        assert "005-draft-blocking" in names  # today

    def test_filter_recent_1_day(self, sample_specs):
        """Test filtering for specs modified in last 1 day."""
        reporter = StatusReporter.__new__(StatusReporter)
        result = reporter.filter_recent(sample_specs, days=1)

        # Only today's spec should be included
        assert len(result) == 1
        assert result[0].name == "005-draft-blocking"

    def test_filter_recent_30_days(self, sample_specs):
        """Test filtering for specs modified in last 30 days."""
        reporter = StatusReporter.__new__(StatusReporter)
        result = reporter.filter_recent(sample_specs, days=31)

        # All specs should be included (using 31 to include the 30-day-old spec)
        assert len(result) == 5

    def test_apply_filters_status_only(self, sample_specs):
        """Test _apply_filters with only status filter."""
        reporter = StatusReporter.__new__(StatusReporter)
        result = reporter._apply_filters(
            sample_specs,
            status_filter=SpecState.DRAFT,
            blocking_only=False,
            recent_days=None,
        )

        assert len(result) == 2
        assert all(s.status == SpecState.DRAFT for s in result)

    def test_apply_filters_blocking_only(self, sample_specs):
        """Test _apply_filters with only blocking filter."""
        reporter = StatusReporter.__new__(StatusReporter)
        result = reporter._apply_filters(
            sample_specs,
            status_filter=None,
            blocking_only=True,
            recent_days=None,
        )

        assert len(result) == 2
        assert all(s.is_blocking for s in result)

    def test_apply_filters_combined(self, sample_specs):
        """Test _apply_filters with multiple filters."""
        reporter = StatusReporter.__new__(StatusReporter)
        result = reporter._apply_filters(
            sample_specs,
            status_filter=SpecState.DRAFT,
            blocking_only=True,
            recent_days=None,
        )

        # Only draft + blocking
        assert len(result) == 1
        assert result[0].name == "005-draft-blocking"

    def test_apply_filters_all_combined(self, sample_specs):
        """Test _apply_filters with all filters."""
        reporter = StatusReporter.__new__(StatusReporter)
        result = reporter._apply_filters(
            sample_specs,
            status_filter=SpecState.DRAFT,
            blocking_only=True,
            recent_days=1,
        )

        # Only draft + blocking + recent (today)
        assert len(result) == 1
        assert result[0].name == "005-draft-blocking"

    def test_apply_filters_no_matches(self, sample_specs):
        """Test _apply_filters when no specs match."""
        reporter = StatusReporter.__new__(StatusReporter)
        result = reporter._apply_filters(
            sample_specs,
            status_filter=SpecState.ERROR,
            blocking_only=False,
            recent_days=None,
        )

        assert len(result) == 0

    def test_apply_filters_empty_input(self):
        """Test _apply_filters with empty spec list."""
        reporter = StatusReporter.__new__(StatusReporter)
        result = reporter._apply_filters(
            [],
            status_filter=SpecState.DRAFT,
            blocking_only=True,
            recent_days=7,
        )

        assert len(result) == 0


class TestStatusReporterInit:
    """Tests for StatusReporter initialization."""

    def test_init_with_valid_project(self, tmp_path):
        """Test reporter initializes with valid doit project."""
        (tmp_path / ".doit").mkdir()

        reporter = StatusReporter(tmp_path)
        assert reporter.project_root == tmp_path

    def test_init_without_doit_dir_raises_error(self, tmp_path):
        """Test reporter raises error when .doit directory is missing."""
        from doit_cli.services.spec_scanner import NotADoitProjectError

        with pytest.raises(NotADoitProjectError):
            StatusReporter(tmp_path)


class TestStatusReporterGenerateReport:
    """Tests for StatusReporter generate_report method."""

    def test_generate_report_empty_project(self, tmp_path):
        """Test generating report for empty project."""
        (tmp_path / ".doit").mkdir()
        (tmp_path / "specs").mkdir()

        reporter = StatusReporter(tmp_path, validate=False)
        report = reporter.generate_report()

        assert isinstance(report, StatusReport)
        assert report.total_count == 0
        assert report.project_root == tmp_path

    def test_generate_report_with_specs(self, tmp_path):
        """Test generating report with specs."""
        (tmp_path / ".doit").mkdir()
        spec_dir = tmp_path / "specs" / "001-test"
        spec_dir.mkdir(parents=True)
        (spec_dir / "spec.md").write_text("**Status**: Draft\n")

        reporter = StatusReporter(tmp_path, validate=False)
        report = reporter.generate_report()

        assert report.total_count == 1
        assert report.draft_count == 1

    def test_generate_report_with_status_filter(self, tmp_path):
        """Test generating report with status filter."""
        (tmp_path / ".doit").mkdir()

        for name, status in [("001-a", "Draft"), ("002-b", "Complete")]:
            spec_dir = tmp_path / "specs" / name
            spec_dir.mkdir(parents=True)
            (spec_dir / "spec.md").write_text(f"**Status**: {status}\n")

        reporter = StatusReporter(tmp_path, validate=False)
        report = reporter.generate_report(status_filter=SpecState.DRAFT)

        assert report.total_count == 1
        assert report.specs[0].name == "001-a"
