"""Unit tests for GitHub roadmap service.

Tests the GitHubService class that interacts with GitHub via gh CLI,
mocking subprocess calls to test various scenarios for roadmap epic integration.
"""

import json
import subprocess
from unittest.mock import MagicMock, patch

import pytest

from doit_cli.models.github_epic import GitHubEpic
from doit_cli.models.github_feature import GitHubFeature
from doit_cli.services.github_service import (
    GitHubAPIError,
    GitHubAuthError,
    GitHubService,
)


@pytest.fixture
def github_service():
    """Create a GitHubService instance for testing."""
    return GitHubService(timeout=30)


@pytest.fixture
def mock_epic_data():
    """Sample epic data from GitHub API."""
    return {
        "number": 577,
        "title": "[Epic]: GitHub Integration",
        "state": "open",
        "labels": [{"name": "epic"}, {"name": "priority:P2"}],
        "body": "Integration with GitHub epics",
        "url": "https://github.com/owner/repo/issues/577",
        "createdAt": "2026-01-21T10:00:00Z",
        "updatedAt": "2026-01-21T15:30:00Z",
    }


@pytest.fixture
def mock_feature_data():
    """Sample feature data from GitHub API."""
    return {
        "number": 578,
        "title": "[Feature]: Display Epics",
        "state": "open",
        "labels": [{"name": "feature"}, {"name": "priority:P1"}],
        "url": "https://github.com/owner/repo/issues/578",
    }


