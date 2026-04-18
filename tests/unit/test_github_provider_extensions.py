"""Tests for the GitHubProvider methods added in the extension PR.

Covers close_issue, add_issue_comment, check_branch_exists, create_branch —
the four operations the legacy github_service shim exposed that the
provider did not. We mock `subprocess.run` to exercise the command
assembly and return-code branches without hitting gh CLI.
"""

from __future__ import annotations

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from doit_cli.services.providers.github import GitHubProvider


@pytest.fixture
def provider() -> GitHubProvider:
    return GitHubProvider(timeout=5)


def _ok(stdout: str = "", stderr: str = "") -> MagicMock:
    """Build a CompletedProcess stub that returncode=0."""
    m = MagicMock()
    m.returncode = 0
    m.stdout = stdout
    m.stderr = stderr
    return m


def _fail(returncode: int = 1, stderr: str = "") -> MagicMock:
    m = MagicMock()
    m.returncode = returncode
    m.stdout = ""
    m.stderr = stderr
    return m


class TestAddIssueComment:
    @patch("doit_cli.services.providers.github.subprocess.run")
    def test_posts_comment_returns_true_on_success(
        self, mock_run, provider: GitHubProvider
    ) -> None:
        mock_run.side_effect = [_ok("ok"), _ok("ok")]  # auth + comment

        result = provider.add_issue_comment("123", "looks good")

        assert result is True
        # The second call is the comment itself.
        call_args = mock_run.call_args_list[1].args[0]
        assert call_args[:4] == ["gh", "issue", "comment", "123"]
        assert "--body" in call_args and "looks good" in call_args

    @patch("doit_cli.services.providers.github.subprocess.run")
    def test_returns_false_when_gh_fails(self, mock_run, provider: GitHubProvider) -> None:
        mock_run.side_effect = [_ok(), _fail(1, "rate limited")]
        assert provider.add_issue_comment("123", "hi") is False

    @patch("doit_cli.services.providers.github.subprocess.run")
    def test_strips_unified_id_prefix(self, mock_run, provider: GitHubProvider) -> None:
        """Unified IDs like `github:123` get reduced to the raw number."""
        mock_run.side_effect = [_ok(), _ok()]
        provider.add_issue_comment("github:123", "x")
        call_args = mock_run.call_args_list[1].args[0]
        assert call_args[3] == "123"


class TestCloseIssue:
    @patch("doit_cli.services.providers.github.subprocess.run")
    def test_close_without_comment(self, mock_run, provider: GitHubProvider) -> None:
        mock_run.side_effect = [_ok(), _ok()]  # auth + close

        assert provider.close_issue("42") is True
        call_args = mock_run.call_args_list[1].args[0]
        assert call_args == ["gh", "issue", "close", "42"]

    @patch("doit_cli.services.providers.github.subprocess.run")
    def test_close_with_comment(self, mock_run, provider: GitHubProvider) -> None:
        mock_run.side_effect = [_ok(), _ok()]

        assert provider.close_issue("42", comment="done") is True
        call_args = mock_run.call_args_list[1].args[0]
        assert "--comment" in call_args
        assert "done" in call_args

    @patch("doit_cli.services.providers.github.subprocess.run")
    def test_returns_false_on_gh_failure(self, mock_run, provider: GitHubProvider) -> None:
        mock_run.side_effect = [_ok(), _fail()]
        assert provider.close_issue("42") is False


class TestCheckBranchExists:
    @patch("doit_cli.services.providers.github.subprocess.run")
    def test_both_local_and_remote_found(
        self, mock_run, provider: GitHubProvider
    ) -> None:
        mock_run.side_effect = [_ok("  feature-x"), _ok("abcdef123\trefs/heads/feature-x")]

        local, remote = provider.check_branch_exists("feature-x")

        assert local is True
        assert remote is True

    @patch("doit_cli.services.providers.github.subprocess.run")
    def test_only_local(self, mock_run, provider: GitHubProvider) -> None:
        mock_run.side_effect = [_ok("  feature-x"), _ok("")]
        local, remote = provider.check_branch_exists("feature-x")
        assert local is True
        assert remote is False

    @patch("doit_cli.services.providers.github.subprocess.run")
    def test_neither(self, mock_run, provider: GitHubProvider) -> None:
        mock_run.side_effect = [_ok(""), _ok("")]
        local, remote = provider.check_branch_exists("feature-missing")
        assert local is False
        assert remote is False

    @patch("doit_cli.services.providers.github.subprocess.run")
    def test_remote_unreachable_falls_back_to_false(
        self, mock_run, provider: GitHubProvider
    ) -> None:
        mock_run.side_effect = [_ok("  feature-x"), subprocess.SubprocessError("offline")]
        local, remote = provider.check_branch_exists("feature-x")
        assert local is True
        assert remote is False


class TestCreateBranch:
    @patch("doit_cli.services.providers.github.subprocess.run")
    def test_checkout_new_branch(self, mock_run, provider: GitHubProvider) -> None:
        mock_run.return_value = _ok()

        assert provider.create_branch("feature-y", from_branch="main") is True
        mock_run.assert_called_once()
        call_args = mock_run.call_args.args[0]
        assert call_args == ["git", "checkout", "-b", "feature-y", "main"]

    @patch("doit_cli.services.providers.github.subprocess.run")
    def test_returns_false_on_git_failure(
        self, mock_run, provider: GitHubProvider
    ) -> None:
        mock_run.return_value = _fail(128, "fatal: A branch named 'x' already exists")
        assert provider.create_branch("x") is False

    @patch("doit_cli.services.providers.github.subprocess.run")
    def test_default_parent_branch_is_main(
        self, mock_run, provider: GitHubProvider
    ) -> None:
        mock_run.return_value = _ok()
        provider.create_branch("feature-z")
        call_args = mock_run.call_args.args[0]
        assert call_args[-1] == "main"
