"""Context loading service for AI context injection.

This module provides the ContextLoader service that loads and aggregates
project context (constitution, roadmap, specs) for injection into doit commands.
"""

import logging
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..models.context_config import (
    CompletedItem,
    ContextConfig,
    ContextSource,
    LoadedContext,
    SourceConfig,
    SummarizationConfig,
)
from .roadmap_summarizer import RoadmapSummarizer

logger = logging.getLogger(__name__)

# Cache for loaded tiktoken encoding
_tiktoken_encoding = None
_tiktoken_available: Optional[bool] = None

# Cache for sklearn availability
_sklearn_available: Optional[bool] = None


def _has_tiktoken() -> bool:
    """Check if tiktoken is available."""
    global _tiktoken_available
    if _tiktoken_available is None:
        try:
            import tiktoken  # noqa: F401
            _tiktoken_available = True
        except ImportError:
            _tiktoken_available = False
    return _tiktoken_available


def _has_sklearn() -> bool:
    """Check if scikit-learn is available."""
    global _sklearn_available
    if _sklearn_available is None:
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer  # noqa: F401
            from sklearn.metrics.pairwise import cosine_similarity  # noqa: F401
            _sklearn_available = True
        except ImportError:
            _sklearn_available = False
    return _sklearn_available


def estimate_tokens(text: str) -> int:
    """Estimate token count for text.

    Uses tiktoken if available, otherwise falls back to character-based estimate.

    Args:
        text: The text to estimate tokens for.

    Returns:
        Estimated token count.
    """
    global _tiktoken_encoding

    if _has_tiktoken():
        try:
            import tiktoken
            if _tiktoken_encoding is None:
                _tiktoken_encoding = tiktoken.get_encoding("cl100k_base")
            return len(_tiktoken_encoding.encode(text))
        except Exception:
            pass

    # Fallback: approximately 4 characters per token
    return max(1, len(text) // 4)


def truncate_content(content: str, max_tokens: int, path: Path) -> tuple[str, bool, int]:
    """Truncate content while preserving markdown structure.

    Algorithm:
    1. If content fits within limit, return as-is
    2. Extract and preserve:
       - Title (first H1)
       - All H2 headers with first paragraph under each
       - Any "Summary" or "Overview" sections in full
    3. Add truncation notice
    4. Fill remaining tokens with content from top of file

    Args:
        content: The markdown content to truncate.
        max_tokens: Maximum token count.
        path: Path to the file (for truncation notice).

    Returns:
        Tuple of (truncated_content, was_truncated, original_tokens).
    """
    original_tokens = estimate_tokens(content)

    if original_tokens <= max_tokens:
        return content, False, original_tokens

    lines = content.split("\n")
    result_lines: list[str] = []
    current_tokens = 0

    # Find title (first H1)
    title_line = None
    for i, line in enumerate(lines):
        if line.startswith("# ") and not line.startswith("## "):
            title_line = line
            break

    if title_line:
        result_lines.append(title_line)
        result_lines.append("")
        current_tokens = estimate_tokens("\n".join(result_lines))

    # Find Summary/Overview sections and H2 headers
    i = 0
    summary_found = False
    while i < len(lines) and current_tokens < max_tokens * 0.7:
        line = lines[i]

        # Check for Summary or Overview sections
        if re.match(r"^##\s+(Summary|Overview)", line, re.IGNORECASE):
            summary_found = True
            section_lines = [line]
            i += 1
            # Collect entire section
            while i < len(lines) and not lines[i].startswith("## "):
                section_lines.append(lines[i])
                i += 1
            section_text = "\n".join(section_lines)
            section_tokens = estimate_tokens(section_text)
            if current_tokens + section_tokens < max_tokens * 0.9:
                result_lines.extend(section_lines)
                current_tokens += section_tokens
            continue

        # Collect H2 headers with first paragraph
        if line.startswith("## ") and not summary_found:
            result_lines.append(line)
            result_lines.append("")
            i += 1
            # Get first paragraph after header
            paragraph_lines = []
            while i < len(lines) and lines[i].strip() and not lines[i].startswith("#"):
                paragraph_lines.append(lines[i])
                i += 1
            if paragraph_lines:
                result_lines.extend(paragraph_lines)
                result_lines.append("")
            current_tokens = estimate_tokens("\n".join(result_lines))
            continue

        i += 1

    # Fill remaining space with content from top
    target_tokens = max_tokens - 50  # Leave room for truncation notice
    if current_tokens < target_tokens:
        # Add content from the beginning that wasn't already added
        remaining_content = []
        for line in lines:
            if line not in result_lines:
                remaining_content.append(line)
                test_result = "\n".join(result_lines + remaining_content)
                if estimate_tokens(test_result) > target_tokens:
                    remaining_content.pop()
                    break
        result_lines.extend(remaining_content)

    # Add truncation notice
    result_lines.append("")
    result_lines.append(f"<!-- Content truncated from {original_tokens} to ~{max_tokens} tokens. Full file at: {path} -->")

    truncated_content = "\n".join(result_lines)
    return truncated_content, True, original_tokens


def extract_keywords(text: str) -> set[str]:
    """Extract meaningful keywords from text for similarity matching.

    Args:
        text: Text to extract keywords from.

    Returns:
        Set of lowercase keywords.
    """
    # Common stop words to exclude
    stop_words = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "as", "is", "was", "are", "were", "been",
        "be", "have", "has", "had", "do", "does", "did", "will", "would",
        "could", "should", "may", "might", "must", "shall", "can", "need",
        "this", "that", "these", "those", "it", "its", "they", "them",
        "their", "we", "our", "you", "your", "i", "my", "me", "he", "she",
        "his", "her", "him", "who", "what", "which", "when", "where", "why",
        "how", "all", "each", "every", "both", "few", "more", "most", "other",
        "some", "such", "no", "not", "only", "own", "same", "so", "than",
        "too", "very", "just", "also", "now", "new", "first", "last", "long",
        "great", "little", "old", "big", "small", "high", "low", "good", "bad",
    }

    # Extract words (alphanumeric sequences)
    words = re.findall(r"\b[a-zA-Z][a-zA-Z0-9_-]*\b", text.lower())

    # Filter out stop words and short words
    keywords = {w for w in words if w not in stop_words and len(w) > 2}

    return keywords


