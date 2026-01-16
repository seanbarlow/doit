"""Unit tests for HookValidator service."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from doit_cli.services.hook_validator import HookValidator, ValidationResult
from doit_cli.models.hook_config import HookConfig, HookRule


class TestValidationResult:
    """Tests for ValidationResult class."""

    def test_success_result_is_truthy(self):
        """Test that successful result is truthy."""
        result = ValidationResult(True, "Success message")
        assert result
        assert result.success is True

    def test_failure_result_is_falsy(self):
        """Test that failed result is falsy."""
        result = ValidationResult(False, "Error message")
        assert not result
        assert result.success is False

    def test_result_stores_message_and_suggestion(self):
        """Test that result stores message and suggestion."""
        result = ValidationResult(False, "Error", "Fix suggestion")
        assert result.message == "Error"
        assert result.suggestion == "Fix suggestion"


class TestHookValidatorBranchParsing:
    """Tests for branch name parsing."""

    def test_extract_branch_spec_name_valid(self, tmp_path: Path):
        """Test extracting spec name from valid branch."""
        validator = HookValidator(project_root=tmp_path)
        assert validator.extract_branch_spec_name("025-feature-name") == "025-feature-name"
        assert validator.extract_branch_spec_name("001-init") == "001-init"

    def test_extract_branch_spec_name_invalid(self, tmp_path: Path):
        """Test extracting spec name from invalid branch."""
        validator = HookValidator(project_root=tmp_path)
        assert validator.extract_branch_spec_name("feature-no-number") is None
        assert validator.extract_branch_spec_name("main") is None
        assert validator.extract_branch_spec_name("develop") is None

    def test_is_protected_branch_default(self, tmp_path: Path):
        """Test default protected branches."""
        validator = HookValidator(project_root=tmp_path)
        assert validator.is_protected_branch("main") is True
        assert validator.is_protected_branch("develop") is True
        assert validator.is_protected_branch("master") is True
        assert validator.is_protected_branch("feature") is False

    def test_is_protected_branch_with_patterns(self, tmp_path: Path):
        """Test protected branches with glob patterns."""
        config = HookConfig.load_default()
        config.pre_commit.exempt_branches = ["hotfix/*", "bugfix/*"]
        validator = HookValidator(project_root=tmp_path, config=config)

        assert validator.is_protected_branch("hotfix/urgent") is True
        assert validator.is_protected_branch("bugfix/issue-123") is True
        assert validator.is_protected_branch("feature/new") is False


class TestHookValidatorPathExemption:
    """Tests for path exemption logic."""

    def test_is_exempt_path_matches(self, tmp_path: Path):
        """Test exempt path matching."""
        config = HookConfig.load_default()
        config.pre_commit.exempt_paths = ["docs/**", "*.md", ".github/**"]
        validator = HookValidator(project_root=tmp_path, config=config)

        assert validator.is_exempt_path("docs/readme.md") is True
        assert validator.is_exempt_path("README.md") is True
        assert validator.is_exempt_path(".github/workflows/ci.yml") is True
        assert validator.is_exempt_path("src/main.py") is False

    def test_all_files_exempt_true(self, tmp_path: Path):
        """Test all files exempt returns True."""
        config = HookConfig.load_default()
        config.pre_commit.exempt_paths = ["docs/**", "*.md"]
        validator = HookValidator(project_root=tmp_path, config=config)

        files = ["docs/guide.md", "README.md", "CHANGELOG.md"]
        assert validator.all_files_exempt(files) is True

    def test_all_files_exempt_false(self, tmp_path: Path):
        """Test all files exempt returns False when code included."""
        config = HookConfig.load_default()
        config.pre_commit.exempt_paths = ["docs/**", "*.md"]
        validator = HookValidator(project_root=tmp_path, config=config)

        files = ["docs/guide.md", "src/main.py"]
        assert validator.all_files_exempt(files) is False

    def test_all_files_exempt_empty_list(self, tmp_path: Path):
        """Test empty file list returns True."""
        validator = HookValidator(project_root=tmp_path)
        assert validator.all_files_exempt([]) is True


class TestHookValidatorSpecChecks:
    """Tests for spec file validation."""

    def test_spec_exists_true(self, tmp_path: Path):
        """Test spec_exists returns True when spec exists."""
        # Create spec directory and file
        spec_dir = tmp_path / "specs" / "025-feature"
        spec_dir.mkdir(parents=True)
        (spec_dir / "spec.md").write_text("# Spec\n**Status**: In Progress")

        validator = HookValidator(project_root=tmp_path)
        assert validator.spec_exists("025-feature") is True

    def test_spec_exists_false(self, tmp_path: Path):
        """Test spec_exists returns False when spec missing."""
        validator = HookValidator(project_root=tmp_path)
        assert validator.spec_exists("025-feature") is False

    def test_get_spec_status(self, tmp_path: Path):
        """Test extracting status from spec file."""
        spec_dir = tmp_path / "specs" / "025-feature"
        spec_dir.mkdir(parents=True)
        (spec_dir / "spec.md").write_text(
            "# Feature Spec\n\n**Status**: In Progress\n\n## Summary"
        )

        validator = HookValidator(project_root=tmp_path)
        assert validator.get_spec_status("025-feature") == "In Progress"

    def test_get_spec_status_draft(self, tmp_path: Path):
        """Test extracting Draft status."""
        spec_dir = tmp_path / "specs" / "025-feature"
        spec_dir.mkdir(parents=True)
        (spec_dir / "spec.md").write_text("# Spec\n\n**Status**: Draft")

        validator = HookValidator(project_root=tmp_path)
        assert validator.get_spec_status("025-feature") == "Draft"

    def test_is_spec_status_valid(self, tmp_path: Path):
        """Test spec status validation."""
        validator = HookValidator(project_root=tmp_path)

        assert validator.is_spec_status_valid("In Progress") is True
        assert validator.is_spec_status_valid("Complete") is True
        assert validator.is_spec_status_valid("Approved") is True
        assert validator.is_spec_status_valid("Draft") is False
        assert validator.is_spec_status_valid(None) is False

    def test_has_code_changes_true(self, tmp_path: Path):
        """Test has_code_changes detects code files."""
        validator = HookValidator(project_root=tmp_path)
        files = ["src/main.py", "specs/025/spec.md"]
        assert validator.has_code_changes(files) is True

    def test_has_code_changes_false(self, tmp_path: Path):
        """Test has_code_changes returns False for docs only."""
        validator = HookValidator(project_root=tmp_path)
        files = ["specs/025/spec.md", "docs/guide.md", "README.md"]
        assert validator.has_code_changes(files) is False


class TestPreCommitValidation:
    """Tests for pre-commit validation logic."""

    def test_validation_disabled(self, tmp_path: Path):
        """Test validation passes when disabled."""
        config = HookConfig.load_default()
        config.pre_commit.enabled = False
        validator = HookValidator(project_root=tmp_path, config=config)

        result = validator.validate_pre_commit()
        assert result.success is True
        assert "disabled" in result.message.lower()

    def test_protected_branch_skips(self, tmp_path: Path):
        """Test protected branch skips validation."""
        validator = HookValidator(project_root=tmp_path)

        with patch.object(validator, "get_current_branch", return_value="main"):
            result = validator.validate_pre_commit()
            assert result.success is True
            assert "protected" in result.message.lower()

    def test_detached_head_skips(self, tmp_path: Path):
        """Test detached HEAD skips validation."""
        validator = HookValidator(project_root=tmp_path)

        with patch.object(validator, "get_current_branch", return_value=None):
            result = validator.validate_pre_commit()
            assert result.success is True
            assert "detached" in result.message.lower()

    def test_all_exempt_files_skips(self, tmp_path: Path):
        """Test all exempt files skips validation."""
        config = HookConfig.load_default()
        config.pre_commit.exempt_paths = ["*.md"]
        config.pre_commit.exempt_branches = []  # Clear defaults
        validator = HookValidator(project_root=tmp_path, config=config)

        with patch.object(validator, "get_current_branch", return_value="025-feature"):
            with patch.object(validator, "get_staged_files", return_value=["README.md"]):
                result = validator.validate_pre_commit()
                assert result.success is True
                assert "exempt" in result.message.lower()

    def test_missing_spec_fails(self, tmp_path: Path):
        """Test missing spec fails validation."""
        validator = HookValidator(project_root=tmp_path)

        with patch.object(validator, "get_current_branch", return_value="025-feature"):
            with patch.object(validator, "get_staged_files", return_value=["src/main.py"]):
                result = validator.validate_pre_commit()
                assert result.success is False
                assert "missing specification" in result.message.lower()

    def test_draft_spec_with_code_fails(self, tmp_path: Path):
        """Test draft spec with code changes fails."""
        # Create spec with Draft status
        spec_dir = tmp_path / "specs" / "025-feature"
        spec_dir.mkdir(parents=True)
        (spec_dir / "spec.md").write_text("# Spec\n\n**Status**: Draft")

        validator = HookValidator(project_root=tmp_path)

        with patch.object(validator, "get_current_branch", return_value="025-feature"):
            with patch.object(validator, "get_staged_files", return_value=["src/main.py"]):
                result = validator.validate_pre_commit()
                assert result.success is False
                assert "invalid status" in result.message.lower()

    def test_valid_spec_passes(self, tmp_path: Path):
        """Test valid spec passes validation."""
        # Create spec with valid status
        spec_dir = tmp_path / "specs" / "025-feature"
        spec_dir.mkdir(parents=True)
        (spec_dir / "spec.md").write_text("# Spec\n\n**Status**: In Progress")

        # Disable spec quality validation for this test (testing status check only)
        config = HookConfig(
            pre_commit=HookRule(
                enabled=True,
                require_spec=True,
                validate_spec=False,  # Disable quality validation for this test
            )
        )
        validator = HookValidator(project_root=tmp_path, config=config)

        with patch.object(validator, "get_current_branch", return_value="025-feature"):
            with patch.object(validator, "get_staged_files", return_value=["src/main.py"]):
                result = validator.validate_pre_commit()
                assert result.success is True


class TestPrePushValidation:
    """Tests for pre-push validation logic."""

    def test_validation_disabled(self, tmp_path: Path):
        """Test validation passes when disabled."""
        config = HookConfig.load_default()
        config.pre_push.enabled = False
        validator = HookValidator(project_root=tmp_path, config=config)

        result = validator.validate_pre_push()
        assert result.success is True

    def test_missing_plan_fails(self, tmp_path: Path):
        """Test missing plan.md fails when required."""
        # Create spec but not plan
        spec_dir = tmp_path / "specs" / "025-feature"
        spec_dir.mkdir(parents=True)
        (spec_dir / "spec.md").write_text("# Spec")

        config = HookConfig.load_default()
        config.pre_push.require_spec = True
        config.pre_push.require_plan = True
        validator = HookValidator(project_root=tmp_path, config=config)

        with patch.object(validator, "get_current_branch", return_value="025-feature"):
            result = validator.validate_pre_push()
            assert result.success is False
            assert "plan.md" in result.message.lower()

    def test_all_artifacts_present_passes(self, tmp_path: Path):
        """Test all required artifacts passes."""
        # Create all artifacts
        spec_dir = tmp_path / "specs" / "025-feature"
        spec_dir.mkdir(parents=True)
        (spec_dir / "spec.md").write_text("# Spec")
        (spec_dir / "plan.md").write_text("# Plan")
        (spec_dir / "tasks.md").write_text("# Tasks")

        config = HookConfig.load_default()
        config.pre_push.require_spec = True
        config.pre_push.require_plan = True
        config.pre_push.require_tasks = True
        validator = HookValidator(project_root=tmp_path, config=config)

        with patch.object(validator, "get_current_branch", return_value="025-feature"):
            result = validator.validate_pre_push()
            assert result.success is True


class TestBypassLogging:
    """Tests for bypass logging functionality."""

    def test_log_bypass_creates_log(self, tmp_path: Path):
        """Test log_bypass creates log file."""
        validator = HookValidator(project_root=tmp_path)

        with patch.object(validator, "get_current_branch", return_value="025-feature"):
            with patch.object(validator, "_get_git_user", return_value="dev@test.com"):
                validator.log_bypass("pre-commit")

        log_path = tmp_path / ".doit" / "logs" / "hook-bypasses.log"
        assert log_path.exists()

        content = log_path.read_text()
        assert "pre-commit" in content
        assert "025-feature" in content
        assert "dev@test.com" in content

    def test_log_bypass_appends(self, tmp_path: Path):
        """Test log_bypass appends to existing log."""
        # Create existing log
        log_dir = tmp_path / ".doit" / "logs"
        log_dir.mkdir(parents=True)
        log_path = log_dir / "hook-bypasses.log"
        log_path.write_text("existing entry\n")

        validator = HookValidator(project_root=tmp_path)

        with patch.object(validator, "get_current_branch", return_value="025-feature"):
            with patch.object(validator, "_get_git_user", return_value="dev@test.com"):
                validator.log_bypass("pre-commit")

        content = log_path.read_text()
        assert "existing entry" in content
        assert "pre-commit" in content

    def test_log_bypass_disabled(self, tmp_path: Path):
        """Test log_bypass does nothing when disabled."""
        config = HookConfig.load_default()
        config.logging.log_bypasses = False
        validator = HookValidator(project_root=tmp_path, config=config)

        validator.log_bypass("pre-commit")

        log_path = tmp_path / ".doit" / "logs" / "hook-bypasses.log"
        assert not log_path.exists()

    def test_get_bypass_report(self, tmp_path: Path):
        """Test get_bypass_report parses log."""
        # Create log with entries
        log_dir = tmp_path / ".doit" / "logs"
        log_dir.mkdir(parents=True)
        log_path = log_dir / "hook-bypasses.log"
        log_path.write_text(
            "2026-01-15T10:00:00 | hook: pre-commit | branch: 025-feature | user: dev@test.com\n"
            "2026-01-15T11:00:00 | hook: pre-push | branch: 026-other | user: other@test.com\n"
        )

        validator = HookValidator(project_root=tmp_path)
        events = validator.get_bypass_report()

        assert len(events) == 2
        assert events[0]["hook"] == "pre-commit"
        assert events[0]["branch"] == "025-feature"
        assert events[1]["hook"] == "pre-push"

    def test_get_bypass_report_empty(self, tmp_path: Path):
        """Test get_bypass_report with no log file."""
        validator = HookValidator(project_root=tmp_path)
        events = validator.get_bypass_report()
        assert events == []
