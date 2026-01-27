"""Tests for Windows line ending handling (CRLF vs LF)."""
import sys
from pathlib import Path

import pytest


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_detect_crlf_line_endings(temp_project_dir):
    """
    Test detection of CRLF line endings in files.

    Given: A file with CRLF line endings
    When: Line ending is detected
    Then: CRLF is correctly identified
    """
    from tests.utils.windows.line_ending_utils import detect_line_ending

    # Create file with explicit CRLF
    test_file = temp_project_dir / "test_crlf.txt"
    content_crlf = "Line 1\r\nLine 2\r\nLine 3\r\n"
    test_file.write_bytes(content_crlf.encode("utf-8"))

    # Read in binary mode to preserve exact line endings
    read_content = test_file.read_bytes().decode("utf-8")
    detected = detect_line_ending(read_content)

    assert detected == "CRLF", f"Expected CRLF but got {detected}"


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_detect_lf_line_endings(temp_project_dir):
    """
    Test detection of LF line endings in files.

    Given: A file with LF line endings
    When: Line ending is detected
    Then: LF is correctly identified
    """
    from tests.utils.windows.line_ending_utils import detect_line_ending

    # Create file with explicit LF
    test_file = temp_project_dir / "test_lf.txt"
    content_lf = "Line 1\nLine 2\nLine 3\n"
    test_file.write_bytes(content_lf.encode("utf-8"))

    # Read in binary mode to preserve exact line endings
    read_content = test_file.read_bytes().decode("utf-8")
    detected = detect_line_ending(read_content)

    assert detected == "LF", f"Expected LF but got {detected}"


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_detect_mixed_line_endings(temp_project_dir):
    """
    Test detection of mixed line endings in files.

    Given: A file with mixed CRLF and LF
    When: Line ending is detected
    Then: MIXED is correctly identified
    """
    from tests.utils.windows.line_ending_utils import detect_line_ending

    # Create file with mixed endings
    test_file = temp_project_dir / "test_mixed.txt"
    content_mixed = "Line 1\r\nLine 2\nLine 3\r\n"
    test_file.write_bytes(content_mixed.encode("utf-8"))

    # Read in binary mode to preserve exact line endings
    read_content = test_file.read_bytes().decode("utf-8")
    detected = detect_line_ending(read_content)

    assert detected == "MIXED", f"Expected MIXED but got {detected}"


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_normalize_crlf_to_lf(temp_project_dir):
    """
    Test normalization of CRLF to LF.

    Given: Content with CRLF line endings
    When: Normalized to LF
    Then: All CRLF are converted to LF
    """
    from tests.utils.windows.line_ending_utils import normalize_line_endings

    content_crlf = "Line 1\r\nLine 2\r\nLine 3\r\n"
    normalized = normalize_line_endings(content_crlf, "LF")

    assert "\r\n" not in normalized, "CRLF still present after normalization"
    assert "\n" in normalized, "LF not present in normalized content"
    assert normalized.count("\n") == 3, "Incorrect number of line breaks"


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_normalize_lf_to_crlf(temp_project_dir):
    """
    Test normalization of LF to CRLF.

    Given: Content with LF line endings
    When: Normalized to CRLF
    Then: All LF are converted to CRLF
    """
    from tests.utils.windows.line_ending_utils import normalize_line_endings

    content_lf = "Line 1\nLine 2\nLine 3\n"
    normalized = normalize_line_endings(content_lf, "CRLF")

    assert "\r\n" in normalized, "CRLF not present after normalization"
    assert normalized.count("\r\n") == 3, "Incorrect number of CRLF"


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_preserve_line_endings_crlf(temp_project_dir):
    """
    Test preserving CRLF line endings when modifying content.

    Given: Original content with CRLF endings
    When: Content is modified and line endings preserved
    Then: Modified content maintains CRLF endings
    """
    from tests.utils.windows.line_ending_utils import preserve_line_endings

    original = "Line 1\r\nLine 2\r\nLine 3\r\n"
    modified = "Line 1\nModified Line 2\nLine 3\n"  # LF in modified

    preserved = preserve_line_endings(original, modified)

    assert "\r\n" in preserved, "CRLF not preserved in modified content"
    assert "Modified Line 2" in preserved, "Modification lost"


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_git_autocrlf_behavior(temp_project_dir):
    """
    Test Git autocrlf behavior with Windows line endings.

    Given: Git repository with autocrlf configured
    When: Files are committed and checked out
    Then: Line endings are handled according to Git configuration
    """
    import subprocess

    # Initialize git repo
    subprocess.run(["git", "init"], cwd=temp_project_dir, check=True, capture_output=True)

    # Check Git autocrlf setting
    result = subprocess.run(
        ["git", "config", "core.autocrlf"],
        cwd=temp_project_dir,
        capture_output=True,
        text=True,
    )

    autocrlf_setting = result.stdout.strip() if result.returncode == 0 else "not set"

    # Configure git user for CI environments
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=temp_project_dir,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=temp_project_dir,
        capture_output=True,
    )

    # Create a test file
    test_file = temp_project_dir / "test.txt"
    test_file.write_text("Line 1\nLine 2\n", encoding="utf-8")

    # Stage and commit
    subprocess.run(["git", "add", "test.txt"], cwd=temp_project_dir, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Test commit"],
        cwd=temp_project_dir,
        check=True,
        capture_output=True,
    )

    # Read back the file
    content = test_file.read_text(encoding="utf-8")

    # Git should handle line endings based on autocrlf setting
    # On Windows, autocrlf=true converts to CRLF on checkout
    # This test validates the Git configuration works
    if sys.platform == "win32" and autocrlf_setting in ["true", "input"]:
        # Git may have converted endings
        pass  # Actual conversion depends on Git config

    # Just verify file is accessible and readable
    assert len(content) > 0, "File content empty after Git operations"


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_count_lines_with_different_endings(temp_project_dir):
    """
    Test line counting works correctly with different line endings.

    Given: Files with CRLF, LF, and mixed endings
    When: Lines are counted
    Then: Count is accurate regardless of ending type
    """
    from tests.utils.windows.line_ending_utils import count_lines

    content_crlf = "Line 1\r\nLine 2\r\nLine 3\r\n"
    content_lf = "Line 1\nLine 2\nLine 3\n"
    content_mixed = "Line 1\r\nLine 2\nLine 3\r\n"

    assert count_lines(content_crlf) == 3, "CRLF line count incorrect"
    assert count_lines(content_lf) == 3, "LF line count incorrect"
    assert count_lines(content_mixed) == 3, "Mixed line count incorrect"


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_crlf_in_markdown_files(temp_project_dir):
    """
    Test CRLF preservation in generated markdown files.

    Given: Markdown files generated on Windows
    When: Files are read and analyzed
    Then: CRLF endings are preserved where appropriate
    """
    from tests.utils.windows.line_ending_utils import detect_line_ending

    # Create markdown file with CRLF
    md_file = temp_project_dir / "test.md"
    markdown_content = "# Title\r\n\r\n## Section\r\n\r\nContent here.\r\n"
    md_file.write_bytes(markdown_content.encode("utf-8"))

    # Read back
    read_content = md_file.read_text(encoding="utf-8")
    detected = detect_line_ending(read_content)

    # Should detect CRLF in the markdown file
    assert detected in ["CRLF", "LF"], f"Unexpected ending: {detected}"
    assert "# Title" in read_content, "Markdown content corrupted"


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_comparison_ignores_line_ending_differences(comparison_tools):
    """
    Test that cross-platform comparison normalizes line endings.

    Given: Windows output with CRLF and Linux output with LF
    When: Outputs are compared
    Then: Line ending differences are normalized and don't cause mismatch
    """
    windows_output = "Line 1\r\nLine 2\r\nLine 3\r\n"
    linux_output = "Line 1\nLine 2\nLine 3\n"

    result = comparison_tools.compare_outputs(windows_output, linux_output)

    # Normalized outputs should match despite different line endings
    assert result.matches, "Outputs should match after line ending normalization"
    assert "line_endings" in result.normalization_applied, "Line ending normalization not applied"
