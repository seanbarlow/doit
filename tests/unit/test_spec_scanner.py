"""Unit tests for SpecScanner service."""

import pytest
from datetime import datetime
from pathlib import Path

from doit_cli.models.status_models import SpecState, SpecStatus, StatusReport
from doit_cli.services.spec_scanner import (
    NotADoitProjectError,
    SpecNotFoundError,
    SpecScanner,
)


class TestSpecState:
    """Tests for SpecState enum."""

    def test_from_string_draft(self):
        """Test parsing Draft status."""
        assert SpecState.from_string("Draft") == SpecState.DRAFT
        assert SpecState.from_string("draft") == SpecState.DRAFT
        assert SpecState.from_string("DRAFT") == SpecState.DRAFT

    def test_from_string_in_progress(self):
        """Test parsing In Progress status variations."""
        assert SpecState.from_string("In Progress") == SpecState.IN_PROGRESS
        assert SpecState.from_string("in progress") == SpecState.IN_PROGRESS
        assert SpecState.from_string("in_progress") == SpecState.IN_PROGRESS
        assert SpecState.from_string("inprogress") == SpecState.IN_PROGRESS
        assert SpecState.from_string("in-progress") == SpecState.IN_PROGRESS

    def test_from_string_complete(self):
        """Test parsing Complete status."""
        assert SpecState.from_string("Complete") == SpecState.COMPLETE
        assert SpecState.from_string("completed") == SpecState.COMPLETE

    def test_from_string_approved(self):
        """Test parsing Approved status."""
        assert SpecState.from_string("Approved") == SpecState.APPROVED
        assert SpecState.from_string("done") == SpecState.APPROVED

    def test_from_string_unknown_returns_error(self):
        """Test that unknown status returns ERROR."""
        assert SpecState.from_string("Unknown") == SpecState.ERROR
        assert SpecState.from_string("invalid") == SpecState.ERROR
        assert SpecState.from_string("") == SpecState.ERROR

    def test_display_name(self):
        """Test human-readable display names."""
        assert SpecState.DRAFT.display_name == "Draft"
        assert SpecState.IN_PROGRESS.display_name == "In Progress"
        assert SpecState.COMPLETE.display_name == "Complete"
        assert SpecState.APPROVED.display_name == "Approved"
        assert SpecState.ERROR.display_name == "Error"

    def test_emoji(self):
        """Test emoji representations."""
        assert SpecState.DRAFT.emoji == "📝"
        assert SpecState.IN_PROGRESS.emoji == "🔄"
        assert SpecState.COMPLETE.emoji == "✅"
        assert SpecState.APPROVED.emoji == "🏆"
        assert SpecState.ERROR.emoji == "❌"


