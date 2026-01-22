"""Priority mapper utility for GitHub label to roadmap priority mapping.

This module provides functions to map GitHub issue labels to roadmap priority levels (P1-P4).
Supports various label formats including standard (priority:P1), short form (P1),
semantic (critical, high, medium, low), and slash format (priority/critical).
"""

from typing import List

# Priority mapping table covering common GitHub label patterns
PRIORITY_MAP = {
    # Standard format
    "priority:P1": "P1",
    "priority:p1": "P1",
    "priority:P2": "P2",
    "priority:p2": "P2",
    "priority:P3": "P3",
    "priority:p3": "P3",
    "priority:P4": "P4",
    "priority:p4": "P4",
    # Short form
    "P1": "P1",
    "p1": "P1",
    "P2": "P2",
    "p2": "P2",
    "P3": "P3",
    "p3": "P3",
    "P4": "P4",
    "p4": "P4",
    # Semantic (common aliases)
    "critical": "P1",
    "Critical": "P1",
    "CRITICAL": "P1",
    "high": "P2",
    "High": "P2",
    "HIGH": "P2",
    "medium": "P3",
    "Medium": "P3",
    "MEDIUM": "P3",
    "low": "P4",
    "Low": "P4",
    "LOW": "P4",
    # Slash format
    "priority/critical": "P1",
    "priority/high": "P2",
    "priority/medium": "P3",
    "priority/low": "P4",
}

DEFAULT_PRIORITY = "P3"


def map_labels_to_priority(labels: List[str]) -> str:
    """Map GitHub issue labels to roadmap priority.

    Searches through the provided labels and returns the first matching priority.
    Uses case-sensitive matching against the PRIORITY_MAP dictionary.
    Defaults to P3 (medium priority) if no priority label is found.

    Args:
        labels: List of GitHub issue label strings

    Returns:
        Priority string (P1, P2, P3, or P4)

    Examples:
        >>> map_labels_to_priority(["epic", "priority:P1", "enhancement"])
        'P1'
        >>> map_labels_to_priority(["epic", "critical"])
        'P1'
        >>> map_labels_to_priority(["epic"])
        'P3'
    """
    if not labels:
        return DEFAULT_PRIORITY

    for label in labels:
        priority = PRIORITY_MAP.get(label)
        if priority:
            return priority

    return DEFAULT_PRIORITY


def get_supported_label_formats() -> List[str]:
    """Get list of all supported label formats for documentation.

    Returns:
        List of example label formats that are recognized

    Examples:
        >>> formats = get_supported_label_formats()
        >>> 'priority:P1' in formats
        True
    """
    return [
        "priority:P1, priority:P2, priority:P3, priority:P4",
        "P1, P2, P3, P4 (case-insensitive)",
        "critical, high, medium, low (semantic)",
        "priority/critical, priority/high, priority/medium, priority/low",
    ]
