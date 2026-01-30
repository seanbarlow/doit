"""Line ending normalization utilities for cross-platform testing."""
from typing import Literal


LineEnding = Literal["CRLF", "LF", "CR", "MIXED"]


def normalize_line_endings(text: str, target: LineEnding = "LF") -> str:
    """
    Normalize all line endings in text to the target format.

    Args:
        text: Text to normalize
        target: Target line ending format ('LF', 'CRLF', or 'CR')

    Returns:
        Text with normalized line endings
    """
    # First normalize everything to LF
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")

    # Then convert to target format
    if target == "CRLF":
        return normalized.replace("\n", "\r\n")
    elif target == "CR":
        return normalized.replace("\n", "\r")
    else:  # LF (default)
        return normalized


def detect_line_ending(text: str) -> LineEnding:
    """
    Detect the line ending format used in text.

    Args:
        text: Text to analyze

    Returns:
        Detected line ending type ('CRLF', 'LF', 'CR', or 'MIXED')
    """
    has_crlf = "\r\n" in text
    has_lf_only = "\n" in text.replace("\r\n", "")  # LF not preceded by CR
    has_cr_only = "\r" in text.replace("\r\n", "")  # CR not followed by LF

    # Check for mixed line endings
    endings_found = sum([has_crlf, has_lf_only, has_cr_only])
    if endings_found > 1:
        return "MIXED"

    # Single line ending type
    if has_crlf:
        return "CRLF"
    elif has_lf_only:
        return "LF"
    elif has_cr_only:
        return "CR"

    # No line endings found (single line or empty)
    return "LF"  # Default assumption


def preserve_line_endings(original: str, modified: str) -> str:
    """
    Preserve the line ending style from original text when applying modifications.

    Args:
        original: Original text with desired line ending style
        modified: Modified text (assumed to have LF line endings)

    Returns:
        Modified text with original's line ending style
    """
    original_ending = detect_line_ending(original)

    if original_ending == "MIXED":
        # Can't reliably preserve mixed endings, default to CRLF on Windows, LF elsewhere
        import sys

        original_ending = "CRLF" if sys.platform == "win32" else "LF"

    return normalize_line_endings(modified, original_ending)


def count_lines(text: str) -> int:
    """
    Count lines in text, handling different line ending formats.

    Args:
        text: Text to count lines in

    Returns:
        Number of lines
    """
    normalized = normalize_line_endings(text, "LF")
    if not normalized:
        return 0
    return normalized.count("\n") + (1 if not normalized.endswith("\n") else 0)
