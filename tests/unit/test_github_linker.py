"""Unit tests for GitHubLinker service."""

import pytest
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from doit_cli.services.github_linker import (
    GitHubLinkerService,
    EpicReference,
    SpecReference
)
from doit_cli.services.github_service import GitHubServiceError


@pytest.fixture
def temp_spec_dir():
    """Create temporary directory for test spec files."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_spec_content():
    """Sample spec file content."""
    return """---
Feature: "Test Feature"
Branch: "[001-test]"
Created: "2026-01-22"
Status: "Draft"
---

# Feature Specification: Test Feature

Content here.
"""


@pytest.fixture
def sample_epic_data():
    """Sample GitHub epic data."""
    return {
        "number": 123,
        "title": "Test Epic",
        "body": "Epic description\n\nSome content here.",
        "state": "open",
        "labels": ["epic", "priority:P1"],
        "url": "https://github.com/owner/repo/issues/123",
        "priority": "P1"
    }


@pytest.fixture
def mock_github_service():
    """Create a mock GitHub service."""
    mock = Mock()
    return mock


class TestEpicReference:
    """Tests for EpicReference dataclass."""

    def test_create_epic_reference(self):
        """Test creating an epic reference."""
        ref = EpicReference(
            number=123,
            url="https://github.com/owner/repo/issues/123",
            priority="P1"
        )
        assert ref.number == 123
        assert ref.url == "https://github.com/owner/repo/issues/123"
        assert ref.priority == "P1"


class TestSpecReference:
    """Tests for SpecReference dataclass."""

    def test_create_spec_reference(self):
        """Test creating a spec reference."""
        ref = SpecReference(
            file_path="specs/001-test/spec.md",
            feature_name="Test Feature",
            branch_name="001-test"
        )
        assert ref.file_path == "specs/001-test/spec.md"
        assert ref.feature_name == "Test Feature"


class TestGetEpicDetails:
    """Tests for get_epic_details method."""

    @patch('subprocess.run')
    @patch.object(GitHubLinkerService, '_get_repo_slug', return_value='owner/repo')
    def test_get_epic_details_success(self, mock_repo_slug, mock_run, sample_epic_data):
        """Test successfully fetching epic details."""
        # Mock subprocess response
        mock_result = Mock()
        mock_result.stdout = json.dumps(sample_epic_data)
        mock_run.return_value = mock_result

        linker = GitHubLinkerService()
        epic = linker.get_epic_details(123)

        assert epic["number"] == 123
        assert epic["title"] == "Test Epic"
        assert epic["state"] == "open"
        assert epic["priority"] == "P1"

    @patch('subprocess.run')
    @patch.object(GitHubLinkerService, '_get_repo_slug', return_value='owner/repo')
    def test_get_epic_details_not_found(self, mock_repo_slug, mock_run, mock_github_service):
        """Test fetching non-existent epic."""
        import subprocess
        mock_run.side_effect = subprocess.CalledProcessError(
            1, 'gh', stderr="404 Not Found"
        )

        linker = GitHubLinkerService(github_service=mock_github_service)

        with pytest.raises(GitHubServiceError, match="not found"):
            linker.get_epic_details(999)

    @patch('subprocess.run')
    @patch.object(GitHubLinkerService, '_get_repo_slug', return_value='owner/repo')
    def test_get_epic_details_invalid_number(self, mock_repo_slug, mock_run):
        """Test fetching epic with invalid number."""
        linker = GitHubLinkerService()

        with pytest.raises(ValueError, match="Invalid epic number"):
            linker.get_epic_details(0)

        with pytest.raises(ValueError, match="Invalid epic number"):
            linker.get_epic_details(-1)


class TestValidateEpicForLinking:
    """Tests for validate_epic_for_linking method."""

    @patch.object(GitHubLinkerService, 'get_epic_details')
    def test_validate_open_epic_with_label(self, mock_get_epic):
        """Test validating an open epic with epic label."""
        mock_get_epic.return_value = {
            "state": "open",
            "labels": ["epic", "priority:P1"]
        }

        linker = GitHubLinkerService()
        is_valid, error = linker.validate_epic_for_linking(123)

        assert is_valid is True
        assert error == ""

    @patch.object(GitHubLinkerService, 'get_epic_details')
    def test_validate_closed_epic(self, mock_get_epic):
        """Test validating a closed epic."""
        mock_get_epic.return_value = {
            "state": "closed",
            "labels": ["epic"]
        }

        linker = GitHubLinkerService()
        is_valid, error = linker.validate_epic_for_linking(123)

        assert is_valid is False
        assert "closed" in error

    @patch.object(GitHubLinkerService, 'get_epic_details')
    def test_validate_issue_without_epic_label(self, mock_get_epic):
        """Test validating an issue without epic label."""
        mock_get_epic.return_value = {
            "state": "open",
            "labels": ["bug", "priority:P1"]
        }

        linker = GitHubLinkerService()
        is_valid, error = linker.validate_epic_for_linking(123)

        assert is_valid is False
        assert "not labeled as an epic" in error

    @patch.object(GitHubLinkerService, 'get_epic_details')
    def test_validate_epic_api_error(self, mock_get_epic):
        """Test validation when API returns error."""
        mock_get_epic.side_effect = GitHubServiceError("API Error")

        linker = GitHubLinkerService()
        is_valid, error = linker.validate_epic_for_linking(123)

        assert is_valid is False
        assert "API Error" in error


class TestAddSpecToBody:
    """Tests for _add_spec_to_body method."""

    def test_add_spec_to_new_body(self):
        """Test adding spec to body without existing Specification section."""
        linker = GitHubLinkerService()
        body = "Epic description\n\nSome content here."

        new_body = linker._add_spec_to_body(body, "specs/001-test/spec.md")

        assert "## Specification" in new_body
        assert "- `specs/001-test/spec.md`" in new_body

    def test_add_spec_to_existing_section(self):
        """Test adding spec to body with existing Specification section."""
        linker = GitHubLinkerService()
        body = """Epic description

