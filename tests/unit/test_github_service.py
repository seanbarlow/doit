"""Unit tests for GitHub service.

Tests for GitHubService class which manages GitHub issue operations via gh CLI.
"""

import json
from unittest.mock import MagicMock, patch

import pytest

from doit_cli.models.fixit_models import GitHubIssue, IssueState
from doit_cli.services.github_service import GitHubService, GitHubServiceError


class TestGitHubServiceInit:
    """Tests for GitHubService initialization."""

    def test_init_succeeds_when_gh_available(self):
        """Should initialize when gh CLI is available."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            service = GitHubService()
            assert service is not None

    def test_init_raises_when_gh_not_found(self):
        """Should raise error when gh CLI is not installed."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError
            with pytest.raises(GitHubServiceError) as exc_info:
                GitHubService()
            assert "GitHub CLI (gh) not found" in str(exc_info.value)

    def test_init_continues_when_gh_not_authenticated(self):
        """Should continue when gh CLI is installed but not authenticated."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1)
            # Should not raise - gh might work for public repos
            service = GitHubService()
            assert service is not None


class TestGitHubServiceIsAvailable:
    """Tests for is_available method."""

    def test_is_available_returns_true_when_api_accessible(self):
        """Should return True when GitHub API is accessible."""
        with patch("subprocess.run") as mock_run:
            # First call for init
            mock_run.return_value = MagicMock(returncode=0)
            service = GitHubService()

            # Call is_available
            result = service.is_available()
            assert result is True

    def test_is_available_returns_false_on_timeout(self):
        """Should return False when API request times out."""
        with patch("subprocess.run") as mock_run:
            # First call for init
            init_mock = MagicMock(returncode=0)

            def side_effect(*args, **kwargs):
                if "rate_limit" in str(args):
                    from subprocess import TimeoutExpired
                    raise TimeoutExpired(cmd="gh", timeout=5)
                return init_mock

            mock_run.side_effect = side_effect
            service = GitHubService()

            result = service.is_available()
            assert result is False


class TestGitHubServiceGetIssue:
    """Tests for get_issue method."""

    def test_get_issue_returns_issue_when_found(self):
        """Should return GitHubIssue when issue exists."""
        issue_data = {
            "number": 123,
            "title": "Test Bug",
            "body": "Bug description",
            "state": "OPEN",
            "labels": [{"name": "bug"}],
        }

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout=json.dumps(issue_data),
            )
            service = GitHubService()

            issue = service.get_issue(123)

            assert issue is not None
            assert issue.number == 123
            assert issue.title == "Test Bug"
            assert issue.state == IssueState.OPEN
            assert "bug" in issue.labels

    def test_get_issue_returns_none_when_not_found(self):
        """Should return None when issue doesn't exist."""
        with patch("subprocess.run") as mock_run:
            # Init call
            init_result = MagicMock(returncode=0)
            # get_issue call
            issue_result = MagicMock(returncode=1, stdout="", stderr="issue not found")

            mock_run.side_effect = [init_result, issue_result]
            service = GitHubService()

            issue = service.get_issue(99999)

            assert issue is None

    def test_get_issue_returns_none_on_invalid_json(self):
        """Should return None when response is invalid JSON."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="not valid json",
            )
            service = GitHubService()

            issue = service.get_issue(123)

            assert issue is None


class TestGitHubServiceListBugs:
    """Tests for list_bugs method."""

    def test_list_bugs_returns_issues_with_bug_label(self):
        """Should return list of issues with bug label."""
        issues_data = [
            {"number": 1, "title": "Bug 1", "body": "", "state": "OPEN", "labels": []},
            {"number": 2, "title": "Bug 2", "body": "", "state": "OPEN", "labels": []},
        ]

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout=json.dumps(issues_data),
            )
            service = GitHubService()

            bugs = service.list_bugs()

            assert len(bugs) == 2
            assert bugs[0].number == 1
            assert bugs[1].number == 2

    def test_list_bugs_with_custom_label(self):
        """Should filter by custom label."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="[]",
            )
            service = GitHubService()

            service.list_bugs(label="critical-bug")

            # Verify the call was made with custom label
            call_args = mock_run.call_args_list[-1]
            assert "--label" in call_args[0][0]
            assert "critical-bug" in call_args[0][0]

    def test_list_bugs_returns_empty_on_error(self):
        """Should return empty list on error."""
        with patch("subprocess.run") as mock_run:
            # Init succeeds
            init_result = MagicMock(returncode=0)
            # List fails
            list_result = MagicMock(returncode=1)
            mock_run.side_effect = [init_result, list_result]

            service = GitHubService()
            bugs = service.list_bugs()

            assert bugs == []


