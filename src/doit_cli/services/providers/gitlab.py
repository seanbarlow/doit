"""GitLab provider stub implementation.

This module provides a stub implementation of the GitProvider interface
for GitLab. Full implementation is planned for a future release.
"""

from typing import Optional

from ...models.provider_models import (
    Issue,
    IssueCreateRequest,
    IssueFilters,
    IssueUpdateRequest,
    Milestone,
    MilestoneCreateRequest,
    MilestoneState,
    PullRequest,
    PRCreateRequest,
    PRFilters,
)
from .base import GitProvider, ProviderType
from .exceptions import ProviderNotImplementedError


class GitLabProvider(GitProvider):
    """GitLab stub implementation.

    This provider is a placeholder for future GitLab support.
    All operations currently raise ProviderNotImplementedError with
    guidance on the feature's development status.

    Note:
        GitLab support is planned for a future release.
        See https://github.com/seanbarlow/doit/issues for status.
    """

    def __init__(self, timeout: int = 30):
        """Initialize the GitLab provider.

        Args:
            timeout: Timeout in seconds for API requests (unused in stub).
        """
        self.timeout = timeout

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.GITLAB

    @property
    def name(self) -> str:
        return "GitLab"

    @property
    def is_available(self) -> bool:
        """GitLab is not yet available."""
        return False

    # -------------------------------------------------------------------------
    # Issue Operations
    # -------------------------------------------------------------------------

    def create_issue(self, request: IssueCreateRequest) -> Issue:
        """Create a new GitLab issue (not implemented)."""
        raise ProviderNotImplementedError("GitLab", "create_issue")

    def get_issue(self, issue_id: str) -> Issue:
        """Get a GitLab issue by ID (not implemented)."""
        raise ProviderNotImplementedError("GitLab", "get_issue")

    def list_issues(self, filters: Optional[IssueFilters] = None) -> list[Issue]:
        """List GitLab issues (not implemented)."""
        raise ProviderNotImplementedError("GitLab", "list_issues")

    def update_issue(self, issue_id: str, updates: IssueUpdateRequest) -> Issue:
        """Update a GitLab issue (not implemented)."""
        raise ProviderNotImplementedError("GitLab", "update_issue")

    # -------------------------------------------------------------------------
    # Pull Request Operations (Merge Requests in GitLab)
    # -------------------------------------------------------------------------

    def create_pull_request(self, request: PRCreateRequest) -> PullRequest:
        """Create a new GitLab merge request (not implemented)."""
        raise ProviderNotImplementedError("GitLab", "create_merge_request")

    def get_pull_request(self, pr_id: str) -> PullRequest:
        """Get a GitLab merge request by ID (not implemented)."""
        raise ProviderNotImplementedError("GitLab", "get_merge_request")

    def list_pull_requests(
        self, filters: Optional[PRFilters] = None
    ) -> list[PullRequest]:
        """List GitLab merge requests (not implemented)."""
        raise ProviderNotImplementedError("GitLab", "list_merge_requests")

    # -------------------------------------------------------------------------
    # Milestone Operations
    # -------------------------------------------------------------------------

    def create_milestone(self, request: MilestoneCreateRequest) -> Milestone:
        """Create a new GitLab milestone (not implemented)."""
        raise ProviderNotImplementedError("GitLab", "create_milestone")

    def get_milestone(self, milestone_id: str) -> Milestone:
        """Get a GitLab milestone by ID (not implemented)."""
        raise ProviderNotImplementedError("GitLab", "get_milestone")

    def list_milestones(
        self, state: Optional[MilestoneState] = None
    ) -> list[Milestone]:
        """List GitLab milestones (not implemented)."""
        raise ProviderNotImplementedError("GitLab", "list_milestones")
