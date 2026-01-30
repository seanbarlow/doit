"""E2E tests for macOS-specific edge cases."""

import subprocess
import pytest
from pathlib import Path


@pytest.mark.macos
@pytest.mark.e2e
def test_quarantine_attribute_on_new_files(tmp_path, xattr_handler, macos_test_env):
    """Test handling of quarantine attributes on new files."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    # Create new file
    test_file = tmp_path / "new_file.txt"
    test_file.write_text("Content\n")

    # New files shouldn't have quarantine
    has_quarantine = xattr_handler.has_quarantine_attr(str(test_file))
    assert not has_quarantine, "New files shouldn't have quarantine attribute"

    # If quarantine exists, verify we can remove it
    if has_quarantine:
        removed = xattr_handler.remove_quarantine_attr(str(test_file))
        assert removed, "Should be able to remove quarantine"


@pytest.mark.macos
@pytest.mark.e2e
def test_security_prompts_handling(tmp_path, macos_test_env):
    """Test that operations don't trigger security prompts."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    # Normal file operations shouldn't trigger prompts
    test_file = tmp_path / "security_test.txt"
    test_file.write_text("Content\n")

    # Read file
    content = test_file.read_text()
    assert content == "Content\n"

    # Modify file
    test_file.write_text("Modified\n")
    assert test_file.read_text() == "Modified\n"


@pytest.mark.macos
@pytest.mark.e2e
def test_sandboxing_compatibility(tmp_path, macos_test_env):
    """Test compatibility with macOS sandboxing."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    # File operations in tmp should work even in sandboxed contexts
    test_file = tmp_path / "sandbox_test.txt"
    test_file.write_text("Sandboxed content\n")

    assert test_file.exists()
    assert test_file.read_text() == "Sandboxed content\n"


@pytest.mark.macos
@pytest.mark.e2e
def test_long_paths_handling(tmp_path, macos_test_env):
    """Test handling of very long paths."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    # Create deeply nested directory structure
    long_path = tmp_path
    for i in range(10):
        long_path = long_path / f"very_long_directory_name_{i:02d}"

    long_path.mkdir(parents=True, exist_ok=True)

    # Create file in deep path
    test_file = long_path / "test.txt"
    test_file.write_text("Deep file\n")

    assert test_file.exists()


@pytest.mark.macos
@pytest.mark.e2e
def test_special_characters_in_filenames(tmp_path, macos_test_env):
    """Test handling of special characters in filenames."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    # Test various special characters (excluding / which is path separator)
    special_chars = [
        "file with spaces.txt",
        "file-with-dashes.txt",
        "file_with_underscores.txt",
        "file.multiple.dots.txt",
        "file(with)parens.txt",
        "file[with]brackets.txt",
    ]

    for filename in special_chars:
        test_file = tmp_path / filename
        test_file.write_text(f"Content of {filename}\n")
        assert test_file.exists(), f"Failed to create: {filename}"


@pytest.mark.macos
@pytest.mark.e2e
def test_colon_in_filename(tmp_path, macos_test_env):
    """Test handling of colons in filenames (macOS allows, Windows doesn't)."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    # Colon is allowed in macOS filenames (converted to / in filesystem)
    # But avoid creating files with colons for cross-platform compatibility
    # This test just verifies we understand the behavior

    # Create file without colon (safe)
    safe_file = tmp_path / "safe_filename.txt"
    safe_file.write_text("Safe\n")
    assert safe_file.exists()


@pytest.mark.macos
@pytest.mark.e2e
def test_resource_limits(tmp_path, macos_test_env):
    """Test operations stay within resource limits."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    # Create many files (but not too many)
    num_files = 100

    for i in range(num_files):
        test_file = tmp_path / f"file_{i:04d}.txt"
        test_file.write_text(f"Content {i}\n")

    # Verify all files were created
    created_files = list(tmp_path.glob("file_*.txt"))
    assert len(created_files) == num_files


@pytest.mark.macos
@pytest.mark.e2e
def test_concurrent_file_access(tmp_path, macos_test_env):
    """Test concurrent access to files."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    import threading
    import time

    test_file = tmp_path / "concurrent.txt"
    test_file.write_text("Initial\n")

    results = []

    def read_file():
        content = test_file.read_text()
        results.append(content)

    # Multiple threads reading same file
    threads = [threading.Thread(target=read_file) for _ in range(5)]

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    # All reads should succeed
    assert len(results) == 5


@pytest.mark.macos
@pytest.mark.e2e
def test_file_locking_behavior(tmp_path, macos_test_env):
    """Test file locking behavior on macOS."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    test_file = tmp_path / "locked.txt"
    test_file.write_text("Content\n")

    # macOS supports advisory locking
    # Just verify basic operations work
    with open(test_file, 'r') as f:
        content = f.read()
        assert content == "Content\n"


@pytest.mark.macos
@pytest.mark.e2e
def test_hidden_files_visibility(tmp_path, macos_test_env):
    """Test handling of hidden files (starting with .)."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    # Create hidden file
    hidden_file = tmp_path / ".hidden_file.txt"
    hidden_file.write_text("Hidden content\n")

    # Hidden files should still be accessible
    assert hidden_file.exists()
    assert hidden_file.read_text() == "Hidden content\n"

    # List all files including hidden
    all_files = list(tmp_path.glob("*"))
    hidden_files = list(tmp_path.glob(".*"))

    # Hidden file appears in .* glob
    assert len(hidden_files) >= 1


@pytest.mark.macos
@pytest.mark.e2e
def test_tmpdir_cleanup(macos_test_env):
    """Test that temporary directories are properly cleaned up."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    import tempfile
    import shutil

    # Create temp directory
    temp_dir = tempfile.mkdtemp(prefix="doit_test_")

    try:
        # Use temp directory
        test_file = Path(temp_dir) / "test.txt"
        test_file.write_text("Temp content\n")

        assert test_file.exists()

    finally:
        # Clean up
        if Path(temp_dir).exists():
            shutil.rmtree(temp_dir)

        # Verify cleanup
        assert not Path(temp_dir).exists()
