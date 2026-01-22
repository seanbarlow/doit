"""Data models for constitution cleanup workflow.

This module contains all data models and dataclasses
for the constitution/tech-stack separation feature.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


class CleanupState(Enum):
    """State of cleanup operation."""

    ANALYZING = "analyzing"
    BACKING_UP = "backing_up"
    EXTRACTING = "extracting"
    PROMPTING = "prompting"
    WRITING = "writing"
    COMPLETE = "complete"
    NO_CHANGES = "no_changes"
    SKIPPED = "skipped"


@dataclass
class CleanupResult:
    """Result of constitution cleanup operation.

    Represents the outcome of separating tech-stack content
    from constitution.md into tech-stack.md.
    """

    backup_path: Optional[Path] = None
    extracted_sections: list[str] = field(default_factory=list)
    preserved_sections: list[str] = field(default_factory=list)
    unclear_sections: list[str] = field(default_factory=list)
    constitution_size_before: int = 0
    constitution_size_after: int = 0
    tech_stack_created: bool = False
    tech_stack_merged: bool = False
    error_message: Optional[str] = None

    @property
    def success(self) -> bool:
        """Return True if cleanup completed successfully."""
        return self.error_message is None and (
            self.tech_stack_created or len(self.extracted_sections) == 0
        )

    @property
    def had_tech_sections(self) -> bool:
        """Return True if tech sections were found and extracted."""
        return len(self.extracted_sections) > 0

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "backup_path": str(self.backup_path) if self.backup_path else None,
            "extracted_sections": self.extracted_sections,
            "preserved_sections": self.preserved_sections,
            "unclear_sections": self.unclear_sections,
            "constitution_size_before": self.constitution_size_before,
            "constitution_size_after": self.constitution_size_after,
            "tech_stack_created": self.tech_stack_created,
            "tech_stack_merged": self.tech_stack_merged,
            "error_message": self.error_message,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CleanupResult":
        """Create CleanupResult from dictionary."""
        return cls(
            backup_path=Path(data["backup_path"]) if data.get("backup_path") else None,
            extracted_sections=data.get("extracted_sections", []),
            preserved_sections=data.get("preserved_sections", []),
            unclear_sections=data.get("unclear_sections", []),
            constitution_size_before=data.get("constitution_size_before", 0),
            constitution_size_after=data.get("constitution_size_after", 0),
            tech_stack_created=data.get("tech_stack_created", False),
            tech_stack_merged=data.get("tech_stack_merged", False),
            error_message=data.get("error_message"),
        )


@dataclass
class AnalysisResult:
    """Result of analyzing constitution content.

    Contains information about what sections would be
    extracted vs preserved during cleanup.
    """

    tech_sections: dict[str, str] = field(default_factory=dict)
    preserved_sections: dict[str, str] = field(default_factory=dict)
    unclear_sections: dict[str, str] = field(default_factory=dict)
    header_content: str = ""
    footer_content: str = ""

    @property
    def has_tech_content(self) -> bool:
        """Return True if any tech sections were found."""
        return len(self.tech_sections) > 0
