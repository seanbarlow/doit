# Interface Contracts: Context Roadmap Summary

**Feature**: `038-context-roadmap-summary`
**Date**: 2026-01-20

## Overview

This feature extends existing internal Python interfaces. No external APIs are introduced.

## Public Interfaces

### RoadmapSummarizer

New service class for roadmap parsing and summarization.

```python
class RoadmapSummarizer:
    """Service for parsing and summarizing roadmap content."""

    def __init__(self, config: SummarizationConfig) -> None:
        """Initialize with summarization configuration."""

    def parse_roadmap(self, content: str) -> list[RoadmapItem]:
        """Parse roadmap.md content into structured items.

        Args:
            content: Raw markdown content of roadmap.md

        Returns:
            List of RoadmapItem objects
        """

    def summarize(
        self,
        items: list[RoadmapItem],
        max_tokens: int,
        current_feature: Optional[str] = None
    ) -> RoadmapSummary:
        """Generate condensed roadmap summary.

        Args:
            items: Parsed roadmap items
            max_tokens: Maximum tokens for output
            current_feature: Current feature branch name for highlighting

        Returns:
            RoadmapSummary with condensed content
        """
```

### CompletedMatcher

New service for matching completed roadmap items.

```python
class CompletedMatcher:
    """Service for matching completed roadmap items to current feature."""

    def __init__(
        self,
        max_items: int = 5,
        min_relevance: float = 0.3
    ) -> None:
        """Initialize matcher with configuration."""

    def parse_completed(self, content: str) -> list[CompletedItem]:
        """Parse completed_roadmap.md content.

        Args:
            content: Raw markdown content

        Returns:
            List of CompletedItem objects without relevance scores
        """

    def match(
        self,
        items: list[CompletedItem],
        feature_branch: str,
        spec_title: Optional[str] = None
    ) -> list[CompletedItem]:
        """Find relevant completed items for current feature.

        Args:
            items: All completed items
            feature_branch: Current feature branch name
            spec_title: Optional spec title for additional keywords

        Returns:
            List of CompletedItem with relevance_score populated,
            filtered by min_relevance and limited to max_items
        """
```

### ContextSummarizer

New service for AI-powered context summarization.

```python
class ContextSummarizer:
    """Service for AI-powered context summarization."""

    def __init__(self, config: SummarizationConfig) -> None:
        """Initialize with configuration."""

    async def summarize(
        self,
        sources: list[ContextSource],
        max_tokens: int
    ) -> SummarizationResult:
        """Summarize multiple context sources.

        Args:
            sources: Context sources to summarize
            max_tokens: Maximum tokens for output

        Returns:
            SummarizationResult with condensed content

        Raises:
            SummarizationTimeout: If API call exceeds timeout
            SummarizationError: On API errors
        """

    def fallback_truncate(
        self,
        sources: list[ContextSource],
        max_tokens: int
    ) -> SummarizationResult:
        """Fallback truncation when AI summarization fails.

        Args:
            sources: Context sources to truncate
            max_tokens: Maximum tokens for output

        Returns:
            SummarizationResult with truncated content
        """
```

## Extended Interfaces

### ContextConfig Extension

```python
@dataclass
class ContextConfig:
    # Existing fields...
    version: int = 1
    enabled: bool = True
    max_tokens_per_source: int = 4000
    total_max_tokens: int = 16000
    sources: dict[str, SourceConfig] = field(default_factory=SourceConfig.default_sources)
    commands: dict[str, CommandOverride] = field(default_factory=dict)

    # NEW: Summarization configuration
    summarization: SummarizationConfig = field(default_factory=SummarizationConfig)
```

### ContextLoader Extension

```python
class ContextLoader:
    # Existing methods...

    # NEW: Methods to add
    def load_completed_roadmap(self) -> Optional[ContextSource]:
        """Load and match completed roadmap items.

        Returns:
            ContextSource with matched completed items, or None if disabled
        """

    def _summarize_roadmap(self, source: ContextSource) -> ContextSource:
        """Summarize roadmap source by priority.

        Args:
            source: Raw roadmap ContextSource

        Returns:
            ContextSource with summarized content
        """

    def _apply_ai_summarization(
        self,
        sources: list[ContextSource]
    ) -> list[ContextSource]:
        """Apply AI summarization if threshold exceeded.

        Args:
            sources: All loaded sources

        Returns:
            Sources with AI summarization applied if needed
        """
```

## Error Types

```python
class SummarizationError(Exception):
    """Base exception for summarization errors."""

class SummarizationTimeout(SummarizationError):
    """Raised when AI summarization times out."""

class SummarizationAPIError(SummarizationError):
    """Raised when AI API returns an error."""
```

## Backward Compatibility

All changes are additive:
- New SummarizationConfig defaults to enabled but with graceful degradation
- Existing ContextConfig YAML files continue to work (new fields have defaults)
- ContextLoader maintains existing method signatures
- No changes to existing return types