## Specification

- `specs/000-existing/spec.md`

## Other Section
Content here.
"""

        new_body = linker._add_spec_to_body(body, "specs/001-test/spec.md")

        assert "- `specs/000-existing/spec.md`" in new_body
        assert "- `specs/001-test/spec.md`" in new_body
        assert new_body.count("## Specification") == 1

    def test_add_duplicate_spec_skipped(self):
        """Test that duplicate spec is not added."""
        linker = GitHubLinkerService()
        body = """Epic description

## Specification

- `specs/001-test/spec.md`
"""

        new_body = linker._add_spec_to_body(body, "specs/001-test/spec.md")

        # Should not add duplicate
        assert new_body == body
        assert new_body.count("specs/001-test/spec.md") == 1


class TestRemoveSpecFromBody:
    """Tests for _remove_spec_from_body method."""

    def test_remove_spec_from_body(self):
        """Test removing spec from body."""
        linker = GitHubLinkerService()
        body = """Epic description

## Specification

- `specs/001-test/spec.md`
- `specs/002-other/spec.md`
"""

        new_body = linker._remove_spec_from_body(body, "specs/001-test/spec.md")

        assert "specs/001-test/spec.md" not in new_body
        assert "specs/002-other/spec.md" in new_body
        assert "## Specification" in new_body

    def test_remove_last_spec_removes_section(self):
        """Test that removing last spec removes the section."""
        linker = GitHubLinkerService()
        body = """Epic description

## Specification

- `specs/001-test/spec.md`

