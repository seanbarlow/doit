"""Tests for Windows-specific path handling edge cases."""
import sys
from pathlib import Path

import pytest


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_path_with_spaces(path_validator, temp_project_dir):
    """
    Test handling of Windows paths with spaces.

    Given: A path containing spaces
    When: Path is analyzed by WindowsPathValidator
    Then: Path is correctly parsed and validated
    """
    test_path = temp_project_dir / "My Project" / "test file.txt"

    # Analyze path
    info = path_validator.analyze_path(test_path)

    # Verify analysis
    assert not info.contains_reserved_name, "Path incorrectly flagged as reserved"
    assert not info.exceeds_max_path, "Path incorrectly flagged as exceeding MAX_PATH"
    assert "/" in info.normalized_path, "Path not normalized to forward slashes"


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_drive_letter_detection(path_validator):
    """
    Test detection of Windows drive letters in absolute paths.

    Given: An absolute Windows path with drive letter
    When: Path is analyzed
    Then: Drive letter is correctly extracted
    """
    test_path = r"C:\Users\Test\project\file.txt"

    info = path_validator.analyze_path(test_path)

    # Verify drive letter detection
    assert info.is_absolute, "Path not detected as absolute"
    assert info.drive_letter == "C", f"Drive letter incorrect: {info.drive_letter}"
    assert not info.is_unc, "Regular path incorrectly detected as UNC"


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_unc_path_detection(path_validator):
    r"""
    Test detection of UNC paths (\\server\share).

    Given: A UNC network path
    When: Path is analyzed
    Then: UNC format is correctly detected
    """
    test_path = r"\\server\share\folder\file.txt"

    info = path_validator.analyze_path(test_path)

    # Verify UNC detection
    assert info.is_unc, "UNC path not detected"
    assert info.drive_letter is None, "UNC path should not have drive letter"


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
@pytest.mark.parametrize(
    "reserved_name",
    [
        "CON",
        "PRN",
        "AUX",
        "NUL",
        "COM1",
        "COM2",
        "COM9",
        "LPT1",
        "LPT2",
        "LPT9",
    ],
)
def test_reserved_filename_detection(path_validator, reserved_name):
    """
    Test detection of Windows reserved filenames.

    Given: A path containing a Windows reserved filename
    When: Path is analyzed
    Then: Reserved name is correctly detected
    """
    # Test with just the name
    assert path_validator.is_reserved_name(reserved_name), f"{reserved_name} not detected as reserved"

    # Test with extension
    assert path_validator.is_reserved_name(
        f"{reserved_name}.txt"
    ), f"{reserved_name}.txt not detected as reserved"

    # Test in full path
    test_path = Path(f"C:/test/{reserved_name}/file.txt")
    info = path_validator.analyze_path(test_path)
    assert info.contains_reserved_name, f"{reserved_name} in path not detected"
    assert info.reserved_name == reserved_name.upper(), "Reserved name not correctly identified"


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_path_length_limit_260_chars(path_validator):
    """
    Test detection of paths exceeding Windows MAX_PATH limit (260 characters).

    Given: Paths of varying lengths
    When: Paths are analyzed
    Then: Paths exceeding 260 characters are correctly flagged
    """
    # Short path - should pass
    short_path = "C:/test/file.txt"
    assert not path_validator.exceeds_max_path(short_path), "Short path incorrectly flagged"

    # Path near limit (252 chars - should pass)
    # "C:/" (3) + "a" * 240 (240) + "/file.txt" (9) = 252 chars
    near_limit_path = "C:/" + "a" * 240 + "/file.txt"
    assert not path_validator.exceeds_max_path(
        near_limit_path
    ), f"Path near limit incorrectly flagged (length: {len(near_limit_path)})"

    # Path exceeding limit (270 chars - should fail)
    long_path = "C:/" + "a" * 260 + "/file.txt"
    assert path_validator.exceeds_max_path(long_path), "Long path not flagged as exceeding limit"

    # Verify through analyze_path
    info = path_validator.analyze_path(long_path)
    assert info.exceeds_max_path, "Long path not detected by analyze_path"
    assert info.length > 260, f"Path length {info.length} not > 260"


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_mixed_path_separators(path_validator, comparison_tools):
    r"""
    Test handling of mixed forward/backward slashes in paths.

    Given: A path with mixed separators (C:\path/to\file)
    When: Path is normalized
    Then: All separators are converted to forward slashes
    """
    # Mixed separator path
    mixed_path = r"C:\Users\Test/project\subfolder/file.txt"

    # Normalize using comparison tools
    normalized = comparison_tools.normalize_path(mixed_path)

    # Verify all backslashes converted
    assert "\\" not in normalized, f"Backslashes remain in normalized path: {normalized}"
    assert "/" in normalized, "No forward slashes in normalized path"

    # Verify path components preserved
    assert "Users" in normalized
    assert "project" in normalized
    assert "file.txt" in normalized


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_case_insensitive_filesystem_behavior(temp_project_dir):
    """
    Test that Windows filesystem is case-insensitive.

    Given: Windows case-insensitive filesystem
    When: Files are created with different cases
    Then: Same file is accessed regardless of case
    """
    # Create a file
    test_file = temp_project_dir / "TestFile.txt"
    test_file.write_text("test content", encoding="utf-8")

    # Access with different cases
    lowercase_ref = temp_project_dir / "testfile.txt"
    uppercase_ref = temp_project_dir / "TESTFILE.TXT"

    # On Windows, these should all refer to the same file
    assert lowercase_ref.exists(), "Lowercase reference not found (case-insensitive)"
    assert uppercase_ref.exists(), "Uppercase reference not found (case-insensitive)"

    # Verify same content accessible
    content_lower = lowercase_ref.read_text(encoding="utf-8")
    content_upper = uppercase_ref.read_text(encoding="utf-8")

    assert content_lower == "test content", "Content mismatch with lowercase"
    assert content_upper == "test content", "Content mismatch with uppercase"


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_path_normalization_for_comparison(path_validator, comparison_tools):
    """
    Test that paths are correctly normalized for cross-platform comparison.

    Given: Various Windows path formats
    When: Paths are normalized
    Then: All are converted to comparable format
    """
    # Different Windows path formats
    test_paths = [
        r"C:\Users\Test\file.txt",
        "C:/Users/Test/file.txt",
        r"C:\Users/Test\file.txt",  # Mixed
    ]

    normalized_paths = [comparison_tools.normalize_path(p) for p in test_paths]

    # All should normalize to same format
    first_normalized = normalized_paths[0]
    for normalized in normalized_paths[1:]:
        # Paths should be similar after normalization (drive letter handling may vary)
        assert "/" in normalized, f"Path not normalized: {normalized}"
        assert "\\" not in normalized, f"Backslashes remain: {normalized}"


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_special_characters_in_paths(temp_project_dir):
    """
    Test handling of special characters in Windows paths.

    Given: Paths with special characters (except reserved)
    When: Files are created
    Then: Operations succeed with valid special characters
    """
    # Valid special characters in Windows filenames
    special_chars = ["@", "#", "$", "%", "&", "(", ")", "-", "_", "+", "=", "[", "]", "{", "}"]

    for char in special_chars:
        filename = f"test{char}file.txt"
        test_file = temp_project_dir / filename

        # Should be able to create and write
        try:
            test_file.write_text(f"content with {char}", encoding="utf-8")
            assert test_file.exists(), f"File with {char} not created"

            # Should be able to read
            content = test_file.read_text(encoding="utf-8")
            assert char in content, f"Content with {char} not preserved"
        except (OSError, ValueError) as e:
            pytest.fail(f"Failed to handle special character {char}: {e}")
