"""GitHub linker service for managing spec-epic bidirectional links.

This service creates and manages links between spec files and GitHub epics by:
1. Adding epic references to spec frontmatter
2. Updating GitHub epic descriptions with spec file paths
"""

import re
import subprocess
from pathlib import Path
from typing import Optional, Tuple
from dataclasses import dataclass

from .github_service import GitHubService, GitHubServiceError
from ..utils.spec_parser import (
    add_epic_reference as add_epic_to_spec,
    remove_epic_reference,
    get_epic_reference,
)


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


class GitHubLinkerService:
    """Service for linking spec files to GitHub epics.

    This service manages bidirectional links: updating spec frontmatter with
    epic references and updating GitHub epic descriptions with spec file paths.
    """

    def __init__(self, github_service: Optional[GitHubService] = None):
        """Initialize the linker service.

        Args:
            github_service: GitHub service instance (creates new if not provided)
        """
        self.github_service = github_service or GitHubService()

    def link_spec_to_epic(
        self,
        spec_path: Path,
        epic_number: int,
        overwrite: bool = False
    ) -> bool:
        """Create bidirectional link between spec file and GitHub epic.

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
            GitHubServiceError: If GitHub API request fails
        """
        if not spec_path.exists():
            raise FileNotFoundError(f"Spec file not found: {spec_path}")

        if epic_number <= 0:
            raise ValueError(f"Invalid epic number: {epic_number}")

        # Check if spec already has epic reference
        existing_epic = get_epic_reference(spec_path)
        if existing_epic and not overwrite:
            existing_num, _ = existing_epic
            if existing_num != epic_number:
                print(f"Warning: Spec already linked to epic #{existing_num}")
                print(f"Use overwrite=True to replace with #{epic_number}")
                return False

        try:
            # Validate epic (fetch to ensure it exists and is open)
            is_valid, error = self.validate_epic_for_linking(epic_number)
            if not is_valid:
                raise ValueError(f"Cannot link to epic #{epic_number}: {error}")

            # Get epic details for priority
            epic = self.get_epic_details(epic_number)

            # Update spec frontmatter
            add_epic_to_spec(
                spec_path,
                epic_number=epic_number,
                epic_url=f"https://github.com/{self._get_repo_slug()}/issues/{epic_number}",
                priority=epic.get("priority")
            )

            # Update epic body with spec reference
            spec_ref = SpecReference(
                file_path=self._get_relative_path(spec_path),
                feature_name=spec_path.parent.name,
                branch_name=spec_path.parent.name
            )
            self.update_epic_body(epic_number, spec_ref)

            return True

        except GitHubServiceError as e:
            print(f"GitHub API error: {e}")
            print("Spec frontmatter updated, but epic update failed.")
            print(f"Retry later with: doit spec link {spec_path.parent}")
            return False

    def update_epic_body(
        self,
        epic_number: int,
        spec_ref: SpecReference
    ) -> None:
        """Update GitHub epic body with spec file reference.

        This method:
        1. Fetches current epic body
        2. Finds or creates "## Specification" section
        3. Appends spec file path to the section
        4. Updates epic via GitHub CLI

        Args:
            epic_number: GitHub issue number
            spec_ref: Spec file reference data

        Raises:
            GitHubServiceError: If GitHub API request fails
            ValueError: If epic number is invalid
        """
        if epic_number <= 0:
            raise ValueError(f"Invalid epic number: {epic_number}")

        try:
            # Fetch current epic body
            epic = self.get_epic_details(epic_number)
            current_body = epic.get("body", "")

            # Update body with spec reference
            new_body = self._add_spec_to_body(current_body, spec_ref.file_path)

            # Update epic via gh CLI
            self._update_epic_via_cli(epic_number, new_body)

        except subprocess.CalledProcessError as e:
            raise GitHubServiceError(f"Failed to update epic #{epic_number}: {e}")

    def get_epic_details(self, epic_number: int) -> dict:
        """Fetch epic details from GitHub API.

        Args:
            epic_number: GitHub issue number

        Returns:
            Dictionary with epic metadata (number, title, body, state, labels, url)

        Raises:
            GitHubServiceError: If API request fails (404, rate limit, etc.)
            ValueError: If epic number is invalid
        """
        if epic_number <= 0:
            raise ValueError(f"Invalid epic number: {epic_number}")

        try:
            repo_slug = self._get_repo_slug()
            cmd = [
                "gh", "api",
                f"repos/{repo_slug}/issues/{epic_number}",
                "--jq", "{number:.number, title:.title, body:.body, state:.state, labels:[.labels[].name], url:.html_url}"
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=30
            )

            import json
            epic_data = json.loads(result.stdout)

            # Extract priority from labels
            priority = None
            for label in epic_data.get("labels", []):
                if label.startswith("priority:"):
                    priority = label.split(":")[1]
                    break

            epic_data["priority"] = priority
            return epic_data

        except subprocess.CalledProcessError as e:
            if "404" in e.stderr:
                raise GitHubServiceError(f"Epic #{epic_number} not found")
            raise GitHubServiceError(f"Failed to fetch epic #{epic_number}: {e.stderr}")
        except subprocess.TimeoutExpired:
            raise GitHubServiceError(f"Timeout fetching epic #{epic_number}")

    def validate_epic_for_linking(self, epic_number: int) -> Tuple[bool, str]:
        """Check if an epic can be linked to a spec.

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
        try:
            epic = self.get_epic_details(epic_number)

            # Check if epic is closed
            if epic.get("state") == "closed":
                return (False, f"Epic #{epic_number} is closed")

            # Check if epic has "epic" label
            labels = epic.get("labels", [])
            if "epic" not in labels:
                return (False, f"Issue #{epic_number} is not labeled as an epic")

            return (True, "")

        except GitHubServiceError as e:
            return (False, str(e))

    def unlink_spec_from_epic(self, spec_path: Path, epic_number: int) -> bool:
        """Remove link between spec file and GitHub epic.

        This method:
        1. Removes epic reference from spec frontmatter
        2. Removes spec path from epic body

        Args:
            spec_path: Path to spec.md file
            epic_number: GitHub issue number

        Returns:
            True if unlinking succeeded, False otherwise
        """
        if not spec_path.exists():
            raise FileNotFoundError(f"Spec file not found: {spec_path}")

        try:
            # Remove from spec frontmatter
            remove_epic_reference(spec_path)

            # Remove from epic body
            epic = self.get_epic_details(epic_number)
            current_body = epic.get("body", "")
            spec_path_str = self._get_relative_path(spec_path)
            new_body = self._remove_spec_from_body(current_body, spec_path_str)

            self._update_epic_via_cli(epic_number, new_body)

            return True

        except GitHubServiceError as e:
            print(f"GitHub API error: {e}")
            print("Spec frontmatter updated, but epic update failed.")
            return False

    def _add_spec_to_body(self, body: str, spec_path: str) -> str:
        """Add spec file path to epic body in "## Specification" section.

        Args:
            body: Current epic body
            spec_path: Relative path to spec file

        Returns:
            Updated body with spec path added
        """
        # Check if "## Specification" section exists
        spec_section_pattern = r'## Specification\s*\n'
        spec_match = re.search(spec_section_pattern, body, re.MULTILINE)

        if spec_match:
            # Section exists, check if spec path is already listed
            # Find the end of the section (next ## or end of body)
            section_start = spec_match.end()
            next_section = re.search(r'\n##\s', body[section_start:])
            section_end = section_start + next_section.start() if next_section else len(body)

            section_content = body[section_start:section_end]

            # Check if spec is already listed
            if f"`{spec_path}`" in section_content:
                return body  # Already listed, no change needed

            # Add spec to existing list
            new_line = f"- `{spec_path}`\n"
            new_body = body[:section_end] + new_line + body[section_end:]
            return new_body
        else:
            # Section doesn't exist, create it
            if body and not body.endswith("\n"):
                body += "\n"
            body += "\n## Specification\n\n"
            body += f"- `{spec_path}`\n"
            return body

    def _remove_spec_from_body(self, body: str, spec_path: str) -> str:
        """Remove spec file path from epic body "## Specification" section.

        Args:
            body: Current epic body
            spec_path: Relative path to spec file

        Returns:
            Updated body with spec path removed
        """
        # Remove the spec path line
        line_pattern = rf"- `{re.escape(spec_path)}`\n"
        new_body = re.sub(line_pattern, "", body)

        # If Specification section is now empty, remove it
        empty_section_pattern = r'## Specification\s*\n\s*(?=\n##|\Z)'
        new_body = re.sub(empty_section_pattern, "", new_body, flags=re.MULTILINE)

        return new_body

    def _update_epic_via_cli(self, epic_number: int, new_body: str) -> None:
        """Update epic body via gh CLI.

        Args:
            epic_number: GitHub issue number
            new_body: New body content

        Raises:
            subprocess.CalledProcessError: If gh CLI command fails
        """
        cmd = ["gh", "issue", "edit", str(epic_number), "--body", new_body]
        subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=30)

    def _get_repo_slug(self) -> str:
        """Get repository slug (owner/repo) from git remote.

        Returns:
            Repository slug in format "owner/repo"

        Raises:
            GitHubServiceError: If git remote not found or malformed
        """
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                capture_output=True,
                text=True,
                check=True
            )
            remote_url = result.stdout.strip()

            # Parse GitHub URL
            # SSH: git@github.com:owner/repo.git
            # HTTPS: https://github.com/owner/repo.git
            if "github.com" not in remote_url:
                raise GitHubServiceError(f"Not a GitHub repository: {remote_url}")

            if remote_url.startswith("git@"):
                slug = remote_url.split(":")[-1].replace(".git", "")
            else:
                slug = remote_url.split("github.com/")[-1].replace(".git", "")

            return slug

        except subprocess.CalledProcessError:
            raise GitHubServiceError("Failed to get git remote URL")

    def create_epic_for_roadmap_item(
        self,
        title: str,
        priority: str,
        feature_description: Optional[str] = None
    ) -> Tuple[int, str]:
        """Create a new GitHub epic for a roadmap item.

        Args:
            title: Epic title (from roadmap item title)
            priority: Priority level (P1, P2, P3, P4)
            feature_description: Optional feature description for epic body

        Returns:
            Tuple of (epic_number, epic_url)

        Raises:
            GitHubServiceError: If epic creation fails
            ValueError: If priority is invalid
        """
        if priority not in ["P1", "P2", "P3", "P4"]:
            raise ValueError(f"Invalid priority: {priority}")

        try:
            # Generate epic body
            body = feature_description or f"Epic for feature: {title}"
            body += "\n\n## Specification\n\n_Spec file will be added when created_"

            # Create epic via GitHub service
            epic = self.github_service.create_epic(
                title=title,
                body=body,
                priority=priority,
                labels=[]
            )

            return (epic.number, epic.url)

        except Exception as e:
            raise GitHubServiceError(f"Failed to create epic: {e}")

    def update_roadmap_with_epic(
        self,
        roadmap_path: Path,
        roadmap_title: str,
        epic_number: int,
        epic_url: str
    ) -> None:
        """Update roadmap.md file with newly created epic reference.

        Args:
            roadmap_path: Path to roadmap.md file
            roadmap_title: Title of the roadmap item to update
            epic_number: GitHub epic number
            epic_url: GitHub epic URL

        Raises:
            FileNotFoundError: If roadmap file doesn't exist
            ValueError: If roadmap item not found
        """
        if not roadmap_path.exists():
            raise FileNotFoundError(f"Roadmap file not found: {roadmap_path}")

        # Read current roadmap content
        with open(roadmap_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Find the row with matching title
        lines = content.splitlines()
        updated_lines = []
        updated = False

        for line in lines:
            # Check if this line contains the target title
            if roadmap_title in line and line.strip().startswith("|") and "---" not in line:
                # Parse the table row
                # Format: | Title | Priority | Branch | GitHub | Status | Category |
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 7:  # Including empty parts at start/end
                    # Update GitHub column (index 4)
                    parts[4] = f"[#{epic_number}]({epic_url})"
                    updated_lines.append("|".join(parts))
                    updated = True
                else:
                    updated_lines.append(line)
            else:
                updated_lines.append(line)

        if not updated:
            raise ValueError(f"Roadmap item not found: {roadmap_title}")

        # Write updated content
        new_content = "\n".join(updated_lines)
        with open(roadmap_path, "w", encoding="utf-8") as f:
            f.write(new_content)

    def _get_relative_path(self, spec_path: Path) -> str:
        """Get relative path from repository root.

        Args:
            spec_path: Absolute path to spec file

        Returns:
            Relative path from repo root (e.g., "specs/040-feature/spec.md")
        """
        try:
            # Get repo root
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                capture_output=True,
                text=True,
                check=True
            )
            repo_root = Path(result.stdout.strip())

            # Get relative path
            return str(spec_path.relative_to(repo_root))

        except (subprocess.CalledProcessError, ValueError):
            # Fallback: assume current directory is repo root
            return str(spec_path)
