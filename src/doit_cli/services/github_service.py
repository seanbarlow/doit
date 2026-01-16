"""Service for GitHub issue operations via gh CLI.

This module provides the GitHubService class for interacting
with GitHub issues using the gh CLI tool.
"""

import json
import subprocess
from typing import Optional

from ..models.fixit_models import GitHubIssue


class GitHubServiceError(Exception):
    """Error raised when GitHub operations fail."""

    pass


class GitHubService:
    """Manages GitHub issue operations via gh CLI."""

    def __init__(self):
        """Initialize the GitHub service."""
        self._verify_gh_cli()

    def _verify_gh_cli(self) -> None:
        """Verify that gh CLI is available and authenticated."""
        try:
            result = subprocess.run(
                ["gh", "auth", "status"],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                # gh CLI not authenticated, but might still work for public repos
                pass
        except FileNotFoundError:
            raise GitHubServiceError(
                "GitHub CLI (gh) not found. Install it from https://cli.github.com/"
            )

    def is_available(self) -> bool:
        """Check if GitHub API is available."""
        try:
            result = subprocess.run(
                ["gh", "api", "rate_limit"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def get_issue(self, issue_id: int) -> Optional[GitHubIssue]:
        """Fetch a GitHub issue by ID.

        Args:
            issue_id: The GitHub issue number.

        Returns:
            GitHubIssue if found, None otherwise.
        """
        result = subprocess.run(
            [
                "gh", "issue", "view", str(issue_id),
                "--json", "number,title,body,state,labels"
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return None

        try:
            data = json.loads(result.stdout)
            return GitHubIssue.from_dict(data)
        except (json.JSONDecodeError, KeyError):
            return None

    def list_bugs(self, label: str = "bug", limit: int = 20) -> list[GitHubIssue]:
        """List open issues with specified label.

        Args:
            label: Label to filter by (default: "bug").
            limit: Maximum number of issues to return.

        Returns:
            List of GitHubIssue objects.
        """
        result = subprocess.run(
            [
                "gh", "issue", "list",
                "--label", label,
                "--state", "open",
                "--limit", str(limit),
                "--json", "number,title,body,state,labels"
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return []

        try:
            data = json.loads(result.stdout)
            return [GitHubIssue.from_dict(item) for item in data]
        except (json.JSONDecodeError, KeyError):
            return []

    def close_issue(self, issue_id: int, comment: str = "") -> bool:
        """Close a GitHub issue.

        Args:
            issue_id: The GitHub issue number.
            comment: Optional comment to add when closing.

        Returns:
            True if successful, False otherwise.
        """
        cmd = ["gh", "issue", "close", str(issue_id)]
        if comment:
            cmd.extend(["--comment", comment])

        result = subprocess.run(cmd, capture_output=True)
        return result.returncode == 0

    def add_comment(self, issue_id: int, comment: str) -> bool:
        """Add a comment to a GitHub issue.

        Args:
            issue_id: The GitHub issue number.
            comment: The comment text.

        Returns:
            True if successful, False otherwise.
        """
        result = subprocess.run(
            ["gh", "issue", "comment", str(issue_id), "--body", comment],
            capture_output=True,
        )
        return result.returncode == 0

    def check_branch_exists(self, branch_name: str) -> tuple[bool, bool]:
        """Check if a branch exists locally or remotely.

        Args:
            branch_name: The branch name to check.

        Returns:
            Tuple of (local_exists, remote_exists).
        """
        # Check local
        local_result = subprocess.run(
            ["git", "show-ref", "--verify", f"refs/heads/{branch_name}"],
            capture_output=True,
        )
        local_exists = local_result.returncode == 0

        # Check remote
        remote_result = subprocess.run(
            ["git", "ls-remote", "--heads", "origin", branch_name],
            capture_output=True,
            text=True,
        )
        remote_exists = bool(remote_result.stdout.strip())

        return local_exists, remote_exists

    def create_branch(self, branch_name: str, from_branch: str = "main") -> bool:
        """Create a new git branch.

        Args:
            branch_name: Name of the new branch.
            from_branch: Base branch to create from.

        Returns:
            True if successful, False otherwise.
        """
        # First try to checkout the base branch
        subprocess.run(
            ["git", "checkout", from_branch],
            capture_output=True,
        )

        # Create and checkout the new branch
        result = subprocess.run(
            ["git", "checkout", "-b", branch_name],
            capture_output=True,
        )
        return result.returncode == 0
