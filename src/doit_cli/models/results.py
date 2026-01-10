"""Result models for init and verify operations."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

from .project import Project


class VerifyStatus(str, Enum):
    """Status of verification check."""

    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"


@dataclass
class VerifyCheck:
    """Single verification check result."""

    name: str
    status: VerifyStatus
    message: str
    suggestion: Optional[str] = None


@dataclass
class InitResult:
    """Result of initialization operation."""

    success: bool
    project: Project
    created_directories: list[Path] = field(default_factory=list)
    created_files: list[Path] = field(default_factory=list)
    updated_files: list[Path] = field(default_factory=list)
    skipped_files: list[Path] = field(default_factory=list)
    backup_path: Optional[Path] = None
    error_message: Optional[str] = None

    @property
    def total_created(self) -> int:
        """Total number of files and directories created."""
        return len(self.created_directories) + len(self.created_files)

    @property
    def summary(self) -> str:
        """Human-readable summary of the operation."""
        if not self.success:
            return f"Failed: {self.error_message or 'Unknown error'}"

        parts = []
        if self.created_directories:
            parts.append(f"{len(self.created_directories)} directories created")
        if self.created_files:
            parts.append(f"{len(self.created_files)} files created")
        if self.updated_files:
            parts.append(f"{len(self.updated_files)} files updated")
        if self.skipped_files:
            parts.append(f"{len(self.skipped_files)} files skipped")

        return ", ".join(parts) if parts else "No changes made"


@dataclass
class VerifyResult:
    """Result of project verification."""

    project: Project
    checks: list[VerifyCheck] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        """All checks passed (no failures)."""
        return not any(c.status == VerifyStatus.FAIL for c in self.checks)

    @property
    def has_warnings(self) -> bool:
        """Any checks have warnings."""
        return any(c.status == VerifyStatus.WARN for c in self.checks)

    @property
    def pass_count(self) -> int:
        """Number of passed checks."""
        return sum(1 for c in self.checks if c.status == VerifyStatus.PASS)

    @property
    def warn_count(self) -> int:
        """Number of warning checks."""
        return sum(1 for c in self.checks if c.status == VerifyStatus.WARN)

    @property
    def fail_count(self) -> int:
        """Number of failed checks."""
        return sum(1 for c in self.checks if c.status == VerifyStatus.FAIL)

    @property
    def summary(self) -> str:
        """Summary of check results."""
        return f"{self.pass_count} passed, {self.warn_count} warnings, {self.fail_count} failed"

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON output."""
        return {
            "status": "passed" if self.passed else "failed",
            "checks": [
                {
                    "name": c.name,
                    "status": c.status.value,
                    "message": c.message,
                    "suggestion": c.suggestion,
                }
                for c in self.checks
            ],
            "summary": {
                "passed": self.pass_count,
                "warnings": self.warn_count,
                "failed": self.fail_count,
            },
        }
