"""Integration tests for team collaboration workflow."""

import json
import pytest
from pathlib import Path
from typer.testing import CliRunner
from unittest.mock import patch


runner = CliRunner()


@pytest.fixture
def git_project(project_dir):
    """Create a project directory with Git initialized."""
    import subprocess

    # Initialize git repo
    subprocess.run(["git", "init"], cwd=project_dir, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=project_dir,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=project_dir,
        capture_output=True,
    )

    # Create initial commit
    readme = project_dir / "README.md"
    readme.write_text("# Test Project\n")
    subprocess.run(["git", "add", "."], cwd=project_dir, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=project_dir,
        capture_output=True,
    )

    return project_dir


@pytest.fixture
def team_project(git_project):
    """Create a project with team collaboration initialized."""
    from doit_cli.main import app

    with runner.isolated_filesystem():
        # Copy git_project to isolated filesystem
        import shutil
        import os

        # Change to git_project directory for the test
        old_cwd = os.getcwd()
        os.chdir(git_project)

        try:
            result = runner.invoke(
                app, ["team", "init", "--name", "Test Team", "--owner", "owner@example.com"]
            )
            assert result.exit_code == 0
            yield git_project
        finally:
            os.chdir(old_cwd)


class TestTeamInit:
    """Tests for team init command."""

    def test_team_init_creates_config(self, git_project):
        """Test that team init creates team.yaml config."""
        from doit_cli.main import app
        import os

        old_cwd = os.getcwd()
        os.chdir(git_project)

        try:
            result = runner.invoke(
                app, ["team", "init", "--name", "My Team", "--owner", "owner@example.com"]
            )

            assert result.exit_code == 0
            assert "initialized" in result.output.lower()

            config_path = git_project / ".doit" / "config" / "team.yaml"
            assert config_path.exists()
        finally:
            os.chdir(old_cwd)

    def test_team_init_uses_git_email_as_default(self, git_project):
        """Test that team init defaults to git user.email for owner."""
        from doit_cli.main import app
        import os

        old_cwd = os.getcwd()
        os.chdir(git_project)

        try:
            result = runner.invoke(app, ["team", "init", "--name", "My Team"])

            assert result.exit_code == 0
            assert "test@example.com" in result.output  # Git email from fixture
        finally:
            os.chdir(old_cwd)

    def test_team_init_rejects_duplicate(self, git_project):
        """Test that team init fails if already initialized."""
        from doit_cli.main import app
        import os

        old_cwd = os.getcwd()
        os.chdir(git_project)

        try:
            # First init
            runner.invoke(
                app, ["team", "init", "--name", "Team", "--owner", "owner@example.com"]
            )

            # Second init should fail
            result = runner.invoke(
                app, ["team", "init", "--name", "Team 2", "--owner", "other@example.com"]
            )

            assert result.exit_code != 0
            assert "already initialized" in result.output.lower()
        finally:
            os.chdir(old_cwd)


class TestTeamMemberManagement:
    """Tests for team member management commands."""

    def test_add_member(self, git_project):
        """Test adding a team member."""
        from doit_cli.main import app
        import os

        old_cwd = os.getcwd()
        os.chdir(git_project)

        try:
            # Initialize team
            runner.invoke(
                app, ["team", "init", "--name", "Team", "--owner", "owner@example.com"]
            )

            # Add member
            result = runner.invoke(app, ["team", "add", "member@example.com"])

            assert result.exit_code == 0
            assert "added" in result.output.lower()
        finally:
            os.chdir(old_cwd)

    def test_add_member_with_role(self, git_project):
        """Test adding a team member with owner role."""
        from doit_cli.main import app
        import os

        old_cwd = os.getcwd()
        os.chdir(git_project)

        try:
            runner.invoke(
                app, ["team", "init", "--name", "Team", "--owner", "owner@example.com"]
            )

            result = runner.invoke(
                app, ["team", "add", "member@example.com", "--role", "owner"]
            )

            assert result.exit_code == 0
            assert "owner" in result.output.lower()
        finally:
            os.chdir(old_cwd)

    def test_add_member_read_only(self, git_project):
        """Test adding a read-only team member."""
        from doit_cli.main import app
        import os

        old_cwd = os.getcwd()
        os.chdir(git_project)

        try:
            runner.invoke(
                app, ["team", "init", "--name", "Team", "--owner", "owner@example.com"]
            )

            result = runner.invoke(
                app, ["team", "add", "member@example.com", "--permission", "read-only"]
            )

            assert result.exit_code == 0
            assert "read-only" in result.output.lower()
        finally:
            os.chdir(old_cwd)

    def test_add_duplicate_member_fails(self, git_project):
        """Test that adding duplicate member fails."""
        from doit_cli.main import app
        import os

        old_cwd = os.getcwd()
        os.chdir(git_project)

        try:
            runner.invoke(
                app, ["team", "init", "--name", "Team", "--owner", "owner@example.com"]
            )
            runner.invoke(app, ["team", "add", "member@example.com"])

            result = runner.invoke(app, ["team", "add", "member@example.com"])

            assert result.exit_code != 0
            assert "already exists" in result.output.lower()
        finally:
            os.chdir(old_cwd)

    def test_list_members(self, git_project):
        """Test listing team members."""
        from doit_cli.main import app
        import os

        old_cwd = os.getcwd()
        os.chdir(git_project)

        try:
            runner.invoke(
                app, ["team", "init", "--name", "Team", "--owner", "owner@example.com"]
            )
            runner.invoke(app, ["team", "add", "member@example.com"])

            result = runner.invoke(app, ["team", "list"])

            assert result.exit_code == 0
            assert "owner@example.com" in result.output
            assert "member@example.com" in result.output
        finally:
            os.chdir(old_cwd)

    def test_list_members_json_format(self, git_project):
        """Test listing members in JSON format."""
        from doit_cli.main import app
        import os

        old_cwd = os.getcwd()
        os.chdir(git_project)

        try:
            runner.invoke(
                app, ["team", "init", "--name", "Team", "--owner", "owner@example.com"]
            )

            result = runner.invoke(app, ["team", "list", "--format", "json"])

            assert result.exit_code == 0
            # Should be valid JSON
            data = json.loads(result.output)
            assert "members" in data
            assert len(data["members"]) == 1
        finally:
            os.chdir(old_cwd)

    def test_remove_member(self, git_project):
        """Test removing a team member."""
        from doit_cli.main import app
        import os

        old_cwd = os.getcwd()
        os.chdir(git_project)

        try:
            runner.invoke(
                app, ["team", "init", "--name", "Team", "--owner", "owner@example.com"]
            )
            runner.invoke(app, ["team", "add", "member@example.com"])

            result = runner.invoke(
                app, ["team", "remove", "member@example.com", "--force"]
            )

            assert result.exit_code == 0
            assert "removed" in result.output.lower()
        finally:
            os.chdir(old_cwd)