class TestFetchEpics:
    """Tests for fetch_epics method."""

    @patch("doit_cli.services.github_service.is_gh_authenticated")
    @patch("doit_cli.services.github_service.has_gh_cli")
    @patch("subprocess.run")
    def test_fetch_epics_success(
        self, mock_run, mock_has_cli, mock_is_auth, github_service, mock_epic_data
    ):
        """Test successful fetch of GitHub epics."""
        # Mock authentication checks
        mock_has_cli.return_value = True
        mock_is_auth.return_value = True

        # Mock successful subprocess call
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps([mock_epic_data]),
            stderr="",
        )

        # Execute
        epics = github_service.fetch_epics()

        # Assert
        assert len(epics) == 1
        assert isinstance(epics[0], GitHubEpic)
        assert epics[0].number == 577
        assert epics[0].title == "[Epic]: GitHub Integration"
        assert epics[0].state == "open"

        # Verify gh CLI was called correctly
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "gh"
        assert call_args[1] == "issue"
        assert call_args[2] == "list"
        assert "--label" in call_args
        assert "epic" in call_args

    @patch("doit_cli.services.github_service.is_gh_authenticated")
    @patch("doit_cli.services.github_service.has_gh_cli")
    @patch("subprocess.run")
    def test_fetch_epics_empty_list(
        self, mock_run, mock_has_cli, mock_is_auth, github_service
    ):
        """Test fetch_epics returns empty list when no epics exist."""
        mock_has_cli.return_value = True
        mock_is_auth.return_value = True

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="[]",
            stderr="",
        )

        epics = github_service.fetch_epics()

        assert len(epics) == 0
        assert isinstance(epics, list)

    @patch("doit_cli.services.github_service.is_gh_authenticated")
    @patch("doit_cli.services.github_service.has_gh_cli")
    @patch("subprocess.run")
    def test_fetch_epics_multiple_states(
        self, mock_run, mock_has_cli, mock_is_auth, github_service, mock_epic_data
    ):
        """Test fetch_epics with different state filters."""
        mock_has_cli.return_value = True
        mock_is_auth.return_value = True

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps([mock_epic_data]),
            stderr="",
        )

        # Test with 'closed' state
        epics = github_service.fetch_epics(state="closed")
        assert len(epics) == 1

        # Verify state parameter was passed
        call_args = mock_run.call_args[0][0]
        assert "--state" in call_args
        assert "closed" in call_args

    @patch("doit_cli.services.github_service.has_gh_cli")
    def test_fetch_epics_no_gh_cli(self, mock_has_cli, github_service):
        """Test fetch_epics raises error when gh CLI not installed."""
        mock_has_cli.return_value = False

        with pytest.raises(GitHubAuthError) as exc_info:
            github_service.fetch_epics()

        assert "not installed" in str(exc_info.value)
        assert "cli.github.com" in str(exc_info.value)

    @patch("doit_cli.services.github_service.is_gh_authenticated")
    @patch("doit_cli.services.github_service.has_gh_cli")
    def test_fetch_epics_not_authenticated(
        self, mock_has_cli, mock_is_auth, github_service
    ):
        """Test fetch_epics raises error when not authenticated."""
        mock_has_cli.return_value = True
        mock_is_auth.return_value = False

        with pytest.raises(GitHubAuthError) as exc_info:
            github_service.fetch_epics()

        assert "not authenticated" in str(exc_info.value)
        assert "gh auth login" in str(exc_info.value)

    @patch("doit_cli.services.github_service.is_gh_authenticated")
    @patch("doit_cli.services.github_service.has_gh_cli")
    @patch("subprocess.run")
    def test_fetch_epics_rate_limit_error(
        self, mock_run, mock_has_cli, mock_is_auth, github_service
    ):
        """Test fetch_epics handles rate limit error."""
        mock_has_cli.return_value = True
        mock_is_auth.return_value = True

        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="API rate limit exceeded",
        )

        with pytest.raises(GitHubAPIError) as exc_info:
            github_service.fetch_epics()

        assert "rate limit" in str(exc_info.value).lower()
        assert "--skip-github" in str(exc_info.value)

    @patch("doit_cli.services.github_service.is_gh_authenticated")
    @patch("doit_cli.services.github_service.has_gh_cli")
    @patch("subprocess.run")
    def test_fetch_epics_timeout(
        self, mock_run, mock_has_cli, mock_is_auth, github_service
    ):
        """Test fetch_epics handles timeout."""
        mock_has_cli.return_value = True
        mock_is_auth.return_value = True

        mock_run.side_effect = subprocess.TimeoutExpired(cmd="gh", timeout=30)

        with pytest.raises(GitHubAPIError) as exc_info:
            github_service.fetch_epics()

        assert "timeout" in str(exc_info.value).lower()
        assert "30 seconds" in str(exc_info.value)

    @patch("doit_cli.services.github_service.is_gh_authenticated")
    @patch("doit_cli.services.github_service.has_gh_cli")
    @patch("subprocess.run")
    def test_fetch_epics_invalid_json(
        self, mock_run, mock_has_cli, mock_is_auth, github_service
    ):
        """Test fetch_epics handles invalid JSON response."""
        mock_has_cli.return_value = True
        mock_is_auth.return_value = True

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="invalid json {",
            stderr="",
        )

        with pytest.raises(GitHubAPIError) as exc_info:
            github_service.fetch_epics()

        assert "parse" in str(exc_info.value).lower()

    @patch("doit_cli.services.github_service.is_gh_authenticated")
    @patch("doit_cli.services.github_service.has_gh_cli")
    @patch("subprocess.run")
    def test_fetch_epics_malformed_epic_skipped(
        self, mock_run, mock_has_cli, mock_is_auth, github_service, mock_epic_data, capsys
    ):
        """Test fetch_epics skips malformed epics and continues."""
        mock_has_cli.return_value = True
        mock_is_auth.return_value = True

        # Create malformed epic (missing required field)
        malformed_epic = {"number": 999}  # Missing title, state, etc.

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps([malformed_epic, mock_epic_data]),
            stderr="",
        )

        epics = github_service.fetch_epics()

        # Should skip malformed and return only valid epic
        assert len(epics) == 1
        assert epics[0].number == 577

        # Verify warning was printed
        captured = capsys.readouterr()
        assert "Warning" in captured.out
        assert "#999" in captured.out

    @patch("doit_cli.services.github_service.is_gh_authenticated")
    @patch("doit_cli.services.github_service.has_gh_cli")
    @patch("subprocess.run")
    def test_fetch_epics_gh_not_in_path(
        self, mock_run, mock_has_cli, mock_is_auth, github_service
    ):
        """Test fetch_epics handles gh CLI not in PATH."""
        mock_has_cli.return_value = True
        mock_is_auth.return_value = True

        mock_run.side_effect = FileNotFoundError("gh not found")

        with pytest.raises(GitHubAuthError) as exc_info:
            github_service.fetch_epics()

        assert "not found in PATH" in str(exc_info.value)