def compute_similarity_scores(
    current_text: str, candidate_texts: list[str]
) -> list[float]:
    """Compute similarity scores between current text and candidates.

    Uses TF-IDF and cosine similarity if scikit-learn is available,
    otherwise falls back to keyword overlap.

    Args:
        current_text: The reference text.
        candidate_texts: List of texts to compare against.

    Returns:
        List of similarity scores (0.0 to 1.0) for each candidate.
    """
    if not candidate_texts:
        return []

    if _has_sklearn():
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            all_texts = [current_text] + candidate_texts
            vectorizer = TfidfVectorizer(stop_words="english", max_features=1000)
            tfidf_matrix = vectorizer.fit_transform(all_texts)

            # Compute cosine similarity between first text and all others
            similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
            return similarities[0].tolist()
        except Exception:
            pass

    # Fallback: keyword overlap (Jaccard similarity)
    current_keywords = extract_keywords(current_text)
    if not current_keywords:
        return [0.0] * len(candidate_texts)

    scores = []
    for candidate in candidate_texts:
        candidate_keywords = extract_keywords(candidate)
        if not candidate_keywords:
            scores.append(0.0)
            continue
        intersection = len(current_keywords & candidate_keywords)
        union = len(current_keywords | candidate_keywords)
        scores.append(intersection / union if union > 0 else 0.0)

    return scores


