"""Unit tests for RoadmapSummarizer service."""

import pytest

from doit_cli.models.context_config import (
    RoadmapItem,
    RoadmapSummary,
    SummarizationConfig,
)
from doit_cli.services.roadmap_summarizer import RoadmapSummarizer


class TestRoadmapSummarizer:
    """Tests for RoadmapSummarizer initialization."""

    def test_initialization_default_config(self):
        """Test initialization with default config."""
        summarizer = RoadmapSummarizer()
        assert summarizer.config is not None
        assert summarizer.config.enabled is True

    def test_initialization_custom_config(self):
        """Test initialization with custom config."""
        config = SummarizationConfig(enabled=False, threshold_percentage=50.0)
        summarizer = RoadmapSummarizer(config=config)
        assert summarizer.config.enabled is False
        assert summarizer.config.threshold_percentage == 50.0


class TestParseRoadmap:
    """Tests for parse_roadmap method."""

    def test_parse_empty_content(self):
        """Test parsing empty content."""
        summarizer = RoadmapSummarizer()
        items = summarizer.parse_roadmap("")
        assert items == []

    def test_parse_priority_sections(self):
        """Test parsing priority section headers."""
        content = """
## P1 - Critical

- [ ] Critical item 1
- [ ] Critical item 2

### P2 - High Priority

- [ ] High priority item

## P3 - Medium

- [ ] Medium priority item

### P4 - Low

- [ ] Low priority item
"""
        summarizer = RoadmapSummarizer()
        items = summarizer.parse_roadmap(content)

        assert len(items) == 5
        assert items[0].priority == "P1"
        assert items[1].priority == "P1"
        assert items[2].priority == "P2"
        assert items[3].priority == "P3"
        assert items[4].priority == "P4"

    def test_parse_checklist_items(self):
        """Test parsing checklist items with checkboxes."""
        content = """
### P1 - Critical

- [ ] Uncompleted item
- [x] Completed item
- [X] Another completed item
"""
        summarizer = RoadmapSummarizer()
        items = summarizer.parse_roadmap(content)

        assert len(items) == 3
        assert items[0].completed is False
        assert items[1].completed is True
        assert items[2].completed is True

    def test_parse_plain_list_items(self):
        """Test parsing plain list items (no checkbox)."""
        content = """
### P2 - High

- Plain list item without checkbox
- Another plain item
"""
        summarizer = RoadmapSummarizer()
        items = summarizer.parse_roadmap(content)

        assert len(items) == 2
        assert items[0].text == "Plain list item without checkbox"
        assert items[0].completed is False
        assert items[1].text == "Another plain item"

    def test_parse_rationale(self):
        """Test parsing rationale from following lines."""
        content = """
### P1 - Critical

- [ ] Important item
  - **Rationale**: This is why it matters
- [ ] Another item
  - Rationale: Without bold formatting
"""
        summarizer = RoadmapSummarizer()
        items = summarizer.parse_roadmap(content)

        assert len(items) == 2
        assert items[0].rationale == "This is why it matters"
        assert items[1].rationale == "Without bold formatting"

    def test_parse_feature_ref(self):
        """Test parsing feature references from item text."""
        content = """
### P1 - Critical

- [ ] Implement feature `[034-fixit-workflow]`
- [ ] Another feature [035-auto-diagrams]
- [ ] Feature with backticks `037-memory-search`
"""
        summarizer = RoadmapSummarizer()
        items = summarizer.parse_roadmap(content)

        assert len(items) == 3
        assert items[0].feature_ref == "034-fixit-workflow"
        assert items[1].feature_ref == "035-auto-diagrams"
        assert items[2].feature_ref == "037-memory-search"

    def test_parse_mixed_content(self):
        """Test parsing mixed content with various formats."""
        content = """
# Project Roadmap

Some introduction text.

## P1 - Critical

- [ ] First critical item `[001-feature]`
  - **Rationale**: Very important

## P2 - High Priority

- [x] Completed high priority item
- [ ] Open high priority item

### P3 - Medium

- Medium priority item (no checkbox)

## P4

- [ ] Low priority item
"""
        summarizer = RoadmapSummarizer()
        items = summarizer.parse_roadmap(content)

        assert len(items) == 5
        assert items[0].priority == "P1"
        assert items[0].feature_ref == "001-feature"
        assert items[0].rationale == "Very important"
        assert items[1].completed is True
        assert items[3].priority == "P3"