class TestFetchFeaturesForEpic:
    """Tests for fetch_features_for_epic method."""

    @patch("doit_cli.services.github_service.is_gh_authenticated")
    @patch("doit_cli.services.github_service.has_gh_cli")
    @patch("subprocess.run")
    def test_fetch_features_success(
        self, mock_run, mock_has_cli, mock_is_auth, github_service, mock_feature_data
    ):
        """Test successful fetch of features for an epic."""
        mock_has_cli.return_value = True
        mock_is_auth.return_value = True

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps([mock_feature_data]),
            stderr="",
        )

        features = github_service.fetch_features_for_epic(577)

        assert len(features) == 1
        assert isinstance(features[0], GitHubFeature)
        assert features[0].number == 578
        assert features[0].epic_number == 577

        # Verify search query
        call_args = mock_run.call_args[0][0]
        assert "gh" in call_args
        assert "--search" in call_args
        search_query_idx = call_args.index("--search") + 1
        assert "part of epic #577" in call_args[search_query_idx].lower()

    @patch("doit_cli.services.github_service.is_gh_authenticated")
    @patch("doit_cli.services.github_service.has_gh_cli")
    @patch("subprocess.run")
    def test_fetch_features_empty_list(
        self, mock_run, mock_has_cli, mock_is_auth, github_service
    ):
        """Test fetch_features_for_epic with no features."""
        mock_has_cli.return_value = True
        mock_is_auth.return_value = True

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="[]",
            stderr="",
        )

        features = github_service.fetch_features_for_epic(577)

        assert len(features) == 0
        assert isinstance(features, list)

    @patch("doit_cli.services.github_service.is_gh_authenticated")
    @patch("doit_cli.services.github_service.has_gh_cli")
    @patch("subprocess.run")
    def test_fetch_features_rate_limit(
        self, mock_run, mock_has_cli, mock_is_auth, github_service
    ):
        """Test fetch_features_for_epic handles rate limit."""
        mock_has_cli.return_value = True
        mock_is_auth.return_value = True

        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="API rate limit exceeded",
        )

        with pytest.raises(GitHubAPIError) as exc_info:
            github_service.fetch_features_for_epic(577)

        assert "rate limit" in str(exc_info.value).lower()

    @patch("doit_cli.services.github_service.is_gh_authenticated")
    @patch("doit_cli.services.github_service.has_gh_cli")
    @patch("subprocess.run")
    def test_fetch_features_timeout(
        self, mock_run, mock_has_cli, mock_is_auth, github_service
    ):
        """Test fetch_features_for_epic handles timeout."""
        mock_has_cli.return_value = True
        mock_is_auth.return_value = True

        mock_run.side_effect = subprocess.TimeoutExpired(cmd="gh", timeout=30)

        with pytest.raises(GitHubAPIError) as exc_info:
            github_service.fetch_features_for_epic(577)

        assert "timeout" in str(exc_info.value).lower()

    @patch("doit_cli.services.github_service.is_gh_authenticated")
    @patch("doit_cli.services.github_service.has_gh_cli")
    @patch("subprocess.run")
    def test_fetch_features_invalid_json(
        self, mock_run, mock_has_cli, mock_is_auth, github_service
    ):
        """Test fetch_features_for_epic handles invalid JSON."""
        mock_has_cli.return_value = True
        mock_is_auth.return_value = True

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="not valid json",
            stderr="",
        )

        with pytest.raises(GitHubAPIError) as exc_info:
            github_service.fetch_features_for_epic(577)

        assert "parse" in str(exc_info.value).lower()

    @patch("doit_cli.services.github_service.is_gh_authenticated")
    @patch("doit_cli.services.github_service.has_gh_cli")
    @patch("subprocess.run")
    def test_fetch_features_malformed_feature_skipped(
        self, mock_run, mock_has_cli, mock_is_auth, github_service, mock_feature_data, capsys
    ):
        """Test fetch_features_for_epic skips malformed features."""
        mock_has_cli.return_value = True
        mock_is_auth.return_value = True

        malformed_feature = {"number": 999}  # Missing required fields

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps([malformed_feature, mock_feature_data]),
            stderr="",
        )

        features = github_service.fetch_features_for_epic(577)

        # Should skip malformed and return only valid feature
        assert len(features) == 1
        assert features[0].number == 578

        # Verify warning
        captured = capsys.readouterr()
        assert "Warning" in captured.out
        assert "#999" in captured.out


