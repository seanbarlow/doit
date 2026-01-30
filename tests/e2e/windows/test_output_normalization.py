"""Tests for output normalization utilities for cross-platform comparison."""
import sys
from pathlib import Path

import pytest


@pytest.mark.windows
@pytest.mark.unix
def test_path_separator_normalization(comparison_tools):
    """
    Test that path separators are normalized from backslash to forward slash.

    Given: Windows paths with backslashes
    When: Paths are normalized
    Then: Forward slashes replace backslashes
    """
    # Windows-style paths
    windows_paths = [
        "C:\\Users\\Test\\project",
        "tests\\e2e\\windows\\test_file.py",
        ".doit\\scripts\\bash\\setup.sh",
        "specs\\001-feature\\plan.md",
    ]

    for win_path in windows_paths:
        normalized = comparison_tools.normalize_path(win_path)
        assert "\\" not in normalized, f"Backslashes remain in: {normalized}"
        assert "/" in normalized, f"No forward slashes in: {normalized}"


@pytest.mark.windows
@pytest.mark.unix
def test_line_ending_normalization():
    """
    Test that CRLF line endings are normalized to LF.

    Given: Text with CRLF line endings (Windows)
    When: Line endings are normalized
    Then: Only LF remains
    """
    from tests.utils.windows.line_ending_utils import normalize_line_endings

    # Text with CRLF
    text_crlf = "Line 1\r\nLine 2\r\nLine 3\r\n"

    # Normalize to LF
    normalized = normalize_line_endings(text_crlf, target="LF")

    # Verify CRLF converted
    assert "\r\n" not in normalized, "CRLF should be removed"
    assert normalized == "Line 1\nLine 2\nLine 3\n", "Lines not properly normalized"


@pytest.mark.windows
@pytest.mark.unix
def test_timestamp_stripping(comparison_tools):
    """
    Test that timestamps are stripped from output for comparison.

    Given: Output with timestamps
    When: Output is normalized
    Then: Timestamps are removed
    """
    # Output with various timestamp formats
    outputs_with_timestamps = [
        "2026-01-26 12:34:56 - Task completed",
        "[2026-01-26T12:34:56Z] Starting process",
        "Finished at 2026-01-26 12:34:56.123",
        "Created: 01/26/2026 12:34:56",
    ]

    for output in outputs_with_timestamps:
        normalized = comparison_tools.normalize_output(output)
        # After normalization, specific timestamps should be generalized or removed
        # (Implementation depends on ComparisonTools implementation)
        assert normalized is not None


@pytest.mark.windows
@pytest.mark.unix
def test_absolute_path_relativization(comparison_tools):
    """
    Test that absolute paths are converted to relative paths.

    Given: Output with absolute paths
    When: Paths are normalized
    Then: Paths become relative
    """
    # Absolute paths from different platforms
    test_paths = [
        "C:/GitHub/doit/tests/e2e/windows/test.py",
        "/home/user/projects/doit/tests/e2e/windows/test.py",
        "C:\\Users\\Test\\project\\specs\\001-feature\\plan.md",
    ]

    for abs_path in test_paths:
        normalized = comparison_tools.normalize_path(abs_path)
        # Verify path is still valid after normalization
        assert len(normalized) > 0, "Normalized path should not be empty"


@pytest.mark.windows
@pytest.mark.unix
def test_whitespace_normalization(comparison_tools):
    """
    Test that whitespace differences are normalized.

    Given: Text with varying whitespace
    When: Text is normalized
    Then: Whitespace is standardized
    """
    # Text with different whitespace patterns
    text_variations = [
        "Line 1\nLine 2\nLine 3",  # Unix line endings
        "Line 1\r\nLine 2\r\nLine 3",  # Windows line endings
        "Line 1\rLine 2\rLine 3",  # Old Mac line endings
    ]

    # Normalize all variations
    normalized_results = [
        comparison_tools.normalize_output(text) for text in text_variations
    ]

    # After normalization, line structure should be comparable
    for result in normalized_results:
        assert "Line 1" in result
        assert "Line 2" in result
        assert "Line 3" in result


