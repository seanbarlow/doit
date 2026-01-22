"""Integration tests for GitLabProvider.

These tests run against a real GitLab API and require:
- GITLAB_TOKEN: A valid GitLab Personal Access Token with 'api' scope
- GITLAB_TEST_PROJECT: A project path to use for testing (e.g., "owner/test-repo")

To run these tests:
    export GITLAB_TOKEN="glpat-xxxxxxxxxxxx"
    export GITLAB_TEST_PROJECT="your-username/test-repo"
    pytest tests/integration/providers/test_gitlab_integration.py -v

Note: These tests create and modify real resources in GitLab. Use a dedicated
test project to avoid polluting production data.
"""

import os
from datetime import datetime, timedelta

import pytest

from doit_cli.models.provider_models import (
    IssueCreateRequest,
    IssueFilters,
    IssueState,
    IssueType,
    IssueUpdateRequest,
    MilestoneCreateRequest,
    MilestoneState,
    PRFilters,
    PRState,
)
from doit_cli.services.providers.exceptions import (
    AuthenticationError,
    ResourceNotFoundError,
)
from doit_cli.services.providers.gitlab import GitLabProvider


# Skip all tests if environment variables are not set
pytestmark = pytest.mark.skipif(
    not os.environ.get("GITLAB_TOKEN") or not os.environ.get("GITLAB_TEST_PROJECT"),
    reason="GITLAB_TOKEN and GITLAB_TEST_PROJECT environment variables required",
)


@pytest.fixture(scope="module")
def provider() -> GitLabProvider:
    """Create a GitLabProvider for integration testing."""
    project_path = os.environ.get("GITLAB_TEST_PROJECT", "")
    return GitLabProvider(
        project_path=project_path,
        token=os.environ.get("GITLAB_TOKEN"),
    )


class TestGitLabProviderIntegration:
    """Integration tests for GitLabProvider against live GitLab API."""

    # -------------------------------------------------------------------------
    # Authentication & Configuration
    # -------------------------------------------------------------------------

    def test_is_available(self, provider: GitLabProvider) -> None:
        """Test provider availability with valid token."""
        assert provider.is_available is True

    def test_validate_token(self, provider: GitLabProvider) -> None:
        """Test token validation returns user info."""
        user_info = provider.validate_token()
        assert "id" in user_info
        assert "username" in user_info

    def test_invalid_token_raises_error(self) -> None:
        """Test invalid token raises AuthenticationError."""
        provider = GitLabProvider(
            project_path=os.environ.get("GITLAB_TEST_PROJECT", ""),
            token="invalid-token",
        )
        with pytest.raises(AuthenticationError):
            provider.validate_token()

    # -------------------------------------------------------------------------
    # Issue Operations
    # -------------------------------------------------------------------------

    def test_create_and_get_issue(self, provider: GitLabProvider) -> None:
        """Test creating and retrieving an issue."""
        # Create issue
        request = IssueCreateRequest(
            title=f"[Test] Integration test issue {datetime.now().isoformat()}",
            body="This is a test issue created by integration tests.",
            type=IssueType.TASK,
            labels=["test"],
        )
        issue = provider.create_issue(request)

        assert issue.provider_id is not None
        assert issue.title == request.title
        assert issue.url is not None

        # Get the same issue
        retrieved = provider.get_issue(issue.provider_id)
        assert retrieved.title == issue.title
        assert retrieved.type == IssueType.TASK

        # Clean up: close the issue
        provider.update_issue(
            issue.provider_id,
            IssueUpdateRequest(state=IssueState.CLOSED),
        )

    def test_list_issues(self, provider: GitLabProvider) -> None:
        """Test listing issues."""
        issues = provider.list_issues(IssueFilters(limit=5))
        assert isinstance(issues, list)
        # May be empty if test project has no issues

    def test_update_issue_state(self, provider: GitLabProvider) -> None:
        """Test updating issue state."""
        # Create an issue
        request = IssueCreateRequest(
            title=f"[Test] State update test {datetime.now().isoformat()}",
            body="Testing state updates.",
            type=IssueType.TASK,
        )
        issue = provider.create_issue(request)

        # Close the issue
        closed = provider.update_issue(
            issue.provider_id,
            IssueUpdateRequest(state=IssueState.CLOSED),
        )
        assert closed.state == IssueState.CLOSED

        # Reopen the issue
        reopened = provider.update_issue(
            issue.provider_id,
            IssueUpdateRequest(state=IssueState.OPEN),
        )
        assert reopened.state == IssueState.OPEN

        # Clean up
        provider.update_issue(
            issue.provider_id,
            IssueUpdateRequest(state=IssueState.CLOSED),
        )

    def test_get_nonexistent_issue(self, provider: GitLabProvider) -> None:
        """Test getting a non-existent issue raises error."""
        with pytest.raises(ResourceNotFoundError):
            provider.get_issue("999999999")

    # -------------------------------------------------------------------------
    # Merge Request Operations (Read-Only)
    # -------------------------------------------------------------------------

    def test_list_merge_requests(self, provider: GitLabProvider) -> None:
        """Test listing merge requests."""
        mrs = provider.list_pull_requests(PRFilters(limit=5))
        assert isinstance(mrs, list)
        # May be empty if test project has no MRs

    def test_list_closed_merge_requests(self, provider: GitLabProvider) -> None:
        """Test listing closed merge requests."""
        mrs = provider.list_pull_requests(PRFilters(state=PRState.CLOSED, limit=5))
        assert isinstance(mrs, list)
        for mr in mrs:
            assert mr.state in [PRState.CLOSED, PRState.MERGED]

    # -------------------------------------------------------------------------
    # Milestone Operations
    # -------------------------------------------------------------------------

    def test_create_and_get_milestone(self, provider: GitLabProvider) -> None:
        """Test creating and retrieving a milestone."""
        # Create milestone
        request = MilestoneCreateRequest(
            title=f"Test Milestone {datetime.now().isoformat()}",
            description="Integration test milestone",
            due_date=datetime.now() + timedelta(days=30),
        )
        milestone = provider.create_milestone(request)

        assert milestone.provider_id is not None
        assert milestone.title == request.title

        # Get the same milestone
        retrieved = provider.get_milestone(milestone.provider_id)
        assert retrieved.title == milestone.title

        # Clean up: close the milestone
        provider.update_milestone(
            milestone.provider_id,
            state=MilestoneState.CLOSED,
        )

    def test_list_milestones(self, provider: GitLabProvider) -> None:
        """Test listing milestones."""
        milestones = provider.list_milestones()
        assert isinstance(milestones, list)

    def test_list_active_milestones(self, provider: GitLabProvider) -> None:
        """Test listing only active milestones."""
        milestones = provider.list_milestones(state=MilestoneState.OPEN)
        assert isinstance(milestones, list)
        for ms in milestones:
            assert ms.state == MilestoneState.OPEN


