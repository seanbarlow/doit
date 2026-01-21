"""Fuzzy string matching utility using difflib.SequenceMatcher.

This module provides fuzzy string matching capabilities for finding similar strings
based on Levenshtein distance. Used primarily for matching feature names to roadmap items.
"""

from difflib import SequenceMatcher
from typing import List, Tuple


def calculate_similarity(str1: str, str2: str) -> float:
    """Calculate similarity ratio between two strings.

    Args:
        str1: First string to compare
        str2: Second string to compare

    Returns:
        Similarity ratio from 0.0 to 1.0, where 1.0 is identical

    Example:
        >>> calculate_similarity("GitHub Issue Linking", "GitHub Issue Auto-linking")
        0.85
    """
    if not str1 or not str2:
        return 0.0

    # Normalize strings: lowercase and strip whitespace
    str1_norm = str1.lower().strip()
    str2_norm = str2.lower().strip()

    # Use SequenceMatcher for Levenshtein-like distance
    matcher = SequenceMatcher(None, str1_norm, str2_norm)
    return matcher.ratio()


def find_best_match(
    target: str,
    candidates: List[str],
    threshold: float = 0.8
) -> Tuple[str, float] | None:
    """Find the best matching string from a list of candidates.

    Args:
        target: The string to match against
        candidates: List of candidate strings to search
        threshold: Minimum similarity ratio (0.0 to 1.0), default 0.8

    Returns:
        Tuple of (best_match, similarity_score) if found, None otherwise

    Example:
        >>> candidates = ["User Authentication", "GitHub Integration", "User Auth System"]
        >>> find_best_match("User Auth", candidates, threshold=0.7)
        ("User Auth System", 0.85)
    """
    if not target or not candidates:
        return None

    best_match = None
    best_score = 0.0

    for candidate in candidates:
        score = calculate_similarity(target, candidate)
        if score > best_score and score >= threshold:
            best_score = score
            best_match = candidate

    if best_match:
        return (best_match, best_score)
    return None


def find_all_matches(
    target: str,
    candidates: List[str],
    threshold: float = 0.8
) -> List[Tuple[str, float]]:
    """Find all matching strings above the threshold.

    Args:
        target: The string to match against
        candidates: List of candidate strings to search
        threshold: Minimum similarity ratio (0.0 to 1.0), default 0.8

    Returns:
        List of (match, score) tuples sorted by score descending

    Example:
        >>> candidates = ["User Auth", "User Authentication", "Authentication Service"]
        >>> find_all_matches("User Auth", candidates, threshold=0.7)
        [("User Auth", 1.0), ("User Authentication", 0.85), ("Authentication Service", 0.75)]
    """
    if not target or not candidates:
        return []

    matches = []
    for candidate in candidates:
        score = calculate_similarity(target, candidate)
        if score >= threshold:
            matches.append((candidate, score))

    # Sort by score descending
    matches.sort(key=lambda x: x[1], reverse=True)
    return matches


def is_exact_match(str1: str, str2: str) -> bool:
    """Check if two strings are an exact match (case-insensitive).

    Args:
        str1: First string
        str2: Second string

    Returns:
        True if strings match exactly (ignoring case/whitespace)

    Example:
        >>> is_exact_match("GitHub Issue Linking", "github issue linking")
        True
    """
    if not str1 or not str2:
        return False

    return str1.lower().strip() == str2.lower().strip()
