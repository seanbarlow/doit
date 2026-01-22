"""GitHub service for interacting with GitHub issues via gh CLI.

This service provides methods to fetch epics, features, and create issues
using the GitHub CLI (gh) command.
"""

import json
import subprocess
from typing import List, Optional

from doit_toolkit_cli.models.github_epic import GitHubEpic
from doit_toolkit_cli.models.milestone import Milestone
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

    def get_all_milestones(self, state: str = "open") -> List[Milestone]:
        """Fetch all GitHub milestones for the repository.

        Args:
            state: Milestone state to filter by (open, closed, or all). Default: open

        Returns:
            List of Milestone instances

        Raises:
            GitHubAuthError: If GitHub authentication is not available
            GitHubAPIError: If the GitHub API returns an error

        Examples:
            >>> service = GitHubService()
            >>> milestones = service.get_all_milestones()
            >>> len(milestones)
            4
        """
        self._ensure_authenticated()

        try:
            # Get repository slug first
            repo_slug = self._get_repo_slug()

            # Fetch milestones via gh API
            result = subprocess.run(
                [
                    "gh",
                    "api",
                    f"repos/{repo_slug}/milestones",
                    "--jq",
                    ".",
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

            # Parse JSON response
            milestones_data = json.loads(result.stdout)

            # Filter by state if requested
            if state != "all":
                milestones_data = [m for m in milestones_data if m["state"] == state]

            # Convert to Milestone instances
            milestones = []
            for ms_data in milestones_data:
                try:
                    milestone = Milestone(
                        number=ms_data["number"],
                        title=ms_data["title"],
                        description=ms_data.get("description", ""),
                        state=ms_data["state"],
                        url=ms_data["html_url"],
                    )
                    milestones.append(milestone)
                except (ValueError, KeyError) as e:
                    print(f"Warning: Skipping malformed milestone: {e}")
                    continue

            return milestones

        except subprocess.TimeoutExpired:
            raise GitHubAPIError(
                f"GitHub CLI timeout after {self.timeout} seconds."
            )
        except json.JSONDecodeError as e:
            raise GitHubAPIError(f"Failed to parse GitHub CLI response: {e}")

    def create_milestone(self, title: str, description: str) -> Milestone:
        """Create a new GitHub milestone.

        Args:
            title: Milestone title (e.g., "P1 - Critical")
            description: Milestone description

        Returns:
            Created Milestone instance

        Raises:
            GitHubAuthError: If GitHub authentication is not available
            GitHubAPIError: If the GitHub API returns an error

        Examples:
            >>> service = GitHubService()
            >>> milestone = service.create_milestone(
            ...     title="P1 - Critical",
            ...     description="Auto-managed by doit..."
            ... )
            >>> milestone.title
            'P1 - Critical'
        """
        self._ensure_authenticated()

        try:
            # Get repository slug first
            repo_slug = self._get_repo_slug()

            # Create milestone via gh API
            result = subprocess.run(
                [
                    "gh",
                    "api",
                    f"repos/{repo_slug}/milestones",
                    "--method",
                    "POST",
                    "--field",
                    f"title={title}",
                    "--field",
                    f"description={description}",
                    "--field",
                    "state=open",
                ],
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )

            if result.returncode != 0:
                if "rate limit" in result.stderr.lower():
                    raise GitHubAPIError("GitHub API rate limit exceeded")
                if "422" in result.stderr:
                    raise GitHubAPIError(
                        f"Milestone with title '{title}' already exists"
                    )
                raise GitHubAPIError(f"Failed to create milestone: {result.stderr}")

            # Parse JSON response
            ms_data = json.loads(result.stdout)

            # Create Milestone instance
            return Milestone(
                number=ms_data["number"],
                title=ms_data["title"],
                description=ms_data["description"],
                state=ms_data["state"],
                url=ms_data["html_url"],
            )

        except subprocess.TimeoutExpired:
            raise GitHubAPIError(f"GitHub CLI timeout after {self.timeout} seconds")
        except json.JSONDecodeError as e:
            raise GitHubAPIError(f"Failed to parse GitHub CLI response: {e}")

    def _get_repo_slug(self) -> str:
        """Get the repository slug (owner/repo) from git remote.

        Returns:
            Repository slug in format "owner/repo"

        Raises:
            GitHubAPIError: If not a GitHub repository or no remote found
        """
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode != 0:
                raise GitHubAPIError("Failed to get git remote: Not in a git repository?")

            remote_url = result.stdout.strip()

            # Parse GitHub URL (supports both HTTPS and SSH)
            # HTTPS: https://github.com/owner/repo.git
            # SSH: git@github.com:owner/repo.git
            if "github.com" not in remote_url:
                raise GitHubAPIError("Not a GitHub repository")

            if remote_url.startswith("git@github.com:"):
                # SSH format
                slug = remote_url.replace("git@github.com:", "").replace(".git", "")
            elif "github.com/" in remote_url:
                # HTTPS format
                slug = remote_url.split("github.com/")[1].replace(".git", "")
            else:
                raise GitHubAPIError("Unable to parse GitHub repository URL")

            return slug

        except subprocess.TimeoutExpired:
            raise GitHubAPIError("Git command timeout")
        except Exception as e:
            raise GitHubAPIError(f"Failed to get repository slug: {e}")

    def close_milestone(self, milestone_number: int) -> Milestone:
        """Close a GitHub milestone.

        Args:
            milestone_number: GitHub milestone number to close

        Returns:
            Updated Milestone instance

        Raises:
            GitHubAuthError: If GitHub authentication is not available
            GitHubAPIError: If the GitHub API returns an error

        Examples:
            >>> service = GitHubService()
            >>> milestone = service.close_milestone(7)
            >>> milestone.state
            'closed'
        """
        self._ensure_authenticated()

        try:
            # Get repository slug first
            repo_slug = self._get_repo_slug()

            # Close milestone via gh API PATCH
            result = subprocess.run(
                [
                    "gh",
                    "api",
                    f"repos/{repo_slug}/milestones/{milestone_number}",
                    "--method",
                    "PATCH",
                    "--field",
                    "state=closed",
                ],
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )

            if result.returncode != 0:
                if "rate limit" in result.stderr.lower():
                    raise GitHubAPIError("GitHub API rate limit exceeded")
                if "404" in result.stderr:
                    raise GitHubAPIError(
                        f"Milestone #{milestone_number} not found"
                    )
                raise GitHubAPIError(f"Failed to close milestone: {result.stderr}")

            # Parse JSON response
            ms_data = json.loads(result.stdout)

            # Create Milestone instance
            return Milestone(
                number=ms_data["number"],
                title=ms_data["title"],
                description=ms_data.get("description", ""),
                state=ms_data["state"],
                url=ms_data["html_url"],
            )

        except subprocess.TimeoutExpired:
            raise GitHubAPIError(f"GitHub CLI timeout after {self.timeout} seconds")
        except json.JSONDecodeError as e:
            raise GitHubAPIError(f"Failed to parse GitHub CLI response: {e}")
