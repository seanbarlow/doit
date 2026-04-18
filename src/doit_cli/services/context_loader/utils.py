"""Shared helpers for the context loader: token estimation and similarity.

These helpers are pure functions (no I/O) split off from the original
`context_loader` module so the orchestration layer can stay focused on
loading files and stitching sources together.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)

_STOP_WORDS: frozenset[str] = frozenset(
    {
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
)

# Module-level caches for optional-dependency probes.
_tiktoken_encoding = None
_tiktoken_available: bool | None = None
_sklearn_available: bool | None = None


def _has_tiktoken() -> bool:
    """Return True if `tiktoken` is importable (cached)."""
    global _tiktoken_available
    if _tiktoken_available is None:
        try:
            import tiktoken  # noqa: F401

            _tiktoken_available = True
        except ImportError:
            _tiktoken_available = False
    return _tiktoken_available


def _has_sklearn() -> bool:
    """Return True if scikit-learn similarity helpers are importable (cached)."""
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
    """
    global _tiktoken_encoding

    if _has_tiktoken():
        try:
            import tiktoken

            if _tiktoken_encoding is None:
                _tiktoken_encoding = tiktoken.get_encoding("cl100k_base")
            return len(_tiktoken_encoding.encode(text))
        except (ImportError, ValueError, KeyError) as exc:
            logger.debug("tiktoken estimate failed, falling back: %s", exc)

    # Fallback: approximately 4 characters per token
    return max(1, len(text) // 4)


def truncate_content(content: str, max_tokens: int, path: Path) -> tuple[str, bool, int]:
    """Truncate content while preserving markdown structure.

    Algorithm:
    1. If content fits within limit, return as-is.
    2. Extract and preserve: title (first H1), every H2 header with its first
       paragraph, and any "Summary"/"Overview" sections in full.
    3. Add a truncation notice pointing at the full file.
    4. Fill any remaining budget with content from the top of the file.

    Returns:
        (truncated_content, was_truncated, original_tokens).
    """
    original_tokens = estimate_tokens(content)

    if original_tokens <= max_tokens:
        return content, False, original_tokens

    lines = content.split("\n")
    result_lines: list[str] = []
    current_tokens = 0

    # Find title (first H1)
    title_line = None
    for line in lines:
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

    # Fill remaining space with content from the top.
    target_tokens = max_tokens - 50  # Leave room for truncation notice
    if current_tokens < target_tokens:
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
    result_lines.append(
        f"<!-- Content truncated from {original_tokens} to ~{max_tokens} tokens. "
        f"Full file at: {path} -->"
    )

    truncated_content = "\n".join(result_lines)
    return truncated_content, True, original_tokens


def extract_keywords(text: str) -> set[str]:
    """Extract meaningful keywords for similarity matching.

    Returns lowercase words of length >2 with common stop words removed.
    """
    words = re.findall(r"\b[a-zA-Z][a-zA-Z0-9_-]*\b", text.lower())
    return {w for w in words if w not in _STOP_WORDS and len(w) > 2}


def compute_similarity_scores(current_text: str, candidate_texts: list[str]) -> list[float]:
    """Compute similarity scores between current text and candidates.

    Uses TF-IDF and cosine similarity if scikit-learn is available,
    otherwise falls back to Jaccard similarity over extracted keywords.
    """
    if not candidate_texts:
        return []

    if _has_sklearn():
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            all_texts = [current_text, *candidate_texts]
            vectorizer = TfidfVectorizer(stop_words="english", max_features=1000)
            tfidf_matrix = vectorizer.fit_transform(all_texts)

            similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
            return similarities[0].tolist()
        except (ValueError, ImportError) as exc:
            logger.debug("sklearn similarity failed, falling back: %s", exc)

    # Fallback: Jaccard similarity over keyword sets
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