class TestSummarize:
    """Tests for summarize method."""

    def test_summarize_empty_items(self):
        """Test summarizing empty item list."""
        summarizer = RoadmapSummarizer()
        summary = summarizer.summarize([])

        assert summary.condensed_text == ""
        assert summary.item_count == 0
        assert summary.priorities_included == []

    def test_summarize_skips_completed_items(self):
        """Test that completed items are excluded from summary."""
        items = [
            RoadmapItem(text="Completed item", priority="P1", completed=True),
            RoadmapItem(text="Open item", priority="P1", completed=False),
        ]
        summarizer = RoadmapSummarizer()
        summary = summarizer.summarize(items)

        assert "Completed item" not in summary.condensed_text
        assert "Open item" in summary.condensed_text
        assert summary.item_count == 1

    def test_summarize_high_priority_with_rationale(self):
        """Test that P1/P2 items include rationale."""
        items = [
            RoadmapItem(
                text="P1 item",
                priority="P1",
                rationale="Important because...",
            ),
            RoadmapItem(
                text="P2 item",
                priority="P2",
                rationale="Also important",
            ),
        ]
        summarizer = RoadmapSummarizer()
        summary = summarizer.summarize(items)

        assert "[P1]" in summary.condensed_text
        assert "[P2]" in summary.condensed_text
        assert "Important because..." in summary.condensed_text
        assert "Also important" in summary.condensed_text
        assert "High Priority (P1-P2)" in summary.condensed_text

    def test_summarize_low_priority_titles_only(self):
        """Test that P3/P4 items are titles only."""
        items = [
            RoadmapItem(
                text="P3 item with long description that should be truncated",
                priority="P3",
                rationale="This rationale should not appear",
            ),
            RoadmapItem(
                text="P4 item",
                priority="P4",
                rationale="Neither should this",
            ),
        ]
        summarizer = RoadmapSummarizer()
        summary = summarizer.summarize(items)

        assert "[P3]" in summary.condensed_text
        assert "[P4]" in summary.condensed_text
        # Rationale should not be in summary for P3/P4
        assert "This rationale should not appear" not in summary.condensed_text
        assert "Other Priorities (P3-P4)" in summary.condensed_text

    def test_summarize_current_feature_highlighting(self):
        """Test current feature is highlighted in summary."""
        items = [
            RoadmapItem(
                text="Current feature work",
                priority="P1",
                feature_ref="038-context-roadmap",
            ),
            RoadmapItem(
                text="Other feature work",
                priority="P1",
                feature_ref="039-other-feature",
            ),
        ]
        summarizer = RoadmapSummarizer()
        summary = summarizer.summarize(items, current_feature="038-context-roadmap")

        assert "Current Feature" in summary.condensed_text
        assert "[CURRENT]" in summary.condensed_text
        assert "Current feature work" in summary.condensed_text

    def test_summarize_priorities_included(self):
        """Test priorities_included is populated correctly."""
        items = [
            RoadmapItem(text="P1 item", priority="P1"),
            RoadmapItem(text="P3 item", priority="P3"),
        ]
        summarizer = RoadmapSummarizer()
        summary = summarizer.summarize(items)

        assert "P1" in summary.priorities_included
        assert "P3" in summary.priorities_included
        assert "P2" not in summary.priorities_included
        assert "P4" not in summary.priorities_included

    def test_summarize_item_count(self):
        """Test item_count is correct."""
        items = [
            RoadmapItem(text="Item 1", priority="P1"),
            RoadmapItem(text="Item 2", priority="P2"),
            RoadmapItem(text="Item 3", priority="P3"),
            RoadmapItem(text="Completed", priority="P1", completed=True),  # Excluded
        ]
        summarizer = RoadmapSummarizer()
        summary = summarizer.summarize(items)

        assert summary.item_count == 3

    def test_summarize_truncates_long_titles(self):
        """Test that P3/P4 item titles are truncated if too long."""
        long_title = "A" * 100  # 100 characters
        items = [
            RoadmapItem(text=long_title, priority="P3"),
        ]
        summarizer = RoadmapSummarizer()
        summary = summarizer.summarize(items)

        # Should be truncated to 80 chars (77 + ...)
        assert "..." in summary.condensed_text
        assert len(long_title) > 80  # Verify the title was long

    def test_summarize_structure(self):
        """Test overall summary structure."""
        items = [
            RoadmapItem(text="P1 item", priority="P1", rationale="P1 rationale"),
            RoadmapItem(text="P2 item", priority="P2"),
            RoadmapItem(text="P3 item", priority="P3"),
            RoadmapItem(text="P4 item", priority="P4"),
        ]
        summarizer = RoadmapSummarizer()
        summary = summarizer.summarize(items)

        # Check structure
        assert "## Roadmap Summary" in summary.condensed_text
        assert "### High Priority (P1-P2)" in summary.condensed_text
        assert "### Other Priorities (P3-P4)" in summary.condensed_text


class TestRoadmapSummaryDataclass:
    """Tests for RoadmapSummary dataclass."""

    def test_default_values(self):
        """Test default RoadmapSummary values."""
        summary = RoadmapSummary(condensed_text="test")
        assert summary.condensed_text == "test"
        assert summary.item_count == 0
        assert summary.priorities_included == []

    def test_custom_values(self):
        """Test RoadmapSummary with custom values."""
        summary = RoadmapSummary(
            condensed_text="## Summary\nContent",
            item_count=5,
            priorities_included=["P1", "P2"],
        )
        assert summary.condensed_text == "## Summary\nContent"
        assert summary.item_count == 5
        assert summary.priorities_included == ["P1", "P2"]
