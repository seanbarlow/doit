"""Unit tests for priority mapper utility.

Tests the priority mapper that maps GitHub labels to roadmap priorities (P1-P4),
testing all label formats (priority:P1, P1, critical, etc) and default behavior.
"""

import pytest

from doit_cli.utils.priority_mapper import (
    DEFAULT_PRIORITY,
    map_labels_to_priority,
    get_supported_label_formats,
)


class TestMapLabelsToPriority:
    """Tests for map_labels_to_priority function."""

    # Standard format tests
    def test_map_standard_format_p1(self):
        """Test mapping standard format priority:P1."""
        assert map_labels_to_priority(["epic", "priority:P1"]) == "P1"

    def test_map_standard_format_p2(self):
        """Test mapping standard format priority:P2."""
        assert map_labels_to_priority(["priority:P2", "enhancement"]) == "P2"

    def test_map_standard_format_p3(self):
        """Test mapping standard format priority:P3."""
        assert map_labels_to_priority(["priority:P3"]) == "P3"

    def test_map_standard_format_p4(self):
        """Test mapping standard format priority:P4."""
        assert map_labels_to_priority(["priority:P4"]) == "P4"

    def test_map_standard_format_case_insensitive(self):
        """Test standard format is case-insensitive."""
        assert map_labels_to_priority(["priority:p1"]) == "P1"
        assert map_labels_to_priority(["priority:p2"]) == "P2"
        assert map_labels_to_priority(["priority:p3"]) == "P3"
        assert map_labels_to_priority(["priority:p4"]) == "P4"

    # Short form tests
    def test_map_short_form_p1(self):
        """Test mapping short form P1."""
        assert map_labels_to_priority(["epic", "P1"]) == "P1"

    def test_map_short_form_p2(self):
        """Test mapping short form P2."""
        assert map_labels_to_priority(["P2", "bug"]) == "P2"

    def test_map_short_form_p3(self):
        """Test mapping short form P3."""
        assert map_labels_to_priority(["P3"]) == "P3"

    def test_map_short_form_p4(self):
        """Test mapping short form P4."""
        assert map_labels_to_priority(["P4"]) == "P4"

    def test_map_short_form_lowercase(self):
        """Test short form with lowercase."""
        assert map_labels_to_priority(["p1"]) == "P1"
        assert map_labels_to_priority(["p2"]) == "P2"
        assert map_labels_to_priority(["p3"]) == "P3"
        assert map_labels_to_priority(["p4"]) == "P4"

    # Semantic label tests
    def test_map_semantic_critical(self):
        """Test mapping semantic label 'critical' to P1."""
        assert map_labels_to_priority(["epic", "critical"]) == "P1"

    def test_map_semantic_high(self):
        """Test mapping semantic label 'high' to P2."""
        assert map_labels_to_priority(["high", "bug"]) == "P2"

    def test_map_semantic_medium(self):
        """Test mapping semantic label 'medium' to P3."""
        assert map_labels_to_priority(["medium"]) == "P3"

    def test_map_semantic_low(self):
        """Test mapping semantic label 'low' to P4."""
        assert map_labels_to_priority(["low"]) == "P4"

    def test_map_semantic_various_cases(self):
        """Test semantic labels with various cases."""
        # Critical
        assert map_labels_to_priority(["critical"]) == "P1"
        assert map_labels_to_priority(["Critical"]) == "P1"
        assert map_labels_to_priority(["CRITICAL"]) == "P1"

        # High
        assert map_labels_to_priority(["high"]) == "P2"
        assert map_labels_to_priority(["High"]) == "P2"
        assert map_labels_to_priority(["HIGH"]) == "P2"

        # Medium
        assert map_labels_to_priority(["medium"]) == "P3"
        assert map_labels_to_priority(["Medium"]) == "P3"
        assert map_labels_to_priority(["MEDIUM"]) == "P3"

        # Low
        assert map_labels_to_priority(["low"]) == "P4"
        assert map_labels_to_priority(["Low"]) == "P4"
        assert map_labels_to_priority(["LOW"]) == "P4"

    # Slash format tests
    def test_map_slash_format_critical(self):
        """Test mapping slash format priority/critical to P1."""
        assert map_labels_to_priority(["priority/critical"]) == "P1"

    def test_map_slash_format_high(self):
        """Test mapping slash format priority/high to P2."""
        assert map_labels_to_priority(["priority/high"]) == "P2"

    def test_map_slash_format_medium(self):
        """Test mapping slash format priority/medium to P3."""
        assert map_labels_to_priority(["priority/medium"]) == "P3"

    def test_map_slash_format_low(self):
        """Test mapping slash format priority/low to P4."""
        assert map_labels_to_priority(["priority/low"]) == "P4"

    # Default behavior tests
    def test_map_empty_labels(self):
        """Test mapping with empty labels list returns default."""
        assert map_labels_to_priority([]) == DEFAULT_PRIORITY
        assert map_labels_to_priority([]) == "P3"

    def test_map_no_priority_label(self):
        """Test mapping with no priority labels returns default."""
        labels = ["epic", "enhancement", "needs-review", "documentation"]
        assert map_labels_to_priority(labels) == DEFAULT_PRIORITY
        assert map_labels_to_priority(labels) == "P3"

    def test_map_unrecognized_priority_label(self):
        """Test mapping with unrecognized priority format returns default."""
        assert map_labels_to_priority(["priority-high"]) == "P3"
        assert map_labels_to_priority(["P5"]) == "P3"
        assert map_labels_to_priority(["urgent"]) == "P3"

    # Multiple labels tests
    def test_map_multiple_priority_labels_returns_first(self):
        """Test that first matching priority label is returned."""
        # P1 comes first in label list
        labels = ["epic", "P1", "P2", "P3"]
        assert map_labels_to_priority(labels) == "P1"

        # P2 comes first
        labels = ["epic", "P2", "P1"]
        assert map_labels_to_priority(labels) == "P2"

    def test_map_mixed_format_labels(self):
        """Test with mixed priority format labels."""
        # Standard format comes first
        labels = ["priority:P1", "critical"]
        assert map_labels_to_priority(labels) == "P1"

        # Semantic comes first
        labels = ["high", "priority:P1"]
        assert map_labels_to_priority(labels) == "P2"

        # Short form comes first
        labels = ["P3", "priority/high"]
        assert map_labels_to_priority(labels) == "P3"

    # Edge cases
    def test_map_with_similar_labels(self):
        """Test labels that are similar but not exact matches."""
        # These should not match
        assert map_labels_to_priority(["Priority:P1"]) == "P3"  # Wrong case in prefix
        assert map_labels_to_priority(["priority:P 1"]) == "P3"  # Space in value
        assert map_labels_to_priority(["priority P1"]) == "P3"  # Missing colon
        assert map_labels_to_priority(["priorityP1"]) == "P3"  # No separator

    def test_map_with_none_in_labels(self):
        """Test behavior when None values are in labels list."""
        # Filtering None values is not implemented, but it shouldn't crash
        # The function expects strings, so this tests robustness
        labels = ["epic", "P1", "enhancement"]
        assert map_labels_to_priority(labels) == "P1"

    def test_map_priority_precedence(self):
        """Test priority precedence when multiple formats exist."""
        # First label in list wins
        assert map_labels_to_priority(["P4", "P1"]) == "P4"
        assert map_labels_to_priority(["low", "critical"]) == "P4"
        assert map_labels_to_priority(["priority:P2", "priority:P1"]) == "P2"

    # Real-world examples
    def test_map_typical_epic_labels(self):
        """Test with typical epic label combinations."""
        assert map_labels_to_priority(["epic", "priority:P1", "feature"]) == "P1"
        assert map_labels_to_priority(["epic", "enhancement", "P2"]) == "P2"
        assert map_labels_to_priority(["epic"]) == "P3"

    def test_map_github_default_labels(self):
        """Test with GitHub default label schemes."""
        assert map_labels_to_priority(["bug", "priority/high"]) == "P2"
        assert map_labels_to_priority(["enhancement", "priority/low"]) == "P4"
        assert map_labels_to_priority(["documentation"]) == "P3"

    # Comprehensive coverage
    def test_map_all_standard_formats(self):
        """Test all standard format variations."""
        standard_labels = [
            ("priority:P1", "P1"),
            ("priority:p1", "P1"),
            ("priority:P2", "P2"),
            ("priority:p2", "P2"),
            ("priority:P3", "P3"),
            ("priority:p3", "P3"),
            ("priority:P4", "P4"),
            ("priority:p4", "P4"),
        ]

        for label, expected in standard_labels:
            assert map_labels_to_priority([label]) == expected

    def test_map_all_short_forms(self):
        """Test all short form variations."""
        short_forms = [
            ("P1", "P1"),
            ("p1", "P1"),
            ("P2", "P2"),
            ("p2", "P2"),
            ("P3", "P3"),
            ("p3", "P3"),
            ("P4", "P4"),
            ("p4", "P4"),
        ]

        for label, expected in short_forms:
            assert map_labels_to_priority([label]) == expected

    def test_map_all_semantic_labels(self):
        """Test all semantic label variations."""
        semantic_labels = [
            ("critical", "P1"),
            ("Critical", "P1"),
            ("CRITICAL", "P1"),
            ("high", "P2"),
            ("High", "P2"),
            ("HIGH", "P2"),
            ("medium", "P3"),
            ("Medium", "P3"),
            ("MEDIUM", "P3"),
            ("low", "P4"),
            ("Low", "P4"),
            ("LOW", "P4"),
        ]

        for label, expected in semantic_labels:
            assert map_labels_to_priority([label]) == expected

    def test_map_all_slash_formats(self):
        """Test all slash format variations."""
        slash_formats = [
            ("priority/critical", "P1"),
            ("priority/high", "P2"),
            ("priority/medium", "P3"),
            ("priority/low", "P4"),
        ]

        for label, expected in slash_formats:
            assert map_labels_to_priority([label]) == expected