class TestCreateEpic:
    """Tests for create_epic method."""

    @patch("doit_cli.services.github_service.is_gh_authenticated")
    @patch("doit_cli.services.github_service.has_gh_cli")
    @patch("subprocess.run")
    def test_create_epic_success(
        self, mock_run, mock_has_cli, mock_is_auth, github_service
    ):
        """Test successful epic creation."""
        mock_has_cli.return_value = True
        mock_is_auth.return_value = True

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="https://github.com/owner/repo/issues/700\n",
            stderr="",
        )

        epic = github_service.create_epic(
            title="[Epic]: New Feature",
            body="Feature description",
            priority="P2",
        )

        assert isinstance(epic, GitHubEpic)
        assert epic.number == 700
        assert epic.title == "[Epic]: New Feature"
        assert epic.state == "open"
        assert "epic" in epic.labels
        assert "priority:P2" in epic.labels
        assert epic.url == "https://github.com/owner/repo/issues/700"

        # Verify gh CLI was called correctly
        call_args = mock_run.call_args[0][0]
        assert "gh" in call_args
        assert "issue" in call_args
        assert "create" in call_args
        assert "--title" in call_args
        assert "[Epic]: New Feature" in call_args
        assert "--body" in call_args
        assert "Feature description" in call_args
        assert "--label" in call_args

    @patch("doit_cli.services.github_service.is_gh_authenticated")
    @patch("doit_cli.services.github_service.has_gh_cli")
    @patch("subprocess.run")
    def test_create_epic_with_additional_labels(
        self, mock_run, mock_has_cli, mock_is_auth, github_service
    ):
        """Test create_epic with additional labels."""
        mock_has_cli.return_value = True
        mock_is_auth.return_value = True

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="https://github.com/owner/repo/issues/701\n",
            stderr="",
        )

        epic = github_service.create_epic(
            title="[Epic]: Test",
            body="Test description",
            priority="P1",
            labels=["enhancement", "needs-review"],
        )

        assert epic.number == 701
        assert "epic" in epic.labels
        assert "priority:P1" in epic.labels
        assert "enhancement" in epic.labels
        assert "needs-review" in epic.labels

        # Verify labels were passed correctly
        call_args = mock_run.call_args[0][0]
        label_idx = call_args.index("--label") + 1
        labels_str = call_args[label_idx]
        assert "epic" in labels_str
        assert "priority:P1" in labels_str
        assert "enhancement" in labels_str
        assert "needs-review" in labels_str

    @patch("doit_cli.services.github_service.is_gh_authenticated")
    @patch("doit_cli.services.github_service.has_gh_cli")
    @patch("subprocess.run")
    def test_create_epic_default_priority(
        self, mock_run, mock_has_cli, mock_is_auth, github_service
    ):
        """Test create_epic uses default P3 priority."""
        mock_has_cli.return_value = True
        mock_is_auth.return_value = True

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="https://github.com/owner/repo/issues/702\n",
            stderr="",
        )

        epic = github_service.create_epic(
            title="[Epic]: Default Priority", body="Description"
        )

        assert "priority:P3" in epic.labels

    @patch("doit_cli.services.github_service.has_gh_cli")
    def test_create_epic_not_authenticated(self, mock_has_cli, github_service):
        """Test create_epic requires authentication."""
        mock_has_cli.return_value = False

        with pytest.raises(GitHubAuthError):
            github_service.create_epic(title="Test", body="Test")

    @patch("doit_cli.services.github_service.is_gh_authenticated")
    @patch("doit_cli.services.github_service.has_gh_cli")
    @patch("subprocess.run")
    def test_create_epic_rate_limit(
        self, mock_run, mock_has_cli, mock_is_auth, github_service
    ):
        """Test create_epic handles rate limit."""
        mock_has_cli.return_value = True
        mock_is_auth.return_value = True

        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="API rate limit exceeded",
        )

        with pytest.raises(GitHubAPIError) as exc_info:
            github_service.create_epic(title="Test", body="Test")

        assert "rate limit" in str(exc_info.value).lower()

    @patch("doit_cli.services.github_service.is_gh_authenticated")
    @patch("doit_cli.services.github_service.has_gh_cli")
    @patch("subprocess.run")
    def test_create_epic_timeout(
        self, mock_run, mock_has_cli, mock_is_auth, github_service
    ):
        """Test create_epic handles timeout."""
        mock_has_cli.return_value = True
        mock_is_auth.return_value = True

        mock_run.side_effect = subprocess.TimeoutExpired(cmd="gh", timeout=30)

        with pytest.raises(GitHubAPIError) as exc_info:
            github_service.create_epic(title="Test", body="Test")

        assert "timeout" in str(exc_info.value).lower()

    @patch("doit_cli.services.github_service.is_gh_authenticated")
    @patch("doit_cli.services.github_service.has_gh_cli")
    @patch("subprocess.run")
    def test_create_epic_invalid_url(
        self, mock_run, mock_has_cli, mock_is_auth, github_service
    ):
        """Test create_epic handles invalid URL response."""
        mock_has_cli.return_value = True
        mock_is_auth.return_value = True

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="not-a-valid-url",
            stderr="",
        )

        with pytest.raises(GitHubAPIError) as exc_info:
            github_service.create_epic(title="Test", body="Test")

        assert "parse" in str(exc_info.value).lower()

    @patch("doit_cli.services.github_service.is_gh_authenticated")
    @patch("doit_cli.services.github_service.has_gh_cli")
    @patch("subprocess.run")
    def test_create_epic_general_error(
        self, mock_run, mock_has_cli, mock_is_auth, github_service
    ):
        """Test create_epic handles general GitHub errors."""
        mock_has_cli.return_value = True
        mock_is_auth.return_value = True

        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="GraphQL: Label does not exist",
        )

        with pytest.raises(GitHubAPIError) as exc_info:
            github_service.create_epic(title="Test", body="Test")

        assert "Failed to create epic" in str(exc_info.value)
        assert "Label does not exist" in str(exc_info.value)


class TestGitHubServiceInit:
    """Tests for GitHubService initialization."""

    def test_default_timeout(self):
        """Test default timeout is 30 seconds."""
        service = GitHubService()
        assert service.timeout == 30

    def test_custom_timeout(self):
        """Test custom timeout can be set."""
        service = GitHubService(timeout=60)
        assert service.timeout == 60