class ContextCondenser:
    """Service for condensing context when it exceeds token thresholds.

    Uses a two-tier approach:
    1. Soft threshold: Add guidance prompt for the AI agent to prioritize
    2. Hard limit: Truncate sources based on priority configuration

    The key insight is that the AI coding agent (Claude, Copilot, etc.) running
    the command IS the summarizer - no external API calls are needed. The guidance
    prompt tells the AI how to prioritize the provided context.
    """

    def __init__(self, config: SummarizationConfig) -> None:
        """Initialize with summarization configuration.

        Args:
            config: SummarizationConfig with threshold and priority settings.
        """
        self.config = config

    def check_threshold(
        self, total_tokens: int, max_tokens: int
    ) -> tuple[bool, bool]:
        """Check if context exceeds soft or hard thresholds.

        Args:
            total_tokens: Current total token count.
            max_tokens: Maximum allowed tokens.

        Returns:
            Tuple of (exceeds_soft_threshold, exceeds_hard_limit).
        """
        soft_threshold = int(max_tokens * (self.config.threshold_percentage / 100.0))
        return (total_tokens >= soft_threshold, total_tokens >= max_tokens)

    def add_guidance_prompt(
        self,
        content: str,
        current_feature: Optional[str] = None,
    ) -> str:
        """Add AI guidance prompt when context exceeds soft threshold.

        The guidance tells the AI coding agent how to prioritize the context.
        This works identically for Claude, Copilot, Cursor, or any AI agent.

        Args:
            content: The markdown context content.
            current_feature: Current feature branch name for highlighting.

        Returns:
            Markdown content with guidance prepended.
        """
        guidance_lines = [
            "<!-- AI CONTEXT GUIDANCE -->",
            "**Context Priority Instructions**: This context has been condensed. Please:",
            "- **Focus on P1/P2 priority items** in the roadmap - these are critical/high priority",
        ]

        if current_feature:
            guidance_lines.append(
                f"- **Pay special attention** to items related to: `{current_feature}`"
            )

        guidance_lines.extend([
            "- Treat P3/P4 items as background context only",
            "- Use completed roadmap items for pattern reference and consistency",
            "<!-- END GUIDANCE -->",
            "",
        ])

        return "\n".join(guidance_lines) + content

    def truncate_if_needed(
        self,
        sources: list["ContextSource"],
        max_tokens: int,
        source_priorities: list[str],
    ) -> tuple[list["ContextSource"], int]:
        """Truncate sources based on priority when exceeding hard limit.

        Removes lowest-priority sources first until under limit.
        Uses source_priorities from config to determine removal order.

        Args:
            sources: List of context sources.
            max_tokens: Maximum total token count.
            source_priorities: Ordered list of source types to preserve.

        Returns:
            Tuple of (filtered sources, new total tokens).
        """
        total_tokens = sum(s.token_count for s in sources)

        if total_tokens <= max_tokens:
            return sources, total_tokens

        # Build priority map (lower index = higher priority = keep)
        priority_map: dict[str, int] = {}
        for idx, source_type in enumerate(source_priorities):
            priority_map[source_type] = idx

        # Sort sources by priority (higher priority = lower index = first)
        # Sources not in priority list get lowest priority (will be removed first)
        sorted_sources = sorted(
            sources,
            key=lambda s: priority_map.get(s.source_type, 999),
        )

        # Keep sources until we exceed the limit
        kept_sources: list[ContextSource] = []
        kept_tokens = 0

        for source in sorted_sources:
            if kept_tokens + source.token_count <= max_tokens:
                kept_sources.append(source)
                kept_tokens += source.token_count
            else:
                logger.debug(
                    f"Truncating source '{source.source_type}' due to token limit "
                    f"({kept_tokens + source.token_count} > {max_tokens})"
                )

        return kept_sources, kept_tokens


