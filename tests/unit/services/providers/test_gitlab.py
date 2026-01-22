"""Unit tests for GitLabProvider.

Tests use mocked httpx responses to verify GitLab API interactions.
"""

from datetime import datetime
from unittest.mock import MagicMock, patch

import httpx
import pytest

from doit_cli.models.provider_models import (
    Issue,
    IssueCreateRequest,
    IssueFilters,
    IssueState,
    IssueType,
    IssueUpdateRequest,
    Milestone,
    MilestoneCreateRequest,
    MilestoneState,
    PRCreateRequest,
    PRFilters,
    PRState,
    PullRequest,
)
from doit_cli.services.providers.base import ProviderType
from doit_cli.services.providers.exceptions import (
    AuthenticationError,
    NetworkError,
    RateLimitError,
    ResourceNotFoundError,
    ValidationError,
)
from doit_cli.services.providers.gitlab import (
    GitLabAPIClient,
    GitLabLabelMapper,
    GitLabProvider,
)


# =============================================================================
# GitLabLabelMapper Tests
# =============================================================================


class TestGitLabLabelMapper:
    """Test suite for GitLabLabelMapper."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.mapper = GitLabLabelMapper()

    def test_to_gitlab_labels_with_type(self) -> None:
        """Test converting issue type to GitLab labels."""
        labels = self.mapper.to_gitlab_labels(IssueType.FEATURE)
        assert labels == ["Feature"]

    def test_to_gitlab_labels_with_priority(self) -> None:
        """Test converting issue type with priority."""
        labels = self.mapper.to_gitlab_labels(IssueType.BUG, priority="P1")
        assert "Bug" in labels
        assert "priority::1" in labels

    def test_to_gitlab_labels_with_extra_labels(self) -> None:
        """Test adding extra labels."""
        labels = self.mapper.to_gitlab_labels(
            IssueType.TASK, extra_labels=["backend", "urgent"]
        )
        assert "Task" in labels
        assert "backend" in labels
        assert "urgent" in labels

    def test_to_gitlab_labels_all_types(self) -> None:
        """Test all issue types are mapped."""
        assert self.mapper.to_gitlab_labels(IssueType.EPIC) == ["Epic"]
        assert self.mapper.to_gitlab_labels(IssueType.FEATURE) == ["Feature"]
        assert self.mapper.to_gitlab_labels(IssueType.BUG) == ["Bug"]
        assert self.mapper.to_gitlab_labels(IssueType.TASK) == ["Task"]
        assert self.mapper.to_gitlab_labels(IssueType.USER_STORY) == ["User Story"]

    def test_from_gitlab_labels_extracts_type(self) -> None:
        """Test extracting issue type from labels."""
        issue_type, priority, remaining = self.mapper.from_gitlab_labels(
            ["Feature", "backend"]
        )
        assert issue_type == IssueType.FEATURE
        assert priority is None
        assert remaining == ["backend"]

    def test_from_gitlab_labels_extracts_priority(self) -> None:
        """Test extracting priority from labels."""
        issue_type, priority, remaining = self.mapper.from_gitlab_labels(
            ["Bug", "priority::2", "frontend"]
        )
        assert issue_type == IssueType.BUG
        assert priority == "P2"
        assert remaining == ["frontend"]

    def test_from_gitlab_labels_default_type(self) -> None:
        """Test default type when no type label present."""
        issue_type, priority, remaining = self.mapper.from_gitlab_labels(
            ["custom-label"]
        )
        assert issue_type == IssueType.TASK
        assert remaining == ["custom-label"]

    def test_get_all_type_labels(self) -> None:
        """Test getting all type labels."""
        labels = self.mapper.get_all_type_labels()
        assert "Epic" in labels
        assert "Feature" in labels
        assert "Bug" in labels
        assert "Task" in labels
        assert "User Story" in labels

    def test_get_all_priority_labels(self) -> None:
        """Test getting all priority labels."""
        labels = self.mapper.get_all_priority_labels()
        assert "priority::1" in labels
        assert "priority::2" in labels
        assert "priority::3" in labels
        assert "priority::4" in labels

    def test_get_label_color(self) -> None:
        """Test getting label colors."""
        assert self.mapper.get_label_color("Epic") == "#6699cc"
        assert self.mapper.get_label_color("Bug") == "#d9534f"
        assert self.mapper.get_label_color("unknown") == "#428bca"


# =============================================================================
# GitLabAPIClient Tests
# =============================================================================


class TestGitLabAPIClient:
    """Test suite for GitLabAPIClient."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.client = GitLabAPIClient(
            project_path="owner%2Frepo",
            host="gitlab.com",
            token="test-token",
        )

    def teardown_method(self) -> None:
        """Clean up resources."""
        self.client.close()

    def test_base_url_default_host(self) -> None:
        """Test base URL construction with default host."""
        assert self.client.base_url == "https://gitlab.com/api/v4"

    def test_base_url_custom_host(self) -> None:
        """Test base URL construction with custom host."""
        client = GitLabAPIClient(
            project_path="org%2Fproject",
            host="gitlab.mycompany.com",
            token="token",
        )
        assert client.base_url == "https://gitlab.mycompany.com/api/v4"
        client.close()

    @patch.object(httpx.Client, "get")
    def test_handle_response_401(self, mock_get: MagicMock) -> None:
        """Test 401 response raises AuthenticationError."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        with pytest.raises(AuthenticationError) as exc_info:
            self.client.get("/test")

        assert "authentication failed" in str(exc_info.value).lower()

    @patch.object(httpx.Client, "get")
    def test_handle_response_403(self, mock_get: MagicMock) -> None:
        """Test 403 response raises AuthenticationError."""
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_get.return_value = mock_response

        with pytest.raises(AuthenticationError) as exc_info:
            self.client.get("/test")

        assert "permissions" in str(exc_info.value).lower()

    @patch.object(httpx.Client, "get")
    def test_handle_response_404(self, mock_get: MagicMock) -> None:
        """Test 404 response raises ResourceNotFoundError."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        with pytest.raises(ResourceNotFoundError):
            self.client.get("/test")

    @patch.object(httpx.Client, "get")
    def test_handle_response_429(self, mock_get: MagicMock) -> None:
        """Test 429 response raises RateLimitError."""
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.headers = {"Retry-After": "120"}
        mock_get.return_value = mock_response

        with pytest.raises(RateLimitError) as exc_info:
            self.client.get("/test")

        assert exc_info.value.retry_after == 120

    @patch.object(httpx.Client, "get")
    def test_handle_response_500(self, mock_get: MagicMock) -> None:
        """Test 5xx response raises NetworkError."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        with pytest.raises(NetworkError):
            self.client.get("/test")

    @patch.object(httpx.Client, "get")
    def test_handle_response_400(self, mock_get: MagicMock) -> None:
        """Test 400 response raises ValidationError."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.content = b'{"message": {"title": ["is too long"]}}'
        mock_response.json.return_value = {"message": {"title": ["is too long"]}}
        mock_get.return_value = mock_response

        with pytest.raises(ValidationError):
            self.client.get("/test")

    @patch.object(httpx.Client, "get")
    def test_get_success(self, mock_get: MagicMock) -> None:
        """Test successful GET request."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.content = b'{"id": 1}'
        mock_response.json.return_value = {"id": 1}
        mock_get.return_value = mock_response

        result = self.client.get("/test")
        assert result == {"id": 1}

    @patch.object(httpx.Client, "post")
    def test_post_success(self, mock_post: MagicMock) -> None:
        """Test successful POST request."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.is_success = True
        mock_response.content = b'{"id": 1, "title": "Test"}'
        mock_response.json.return_value = {"id": 1, "title": "Test"}
        mock_post.return_value = mock_response

        result = self.client.post("/test", {"title": "Test"})
        assert result == {"id": 1, "title": "Test"}

    @patch.object(httpx.Client, "put")
    def test_put_success(self, mock_put: MagicMock) -> None:
        """Test successful PUT request."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.content = b'{"id": 1, "title": "Updated"}'
        mock_response.json.return_value = {"id": 1, "title": "Updated"}
        mock_put.return_value = mock_response

        result = self.client.put("/test", {"title": "Updated"})
        assert result == {"id": 1, "title": "Updated"}

    @patch.object(httpx.Client, "get")
    def test_validate_token(self, mock_get: MagicMock) -> None:
        """Test token validation."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.content = b'{"id": 1, "username": "testuser"}'
        mock_response.json.return_value = {"id": 1, "username": "testuser"}
        mock_get.return_value = mock_response

        result = self.client.validate_token()
        assert result["username"] == "testuser"
        mock_get.assert_called_with("/user", params=None)


