"""Hook validation service for workflow enforcement."""

import fnmatch
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..models.hook_config import HookConfig


class ValidationResult:
    """Result of a hook validation check."""

    def __init__(
        self,
        success: bool,
        message: str = "",
        suggestion: str = "",
    ):
        self.success = success
        self.message = message
        self.suggestion = suggestion

    def __bool__(self) -> bool:
        return self.success


class HookValidator:
    """Validates workflow compliance for Git hooks."""

    # Regex pattern for feature branch naming (e.g., 025-feature-name)
    BRANCH_PATTERN = re.compile(r"^(\d{3})-(.+)$")

    # Protected branches that skip validation
    DEFAULT_PROTECTED_BRANCHES = ["main", "develop", "master"]

    # Allowed spec statuses for code commits
    ALLOWED_SPEC_STATUSES = ["In Progress", "Complete", "Approved"]

    def __init__(
        self,
        project_root: Optional[Path] = None,
        config: Optional[HookConfig] = None,
    ):
        """Initialize the validator.

        Args:
            project_root: Root directory of the project (defaults to cwd)
            config: Hook configuration (loads from file if not provided)
        """
        self.project_root = project_root or Path.cwd()
        self.config = config or self._load_config()
        self.specs_dir = self.project_root / "specs"
        self.logs_dir = self.project_root / ".doit" / "logs"

    def _load_config(self) -> HookConfig:
        """Load configuration from file or return defaults."""
        config_path = self.project_root / ".doit" / "config" / "hooks.yaml"
        if config_path.exists():
            return HookConfig.load_from_file(config_path)
        return HookConfig.load_default()

    def get_current_branch(self) -> Optional[str]:
        """Get the current Git branch name.

        Returns:
            Branch name or None if not on a branch (detached HEAD)
        """
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )
            if result.returncode == 0:
                branch = result.stdout.strip()
                if branch == "HEAD":
                    return None  # Detached HEAD state
                return branch
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
        return None

    def get_staged_files(self) -> list[str]:
        """Get list of staged files for commit.

        Returns:
            List of staged file paths relative to project root
        """
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )
            if result.returncode == 0:
                return [f for f in result.stdout.strip().split("\n") if f]
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
        return []

    def is_protected_branch(self, branch: str) -> bool:
        """Check if branch is protected (skip validation).

        Args:
            branch: Branch name to check

        Returns:
            True if branch should skip validation
        """
        # Check default protected branches
        if branch in self.DEFAULT_PROTECTED_BRANCHES:
            return True

        # Check configured exempt branches
        exempt = self.config.pre_commit.exempt_branches
        for pattern in exempt:
            if fnmatch.fnmatch(branch, pattern):
                return True

        return False

    def is_exempt_path(self, file_path: str) -> bool:
        """Check if file path is exempt from validation.

        Args:
            file_path: File path to check

        Returns:
            True if file should skip validation
        """
        exempt = self.config.pre_commit.exempt_paths
        for pattern in exempt:
            if fnmatch.fnmatch(file_path, pattern):
                return True
        return False

    def all_files_exempt(self, files: list[str]) -> bool:
        """Check if all staged files are exempt from validation.

        Args:
            files: List of file paths

        Returns:
            True if all files match exempt patterns
        """
        if not files:
            return True
        return all(self.is_exempt_path(f) for f in files)

    def extract_branch_spec_name(self, branch: str) -> Optional[str]:
        """Extract spec directory name from branch name.

        Args:
            branch: Git branch name

        Returns:
            Spec directory name or None if pattern doesn't match
        """
        match = self.BRANCH_PATTERN.match(branch)
        if match:
            return branch  # Full branch name is the spec directory
        return None

    def get_spec_path(self, branch: str) -> Optional[Path]:
        """Get the expected spec.md path for a branch.

        Args:
            branch: Git branch name

        Returns:
            Path to expected spec.md or None if branch pattern doesn't match
        """
        spec_name = self.extract_branch_spec_name(branch)
        if spec_name:
            return self.specs_dir / spec_name / "spec.md"
        return None

    def spec_exists(self, branch: str) -> bool:
        """Check if spec.md exists for the branch.

        Args:
            branch: Git branch name

        Returns:
            True if spec.md exists
        """
        spec_path = self.get_spec_path(branch)
        return spec_path is not None and spec_path.exists()

    def get_spec_status(self, branch: str) -> Optional[str]:
        """Get the status field from spec.md.

        Args:
            branch: Git branch name

        Returns:
            Status string or None if not found
        """
        spec_path = self.get_spec_path(branch)
        if not spec_path or not spec_path.exists():
            return None

        try:
            content = spec_path.read_text()
            # Look for **Status**: value pattern
            match = re.search(r"\*\*Status\*\*:\s*(\w+(?:\s+\w+)*)", content)
            if match:
                return match.group(1).strip()
        except (OSError, IOError):
            pass
        return None

    def is_spec_status_valid(self, status: Optional[str]) -> bool:
        """Check if spec status allows code commits.

        Args:
            status: Spec status string

        Returns:
            True if status allows code commits
        """
        if status is None:
            return False

        # Check configured allowed statuses or use defaults
        allowed = self.config.pre_commit.allowed_statuses
        if allowed:
            return status in allowed
        return status in self.ALLOWED_SPEC_STATUSES

    def has_code_changes(self, files: list[str]) -> bool:
        """Check if staged files include code (not just spec/docs).

        Args:
            files: List of staged file paths

        Returns:
            True if any file is not a spec/doc file
        """
        spec_doc_patterns = ["specs/**", "docs/**", "*.md", ".github/**"]
        for f in files:
            is_spec_doc = any(fnmatch.fnmatch(f, p) for p in spec_doc_patterns)
            if not is_spec_doc:
                return True
        return False

    def validate_pre_commit(self) -> ValidationResult:
        """Validate pre-commit hook requirements.

        Returns:
            ValidationResult with success status and messages
        """
        # Check if pre-commit validation is enabled
        if not self.config.pre_commit.enabled:
            return ValidationResult(True, "Pre-commit validation disabled")

        # Get current branch
        branch = self.get_current_branch()
        if branch is None:
            return ValidationResult(
                True,
                "Detached HEAD state - skipping validation",
            )

        # Check if protected branch
        if self.is_protected_branch(branch):
            return ValidationResult(
                True,
                f"Protected branch '{branch}' - skipping validation",
            )

        # Get staged files
        staged_files = self.get_staged_files()

        # Check if all files are exempt
        if self.all_files_exempt(staged_files):
            return ValidationResult(
                True,
                "All staged files match exempt patterns - skipping validation",
            )

        # Check if require_spec is enabled
        if not self.config.pre_commit.require_spec:
            return ValidationResult(True, "Spec requirement disabled")

        # Extract spec name from branch
        spec_name = self.extract_branch_spec_name(branch)
        if spec_name is None:
            # Branch doesn't follow naming convention - warn but allow
            return ValidationResult(
                True,
                f"Branch '{branch}' doesn't follow naming convention (###-feature-name)",
                "Consider using standard branch naming for better workflow tracking",
            )

        # Check if spec exists
        spec_path = self.get_spec_path(branch)
        if not self.spec_exists(branch):
            return ValidationResult(
                False,
                f"Missing specification for branch: {branch}",
                f"Expected: {spec_path}\n\nTo fix: Run `doit specit \"Your feature description\"` first\n\nOr bypass with: git commit --no-verify (not recommended)",
            )

        # Check spec status for code changes
        if self.has_code_changes(staged_files):
            status = self.get_spec_status(branch)
            if not self.is_spec_status_valid(status):
                allowed = self.config.pre_commit.allowed_statuses or self.ALLOWED_SPEC_STATUSES
                return ValidationResult(
                    False,
                    f"Specification has invalid status: {status or 'Unknown'}",
                    f"Allowed statuses: {', '.join(allowed)}\n\nTo fix: Update spec.md status to 'In Progress' before committing code",
                )

        # Run spec validation if enabled
        if self.config.pre_commit.validate_spec:
            validation_result = self._validate_spec_quality(spec_path)
            if not validation_result.success:
                return validation_result

        return ValidationResult(True, "Pre-commit validation passed")

    def _validate_spec_quality(self, spec_path: Path) -> ValidationResult:
        """Validate spec quality using validation rules.

        Args:
            spec_path: Path to the spec.md file.

        Returns:
            ValidationResult with success status and messages.
        """
        try:
            from .validation_service import ValidationService

            service = ValidationService()
            result = service.validate_file(spec_path)

            threshold = self.config.pre_commit.validate_spec_threshold

            if result.error_count > 0:
                # Format issues summary
                issues_summary = []
                for issue in result.issues:
                    if issue.severity.value == "error":
                        issues_summary.append(f"  - {issue.message}")

                return ValidationResult(
                    False,
                    f"Specification validation failed with {result.error_count} error(s)\n\n"
                    + "\n".join(issues_summary[:5])  # Show first 5 errors
                    + (f"\n  ... and {result.error_count - 5} more" if result.error_count > 5 else ""),
                    f"Quality score: {result.quality_score}/100 (threshold: {threshold})\n\n"
                    f"To fix: Run `doit validate {spec_path}` to see all issues\n\n"
                    "Or bypass with: git commit --no-verify (not recommended)",
                )

            if result.quality_score < threshold:
                return ValidationResult(
                    False,
                    f"Specification quality score ({result.quality_score}) below threshold ({threshold})",
                    f"Warnings: {result.warning_count}\n\n"
                    f"To fix: Run `doit validate {spec_path}` to see issues and improve the spec\n\n"
                    "Or bypass with: git commit --no-verify (not recommended)",
                )

        except ImportError:
            # ValidationService not available - skip validation
            pass
        except Exception as e:
            # Log error but don't block commit for validation failures
            pass

        return ValidationResult(True, "Spec validation passed")

    def validate_pre_push(self) -> ValidationResult:
        """Validate pre-push hook requirements.

        Returns:
            ValidationResult with success status and messages
        """
        # Check if pre-push validation is enabled
        if not self.config.pre_push.enabled:
            return ValidationResult(True, "Pre-push validation disabled")

        # Get current branch
        branch = self.get_current_branch()
        if branch is None:
            return ValidationResult(
                True,
                "Detached HEAD state - skipping validation",
            )

        # Check if protected branch
        if self.is_protected_branch(branch):
            return ValidationResult(
                True,
                f"Protected branch '{branch}' - skipping validation",
            )

        # Extract spec name from branch
        spec_name = self.extract_branch_spec_name(branch)
        if spec_name is None:
            return ValidationResult(
                True,
                f"Branch '{branch}' doesn't follow naming convention",
            )

        # Check for required artifacts
        spec_dir = self.specs_dir / spec_name

        # Check spec.md
        if self.config.pre_push.require_spec:
            spec_path = spec_dir / "spec.md"
            if not spec_path.exists():
                return ValidationResult(
                    False,
                    f"Missing required artifact: spec.md",
                    f"Expected: {spec_path}\n\nTo fix: Run `doit specit \"Your feature description\"` first",
                )

        # Check plan.md
        if self.config.pre_push.require_plan:
            plan_path = spec_dir / "plan.md"
            if not plan_path.exists():
                return ValidationResult(
                    False,
                    f"Missing required artifact: plan.md",
                    f"Expected: {plan_path}\n\nTo fix: Run `/doit.planit` to create implementation plan",
                )

        # Check tasks.md
        if self.config.pre_push.require_tasks:
            tasks_path = spec_dir / "tasks.md"
            if not tasks_path.exists():
                return ValidationResult(
                    False,
                    f"Missing required artifact: tasks.md",
                    f"Expected: {tasks_path}\n\nTo fix: Run `/doit.taskit` to generate task breakdown",
                )

        return ValidationResult(True, "Pre-push validation passed")

    def log_bypass(self, hook_type: str, commit_hash: Optional[str] = None) -> None:
        """Log a hook bypass event.

        Args:
            hook_type: Type of hook that was bypassed (pre-commit, pre-push)
            commit_hash: Optional commit hash for post-commit logging
        """
        if not self.config.logging.log_bypasses:
            return

        self.logs_dir.mkdir(parents=True, exist_ok=True)
        log_path = self.logs_dir / "hook-bypasses.log"

        # Get context
        branch = self.get_current_branch() or "unknown"
        user = self._get_git_user()
        timestamp = datetime.now().isoformat(timespec="seconds")

        # Format log entry
        entry = f"{timestamp} | hook: {hook_type} | branch: {branch}"
        if commit_hash:
            entry += f" | commit: {commit_hash}"
        if user:
            entry += f" | user: {user}"
        entry += "\n"

        # Append to log
        with open(log_path, "a") as f:
            f.write(entry)

    def _get_git_user(self) -> Optional[str]:
        """Get the current Git user email."""
        try:
            result = subprocess.run(
                ["git", "config", "user.email"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
        return None

    def get_bypass_report(self) -> list[dict]:
        """Get bypass events from the log.

        Returns:
            List of bypass event dictionaries
        """
        log_path = self.logs_dir / "hook-bypasses.log"
        if not log_path.exists():
            return []

        events = []
        try:
            with open(log_path) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    # Parse log entry
                    event = {}
                    parts = line.split(" | ")
                    for part in parts:
                        if ": " in part:
                            key, value = part.split(": ", 1)
                            event[key] = value
                        else:
                            # First part is timestamp
                            event["timestamp"] = part

                    events.append(event)
        except (OSError, IOError):
            pass

        return events
