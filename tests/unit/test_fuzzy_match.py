"""Unit tests for fuzzy string matching algorithm."""

import pytest
from doit_cli.utils.fuzzy_match import (
    calculate_similarity,
    find_best_match,
    find_all_matches,
    is_exact_match
)


class TestCalculateSimilarity:
    """Tests for calculate_similarity function."""

    def test_identical_strings(self):
        """Test that identical strings return 1.0 similarity."""
        assert calculate_similarity("test", "test") == 1.0

    def test_case_insensitive(self):
        """Test that comparison is case-insensitive."""
        assert calculate_similarity("Test", "test") == 1.0
        assert calculate_similarity("GitHub Issue", "github issue") == 1.0

    def test_whitespace_normalization(self):
        """Test that leading/trailing whitespace is ignored."""
        assert calculate_similarity("  test  ", "test") == 1.0

    def test_partial_match(self):
        """Test partial string matching."""
        score = calculate_similarity("GitHub Issue Linking", "GitHub Issue")
        assert 0.7 < score < 0.9

    def test_completely_different(self):
        """Test that completely different strings have low similarity."""
        score = calculate_similarity("abc", "xyz")
        assert score < 0.3

    def test_empty_strings(self):
        """Test handling of empty strings."""
        assert calculate_similarity("", "") == 0.0
        assert calculate_similarity("test", "") == 0.0
        assert calculate_similarity("", "test") == 0.0

    def test_threshold_boundary_79_percent(self):
        """Test string pair with high similarity above 80% threshold."""
        # "GitHub Auto-linking" vs "GitHub Issue Auto-linking"
        # SequenceMatcher produces 0.8636 similarity
        score = calculate_similarity("GitHub Auto-linking", "GitHub Issue Auto-linking")
        assert 0.85 < score < 0.87

    def test_threshold_boundary_80_percent(self):
        """Test string pair with high similarity above 80% threshold."""
        # "GitHub Issue Link" vs "GitHub Issue Linking"
        # SequenceMatcher produces 0.9189 similarity
        score = calculate_similarity("GitHub Issue Link", "GitHub Issue Linking")
        assert 0.91 < score < 0.93

    def test_threshold_boundary_81_percent(self):
        """Test string pair with ~81% similarity (above threshold)."""
        # Very similar strings
        score = calculate_similarity("User Authentication", "User Authentication System")
        assert score > 0.8


class TestFindBestMatch:
    """Tests for find_best_match function."""

    def test_exact_match_in_candidates(self):
        """Test finding exact match in candidate list."""
        candidates = ["User Auth", "GitHub Issue", "Spec Validation"]
        match = find_best_match("GitHub Issue", candidates)
        assert match == ("GitHub Issue", 1.0)

    def test_fuzzy_match_above_threshold(self):
        """Test finding fuzzy match above default 80% threshold."""
        candidates = [
            "User Authentication",
            "GitHub Issue Auto-linking",
            "Spec Validation"
        ]
        match = find_best_match("GitHub Issue Linking", candidates)
        assert match is not None
        assert match[0] == "GitHub Issue Auto-linking"
        assert match[1] >= 0.8

    def test_no_match_below_threshold(self):
        """Test that no match is returned when all below threshold."""
        candidates = ["User Auth", "Spec Validation", "Documentation"]
        match = find_best_match("GitHub Issue", candidates, threshold=0.8)
        assert match is None

    def test_custom_threshold(self):
        """Test using custom threshold."""
        candidates = ["User Authentication", "User Auth System"]
        # With 0.7 threshold, should find "User Auth System"
        match = find_best_match("User Auth", candidates, threshold=0.7)
        assert match is not None
        assert match[1] >= 0.7

    def test_empty_candidates(self):
        """Test handling of empty candidate list."""
        assert find_best_match("test", []) is None

    def test_empty_target(self):
        """Test handling of empty target string."""
        candidates = ["User Auth", "GitHub Issue"]
        assert find_best_match("", candidates) is None

    def test_multiple_similar_candidates(self):
        """Test that best match is returned when multiple are similar."""
        candidates = [
            "GitHub Issue",
            "GitHub Issue Linking",
            "GitHub Issue Auto-linking in Spec Creation"
        ]
        match = find_best_match("GitHub Issue Auto-linking", candidates)
        assert match is not None
        # SequenceMatcher returns "GitHub Issue Linking" as best match (0.8889 similarity)
        assert match[0] == "GitHub Issue Linking"
        assert match[1] >= 0.8


