"""
Service Contract: GitHub Linker

Purpose: Create and manage bidirectional links between spec files and GitHub epics.
"""

from typing import Protocol, Optional
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime


@dataclass
class EpicReference:
    """Reference to a GitHub epic from a spec file."""

    number: int
    url: str
    priority: Optional[str]  # P1, P2, P3, P4


@dataclass
class SpecReference:
    """Reference to a spec file from a GitHub epic."""

    file_path: str  # Relative path from repo root
    feature_name: str
    branch_name: str


@dataclass
class GitHubEpic:
    """Represents a GitHub issue with epic label."""

    number: int
    title: str
    url: str
    state: str  # open, closed
    labels: list[str]
    body: str
    spec_paths: list[str]  # Extracted from body
    created_at: datetime
    updated_at: datetime

    @property
    def is_open(self) -> bool:
        """Check if epic is open."""
        return self.state == "open"

    @property
    def priority(self) -> Optional[str]:
        """Extract priority label from labels list."""
        for label in self.labels:
            if label.startswith("priority:"):
                return label.split(":")[1]
        return None


class GitHubLinkerService(Protocol):
    """
    Service for linking spec files to GitHub epics.

    This service manages bidirectional links: updating spec frontmatter with
    epic references and updating GitHub epic descriptions with spec file paths.
    """

    def link_spec_to_epic(
        self, spec_path: Path, epic_number: int, overwrite: bool = False
    ) -> bool:
        """
        Create bidirectional link between spec file and GitHub epic.

        This method:
        1. Fetches epic details from GitHub
        2. Updates spec frontmatter with epic reference
        3. Updates GitHub epic body with spec file path

        Args:
            spec_path: Path to spec.md file
            epic_number: GitHub issue number
            overwrite: If True, replace existing epic link. If False, prompt user.

        Returns:
            True if linking succeeded, False otherwise

        Raises:
            FileNotFoundError: If spec file doesn't exist
            ValueError: If epic number is invalid or epic is closed
            GitHubAPIError: If GitHub API request fails
        """
        ...

    def update_spec_frontmatter(
        self, spec_path: Path, epic_ref: EpicReference
    ) -> None:
        """
        Update spec file frontmatter with epic reference.

        Args:
            spec_path: Path to spec.md file
            epic_ref: Epic reference data

        Raises:
            FileNotFoundError: If spec file doesn't exist
            ValueError: If frontmatter is malformed
        """
        ...

    def update_epic_body(
        self, epic_number: int, spec_ref: SpecReference
    ) -> None:
        """
        Update GitHub epic body with spec file reference.

        This method:
        1. Fetches current epic body
        2. Finds or creates "## Specification" section
        3. Appends spec file path to the section
        4. Updates epic via GitHub API

        Args:
            epic_number: GitHub issue number
            spec_ref: Spec file reference data

        Raises:
            GitHubAPIError: If GitHub API request fails
            ValueError: If epic number is invalid
        """
        ...

    def get_epic_details(self, epic_number: int) -> GitHubEpic:
        """
        Fetch epic details from GitHub API.

        Args:
            epic_number: GitHub issue number

        Returns:
            GitHubEpic object with all epic metadata

        Raises:
            GitHubAPIError: If API request fails (404, rate limit, etc.)
            ValueError: If epic number is invalid
        """
        ...

    def validate_epic_for_linking(self, epic_number: int) -> tuple[bool, str]:
        """
        Check if an epic can be linked to a spec.

        Validation checks:
        - Epic exists
        - Epic is open (not closed)
        - Epic has "epic" label
        - User has write access to repository

        Args:
            epic_number: GitHub issue number

        Returns:
            Tuple of (is_valid, error_message)
            If is_valid=True, error_message is empty string
        """
        ...

    def update_all_spec_links(self, specs_dir: Path) -> dict[str, bool]:
        """
        Refresh all spec-epic links in the repository.

        This method scans all spec files, extracts epic references,
        and updates GitHub epic bodies with current spec paths.

        Args:
            specs_dir: Path to specs/ directory

        Returns:
            Dictionary mapping spec paths to success status

        Raises:
            ValueError: If specs_dir doesn't exist
        """
        ...

    def unlink_spec_from_epic(self, spec_path: Path, epic_number: int) -> bool:
        """
        Remove link between spec file and GitHub epic.

        This method:
        1. Removes epic reference from spec frontmatter
        2. Removes spec path from epic body

        Args:
            spec_path: Path to spec.md file
            epic_number: GitHub issue number

        Returns:
            True if unlinking succeeded, False otherwise
        """
        ...


# Example Usage

"""
# Initialize service
linker = GitHubLinkerServiceImpl(github_client=GitHubClient())

# Link spec to epic
try:
    success = linker.link_spec_to_epic(
        spec_path=Path("specs/040-spec-github-linking/spec.md"),
        epic_number=123,
        overwrite=False
    )
    if success:
        print("✓ Spec linked to epic #123")
except ValueError as e:
    print(f"✗ Linking failed: {e}")

# Validate epic before linking
is_valid, error = linker.validate_epic_for_linking(epic_number=123)
if not is_valid:
    print(f"Cannot link: {error}")

# Update all spec links (for --update-links flag)
results = linker.update_all_spec_links(specs_dir=Path("specs/"))
success_count = sum(1 for status in results.values() if status)
print(f"Updated {success_count}/{len(results)} spec links")

# Get epic details
epic = linker.get_epic_details(epic_number=123)
print(f"Epic: {epic.title}")
print(f"Priority: {epic.priority}")
print(f"Linked specs: {', '.join(epic.spec_paths)}")
"""