class TestSpecScanner:
    """Tests for SpecScanner service."""

    def test_init_with_valid_project(self, tmp_path):
        """Test scanner initializes with valid doit project."""
        # Create .doit directory
        (tmp_path / ".doit").mkdir()

        scanner = SpecScanner(tmp_path)
        assert scanner.project_root == tmp_path

    def test_init_without_doit_dir_raises_error(self, tmp_path):
        """Test scanner raises error when .doit directory is missing."""
        with pytest.raises(NotADoitProjectError) as excinfo:
            SpecScanner(tmp_path)

        assert "Not a doit project" in str(excinfo.value)
        assert "doit init" in str(excinfo.value)

    def test_scan_empty_specs_directory(self, tmp_path):
        """Test scanning when specs directory is empty."""
        (tmp_path / ".doit").mkdir()
        (tmp_path / "specs").mkdir()

        scanner = SpecScanner(tmp_path)
        result = scanner.scan()

        assert result == []

    def test_scan_no_specs_directory(self, tmp_path):
        """Test scanning when specs directory doesn't exist."""
        (tmp_path / ".doit").mkdir()

        scanner = SpecScanner(tmp_path)
        result = scanner.scan()

        assert result == []

    def test_scan_single_spec(self, tmp_path):
        """Test scanning a single spec."""
        # Setup
        (tmp_path / ".doit").mkdir()
        spec_dir = tmp_path / "specs" / "001-test-feature"
        spec_dir.mkdir(parents=True)

        spec_content = """# Feature Specification: Test Feature

**Feature Branch**: `001-test-feature`
**Created**: 2026-01-16
**Status**: Draft

## Requirements
- Something
"""
        (spec_dir / "spec.md").write_text(spec_content)

        # Test
        scanner = SpecScanner(tmp_path)
        result = scanner.scan()

        assert len(result) == 1
        assert result[0].name == "001-test-feature"
        assert result[0].status == SpecState.DRAFT
        assert result[0].error is None

    def test_scan_multiple_specs(self, tmp_path):
        """Test scanning multiple specs."""
        (tmp_path / ".doit").mkdir()

        specs = [
            ("001-feature-a", "Draft"),
            ("002-feature-b", "In Progress"),
            ("003-feature-c", "Complete"),
        ]

        for name, status in specs:
            spec_dir = tmp_path / "specs" / name
            spec_dir.mkdir(parents=True)
            (spec_dir / "spec.md").write_text(f"**Status**: {status}\n")

        scanner = SpecScanner(tmp_path)
        result = scanner.scan()

        assert len(result) == 3
        assert result[0].name == "001-feature-a"
        assert result[0].status == SpecState.DRAFT
        assert result[1].name == "002-feature-b"
        assert result[1].status == SpecState.IN_PROGRESS
        assert result[2].name == "003-feature-c"
        assert result[2].status == SpecState.COMPLETE

    def test_scan_spec_without_status_returns_error(self, tmp_path):
        """Test that specs without status field get ERROR state."""
        (tmp_path / ".doit").mkdir()
        spec_dir = tmp_path / "specs" / "001-missing-status"
        spec_dir.mkdir(parents=True)
        (spec_dir / "spec.md").write_text("# No status here\n")

        scanner = SpecScanner(tmp_path)
        result = scanner.scan()

        assert len(result) == 1
        assert result[0].status == SpecState.ERROR

    def test_scan_single_by_name(self, tmp_path):
        """Test scanning a single spec by name."""
        (tmp_path / ".doit").mkdir()
        spec_dir = tmp_path / "specs" / "001-test"
        spec_dir.mkdir(parents=True)
        (spec_dir / "spec.md").write_text("**Status**: Draft\n")

        scanner = SpecScanner(tmp_path)
        result = scanner.scan_single("001-test")

        assert result.name == "001-test"
        assert result.status == SpecState.DRAFT

    def test_scan_single_not_found_raises_error(self, tmp_path):
        """Test that scan_single raises error for missing spec."""
        (tmp_path / ".doit").mkdir()
        (tmp_path / "specs").mkdir()

        scanner = SpecScanner(tmp_path)

        with pytest.raises(SpecNotFoundError) as excinfo:
            scanner.scan_single("nonexistent")

        assert "Spec not found" in str(excinfo.value)

    def test_generate_report(self, tmp_path):
        """Test generating a full StatusReport."""
        (tmp_path / ".doit").mkdir()

        for name, status in [("001-a", "Draft"), ("002-b", "Complete")]:
            spec_dir = tmp_path / "specs" / name
            spec_dir.mkdir(parents=True)
            (spec_dir / "spec.md").write_text(f"**Status**: {status}\n")

        scanner = SpecScanner(tmp_path)
        report = scanner.generate_report()

        assert isinstance(report, StatusReport)
        assert report.total_count == 2
        assert report.project_root == tmp_path
        assert report.draft_count == 1
        assert report.complete_count == 1


