"""E2E tests for symbolic links on macOS."""

import pytest
from pathlib import Path


@pytest.mark.macos
@pytest.mark.e2e
@pytest.mark.filesystem
@pytest.mark.ci
def test_symlink_creation_in_project(tmp_path, macos_test_env):
    """Test symlink creation in project directories."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    # Create source file
    source_file = tmp_path / "source.txt"
    source_file.write_text("Source content\n")

    # Create symlink
    symlink_file = tmp_path / "link.txt"
    symlink_file.symlink_to(source_file)

    # Verify symlink works
    assert symlink_file.exists(), "Symlink doesn't resolve"
    assert symlink_file.is_symlink(), "Not recognized as symlink"
    assert symlink_file.read_text() == source_file.read_text()


@pytest.mark.macos
@pytest.mark.e2e
@pytest.mark.filesystem
def test_symlink_resolution_in_doit_commands(tmp_path, macos_test_env):
    """Test symlink resolution in doit command paths."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    # Create real directory
    real_dir = tmp_path / "real_specs"
    real_dir.mkdir()

    # Create symlink to directory
    link_dir = tmp_path / "specs"
    link_dir.symlink_to(real_dir)

    # Create file through symlink
    test_file = link_dir / "spec.md"
    test_file.write_text("# Spec\n")

    # Verify file exists in real location
    real_file = real_dir / "spec.md"
    assert real_file.exists(), "File not created in real location"
    assert test_file.read_text() == real_file.read_text()


@pytest.mark.macos
@pytest.mark.e2e
@pytest.mark.filesystem
def test_circular_symlink_handling(tmp_path, macos_test_env):
    """Test handling of circular symlinks."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    # Create circular symlinks
    link1 = tmp_path / "link1"
    link2 = tmp_path / "link2"

    link1.symlink_to(link2)
    link2.symlink_to(link1)

    # Verify they exist as symlinks but don't resolve
    assert link1.is_symlink()
    assert link2.is_symlink()
    assert not link1.exists()  # Circular, so doesn't resolve
    assert not link2.exists()


@pytest.mark.macos
@pytest.mark.e2e
@pytest.mark.filesystem
def test_symlink_vs_hard_link_behavior(tmp_path, macos_test_env):
    """Test difference between symlinks and hard links."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    # Create source file
    source_file = tmp_path / "source.txt"
    source_file.write_text("Original\n")

    # Create symlink
    symlink_file = tmp_path / "symlink.txt"
    symlink_file.symlink_to(source_file)

    # Create hard link
    hardlink_file = tmp_path / "hardlink.txt"
    hardlink_file.hardlink_to(source_file)

    # Verify types
    assert symlink_file.is_symlink()
    assert not hardlink_file.is_symlink()

    # Both should have same content
    assert symlink_file.read_text() == source_file.read_text()
    assert hardlink_file.read_text() == source_file.read_text()


@pytest.mark.macos
@pytest.mark.e2e
@pytest.mark.filesystem
def test_broken_symlink_handling(tmp_path, macos_test_env):
    """Test handling of broken symlinks."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    # Create symlink to non-existent file
    broken_link = tmp_path / "broken.txt"
    target = tmp_path / "nonexistent.txt"
    broken_link.symlink_to(target)

    # Verify it's a symlink but doesn't resolve
    assert broken_link.is_symlink()
    assert not broken_link.exists()  # Target doesn't exist
