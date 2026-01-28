"""Unicode normalization utilities for macOS testing.

macOS uses NFD (Normalization Form Decomposed) by default for filenames,
while Windows and Linux typically use NFC (Normalization Form Composed).
This module provides utilities to handle these differences in testing.
"""

import os
import unicodedata
from pathlib import Path
from typing import List, Tuple, Optional


def normalize_nfd(text: str) -> str:
    """Normalize text to NFD (Normalization Form Decomposed).

    This is the default normalization form used by macOS for filenames.

    Args:
        text: Text to normalize

    Returns:
        NFD-normalized text
    """
    return unicodedata.normalize("NFD", text)


def normalize_nfc(text: str) -> str:
    """Normalize text to NFC (Normalization Form Composed).

    This is the default normalization form used by Windows and Linux.

    Args:
        text: Text to normalize

    Returns:
        NFC-normalized text
    """
    return unicodedata.normalize("NFC", text)


def detect_normalization(text: str) -> Optional[str]:
    """Detect the Unicode normalization form of the given text.

    Args:
        text: Text to check

    Returns:
        "NFD", "NFC", "NFKD", "NFKC", or None if text is ASCII-only
    """
    # Check if text is ASCII-only (no normalization needed)
    if text.isascii():
        return None

    # Check each normalization form
    if text == unicodedata.normalize("NFD", text):
        return "NFD"
    elif text == unicodedata.normalize("NFC", text):
        return "NFC"
    elif text == unicodedata.normalize("NFKD", text):
        return "NFKD"
    elif text == unicodedata.normalize("NFKC", text):
        return "NFKC"

    # Mixed or unknown normalization
    return "MIXED"


def compare_normalized(text1: str, text2: str, normalization: str = "NFC") -> bool:
    """Compare two strings after normalizing them to the same form.

    Args:
        text1: First string to compare
        text2: Second string to compare
        normalization: Normalization form to use ("NFC" or "NFD")

    Returns:
        True if the normalized strings are equal, False otherwise
    """
    if normalization.upper() == "NFD":
        return normalize_nfd(text1) == normalize_nfd(text2)
    elif normalization.upper() == "NFC":
        return normalize_nfc(text1) == normalize_nfc(text2)
    else:
        raise ValueError(f"Unsupported normalization form: {normalization}")


def get_filename_normalization(filepath: str) -> Optional[str]:
    """Detect the normalization form of a filename as stored on disk.

    Args:
        filepath: Path to file to check

    Returns:
        "NFD", "NFC", or None if ASCII-only or file doesn't exist
    """
    if not os.path.exists(filepath):
        return None

    # Get the actual filename from the filesystem
    filename = os.path.basename(filepath)

    return detect_normalization(filename)


def create_nfd_filename(base_path: str, filename: str) -> Path:
    """Create a file with an NFD-normalized filename.

    Args:
        base_path: Directory to create the file in
        filename: Desired filename (will be NFD-normalized)

    Returns:
        Path object pointing to the created file
    """
    nfd_filename = normalize_nfd(filename)
    filepath = Path(base_path) / nfd_filename
    filepath.touch()
    return filepath


def create_nfc_filename(base_path: str, filename: str) -> Path:
    """Create a file with an NFC-normalized filename.

    Args:
        base_path: Directory to create the file in
        filename: Desired filename (will be NFC-normalized)

    Returns:
        Path object pointing to the created file
    """
    nfc_filename = normalize_nfc(filename)
    filepath = Path(base_path) / nfc_filename
    filepath.touch()
    return filepath


def find_unicode_differences(text1: str, text2: str) -> List[Tuple[int, str, str]]:
    """Find positions where two strings differ in Unicode normalization.

    Args:
        text1: First string
        text2: Second string

    Returns:
        List of tuples (position, char1, char2) where strings differ
    """
    differences = []

    # Normalize to same length for comparison
    max_len = max(len(text1), len(text2))

    for i in range(max_len):
        char1 = text1[i] if i < len(text1) else ""
        char2 = text2[i] if i < len(text2) else ""

        if char1 != char2:
            differences.append((i, char1, char2))

    return differences


def list_unicode_files(directory: str) -> List[Tuple[str, str]]:
    """List all files in a directory that contain non-ASCII Unicode characters.

    Args:
        directory: Directory to scan

    Returns:
        List of tuples (filepath, normalization_form)
    """
    unicode_files = []

    try:
        for root, dirs, files in os.walk(directory):
            for filename in files:
                if not filename.isascii():
                    filepath = os.path.join(root, filename)
                    norm_form = detect_normalization(filename)
                    unicode_files.append((filepath, norm_form or "ASCII"))

    except (OSError, PermissionError):
        pass

    return unicode_files


def test_unicode_sample_strings() -> dict:
    """Provide sample Unicode strings for testing normalization.

    Returns:
        Dictionary of test strings with NFD and NFC variants
    """
    return {
        "e_acute": {
            "nfc": "\u00e9",  # é (single character)
            "nfd": "e\u0301",  # e + combining acute accent
            "display": "é",
        },
        "a_ring": {
            "nfc": "\u00e5",  # å (single character)
            "nfd": "a\u030a",  # a + combining ring above
            "display": "å",
        },
        "o_umlaut": {
            "nfc": "\u00f6",  # ö (single character)
            "nfd": "o\u0308",  # o + combining diaeresis
            "display": "ö",
        },
        "n_tilde": {
            "nfc": "\u00f1",  # ñ (single character)
            "nfd": "n\u0303",  # n + combining tilde
            "display": "ñ",
        },
    }