class TestStatusReport:
    """Tests for StatusReport computed properties."""

    def test_empty_report(self):
        """Test computed properties with empty report."""
        report = StatusReport()

        assert report.total_count == 0
        assert report.blocking_count == 0
        assert report.completion_percentage == 0.0
        assert report.is_ready_to_commit is True

    def test_completion_percentage(self):
        """Test completion percentage calculation."""
        specs = [
            SpecStatus(
                name="a",
                path=Path("a"),
                status=SpecState.DRAFT,
                last_modified=datetime.now(),
            ),
            SpecStatus(
                name="b",
                path=Path("b"),
                status=SpecState.COMPLETE,
                last_modified=datetime.now(),
            ),
            SpecStatus(
                name="c",
                path=Path("c"),
                status=SpecState.APPROVED,
                last_modified=datetime.now(),
            ),
            SpecStatus(
                name="d",
                path=Path("d"),
                status=SpecState.IN_PROGRESS,
                last_modified=datetime.now(),
            ),
        ]

        report = StatusReport(specs=specs)

        # 2 out of 4 are Complete or Approved = 50%
        assert report.completion_percentage == 50.0

    def test_blocking_count(self):
        """Test blocking count calculation."""
        specs = [
            SpecStatus(
                name="a",
                path=Path("a"),
                status=SpecState.DRAFT,
                last_modified=datetime.now(),
                is_blocking=False,
            ),
            SpecStatus(
                name="b",
                path=Path("b"),
                status=SpecState.IN_PROGRESS,
                last_modified=datetime.now(),
                is_blocking=True,
            ),
            SpecStatus(
                name="c",
                path=Path("c"),
                status=SpecState.IN_PROGRESS,
                last_modified=datetime.now(),
                is_blocking=True,
            ),
        ]

        report = StatusReport(specs=specs)

        assert report.blocking_count == 2
        assert report.is_ready_to_commit is False

    def test_by_status(self):
        """Test status grouping."""
        specs = [
            SpecStatus(
                name="a",
                path=Path("a"),
                status=SpecState.DRAFT,
                last_modified=datetime.now(),
            ),
            SpecStatus(
                name="b",
                path=Path("b"),
                status=SpecState.DRAFT,
                last_modified=datetime.now(),
            ),
            SpecStatus(
                name="c",
                path=Path("c"),
                status=SpecState.IN_PROGRESS,
                last_modified=datetime.now(),
            ),
        ]

        report = StatusReport(specs=specs)
        by_status = report.by_status

        assert by_status[SpecState.DRAFT] == 2
        assert by_status[SpecState.IN_PROGRESS] == 1
        assert by_status[SpecState.COMPLETE] == 0