class TestGitHubServiceCloseIssue:
    """Tests for close_issue method."""

    def test_close_issue_returns_true_on_success(self):
        """Should return True when issue is closed."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            service = GitHubService()

            result = service.close_issue(123)

            assert result is True

    def test_close_issue_with_comment(self):
        """Should include comment when provided."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            service = GitHubService()

            service.close_issue(123, comment="Fixed in PR #456")

            # Verify comment was included
            call_args = mock_run.call_args_list[-1]
            assert "--comment" in call_args[0][0]

    def test_close_issue_returns_false_on_failure(self):
        """Should return False when close fails."""
        with patch("subprocess.run") as mock_run:
            init_result = MagicMock(returncode=0)
            close_result = MagicMock(returncode=1)
            mock_run.side_effect = [init_result, close_result]

            service = GitHubService()
            result = service.close_issue(123)

            assert result is False


class TestGitHubServiceAddComment:
    """Tests for add_comment method."""

    def test_add_comment_returns_true_on_success(self):
        """Should return True when comment is added."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            service = GitHubService()

            result = service.add_comment(123, "Test comment")

            assert result is True

    def test_add_comment_returns_false_on_failure(self):
        """Should return False when add fails."""
        with patch("subprocess.run") as mock_run:
            init_result = MagicMock(returncode=0)
            comment_result = MagicMock(returncode=1)
            mock_run.side_effect = [init_result, comment_result]

            service = GitHubService()
            result = service.add_comment(123, "Test comment")

            assert result is False


class TestGitHubServiceCheckBranchExists:
    """Tests for check_branch_exists method."""

    def test_check_branch_exists_local_only(self):
        """Should detect when branch exists locally only."""
        with patch("subprocess.run") as mock_run:
            init_result = MagicMock(returncode=0)
            local_result = MagicMock(returncode=0)  # Branch exists locally
            remote_result = MagicMock(returncode=0, stdout="")  # Not on remote
            mock_run.side_effect = [init_result, local_result, remote_result]

            service = GitHubService()
            local, remote = service.check_branch_exists("fix/123-test")

            assert local is True
            assert remote is False

    def test_check_branch_exists_remote_only(self):
        """Should detect when branch exists on remote only."""
        with patch("subprocess.run") as mock_run:
            init_result = MagicMock(returncode=0)
            local_result = MagicMock(returncode=1)  # Not local
            remote_result = MagicMock(returncode=0, stdout="abc123 refs/heads/fix/123-test")
            mock_run.side_effect = [init_result, local_result, remote_result]

            service = GitHubService()
            local, remote = service.check_branch_exists("fix/123-test")

            assert local is False
            assert remote is True

    def test_check_branch_not_exists(self):
        """Should detect when branch doesn't exist."""
        with patch("subprocess.run") as mock_run:
            init_result = MagicMock(returncode=0)
            local_result = MagicMock(returncode=1)
            remote_result = MagicMock(returncode=0, stdout="")
            mock_run.side_effect = [init_result, local_result, remote_result]

            service = GitHubService()
            local, remote = service.check_branch_exists("nonexistent")

            assert local is False
            assert remote is False


class TestGitHubServiceCreateBranch:
    """Tests for create_branch method."""

    def test_create_branch_returns_true_on_success(self):
        """Should return True when branch is created."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            service = GitHubService()

            result = service.create_branch("fix/123-test")

            assert result is True

    def test_create_branch_from_custom_base(self):
        """Should checkout custom base branch."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            service = GitHubService()

            service.create_branch("fix/123-test", from_branch="develop")

            # Verify checkout of base branch
            calls = mock_run.call_args_list
            checkout_calls = [c for c in calls if "checkout" in str(c)]
            assert len(checkout_calls) >= 2  # One for base, one for new branch

    def test_create_branch_returns_false_on_failure(self):
        """Should return False when create fails."""
        with patch("subprocess.run") as mock_run:
            # Init succeeds
            init_result = MagicMock(returncode=0)
            # Checkout base succeeds
            checkout_result = MagicMock(returncode=0)
            # Create fails
            create_result = MagicMock(returncode=1)
            mock_run.side_effect = [init_result, checkout_result, create_result]

            service = GitHubService()
            result = service.create_branch("fix/123-test")

            assert result is False
