"""GitHub service for interacting with GitHub issues via gh CLI.

This service provides methods to fetch epics, features, and create issues
using the GitHub CLI (gh) command.
"""

import json
import subprocess
from typing import List, Optional

from doit_toolkit_cli.models.github_epic import GitHubEpic
from doit_toolkit_cli.utils.github_auth import has_gh_cli, is_gh_authenticated


class GitHubServiceError(Exception):
    """Base exception for GitHub service errors."""

    pass


class GitHubAuthError(GitHubServiceError):
    """Raised when GitHub authentication is required but not available."""

    pass


class GitHubAPIError(GitHubServiceError):
    """Raised when GitHub API returns an error."""

    pass


class GitHubService:
    """Service for interacting with GitHub issues via gh CLI.

    This service handles all GitHub API interactions using the gh CLI tool,
    including fetching epics, features, and creating issues.
    """

    def __init__(self, timeout: int = 30):
        """Initialize GitHub service.

        Args:
            timeout: Timeout in seconds for gh CLI commands (default: 30)
        """
        self.timeout = timeout

    def _ensure_authenticated(self) -> None:
        """Verify GitHub CLI is available and authenticated.

        Raises:
            GitHubAuthError: If gh CLI is not available or not authenticated
        """
        if not has_gh_cli():
            raise GitHubAuthError(
                "GitHub CLI (gh) not installed. Install from: https://cli.github.com"
            )

        if not is_gh_authenticated():
            raise GitHubAuthError(
                "GitHub CLI not authenticated. Run: gh auth login"
            )

    def fetch_epics(self, state: str = "open") -> List[GitHubEpic]:
        """Fetch all GitHub issues labeled as 'epic'.

        Args:
            state: Issue state to filter by (open, closed, or all). Default: open

        Returns:
            List of GitHubEpic instances

        Raises:
            GitHubAuthError: If GitHub authentication is not available
            GitHubAPIError: If the GitHub API returns an error

        Examples:
            >>> service = GitHubService()
            >>> epics = service.fetch_epics()
            >>> len(epics)
            2
        """
        self._ensure_authenticated()

        try:
            # Run gh CLI to fetch issues with 'epic' label
            result = subprocess.run(
                [
                    "gh",
                    "issue",
                    "list",
                    "--label",
                    "epic",
                    "--state",
                    state,
                    "--json",
                    "number,title,labels,body,url,state,createdAt,updatedAt",
                    "--limit",
                    "200",  # Support up to 200 epics per spec
                ],
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )

            if result.returncode != 0:
                # Check for rate limit error
                if "rate limit" in result.stderr.lower():
                    raise GitHubAPIError(
                        "GitHub API rate limit exceeded. Try again later or use --skip-github flag."
                    )
                raise GitHubAPIError(f"GitHub CLI error: {result.stderr}")

            # Parse JSON response
            issues_data = json.loads(result.stdout)

            # Convert to GitHubEpic instances
            epics = []
            for issue_data in issues_data:
                try:
                    epic = GitHubEpic.from_gh_json(issue_data)
                    epics.append(epic)
                except (ValueError, KeyError) as e:
                    # Log warning but continue with other epics
                    print(f"Warning: Skipping malformed epic #{issue_data.get('number')}: {e}")
                    continue

            return epics

        except subprocess.TimeoutExpired:
            raise GitHubAPIError(
                f"GitHub CLI timeout after {self.timeout} seconds. "
                "Try increasing timeout or use --skip-github flag."
            )
        except json.JSONDecodeError as e:
            raise GitHubAPIError(f"Failed to parse GitHub CLI response: {e}")
        except FileNotFoundError:
            raise GitHubAuthError(
                "GitHub CLI (gh) not found in PATH. Install from: https://cli.github.com"
            )

    def fetch_features_for_epic(self, epic_number: int) -> List["GitHubFeature"]:  # type: ignore
        """Fetch all feature issues linked to a specific epic.

        Searches for issues that reference the epic using "Part of Epic #XXX" pattern.

        Args:
            epic_number: GitHub issue number of the epic

        Returns:
            List of GitHubFeature instances

        Raises:
            GitHubAuthError: If GitHub authentication is not available
            GitHubAPIError: If the GitHub API returns an error

        Examples:
            >>> service = GitHubService()
            >>> features = service.fetch_features_for_epic(577)
            >>> len(features)
            3
        """
        self._ensure_authenticated()

        try:
            # Search for issues mentioning "Part of Epic #XXX"
            search_query = f"is:open part of epic #{epic_number}"

            result = subprocess.run(
                [
                    "gh",
                    "issue",
                    "list",
                    "--search",
                    search_query,
                    "--json",
                    "number,title,labels,state,url",
                    "--limit",
                    "100",
                ],
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )

            if result.returncode != 0:
                if "rate limit" in result.stderr.lower():
                    raise GitHubAPIError(
                        "GitHub API rate limit exceeded. Try again later."
                    )
                raise GitHubAPIError(f"GitHub CLI error: {result.stderr}")

            issues_data = json.loads(result.stdout)

            # Import here to avoid circular dependency
            from doit_toolkit_cli.models.github_feature import GitHubFeature

            features = []
            for issue_data in issues_data:
                try:
                    feature = GitHubFeature.from_gh_json(issue_data, epic_number)
                    features.append(feature)
                except (ValueError, KeyError) as e:
                    print(f"Warning: Skipping malformed feature #{issue_data.get('number')}: {e}")
                    continue

            return features

        except subprocess.TimeoutExpired:
            raise GitHubAPIError(f"GitHub CLI timeout after {self.timeout} seconds")
        except json.JSONDecodeError as e:
            raise GitHubAPIError(f"Failed to parse GitHub CLI response: {e}")

    def create_epic(
        self, title: str, body: str, priority: str = "P3", labels: Optional[List[str]] = None
    ) -> GitHubEpic:
        """Create a new GitHub epic issue.

        Args:
            title: Epic title
            body: Epic description/body text
            priority: Priority level (P1-P4). Default: P3
            labels: Additional labels to add. Default: None

        Returns:
            Created GitHubEpic instance

        Raises:
            GitHubAuthError: If GitHub authentication is not available
            GitHubAPIError: If the GitHub API returns an error

        Examples:
            >>> service = GitHubService()
            >>> epic = service.create_epic(
            ...     title="[Epic]: New Feature",
            ...     body="Description",
            ...     priority="P2"
            ... )
            >>> epic.title
            '[Epic]: New Feature'
        """
        self._ensure_authenticated()

        # Build label list
        all_labels = ["epic", f"priority:{priority}"]
        if labels:
            all_labels.extend(labels)

        labels_str = ",".join(all_labels)

        try:
            result = subprocess.run(
                [
                    "gh",
                    "issue",
                    "create",
                    "--title",
                    title,
                    "--body",
                    body,
                    "--label",
                    labels_str,
                ],
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )

            if result.returncode != 0:
                if "rate limit" in result.stderr.lower():
                    raise GitHubAPIError("GitHub API rate limit exceeded")
                raise GitHubAPIError(f"Failed to create epic: {result.stderr}")

            # Extract issue URL from output
            issue_url = result.stdout.strip()

            # Extract issue number from URL (e.g., https://github.com/owner/repo/issues/123)
            issue_number = int(issue_url.split("/")[-1])

            # Create GitHubEpic instance
            return GitHubEpic(
                number=issue_number,
                title=title,
                state="open",
                labels=all_labels,
                body=body,
                url=issue_url,
            )

        except subprocess.TimeoutExpired:
            raise GitHubAPIError(f"GitHub CLI timeout after {self.timeout} seconds")
        except (ValueError, IndexError) as e:
            raise GitHubAPIError(f"Failed to parse created issue URL: {e}")
