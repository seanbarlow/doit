"""Integration tests for hooks CLI commands."""

import subprocess
import pytest
from pathlib import Path


class TestHooksCommandIntegration:
    """Integration tests for doit hooks commands."""

    @pytest.fixture
    def git_repo(self, tmp_path: Path):
        """Create a temporary git repository."""
        # Initialize git repo
        subprocess.run(
            ["git", "init"],
            cwd=tmp_path,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=tmp_path,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=tmp_path,
            capture_output=True,
        )
        return tmp_path

    def test_hooks_install_in_git_repo(self, git_repo: Path):
        """Test hooks install succeeds in git repo."""
        result = subprocess.run(
            ["doit", "hooks", "install"],
            cwd=git_repo,
            capture_output=True,
            text=True,
        )

        # Should succeed or indicate hooks installed
        assert result.returncode == 0 or "installed" in result.stdout.lower()

    def test_hooks_install_not_git_repo(self, tmp_path: Path):
        """Test hooks install fails outside git repo."""
        result = subprocess.run(
            ["doit", "hooks", "install"],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0
        assert "not a git repository" in result.stdout.lower()

    def test_hooks_status_shows_info(self, git_repo: Path):
        """Test hooks status shows installation info."""
        result = subprocess.run(
            ["doit", "hooks", "status"],
            cwd=git_repo,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "git hooks status" in result.stdout.lower()

    def test_hooks_uninstall_removes_hooks(self, git_repo: Path):
        """Test hooks uninstall removes installed hooks."""
        # First install
        subprocess.run(
            ["doit", "hooks", "install"],
            cwd=git_repo,
            capture_output=True,
        )

        # Then uninstall
        result = subprocess.run(
            ["doit", "hooks", "uninstall"],
            cwd=git_repo,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0

    def test_hooks_validate_pre_commit_on_main(self, git_repo: Path):
        """Test pre-commit validation passes on main branch."""
        result = subprocess.run(
            ["doit", "hooks", "validate", "pre-commit"],
            cwd=git_repo,
            capture_output=True,
            text=True,
        )

        # Should pass on main/master (default branch after git init)
        assert result.returncode == 0

    def test_hooks_report_empty(self, git_repo: Path):
        """Test hooks report with no bypasses."""
        result = subprocess.run(
            ["doit", "hooks", "report"],
            cwd=git_repo,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "no bypass events" in result.stdout.lower()

    def test_hooks_help(self):
        """Test hooks help shows available commands."""
        result = subprocess.run(
            ["doit", "hooks", "--help"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "install" in result.stdout.lower()
        assert "uninstall" in result.stdout.lower()
        assert "status" in result.stdout.lower()


class TestHooksValidationIntegration:
    """Integration tests for hook validation logic."""

    @pytest.fixture
    def feature_branch_repo(self, tmp_path: Path):
        """Create a git repo with feature branch."""
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=tmp_path,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=tmp_path,
            capture_output=True,
        )

        # Create initial commit on main
        readme = tmp_path / "README.md"
        readme.write_text("# Test Project")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=tmp_path,
            capture_output=True,
        )

        # Create feature branch
        subprocess.run(
            ["git", "checkout", "-b", "025-test-feature"],
            cwd=tmp_path,
            capture_output=True,
        )

        return tmp_path

    def test_validation_fails_without_spec(self, feature_branch_repo: Path):
        """Test validation fails on feature branch without spec."""
        # Add a code file
        code_file = feature_branch_repo / "main.py"
        code_file.write_text("print('hello')")
        subprocess.run(
            ["git", "add", "main.py"],
            cwd=feature_branch_repo,
            capture_output=True,
        )

        result = subprocess.run(
            ["doit", "hooks", "validate", "pre-commit"],
            cwd=feature_branch_repo,
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0
        assert "missing specification" in result.stdout.lower()

    def test_validation_passes_with_spec(self, feature_branch_repo: Path):
        """Test validation passes on feature branch with valid spec."""
        # Create specs directory and spec.md with all required sections
        spec_dir = feature_branch_repo / "specs" / "025-test-feature"
        spec_dir.mkdir(parents=True)
        spec_file = spec_dir / "spec.md"
        spec_content = """# Feature: Test Feature

**Status**: In Progress
**Feature Branch**: `025-test-feature`

## User Scenarios

### User Story 1: Basic Test

As a user, I want to test the feature.

- **Given** I have setup **When** I perform action **Then** I see result

## Requirements

- **FR-001**: First requirement
- **FR-002**: Second requirement

## Success Criteria

- **SC-001**: First criterion
- **SC-002**: Second criterion
"""
        spec_file.write_text(spec_content)

        # Add a code file
        code_file = feature_branch_repo / "main.py"
        code_file.write_text("print('hello')")
        subprocess.run(
            ["git", "add", "."],
            cwd=feature_branch_repo,
            capture_output=True,
        )

        result = subprocess.run(
            ["doit", "hooks", "validate", "pre-commit"],
            cwd=feature_branch_repo,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0

    def test_validation_fails_with_draft_spec(self, feature_branch_repo: Path):
        """Test validation fails with Draft status spec."""
        # Create specs directory and spec.md with Draft status
        spec_dir = feature_branch_repo / "specs" / "025-test-feature"
        spec_dir.mkdir(parents=True)
        spec_file = spec_dir / "spec.md"
        spec_file.write_text("# Test Feature\n\n**Status**: Draft\n\n## Summary")

        # Add a code file
        code_file = feature_branch_repo / "main.py"
        code_file.write_text("print('hello')")
        subprocess.run(
            ["git", "add", "."],
            cwd=feature_branch_repo,
            capture_output=True,
        )

        result = subprocess.run(
            ["doit", "hooks", "validate", "pre-commit"],
            cwd=feature_branch_repo,
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0
        assert "invalid status" in result.stdout.lower()