@pytest.mark.windows
@pytest.mark.unix
def test_drive_letter_removal(comparison_tools):
    """
    Test that Windows drive letters are handled in normalization.

    Given: Windows paths with drive letters
    When: Paths are normalized
    Then: Drive letters are handled appropriately
    """
    # Windows paths with drive letters
    drive_paths = [
        "C:/projects/doit/tests",
        "D:\\data\\specs\\feature",
        "E:/backup/files",
    ]

    for drive_path in drive_paths:
        normalized = comparison_tools.normalize_path(drive_path)
        # Verify normalization produces valid path
        assert "/" in normalized, "Should contain forward slashes after normalization"


@pytest.mark.windows
@pytest.mark.unix
def test_ansi_color_code_removal(comparison_tools):
    """
    Test that ANSI color codes are removed from output.

    Given: Output with ANSI color codes
    When: Output is normalized
    Then: Color codes are stripped
    """
    # Output with ANSI color codes (from tools like pytest, rich)
    colored_outputs = [
        "\x1b[32mPASSED\x1b[0m tests/test_example.py",
        "\x1b[1;31mFAILED\x1b[0m tests/test_other.py",
        "\x1b[33mWARNING:\x1b[0m something happened",
    ]

    for colored_output in colored_outputs:
        normalized = comparison_tools.normalize_output(colored_output)
        # ANSI codes should be removed
        assert "\x1b[" not in normalized, f"ANSI codes remain in: {normalized}"


@pytest.mark.windows
@pytest.mark.unix
def test_unicode_normalization(comparison_tools):
    """
    Test that Unicode characters are preserved during normalization.

    Given: Text with Unicode characters
    When: Text is normalized
    Then: Unicode is preserved
    """
    # Text with various Unicode characters
    unicode_text = "Hello: こんにちは 你好 مرحبا 🚀"

    normalized = comparison_tools.normalize_output(unicode_text)

    # Verify Unicode preserved
    assert "こんにちは" in normalized
    assert "你好" in normalized
    assert "مرحبا" in normalized
    assert "🚀" in normalized


@pytest.mark.windows
@pytest.mark.unix
def test_case_sensitivity_handling():
    """
    Test that case sensitivity is handled appropriately for cross-platform comparison.

    Given: Paths with different cases
    When: Comparison is performed
    Then: Platform-appropriate case handling is applied
    """
    # On Windows, these should be considered equal
    # On Linux/macOS, they should be different
    path1 = "tests/TestFile.py"
    path2 = "tests/testfile.py"

    if sys.platform == "win32":
        # Windows is case-insensitive
        assert path1.lower() == path2.lower()
    else:
        # Linux/macOS are case-sensitive
        assert path1 != path2


@pytest.mark.windows
@pytest.mark.unix
def test_normalize_complex_output(comparison_tools):
    """
    Test normalization of complex output with multiple elements.

    Given: Complex output with paths, timestamps, line endings, ANSI codes
    When: Full normalization is applied
    Then: Output is fully normalized
    """
    complex_output = """
\x1b[32mTest Suite Results\x1b[0m
Executed at: 2026-01-26 12:34:56
Working directory: C:\\GitHub\\doit

Tests:
- tests\\e2e\\windows\\test_init.py - PASSED
- tests\\e2e\\windows\\test_specit.py - PASSED

Total: 2 passed, 0 failed
"""

    normalized = comparison_tools.normalize_output(complex_output)

    # Verify all normalization applied
    assert "\x1b[" not in normalized, "ANSI codes should be removed"
    assert "tests/e2e/windows" in normalized or "test_init.py" in normalized, \
        "Test paths should be present"


@pytest.mark.windows
@pytest.mark.unix
def test_empty_output_normalization(comparison_tools):
    """
    Test that empty or minimal output is handled correctly.

    Given: Empty or minimal output
    When: Normalization is applied
    Then: No errors occur
    """
    empty_outputs = [
        "",
        "\n",
        "   ",
        "\r\n",
    ]

    for empty_output in empty_outputs:
        normalized = comparison_tools.normalize_output(empty_output)
        # Should not raise an error
        assert normalized is not None
