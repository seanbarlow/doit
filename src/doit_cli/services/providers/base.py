"""Abstract base class for git providers.

This module defines the GitProvider interface that all provider
implementations must follow.
"""

from abc import ABC, abstractmethod
from enum import Enum
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


class ProviderType(Enum):
    """Supported git provider types."""

    GITHUB = "github"
    AZURE_DEVOPS = "azure_devops"
    GITLAB = "gitlab"


class GitProvider(ABC):
    """Abstract interface for git hosting providers.

    All git providers (GitHub, Azure DevOps, GitLab) must implement this interface
    to be used with the doit CLI.

    Usage:
        provider = ProviderFactory.create()
        issue = provider.create_issue(IssueCreateRequest(title="Bug fix"))
    """

    @property
    @abstractmethod
    def provider_type(self) -> ProviderType:
        """Return the provider type identifier."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the human-readable provider name."""
        pass

    @property
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is properly configured and available.

        Returns:
            True if the provider can make API calls, False otherwise.
        """
        pass

    # -------------------------------------------------------------------------
    # Issue Operations
    # -------------------------------------------------------------------------

    @abstractmethod
    def create_issue(self, request: IssueCreateRequest) -> Issue:
        """Create a new issue.

        Args:
            request: Issue creation parameters.

        Returns:
            The created Issue with populated ID and URL.

        Raises:
            AuthenticationError: If not authenticated.
            ValidationError: If request parameters are invalid.
            ProviderError: For other provider-specific errors.
        """
        pass

    @abstractmethod
    def get_issue(self, issue_id: str) -> Issue:
        """Get an issue by its ID.

        Args:
            issue_id: The issue ID (provider-specific or unified).

        Returns:
            The Issue object.

        Raises:
            ResourceNotFoundError: If the issue does not exist.
            AuthenticationError: If not authenticated.
        """
        pass

    @abstractmethod
    def list_issues(self, filters: Optional[IssueFilters] = None) -> list[Issue]:
        """List issues matching the given filters.

        Args:
            filters: Optional filters to apply.

        Returns:
            List of matching Issue objects.

        Raises:
            AuthenticationError: If not authenticated.
        """
        pass

    @abstractmethod
    def update_issue(self, issue_id: str, updates: IssueUpdateRequest) -> Issue:
        """Update an existing issue.

        Args:
            issue_id: The issue ID to update.
            updates: The fields to update.

        Returns:
            The updated Issue object.

        Raises:
            ResourceNotFoundError: If the issue does not exist.
            ValidationError: If update parameters are invalid.
        """
        pass

    # -------------------------------------------------------------------------
    # Pull Request Operations
    # -------------------------------------------------------------------------

    @abstractmethod
    def create_pull_request(self, request: PRCreateRequest) -> PullRequest:
        """Create a new pull request.

        Args:
            request: Pull request creation parameters.

        Returns:
            The created PullRequest with populated ID and URL.

        Raises:
            AuthenticationError: If not authenticated.
            ValidationError: If request parameters are invalid.
            ResourceNotFoundError: If source/target branch doesn't exist.
        """
        pass

    @abstractmethod
    def get_pull_request(self, pr_id: str) -> PullRequest:
        """Get a pull request by its ID.

        Args:
            pr_id: The pull request ID (provider-specific or unified).

        Returns:
            The PullRequest object.

        Raises:
            ResourceNotFoundError: If the PR does not exist.
        """
        pass

    @abstractmethod
    def list_pull_requests(
        self, filters: Optional[PRFilters] = None
    ) -> list[PullRequest]:
        """List pull requests matching the given filters.

        Args:
            filters: Optional filters to apply.

        Returns:
            List of matching PullRequest objects.
        """
        pass

    # -------------------------------------------------------------------------
    # Milestone Operations
    # -------------------------------------------------------------------------

    @abstractmethod
    def create_milestone(self, request: MilestoneCreateRequest) -> Milestone:
        """Create a new milestone.

        Args:
            request: Milestone creation parameters.

        Returns:
            The created Milestone with populated ID.

        Raises:
            AuthenticationError: If not authenticated.
            ValidationError: If request parameters are invalid.
        """
        pass

    @abstractmethod
    def get_milestone(self, milestone_id: str) -> Milestone:
        """Get a milestone by its ID.

        Args:
            milestone_id: The milestone ID (provider-specific or unified).

        Returns:
            The Milestone object.

        Raises:
            ResourceNotFoundError: If the milestone does not exist.
        """
        pass

    @abstractmethod
    def list_milestones(
        self, state: Optional[MilestoneState] = None
    ) -> list[Milestone]:
        """List milestones.

        Args:
            state: Optional state filter (open/closed).

        Returns:
            List of Milestone objects.
        """
        pass

    # -------------------------------------------------------------------------
    # Helper Methods (common to all providers)
    # -------------------------------------------------------------------------

    def _make_unified_id(self, entity_type: str, provider_id: str) -> str:
        """Create a unified ID from a provider-specific ID.

        Args:
            entity_type: Type of entity (e.g., "issue", "pr", "ms")
            provider_id: The provider-specific ID

        Returns:
            Unified ID in format: {provider}:{entity_type}:{provider_id}
        """
        return f"{self.provider_type.value}:{entity_type}:{provider_id}"

    def _extract_provider_id(self, unified_id: str) -> str:
        """Extract the provider-specific ID from a unified ID.

        Args:
            unified_id: A unified ID or provider-specific ID

        Returns:
            The provider-specific ID
        """
        if ":" in unified_id:
            parts = unified_id.split(":")
            return parts[-1]
        return unified_id


# =============================================================================
# Rate Limiting Utilities
# =============================================================================

import time
from functools import wraps
from typing import Callable, TypeVar

T = TypeVar("T")


def with_retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator for retrying operations with exponential backoff.

    Use this decorator on provider methods that may encounter
    rate limits or transient network errors.

    Args:
        max_retries: Maximum number of retry attempts.
        base_delay: Initial delay in seconds.
        max_delay: Maximum delay in seconds.
        exponential_base: Base for exponential backoff calculation.

    Returns:
        Decorated function that retries on RateLimitError.

    Example:
        @with_retry(max_retries=3)
        def create_issue(self, request):
            ...
    """
    from .exceptions import RateLimitError

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            delay = base_delay

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except RateLimitError as e:
                    last_exception = e

                    if attempt == max_retries:
                        raise

                    # Use retry_after if provided, otherwise exponential backoff
                    if e.retry_after:
                        wait_time = min(e.retry_after, max_delay)
                    else:
                        wait_time = min(delay, max_delay)
                        delay *= exponential_base

                    time.sleep(wait_time)

            # Should not reach here, but satisfy type checker
            if last_exception:
                raise last_exception
            raise RuntimeError("Unexpected retry loop exit")

        return wrapper

    return decorator
