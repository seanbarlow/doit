"""E2E tests for macOS-specific path handling."""

import os
import subprocess
import tempfile
from pathlib import Path
import pytest


@pytest.mark.macos
@pytest.mark.e2e
@pytest.mark.ci
def test_paths_with_spaces(tmp_path, macos_test_env):
    """Test handling of paths with spaces on macOS."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    path_with_spaces = tmp_path / "my test directory"
    path_with_spaces.mkdir()

    test_file = path_with_spaces / "file.txt"
    test_file.write_text("Content\n")

    assert test_file.exists(), "File in path with spaces not created"


@pytest.mark.macos
@pytest.mark.e2e
def test_applications_paths(macos_test_env, macos_path_samples):
    """Test /Applications path handling."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    applications_path = Path("/Applications")
    assert applications_path.exists(), "/Applications directory not found"
    assert applications_path.is_dir(), "/Applications is not a directory"


@pytest.mark.macos
@pytest.mark.e2e
def test_library_paths(macos_test_env, macos_path_samples):
    """Test ~/Library path handling."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    library_path = Path(macos_path_samples["library"])
    assert library_path.exists(), "~/Library directory not found"
    assert library_path.is_dir(), "~/Library is not a directory"


@pytest.mark.macos
@pytest.mark.e2e
def test_tmpdir_structure(macos_test_env):
    """Test TMPDIR structure on macOS."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    tmpdir = tempfile.gettempdir()
    assert tmpdir, "TMPDIR not set"
    assert os.path.exists(tmpdir), f"TMPDIR {tmpdir} doesn't exist"


@pytest.mark.macos
@pytest.mark.e2e
def test_private_tmp_handling(macos_test_env):
    """Test /private/tmp handling on macOS."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    private_tmp = Path("/private/tmp")
    if private_tmp.exists():
        assert private_tmp.is_dir(), "/private/tmp is not a directory"


@pytest.mark.macos
@pytest.mark.e2e
@pytest.mark.unicode
def test_unicode_in_paths(tmp_path, macos_test_env):
    """Test Unicode characters in paths on macOS."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    unicode_dir = tmp_path / "café"
    unicode_dir.mkdir()

    test_file = unicode_dir / "tëst.txt"
    test_file.write_text("Content\n")

    assert test_file.exists(), "File with Unicode in path not created"
