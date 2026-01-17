"""Unit tests for memory search service."""

import tempfile
from pathlib import Path

import pytest

from doit_cli.models.search_models import (
    QueryType,
    SearchQuery,
    SourceFilter,
)
from doit_cli.services.memory_search import MemorySearchService


@pytest.fixture
def temp_project():
    """Create a temporary project structure for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)

        # Create .doit/memory directory
        memory_dir = project_root / ".doit" / "memory"
        memory_dir.mkdir(parents=True)

        # Create constitution.md
        constitution = memory_dir / "constitution.md"
        constitution.write_text(
            """# Project Constitution

## Vision

This project aims to build an authentication system.

## Requirements

- FR-001: Users must authenticate
- FR-002: System must validate credentials
"""
        )

        # Create roadmap.md
        roadmap = memory_dir / "roadmap.md"
        roadmap.write_text(
            """# Project Roadmap

## Active Requirements

- [x] User authentication
- [ ] Role-based access control
"""
        )

        # Create specs directory
        specs_dir = project_root / "specs"
        specs_dir.mkdir()

        # Create a spec
        spec_dir = specs_dir / "001-user-auth"
        spec_dir.mkdir()
        spec_file = spec_dir / "spec.md"
        spec_file.write_text(
            """# Feature Specification: User Authentication

## Summary

Implement user authentication with login and logout functionality.

## Requirements

- FR-001: Users must be able to log in
- FR-002: Sessions must expire after 24 hours
"""
        )

        yield project_root


class TestMemorySearchService:
    """Tests for MemorySearchService."""

    def test_search_keyword_finds_matches(self, temp_project):
        """Test that keyword search finds matching terms."""
        service = MemorySearchService(temp_project)

        results, sources, query = service.search("authentication")

        assert len(results) > 0
        assert any("authentication" in r.matched_text.lower() for r in results)

    def test_search_keyword_no_matches(self, temp_project):
        """Test that search returns empty for non-existent terms."""
        service = MemorySearchService(temp_project)

        results, sources, query = service.search("xyznonexistent123")

        assert len(results) == 0

    def test_search_keyword_case_insensitive(self, temp_project):
        """Test that search is case-insensitive by default."""
        service = MemorySearchService(temp_project)

        results_lower, _, _ = service.search("authentication")
        results_upper, _, _ = service.search("AUTHENTICATION")

        # Both should find results
        assert len(results_lower) > 0
        assert len(results_upper) > 0

    def test_search_keyword_case_sensitive(self, temp_project):
        """Test case-sensitive search."""
        service = MemorySearchService(temp_project)

        results_exact, _, _ = service.search(
            "authentication", case_sensitive=True
        )
        results_upper, _, _ = service.search(
            "AUTHENTICATION", case_sensitive=True
        )

        # Only exact case should match
        assert len(results_exact) > 0
        assert len(results_upper) == 0

    def test_relevance_scoring(self, temp_project):
        """Test that results are sorted by relevance score."""
        service = MemorySearchService(temp_project)

        results, _, _ = service.search("FR-001")

        # Results should be sorted by relevance (descending)
        if len(results) > 1:
            for i in range(len(results) - 1):
                assert results[i].relevance_score >= results[i + 1].relevance_score

    def test_max_results_limit(self, temp_project):
        """Test that max_results limits the number of results."""
        service = MemorySearchService(temp_project)

        results, _, _ = service.search("user", max_results=2)

        assert len(results) <= 2

    def test_source_filter_governance(self, temp_project):
        """Test filtering to governance files only."""
        service = MemorySearchService(temp_project)

        results, sources, _ = service.search(
            "authentication",
            source_filter=SourceFilter.GOVERNANCE,
        )

        # All sources should be from memory directory
        for source in sources:
            assert ".doit/memory" in str(source.file_path)

    def test_source_filter_specs(self, temp_project):
        """Test filtering to spec files only."""
        service = MemorySearchService(temp_project)

        results, sources, _ = service.search(
            "login",
            source_filter=SourceFilter.SPECS,
        )

        # All sources should be from specs directory
        for source in sources:
            assert "specs" in str(source.file_path)

    def test_search_phrase(self, temp_project):
        """Test phrase search."""
        service = MemorySearchService(temp_project)

        results, _, _ = service.search(
            "User Authentication",
            query_type=QueryType.PHRASE,
        )

        # Should find exact phrase
        assert len(results) > 0

    def test_search_regex(self, temp_project):
        """Test regex search."""
        service = MemorySearchService(temp_project)

        results, _, _ = service.search(
            r"FR-\d{3}",
            query_type=QueryType.REGEX,
        )

        # Should find FR-001, FR-002, etc.
        assert len(results) > 0


class TestSearchQuery:
    """Tests for SearchQuery validation."""

    def test_empty_query_raises_error(self):
        """Test that empty query raises ValueError."""
        with pytest.raises(ValueError, match="Query text cannot be empty"):
            SearchQuery(query_text="")

    def test_query_max_length(self):
        """Test that query exceeding max length raises ValueError."""
        long_query = "a" * 501
        with pytest.raises(ValueError, match="exceeds maximum length"):
            SearchQuery(query_text=long_query)

    def test_max_results_validation(self):
        """Test that invalid max_results raises ValueError."""
        with pytest.raises(ValueError, match="between 1 and 100"):
            SearchQuery(query_text="test", max_results=0)

        with pytest.raises(ValueError, match="between 1 and 100"):
            SearchQuery(query_text="test", max_results=101)


class TestSearchHistory:
    """Tests for search history functionality."""

    def test_history_tracking(self, temp_project):
        """Test that search queries are tracked in history."""
        service = MemorySearchService(temp_project)

        service.search("test1")
        service.search("test2")

        history = service.get_history()
        recent = history.get_recent(10)

        assert len(recent) == 2
        assert recent[0].query_text == "test2"  # Most recent first
        assert recent[1].query_text == "test1"

    def test_history_clear(self, temp_project):
        """Test clearing search history."""
        service = MemorySearchService(temp_project)

        service.search("test")
        service.clear_history()

        history = service.get_history()
        assert len(history.entries) == 0

    def test_history_max_entries(self, temp_project):
        """Test that history respects max entries limit."""
        service = MemorySearchService(temp_project)

        # Search more than max entries (default 10)
        for i in range(15):
            service.search(f"query{i}")

        history = service.get_history()
        assert len(history.entries) == 10