# =============================================================================
# GitLabProvider Tests
# =============================================================================


class TestGitLabProvider:
    """Test suite for GitLabProvider implementation."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.provider = GitLabProvider(
            project_path="owner/repo",
            host="gitlab.com",
            token="test-token",
        )

    # -------------------------------------------------------------------------
    # Provider Properties
    # -------------------------------------------------------------------------

    def test_provider_type(self) -> None:
        """Test provider_type returns GITLAB."""
        assert self.provider.provider_type == ProviderType.GITLAB

    def test_name(self) -> None:
        """Test name returns GitLab."""
        assert self.provider.name == "GitLab"

    @patch.object(GitLabAPIClient, "validate_token")
    def test_is_available_with_valid_token(self, mock_validate: MagicMock) -> None:
        """Test is_available returns True with valid token."""
        mock_validate.return_value = {"id": 1}
        assert self.provider.is_available is True

    @patch.object(GitLabAPIClient, "validate_token")
    def test_is_available_with_invalid_token(self, mock_validate: MagicMock) -> None:
        """Test is_available returns False with invalid token."""
        mock_validate.side_effect = AuthenticationError("Invalid", provider="gitlab")
        assert self.provider.is_available is False

    def test_is_available_without_token(self) -> None:
        """Test is_available returns False without token."""
        provider = GitLabProvider(project_path="owner/repo", token="")
        with patch.dict("os.environ", {}, clear=True):
            assert provider.is_available is False

    # -------------------------------------------------------------------------
    # Issue Operations
    # -------------------------------------------------------------------------

    @patch.object(GitLabAPIClient, "post")
    @patch.object(GitLabAPIClient, "get_list")
    def test_create_issue(
        self, mock_get_list: MagicMock, mock_post: MagicMock
    ) -> None:
        """Test creating an issue."""
        mock_get_list.return_value = []  # No existing labels
        mock_post.side_effect = [
            {},  # Label creation
            {
                "iid": 42,
                "title": "Test Issue",
                "description": "Body",
                "state": "opened",
                "web_url": "https://gitlab.com/owner/repo/-/issues/42",
                "labels": ["Feature"],
                "created_at": "2026-01-22T10:00:00Z",
                "updated_at": "2026-01-22T10:00:00Z",
            },
        ]

        request = IssueCreateRequest(
            title="Test Issue",
            body="Body",
            type=IssueType.FEATURE,
        )
        issue = self.provider.create_issue(request)

        assert issue.title == "Test Issue"
        assert issue.provider_id == "42"

    @patch.object(GitLabAPIClient, "get")
    def test_get_issue(self, mock_get: MagicMock) -> None:
        """Test getting an issue by ID."""
        mock_get.return_value = {
            "iid": 42,
            "title": "Test Issue",
            "description": "Body",
            "state": "opened",
            "web_url": "https://gitlab.com/owner/repo/-/issues/42",
            "labels": ["Bug", "priority::1"],
            "created_at": "2026-01-22T10:00:00Z",
            "updated_at": "2026-01-22T10:00:00Z",
        }

        issue = self.provider.get_issue("42")

        assert issue.title == "Test Issue"
        assert issue.type == IssueType.BUG
        assert issue.state == IssueState.OPEN

    @patch.object(GitLabAPIClient, "get")
    def test_get_issue_not_found(self, mock_get: MagicMock) -> None:
        """Test getting a non-existent issue."""
        mock_get.side_effect = ResourceNotFoundError("resource", "unknown")

        with pytest.raises(ResourceNotFoundError):
            self.provider.get_issue("999")

    @patch.object(GitLabAPIClient, "get_list")
    def test_list_issues(self, mock_get_list: MagicMock) -> None:
        """Test listing issues."""
        mock_get_list.return_value = [
            {
                "iid": 1,
                "title": "Issue 1",
                "state": "opened",
                "web_url": "https://gitlab.com/owner/repo/-/issues/1",
                "labels": [],
                "created_at": "2026-01-22T10:00:00Z",
                "updated_at": "2026-01-22T10:00:00Z",
            },
            {
                "iid": 2,
                "title": "Issue 2",
                "state": "closed",
                "web_url": "https://gitlab.com/owner/repo/-/issues/2",
                "labels": [],
                "created_at": "2026-01-22T11:00:00Z",
                "updated_at": "2026-01-22T11:00:00Z",
            },
        ]

        issues = self.provider.list_issues()

        assert len(issues) == 2
        assert issues[0].title == "Issue 1"
        assert issues[1].state == IssueState.CLOSED

    @patch.object(GitLabAPIClient, "get_list")
    def test_list_issues_with_filters(self, mock_get_list: MagicMock) -> None:
        """Test listing issues with filters."""
        mock_get_list.return_value = []

        filters = IssueFilters(state=IssueState.OPEN, labels=["Bug"], limit=10)
        self.provider.list_issues(filters)

        mock_get_list.assert_called_once()
        # get_list is called with positional args: (endpoint, params)
        call_args = mock_get_list.call_args[0]
        call_params = call_args[1] if len(call_args) > 1 else {}
        assert call_params["state"] == "opened"
        assert call_params["labels"] == "Bug"
        assert call_params["per_page"] == 10

    @patch.object(GitLabAPIClient, "put")
    @patch.object(GitLabAPIClient, "get_list")
    def test_update_issue(
        self, mock_get_list: MagicMock, mock_put: MagicMock
    ) -> None:
        """Test updating an issue."""
        mock_get_list.return_value = []
        mock_put.return_value = {
            "iid": 42,
            "title": "Updated Title",
            "description": "Updated body",
            "state": "closed",
            "web_url": "https://gitlab.com/owner/repo/-/issues/42",
            "labels": [],
            "created_at": "2026-01-22T10:00:00Z",
            "updated_at": "2026-01-22T12:00:00Z",
        }

        updates = IssueUpdateRequest(
            title="Updated Title",
            body="Updated body",
            state=IssueState.CLOSED,
        )
        issue = self.provider.update_issue("42", updates)

        assert issue.title == "Updated Title"
        assert issue.state == IssueState.CLOSED

    # -------------------------------------------------------------------------
    # Merge Request Operations
    # -------------------------------------------------------------------------

    @patch.object(GitLabAPIClient, "post")
    @patch.object(GitLabAPIClient, "get_list")
    def test_create_pull_request(
        self, mock_get_list: MagicMock, mock_post: MagicMock
    ) -> None:
        """Test creating a merge request."""
        mock_get_list.return_value = []
        mock_post.return_value = {
            "iid": 10,
            "title": "Feature MR",
            "description": "Description",
            "source_branch": "feature-branch",
            "target_branch": "main",
            "state": "opened",
            "web_url": "https://gitlab.com/owner/repo/-/merge_requests/10",
            "labels": [],
            "created_at": "2026-01-22T10:00:00Z",
        }

        request = PRCreateRequest(
            title="Feature MR",
            body="Description",
            source_branch="feature-branch",
            target_branch="main",
        )
        mr = self.provider.create_pull_request(request)

        assert mr.title == "Feature MR"
        assert mr.source_branch == "feature-branch"
        assert mr.target_branch == "main"
        assert mr.state == PRState.OPEN

    @patch.object(GitLabAPIClient, "get")
    def test_get_pull_request(self, mock_get: MagicMock) -> None:
        """Test getting a merge request."""
        mock_get.return_value = {
            "iid": 10,
            "title": "Feature MR",
            "description": "Description",
            "source_branch": "feature-branch",
            "target_branch": "main",
            "state": "merged",
            "web_url": "https://gitlab.com/owner/repo/-/merge_requests/10",
            "labels": [],
            "created_at": "2026-01-22T10:00:00Z",
            "merged_at": "2026-01-22T14:00:00Z",
        }

        mr = self.provider.get_pull_request("10")

        assert mr.title == "Feature MR"
        assert mr.state == PRState.MERGED
        assert mr.merged_at is not None

    @patch.object(GitLabAPIClient, "get_list")
    def test_list_pull_requests(self, mock_get_list: MagicMock) -> None:
        """Test listing merge requests."""
        mock_get_list.return_value = [
            {
                "iid": 1,
                "title": "MR 1",
                "source_branch": "branch1",
                "target_branch": "main",
                "state": "opened",
                "web_url": "https://gitlab.com/owner/repo/-/merge_requests/1",
                "labels": [],
                "created_at": "2026-01-22T10:00:00Z",
            },
        ]

        mrs = self.provider.list_pull_requests()

        assert len(mrs) == 1
        assert mrs[0].title == "MR 1"

    @patch.object(GitLabAPIClient, "get_list")
    def test_list_pull_requests_with_filters(self, mock_get_list: MagicMock) -> None:
        """Test listing merge requests with filters."""
        mock_get_list.return_value = []

        filters = PRFilters(state=PRState.MERGED, target_branch="main")
        self.provider.list_pull_requests(filters)

        mock_get_list.assert_called_once()
        # get_list is called with positional args: (endpoint, params)
        call_args = mock_get_list.call_args[0]
        call_params = call_args[1] if len(call_args) > 1 else {}
        assert call_params["state"] == "merged"
        assert call_params["target_branch"] == "main"

    # -------------------------------------------------------------------------
    # Milestone Operations
    # -------------------------------------------------------------------------

    @patch.object(GitLabAPIClient, "post")
    def test_create_milestone(self, mock_post: MagicMock) -> None:
        """Test creating a milestone."""
        mock_post.return_value = {
            "id": 5,
            "title": "v1.0",
            "description": "First release",
            "state": "active",
            "due_date": "2026-02-01",
            "web_url": "https://gitlab.com/owner/repo/-/milestones/5",
        }

        request = MilestoneCreateRequest(
            title="v1.0",
            description="First release",
            due_date=datetime(2026, 2, 1),
        )
        milestone = self.provider.create_milestone(request)

        assert milestone.title == "v1.0"
        assert milestone.state == MilestoneState.OPEN

    @patch.object(GitLabAPIClient, "get")
    def test_get_milestone(self, mock_get: MagicMock) -> None:
        """Test getting a milestone."""
        mock_get.return_value = {
            "id": 5,
            "title": "v1.0",
            "description": "First release",
            "state": "active",
            "due_date": "2026-02-01",
            "web_url": "https://gitlab.com/owner/repo/-/milestones/5",
        }

        milestone = self.provider.get_milestone("5")

        assert milestone.title == "v1.0"
        assert milestone.due_date is not None

    @patch.object(GitLabAPIClient, "get_list")
    def test_list_milestones(self, mock_get_list: MagicMock) -> None:
        """Test listing milestones."""
        mock_get_list.return_value = [
            {
                "id": 1,
                "title": "v1.0",
                "state": "active",
                "web_url": "https://gitlab.com/owner/repo/-/milestones/1",
            },
            {
                "id": 2,
                "title": "v0.9",
                "state": "closed",
                "web_url": "https://gitlab.com/owner/repo/-/milestones/2",
            },
        ]

        milestones = self.provider.list_milestones()

        assert len(milestones) == 2
        assert milestones[0].title == "v1.0"
        assert milestones[1].state == MilestoneState.CLOSED

    @patch.object(GitLabAPIClient, "get_list")
    def test_list_milestones_with_state(self, mock_get_list: MagicMock) -> None:
        """Test listing milestones with state filter."""
        mock_get_list.return_value = []

        self.provider.list_milestones(state=MilestoneState.OPEN)

        mock_get_list.assert_called_once()
        # get_list is called with positional args: (endpoint, params)
        call_args = mock_get_list.call_args[0]
        call_params = call_args[1] if len(call_args) > 1 else {}
        assert call_params["state"] == "active"

    @patch.object(GitLabAPIClient, "put")
    def test_update_milestone(self, mock_put: MagicMock) -> None:
        """Test updating a milestone."""
        mock_put.return_value = {
            "id": 5,
            "title": "v1.0 Final",
            "description": "Updated",
            "state": "closed",
            "web_url": "https://gitlab.com/owner/repo/-/milestones/5",
        }

        milestone = self.provider.update_milestone(
            "5",
            title="v1.0 Final",
            state=MilestoneState.CLOSED,
        )

        assert milestone.title == "v1.0 Final"
        assert milestone.state == MilestoneState.CLOSED

    # -------------------------------------------------------------------------
    # Response Parsers
    # -------------------------------------------------------------------------

    def test_parse_issue_with_labels(self) -> None:
        """Test parsing issue with type and priority labels."""
        data = {
            "iid": 1,
            "title": "Bug Report",
            "description": "Details",
            "state": "opened",
            "web_url": "https://gitlab.com/test/-/issues/1",
            "labels": ["Bug", "priority::1", "backend"],
            "created_at": "2026-01-22T10:00:00Z",
            "updated_at": "2026-01-22T10:00:00Z",
            "milestone": {"id": 5},
        }

        issue = self.provider._parse_issue(data)

        assert issue.type == IssueType.BUG
        assert issue.milestone_id == "5"
        assert len(issue.labels) == 1  # Only "backend" remains
        assert issue.labels[0].name == "backend"

    def test_parse_pull_request_merged(self) -> None:
        """Test parsing merged merge request."""
        data = {
            "iid": 10,
            "title": "Feature",
            "description": "Desc",
            "source_branch": "feature",
            "target_branch": "main",
            "state": "merged",
            "web_url": "https://gitlab.com/test/-/merge_requests/10",
            "labels": [],
            "created_at": "2026-01-22T10:00:00Z",
            "merged_at": "2026-01-22T14:00:00Z",
        }

        mr = self.provider._parse_pull_request(data)

        assert mr.state == PRState.MERGED
        assert mr.merged_at is not None

    def test_parse_milestone_closed(self) -> None:
        """Test parsing closed milestone."""
        data = {
            "id": 5,
            "title": "v0.9",
            "description": "Old release",
            "state": "closed",
            "due_date": "2025-12-01",
            "web_url": "https://gitlab.com/test/-/milestones/5",
        }

        milestone = self.provider._parse_milestone(data)

        assert milestone.state == MilestoneState.CLOSED
        assert milestone.due_date is not None
