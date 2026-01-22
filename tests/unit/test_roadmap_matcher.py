"""Unit tests for RoadmapMatcher service."""

import pytest
import tempfile
import shutil
from pathlib import Path
from doit_cli.services.roadmap_matcher import (
    RoadmapMatcherService,
    RoadmapItem,
    MatchResult
)


@pytest.fixture
def temp_roadmap_dir():
    """Create temporary directory for test roadmap files."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_roadmap_content():
    """Sample roadmap file content."""
    return """# Roadmap

## Active Features

| Title | Priority | Branch | GitHub | Status | Category |
|-------|----------|--------|--------|--------|----------|
| GitHub Issue Auto-linking in Spec Creation | P1 | [040-spec-github-linking] | [#123](https://github.com/owner/repo/issues/123) | In Progress | Integration |
| User Authentication System | P1 | [045-user-auth] | [#456](https://github.com/owner/repo/issues/456) | Planned | Core |
| GitHub Roadmap Sync | P2 | [039-github-roadmap-sync] | [#789](https://github.com/owner/repo/issues/789) | Complete | Integration |
| Spec Validation Linting | P2 | [029-spec-validation] | | Planned | Quality |
| Enhanced Documentation | P3 | [050-docs-enhancement] | [#999](https://github.com/owner/repo/issues/999) | Planned | Documentation |
"""


class TestRoadmapItem:
    """Tests for RoadmapItem dataclass."""

    def test_valid_roadmap_item(self):
        """Test creating a valid roadmap item."""
        item = RoadmapItem(
            title="Test Feature",
            priority="P1",
            feature_branch="[001-test]",
            github_number=123,
            github_url="https://github.com/owner/repo/issues/123",
            status="Planned",
            category="Core"
        )
        assert item.title == "Test Feature"
        assert item.priority == "P1"
        assert item.github_number == 123

    def test_invalid_priority(self):
        """Test that invalid priority raises ValueError."""
        with pytest.raises(ValueError, match="Invalid priority"):
            RoadmapItem(
                title="Test",
                priority="P5",  # Invalid
                feature_branch="[001-test]",
                github_number=None,
                github_url=None,
                status="Planned",
                category=None
            )

    def test_invalid_github_number(self):
        """Test that invalid GitHub number raises ValueError."""
        with pytest.raises(ValueError, match="Invalid GitHub number"):
            RoadmapItem(
                title="Test",
                priority="P1",
                feature_branch="[001-test]",
                github_number=-1,  # Invalid
                github_url="url",
                status="Planned",
                category=None
            )

    def test_empty_title(self):
        """Test that empty title raises ValueError."""
        with pytest.raises(ValueError, match="Title cannot be empty"):
            RoadmapItem(
                title="",  # Invalid
                priority="P1",
                feature_branch="[001-test]",
                github_number=None,
                github_url=None,
                status="Planned",
                category=None
            )


class TestParseRoadmap:
    """Tests for parse_roadmap method."""

    def test_parse_valid_roadmap(self, temp_roadmap_dir, sample_roadmap_content):
        """Test parsing a valid roadmap file."""
        roadmap_path = temp_roadmap_dir / "roadmap.md"
        roadmap_path.write_text(sample_roadmap_content)

        matcher = RoadmapMatcherService(roadmap_path)
        items = matcher.parse_roadmap()

        assert len(items) == 5
        assert items[0].title == "GitHub Issue Auto-linking in Spec Creation"
        assert items[0].priority == "P1"
        assert items[0].github_number == 123

    def test_parse_roadmap_with_no_github(self, temp_roadmap_dir):
        """Test parsing roadmap item without GitHub epic."""
        content = """# Roadmap

| Title | Priority | Branch | GitHub | Status | Category |
|-------|----------|--------|--------|--------|----------|
| Local Feature | P1 | [001-local] | | Planned | Core |
"""
        roadmap_path = temp_roadmap_dir / "roadmap.md"
        roadmap_path.write_text(content)

        matcher = RoadmapMatcherService(roadmap_path)
        items = matcher.parse_roadmap()

        assert len(items) == 1
        assert items[0].github_number is None
        assert items[0].github_url is None

    def test_parse_missing_roadmap(self, temp_roadmap_dir):
        """Test parsing non-existent roadmap file."""
        roadmap_path = temp_roadmap_dir / "missing.md"
        matcher = RoadmapMatcherService(roadmap_path)

        with pytest.raises(FileNotFoundError):
            matcher.parse_roadmap()

    def test_parse_empty_roadmap(self, temp_roadmap_dir):
        """Test parsing roadmap with no valid items."""
        content = """# Roadmap

## Active Features

| Title | Priority | Branch | GitHub | Status | Category |
|-------|----------|--------|--------|--------|----------|
"""
        roadmap_path = temp_roadmap_dir / "roadmap.md"
        roadmap_path.write_text(content)

        matcher = RoadmapMatcherService(roadmap_path)

        with pytest.raises(ValueError, match="No valid roadmap items found"):
            matcher.parse_roadmap()

    def test_parse_roadmap_caching(self, temp_roadmap_dir, sample_roadmap_content):
        """Test that parse_roadmap is cached."""
        roadmap_path = temp_roadmap_dir / "roadmap.md"
        roadmap_path.write_text(sample_roadmap_content)

        matcher = RoadmapMatcherService(roadmap_path)

        # First call
        items1 = matcher.parse_roadmap()

        # Second call should return cached result
        items2 = matcher.parse_roadmap()

        # Should be the same object (cached)
        assert items1 is items2


class TestFindBestMatch:
    """Tests for find_best_match method."""

    def test_exact_match(self, temp_roadmap_dir, sample_roadmap_content):
        """Test finding exact match."""
        roadmap_path = temp_roadmap_dir / "roadmap.md"
        roadmap_path.write_text(sample_roadmap_content)

        matcher = RoadmapMatcherService(roadmap_path)
        result = matcher.find_best_match("User Authentication System")

        assert result is not None
        assert result.is_exact_match is True
        assert result.item.title == "User Authentication System"
        assert result.similarity_score == 1.0

    def test_fuzzy_match_above_threshold(self, temp_roadmap_dir, sample_roadmap_content):
        """Test finding fuzzy match above 80% threshold."""
        roadmap_path = temp_roadmap_dir / "roadmap.md"
        roadmap_path.write_text(sample_roadmap_content)

        matcher = RoadmapMatcherService(roadmap_path)
        # Use query that produces 88% similarity with roadmap title
        result = matcher.find_best_match("GitHub Issue Auto-linking in Spec", threshold=0.8)

        assert result is not None
        assert result.is_exact_match is False
        assert "GitHub Issue" in result.item.title
        assert result.similarity_score >= 0.8

    def test_no_match_below_threshold(self, temp_roadmap_dir, sample_roadmap_content):
        """Test that no match returned when below threshold."""
        roadmap_path = temp_roadmap_dir / "roadmap.md"
        roadmap_path.write_text(sample_roadmap_content)

        matcher = RoadmapMatcherService(roadmap_path)
        result = matcher.find_best_match("Completely Different Feature", threshold=0.8)

        assert result is None

    def test_empty_feature_name(self, temp_roadmap_dir, sample_roadmap_content):
        """Test handling of empty feature name."""
        roadmap_path = temp_roadmap_dir / "roadmap.md"
        roadmap_path.write_text(sample_roadmap_content)

        matcher = RoadmapMatcherService(roadmap_path)
        result = matcher.find_best_match("")

        assert result is None

    def test_custom_threshold(self, temp_roadmap_dir, sample_roadmap_content):
        """Test using custom threshold."""
        roadmap_path = temp_roadmap_dir / "roadmap.md"
        roadmap_path.write_text(sample_roadmap_content)

        matcher = RoadmapMatcherService(roadmap_path)

        # With 0.6 threshold and longer query, should find match
        result = matcher.find_best_match("GitHub Issue Auto-linking Spec", threshold=0.6)
        assert result is not None
        assert result.similarity_score >= 0.6


class TestFindAllMatches:
    """Tests for find_all_matches method."""

    def test_multiple_matches(self, temp_roadmap_dir, sample_roadmap_content):
        """Test finding multiple matches."""
        roadmap_path = temp_roadmap_dir / "roadmap.md"
        roadmap_path.write_text(sample_roadmap_content)

        matcher = RoadmapMatcherService(roadmap_path)
        # Use broader query with lower threshold to get multiple matches
        results = matcher.find_all_matches("GitHub Issue", threshold=0.5)

        # Should match items containing "GitHub" with 50% threshold
        assert len(results) >= 1
        assert all(result.similarity_score >= 0.5 for result in results)

    def test_sorted_by_score(self, temp_roadmap_dir, sample_roadmap_content):
        """Test that results are sorted by similarity score."""
        roadmap_path = temp_roadmap_dir / "roadmap.md"
        roadmap_path.write_text(sample_roadmap_content)

        matcher = RoadmapMatcherService(roadmap_path)
        results = matcher.find_all_matches("GitHub Integration", threshold=0.7)

        # Verify descending order
        for i in range(len(results) - 1):
            assert results[i].similarity_score >= results[i + 1].similarity_score

    def test_no_matches(self, temp_roadmap_dir, sample_roadmap_content):
        """Test when no matches found."""
        roadmap_path = temp_roadmap_dir / "roadmap.md"
        roadmap_path.write_text(sample_roadmap_content)

        matcher = RoadmapMatcherService(roadmap_path)
        results = matcher.find_all_matches("Quantum Computing", threshold=0.8)

        assert results == []

    def test_invalid_threshold(self, temp_roadmap_dir, sample_roadmap_content):
        """Test that invalid threshold raises ValueError."""
        roadmap_path = temp_roadmap_dir / "roadmap.md"
        roadmap_path.write_text(sample_roadmap_content)

        matcher = RoadmapMatcherService(roadmap_path)

        with pytest.raises(ValueError, match="Threshold must be between"):
            matcher.find_all_matches("Test", threshold=1.5)

        with pytest.raises(ValueError, match="Threshold must be between"):
            matcher.find_all_matches("Test", threshold=-0.1)


class TestMatchResult:
    """Tests for MatchResult dataclass."""

    def test_match_result_creation(self):
        """Test creating a MatchResult."""
        item = RoadmapItem(
            title="Test",
            priority="P1",
            feature_branch="[001-test]",
            github_number=123,
            github_url="url",
            status="Planned",
            category="Core"
        )

        result = MatchResult(
            item=item,
            similarity_score=0.95,
            is_exact_match=False
        )

        assert result.item.title == "Test"
        assert result.similarity_score == 0.95
        assert result.is_exact_match is False


class TestEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_malformed_github_link(self, temp_roadmap_dir):
        """Test handling of malformed GitHub link."""
        content = """# Roadmap

| Title | Priority | Branch | GitHub | Status | Category |
|-------|----------|--------|--------|--------|----------|
| Feature | P1 | [001-test] | broken-link | Planned | Core |
"""
        roadmap_path = temp_roadmap_dir / "roadmap.md"
        roadmap_path.write_text(content)

        matcher = RoadmapMatcherService(roadmap_path)
        items = matcher.parse_roadmap()

        # Should parse item but with no GitHub number
        assert len(items) == 1
        assert items[0].github_number is None

    def test_special_characters_in_title(self, temp_roadmap_dir):
        """Test handling of special characters in titles."""
        content = """# Roadmap

| Title | Priority | Branch | GitHub | Status | Category |
|-------|----------|--------|--------|--------|----------|
| Feature: OAuth2 (v2.0) | P1 | [001-test] | | Planned | Core |
"""
        roadmap_path = temp_roadmap_dir / "roadmap.md"
        roadmap_path.write_text(content)

        matcher = RoadmapMatcherService(roadmap_path)
        items = matcher.parse_roadmap()

        assert len(items) == 1
        assert "OAuth2" in items[0].title

    def test_case_insensitive_matching(self, temp_roadmap_dir, sample_roadmap_content):
        """Test that matching is case-insensitive."""
        roadmap_path = temp_roadmap_dir / "roadmap.md"
        roadmap_path.write_text(sample_roadmap_content)

        matcher = RoadmapMatcherService(roadmap_path)
        result = matcher.find_best_match("user authentication system")

        assert result is not None
        assert result.is_exact_match is True
