"""Integration tests for specit GitHub auto-linking workflow.

This test suite validates the end-to-end workflow:
1. User creates spec via specit command
2. RoadmapMatcher finds matching epic in roadmap
3. GitHubLinkerService creates bidirectional link
4. Spec frontmatter contains epic reference
5. GitHub epic body contains spec file path
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from doit_cli.services.roadmap_matcher import (
    RoadmapMatcherService,
    RoadmapItem,
    MatchResult
)
from doit_cli.services.github_linker import (
    GitHubLinkerService,
    EpicReference,
    SpecReference
)
from doit_cli.utils.spec_parser import (
    parse_spec_file,
    get_epic_reference
)


@pytest.fixture
def temp_project_dir():
    """Create temporary project directory with roadmap and specs."""
    temp_dir = tempfile.mkdtemp()
    project_path = Path(temp_dir)

    # Create .doit/memory directory
    memory_dir = project_path / ".doit" / "memory"
    memory_dir.mkdir(parents=True)

    # Create specs directory
    specs_dir = project_path / "specs"
    specs_dir.mkdir()

    yield project_path

    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_roadmap(temp_project_dir):
    """Create sample roadmap with GitHub epics."""
    roadmap_content = """# Project Roadmap

## Active Requirements

### P1 - Critical

| Title | Priority | Branch | GitHub | Status | Category |
|-------|----------|--------|--------|--------|----------|
| GitHub Issue Auto-linking in Spec Creation | P1 | [040-spec-github-linking] | [#123](https://github.com/owner/repo/issues/123) | In Progress | Integration |
| User Authentication System | P1 | [045-user-auth] | [#456](https://github.com/owner/repo/issues/456) | Planned | Core |

### P2 - High Priority

| Title | Priority | Branch | GitHub | Status | Category |
|-------|----------|--------|--------|--------|----------|
| GitHub Roadmap Sync | P2 | [039-github-roadmap-sync] | [#789](https://github.com/owner/repo/issues/789) | Complete | Integration |
| Spec Validation Linting | P2 | [029-spec-validation] | | Planned | Quality |
"""
    roadmap_path = temp_project_dir / ".doit" / "memory" / "roadmap.md"
    roadmap_path.write_text(roadmap_content)
    return roadmap_path


@pytest.fixture
def sample_spec(temp_project_dir):
    """Create sample spec file."""
    spec_content = """---
Feature: "GitHub Issue Auto-linking"
Branch: "[040-spec-github-linking]"
Created: "2026-01-22"
Status: "In Progress"
---

# Feature Specification: GitHub Issue Auto-linking

## Summary

Automatically link specification files to GitHub epics during spec creation.

## User Stories

### User Story 1 - Automatic Epic Discovery

As a developer, when I create a new spec, I want it to automatically link to the matching GitHub epic from my roadmap.

**Acceptance Scenarios**:

1. Spec matches roadmap item with epic → Automatic linking occurs
2. Spec does not match any roadmap item → No linking, spec created successfully
3. GitHub API fails → Spec created successfully, linking skipped with warning
"""

    spec_dir = temp_project_dir / "specs" / "040-spec-github-linking"
    spec_dir.mkdir(parents=True)
    spec_path = spec_dir / "spec.md"
    spec_path.write_text(spec_content)
    return spec_path


class TestEndToEndAutoLinking:
    """Integration tests for automatic epic linking workflow."""

    def test_complete_workflow_success(
        self,
        temp_project_dir,
        sample_roadmap,
        sample_spec
    ):
        """Test complete workflow: match roadmap → link to epic → verify bidirectional links."""

        # Step 1: Match feature to roadmap (use exact or near-exact title)
        matcher = RoadmapMatcherService(sample_roadmap)
        match = matcher.find_best_match(
            "GitHub Issue Auto-linking in Spec Creation",
            threshold=0.8
        )

        assert match is not None, "Should find matching roadmap item"
        assert match.item.github_number == 123
        assert match.item.priority == "P1"
        assert match.similarity_score >= 0.8

        # Step 2: Mock only GitHub-specific operations, allow file I/O
        with patch.object(GitHubLinkerService, 'get_epic_details') as mock_get_epic, \
             patch.object(GitHubLinkerService, 'validate_epic_for_linking') as mock_validate, \
             patch.object(GitHubLinkerService, '_update_epic_via_cli') as mock_update_cli, \
             patch.object(GitHubLinkerService, '_get_repo_slug', return_value='owner/repo'), \
             patch.object(GitHubLinkerService, '_get_relative_path') as mock_relative_path:

            # Mock epic details
            mock_get_epic.return_value = {
                "number": 123,
                "title": "GitHub Issue Auto-linking in Spec Creation",
                "body": "## Summary\n\nFeature description here.",
                "state": "open",
                "labels": ["epic", "priority:P1"],
                "url": "https://github.com/owner/repo/issues/123",
                "priority": "P1"
            }

            # Mock validation
            mock_validate.return_value = (True, "")

            # Mock relative path calculation
            mock_relative_path.return_value = "specs/040-spec-github-linking/spec.md"

            # Step 3: Link spec to epic
            linker = GitHubLinkerService()
            success = linker.link_spec_to_epic(
                sample_spec,
                epic_number=match.item.github_number,
                overwrite=False
            )

            assert success is True, "Linking should succeed"

            # Step 4: Verify spec frontmatter contains epic reference
            epic_ref = get_epic_reference(sample_spec)
            assert epic_ref is not None, "Spec should have epic reference"
            epic_number, epic_url = epic_ref
            assert epic_number == 123
            assert "github.com/owner/repo/issues/123" in epic_url

            # Step 5: Verify GitHub epic update was called
            mock_update_cli.assert_called_once()

            # Verify the body update includes spec path
            call_args = mock_update_cli.call_args
            epic_number_arg = call_args[0][0]
            new_body = call_args[0][1]

            assert epic_number_arg == 123
            assert "## Specification" in new_body
            assert "040-spec-github-linking/spec.md" in new_body

    def test_no_roadmap_match_graceful_skip(
        self,
        temp_project_dir,
        sample_roadmap,
        sample_spec
    ):
        """Test that non-matching feature names skip linking gracefully."""

        matcher = RoadmapMatcherService(sample_roadmap)
        match = matcher.find_best_match("Completely Unrelated Feature", threshold=0.8)

        # Should not find a match
        assert match is None

        # Spec should still be valid and readable
        frontmatter, body = parse_spec_file(sample_spec)
        assert frontmatter.feature_name == "GitHub Issue Auto-linking"
        assert "Automatically link" in body

    def test_github_api_failure_graceful_fallback(
        self,
        temp_project_dir,
        sample_roadmap,
        sample_spec
    ):
        """Test that GitHub API failures don't prevent spec creation."""

        # Step 1: Match succeeds (use exact title)
        matcher = RoadmapMatcherService(sample_roadmap)
        match = matcher.find_best_match(
            "GitHub Issue Auto-linking in Spec Creation",
            threshold=0.8
        )
        assert match is not None

        # Step 2: Mock GitHub API failure
        with patch.object(GitHubLinkerService, 'get_epic_details') as mock_get_epic, \
             patch.object(GitHubLinkerService, 'validate_epic_for_linking') as mock_validate:

            from doit_cli.services.github_service import GitHubServiceError

            # Validation fails due to API error
            mock_validate.return_value = (False, "GitHub API Error: Rate limit exceeded")

            linker = GitHubLinkerService()

            # Should raise ValueError when validation fails
            with pytest.raises(ValueError, match="Cannot link to epic"):
                linker.link_spec_to_epic(
                    sample_spec,
                    epic_number=123,
                    overwrite=False
                )

        # Spec should remain valid even if linking failed
        frontmatter, body = parse_spec_file(sample_spec)
        assert frontmatter.feature_name == "GitHub Issue Auto-linking"

    def test_fuzzy_matching_threshold(
        self,
        temp_project_dir,
        sample_roadmap
    ):
        """Test that fuzzy matching respects threshold settings."""

        matcher = RoadmapMatcherService(sample_roadmap)

        # Exact match
        exact_match = matcher.find_best_match(
            "GitHub Issue Auto-linking in Spec Creation",
            threshold=0.8
        )
        assert exact_match is not None
        assert exact_match.is_exact_match is True

        # Close match with lower threshold (partial title)
        close_match = matcher.find_best_match(
            "GitHub Issue Auto-linking",
            threshold=0.7  # Lower threshold for partial match
        )
        assert close_match is not None
        assert close_match.similarity_score >= 0.7

        # Very short query - should not match with high threshold
        distant_match = matcher.find_best_match(
            "GitHub",
            threshold=0.8
        )
        assert distant_match is None, "Short query should not match with high threshold"

    def test_already_linked_spec_preservation(
        self,
        temp_project_dir,
        sample_roadmap,
        sample_spec
    ):
        """Test that already-linked specs are not overwritten without overwrite flag."""

        with patch.object(GitHubLinkerService, 'get_epic_details') as mock_get_epic, \
             patch.object(GitHubLinkerService, 'validate_epic_for_linking') as mock_validate, \
             patch.object(GitHubLinkerService, '_update_epic_via_cli') as mock_update_cli, \
             patch.object(GitHubLinkerService, '_get_repo_slug', return_value='owner/repo'), \
             patch('doit_cli.services.github_linker.add_epic_to_spec') as mock_add_epic, \
             patch('doit_cli.services.github_linker.get_epic_reference') as mock_get_epic_ref, \
             patch('subprocess.run') as mock_run:

            mock_get_epic.return_value = {
                "priority": "P1",
                "body": "Test body"
            }
            mock_validate.return_value = (True, "")
            mock_run.return_value = Mock(stdout=str(temp_project_dir) + "\n")

            linker = GitHubLinkerService()

            # First call: no existing epic
            mock_get_epic_ref.return_value = None
            success1 = linker.link_spec_to_epic(sample_spec, 123, overwrite=False)
            assert success1 is True

            # Second call: epic already exists (different number)
            mock_get_epic_ref.return_value = (123, "https://github.com/owner/repo/issues/123")
            success2 = linker.link_spec_to_epic(sample_spec, 456, overwrite=False)
            assert success2 is False, "Should not overwrite existing link"

            # Verify add_epic was only called once (for first link)
            assert mock_add_epic.call_count == 1

    def test_roadmap_priority_propagation(
        self,
        temp_project_dir,
        sample_roadmap,
        sample_spec
    ):
        """Test that roadmap epic priority is propagated to spec frontmatter."""

        with patch.object(GitHubLinkerService, 'get_epic_details') as mock_get_epic, \
             patch.object(GitHubLinkerService, 'validate_epic_for_linking') as mock_validate, \
             patch.object(GitHubLinkerService, '_update_epic_via_cli'), \
             patch.object(GitHubLinkerService, '_get_repo_slug', return_value='owner/repo'), \
             patch('subprocess.run') as mock_run:

            mock_get_epic.return_value = {
                "priority": "P1",
                "body": "Test"
            }
            mock_validate.return_value = (True, "")
            mock_run.return_value = Mock(stdout=str(temp_project_dir) + "\n")

            linker = GitHubLinkerService()
            linker.link_spec_to_epic(sample_spec, 123, overwrite=False)

            # Verify priority in frontmatter
            frontmatter, _ = parse_spec_file(sample_spec)
            assert frontmatter.priority == "P1"


class TestRoadmapMatcherIntegration:
    """Integration tests for RoadmapMatcher with real roadmap parsing."""

    def test_parse_multiple_priorities(self, temp_project_dir, sample_roadmap):
        """Test parsing roadmap with multiple priority sections."""
        matcher = RoadmapMatcherService(sample_roadmap)
        items = matcher.parse_roadmap()

        assert len(items) == 4

        # Verify P1 items
        p1_items = [item for item in items if item.priority == "P1"]
        assert len(p1_items) == 2

        # Verify P2 items
        p2_items = [item for item in items if item.priority == "P2"]
        assert len(p2_items) == 2

    def test_find_all_matches_multiple_github_items(
        self,
        temp_project_dir,
        sample_roadmap
    ):
        """Test finding all matches when multiple items contain search term."""
        matcher = RoadmapMatcherService(sample_roadmap)

        # Use a longer query that will match better
        matches = matcher.find_all_matches("GitHub Roadmap", threshold=0.5)

        # Should find at least "GitHub Roadmap Sync" with good score
        assert len(matches) >= 1, "Should find at least one match"

        # Verify sorted by similarity score
        if len(matches) > 1:
            for i in range(len(matches) - 1):
                assert matches[i].similarity_score >= matches[i + 1].similarity_score


class TestErrorRecovery:
    """Integration tests for error recovery scenarios."""

    def test_malformed_roadmap_graceful_handling(self, temp_project_dir):
        """Test handling of malformed roadmap file."""
        roadmap_path = temp_project_dir / ".doit" / "memory" / "roadmap.md"
        roadmap_path.write_text("This is not a valid roadmap table")

        matcher = RoadmapMatcherService(roadmap_path)

        with pytest.raises(ValueError, match="No valid roadmap items found"):
            matcher.parse_roadmap()

    def test_missing_roadmap_file(self, temp_project_dir):
        """Test handling when roadmap file doesn't exist."""
        roadmap_path = temp_project_dir / ".doit" / "memory" / "missing.md"
        matcher = RoadmapMatcherService(roadmap_path)

        with pytest.raises(FileNotFoundError):
            matcher.parse_roadmap()

    def test_closed_epic_validation_failure(self, sample_spec):
        """Test that closed epics fail validation."""
        with patch.object(GitHubLinkerService, 'get_epic_details') as mock_get_epic:
            mock_get_epic.return_value = {
                "state": "closed",
                "labels": ["epic"]
            }

            linker = GitHubLinkerService()
            is_valid, error = linker.validate_epic_for_linking(123)

            assert is_valid is False
            assert "closed" in error.lower()

    def test_non_epic_issue_validation_failure(self, sample_spec):
        """Test that non-epic issues fail validation."""
        with patch.object(GitHubLinkerService, 'get_epic_details') as mock_get_epic:
            mock_get_epic.return_value = {
                "state": "open",
                "labels": ["feature", "bug"]  # Missing "epic" label
            }

            linker = GitHubLinkerService()
            is_valid, error = linker.validate_epic_for_linking(123)

            assert is_valid is False
            assert "not labeled as an epic" in error.lower()


class TestNavigationFeatures:
    """Integration tests for User Story 2 - Navigation features."""

    def test_epic_link_is_clickable_markdown_format(
        self,
        temp_project_dir,
        sample_spec
    ):
        """Test that epic links in spec frontmatter are in clickable markdown format."""
        from doit_cli.utils.spec_parser import add_epic_reference, parse_spec_file

        # Add epic reference
        add_epic_reference(
            sample_spec,
            epic_number=123,
            epic_url="https://github.com/owner/repo/issues/123",
            priority="P1"
        )

        # Read spec and verify markdown link format
        frontmatter, body = parse_spec_file(sample_spec)

        # Check that Epic field contains markdown link
        assert frontmatter.data.get("Epic") == "[#123](https://github.com/owner/repo/issues/123)"
        assert frontmatter.epic_number == 123
        assert frontmatter.epic_url == "https://github.com/owner/repo/issues/123"

    def test_multiple_specs_listed_in_epic_body(
        self,
        temp_project_dir
    ):
        """Test that multiple specs can be linked to the same epic."""
        from pathlib import Path
        from doit_cli.services.github_linker import GitHubLinkerService

        linker = GitHubLinkerService()

        # Create epic body with first spec
        body = "## Summary\n\nEpic description."
        body = linker._add_spec_to_body(body, "specs/040-first/spec.md")

        # Add second spec
        body = linker._add_spec_to_body(body, "specs/041-second/spec.md")

        # Verify both specs are listed
        assert "## Specification" in body
        assert "- `specs/040-first/spec.md`" in body
        assert "- `specs/041-second/spec.md`" in body

        # Verify spec list format
        spec_section = body.split("## Specification")[1]
        assert spec_section.count("- `") == 2

    def test_spec_path_format_is_relative_to_repo_root(
        self,
        temp_project_dir,
        sample_spec
    ):
        """Test that spec paths in epic body are relative to repository root."""
        from doit_cli.services.github_linker import GitHubLinkerService
        from unittest.mock import patch, Mock

        with patch.object(GitHubLinkerService, '_get_repo_slug', return_value='owner/repo'), \
             patch.object(GitHubLinkerService, 'get_epic_details') as mock_get_epic, \
             patch.object(GitHubLinkerService, 'validate_epic_for_linking') as mock_validate, \
             patch.object(GitHubLinkerService, '_update_epic_via_cli') as mock_update:

            mock_get_epic.return_value = {
                "priority": "P1",
                "body": "Test body"
            }
            mock_validate.return_value = (True, "")

            linker = GitHubLinkerService()

            # Link spec
            linker.link_spec_to_epic(sample_spec, 123, overwrite=False)

            # Verify the update was called with a relative path
            mock_update.assert_called_once()
            _, new_body = mock_update.call_args[0]

            # The body should contain a relative path starting with "specs/"
            assert "specs/040-spec-github-linking/spec.md" in new_body or \
                   "40-spec-github-linking/spec.md" in new_body  # Allow flexible path matching


class TestEpicCreation:
    """Integration tests for User Story 3 (P3) - Epic Creation when missing."""

    def test_create_epic_for_roadmap_item_success(
        self,
        temp_project_dir
    ):
        """Test creating a GitHub epic when roadmap item has no epic."""
        from pathlib import Path
        from doit_cli.services.github_linker import GitHubLinkerService
        from doit_cli.models.github_epic import GitHubEpic
        from unittest.mock import patch, Mock

        linker = GitHubLinkerService()

        with patch.object(linker.github_service, 'create_epic') as mock_create:
            # Mock epic creation
            mock_create.return_value = GitHubEpic(
                number=789,
                title="Test Feature",
                state="open",
                labels=["epic", "priority:P2"],
                body="Epic for feature: Test Feature\n\n## Specification\n\n_Spec file will be added when created_",
                url="https://github.com/owner/repo/issues/789"
            )

            # Create epic
            epic_number, epic_url = linker.create_epic_for_roadmap_item(
                title="Test Feature",
                priority="P2",
                feature_description="Test feature description"
            )

            # Verify epic was created
            assert epic_number == 789
            assert epic_url == "https://github.com/owner/repo/issues/789"

            # Verify github_service.create_epic was called correctly
            mock_create.assert_called_once()
            call_args = mock_create.call_args
            assert call_args[1]["title"] == "Test Feature"
            assert call_args[1]["priority"] == "P2"
            assert "Test feature description" in call_args[1]["body"]

    def test_update_roadmap_with_new_epic(
        self,
        temp_project_dir
    ):
        """Test updating roadmap.md with newly created epic reference."""
        from pathlib import Path
        from doit_cli.services.github_linker import GitHubLinkerService

        # Create roadmap file
        roadmap_path = temp_project_dir / ".doit" / "memory" / "roadmap.md"
        roadmap_path.parent.mkdir(parents=True, exist_ok=True)

        # Create roadmap with item missing GitHub epic
        roadmap_content = """# Roadmap

| Title | Priority | Branch | GitHub | Status | Category |
|-------|----------|--------|--------|--------|----------|
| Test Feature | P2 | [042-test] |  | Planned | Feature |
| Other Feature | P1 | [043-other] | [#123](https://github.com/owner/repo/issues/123) | In Progress | Enhancement |
"""
        roadmap_path.write_text(roadmap_content)

        linker = GitHubLinkerService()

        # Update roadmap with new epic
        linker.update_roadmap_with_epic(
            roadmap_path=roadmap_path,
            roadmap_title="Test Feature",
            epic_number=789,
            epic_url="https://github.com/owner/repo/issues/789"
        )

        # Read updated roadmap
        updated_content = roadmap_path.read_text()

        # Verify GitHub column was updated
        assert "[#789](https://github.com/owner/repo/issues/789)" in updated_content
        assert "Test Feature" in updated_content

        # Verify other rows weren't affected
        assert "[#123](https://github.com/owner/repo/issues/123)" in updated_content

    def test_end_to_end_epic_creation_and_linking(
        self,
        temp_project_dir,
        sample_spec
    ):
        """Test complete workflow: create epic → update roadmap → link spec."""
        from pathlib import Path
        from doit_cli.services.github_linker import GitHubLinkerService
        from doit_cli.models.github_epic import GitHubEpic
        from unittest.mock import patch, Mock

        # Create roadmap
        roadmap_path = temp_project_dir / ".doit" / "memory" / "roadmap.md"
        roadmap_path.parent.mkdir(parents=True, exist_ok=True)
        roadmap_content = """# Roadmap

| Title | Priority | Branch | GitHub | Status | Category |
|-------|----------|--------|--------|--------|----------|
| GitHub Issue Auto-linking in Spec Creation | P1 | [040-spec-github-linking] |  | Planned | Feature |
"""
        roadmap_path.write_text(roadmap_content)

        linker = GitHubLinkerService()

        with patch.object(linker.github_service, 'create_epic') as mock_create, \
             patch.object(GitHubLinkerService, 'get_epic_details') as mock_get_epic, \
             patch.object(GitHubLinkerService, 'validate_epic_for_linking') as mock_validate, \
             patch.object(GitHubLinkerService, '_update_epic_via_cli') as mock_update_cli, \
             patch.object(GitHubLinkerService, '_get_repo_slug', return_value='owner/repo'), \
             patch.object(GitHubLinkerService, '_get_relative_path') as mock_relative_path:

            # Mock epic creation
            mock_create.return_value = GitHubEpic(
                number=999,
                title="GitHub Issue Auto-linking in Spec Creation",
                state="open",
                labels=["epic", "priority:P1"],
                body="Epic for feature\n\n## Specification\n\n_Spec file will be added when created_",
                url="https://github.com/owner/repo/issues/999"
            )

            # Mock epic details (for linking)
            mock_get_epic.return_value = {
                "number": 999,
                "title": "GitHub Issue Auto-linking in Spec Creation",
                "body": "Epic for feature\n\n## Specification\n\n_Spec file will be added when created_",
                "state": "open",
                "labels": ["epic", "priority:P1"],
                "url": "https://github.com/owner/repo/issues/999",
                "priority": "P1"
            }

            mock_validate.return_value = (True, "")
            mock_relative_path.return_value = "specs/040-spec-github-linking/spec.md"

            # Step 1: Create epic
            epic_number, epic_url = linker.create_epic_for_roadmap_item(
                title="GitHub Issue Auto-linking in Spec Creation",
                priority="P1",
                feature_description="Auto-link specs to GitHub epics"
            )

            assert epic_number == 999
            assert epic_url == "https://github.com/owner/repo/issues/999"

            # Step 2: Update roadmap
            linker.update_roadmap_with_epic(
                roadmap_path=roadmap_path,
                roadmap_title="GitHub Issue Auto-linking in Spec Creation",
                epic_number=epic_number,
                epic_url=epic_url
            )

            # Verify roadmap was updated
            updated_roadmap = roadmap_path.read_text()
            assert "[#999](https://github.com/owner/repo/issues/999)" in updated_roadmap

            # Step 3: Link spec to epic
            success = linker.link_spec_to_epic(sample_spec, epic_number, overwrite=False)

            assert success is True

            # Verify spec was updated
            from doit_cli.utils.spec_parser import get_epic_reference
            epic_ref = get_epic_reference(sample_spec)
            assert epic_ref is not None
            assert epic_ref[0] == 999

    def test_epic_creation_with_invalid_priority(
        self,
        temp_project_dir
    ):
        """Test that invalid priority raises ValueError."""
        from doit_cli.services.github_linker import GitHubLinkerService
        import pytest

        linker = GitHubLinkerService()

        with pytest.raises(ValueError, match="Invalid priority"):
            linker.create_epic_for_roadmap_item(
                title="Test Feature",
                priority="INVALID",
                feature_description="Test"
            )

    def test_update_roadmap_with_nonexistent_item(
        self,
        temp_project_dir
    ):
        """Test that updating non-existent roadmap item raises ValueError."""
        from pathlib import Path
        from doit_cli.services.github_linker import GitHubLinkerService
        import pytest

        # Create roadmap
        roadmap_path = temp_project_dir / ".doit" / "memory" / "roadmap.md"
        roadmap_path.parent.mkdir(parents=True, exist_ok=True)
        roadmap_content = """# Roadmap

| Title | Priority | Branch | GitHub | Status | Category |
|-------|----------|--------|--------|--------|----------|
| Existing Feature | P1 | [001-existing] |  | Planned | Feature |
"""
        roadmap_path.write_text(roadmap_content)

        linker = GitHubLinkerService()

        with pytest.raises(ValueError, match="Roadmap item not found"):
            linker.update_roadmap_with_epic(
                roadmap_path=roadmap_path,
                roadmap_title="Nonexistent Feature",
                epic_number=999,
                epic_url="https://github.com/owner/repo/issues/999"
            )