class TestBlockingLogic:
    """Tests for blocking logic computation (T016)."""

    def test_in_progress_with_validation_errors_is_blocking(self, tmp_path):
        """Test that IN_PROGRESS specs block when validation fails."""
        from doit_cli.models.validation_models import (
            ValidationResult,
            ValidationIssue,
            Severity,
        )

        spec_status = SpecStatus(
            name="test-spec",
            path=tmp_path / "spec.md",
            status=SpecState.IN_PROGRESS,
            last_modified=datetime.now(),
            validation_result=ValidationResult(
                spec_path=str(tmp_path / "spec.md"),
                issues=[
                    ValidationIssue(
                        rule_id="test-rule",
                        severity=Severity.ERROR,
                        line_number=1,
                        message="Test error",
                    )
                ],
            ),
            is_blocking=False,
        )

        (tmp_path / ".doit").mkdir()
        scanner = SpecScanner(tmp_path, validate=False)
        result = scanner._compute_blocking(spec_status)

        assert result.is_blocking is True

    def test_in_progress_with_no_errors_not_blocking(self, tmp_path):
        """Test that IN_PROGRESS specs don't block when validation passes."""
        from doit_cli.models.validation_models import ValidationResult

        spec_status = SpecStatus(
            name="test-spec",
            path=tmp_path / "spec.md",
            status=SpecState.IN_PROGRESS,
            last_modified=datetime.now(),
            validation_result=ValidationResult(
                spec_path=str(tmp_path / "spec.md"),
                issues=[],
            ),
            is_blocking=False,
        )

        (tmp_path / ".doit").mkdir()
        scanner = SpecScanner(tmp_path, validate=False)
        result = scanner._compute_blocking(spec_status)

        assert result.is_blocking is False

    def test_draft_with_errors_not_staged_not_blocking(self, tmp_path, monkeypatch):
        """Test that DRAFT specs don't block when not staged, even with errors."""
        from unittest.mock import Mock
        from doit_cli.models.validation_models import (
            ValidationResult,
            ValidationIssue,
            Severity,
        )

        spec_status = SpecStatus(
            name="test-spec",
            path=tmp_path / "specs" / "test-spec" / "spec.md",
            status=SpecState.DRAFT,
            last_modified=datetime.now(),
            validation_result=ValidationResult(
                spec_path=str(tmp_path / "specs" / "test-spec" / "spec.md"),
                issues=[
                    ValidationIssue(
                        rule_id="test-rule",
                        severity=Severity.ERROR,
                        line_number=1,
                        message="Test error",
                    )
                ],
            ),
            is_blocking=False,
        )

        (tmp_path / ".doit").mkdir()
        scanner = SpecScanner(tmp_path, validate=False)

        # Mock git to return empty (not staged)
        mock_result = Mock(returncode=0, stdout="")
        monkeypatch.setattr("subprocess.run", lambda *args, **kwargs: mock_result)

        result = scanner._compute_blocking(spec_status)

        assert result.is_blocking is False

    def test_draft_with_errors_and_staged_is_blocking(self, tmp_path, monkeypatch):
        """Test that DRAFT specs block when staged with errors."""
        from unittest.mock import Mock
        from doit_cli.models.validation_models import (
            ValidationResult,
            ValidationIssue,
            Severity,
        )

        spec_path = tmp_path / "specs" / "test-spec" / "spec.md"
        spec_status = SpecStatus(
            name="test-spec",
            path=spec_path,
            status=SpecState.DRAFT,
            last_modified=datetime.now(),
            validation_result=ValidationResult(
                spec_path=str(spec_path),
                issues=[
                    ValidationIssue(
                        rule_id="test-rule",
                        severity=Severity.ERROR,
                        line_number=1,
                        message="Test error",
                    )
                ],
            ),
            is_blocking=False,
        )

        (tmp_path / ".doit").mkdir()
        scanner = SpecScanner(tmp_path, validate=False)

        # Mock git to return the spec file as staged
        mock_result = Mock(returncode=0, stdout="specs/test-spec/spec.md\n")
        monkeypatch.setattr("subprocess.run", lambda *args, **kwargs: mock_result)

        result = scanner._compute_blocking(spec_status)

        assert result.is_blocking is True

    def test_complete_spec_never_blocking(self, tmp_path):
        """Test that COMPLETE specs never block regardless of validation."""
        from doit_cli.models.validation_models import (
            ValidationResult,
            ValidationIssue,
            Severity,
        )

        spec_status = SpecStatus(
            name="test-spec",
            path=tmp_path / "spec.md",
            status=SpecState.COMPLETE,
            last_modified=datetime.now(),
            validation_result=ValidationResult(
                spec_path=str(tmp_path / "spec.md"),
                issues=[
                    ValidationIssue(
                        rule_id="test-rule",
                        severity=Severity.ERROR,
                        line_number=1,
                        message="Test error",
                    )
                ],
            ),
            is_blocking=False,
        )

        (tmp_path / ".doit").mkdir()
        scanner = SpecScanner(tmp_path, validate=False)
        result = scanner._compute_blocking(spec_status)

        assert result.is_blocking is False

    def test_approved_spec_never_blocking(self, tmp_path):
        """Test that APPROVED specs never block regardless of validation."""
        from doit_cli.models.validation_models import (
            ValidationResult,
            ValidationIssue,
            Severity,
        )

        spec_status = SpecStatus(
            name="test-spec",
            path=tmp_path / "spec.md",
            status=SpecState.APPROVED,
            last_modified=datetime.now(),
            validation_result=ValidationResult(
                spec_path=str(tmp_path / "spec.md"),
                issues=[
                    ValidationIssue(
                        rule_id="test-rule",
                        severity=Severity.ERROR,
                        line_number=1,
                        message="Test error",
                    )
                ],
            ),
            is_blocking=False,
        )

        (tmp_path / ".doit").mkdir()
        scanner = SpecScanner(tmp_path, validate=False)
        result = scanner._compute_blocking(spec_status)

        assert result.is_blocking is False

    def test_no_validation_result_not_blocking(self, tmp_path):
        """Test that specs without validation results are not blocking."""
        spec_status = SpecStatus(
            name="test-spec",
            path=tmp_path / "spec.md",
            status=SpecState.IN_PROGRESS,
            last_modified=datetime.now(),
            validation_result=None,
            is_blocking=False,
        )

        (tmp_path / ".doit").mkdir()
        scanner = SpecScanner(tmp_path, validate=False)
        result = scanner._compute_blocking(spec_status)

        assert result.is_blocking is False

    def test_spec_with_error_field_not_blocking(self, tmp_path):
        """Test that specs with error field set skip blocking computation."""
        spec_status = SpecStatus(
            name="test-spec",
            path=tmp_path / "spec.md",
            status=SpecState.IN_PROGRESS,
            last_modified=datetime.now(),
            validation_result=None,
            is_blocking=False,
            error="Unable to read file",
        )

        (tmp_path / ".doit").mkdir()
        scanner = SpecScanner(tmp_path, validate=False)
        # _add_validation returns early for specs with errors
        result = scanner._add_validation(spec_status)

        assert result.error == "Unable to read file"


