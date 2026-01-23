"""GitLab provider implementation.

This module provides a full implementation of the GitProvider interface
for GitLab using the REST API v4. Supports both gitlab.com and self-hosted
GitLab instances.

Features:
    - Personal Access Token (PAT) authentication
    - Issue management (create, read, update, list)
    - Merge request management (create, read, list)
    - Milestone management (create, read, update, list)
    - Label auto-creation and mapping
    - Self-hosted GitLab support
    - Rate limiting with exponential backoff
"""

from __future__ import annotations

import os
import ssl
from datetime import datetime
from typing import Any, Optional
from urllib.parse import quote

import httpx

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
    PRCreateRequest,
    PRFilters,
    PRState,
    PullRequest,
)
from .base import GitProvider, ProviderType, with_retry
from .exceptions import (
    AuthenticationError,
    NetworkError,
    ProviderError,
    RateLimitError,
    ResourceNotFoundError,
    ValidationError,
)


# =============================================================================
# GitLabLabelMapper - Maps between unified types and GitLab labels
# =============================================================================


class GitLabLabelMapper:
    """Maps between unified IssueType/priority and GitLab labels.

    GitLab doesn't have native issue types, so we use labels to categorize
    issues. This mapper handles the bidirectional conversion.
    """

    # Mapping from IssueType enum to GitLab label name
    TYPE_TO_LABEL: dict[IssueType, str] = {
        IssueType.EPIC: "Epic",
        IssueType.FEATURE: "Feature",
        IssueType.BUG: "Bug",
        IssueType.TASK: "Task",
        IssueType.USER_STORY: "User Story",
    }

    # Reverse mapping from GitLab label to IssueType
    LABEL_TO_TYPE: dict[str, IssueType] = {v: k for k, v in TYPE_TO_LABEL.items()}

    # Priority label mapping using GitLab scoped labels
    PRIORITY_TO_LABEL: dict[str, str] = {
        "P1": "priority::1",
        "P2": "priority::2",
        "P3": "priority::3",
        "P4": "priority::4",
    }

    # Reverse priority mapping
    LABEL_TO_PRIORITY: dict[str, str] = {v: k for k, v in PRIORITY_TO_LABEL.items()}

    # Default colors for auto-created labels
    LABEL_COLORS: dict[str, str] = {
        "Epic": "#6699cc",
        "Feature": "#428bca",
        "Bug": "#d9534f",
        "Task": "#5cb85c",
        "User Story": "#f0ad4e",
        "priority::1": "#d9534f",
        "priority::2": "#f0ad4e",
        "priority::3": "#5bc0de",
        "priority::4": "#777777",
    }

    def to_gitlab_labels(
        self,
        issue_type: IssueType,
        priority: Optional[str] = None,
        extra_labels: Optional[list[str]] = None,
    ) -> list[str]:
        """Convert unified issue type and priority to GitLab labels.

        Args:
            issue_type: The unified issue type.
            priority: Optional priority string (P1, P2, P3, P4).
            extra_labels: Additional labels to include.

        Returns:
            List of GitLab label names.
        """
        labels: list[str] = []

        # Add type label
        if issue_type in self.TYPE_TO_LABEL:
            labels.append(self.TYPE_TO_LABEL[issue_type])

        # Add priority label
        if priority and priority in self.PRIORITY_TO_LABEL:
            labels.append(self.PRIORITY_TO_LABEL[priority])

        # Add extra labels
        if extra_labels:
            labels.extend(extra_labels)

        return labels

    def from_gitlab_labels(
        self, labels: list[str]
    ) -> tuple[IssueType, Optional[str], list[str]]:
        """Extract unified issue type and priority from GitLab labels.

        Args:
            labels: List of GitLab label names.

        Returns:
            Tuple of (issue_type, priority, remaining_labels).
        """
        issue_type = IssueType.TASK  # Default
        priority: Optional[str] = None
        remaining: list[str] = []

        for label in labels:
            if label in self.LABEL_TO_TYPE:
                issue_type = self.LABEL_TO_TYPE[label]
            elif label in self.LABEL_TO_PRIORITY:
                priority = self.LABEL_TO_PRIORITY[label]
            else:
                remaining.append(label)

        return issue_type, priority, remaining

    def get_all_type_labels(self) -> list[str]:
        """Get all type label names for auto-creation."""
        return list(self.TYPE_TO_LABEL.values())

    def get_all_priority_labels(self) -> list[str]:
        """Get all priority label names for auto-creation."""
        return list(self.PRIORITY_TO_LABEL.values())

    def get_label_color(self, label_name: str) -> str:
        """Get the default color for a label."""
        return self.LABEL_COLORS.get(label_name, "#428bca")


