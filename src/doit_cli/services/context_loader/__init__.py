"""Context loading package.

Re-exports the public API so existing imports like
`from doit_cli.services.context_loader import ContextLoader, estimate_tokens`
keep working after the Phase 3 split.

The original monolithic module has been split into:
- `utils`      — token estimation, truncation, keyword/similarity helpers.
- `condenser`  — `ContextCondenser` (soft-threshold guidance + hard-limit drop).
- `completed`  — completed-roadmap parsing and formatting.
- `loader`     — the `ContextLoader` orchestrator.
"""

from __future__ import annotations

from .completed import format_completed_for_context, parse_completed_roadmap
from .condenser import ContextCondenser
from .loader import ContextLoader
from .utils import (
    compute_similarity_scores,
    estimate_tokens,
    extract_keywords,
    truncate_content,
)

__all__ = [
    "ContextCondenser",
    "ContextLoader",
    "compute_similarity_scores",
    "estimate_tokens",
    "extract_keywords",
    "format_completed_for_context",
    "parse_completed_roadmap",
    "truncate_content",
]
