"""GitHub provider implementation using gh CLI.

This module implements the GitProvider interface for GitHub
using the gh CLI tool for API operations.
"""

import json
import subprocess
from datetime import datetime
from typing import Optional

from ...models.provider_models import (
    Issue,
    IssueCreateRequest,
    IssueFilters,
    IssueState,
    IssueType,
    IssueUpdateRequest,
    Label,
    Milestone,
    MilestoneCreateRequest,
    MilestoneState,
    PullRequest,
    PRCreateRequest,
    PRFilters,
    PRState,
)
from .base import GitProvider, ProviderType
from .exceptions import (
    AuthenticationError,
    NetworkError,
    ProviderError,
    RateLimitError,
    ResourceNotFoundError,
    ValidationError,
)


class GitHubLabelMapper:
    """Maps labels between unified format and GitHub format."""

    # Issue type to GitHub labels
    TYPE_TO_LABELS = {
        IssueType.BUG: ["bug"],
        IssueType.TASK: ["task"],
        IssueType.USER_STORY: ["enhancement"],
        IssueType.FEATURE: ["feature"],
        IssueType.EPIC: ["epic"],
    }

    # Reverse mapping
    LABEL_TO_TYPE = {
        "bug": IssueType.BUG,
        "task": IssueType.TASK,
        "enhancement": IssueType.USER_STORY,
        "feature": IssueType.FEATURE,
        "epic": IssueType.EPIC,
    }

    @classmethod
    def type_to_labels(cls, issue_type: IssueType) -> list[str]:
        """Convert issue type to GitHub labels."""
        return cls.TYPE_TO_LABELS.get(issue_type, [])

    @classmethod
    def labels_to_type(cls, labels: list[str]) -> IssueType:
        """Infer issue type from GitHub labels."""
        for label in labels:
            label_lower = label.lower()
            if label_lower in cls.LABEL_TO_TYPE:
                return cls.LABEL_TO_TYPE[label_lower]
        return IssueType.TASK  # Default