# =============================================================================
# GitLabAPIClient - HTTP client wrapper for GitLab REST API v4
# =============================================================================


class GitLabAPIClient:
    """HTTP client for GitLab REST API v4.

    Handles authentication, error responses, and request/response processing.
    Supports both gitlab.com and self-hosted GitLab instances.

    Args:
        project_path: URL-encoded project path (e.g., "owner%2Frepo").
        host: GitLab host (default: "gitlab.com").
        token: Personal Access Token (defaults to GITLAB_TOKEN env var).
        timeout: Request timeout in seconds.
    """

    def __init__(
        self,
        project_path: str,
        host: str = "gitlab.com",
        token: Optional[str] = None,
        timeout: int = 30,
    ):
        self.project_path = project_path
        self.host = host
        self.base_url = f"https://{host}/api/v4"
        self.token = token or os.environ.get("GITLAB_TOKEN", "")
        self.timeout = timeout
        self._client: Optional[httpx.Client] = None

    @property
    def client(self) -> httpx.Client:
        """Lazy-initialize and return the HTTP client."""
        if self._client is None:
            self._client = httpx.Client(
                base_url=self.base_url,
                headers={
                    "PRIVATE-TOKEN": self.token,
                    "Content-Type": "application/json",
                },
                timeout=self.timeout,
            )
        return self._client

    def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            self._client.close()
            self._client = None

    def _handle_response(self, response: httpx.Response) -> dict[str, Any]:
        """Handle HTTP response and raise appropriate exceptions.

        Args:
            response: The httpx Response object.

        Returns:
            Parsed JSON response as dict.

        Raises:
            AuthenticationError: For 401/403 responses.
            ResourceNotFoundError: For 404 responses.
            RateLimitError: For 429 responses.
            NetworkError: For 5xx responses or SSL errors.
            ValidationError: For 400 responses.
            ProviderError: For other error responses.
        """
        try:
            if response.status_code == 401:
                raise AuthenticationError(
                    "GitLab authentication failed. Check your GITLAB_TOKEN.",
                    provider="gitlab",
                )

            if response.status_code == 403:
                raise AuthenticationError(
                    "Insufficient permissions for this operation. "
                    "Ensure your token has 'api' scope.",
                    provider="gitlab",
                )

            if response.status_code == 404:
                raise ResourceNotFoundError(
                    "resource",
                    "unknown",
                )

            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 60))
                raise RateLimitError(
                    "GitLab API rate limit exceeded.",
                    retry_after=retry_after,
                )

            if response.status_code >= 500:
                raise NetworkError(
                    f"GitLab server error ({response.status_code}). Try again later."
                )

            if response.status_code == 400:
                error_data = response.json() if response.content else {}
                message = error_data.get("message", "Validation error")
                if isinstance(message, dict):
                    # GitLab returns field-specific errors as dict
                    field = next(iter(message.keys()), None)
                    msg = message.get(field, ["Validation error"])[0]
                    raise ValidationError(f"{field}: {msg}", field=field)
                raise ValidationError(str(message))

            if not response.is_success:
                error_data = response.json() if response.content else {}
                message = error_data.get("message", f"Error {response.status_code}")
                raise ProviderError(f"GitLab API error: {message}")

            # Return empty dict for 204 No Content
            if response.status_code == 204 or not response.content:
                return {}

            return response.json()

        except ssl.SSLError as e:
            raise NetworkError(
                f"SSL certificate error connecting to {self.host}. "
                "For self-hosted GitLab, ensure your certificate is valid.",
                cause=e,
            )
        except httpx.TimeoutException as e:
            raise NetworkError(
                "Request timed out. Check your network connection.",
                cause=e,
                is_timeout=True,
            )
        except httpx.ConnectError as e:
            raise NetworkError(
                f"Could not connect to {self.host}. Check your network connection.",
                cause=e,
            )

    def get(
        self, endpoint: str, params: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """Make a GET request to the GitLab API.

        Args:
            endpoint: API endpoint path.
            params: Optional query parameters.

        Returns:
            Parsed JSON response.
        """
        response = self.client.get(endpoint, params=params)
        return self._handle_response(response)

    def get_list(
        self, endpoint: str, params: Optional[dict[str, Any]] = None
    ) -> list[dict[str, Any]]:
        """Make a GET request expecting a list response.

        Args:
            endpoint: API endpoint path.
            params: Optional query parameters.

        Returns:
            List of parsed JSON objects.
        """
        response = self.client.get(endpoint, params=params)
        if response.status_code == 401:
            raise AuthenticationError(
                "GitLab authentication failed. Check your GITLAB_TOKEN.",
                provider="gitlab",
            )
        if response.status_code == 403:
            raise AuthenticationError(
                "Insufficient permissions for this operation.",
                provider="gitlab",
            )
        if not response.is_success:
            self._handle_response(response)
        return response.json()

    def post(
        self, endpoint: str, data: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """Make a POST request to the GitLab API.

        Args:
            endpoint: API endpoint path.
            data: Request body data.

        Returns:
            Parsed JSON response.
        """
        response = self.client.post(endpoint, json=data or {})
        return self._handle_response(response)

    def put(
        self, endpoint: str, data: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """Make a PUT request to the GitLab API.

        Args:
            endpoint: API endpoint path.
            data: Request body data.

        Returns:
            Parsed JSON response.
        """
        response = self.client.put(endpoint, json=data or {})
        return self._handle_response(response)

    def validate_token(self) -> dict[str, Any]:
        """Validate the token by fetching current user info.

        Returns:
            User information dict.

        Raises:
            AuthenticationError: If token is invalid.
        """
        return self.get("/user")


# =============================================================================
# GitLabProvider - Full implementation of GitProvider interface
# =============================================================================


class GitLabProvider(GitProvider):
    """GitLab implementation of the GitProvider interface.

    This provider uses the GitLab REST API v4 to interact with GitLab
    repositories. It supports both gitlab.com and self-hosted instances.

    Usage:
        provider = GitLabProvider(project_path="owner/repo")
        if provider.is_available:
            issue = provider.create_issue(IssueCreateRequest(title="Bug fix"))

    Args:
        project_path: Project path in format "owner/repo" (will be URL-encoded).
        host: GitLab host (default: "gitlab.com").
        token: Personal Access Token (defaults to GITLAB_TOKEN env var).
        timeout: Timeout in seconds for API requests.
    """

    def __init__(
        self,
        project_path: str = "",
        host: str = "gitlab.com",
        token: Optional[str] = None,
        timeout: int = 30,
    ):
        # URL-encode the project path for API calls
        self._project_path = project_path
        self._encoded_path = quote(project_path, safe="") if project_path else ""
        self._host = host
        self._token = token
        self._timeout = timeout
        self._client: Optional[GitLabAPIClient] = None
        self._label_mapper = GitLabLabelMapper()
        self._validated = False

    @property
    def _api(self) -> GitLabAPIClient:
        """Lazy-initialize and return the API client."""
        if self._client is None:
            self._client = GitLabAPIClient(
                project_path=self._encoded_path,
                host=self._host,
                token=self._token,
                timeout=self._timeout,
            )
        return self._client

    # -------------------------------------------------------------------------
    # Provider Properties
    # -------------------------------------------------------------------------

    @property
    def provider_type(self) -> ProviderType:
        """Return the GitLab provider type."""
        return ProviderType.GITLAB

    @property
    def name(self) -> str:
        """Return the human-readable provider name."""
        return "GitLab"

    @property
    def is_available(self) -> bool:
        """Check if the GitLab provider is properly configured.

        Returns:
            True if GITLAB_TOKEN is set and valid, False otherwise.
        """
        token = self._token or os.environ.get("GITLAB_TOKEN", "")
        if not token:
            return False

        if self._validated:
            return True

        try:
            self._api.validate_token()
            self._validated = True
            return True
        except (AuthenticationError, NetworkError):
            return False

    def validate_token(self) -> dict[str, Any]:
        """Validate the configured token and return user info.

        Returns:
            Dict containing user information (id, username, name, email).

        Raises:
            AuthenticationError: If token is invalid or missing.
        """
        token = self._token or os.environ.get("GITLAB_TOKEN", "")
        if not token:
            raise AuthenticationError(
                "GITLAB_TOKEN environment variable is not set.",
                provider="gitlab",
            )
        return self._api.validate_token()

    # -------------------------------------------------------------------------
    # Response Parsers
    # -------------------------------------------------------------------------

    def _parse_issue(self, data: dict[str, Any]) -> Issue:
        """Parse GitLab issue JSON into unified Issue model.

        Args:
            data: GitLab issue API response.

        Returns:
            Unified Issue object.
        """
        # Extract labels as strings
        label_names = [
            lbl if isinstance(lbl, str) else lbl.get("name", "")
            for lbl in data.get("labels", [])
        ]

        # Parse issue type and priority from labels
        issue_type, _, remaining = self._label_mapper.from_gitlab_labels(label_names)

        # Map GitLab state to unified state
        state = IssueState.CLOSED if data.get("state") == "closed" else IssueState.OPEN

        # Parse timestamps
        created_at = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
        updated_at = datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))

        # Extract milestone ID if present
        milestone_id = None
        if data.get("milestone"):
            milestone_id = str(data["milestone"].get("id", ""))

        return Issue(
            id=self._make_unified_id("issue", str(data["iid"])),
            provider_id=str(data["iid"]),
            title=data["title"],
            body=data.get("description"),
            state=state,
            type=issue_type,
            url=data["web_url"],
            created_at=created_at,
            updated_at=updated_at,
            labels=[Label(name=lbl) for lbl in remaining],
            milestone_id=milestone_id,
        )

    def _parse_pull_request(self, data: dict[str, Any]) -> PullRequest:
        """Parse GitLab merge request JSON into unified PullRequest model.

        Args:
            data: GitLab merge request API response.

        Returns:
            Unified PullRequest object.
        """
        # Extract labels
        label_names = [
            lbl if isinstance(lbl, str) else lbl.get("name", "")
            for lbl in data.get("labels", [])
        ]

        # Map GitLab state to unified state
        gl_state = data.get("state", "opened")
        if gl_state == "merged":
            state = PRState.MERGED
        elif gl_state == "closed":
            state = PRState.CLOSED
        else:
            state = PRState.OPEN

        # Parse timestamps
        created_at = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
        merged_at = None
        if data.get("merged_at"):
            merged_at = datetime.fromisoformat(data["merged_at"].replace("Z", "+00:00"))

        return PullRequest(
            id=self._make_unified_id("mr", str(data["iid"])),
            provider_id=str(data["iid"]),
            title=data["title"],
            body=data.get("description"),
            source_branch=data["source_branch"],
            target_branch=data["target_branch"],
            state=state,
            url=data["web_url"],
            created_at=created_at,
            labels=[Label(name=lbl) for lbl in label_names],
            merged_at=merged_at,
        )

    def _parse_milestone(self, data: dict[str, Any]) -> Milestone:
        """Parse GitLab milestone JSON into unified Milestone model.

        Args:
            data: GitLab milestone API response.

        Returns:
            Unified Milestone object.
        """
        # Map GitLab state to unified state
        state = (
            MilestoneState.CLOSED if data.get("state") == "closed" else MilestoneState.OPEN
        )

        # Parse due date if present
        due_date = None
        if data.get("due_date"):
            due_date = datetime.strptime(data["due_date"], "%Y-%m-%d")

        return Milestone(
            id=self._make_unified_id("ms", str(data["id"])),
            provider_id=str(data["id"]),
            title=data["title"],
            description=data.get("description"),
            state=state,
            due_date=due_date,
            url=data.get("web_url"),
        )

    # -------------------------------------------------------------------------
    # Label Management
    # -------------------------------------------------------------------------

    def _ensure_labels_exist(self, labels: list[str]) -> None:
        """Ensure required labels exist in the GitLab project.

        Creates any missing labels with default colors.

        Args:
            labels: List of label names to ensure exist.
        """
        # Get existing labels
        try:
            existing = self._api.get_list(f"/projects/{self._encoded_path}/labels")
            existing_names = {lbl["name"] for lbl in existing}
        except ProviderError:
            existing_names = set()

        # Create missing labels
        for label in labels:
            if label not in existing_names:
                try:
                    self._api.post(
                        f"/projects/{self._encoded_path}/labels",
                        {
                            "name": label,
                            "color": self._label_mapper.get_label_color(label),
                        },
                    )
                except ValidationError:
                    # Label might already exist (race condition)
                    pass

    def _create_issue_link(
        self, source_iid: int, target_iid: int, link_type: str = "relates_to"
    ) -> None:
        """Create a link between two issues.

        Args:
            source_iid: The source issue IID.
            target_iid: The target issue IID.
            link_type: The link type (relates_to, blocks, is_blocked_by).
        """
        try:
            self._api.post(
                f"/projects/{self._encoded_path}/issues/{source_iid}/links",
                {
                    "target_project_id": self._encoded_path,
                    "target_issue_iid": target_iid,
                    "link_type": link_type,
                },
            )
        except ProviderError:
            # Link might already exist or not be supported
            pass

    # -------------------------------------------------------------------------
    # Issue Operations
    # -------------------------------------------------------------------------

    @with_retry(max_retries=3)
    def create_issue(self, request: IssueCreateRequest) -> Issue:
        """Create a new issue in GitLab.

        Args:
            request: Issue creation parameters.

        Returns:
            The created Issue with populated ID and URL.

        Raises:
            AuthenticationError: If not authenticated.
            ValidationError: If request parameters are invalid.
        """
        # Build labels list
        labels = self._label_mapper.to_gitlab_labels(
            request.type,
            extra_labels=request.labels,
        )

        # Ensure labels exist
        self._ensure_labels_exist(labels)

        # Build request payload
        payload: dict[str, Any] = {
            "title": request.title,
        }

        if request.body:
            payload["description"] = request.body

        if labels:
            payload["labels"] = ",".join(labels)

        if request.milestone_id:
            payload["milestone_id"] = int(
                self._extract_provider_id(request.milestone_id)
            )

        # Create issue
        data = self._api.post(f"/projects/{self._encoded_path}/issues", payload)
        return self._parse_issue(data)

    @with_retry(max_retries=3)
    def get_issue(self, issue_id: str) -> Issue:
        """Get an issue by its ID.

        Args:
            issue_id: The issue ID (unified or provider-specific IID).

        Returns:
            The Issue object.

        Raises:
            ResourceNotFoundError: If the issue does not exist.
        """
        iid = self._extract_provider_id(issue_id)
        try:
            data = self._api.get(f"/projects/{self._encoded_path}/issues/{iid}")
            return self._parse_issue(data)
        except ResourceNotFoundError:
            raise ResourceNotFoundError("Issue", issue_id)

    @with_retry(max_retries=3)
    def list_issues(self, filters: Optional[IssueFilters] = None) -> list[Issue]:
        """List issues matching the given filters.

        Args:
            filters: Optional filters to apply.

        Returns:
            List of matching Issue objects.
        """
        params: dict[str, Any] = {"per_page": 100}

        if filters:
            if filters.state:
                # GitLab uses 'opened' instead of 'open'
                state_map = {IssueState.OPEN: "opened", IssueState.CLOSED: "closed"}
                params["state"] = state_map.get(filters.state, "all")

            if filters.labels:
                params["labels"] = ",".join(filters.labels)

            if filters.milestone_id:
                params["milestone_id"] = self._extract_provider_id(filters.milestone_id)

            if filters.limit:
                params["per_page"] = min(filters.limit, 100)

        data = self._api.get_list(f"/projects/{self._encoded_path}/issues", params)
        return [self._parse_issue(item) for item in data]

    @with_retry(max_retries=3)
    def update_issue(self, issue_id: str, updates: IssueUpdateRequest) -> Issue:
        """Update an existing issue.

        Args:
            issue_id: The issue ID to update.
            updates: The fields to update.

        Returns:
            The updated Issue object.

        Raises:
            ResourceNotFoundError: If the issue does not exist.
        """
        iid = self._extract_provider_id(issue_id)
        payload: dict[str, Any] = {}

        if updates.title is not None:
            payload["title"] = updates.title

        if updates.body is not None:
            payload["description"] = updates.body

        if updates.state is not None:
            # GitLab uses state_event to change state
            payload["state_event"] = (
                "close" if updates.state == IssueState.CLOSED else "reopen"
            )

        if updates.labels is not None:
            self._ensure_labels_exist(updates.labels)
            payload["labels"] = ",".join(updates.labels)

        if updates.milestone_id is not None:
            payload["milestone_id"] = int(
                self._extract_provider_id(updates.milestone_id)
            )

        try:
            data = self._api.put(
                f"/projects/{self._encoded_path}/issues/{iid}", payload
            )
            return self._parse_issue(data)
        except ResourceNotFoundError:
            raise ResourceNotFoundError("Issue", issue_id)

    # -------------------------------------------------------------------------
    # Pull Request (Merge Request) Operations
    # -------------------------------------------------------------------------

    @with_retry(max_retries=3)
    def create_pull_request(self, request: PRCreateRequest) -> PullRequest:
        """Create a new merge request in GitLab.

        Args:
            request: Merge request creation parameters.

        Returns:
            The created PullRequest with populated ID and URL.

        Raises:
            AuthenticationError: If not authenticated.
            ValidationError: If request parameters are invalid.
        """
        payload: dict[str, Any] = {
            "source_branch": request.source_branch,
            "target_branch": request.target_branch,
            "title": request.title,
        }

        if request.body:
            payload["description"] = request.body

        if request.labels:
            self._ensure_labels_exist(request.labels)
            payload["labels"] = ",".join(request.labels)

        data = self._api.post(
            f"/projects/{self._encoded_path}/merge_requests", payload
        )
        return self._parse_pull_request(data)

    @with_retry(max_retries=3)
    def get_pull_request(self, pr_id: str) -> PullRequest:
        """Get a merge request by its ID.

        Args:
            pr_id: The merge request ID (unified or provider-specific IID).

        Returns:
            The PullRequest object.

        Raises:
            ResourceNotFoundError: If the MR does not exist.
        """
        iid = self._extract_provider_id(pr_id)
        try:
            data = self._api.get(
                f"/projects/{self._encoded_path}/merge_requests/{iid}"
            )
            return self._parse_pull_request(data)
        except ResourceNotFoundError:
            raise ResourceNotFoundError("Merge Request", pr_id)

    @with_retry(max_retries=3)
    def list_pull_requests(
        self, filters: Optional[PRFilters] = None
    ) -> list[PullRequest]:
        """List merge requests matching the given filters.

        Args:
            filters: Optional filters to apply.

        Returns:
            List of matching PullRequest objects.
        """
        params: dict[str, Any] = {"per_page": 100}

        if filters:
            if filters.state:
                state_map = {
                    PRState.OPEN: "opened",
                    PRState.MERGED: "merged",
                    PRState.CLOSED: "closed",
                }
                params["state"] = state_map.get(filters.state, "all")

            if filters.source_branch:
                params["source_branch"] = filters.source_branch

            if filters.target_branch:
                params["target_branch"] = filters.target_branch

            if filters.limit:
                params["per_page"] = min(filters.limit, 100)

        data = self._api.get_list(
            f"/projects/{self._encoded_path}/merge_requests", params
        )
        return [self._parse_pull_request(item) for item in data]

    # -------------------------------------------------------------------------
    # Milestone Operations
    # -------------------------------------------------------------------------

    @with_retry(max_retries=3)
    def create_milestone(self, request: MilestoneCreateRequest) -> Milestone:
        """Create a new milestone in GitLab.

        Args:
            request: Milestone creation parameters.

        Returns:
            The created Milestone with populated ID.

        Raises:
            AuthenticationError: If not authenticated.
            ValidationError: If request parameters are invalid.
        """
        payload: dict[str, Any] = {
            "title": request.title,
        }

        if request.description:
            payload["description"] = request.description

        if request.due_date:
            payload["due_date"] = request.due_date.strftime("%Y-%m-%d")

        data = self._api.post(f"/projects/{self._encoded_path}/milestones", payload)
        return self._parse_milestone(data)

    @with_retry(max_retries=3)
    def get_milestone(self, milestone_id: str) -> Milestone:
        """Get a milestone by its ID.

        Args:
            milestone_id: The milestone ID (unified or provider-specific).

        Returns:
            The Milestone object.

        Raises:
            ResourceNotFoundError: If the milestone does not exist.
        """
        ms_id = self._extract_provider_id(milestone_id)
        try:
            data = self._api.get(f"/projects/{self._encoded_path}/milestones/{ms_id}")
            return self._parse_milestone(data)
        except ResourceNotFoundError:
            raise ResourceNotFoundError("Milestone", milestone_id)

    @with_retry(max_retries=3)
    def list_milestones(
        self, state: Optional[MilestoneState] = None
    ) -> list[Milestone]:
        """List milestones.

        Args:
            state: Optional state filter (open/closed).

        Returns:
            List of Milestone objects.
        """
        params: dict[str, Any] = {"per_page": 100}

        if state:
            params["state"] = "active" if state == MilestoneState.OPEN else "closed"

        data = self._api.get_list(f"/projects/{self._encoded_path}/milestones", params)
        return [self._parse_milestone(item) for item in data]

    def update_milestone(
        self,
        milestone_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        due_date: Optional[datetime] = None,
        state: Optional[MilestoneState] = None,
    ) -> Milestone:
        """Update an existing milestone.

        Args:
            milestone_id: The milestone ID to update.
            title: New title (optional).
            description: New description (optional).
            due_date: New due date (optional).
            state: New state (optional).

        Returns:
            The updated Milestone object.

        Raises:
            ResourceNotFoundError: If the milestone does not exist.
        """
        ms_id = self._extract_provider_id(milestone_id)
        payload: dict[str, Any] = {}

        if title is not None:
            payload["title"] = title

        if description is not None:
            payload["description"] = description

        if due_date is not None:
            payload["due_date"] = due_date.strftime("%Y-%m-%d")

        if state is not None:
            # GitLab uses state_event to change state
            payload["state_event"] = (
                "close" if state == MilestoneState.CLOSED else "activate"
            )

        try:
            data = self._api.put(
                f"/projects/{self._encoded_path}/milestones/{ms_id}", payload
            )
            return self._parse_milestone(data)
        except ResourceNotFoundError:
            raise ResourceNotFoundError("Milestone", milestone_id)
