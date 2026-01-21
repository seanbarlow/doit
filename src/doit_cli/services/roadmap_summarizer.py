"""Roadmap summarization service for AI context injection.

This module provides the RoadmapSummarizer service that parses roadmap.md
and generates condensed summaries with P1/P2 items prioritized.
"""

import re
from typing import Optional

from ..models.context_config import (
    RoadmapItem,
    RoadmapSummary,
    SummarizationConfig,
)


class RoadmapSummarizer:
    """Service for parsing and summarizing roadmap content.

    Parses roadmap.md by priority sections (P1-P4) and generates condensed
    summaries that include full P1/P2 items with rationale while reducing
    P3/P4 to titles only.
    """

    def __init__(self, config: Optional[SummarizationConfig] = None) -> None:
        """Initialize with summarization configuration.

        Args:
            config: Summarization configuration (uses defaults if None).
        """
        self.config = config or SummarizationConfig()

    def parse_roadmap(self, content: str) -> list[RoadmapItem]:
        """Parse roadmap.md content into structured items.

        Extracts items from markdown, parsing P1-P4 sections, rationale,
        and feature references.

        Args:
            content: Raw markdown content of roadmap.md

        Returns:
            List of RoadmapItem objects
        """
        items: list[RoadmapItem] = []
        lines = content.split("\n")

        current_priority = "P4"  # Default priority
        i = 0

        while i < len(lines):
            line = lines[i]

            # Check for priority section headers (### P1 - Critical, ## P2, etc.)
            priority_match = re.match(r"^#{2,3}\s*(P[1-4])\s*[-:]?\s*", line, re.IGNORECASE)
            if priority_match:
                current_priority = priority_match.group(1).upper()
                i += 1
                continue

            # Check for checklist items (- [ ] or - [x]) or plain list items (- text)
            item_match = re.match(r"^-\s*\[([ xX])\]\s*(.+)$", line)
            plain_match = re.match(r"^-\s+([^[\s].+)$", line) if not item_match else None

            if item_match:
                completed = item_match.group(1).lower() == "x"
                text = item_match.group(2).strip()
            elif plain_match:
                completed = False
                text = plain_match.group(1).strip()
            else:
                i += 1
                continue

            # Extract feature reference from text (e.g., `[034-fixit-workflow]` or [034-fixit])
            feature_ref = ""
            feature_match = re.search(r"`?\[?(\d{3}-[\w-]+)\]?`?", text)
            if feature_match:
                feature_ref = feature_match.group(1)

            # Look for rationale in following lines
            rationale = ""
            j = i + 1
            while j < len(lines):
                next_line = lines[j].strip()
                # Check for rationale line
                rationale_match = re.match(r"^-?\s*\*?\*?Rationale\*?\*?:\s*(.+)$", next_line, re.IGNORECASE)
                if rationale_match:
                    rationale = rationale_match.group(1).strip()
                    break
                # Stop if we hit another item or section
                if next_line.startswith("- [") or next_line.startswith("-") or next_line.startswith("#"):
                    break
                j += 1

            items.append(RoadmapItem(
                text=text,
                priority=current_priority,
                rationale=rationale,
                feature_ref=feature_ref,
                completed=completed,
            ))

            i += 1

        return items

    def summarize(
        self,
        items: list[RoadmapItem],
        max_tokens: int = 2000,
        current_feature: Optional[str] = None,
    ) -> RoadmapSummary:
        """Generate condensed roadmap summary.

        Creates a summary with:
        - Full P1/P2 items including rationale
        - P3/P4 items as titles only
        - Current feature highlighted if provided

        Args:
            items: Parsed roadmap items
            max_tokens: Maximum tokens for output
            current_feature: Current feature branch name for highlighting

        Returns:
            RoadmapSummary with condensed content
        """
        if not items:
            return RoadmapSummary(
                condensed_text="",
                item_count=0,
                priorities_included=[],
            )

        sections: list[str] = ["## Roadmap Summary", ""]
        priorities_included: set[str] = set()
        item_count = 0

        # Group items by priority
        by_priority: dict[str, list[RoadmapItem]] = {"P1": [], "P2": [], "P3": [], "P4": []}
        current_feature_items: list[RoadmapItem] = []

        for item in items:
            if item.completed:
                continue  # Skip completed items in roadmap summary

            priority = item.priority.upper()
            if priority in by_priority:
                by_priority[priority].append(item)

            # Check if this is the current feature
            if current_feature and item.feature_ref:
                # Match feature ref against current branch
                if current_feature in item.feature_ref or item.feature_ref in current_feature:
                    current_feature_items.append(item)

        # Add current feature section if we found matches
        if current_feature_items:
            sections.append("### Current Feature")
            for item in current_feature_items:
                sections.append(f"- **[CURRENT]** {item.text}")
                if item.rationale:
                    sections.append(f"  - *Rationale*: {item.rationale}")
                item_count += 1
                priorities_included.add(item.priority)
            sections.append("")

        # High priority section (P1/P2) - full details
        high_priority = by_priority["P1"] + by_priority["P2"]
        # Filter out items already shown in current feature
        high_priority = [i for i in high_priority if i not in current_feature_items]

        if high_priority:
            sections.append("### High Priority (P1-P2)")
            for item in high_priority:
                marker = "[P1]" if item.priority == "P1" else "[P2]"
                sections.append(f"- {marker} {item.text}")
                if item.rationale:
                    sections.append(f"  - *Rationale*: {item.rationale}")
                item_count += 1
                priorities_included.add(item.priority)
            sections.append("")

        # Lower priority section (P3/P4) - titles only
        low_priority = by_priority["P3"] + by_priority["P4"]
        # Filter out items already shown
        low_priority = [i for i in low_priority if i not in current_feature_items]

        if low_priority:
            sections.append("### Other Priorities (P3-P4)")
            for item in low_priority:
                # Extract just the title (first sentence or up to first period)
                title = item.text.split(".")[0].strip()
                if len(title) > 80:
                    title = title[:77] + "..."
                marker = "[P3]" if item.priority == "P3" else "[P4]"
                sections.append(f"- {marker} {title}")
                item_count += 1
                priorities_included.add(item.priority)
            sections.append("")

        condensed_text = "\n".join(sections)

        return RoadmapSummary(
            condensed_text=condensed_text,
            item_count=item_count,
            priorities_included=sorted(priorities_included),
        )
