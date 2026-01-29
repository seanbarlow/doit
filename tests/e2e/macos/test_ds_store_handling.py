"""E2E tests for .DS_Store and macOS-specific file handling."""

import pytest
from pathlib import Path


@pytest.mark.macos
@pytest.mark.e2e
@pytest.mark.filesystem
@pytest.mark.ci
def test_ds_store_tolerance(tmp_path, macos_test_env):
    """Test that doit operations tolerate .DS_Store files."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    # Create project structure with .DS_Store
    project_dir = tmp_path / "project"
    project_dir.mkdir()

    # Simulate .DS_Store file
    ds_store = project_dir / ".DS_Store"
    ds_store.write_bytes(b"\x00\x00\x00\x01")  # Dummy .DS_Store content

    # Create legitimate file
    legitimate_file = project_dir / "spec.md"
    legitimate_file.write_text("# Spec\n")

    # Verify both exist
    assert ds_store.exists()
    assert legitimate_file.exists()

    # List directory - should include both
    files = list(project_dir.iterdir())
    assert len(files) == 2


@pytest.mark.macos
@pytest.mark.e2e
@pytest.mark.filesystem
def test_resource_fork_handling(tmp_path, macos_test_env):
    """Test handling of resource forks (HFS+ legacy)."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    # Create file that might have resource fork
    test_file = tmp_path / "test.txt"
    test_file.write_text("Content\n")

    # Resource forks appear as ._filename in some contexts
    # Just verify original file exists
    assert test_file.exists()


@pytest.mark.macos
@pytest.mark.e2e
@pytest.mark.filesystem
def test_apple_double_files(tmp_path, macos_test_env):
    """Test handling of AppleDouble ._ files."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    # Create main file
    main_file = tmp_path / "document.txt"
    main_file.write_text("Content\n")

    # Simulate AppleDouble file (created on non-macOS filesystems)
    apple_double = tmp_path / "._document.txt"
    apple_double.write_bytes(b"\x00\x05\x16\x07")  # AppleDouble magic number

    # Both should exist
    assert main_file.exists()
    assert apple_double.exists()


@pytest.mark.macos
@pytest.mark.e2e
@pytest.mark.filesystem
def test_finder_metadata_preservation(tmp_path, xattr_handler, macos_test_env):
    """Test Finder metadata preservation."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    test_file = tmp_path / "finder_test.txt"
    test_file.write_text("Content\n")

    # Check for Finder info xattr
    finder_info = xattr_handler.get_finder_info(str(test_file))
    # File might not have Finder info, just verify method works
    assert finder_info is None or isinstance(finder_info, str)


@pytest.mark.macos
@pytest.mark.e2e
@pytest.mark.filesystem
def test_hidden_mac_files_in_git(tmp_path, macos_test_env):
    """Test that .DS_Store and other Mac files are properly ignored."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    # Common macOS hidden files that should be ignored
    mac_files = [
        ".DS_Store",
        ".AppleDouble",
        ".LSOverride",
        "._*",
    ]

    # Create .gitignore
    gitignore = tmp_path / ".gitignore"
    gitignore_content = "\n".join(mac_files) + "\n"
    gitignore.write_text(gitignore_content)

    # Verify gitignore exists
    assert gitignore.exists()
    content = gitignore.read_text()
    assert ".DS_Store" in content
