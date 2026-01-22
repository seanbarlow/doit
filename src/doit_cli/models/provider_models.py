"""Provider-agnostic data models for git operations.

This module defines unified data models that work across all git providers
(GitHub, Azure DevOps, GitLab).
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


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


@dataclass
class Label:
    """A label/tag that can be applied to issues and pull requests."""

    name: str
    color: Optional[str] = None
    description: Optional[str] = None


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
    body: Optional[str] = None
    type: IssueType = IssueType.TASK
    labels: list[Label] = field(default_factory=list)
    milestone_id: Optional[str] = None


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
    body: Optional[str] = None
    labels: list[Label] = field(default_factory=list)
    closes_issues: list[str] = field(default_factory=list)  # Issue IDs
    merged_at: Optional[datetime] = None


@dataclass
class Milestone:
    """Unified milestone / iteration / sprint representation."""

    id: str  # Unified ID: {provider}:ms:{provider_id}
    provider_id: str  # Provider-specific ID
    title: str
    state: MilestoneState
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    issue_count: int = 0
    closed_issue_count: int = 0
    url: Optional[str] = None


# =============================================================================
# Request Models
# =============================================================================


@dataclass
class IssueCreateRequest:
    """Request to create a new issue."""

    title: str
    body: Optional[str] = None
    type: IssueType = IssueType.TASK
    labels: list[str] = field(default_factory=list)
    milestone_id: Optional[str] = None


@dataclass
class IssueUpdateRequest:
    """Request to update an existing issue."""

    title: Optional[str] = None
    body: Optional[str] = None
    state: Optional[IssueState] = None
    labels: Optional[list[str]] = None
    milestone_id: Optional[str] = None


@dataclass
class IssueFilters:
    """Filters for querying issues."""

    state: Optional[IssueState] = None
    labels: Optional[list[str]] = None
    milestone_id: Optional[str] = None
    type: Optional[IssueType] = None
    limit: int = 100


@dataclass
class PRCreateRequest:
    """Request to create a new pull request."""

    title: str
    source_branch: str
    target_branch: str = "main"
    body: Optional[str] = None
    labels: list[str] = field(default_factory=list)
    closes_issues: list[str] = field(default_factory=list)


@dataclass
class PRFilters:
    """Filters for querying pull requests."""

    state: Optional[PRState] = None
    source_branch: Optional[str] = None
    target_branch: Optional[str] = None
    limit: int = 100


@dataclass
class MilestoneCreateRequest:
    """Request to create a new milestone."""

    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