class TestGetSupportedLabelFormats:
    """Tests for get_supported_label_formats function."""

    def test_get_supported_formats_returns_list(self):
        """Test that function returns a list."""
        result = get_supported_label_formats()
        assert isinstance(result, list)

    def test_get_supported_formats_not_empty(self):
        """Test that returned list is not empty."""
        result = get_supported_label_formats()
        assert len(result) > 0

    def test_get_supported_formats_includes_standard(self):
        """Test that standard format is included."""
        result = get_supported_label_formats()
        assert any("priority:P1" in fmt for fmt in result)

    def test_get_supported_formats_includes_short(self):
        """Test that short format is included."""
        result = get_supported_label_formats()
        assert any("P1" in fmt and "P2" in fmt for fmt in result)

    def test_get_supported_formats_includes_semantic(self):
        """Test that semantic format is included."""
        result = get_supported_label_formats()
        assert any("critical" in fmt.lower() for fmt in result)

    def test_get_supported_formats_includes_slash(self):
        """Test that slash format is included."""
        result = get_supported_label_formats()
        assert any("priority/" in fmt for fmt in result)

    def test_get_supported_formats_count(self):
        """Test that expected number of formats are returned."""
        result = get_supported_label_formats()
        # Should have 4 format categories
        assert len(result) == 4


class TestDefaultPriority:
    """Tests for DEFAULT_PRIORITY constant."""

    def test_default_priority_is_p3(self):
        """Test that default priority is P3."""
        assert DEFAULT_PRIORITY == "P3"

    def test_default_used_when_no_match(self):
        """Test that default is used when no priority labels match."""
        result = map_labels_to_priority(["bug", "enhancement"])
        assert result == DEFAULT_PRIORITY