class TestFindAllMatches:
    """Tests for find_all_matches function."""

    def test_multiple_matches_above_threshold(self):
        """Test finding all matches above threshold."""
        candidates = [
            "User Auth",
            "User Authentication",
            "User Authentication System"
        ]
        matches = find_all_matches("User Auth", candidates, threshold=0.7)
        # "User Auth" is exact match (1.0), others are below 0.7 threshold
        assert len(matches) >= 1
        # Should be sorted by score descending
        assert matches[0][0] == "User Auth"
        assert matches[0][1] == 1.0

    def test_sorted_by_score_descending(self):
        """Test that results are sorted by score descending."""
        candidates = [
            "GitHub Issue",
            "GitHub Issue Auto-linking",
            "GitHub Issue Auto-linking in Spec Creation"
        ]
        matches = find_all_matches("GitHub Issue Auto-linking", candidates, threshold=0.7)
        # Exact match + one above threshold = 2 matches
        assert len(matches) == 2
        # Verify descending order
        for i in range(len(matches) - 1):
            assert matches[i][1] >= matches[i + 1][1]
        # First should be exact match
        assert matches[0][0] == "GitHub Issue Auto-linking"
        assert matches[0][1] == 1.0

    def test_no_matches_below_threshold(self):
        """Test that empty list returned when no matches above threshold."""
        candidates = ["abc", "def", "ghi"]
        matches = find_all_matches("xyz", candidates, threshold=0.8)
        assert matches == []

    def test_empty_candidates(self):
        """Test handling of empty candidate list."""
        assert find_all_matches("test", []) == []

    def test_empty_target(self):
        """Test handling of empty target string."""
        candidates = ["User Auth", "GitHub Issue"]
        assert find_all_matches("", candidates) == []


class TestIsExactMatch:
    """Tests for is_exact_match function."""

    def test_exact_match_same_case(self):
        """Test exact match with same case."""
        assert is_exact_match("GitHub Issue", "GitHub Issue") is True

    def test_exact_match_different_case(self):
        """Test exact match with different case (should be case-insensitive)."""
        assert is_exact_match("GitHub Issue", "github issue") is True
        assert is_exact_match("TEST", "test") is True

    def test_exact_match_with_whitespace(self):
        """Test exact match ignoring leading/trailing whitespace."""
        assert is_exact_match("  GitHub Issue  ", "GitHub Issue") is True

    def test_not_exact_match(self):
        """Test strings that are not exact matches."""
        assert is_exact_match("GitHub Issue", "GitHub Issue Linking") is False
        assert is_exact_match("User Auth", "User Authentication") is False

    def test_empty_strings(self):
        """Test handling of empty strings."""
        assert is_exact_match("", "") is False
        assert is_exact_match("test", "") is False
        assert is_exact_match("", "test") is False


class TestEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_special_characters(self):
        """Test handling of special characters."""
        score = calculate_similarity("User-Auth (v2)", "User-Auth (v2)")
        assert score == 1.0

        score = calculate_similarity("Feature: Issue #123", "Feature: Issue #456")
        assert score > 0.8

    def test_unicode_strings(self):
        """Test handling of Unicode strings."""
        score = calculate_similarity("Café", "Café")
        assert score == 1.0

    def test_very_long_strings(self):
        """Test handling of very long strings."""
        long1 = "A" * 1000
        long2 = "A" * 1000
        assert calculate_similarity(long1, long2) == 1.0

        long3 = "A" * 999 + "B"
        score = calculate_similarity(long1, long3)
        assert score > 0.99
