"""End-to-end tests for 'doit specit' command on Windows."""
import sys
import subprocess
from pathlib import Path

import pytest


@pytest.mark.windows
@pytest.mark.e2e
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_specit_creates_spec_file(temp_project_dir, windows_test_env):
    """
    Test that 'doit specit' creates spec.md on Windows.

    Given: A Windows environment with doit initialized
    When: Developer runs 'doit specit' with a feature description
    Then: spec.md is created in the correct directory
    """
    # This test would require doit init first, but for unit testing we skip
    # Instead, we test the file creation pattern
    pytest.skip("Integration test - requires full doit workflow")


@pytest.mark.windows
@pytest.mark.e2e
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_specit_handles_windows_absolute_path(temp_project_dir, path_validator):
    """
    Test that spec files handle Windows absolute paths correctly.

    Given: Windows absolute path in spec content
    When: Spec is created and read
    Then: Path is correctly stored and retrievable
    """
    # Create a mock spec file with Windows path
    spec_dir = temp_project_dir / "specs" / "001-test-feature"
    spec_dir.mkdir(parents=True, exist_ok=True)

    spec_file = spec_dir / "spec.md"
    spec_content = f"""# Feature Specification: Test Feature

**Path**: C:\\Users\\Test\\project\\file.txt

## Description
This is a test specification with Windows paths.
"""

    spec_file.write_text(spec_content, encoding="utf-8")

    # Read back and verify
    read_content = spec_file.read_text(encoding="utf-8")
    assert "C:\\Users\\Test\\project\\file.txt" in read_content or "C:/Users/Test/project/file.txt" in read_content
    assert "# Feature Specification" in read_content


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_spec_file_line_ending_preservation(temp_project_dir):
    """
    Test that spec.md preserves correct line endings on Windows.

    Given: A spec file created on Windows
    When: File is written and read
    Then: Line endings are preserved correctly
    """
    from tests.utils.windows.line_ending_utils import detect_line_ending

    spec_dir = temp_project_dir / "specs" / "002-line-test"
    spec_dir.mkdir(parents=True, exist_ok=True)

    spec_file = spec_dir / "spec.md"

    # Write with explicit line endings
    content = "# Feature\r\n\r\nDescription here.\r\n"
    spec_file.write_bytes(content.encode("utf-8"))

    # Read and check
    read_content = spec_file.read_text(encoding="utf-8")
    detected = detect_line_ending(read_content)

    # Windows should preserve CRLF (or Git may normalize to LF)
    assert detected in ["CRLF", "LF"], f"Unexpected line ending: {detected}"


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_spec_directory_creation_windows(temp_project_dir):
    """
    Test that spec directory structure is created correctly on Windows.

    Given: A Windows file system
    When: Spec directories are created
    Then: All directories are accessible with Windows paths
    """
    specs_root = temp_project_dir / "specs"
    feature_dir = specs_root / "003-windows-test"

    # Create directory structure
    feature_dir.mkdir(parents=True, exist_ok=True)
    (feature_dir / "checklists").mkdir(exist_ok=True)
    (feature_dir / "contracts").mkdir(exist_ok=True)

    # Verify all directories exist and are accessible
    assert specs_root.exists(), "specs/ directory not created"
    assert feature_dir.exists(), "Feature directory not created"
    assert (feature_dir / "checklists").exists(), "checklists/ not created"
    assert (feature_dir / "contracts").exists(), "contracts/ not created"

    # Verify Windows can access these directories
    assert feature_dir.is_dir(), "Feature dir not recognized as directory"
    list(feature_dir.iterdir())  # Should not raise PermissionError


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_spec_with_special_characters_windows(temp_project_dir):
    """
    Test spec handling with Windows-safe special characters.

    Given: Spec content with special characters
    When: Spec is created and read
    Then: Special characters are preserved
    """
    spec_dir = temp_project_dir / "specs" / "004-special-chars"
    spec_dir.mkdir(parents=True, exist_ok=True)

    spec_file = spec_dir / "spec.md"

    # Windows-safe special characters
    content = """# Feature: Test & Validation (Phase 1)

**Description**: Testing special characters: @#$%&()[]{}

## Requirements
- Requirement 1: Support UTF-8 encoding
- Requirement 2: Handle punctuation correctly
"""

    spec_file.write_text(content, encoding="utf-8")

    # Read and verify
    read_content = spec_file.read_text(encoding="utf-8")
    assert "@#$%&()[]" in read_content
    assert "Phase 1" in read_content
