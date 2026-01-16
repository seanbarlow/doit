"""Spec scanner service for discovering and parsing spec metadata."""

import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..models.status_models import SpecState, SpecStatus, StatusReport
from ..models.validation_models import ValidationResult


class NotADoitProjectError(Exception):
    """Raised when project_root lacks .doit/ directory."""

    pass


class SpecNotFoundError(Exception):
    """Raised when a spec directory doesn't exist."""

    pass


class SpecScanner:
    """Scans specs directory and parses spec metadata.

    This service discovers all specification directories in a project,
    parses their status from spec.md frontmatter, and returns structured
    SpecStatus objects for each spec found.
    """

    # Regex pattern to extract status from spec.md
    # Matches: **Status**: Draft (or In Progress, Complete, Approved)
    STATUS_PATTERN = re.compile(
        r"\*\*Status\*\*:\s*([A-Za-z]+(?:\s+[A-Za-z]+)?)", re.IGNORECASE
    )

    # Default specs directory name
    SPECS_DIR = "specs"

    def __init__(
        self,
        project_root: Optional[Path] = None,
        validate: bool = True,
    ) -> None:
        """Initialize scanner with project root directory.

        Args:
            project_root: Root directory of the doit project.
                         Defaults to current working directory.
            validate: Whether to run validation on specs.

        Raises:
            NotADoitProjectError: If project_root lacks .doit/ directory.
        """
        self.project_root = project_root or Path.cwd()
        self.validate = validate
        self._validator = None

        # Validate this is a doit project
        doit_dir = self.project_root / ".doit"
        if not doit_dir.exists():
            raise NotADoitProjectError(
                f"Not a doit project. Run 'doit init' first. "
                f"(Missing .doit/ directory in {self.project_root})"
            )

    @property
    def validator(self):
        """Lazy-load the ValidationService."""
        if self._validator is None and self.validate:
            try:
                from .validation_service import ValidationService

                self._validator = ValidationService(self.project_root)
            except ImportError:
                # Validation service not available
                self._validator = None
        return self._validator

    def scan(self, include_validation: bool = True) -> list[SpecStatus]:
        """Scan specs/ directory and return all spec statuses.

        Discovers all subdirectories in specs/ that contain a spec.md file
        and parses their metadata.

        Args:
            include_validation: Whether to include validation results.

        Returns:
            List of SpecStatus objects, one per spec directory.
            Sorted by spec name alphabetically.
        """
        specs_dir = self.project_root / self.SPECS_DIR

        if not specs_dir.exists():
            return []

        statuses: list[SpecStatus] = []

        # Find all spec.md files in subdirectories
        for spec_file in sorted(specs_dir.rglob("spec.md")):
            # Get spec name from parent directory
            spec_name = spec_file.parent.name

            # Skip if this is a nested spec (only want top-level)
            relative_path = spec_file.parent.relative_to(specs_dir)
            if len(relative_path.parts) > 1:
                continue

            status = self._parse_spec(spec_name, spec_file)

            # Add validation if enabled
            if include_validation and self.validate and self.validator:
                status = self._add_validation(status)
                status = self._compute_blocking(status)

            statuses.append(status)

        return statuses

    def scan_single(self, spec_name: str) -> SpecStatus:
        """Parse status for a single spec by name.

        Args:
            spec_name: Directory name of the spec (e.g., "032-status-dashboard")

        Returns:
            SpecStatus for the specified spec.

        Raises:
            SpecNotFoundError: If spec directory doesn't exist.
        """
        spec_dir = self.project_root / self.SPECS_DIR / spec_name
        spec_file = spec_dir / "spec.md"

        if not spec_dir.exists() or not spec_file.exists():
            raise SpecNotFoundError(
                f"Spec not found: {spec_name}. "
                f"Expected spec.md at {spec_file}"
            )

        status = self._parse_spec(spec_name, spec_file)

        if self.validate and self.validator:
            status = self._add_validation(status)
            status = self._compute_blocking(status)

        return status

    def _parse_spec(self, spec_name: str, spec_file: Path) -> SpecStatus:
        """Parse a single spec.md file and extract metadata.

        Args:
            spec_name: Name of the spec (directory name)
            spec_file: Path to the spec.md file

        Returns:
            SpecStatus with parsed metadata or error state
        """
        try:
            content = spec_file.read_text(encoding="utf-8")
            status = self._parse_status(content)
            last_modified = datetime.fromtimestamp(spec_file.stat().st_mtime)

            return SpecStatus(
                name=spec_name,
                path=spec_file,
                status=status,
                last_modified=last_modified,
                validation_result=None,
                is_blocking=False,
                error=None,
            )

        except (OSError, UnicodeDecodeError) as e:
            # File exists but couldn't be read
            return SpecStatus(
                name=spec_name,
                path=spec_file,
                status=SpecState.ERROR,
                last_modified=datetime.now(),
                validation_result=None,
                is_blocking=False,
                error=f"Unable to read file: {e}",
            )

    def _parse_status(self, content: str) -> SpecState:
        """Extract status from spec.md content.

        Looks for pattern: **Status**: <value>

        Args:
            content: Full content of spec.md file

        Returns:
            SpecState enum value, or ERROR if not found/parseable
        """
        match = self.STATUS_PATTERN.search(content)
        if not match:
            return SpecState.ERROR

        status_text = match.group(1).strip()
        return SpecState.from_string(status_text)

    def _add_validation(self, spec_status: SpecStatus) -> SpecStatus:
        """Add validation result to a SpecStatus.

        Args:
            spec_status: SpecStatus to add validation to.

        Returns:
            Updated SpecStatus with validation_result populated.
        """
        if self.validator is None or spec_status.error:
            return spec_status

        try:
            result = self.validator.validate_file(spec_status.path)
            return SpecStatus(
                name=spec_status.name,
                path=spec_status.path,
                status=spec_status.status,
                last_modified=spec_status.last_modified,
                validation_result=result,
                is_blocking=spec_status.is_blocking,
                error=spec_status.error,
            )
        except Exception as e:
            # Validation failed, mark as error
            return SpecStatus(
                name=spec_status.name,
                path=spec_status.path,
                status=spec_status.status,
                last_modified=spec_status.last_modified,
                validation_result=None,
                is_blocking=spec_status.is_blocking,
                error=f"Validation error: {e}",
            )

    def _compute_blocking(self, spec_status: SpecStatus) -> SpecStatus:
        """Compute whether a spec is blocking commits.

        A spec is blocking if:
        1. Status is IN_PROGRESS and validation fails, OR
        2. Status is DRAFT and validation fails AND spec is git-staged

        Args:
            spec_status: SpecStatus to check.

        Returns:
            Updated SpecStatus with is_blocking computed.
        """
        is_blocking = False

        # Check if validation failed
        validation_failed = (
            spec_status.validation_result is not None
            and spec_status.validation_result.error_count > 0
        )

        if validation_failed:
            if spec_status.status == SpecState.IN_PROGRESS:
                # In Progress specs always block when validation fails
                is_blocking = True
            elif spec_status.status == SpecState.DRAFT:
                # Draft specs only block if they're staged
                is_blocking = self._is_git_staged(spec_status.path)

        return SpecStatus(
            name=spec_status.name,
            path=spec_status.path,
            status=spec_status.status,
            last_modified=spec_status.last_modified,
            validation_result=spec_status.validation_result,
            is_blocking=is_blocking,
            error=spec_status.error,
        )

    def _is_git_staged(self, spec_path: Path) -> bool:
        """Check if a spec file is staged for commit.

        Args:
            spec_path: Path to the spec file.

        Returns:
            True if the file is in git's staging area.
        """
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )
            if result.returncode != 0:
                return False

            # Check if spec path (relative) is in staged files
            try:
                relative_path = spec_path.relative_to(self.project_root)
                return str(relative_path) in result.stdout
            except ValueError:
                return False

        except (FileNotFoundError, subprocess.SubprocessError):
            # Git not available or command failed
            return False

    def generate_report(self, include_validation: bool = True) -> StatusReport:
        """Scan all specs and generate a StatusReport.

        Convenience method that combines scan() with report generation.

        Args:
            include_validation: Whether to include validation results.

        Returns:
            StatusReport containing all spec statuses and computed stats.
        """
        specs = self.scan(include_validation=include_validation)
        return StatusReport(
            specs=specs,
            generated_at=datetime.now(),
            project_root=self.project_root,
        )