def parse_completed_roadmap(content: str) -> list[CompletedItem]:
    """Parse completed_roadmap.md content into CompletedItem list.

    Handles markdown table format with columns for item, priority, date, branch.

    Args:
        content: Raw markdown content of completed_roadmap.md

    Returns:
        List of CompletedItem objects
    """
    from datetime import date as date_type

    items: list[CompletedItem] = []
    lines = content.split("\n")

    # Find table rows (lines starting with |)
    in_table = False
    for line in lines:
        line = line.strip()

        # Skip header separator row (|---|---|...)
        if line.startswith("|") and "---" in line:
            in_table = True
            continue

        # Skip header row before separator
        if line.startswith("|") and not in_table:
            continue

        # Parse table data rows
        if line.startswith("|") and in_table:
            # Split by | and filter empty strings
            cells = [c.strip() for c in line.split("|") if c.strip()]
            if len(cells) >= 2:
                text = cells[0]
                priority = cells[1] if len(cells) > 1 else ""
                date_str = cells[2] if len(cells) > 2 else ""
                branch = cells[3] if len(cells) > 3 else ""

                # Parse date if provided
                completion_date = None
                if date_str:
                    try:
                        # Try common formats
                        for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d-%m-%Y"]:
                            try:
                                completion_date = date_type.fromisoformat(date_str) if "-" in date_str and len(date_str) == 10 else None
                                break
                            except ValueError:
                                continue
                    except Exception:
                        pass

                items.append(CompletedItem(
                    text=text,
                    priority=priority,
                    completion_date=completion_date,
                    feature_branch=branch,
                    relevance_score=0.0,
                ))

    return items


def format_completed_for_context(items: list[CompletedItem]) -> str:
    """Format completed items as AI-friendly markdown.

    Creates a structured format that AI agents can semantically match
    against the current feature being implemented.

    Args:
        items: List of CompletedItem to format

    Returns:
        Formatted markdown string for context injection
    """
    if not items:
        return ""

    sections = ["## Completed Roadmap Items", ""]
    sections.append("*Related completed features for context:*")
    sections.append("")

    for item in items:
        # Format the item with available metadata
        line = f"- **{item.text}**"
        if item.priority:
            line += f" ({item.priority})"
        sections.append(line)

        # Add metadata as sub-items
        if item.completion_date:
            sections.append(f"  - Completed: {item.completion_date}")
        if item.feature_branch:
            sections.append(f"  - Branch: `{item.feature_branch}`")

    sections.append("")
    return "\n".join(sections)


