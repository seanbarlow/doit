"""Date inference service for spec analytics.

This module extracts creation and completion dates for specifications using
a multi-tier fallback strategy:
1. Parse dates from spec.md metadata (e.g., **Created**: YYYY-MM-DD)
2. Extract dates from git history
3. Fall back to file system timestamps
"""

import re
import subprocess
from datetime import date, datetime
from pathlib import Path
from typing import Optional


class DateInferrer:
    """Service for inferring spec lifecycle dates.

    Uses a multi-tier fallback strategy to extract creation and completion
    dates from various sources.
    """

    # Patterns for extracting dates from spec metadata
    CREATED_PATTERN = re.compile(
        r"\*\*Created\*\*:\s*(\d{4}-\d{2}-\d{2})", re.IGNORECASE
    )
    DATE_PATTERN = re.compile(
        r"\*\*Date\*\*:\s*(\d{4}-\d{2}-\d{2})", re.IGNORECASE
    )
    STATUS_COMPLETE_PATTERN = re.compile(
        r"\*\*Status\*\*:\s*(Complete|Completed|Approved)", re.IGNORECASE
    )

    def __init__(self, project_root: Path):
        """Initialize the date inferrer.

        Args:
            project_root: Root directory of the project
        """
        self.project_root = project_root
        self._git_available: Optional[bool] = None

    def _is_git_available(self) -> bool:
        """Check if git is available and project is a git repo."""
        if self._git_available is not None:
            return self._git_available

        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5,
            )
            self._git_available = result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            self._git_available = False

        return self._git_available

    def infer_created_date(self, spec_path: Path) -> Optional[date]:
        """Infer the creation date for a spec.

        Tries sources in order:
        1. **Created**: in spec.md metadata
        2. **Date**: in spec.md metadata (fallback)
        3. Git first commit date for the file
        4. File system creation time

        Args:
            spec_path: Path to the spec.md file

        Returns:
            Inferred creation date or None if cannot determine
        """
        # Tier 1: Parse from metadata
        if spec_path.exists():
            metadata_date = self._parse_created_from_metadata(spec_path)
            if metadata_date:
                return metadata_date

        # Tier 2: Git first commit
        if self._is_git_available():
            git_date = self._get_git_first_commit_date(spec_path)
            if git_date:
                return git_date

        # Tier 3: File system
        return self._get_file_creation_date(spec_path)

    def infer_completed_date(self, spec_path: Path) -> Optional[date]:
        """Infer the completion date for a spec.

        Tries sources in order:
        1. Git commit that changed status to Complete/Approved
        2. Git last modification date (if status is Complete/Approved)
        3. File modification time (if status is Complete/Approved)

        Args:
            spec_path: Path to the spec.md file

        Returns:
            Inferred completion date or None if not completed
        """
        if not spec_path.exists():
            return None

        # Check if spec is actually completed
        if not self._is_spec_completed(spec_path):
            return None

        # Tier 1: Git commit that changed status to Complete
        if self._is_git_available():
            status_change_date = self._get_git_status_change_date(spec_path)
            if status_change_date:
                return status_change_date

            # Tier 2: Git last modification date
            last_mod_date = self._get_git_last_modified_date(spec_path)
            if last_mod_date:
                return last_mod_date

        # Tier 3: File modification time
        return self._get_file_modification_date(spec_path)

    def _parse_created_from_metadata(self, spec_path: Path) -> Optional[date]:
        """Parse creation date from spec metadata.

        Args:
            spec_path: Path to spec.md file

        Returns:
            Parsed date or None
        """
        try:
            content = spec_path.read_text(encoding="utf-8")

            # Try **Created**: first
            match = self.CREATED_PATTERN.search(content)
            if match:
                return self._parse_date_string(match.group(1))

            # Fall back to **Date**:
            match = self.DATE_PATTERN.search(content)
            if match:
                return self._parse_date_string(match.group(1))

        except (OSError, UnicodeDecodeError):
            pass

        return None

    def _is_spec_completed(self, spec_path: Path) -> bool:
        """Check if spec has Complete or Approved status.

        Args:
            spec_path: Path to spec.md file

        Returns:
            True if completed, False otherwise
        """
        try:
            content = spec_path.read_text(encoding="utf-8")
            return bool(self.STATUS_COMPLETE_PATTERN.search(content))
        except (OSError, UnicodeDecodeError):
            return False

    def _get_git_first_commit_date(self, spec_path: Path) -> Optional[date]:
        """Get the date of the first git commit for a file.

        Args:
            spec_path: Path to the file

        Returns:
            Date of first commit or None
        """
        try:
            result = subprocess.run(
                [
                    "git",
                    "log",
                    "--follow",
                    "--diff-filter=A",
                    "--format=%aI",
                    "--",
                    str(spec_path),
                ],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0 and result.stdout.strip():
                # Get the last line (first commit) if multiple
                lines = result.stdout.strip().split("\n")
                first_commit_date = lines[-1] if lines else None
                if first_commit_date:
                    return self._parse_iso_datetime(first_commit_date)

        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass

        return None

    def _get_git_last_modified_date(self, spec_path: Path) -> Optional[date]:
        """Get the date of the last git modification for a file.

        Args:
            spec_path: Path to the file

        Returns:
            Date of last modification or None
        """
        try:
            result = subprocess.run(
                [
                    "git",
                    "log",
                    "-1",
                    "--format=%aI",
                    "--",
                    str(spec_path),
                ],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0 and result.stdout.strip():
                return self._parse_iso_datetime(result.stdout.strip())

        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass

        return None

    def _get_git_status_change_date(self, spec_path: Path) -> Optional[date]:
        """Get the date when status changed to Complete/Approved.

        Args:
            spec_path: Path to the file

        Returns:
            Date of status change or None
        """
        try:
            # Search git log for commits that mention status change
            result = subprocess.run(
                [
                    "git",
                    "log",
                    "-p",
                    "--format=%aI",
                    "-S",
                    "Status**: Complete",
                    "--",
                    str(spec_path),
                ],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=15,
            )

            if result.returncode == 0 and result.stdout.strip():
                # Extract the first date (most recent change)
                lines = result.stdout.strip().split("\n")
                for line in lines:
                    if line.startswith("20") and "T" in line:  # ISO date
                        return self._parse_iso_datetime(line)

        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass

        return None

    def _get_file_creation_date(self, spec_path: Path) -> Optional[date]:
        """Get file system creation date.

        Args:
            spec_path: Path to the file

        Returns:
            Creation date or None
        """
        try:
            if spec_path.exists():
                stat = spec_path.stat()
                # Try birth time (macOS), fall back to ctime
                timestamp = getattr(stat, "st_birthtime", stat.st_ctime)
                return date.fromtimestamp(timestamp)
        except (OSError, ValueError):
            pass

        return None

    def _get_file_modification_date(self, spec_path: Path) -> Optional[date]:
        """Get file system modification date.

        Args:
            spec_path: Path to the file

        Returns:
            Modification date or None
        """
        try:
            if spec_path.exists():
                stat = spec_path.stat()
                return date.fromtimestamp(stat.st_mtime)
        except (OSError, ValueError):
            pass

        return None

    @staticmethod
    def _parse_date_string(date_str: str) -> Optional[date]:
        """Parse a YYYY-MM-DD date string.

        Args:
            date_str: Date string in YYYY-MM-DD format

        Returns:
            Parsed date or None
        """
        try:
            return datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
        except ValueError:
            return None

    @staticmethod
    def _parse_iso_datetime(iso_str: str) -> Optional[date]:
        """Parse an ISO 8601 datetime string to date.

        Args:
            iso_str: ISO datetime string (e.g., 2026-01-16T14:30:00-08:00)

        Returns:
            Parsed date or None
        """
        try:
            # Handle timezone offset by truncating to date portion
            date_part = iso_str.split("T")[0]
            return datetime.strptime(date_part, "%Y-%m-%d").date()
        except (ValueError, IndexError):
            return None
