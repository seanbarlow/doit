"""
Service Contract: Spec Parser

Purpose: Parse and manipulate spec file frontmatter and content.
"""

from typing import Protocol, Any
from pathlib import Path
from dataclasses import dataclass


@dataclass
class SpecFrontmatter:
    """Represents parsed YAML frontmatter from a spec file."""

    feature_name: str
    branch_name: str
    created_date: str
    status: str
    epic_number: int | None = None
    epic_url: str | None = None
    priority: str | None = None
    raw_data: dict[str, Any] | None = None  # For preserving unknown fields

    def to_yaml_dict(self) -> dict[str, Any]:
        """Convert frontmatter to YAML-compatible dictionary."""
        data = {
            "Feature": self.feature_name,
            "Branch": self.branch_name,
            "Created": self.created_date,
            "Status": self.status,
        }

        if self.epic_number and self.epic_url:
            data["Epic"] = f"[#{self.epic_number}]({self.epic_url})"
            data["Epic URL"] = self.epic_url

        if self.priority:
            data["Priority"] = self.priority

        # Preserve unknown fields
        if self.raw_data:
            for key, value in self.raw_data.items():
                if key not in data:
                    data[key] = value

        return data


class SpecParserService(Protocol):
    """
    Service for parsing and manipulating spec file frontmatter.

    This service handles reading, parsing, updating, and writing spec files
    while preserving frontmatter and content structure.
    """

    def parse_frontmatter(self, spec_path: Path) -> SpecFrontmatter:
        """
        Parse YAML frontmatter from a spec file.

        Args:
            spec_path: Path to spec.md file

        Returns:
            SpecFrontmatter object with parsed fields

        Raises:
            FileNotFoundError: If spec file doesn't exist
            ValueError: If frontmatter is malformed or missing required fields
        """
        ...

    def update_frontmatter(
        self, spec_path: Path, updates: dict[str, Any]
    ) -> None:
        """
        Update specific fields in spec frontmatter.

        This method:
        1. Reads current spec file
        2. Parses frontmatter
        3. Applies updates (merges with existing fields)
        4. Writes updated spec file atomically

        Args:
            spec_path: Path to spec.md file
            updates: Dictionary of fields to update

        Raises:
            FileNotFoundError: If spec file doesn't exist
            ValueError: If frontmatter is malformed
        """
        ...

    def add_epic_reference(
        self,
        spec_path: Path,
        epic_number: int,
        epic_url: str,
        priority: str | None = None,
    ) -> None:
        """
        Add or update epic reference in spec frontmatter.

        Args:
            spec_path: Path to spec.md file
            epic_number: GitHub issue number
            epic_url: Full GitHub issue URL
            priority: Optional priority (P1, P2, P3, P4)

        Raises:
            FileNotFoundError: If spec file doesn't exist
            ValueError: If epic data is invalid
        """
        ...

    def remove_epic_reference(self, spec_path: Path) -> None:
        """
        Remove epic reference from spec frontmatter.

        Args:
            spec_path: Path to spec.md file

        Raises:
            FileNotFoundError: If spec file doesn't exist
        """
        ...

    def get_epic_reference(self, spec_path: Path) -> tuple[int, str] | None:
        """
        Extract epic reference from spec frontmatter.

        Args:
            spec_path: Path to spec.md file

        Returns:
            Tuple of (epic_number, epic_url) if present, None otherwise

        Raises:
            FileNotFoundError: If spec file doesn't exist
        """
        ...

    def write_spec_file(
        self, spec_path: Path, frontmatter: SpecFrontmatter, content: str
    ) -> None:
        """
        Write spec file with frontmatter and content atomically.

        This method uses atomic file operations (write to temp + rename)
        to prevent corruption if process is interrupted.

        Args:
            spec_path: Path to spec.md file
            frontmatter: Frontmatter data
            content: Markdown content (after frontmatter)

        Raises:
            OSError: If file write fails
        """
        ...

    def validate_frontmatter(self, frontmatter: SpecFrontmatter) -> list[str]:
        """
        Validate frontmatter fields against schema.

        Checks:
        - Required fields are present
        - Field values match expected format
        - Epic reference is valid if present

        Args:
            frontmatter: Frontmatter to validate

        Returns:
            List of validation error messages (empty if valid)
        """
        ...


# Example Usage

"""
# Initialize service
parser = SpecParserServiceImpl()

# Parse existing spec
frontmatter = parser.parse_frontmatter(
    Path("specs/040-spec-github-linking/spec.md")
)
print(f"Feature: {frontmatter.feature_name}")
print(f"Status: {frontmatter.status}")

# Add epic reference
parser.add_epic_reference(
    spec_path=Path("specs/040-spec-github-linking/spec.md"),
    epic_number=123,
    epic_url="https://github.com/owner/repo/issues/123",
    priority="P1"
)

# Check if spec has epic
epic_ref = parser.get_epic_reference(
    Path("specs/040-spec-github-linking/spec.md")
)
if epic_ref:
    epic_number, epic_url = epic_ref
    print(f"Linked to epic #{epic_number}")

# Update multiple fields
parser.update_frontmatter(
    spec_path=Path("specs/040-spec-github-linking/spec.md"),
    updates={
        "Status": "In Progress",
        "Priority": "P1"
    }
)

# Validate frontmatter
errors = parser.validate_frontmatter(frontmatter)
if errors:
    print("Validation errors:")
    for error in errors:
        print(f"  - {error}")
"""