class ContextLoader:
    """Service for loading and aggregating project context.

    This service loads context from various sources (constitution, roadmap,
    specs) and formats them for injection into AI command prompts.
    """

    def __init__(
        self,
        project_root: Path,
        config: Optional[ContextConfig] = None,
        command: Optional[str] = None,
    ):
        """Initialize context loader.

        Args:
            project_root: Root directory of the project.
            config: Context configuration (loads default if None).
            command: Current command name for per-command overrides.
        """
        self.project_root = project_root
        self.command = command

        # Load config from file if not provided
        if config is None:
            config_path = project_root / ".doit" / "config" / "context.yaml"
            self.config = ContextConfig.from_yaml(config_path)
        else:
            self.config = config

        # Internal cache for loaded content
        self._cache: dict[Path, str] = {}

    def _is_debug_enabled(self) -> bool:
        """Check if debug mode is enabled."""
        return os.environ.get("DOIT_DEBUG", "").lower() in ("1", "true", "yes")

    def _log_debug(self, message: str) -> None:
        """Log debug message if debug mode is enabled."""
        if self._is_debug_enabled():
            print(f"[context] {message}")

    def _read_file(self, path: Path) -> Optional[str]:
        """Read file content with caching.

        Args:
            path: Path to the file to read.

        Returns:
            File content or None if file doesn't exist or can't be read.
        """
        if path in self._cache:
            return self._cache[path]

        if not path.exists():
            return None

        try:
            content = path.read_text(encoding="utf-8")
            self._cache[path] = content
            return content
        except (OSError, UnicodeDecodeError) as e:
            self._log_debug(f"Warning: Could not read {path}: {e}")
            return None

    def load(self) -> LoadedContext:
        """Load all configured context sources.

        Returns:
            LoadedContext with all sources loaded and processed.
        """
        if not self.config.enabled:
            return LoadedContext(loaded_at=datetime.now())

        sources: list[ContextSource] = []
        total_tokens = 0

        # Get source configs sorted by priority
        source_configs = [
            (name, self.config.get_source_config(name, self.command))
            for name in ["constitution", "tech_stack", "roadmap", "completed_roadmap", "current_spec", "related_specs"]
        ]
        source_configs.sort(key=lambda x: x[1].priority)

        for source_name, source_config in source_configs:
            if not source_config.enabled:
                continue

            # Check total token limit
            if total_tokens >= self.config.total_max_tokens:
                self._log_debug(f"Skipping {source_name}: total token limit reached")
                break

            remaining_tokens = self.config.total_max_tokens - total_tokens
            max_for_source = min(self.config.max_tokens_per_source, remaining_tokens)

            if source_name == "constitution":
                source = self.load_constitution(max_tokens=max_for_source)
                if source:
                    sources.append(source)
                    total_tokens += source.token_count
            elif source_name == "tech_stack":
                source = self.load_tech_stack(max_tokens=max_for_source)
                if source:
                    sources.append(source)
                    total_tokens += source.token_count
            elif source_name == "roadmap":
                source = self.load_roadmap(max_tokens=max_for_source)
                if source:
                    sources.append(source)
                    total_tokens += source.token_count
            elif source_name == "completed_roadmap":
                source = self.load_completed_roadmap(max_tokens=max_for_source)
                if source:
                    sources.append(source)
                    total_tokens += source.token_count
            elif source_name == "current_spec":
                source = self.load_current_spec(max_tokens=max_for_source)
                if source:
                    sources.append(source)
                    total_tokens += source.token_count
            elif source_name == "related_specs":
                related = self.find_related_specs(
                    max_count=source_config.max_count,
                    max_tokens_per_spec=max_for_source // max(source_config.max_count, 1),
                )
                for spec in related:
                    if total_tokens + spec.token_count <= self.config.total_max_tokens:
                        sources.append(spec)
                        total_tokens += spec.token_count

        any_truncated = any(s.truncated for s in sources)

        self._log_debug(f"Total context: {total_tokens} tokens from {len(sources)} sources")

        # Apply condensation if needed
        context = LoadedContext(
            sources=sources,
            total_tokens=total_tokens,
            any_truncated=any_truncated,
            loaded_at=datetime.now(),
        )

        return self._check_and_apply_condensation(context)

    def _check_and_apply_condensation(
        self, context: LoadedContext
    ) -> LoadedContext:
        """Apply condensation if context exceeds token thresholds.

        Uses a two-tier approach:
        1. Soft threshold: Adds guidance prompt for AI to prioritize
        2. Hard limit: Truncates sources based on priority

        The guidance prompt is designed to work with any AI coding agent
        (Claude, Copilot, Cursor, etc.) - no external API calls needed.

        Args:
            context: The loaded context to check.

        Returns:
            LoadedContext, possibly with condensation_guidance set.
        """
        if not self.config.summarization.enabled:
            return context

        condenser = ContextCondenser(self.config.summarization)

        exceeds_soft, exceeds_hard = condenser.check_threshold(
            context.total_tokens, self.config.total_max_tokens
        )

        # If exceeds hard limit, truncate sources
        if exceeds_hard:
            self._log_debug(
                f"Context exceeds hard limit ({context.total_tokens} >= "
                f"{self.config.total_max_tokens}), truncating sources"
            )
            new_sources, new_total = condenser.truncate_if_needed(
                context.sources,
                self.config.total_max_tokens,
                self.config.summarization.source_priorities,
            )
            context = LoadedContext(
                sources=new_sources,
                total_tokens=new_total,
                any_truncated=True,
                loaded_at=context.loaded_at,
            )
            # Recheck soft threshold after truncation
            exceeds_soft, _ = condenser.check_threshold(
                context.total_tokens, self.config.total_max_tokens
            )

        # If exceeds soft threshold, add guidance prompt
        if exceeds_soft:
            soft_threshold = int(
                self.config.total_max_tokens
                * (self.config.summarization.threshold_percentage / 100.0)
            )
            self._log_debug(
                f"Context exceeds soft threshold ({context.total_tokens} >= "
                f"{soft_threshold}), adding guidance prompt"
            )

            # Get current feature for context-aware guidance
            current_feature = None
            branch = self.get_current_branch()
            if branch:
                current_feature = self.extract_feature_name(branch)

            # Store guidance flag in context for to_markdown to use
            context._guidance_prompt = condenser.add_guidance_prompt(
                "", current_feature
            ).rstrip()

        return context

    def load_constitution(self, max_tokens: Optional[int] = None) -> Optional[ContextSource]:
        """Load constitution.md if enabled and exists.

        Args:
            max_tokens: Maximum token count (uses config default if None).

        Returns:
            ContextSource for constitution or None if not available.
        """
        max_tokens = max_tokens or self.config.max_tokens_per_source
        path = self.project_root / ".doit" / "memory" / "constitution.md"

        content = self._read_file(path)
        if content is None:
            self._log_debug("Constitution not found")
            return None

        truncated_content, was_truncated, original_tokens = truncate_content(
            content, max_tokens, path
        )
        token_count = estimate_tokens(truncated_content)

        self._log_debug(f"Loaded constitution: {token_count} tokens")

        return ContextSource(
            source_type="constitution",
            path=path,
            content=truncated_content,
            token_count=token_count,
            truncated=was_truncated,
            original_tokens=original_tokens if was_truncated else None,
        )

    def load_tech_stack(self, max_tokens: Optional[int] = None) -> Optional[ContextSource]:
        """Load tech-stack.md if enabled and exists.

        Args:
            max_tokens: Maximum token count (uses config default if None).

        Returns:
            ContextSource for tech_stack or None if not available.
        """
        max_tokens = max_tokens or self.config.max_tokens_per_source
        path = self.project_root / ".doit" / "memory" / "tech-stack.md"

        content = self._read_file(path)
        if content is None:
            self._log_debug("Tech stack not found")
            return None

        truncated_content, was_truncated, original_tokens = truncate_content(
            content, max_tokens, path
        )
        token_count = estimate_tokens(truncated_content)

        self._log_debug(f"Loaded tech stack: {token_count} tokens")

        return ContextSource(
            source_type="tech_stack",
            path=path,
            content=truncated_content,
            token_count=token_count,
            truncated=was_truncated,
            original_tokens=original_tokens if was_truncated else None,
        )

    def load_roadmap(self, max_tokens: Optional[int] = None) -> Optional[ContextSource]:
        """Load roadmap.md if enabled and exists.

        If summarization is enabled AND the roadmap exceeds max_tokens,
        parses the roadmap and generates a condensed summary with P1/P2
        items prioritized.

        Args:
            max_tokens: Maximum token count (uses config default if None).

        Returns:
            ContextSource for roadmap or None if not available.
        """
        max_tokens = max_tokens or self.config.max_tokens_per_source
        path = self.project_root / ".doit" / "memory" / "roadmap.md"

        content = self._read_file(path)
        if content is None:
            self._log_debug("Roadmap not found")
            return None

        # Check if summarization is needed (enabled AND exceeds limit)
        original_tokens = estimate_tokens(content)
        if self.config.summarization.enabled and original_tokens > max_tokens:
            return self._summarize_roadmap(path, content, max_tokens)

        # Content fits within limit - use truncation only if needed
        truncated_content, was_truncated, original_tokens = truncate_content(
            content, max_tokens, path
        )
        token_count = estimate_tokens(truncated_content)

        self._log_debug(f"Loaded roadmap: {token_count} tokens")

        return ContextSource(
            source_type="roadmap",
            path=path,
            content=truncated_content,
            token_count=token_count,
            truncated=was_truncated,
            original_tokens=original_tokens if was_truncated else None,
        )

    def _summarize_roadmap(
        self, path: Path, content: str, max_tokens: int
    ) -> ContextSource:
        """Summarize roadmap content by priority.

        Args:
            path: Path to roadmap file.
            content: Raw roadmap content.
            max_tokens: Maximum token count.

        Returns:
            ContextSource with summarized roadmap content.
        """
        original_tokens = estimate_tokens(content)

        # Get current feature for highlighting
        branch = self.get_current_branch()
        current_feature = self.extract_feature_name(branch) if branch else None

        # Parse and summarize
        summarizer = RoadmapSummarizer(self.config.summarization)
        items = summarizer.parse_roadmap(content)
        summary = summarizer.summarize(items, max_tokens, current_feature)

        token_count = estimate_tokens(summary.condensed_text)
        was_summarized = token_count < original_tokens

        self._log_debug(
            f"Loaded roadmap (summarized): {token_count} tokens "
            f"({summary.item_count} items, priorities: {summary.priorities_included})"
        )

        return ContextSource(
            source_type="roadmap",
            path=path,
            content=summary.condensed_text,
            token_count=token_count,
            truncated=was_summarized,
            original_tokens=original_tokens if was_summarized else None,
        )

    def load_completed_roadmap(
        self, max_tokens: Optional[int] = None
    ) -> Optional[ContextSource]:
        """Load completed_roadmap.md and format for AI context.

        Parses the completed roadmap items and formats them for semantic
        matching by the AI coding agent.

        Args:
            max_tokens: Maximum token count (uses config default if None).

        Returns:
            ContextSource with formatted completed items, or None if not available.
        """
        max_tokens = max_tokens or self.config.max_tokens_per_source
        path = self.project_root / ".doit" / "memory" / "completed_roadmap.md"

        content = self._read_file(path)
        if content is None:
            self._log_debug("Completed roadmap not found")
            return None

        # Parse completed items
        items = parse_completed_roadmap(content)
        if not items:
            self._log_debug("No completed items found in completed_roadmap.md")
            return None

        # Limit items based on config
        max_count = self.config.summarization.completed_items_max_count
        items = items[:max_count]

        # Format for context
        formatted_content = format_completed_for_context(items)
        token_count = estimate_tokens(formatted_content)

        # Truncate if needed
        if token_count > max_tokens:
            truncated_content, was_truncated, original_tokens = truncate_content(
                formatted_content, max_tokens, path
            )
            token_count = estimate_tokens(truncated_content)
        else:
            truncated_content = formatted_content
            was_truncated = False
            original_tokens = token_count

        self._log_debug(f"Loaded completed_roadmap: {token_count} tokens ({len(items)} items)")

        return ContextSource(
            source_type="completed_roadmap",
            path=path,
            content=truncated_content,
            token_count=token_count,
            truncated=was_truncated,
            original_tokens=original_tokens if was_truncated else None,
        )

    def get_current_branch(self) -> Optional[str]:
        """Get current git branch name.

        Returns:
            Branch name or None if not in a git repo or git unavailable.
        """
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=5,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except (subprocess.SubprocessError, FileNotFoundError, OSError):
            pass
        return None

    def extract_feature_name(self, branch: str) -> Optional[str]:
        """Extract feature name from branch name.

        Expects branch format like '026-ai-context-injection' or 'feature/026-name'.

        Args:
            branch: Git branch name.

        Returns:
            Feature name (e.g., '026-ai-context-injection') or None if not matched.
        """
        # Match patterns like: 026-feature-name, feature/026-name
        patterns = [
            r"^(\d{3}-[\w-]+)",  # 026-feature-name
            r"^feature/(\d{3}-[\w-]+)",  # feature/026-name
            r"^feat/(\d{3}-[\w-]+)",  # feat/026-name
        ]

        for pattern in patterns:
            match = re.match(pattern, branch)
            if match:
                return match.group(1)

        return None

    def load_current_spec(self, max_tokens: Optional[int] = None) -> Optional[ContextSource]:
        """Load current feature spec based on branch name.

        Args:
            max_tokens: Maximum token count (uses config default if None).

        Returns:
            ContextSource for current spec or None if not available.
        """
        max_tokens = max_tokens or self.config.max_tokens_per_source

        branch = self.get_current_branch()
        if not branch:
            self._log_debug("Not in a git repository or git unavailable")
            return None

        feature_name = self.extract_feature_name(branch)
        if not feature_name:
            self._log_debug(f"Branch '{branch}' does not match feature pattern")
            return None

        # Look for spec in specs directory
        spec_path = self.project_root / "specs" / feature_name / "spec.md"
        if not spec_path.exists():
            self._log_debug(f"Spec not found at {spec_path}")
            return None

        content = self._read_file(spec_path)
        if content is None:
            return None

        truncated_content, was_truncated, original_tokens = truncate_content(
            content, max_tokens, spec_path
        )
        token_count = estimate_tokens(truncated_content)

        self._log_debug(f"Loaded current_spec ({feature_name}): {token_count} tokens")

        return ContextSource(
            source_type="current_spec",
            path=spec_path,
            content=truncated_content,
            token_count=token_count,
            truncated=was_truncated,
            original_tokens=original_tokens if was_truncated else None,
        )

    def get_memory_files(self) -> list[Path]:
        """Get list of governance memory files.

        Returns paths to constitution.md, roadmap.md, and completed_roadmap.md
        if they exist.

        Returns:
            List of paths to governance memory files.
        """
        memory_dir = self.project_root / ".doit" / "memory"
        files = []

        governance_files = [
            "constitution.md",
            "roadmap.md",
            "completed_roadmap.md",
        ]

        for filename in governance_files:
            path = memory_dir / filename
            if path.exists():
                files.append(path)

        return files

    def get_spec_files(self) -> list[Path]:
        """Get list of all spec.md files in the specs directory.

        Returns:
            List of paths to spec.md files.
        """
        specs_dir = self.project_root / "specs"
        files = []

        if not specs_dir.exists():
            return files

        for spec_dir in specs_dir.iterdir():
            if not spec_dir.is_dir():
                continue
            spec_path = spec_dir / "spec.md"
            if spec_path.exists():
                files.append(spec_path)

        return sorted(files)

    def get_all_searchable_files(self) -> list[Path]:
        """Get all files that can be searched.

        Returns:
            Combined list of memory and spec files.
        """
        return self.get_memory_files() + self.get_spec_files()

    def find_related_specs(
        self,
        max_count: int = 3,
        max_tokens_per_spec: Optional[int] = None,
        similarity_threshold: float = 0.3,
    ) -> list[ContextSource]:
        """Find specs related to current feature.

        Args:
            max_count: Maximum number of related specs to return.
            max_tokens_per_spec: Maximum tokens per spec (uses config default if None).
            similarity_threshold: Minimum similarity score to include.

        Returns:
            List of ContextSource objects for related specs.
        """
        max_tokens = max_tokens_per_spec or self.config.max_tokens_per_source

        # Get current spec for comparison
        current_spec = self.load_current_spec(max_tokens=max_tokens)
        if not current_spec:
            return []

        current_feature = self.extract_feature_name(self.get_current_branch() or "")
        if not current_feature:
            return []

        # Find all spec directories
        specs_dir = self.project_root / "specs"
        if not specs_dir.exists():
            return []

        candidate_specs: list[tuple[Path, str]] = []
        for spec_dir in specs_dir.iterdir():
            if not spec_dir.is_dir():
                continue
            if spec_dir.name == current_feature:
                continue  # Skip current spec

            spec_path = spec_dir / "spec.md"
            if spec_path.exists():
                content = self._read_file(spec_path)
                if content:
                    # Use title and summary for matching
                    # Extract first 1000 chars for efficiency
                    candidate_specs.append((spec_path, content[:1000]))

        if not candidate_specs:
            return []

        # Compute similarity scores
        candidate_texts = [text for _, text in candidate_specs]
        scores = compute_similarity_scores(current_spec.content[:1000], candidate_texts)

        # Filter by threshold and sort by score
        scored_specs = [
            (score, path, text)
            for score, (path, text) in zip(scores, candidate_specs)
            if score >= similarity_threshold
        ]
        scored_specs.sort(key=lambda x: x[0], reverse=True)

        # Load top specs
        related: list[ContextSource] = []
        for score, path, _ in scored_specs[:max_count]:
            content = self._read_file(path)
            if content is None:
                continue

            truncated_content, was_truncated, original_tokens = truncate_content(
                content, max_tokens, path
            )
            token_count = estimate_tokens(truncated_content)

            self._log_debug(
                f"Loaded related_spec ({path.parent.name}): "
                f"{token_count} tokens (similarity: {score:.2f})"
            )

            related.append(
                ContextSource(
                    source_type="related_specs",
                    path=path,
                    content=truncated_content,
                    token_count=token_count,
                    truncated=was_truncated,
                    original_tokens=original_tokens if was_truncated else None,
                )
            )

        return related