class TestGitLabSelfHostedIntegration:
    """Integration tests for self-hosted GitLab instances.

    These tests require additional environment variables:
    - GITLAB_SELF_HOSTED_URL: The base URL of the self-hosted GitLab
    - GITLAB_SELF_HOSTED_TOKEN: Token for the self-hosted instance
    - GITLAB_SELF_HOSTED_PROJECT: Project path on the self-hosted instance
    """

    @pytest.mark.skipif(
        not os.environ.get("GITLAB_SELF_HOSTED_URL"),
        reason="GITLAB_SELF_HOSTED_URL not set",
    )
    def test_self_hosted_provider(self) -> None:
        """Test provider works with self-hosted GitLab."""
        provider = GitLabProvider(
            project_path=os.environ.get("GITLAB_SELF_HOSTED_PROJECT", ""),
            host=os.environ.get("GITLAB_SELF_HOSTED_URL", "").replace("https://", ""),
            token=os.environ.get("GITLAB_SELF_HOSTED_TOKEN"),
        )
        assert provider.is_available is True
        user_info = provider.validate_token()
        assert "username" in user_info


class TestGitLabLabelCreation:
    """Tests for automatic label creation in GitLab."""

    def test_labels_auto_created(self, provider: GitLabProvider) -> None:
        """Test that labels are automatically created when needed."""
        # Create an issue with labels that may not exist
        unique_label = f"test-auto-{datetime.now().timestamp()}"
        request = IssueCreateRequest(
            title=f"[Test] Label creation test {datetime.now().isoformat()}",
            body="Testing automatic label creation.",
            type=IssueType.FEATURE,  # Will create "Feature" label if needed
            labels=[unique_label],
        )
        issue = provider.create_issue(request)

        # Issue should be created successfully
        assert issue.provider_id is not None

        # Clean up
        provider.update_issue(
            issue.provider_id,
            IssueUpdateRequest(state=IssueState.CLOSED),
        )