class TestTeamStatus:
    """Tests for team status command."""

    def test_status_shows_team_info(self, git_project):
        """Test that status shows team information."""
        from doit_cli.main import app
        import os

        old_cwd = os.getcwd()
        os.chdir(git_project)

        try:
            runner.invoke(
                app, ["team", "init", "--name", "Test Team", "--owner", "owner@example.com"]
            )

            result = runner.invoke(app, ["team", "status"])

            assert result.exit_code == 0
            assert "Test Team" in result.output
        finally:
            os.chdir(old_cwd)


class TestTeamNotifications:
    """Tests for team notification commands."""

    def test_notify_list_empty(self, git_project):
        """Test listing notifications when empty."""
        from doit_cli.main import app
        import os

        old_cwd = os.getcwd()
        os.chdir(git_project)

        try:
            runner.invoke(
                app, ["team", "init", "--name", "Team", "--owner", "owner@example.com"]
            )

            result = runner.invoke(app, ["team", "notify", "list"])

            assert result.exit_code == 0
            assert "no unread" in result.output.lower()
        finally:
            os.chdir(old_cwd)

    def test_notify_config_show(self, git_project):
        """Test showing notification config."""
        from doit_cli.main import app
        import os

        old_cwd = os.getcwd()
        os.chdir(git_project)

        try:
            runner.invoke(
                app, ["team", "init", "--name", "Team", "--owner", "owner@example.com"]
            )

            result = runner.invoke(app, ["team", "notify", "config"])

            assert result.exit_code == 0
            assert "settings" in result.output.lower()
        finally:
            os.chdir(old_cwd)


class TestTeamConfig:
    """Tests for team config command."""

    def test_config_shows_settings(self, git_project):
        """Test that config shows team settings."""
        from doit_cli.main import app
        import os

        old_cwd = os.getcwd()
        os.chdir(git_project)

        try:
            runner.invoke(
                app, ["team", "init", "--name", "My Team", "--owner", "owner@example.com"]
            )

            result = runner.invoke(app, ["team", "config"])

            assert result.exit_code == 0
            assert "My Team" in result.output
            assert "owner@example.com" in result.output
        finally:
            os.chdir(old_cwd)

    def test_config_json_format(self, git_project):
        """Test config in JSON format."""
        from doit_cli.main import app
        import os

        old_cwd = os.getcwd()
        os.chdir(git_project)

        try:
            runner.invoke(
                app, ["team", "init", "--name", "Team", "--owner", "owner@example.com"]
            )

            result = runner.invoke(app, ["team", "config", "--format", "json"])

            assert result.exit_code == 0
            data = json.loads(result.output)
            assert "team" in data
            assert data["team"]["name"] == "Team"
        finally:
            os.chdir(old_cwd)


class TestTeamConflicts:
    """Tests for team conflict commands."""

    def test_conflict_list_empty(self, git_project):
        """Test listing conflicts when none exist."""
        from doit_cli.main import app
        import os

        old_cwd = os.getcwd()
        os.chdir(git_project)

        try:
            runner.invoke(
                app, ["team", "init", "--name", "Team", "--owner", "owner@example.com"]
            )

            result = runner.invoke(app, ["team", "conflict", "list"])

            assert result.exit_code == 0
            assert "no active conflicts" in result.output.lower()
        finally:
            os.chdir(old_cwd)


class TestUninitializedTeam:
    """Tests for commands when team is not initialized."""

    def test_add_fails_without_init(self, git_project):
        """Test that add fails without team init."""
        from doit_cli.main import app
        import os

        old_cwd = os.getcwd()
        os.chdir(git_project)

        try:
            result = runner.invoke(app, ["team", "add", "member@example.com"])

            assert result.exit_code != 0
            assert "not initialized" in result.output.lower() or "init" in result.output.lower()
        finally:
            os.chdir(old_cwd)

    def test_list_fails_without_init(self, git_project):
        """Test that list fails without team init."""
        from doit_cli.main import app
        import os

        old_cwd = os.getcwd()
        os.chdir(git_project)

        try:
            result = runner.invoke(app, ["team", "list"])

            assert result.exit_code != 0
        finally:
            os.chdir(old_cwd)