class TestGitStaged:
    """Tests for git staging detection."""

    def test_git_staged_when_file_in_output(self, tmp_path, monkeypatch):
        """Test detection when file is in git staged output."""
        from unittest.mock import Mock

        (tmp_path / ".doit").mkdir()
        scanner = SpecScanner(tmp_path, validate=False)

        spec_path = tmp_path / "specs" / "001-test" / "spec.md"

        mock_result = Mock(returncode=0, stdout="specs/001-test/spec.md\nother/file.txt\n")
        monkeypatch.setattr("subprocess.run", lambda *args, **kwargs: mock_result)

        result = scanner._is_git_staged(spec_path)

        assert result is True

    def test_git_not_staged_when_file_not_in_output(self, tmp_path, monkeypatch):
        """Test detection when file is not in git staged output."""
        from unittest.mock import Mock

        (tmp_path / ".doit").mkdir()
        scanner = SpecScanner(tmp_path, validate=False)

        spec_path = tmp_path / "specs" / "001-test" / "spec.md"

        mock_result = Mock(returncode=0, stdout="other/file.txt\n")
        monkeypatch.setattr("subprocess.run", lambda *args, **kwargs: mock_result)

        result = scanner._is_git_staged(spec_path)

        assert result is False

    def test_git_command_fails_returns_false(self, tmp_path, monkeypatch):
        """Test that git command failure returns False (safe default)."""
        from unittest.mock import Mock

        (tmp_path / ".doit").mkdir()
        scanner = SpecScanner(tmp_path, validate=False)

        spec_path = tmp_path / "specs" / "001-test" / "spec.md"

        mock_result = Mock(returncode=1, stdout="")
        monkeypatch.setattr("subprocess.run", lambda *args, **kwargs: mock_result)

        result = scanner._is_git_staged(spec_path)

        assert result is False

    def test_git_not_available_returns_false(self, tmp_path, monkeypatch):
        """Test that missing git command returns False (safe default)."""
        (tmp_path / ".doit").mkdir()
        scanner = SpecScanner(tmp_path, validate=False)

        spec_path = tmp_path / "specs" / "001-test" / "spec.md"

        def raise_error(*args, **kwargs):
            raise FileNotFoundError("git not found")

        monkeypatch.setattr("subprocess.run", raise_error)

        result = scanner._is_git_staged(spec_path)

        assert result is False
