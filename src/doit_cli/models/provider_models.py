"""Provider-agnostic data models for git operations.

This module defines unified data models that work across all git providers
(GitHub, Azure DevOps, GitLab).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


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
    url: str | None = None


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
