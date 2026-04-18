"""Context condensing: guidance prompts and priority-based truncation.

The AI coding agent (Claude, Copilot, Cursor, etc.) running the command is
the summarizer — no external API calls are needed. This module adds the
guidance prompt that tells the AI how to prioritize the context, and drops
the lowest-priority sources when the hard limit is exceeded.
"""

from __future__ import annotations

import logging

from ...models.context_config import ContextSource, SummarizationConfig

logger = logging.getLogger(__name__)


class ContextCondenser:
    """Service for condensing context when it exceeds token thresholds.

    Two-tier approach:
    1. Soft threshold: add a guidance prompt so the AI agent prioritizes well.
    2. Hard limit: drop lowest-priority sources until under limit.
    """

    def __init__(self, config: SummarizationConfig) -> None:
        self.config = config

    def check_threshold(self, total_tokens: int, max_tokens: int) -> tuple[bool, bool]:
        """Return (exceeds_soft_threshold, exceeds_hard_limit)."""
        soft_threshold = int(max_tokens * (self.config.threshold_percentage / 100.0))
        return (total_tokens >= soft_threshold, total_tokens >= max_tokens)

    def add_guidance_prompt(
        self,
        content: str,
        current_feature: str | None = None,
    ) -> str:
        """Prepend AI guidance when context exceeds the soft threshold."""
        guidance_lines = [
            "<!-- AI CONTEXT GUIDANCE -->",
            "**Context Priority Instructions**: This context has been condensed. Please:",
            "- **Focus on P1/P2 priority items** in the roadmap - these are critical/high priority",
        ]

        if current_feature:
            guidance_lines.append(
                f"- **Pay special attention** to items related to: `{current_feature}`"
            )

        guidance_lines.extend(
            [
                "- Treat P3/P4 items as background context only",
                "- Use completed roadmap items for pattern reference and consistency",
                "<!-- END GUIDANCE -->",
                "",
            ]
        )

        return "\n".join(guidance_lines) + content

    def truncate_if_needed(
        self,
        sources: list[ContextSource],
        max_tokens: int,
        source_priorities: list[str],
    ) -> tuple[list[ContextSource], int]:
        """Drop lowest-priority sources until under `max_tokens`.

        Sources not listed in `source_priorities` are treated as lowest
        priority and removed first.
        """
        total_tokens = sum(s.token_count for s in sources)

        if total_tokens <= max_tokens:
            return sources, total_tokens

        priority_map: dict[str, int] = {}
        for idx, source_type in enumerate(source_priorities):
            priority_map[source_type] = idx

        sorted_sources = sorted(
            sources,
            key=lambda s: priority_map.get(s.source_type, 999),
        )

        kept_sources: list[ContextSource] = []
        kept_tokens = 0

        for source in sorted_sources:
            if kept_tokens + source.token_count <= max_tokens:
                kept_sources.append(source)
                kept_tokens += source.token_count
            else:
                logger.debug(
                    "Truncating source '%s' due to token limit (%d > %d)",
                    source.source_type,
                    kept_tokens + source.token_count,
                    max_tokens,
                )

        return kept_sources, kept_tokens