class GitHubProvider(GitProvider):
    """GitHub implementation using the gh CLI.

    This provider uses the gh CLI tool for all GitHub API operations,
    which handles authentication automatically.
    """

    def __init__(self, timeout: int = 30):
        """Initialize the GitHub provider.

        Args:
            timeout: Timeout in seconds for gh CLI commands.
        """
        self.timeout = timeout

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.GITHUB

    @property
    def name(self) -> str:
        return "GitHub"

    @property
    def is_available(self) -> bool:
        """Check if gh CLI is installed and authenticated."""
        try:
            result = subprocess.run(
                ["gh", "auth", "status"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    # -------------------------------------------------------------------------
    # Issue Operations
    # -------------------------------------------------------------------------

    def create_issue(self, request: IssueCreateRequest) -> Issue:
        """Create a new GitHub issue."""
        self._ensure_authenticated()

        # Build label list
        all_labels = list(request.labels)
        all_labels.extend(GitHubLabelMapper.type_to_labels(request.type))

        cmd = ["gh", "issue", "create", "--title", request.title]

        if request.body:
            cmd.extend(["--body", request.body])

        if all_labels:
            cmd.extend(["--label", ",".join(all_labels)])

        if request.milestone_id:
            cmd.extend(["--milestone", request.milestone_id])

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )

            if result.returncode != 0:
                self._handle_error(result.stderr)

            # Parse created issue URL
            url = result.stdout.strip()
            issue_number = url.split("/")[-1]

            # Fetch the created issue to get full details
            return self.get_issue(issue_number)

        except subprocess.TimeoutExpired:
            raise NetworkError("GitHub CLI timeout", is_timeout=True)

    def get_issue(self, issue_id: str) -> Issue:
        """Get a GitHub issue by number."""
        self._ensure_authenticated()
        provider_id = self._extract_provider_id(issue_id)

        try:
            result = subprocess.run(
                [
                    "gh", "issue", "view", provider_id,
                    "--json", "number,title,body,state,url,createdAt,updatedAt,labels,milestone"
                ],
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )

            if result.returncode != 0:
                if "not found" in result.stderr.lower():
                    raise ResourceNotFoundError("Issue", provider_id)
                self._handle_error(result.stderr)

            data = json.loads(result.stdout)
            return self._parse_issue(data)

        except subprocess.TimeoutExpired:
            raise NetworkError("GitHub CLI timeout", is_timeout=True)
        except json.JSONDecodeError as e:
            raise ProviderError(f"Failed to parse GitHub response: {e}")

    def list_issues(self, filters: Optional[IssueFilters] = None) -> list[Issue]:
        """List GitHub issues matching filters."""
        self._ensure_authenticated()

        cmd = [
            "gh", "issue", "list",
            "--json", "number,title,body,state,url,createdAt,updatedAt,labels,milestone"
        ]

        if filters:
            if filters.state:
                state_map = {
                    IssueState.OPEN: "open",
                    IssueState.CLOSED: "closed",
                }
                cmd.extend(["--state", state_map.get(filters.state, "open")])

            if filters.labels:
                for label in filters.labels:
                    cmd.extend(["--label", label])

            if filters.limit:
                cmd.extend(["--limit", str(filters.limit)])

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )

            if result.returncode != 0:
                self._handle_error(result.stderr)

            data = json.loads(result.stdout)
            return [self._parse_issue(item) for item in data]

        except subprocess.TimeoutExpired:
            raise NetworkError("GitHub CLI timeout", is_timeout=True)
        except json.JSONDecodeError as e:
            raise ProviderError(f"Failed to parse GitHub response: {e}")

    def update_issue(self, issue_id: str, updates: IssueUpdateRequest) -> Issue:
        """Update a GitHub issue."""
        self._ensure_authenticated()
        provider_id = self._extract_provider_id(issue_id)

        cmd = ["gh", "issue", "edit", provider_id]

        if updates.title:
            cmd.extend(["--title", updates.title])

        if updates.body:
            cmd.extend(["--body", updates.body])

        if updates.labels is not None:
            for label in updates.labels:
                cmd.extend(["--add-label", label])

        try:
            if len(cmd) > 3:  # Only run if there are updates
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                )

                if result.returncode != 0:
                    self._handle_error(result.stderr)

            # Handle state change separately
            if updates.state == IssueState.CLOSED:
                subprocess.run(
                    ["gh", "issue", "close", provider_id],
                    capture_output=True,
                    timeout=self.timeout,
                )
            elif updates.state == IssueState.OPEN:
                subprocess.run(
                    ["gh", "issue", "reopen", provider_id],
                    capture_output=True,
                    timeout=self.timeout,
                )

            return self.get_issue(provider_id)

        except subprocess.TimeoutExpired:
            raise NetworkError("GitHub CLI timeout", is_timeout=True)

    # -------------------------------------------------------------------------
    # Pull Request Operations
    # -------------------------------------------------------------------------

    def create_pull_request(self, request: PRCreateRequest) -> PullRequest:
        """Create a new GitHub pull request."""
        self._ensure_authenticated()

        cmd = [
            "gh", "pr", "create",
            "--title", request.title,
            "--head", request.source_branch,
            "--base", request.target_branch,
        ]

        if request.body:
            cmd.extend(["--body", request.body])

        if request.labels:
            cmd.extend(["--label", ",".join(request.labels)])

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )

            if result.returncode != 0:
                self._handle_error(result.stderr)

            # Parse created PR URL
            url = result.stdout.strip()
            pr_number = url.split("/")[-1]

            return self.get_pull_request(pr_number)

        except subprocess.TimeoutExpired:
            raise NetworkError("GitHub CLI timeout", is_timeout=True)

    def get_pull_request(self, pr_id: str) -> PullRequest:
        """Get a GitHub pull request by number."""
        self._ensure_authenticated()
        provider_id = self._extract_provider_id(pr_id)

        try:
            result = subprocess.run(
                [
                    "gh", "pr", "view", provider_id,
                    "--json", "number,title,body,state,url,createdAt,mergedAt,headRefName,baseRefName,labels"
                ],
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )

            if result.returncode != 0:
                if "not found" in result.stderr.lower():
                    raise ResourceNotFoundError("Pull Request", provider_id)
                self._handle_error(result.stderr)

            data = json.loads(result.stdout)
            return self._parse_pull_request(data)

        except subprocess.TimeoutExpired:
            raise NetworkError("GitHub CLI timeout", is_timeout=True)
        except json.JSONDecodeError as e:
            raise ProviderError(f"Failed to parse GitHub response: {e}")

    def list_pull_requests(
        self, filters: Optional[PRFilters] = None
    ) -> list[PullRequest]:
        """List GitHub pull requests matching filters."""
        self._ensure_authenticated()

        cmd = [
            "gh", "pr", "list",
            "--json", "number,title,body,state,url,createdAt,mergedAt,headRefName,baseRefName,labels"
        ]

        if filters:
            if filters.state:
                state_map = {
                    PRState.OPEN: "open",
                    PRState.MERGED: "merged",
                    PRState.CLOSED: "closed",
                }
                cmd.extend(["--state", state_map.get(filters.state, "open")])

            if filters.source_branch:
                cmd.extend(["--head", filters.source_branch])

            if filters.target_branch:
                cmd.extend(["--base", filters.target_branch])

            if filters.limit:
                cmd.extend(["--limit", str(filters.limit)])

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )

            if result.returncode != 0:
                self._handle_error(result.stderr)

            data = json.loads(result.stdout)
            return [self._parse_pull_request(item) for item in data]

        except subprocess.TimeoutExpired:
            raise NetworkError("GitHub CLI timeout", is_timeout=True)
        except json.JSONDecodeError as e:
            raise ProviderError(f"Failed to parse GitHub response: {e}")

    # -------------------------------------------------------------------------
    # Milestone Operations
    # -------------------------------------------------------------------------

    def create_milestone(self, request: MilestoneCreateRequest) -> Milestone:
        """Create a new GitHub milestone."""
        self._ensure_authenticated()
        repo_slug = self._get_repo_slug()

        cmd = [
            "gh", "api",
            f"repos/{repo_slug}/milestones",
            "--method", "POST",
            "--field", f"title={request.title}",
            "--field", "state=open",
        ]

        if request.description:
            cmd.extend(["--field", f"description={request.description}"])

        if request.due_date:
            cmd.extend(["--field", f"due_on={request.due_date.isoformat()}"])

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )

            if result.returncode != 0:
                if "422" in result.stderr:
                    raise ValidationError(f"Milestone '{request.title}' already exists")
                self._handle_error(result.stderr)

            data = json.loads(result.stdout)
            return self._parse_milestone(data)

        except subprocess.TimeoutExpired:
            raise NetworkError("GitHub CLI timeout", is_timeout=True)
        except json.JSONDecodeError as e:
            raise ProviderError(f"Failed to parse GitHub response: {e}")

    def get_milestone(self, milestone_id: str) -> Milestone:
        """Get a GitHub milestone by number."""
        self._ensure_authenticated()
        provider_id = self._extract_provider_id(milestone_id)
        repo_slug = self._get_repo_slug()

        try:
            result = subprocess.run(
                ["gh", "api", f"repos/{repo_slug}/milestones/{provider_id}"],
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )

            if result.returncode != 0:
                if "404" in result.stderr:
                    raise ResourceNotFoundError("Milestone", provider_id)
                self._handle_error(result.stderr)

            data = json.loads(result.stdout)
            return self._parse_milestone(data)

        except subprocess.TimeoutExpired:
            raise NetworkError("GitHub CLI timeout", is_timeout=True)
        except json.JSONDecodeError as e:
            raise ProviderError(f"Failed to parse GitHub response: {e}")

    def list_milestones(
        self, state: Optional[MilestoneState] = None
    ) -> list[Milestone]:
        """List GitHub milestones."""
        self._ensure_authenticated()
        repo_slug = self._get_repo_slug()

        try:
            result = subprocess.run(
                ["gh", "api", f"repos/{repo_slug}/milestones"],
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )

            if result.returncode != 0:
                self._handle_error(result.stderr)

            data = json.loads(result.stdout)

            # Filter by state if requested
            if state:
                state_str = "open" if state == MilestoneState.OPEN else "closed"
                data = [m for m in data if m.get("state") == state_str]

            return [self._parse_milestone(item) for item in data]

        except subprocess.TimeoutExpired:
            raise NetworkError("GitHub CLI timeout", is_timeout=True)
        except json.JSONDecodeError as e:
            raise ProviderError(f"Failed to parse GitHub response: {e}")

    # -------------------------------------------------------------------------
    # Helper Methods
    # -------------------------------------------------------------------------

    def _ensure_authenticated(self) -> None:
        """Verify gh CLI is available and authenticated."""
        try:
            result = subprocess.run(
                ["gh", "auth", "status"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode != 0:
                raise AuthenticationError(
                    "GitHub CLI not authenticated. Run: gh auth login",
                    provider="GitHub",
                )
        except FileNotFoundError:
            raise AuthenticationError(
                "GitHub CLI (gh) not installed. Install from: https://cli.github.com",
                provider="GitHub",
            )

    def _handle_error(self, stderr: str) -> None:
        """Convert gh CLI error to appropriate exception."""
        stderr_lower = stderr.lower()

        if "rate limit" in stderr_lower:
            raise RateLimitError("GitHub API rate limit exceeded")
        elif "not found" in stderr_lower or "404" in stderr:
            raise ResourceNotFoundError("Resource", "unknown")
        elif "unauthorized" in stderr_lower or "401" in stderr:
            raise AuthenticationError("GitHub authentication failed", provider="GitHub")
        elif "validation" in stderr_lower or "422" in stderr:
            raise ValidationError(f"GitHub validation error: {stderr}")
        else:
            raise ProviderError(f"GitHub error: {stderr}")

    def _get_repo_slug(self) -> str:
        """Get the repository slug (owner/repo) from git remote."""
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode != 0:
                raise ProviderError("Not in a git repository")

            remote_url = result.stdout.strip()

            # Parse GitHub URL
            if remote_url.startswith("git@github.com:"):
                slug = remote_url.replace("git@github.com:", "").replace(".git", "")
            elif "github.com/" in remote_url:
                slug = remote_url.split("github.com/")[1].replace(".git", "")
            else:
                raise ProviderError("Not a GitHub repository")

            return slug

        except subprocess.TimeoutExpired:
            raise NetworkError("Git command timeout", is_timeout=True)

    def _parse_issue(self, data: dict) -> Issue:
        """Parse gh CLI JSON output into Issue model."""
        labels = [Label(name=l["name"]) for l in data.get("labels", [])]
        label_names = [l["name"] for l in data.get("labels", [])]

        state = IssueState.OPEN if data.get("state", "").upper() == "OPEN" else IssueState.CLOSED

        milestone_id = None
        if data.get("milestone"):
            milestone_id = str(data["milestone"].get("number", ""))

        return Issue(
            id=self._make_unified_id("issue", str(data["number"])),
            provider_id=str(data["number"]),
            title=data["title"],
            body=data.get("body"),
            state=state,
            type=GitHubLabelMapper.labels_to_type(label_names),
            url=data["url"],
            created_at=self._parse_datetime(data.get("createdAt", "")),
            updated_at=self._parse_datetime(data.get("updatedAt", "")),
            labels=labels,
            milestone_id=milestone_id,
        )

    def _parse_pull_request(self, data: dict) -> PullRequest:
        """Parse gh CLI JSON output into PullRequest model."""
        labels = [Label(name=l["name"]) for l in data.get("labels", [])]

        state_str = data.get("state", "").upper()
        if state_str == "MERGED":
            state = PRState.MERGED
        elif state_str == "CLOSED":
            state = PRState.CLOSED
        else:
            state = PRState.OPEN

        merged_at = None
        if data.get("mergedAt"):
            merged_at = self._parse_datetime(data["mergedAt"])

        return PullRequest(
            id=self._make_unified_id("pr", str(data["number"])),
            provider_id=str(data["number"]),
            title=data["title"],
            body=data.get("body"),
            source_branch=data.get("headRefName", ""),
            target_branch=data.get("baseRefName", ""),
            state=state,
            url=data["url"],
            created_at=self._parse_datetime(data.get("createdAt", "")),
            labels=labels,
            merged_at=merged_at,
        )

    def _parse_milestone(self, data: dict) -> Milestone:
        """Parse gh API JSON output into Milestone model."""
        state = MilestoneState.OPEN if data.get("state") == "open" else MilestoneState.CLOSED

        due_date = None
        if data.get("due_on"):
            due_date = self._parse_datetime(data["due_on"])

        return Milestone(
            id=self._make_unified_id("ms", str(data["number"])),
            provider_id=str(data["number"]),
            title=data["title"],
            description=data.get("description"),
            state=state,
            due_date=due_date,
            issue_count=data.get("open_issues", 0) + data.get("closed_issues", 0),
            closed_issue_count=data.get("closed_issues", 0),
            url=data.get("html_url"),
        )

    def _parse_datetime(self, date_str: str) -> datetime:
        """Parse ISO datetime string."""
        if not date_str:
            return datetime.now()
        try:
            # Handle GitHub's datetime format
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except ValueError:
            return datetime.now()
