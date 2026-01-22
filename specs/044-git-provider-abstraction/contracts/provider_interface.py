"""
Git Provider Interface Contract

This module defines the abstract interface that all git providers must implement.
It serves as the contract between the doit CLI and provider implementations.

Feature: 044-git-provider-abstraction
Date: 2026-01-22
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Protocol, runtime_checkable


# =============================================================================
# Enumerations
# =============================================================================


class ProviderType(Enum):
    """Supported git provider types."""

    GITHUB = "github"
    AZURE_DEVOPS = "azure_devops"
    GITLAB = "gitlab"


class IssueType(Enum):
    """Unified issue type classification."""

    BUG = "bug"
    TASK = "task"
    USER_STORY = "user_story"
    FEATURE = "feature"
    EPIC = "epic"


class IssueState(Enum):
    """Issue state."""

    OPEN = "open"
    CLOSED = "closed"


class PRState(Enum):
    """Pull request state."""

    OPEN = "open"
    MERGED = "merged"
    CLOSED = "closed"


class MilestoneState(Enum):
    """Milestone state."""

    OPEN = "open"
    CLOSED = "closed"


# =============================================================================
# Data Models
# =============================================================================


@dataclass
class Label:
    """A label/tag that can be applied to issues and pull requests."""

    name: str
    color: str | None = None
    description: str | None = None


@dataclass
class Issue:
    """Unified issue representation across all providers."""

    id: str  # Unified ID: {provider}:{provider_id}
    provider_id: str  # Provider-specific ID
    title: str
    state: IssueState
    url: str
    created_at: datetime
    updated_at: datetime
    body: str | None = None
    type: IssueType = IssueType.TASK
    labels: list[Label] = field(default_factory=list)
    milestone_id: str | None = None


@dataclass
class PullRequest:
    """Unified pull request / merge request representation."""

    id: str  # Unified ID: {provider}:pr:{provider_id}
    provider_id: str  # Provider-specific ID
    title: str
    source_branch: str
    target_branch: str
    state: PRState
    url: str
    created_at: datetime
    body: str | None = None
    labels: list[Label] = field(default_factory=list)
    closes_issues: list[str] = field(default_factory=list)  # Issue IDs
    merged_at: datetime | None = None


@dataclass
class Milestone:
    """Unified milestone / iteration / sprint representation."""

    id: str  # Unified ID: {provider}:ms:{provider_id}
    provider_id: str  # Provider-specific ID
    title: str
    state: MilestoneState
    description: str | None = None
    due_date: datetime | None = None
    issue_count: int = 0
    closed_issue_count: int = 0


# =============================================================================
# Request Models
# =============================================================================


@dataclass
class IssueCreateRequest:
    """Request to create a new issue."""

    title: str
    body: str | None = None
    type: IssueType = IssueType.TASK
    labels: list[str] = field(default_factory=list)
    milestone_id: str | None = None


@dataclass
class IssueUpdateRequest:
    """Request to update an existing issue."""

    title: str | None = None
    body: str | None = None
    state: IssueState | None = None
    labels: list[str] | None = None
    milestone_id: str | None = None


@dataclass
class IssueFilters:
    """Filters for querying issues."""

    state: IssueState | None = None
    labels: list[str] | None = None
    milestone_id: str | None = None
    type: IssueType | None = None
    limit: int = 100


@dataclass
class PRCreateRequest:
    """Request to create a new pull request."""

    title: str
    source_branch: str
    target_branch: str = "main"
    body: str | None = None
    labels: list[str] = field(default_factory=list)
    closes_issues: list[str] = field(default_factory=list)


@dataclass
class PRFilters:
    """Filters for querying pull requests."""

    state: PRState | None = None
    source_branch: str | None = None
    target_branch: str | None = None
    limit: int = 100


@dataclass
class MilestoneCreateRequest:
    """Request to create a new milestone."""

    title: str
    description: str | None = None
    due_date: datetime | None = None


# =============================================================================
# Exceptions
# =============================================================================


class ProviderError(Exception):
    """Base exception for all provider errors."""

    def __init__(self, message: str, cause: Exception | None = None):
        super().__init__(message)
        self.cause = cause


class AuthenticationError(ProviderError):
    """Raised when authentication fails."""

    pass


class RateLimitError(ProviderError):
    """Raised when API rate limit is exceeded."""

    def __init__(
        self, message: str, retry_after: int | None = None, cause: Exception | None = None
    ):
        super().__init__(message, cause)
        self.retry_after = retry_after  # Seconds until rate limit resets


class ResourceNotFoundError(ProviderError):
    """Raised when a requested resource does not exist."""

    def __init__(self, resource_type: str, resource_id: str, cause: Exception | None = None):
        super().__init__(f"{resource_type} not found: {resource_id}", cause)
        self.resource_type = resource_type
        self.resource_id = resource_id


class ValidationError(ProviderError):
    """Raised when request validation fails."""

    def __init__(self, message: str, field: str | None = None, cause: Exception | None = None):
        super().__init__(message, cause)
        self.field = field


class NetworkError(ProviderError):
    """Raised when a network operation fails."""

    pass


# =============================================================================
# Provider Interface
# =============================================================================


@runtime_checkable
class GitProvider(Protocol):
    """
    Abstract interface for git hosting providers.

    All git providers (GitHub, Azure DevOps, GitLab) must implement this interface
    to be used with the doit CLI.

    Usage:
        provider = ProviderFactory.create()
        issue = provider.create_issue(IssueCreateRequest(title="Bug fix"))
    """

    @property
    def provider_type(self) -> ProviderType:
        """Return the provider type identifier."""
        ...

    @property
    def name(self) -> str:
        """Return the human-readable provider name."""
        ...

    @property
    def is_available(self) -> bool:
        """
        Check if the provider is properly configured and available.

        Returns:
            True if the provider can make API calls, False otherwise.
        """
        ...

    # -------------------------------------------------------------------------
    # Issue Operations
    # -------------------------------------------------------------------------

    def create_issue(self, request: IssueCreateRequest) -> Issue:
        """
        Create a new issue.

        Args:
            request: Issue creation parameters.

        Returns:
            The created Issue with populated ID and URL.

        Raises:
            AuthenticationError: If not authenticated.
            ValidationError: If request parameters are invalid.
            ProviderError: For other provider-specific errors.
        """
        ...

    def get_issue(self, issue_id: str) -> Issue:
        """
        Get an issue by its ID.

        Args:
            issue_id: The issue ID (provider-specific or unified).

        Returns:
            The Issue object.

        Raises:
            ResourceNotFoundError: If the issue does not exist.
            AuthenticationError: If not authenticated.
        """
        ...

    def list_issues(self, filters: IssueFilters | None = None) -> list[Issue]:
        """
        List issues matching the given filters.

        Args:
            filters: Optional filters to apply.

        Returns:
            List of matching Issue objects.

        Raises:
            AuthenticationError: If not authenticated.
        """
        ...

    def update_issue(self, issue_id: str, updates: IssueUpdateRequest) -> Issue:
        """
        Update an existing issue.

        Args:
            issue_id: The issue ID to update.
            updates: The fields to update.

        Returns:
            The updated Issue object.

        Raises:
            ResourceNotFoundError: If the issue does not exist.
            ValidationError: If update parameters are invalid.
        """
        ...

    # -------------------------------------------------------------------------
    # Pull Request Operations
    # -------------------------------------------------------------------------

    def create_pull_request(self, request: PRCreateRequest) -> PullRequest:
        """
        Create a new pull request.

        Args:
            request: Pull request creation parameters.

        Returns:
            The created PullRequest with populated ID and URL.

        Raises:
            AuthenticationError: If not authenticated.
            ValidationError: If request parameters are invalid.
            ResourceNotFoundError: If source/target branch doesn't exist.
        """
        ...

    def get_pull_request(self, pr_id: str) -> PullRequest:
        """
        Get a pull request by its ID.

        Args:
            pr_id: The pull request ID (provider-specific or unified).

        Returns:
            The PullRequest object.

        Raises:
            ResourceNotFoundError: If the PR does not exist.
        """
        ...

    def list_pull_requests(self, filters: PRFilters | None = None) -> list[PullRequest]:
        """
        List pull requests matching the given filters.

        Args:
            filters: Optional filters to apply.

        Returns:
            List of matching PullRequest objects.
        """
        ...

    # -------------------------------------------------------------------------
    # Milestone Operations
    # -------------------------------------------------------------------------

    def create_milestone(self, request: MilestoneCreateRequest) -> Milestone:
        """
        Create a new milestone.

        Args:
            request: Milestone creation parameters.

        Returns:
            The created Milestone with populated ID.

        Raises:
            AuthenticationError: If not authenticated.
            ValidationError: If request parameters are invalid.
        """
        ...

    def get_milestone(self, milestone_id: str) -> Milestone:
        """
        Get a milestone by its ID.

        Args:
            milestone_id: The milestone ID (provider-specific or unified).

        Returns:
            The Milestone object.

        Raises:
            ResourceNotFoundError: If the milestone does not exist.
        """
        ...

    def list_milestones(self, state: MilestoneState | None = None) -> list[Milestone]:
        """
        List milestones.

        Args:
            state: Optional state filter (open/closed).

        Returns:
            List of Milestone objects.
        """
        ...


class BaseGitProvider(ABC):
    """
    Abstract base class for git providers.

    Provides common functionality and enforces the GitProvider interface.
    Concrete providers should inherit from this class.
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
        """Check if the provider is properly configured and available."""
        pass

    # Issue Operations
    @abstractmethod
    def create_issue(self, request: IssueCreateRequest) -> Issue:
        pass

    @abstractmethod
    def get_issue(self, issue_id: str) -> Issue:
        pass

    @abstractmethod
    def list_issues(self, filters: IssueFilters | None = None) -> list[Issue]:
        pass

    @abstractmethod
    def update_issue(self, issue_id: str, updates: IssueUpdateRequest) -> Issue:
        pass

    # Pull Request Operations
    @abstractmethod
    def create_pull_request(self, request: PRCreateRequest) -> PullRequest:
        pass

    @abstractmethod
    def get_pull_request(self, pr_id: str) -> PullRequest:
        pass

    @abstractmethod
    def list_pull_requests(self, filters: PRFilters | None = None) -> list[PullRequest]:
        pass

    # Milestone Operations
    @abstractmethod
    def create_milestone(self, request: MilestoneCreateRequest) -> Milestone:
        pass

    @abstractmethod
    def get_milestone(self, milestone_id: str) -> Milestone:
        pass

    @abstractmethod
    def list_milestones(self, state: MilestoneState | None = None) -> list[Milestone]:
        pass

    # -------------------------------------------------------------------------
    # Helper Methods (common to all providers)
    # -------------------------------------------------------------------------

    def _make_unified_id(self, entity_type: str, provider_id: str) -> str:
        """
        Create a unified ID from a provider-specific ID.

        Args:
            entity_type: Type of entity (e.g., "issue", "pr", "ms")
            provider_id: The provider-specific ID

        Returns:
            Unified ID in format: {provider}:{entity_type}:{provider_id}
        """
        return f"{self.provider_type.value}:{entity_type}:{provider_id}"

    def _extract_provider_id(self, unified_id: str) -> str:
        """
        Extract the provider-specific ID from a unified ID.

        Args:
            unified_id: A unified ID or provider-specific ID

        Returns:
            The provider-specific ID
        """
        if ":" in unified_id:
            parts = unified_id.split(":")
            return parts[-1]
        return unified_id