## Other Section
Content here.
"""

        new_body = linker._remove_spec_from_body(body, "specs/001-test/spec.md")

        assert "specs/001-test/spec.md" not in new_body
        assert "## Specification" not in new_body
        assert "## Other Section" in new_body


class TestGetRepoSlug:
    """Tests for _get_repo_slug method."""

    @patch('subprocess.run')
    def test_get_repo_slug_ssh(self, mock_run):
        """Test getting repo slug from SSH remote URL."""
        mock_result = Mock()
        mock_result.stdout = "git@github.com:owner/repo.git\n"
        mock_run.return_value = mock_result

        linker = GitHubLinkerService()
        slug = linker._get_repo_slug()

        assert slug == "owner/repo"

    @patch('subprocess.run')
    def test_get_repo_slug_https(self, mock_run):
        """Test getting repo slug from HTTPS remote URL."""
        mock_result = Mock()
        mock_result.stdout = "https://github.com/owner/repo.git\n"
        mock_run.return_value = mock_result

        linker = GitHubLinkerService()
        slug = linker._get_repo_slug()

        assert slug == "owner/repo"

    @patch('subprocess.run')
    def test_get_repo_slug_not_github(self, mock_run):
        """Test error when remote is not GitHub."""
        mock_result = Mock()
        mock_result.stdout = "https://gitlab.com/owner/repo.git\n"
        mock_run.return_value = mock_result

        linker = GitHubLinkerService()

        with pytest.raises(GitHubServiceError, match="Not a GitHub repository"):
            linker._get_repo_slug()

    @patch('subprocess.run')
    def test_get_repo_slug_no_remote(self, mock_run, mock_github_service):
        """Test error when no git remote found."""
        import subprocess
        mock_run.side_effect = subprocess.CalledProcessError(1, 'git')

        linker = GitHubLinkerService(github_service=mock_github_service)

        with pytest.raises(GitHubServiceError, match="Failed to get git remote"):
            linker._get_repo_slug()


class TestGetRelativePath:
    """Tests for _get_relative_path method."""

    @patch('subprocess.run')
    def test_get_relative_path_success(self, mock_run):
        """Test getting relative path from repo root."""
        mock_result = Mock()
        mock_result.stdout = "/home/user/repo\n"
        mock_run.return_value = mock_result

        linker = GitHubLinkerService()
        spec_path = Path("/home/user/repo/specs/001-test/spec.md")

        relative_path = linker._get_relative_path(spec_path)

        assert relative_path == "specs/001-test/spec.md"

    @patch('subprocess.run')
    def test_get_relative_path_fallback(self, mock_run, mock_github_service):
        """Test fallback when git command fails."""
        import subprocess
        mock_run.side_effect = subprocess.CalledProcessError(1, 'git')

        linker = GitHubLinkerService(github_service=mock_github_service)
        spec_path = Path("/home/user/repo/specs/001-test/spec.md")

        # Should return full path as fallback
        relative_path = linker._get_relative_path(spec_path)
        assert "spec.md" in relative_path


class TestLinkSpecToEpic:
    """Tests for link_spec_to_epic method."""

    @patch.object(GitHubLinkerService, 'validate_epic_for_linking', return_value=(True, ""))
    @patch.object(GitHubLinkerService, 'get_epic_details')
    @patch.object(GitHubLinkerService, 'update_epic_body')
    @patch.object(GitHubLinkerService, '_get_repo_slug', return_value='owner/repo')
    @patch('doit_cli.services.github_linker.add_epic_to_spec')
    @patch('doit_cli.services.github_linker.get_epic_reference', return_value=None)
    def test_link_spec_to_epic_success(
        self,
        mock_get_epic_ref,
        mock_add_epic,
        mock_repo_slug,
        mock_update_body,
        mock_get_epic,
        mock_validate,
        temp_spec_dir,
        sample_spec_content
    ):
        """Test successfully linking spec to epic."""
        # Create spec file
        spec_path = temp_spec_dir / "spec.md"
        spec_path.write_text(sample_spec_content)

        mock_get_epic.return_value = {"priority": "P1"}

        linker = GitHubLinkerService()
        result = linker.link_spec_to_epic(spec_path, epic_number=123)

        assert result is True
        mock_add_epic.assert_called_once()
        mock_update_body.assert_called_once()

    @patch.object(GitHubLinkerService, 'validate_epic_for_linking', return_value=(False, "Epic is closed"))
    def test_link_spec_to_closed_epic(self, mock_validate, temp_spec_dir, sample_spec_content):
        """Test linking to closed epic fails validation."""
        spec_path = temp_spec_dir / "spec.md"
        spec_path.write_text(sample_spec_content)

        linker = GitHubLinkerService()

        with pytest.raises(ValueError, match="Epic is closed"):
            linker.link_spec_to_epic(spec_path, epic_number=123)

    def test_link_nonexistent_spec(self, temp_spec_dir):
        """Test linking non-existent spec file."""
        spec_path = temp_spec_dir / "missing.md"

        linker = GitHubLinkerService()

        with pytest.raises(FileNotFoundError):
            linker.link_spec_to_epic(spec_path, epic_number=123)

    def test_link_invalid_epic_number(self, temp_spec_dir, sample_spec_content):
        """Test linking with invalid epic number."""
        spec_path = temp_spec_dir / "spec.md"
        spec_path.write_text(sample_spec_content)

        linker = GitHubLinkerService()

        with pytest.raises(ValueError, match="Invalid epic number"):
            linker.link_spec_to_epic(spec_path, epic_number=0)

    @patch('doit_cli.services.github_linker.get_epic_reference', return_value=(456, "url"))
    def test_link_spec_already_linked(self, mock_get_epic_ref, temp_spec_dir, sample_spec_content):
        """Test linking spec that's already linked to different epic."""
        spec_path = temp_spec_dir / "spec.md"
        spec_path.write_text(sample_spec_content)

        linker = GitHubLinkerService()
        result = linker.link_spec_to_epic(spec_path, epic_number=123, overwrite=False)

        assert result is False


class TestUnlinkSpecFromEpic:
    """Tests for unlink_spec_from_epic method."""

    @patch.object(GitHubLinkerService, 'get_epic_details')
    @patch.object(GitHubLinkerService, '_update_epic_via_cli')
    @patch('doit_cli.services.github_linker.remove_epic_reference')
    def test_unlink_success(
        self,
        mock_remove_epic,
        mock_update_cli,
        mock_get_epic,
        temp_spec_dir,
        sample_spec_content
    ):
        """Test successfully unlinking spec from epic."""
        spec_path = temp_spec_dir / "spec.md"
        spec_path.write_text(sample_spec_content)

        mock_get_epic.return_value = {
            "body": "## Specification\n\n- `specs/001-test/spec.md`\n"
        }

        linker = GitHubLinkerService()
        result = linker.unlink_spec_from_epic(spec_path, epic_number=123)

        assert result is True
        mock_remove_epic.assert_called_once()
        mock_update_cli.assert_called_once()

    def test_unlink_nonexistent_spec(self, temp_spec_dir):
        """Test unlinking non-existent spec file."""
        spec_path = temp_spec_dir / "missing.md"

        linker = GitHubLinkerService()

        with pytest.raises(FileNotFoundError):
            linker.unlink_spec_from_epic(spec_path, epic_number=123)
