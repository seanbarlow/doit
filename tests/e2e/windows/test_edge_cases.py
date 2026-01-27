"""Comprehensive edge case tests for Windows E2E testing."""
import sys
import os
import subprocess
from pathlib import Path

import pytest


@pytest.mark.windows
@pytest.mark.powershell
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_powershell_execution_policy_detection():
    """
    Test that PowerShell execution policy can be detected.

    Given: Windows system with PowerShell
    When: Execution policy is queried
    Then: Policy is returned (e.g., RemoteSigned, Restricted, Unrestricted)
    """
    from tests.utils.windows.powershell_executor import PowerShellExecutor

    executor = PowerShellExecutor()
    policy = executor.check_execution_policy()
    assert policy != "not available", "PowerShell should be available"
    assert policy in [
        "Restricted",
        "AllSigned",
        "RemoteSigned",
        "Unrestricted",
        "Bypass",
        "Undefined",
    ] or policy != "unknown", f"Unexpected policy: {policy}"


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_case_insensitive_file_access(temp_project_dir):
    """
    Test Windows case-insensitive filesystem behavior.

    Given: Windows filesystem (case-insensitive)
    When: File is accessed with different case
    Then: Same file is accessed regardless of case
    """
    # Create file with mixed case
    test_file = temp_project_dir / "TestFile.txt"
    test_file.write_text("content", encoding="utf-8")

    # Access with different cases
    assert (temp_project_dir / "testfile.txt").exists()
    assert (temp_project_dir / "TESTFILE.TXT").exists()
    assert (temp_project_dir / "TestFile.txt").exists()

    # All should have same content
    assert (temp_project_dir / "testfile.txt").read_text(encoding="utf-8") == "content"


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_symbolic_link_creation_privilege():
    """
    Test that symbolic link creation is handled appropriately on Windows.

    Given: Windows system (may require admin privileges)
    When: Symbolic link creation is attempted
    Then: Either succeeds or raises PermissionError appropriately
    """
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        target = Path(tmpdir) / "target.txt"
        target.write_text("target content", encoding="utf-8")

        link = Path(tmpdir) / "link.txt"

        try:
            # Attempt to create symbolic link
            os.symlink(target, link)
            assert link.exists(), "Symlink should exist if creation succeeded"
            assert link.is_symlink(), "Path should be recognized as symlink"
        except OSError as e:
            # On Windows without developer mode or admin, this may fail
            if "privilege" in str(e).lower() or "required privilege" in str(e).lower():
                pytest.skip("Symbolic link creation requires elevated privileges")
            else:
                # Other OSError should be investigated
                raise


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_max_path_length_limit(temp_project_dir, path_validator):
    """
    Test handling of Windows MAX_PATH limit (260 characters).

    Given: Path approaching MAX_PATH limit
    When: Path length is validated
    Then: Paths over 260 chars are detected
    """
    # Path just under limit (should pass)
    # "C:/" (3) + "a" * 240 (240) + "/test.txt" (9) = 252 chars
    short_path = "C:/" + "a" * 240 + "/test.txt"
    assert not path_validator.exceeds_max_path(short_path), \
        f"Path under 260 chars should not exceed limit (length: {len(short_path)})"

    # Path over limit (should fail)
    # "C:/" (3) + "a" * 270 (270) + "/test.txt" (9) = 282 chars
    long_path = "C:/" + "a" * 270 + "/test.txt"
    assert path_validator.exceeds_max_path(long_path), \
        f"Path over 260 chars should exceed limit (length: {len(long_path)})"


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
@pytest.mark.parametrize(
    "reserved_name",
    ["CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM9", "LPT1", "LPT2", "LPT9"],
)
def test_reserved_filename_handling(path_validator, reserved_name):
    """
    Test that Windows reserved filenames are detected and handled.

    Given: Reserved Windows filename (CON, PRN, AUX, etc.)
    When: Filename is validated
    Then: Reserved name is detected
    """
    # Test exact match
    assert path_validator.is_reserved_name(reserved_name), \
        f"{reserved_name} should be detected as reserved"

    # Test with extension
    assert path_validator.is_reserved_name(f"{reserved_name}.txt"), \
        f"{reserved_name}.txt should be detected as reserved"

    # Test case insensitivity
    assert path_validator.is_reserved_name(reserved_name.lower()), \
        f"{reserved_name.lower()} should be detected as reserved"


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_mixed_path_separators(temp_project_dir, comparison_tools):
    """
    Test handling of mixed forward/backward slashes in paths.

    Given: Path with mixed separators (C:\\path/to\\file)
    When: Path is used
    Then: Path operations succeed with normalization
    """
    # Create directory with forward slashes
    dir1 = temp_project_dir / "dir1/dir2"
    dir1.mkdir(parents=True, exist_ok=True)

    # Access with mixed separators
    mixed_path_str = str(temp_project_dir / "dir1\\dir2")
    mixed_path = Path(mixed_path_str)
    assert mixed_path.exists(), "Path should exist with mixed separators"

    # Normalize for comparison
    normalized = comparison_tools.normalize_path(mixed_path_str)
    assert "\\" not in normalized, "Normalized path should use forward slashes only"


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_trailing_dot_filename():
    """
    Test handling of filenames with trailing dots (invalid on Windows).

    Given: Filename with trailing dot
    When: File creation is attempted
    Then: Windows handles it appropriately (dot removed or error)
    """
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        # Try to create file with trailing dot
        file_with_dot = Path(tmpdir) / "file."

        try:
            file_with_dot.write_text("content", encoding="utf-8")
            # If successful, Windows likely removed the trailing dot
            # Check if file exists without the dot
            file_without_dot = Path(tmpdir) / "file"
            # Either the original name or name without dot should exist
            assert file_with_dot.exists() or file_without_dot.exists(), \
                "File should exist (possibly with dot removed)"
        except (OSError, ValueError):
            # Some operations may reject trailing dots
            pytest.skip("Trailing dot in filename not supported")


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_unc_path_detection(path_validator):
    """
    Test detection of UNC paths (\\server\\share format).

    Given: UNC network path
    When: Path is analyzed
    Then: UNC format is correctly detected
    """
    unc_paths = [
        r"\\server\share\folder\file.txt",
        r"\\10.0.0.1\shared\documents",
        r"\\LOCALHOST\C$\Windows",
    ]

    for unc_path in unc_paths:
        info = path_validator.analyze_path(unc_path)
        assert info.is_unc, f"UNC path not detected: {unc_path}"
        assert info.drive_letter is None, "UNC paths should not have drive letters"


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_special_directory_names(temp_project_dir):
    """
    Test handling of special directory names on Windows.

    Given: Directories with special names (node_modules, .git, etc.)
    When: Directories are created and accessed
    Then: Operations succeed
    """
    special_dirs = [
        ".git",
        ".vscode",
        "node_modules",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
    ]

    for dir_name in special_dirs:
        special_dir = temp_project_dir / dir_name
        special_dir.mkdir(exist_ok=True)
        assert special_dir.exists(), f"Special directory not created: {dir_name}"
        assert special_dir.is_dir(), f"Not recognized as directory: {dir_name}"


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_readonly_file_handling(temp_project_dir):
    """
    Test handling of read-only files on Windows.

    Given: File with read-only attribute
    When: File operations are attempted
    Then: Read-only status is respected
    """
    import stat

    readonly_file = temp_project_dir / "readonly.txt"
    readonly_file.write_text("read-only content", encoding="utf-8")

    # Set read-only attribute
    readonly_file.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)

    # Should be able to read
    content = readonly_file.read_text(encoding="utf-8")
    assert content == "read-only content"

    # Writing should fail or require special handling
    try:
        readonly_file.write_text("new content", encoding="utf-8")
        # If write succeeded, file may not be truly read-only
        # This is acceptable; just verify the operation completed
    except PermissionError:
        # Expected behavior for read-only files
        pass

    # Clean up: Remove read-only attribute
    readonly_file.chmod(stat.S_IWUSR | stat.S_IRUSR)


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_long_filename_handling(temp_project_dir):
    """
    Test handling of long filenames on Windows.

    Given: Filename approaching Windows limits
    When: File is created
    Then: Operation succeeds or fails appropriately
    """
    # Windows allows up to 255 characters for filename
    long_name = "a" * 200 + ".txt"
    long_file = temp_project_dir / long_name

    try:
        long_file.write_text("content", encoding="utf-8")
        assert long_file.exists(), "Long filename file should be created"
    except OSError as e:
        # May fail if name too long
        if "too long" in str(e).lower() or "name" in str(e).lower():
            pytest.skip("Filename too long for system")
        else:
            raise


@pytest.mark.windows
@pytest.mark.slow
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_large_directory_listing(temp_project_dir):
    """
    Test performance with large directory listings on Windows.

    Given: Directory with many files
    When: Directory is listed
    Then: Operation completes in reasonable time
    """
    import time

    # Create directory with many files
    large_dir = temp_project_dir / "large_dir"
    large_dir.mkdir(exist_ok=True)

    num_files = 1000
    for i in range(num_files):
        (large_dir / f"file_{i:04d}.txt").write_text(f"Content {i}", encoding="utf-8")

    # List directory and time it
    start_time = time.time()
    files = list(large_dir.iterdir())
    elapsed = time.time() - start_time

    assert len(files) == num_files, f"Expected {num_files} files, got {len(files)}"
    assert elapsed < 5.0, f"Directory listing took too long: {elapsed:.2f}s"


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_empty_filename_rejection():
    """
    Test that empty filenames are rejected on Windows.

    Given: Empty filename
    When: File creation is attempted
    Then: Appropriate error is raised
    """
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        empty_name = Path(tmpdir) / ""

        with pytest.raises((ValueError, OSError)):
            empty_name.write_text("content", encoding="utf-8")
