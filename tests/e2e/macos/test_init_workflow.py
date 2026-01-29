"""E2E tests for doit init command on macOS.

Tests the initialization workflow including:
- .doit directory creation
- macOS path handling (spaces, ~/Library, etc.)
- LF line ending preservation
- Constitution.md creation
"""

import os
import subprocess
from pathlib import Path

import pytest


@pytest.mark.macos
@pytest.mark.e2e
@pytest.mark.ci
def test_init_creates_doit_directory(temp_project_dir, macos_test_env, comparison_tools):
    """Test that doit init creates .doit directory on macOS."""
    # Run doit init
    result = subprocess.run(
        ["doit", "init"],
        capture_output=True,
        text=True,
        cwd=temp_project_dir
    )

    # Check command succeeded
    assert result.returncode == 0, f"doit init failed: {result.stderr}"

    # Check .doit directory exists
    doit_dir = temp_project_dir / ".doit"
    assert doit_dir.exists(), ".doit directory was not created"
    assert doit_dir.is_dir(), ".doit is not a directory"

    # Check expected subdirectories
    expected_dirs = [
        "memory",
        "templates",
        "scripts",
    ]

    for dir_name in expected_dirs:
        dir_path = doit_dir / dir_name
        assert dir_path.exists(), f".doit/{dir_name} directory was not created"


@pytest.mark.macos
@pytest.mark.e2e
def test_init_handles_macos_paths_with_spaces(tmp_path, macos_test_env):
    """Test that doit init handles macOS paths with spaces correctly."""
    # Create directory with spaces in name
    project_dir = tmp_path / "my project with spaces"
    project_dir.mkdir(parents=True, exist_ok=True)

    # Run doit init
    result = subprocess.run(
        ["doit", "init"],
        capture_output=True,
        text=True,
        cwd=project_dir
    )

    # Check command succeeded
    assert result.returncode == 0, f"doit init failed with spaces in path: {result.stderr}"

    # Check .doit directory exists
    doit_dir = project_dir / ".doit"
    assert doit_dir.exists(), ".doit directory was not created in path with spaces"


@pytest.mark.macos
@pytest.mark.e2e
def test_init_creates_constitution_with_lf_line_endings(temp_project_dir, comparison_tools):
    """Test that constitution.md is created with LF line endings on macOS."""
    # Run doit init
    result = subprocess.run(
        ["doit", "init"],
        capture_output=True,
        text=True,
        cwd=temp_project_dir
    )

    assert result.returncode == 0, f"doit init failed: {result.stderr}"

    # Check constitution.md exists
    constitution_file = temp_project_dir / ".doit" / "memory" / "constitution.md"
    assert constitution_file.exists(), "constitution.md was not created"

    # Check line endings
    line_ending_type = comparison_tools.verify_line_endings(str(constitution_file))
    assert line_ending_type == "LF", f"Expected LF line endings, got {line_ending_type}"


@pytest.mark.macos
@pytest.mark.e2e
def test_init_handles_library_paths(macos_test_env, macos_path_samples):
    """Test that doit init works correctly in ~/Library paths on macOS."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    # Create test directory in temporary location (not actual ~/Library to avoid pollution)
    import tempfile
    with tempfile.TemporaryDirectory(prefix="doit_test_library_") as tmpdir:
        library_style_path = Path(tmpdir) / "Application Support" / "doit_test"
        library_style_path.mkdir(parents=True, exist_ok=True)

        # Run doit init
        result = subprocess.run(
            ["doit", "init"],
            capture_output=True,
            text=True,
            cwd=library_style_path
        )

        # Check command succeeded
        assert result.returncode == 0, f"doit init failed in Library-style path: {result.stderr}"

        # Check .doit directory exists
        doit_dir = library_style_path / ".doit"
        assert doit_dir.exists(), ".doit directory was not created in Library-style path"


@pytest.mark.macos
@pytest.mark.e2e
def test_init_preserves_existing_git_config(temp_project_dir, git_repo):
    """Test that doit init doesn't interfere with existing git configuration."""
    # Use git_repo fixture which already has git initialized
    result = subprocess.run(
        ["doit", "init"],
        capture_output=True,
        text=True,
        cwd=git_repo
    )

    assert result.returncode == 0, f"doit init failed in git repo: {result.stderr}"

    # Check .doit directory was created
    doit_dir = git_repo / ".doit"
    assert doit_dir.exists(), ".doit directory was not created"

    # Check git config is still intact
    git_config_result = subprocess.run(
        ["git", "config", "user.email"],
        capture_output=True,
        text=True,
        cwd=git_repo
    )

    assert git_config_result.returncode == 0, "Git config was corrupted"
    assert "test@example.com" in git_config_result.stdout, "Git user.email was lost"


@pytest.mark.macos
@pytest.mark.e2e
def test_init_creates_all_required_files(temp_project_dir):
    """Test that doit init creates all required files and directories."""
    # Run doit init
    result = subprocess.run(
        ["doit", "init"],
        capture_output=True,
        text=True,
        cwd=temp_project_dir
    )

    assert result.returncode == 0, f"doit init failed: {result.stderr}"

    # Check all required paths exist
    required_paths = [
        ".doit",
        ".doit/memory",
        ".doit/memory/constitution.md",
        ".doit/templates",
        ".doit/scripts",
    ]

    for path_str in required_paths:
        path = temp_project_dir / path_str
        assert path.exists(), f"Required path not created: {path_str}"


@pytest.mark.macos
@pytest.mark.e2e
@pytest.mark.unicode
def test_init_handles_unicode_in_project_path(tmp_path, macos_test_env):
    """Test that doit init handles Unicode characters in project path (NFD normalization)."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS for Unicode normalization testing")

    # Create directory with Unicode characters (using é which has NFD/NFC variants)
    project_dir = tmp_path / "café_project"
    project_dir.mkdir(parents=True, exist_ok=True)

    # Run doit init
    result = subprocess.run(
        ["doit", "init"],
        capture_output=True,
        text=True,
        cwd=project_dir
    )

    # Check command succeeded
    assert result.returncode == 0, f"doit init failed with Unicode in path: {result.stderr}"

    # Check .doit directory exists
    doit_dir = project_dir / ".doit"
    assert doit_dir.exists(), ".doit directory was not created in path with Unicode"


@pytest.mark.macos
@pytest.mark.e2e
def test_init_idempotent(temp_project_dir):
    """Test that running doit init multiple times is safe (idempotent)."""
    # Run doit init first time
    result1 = subprocess.run(
        ["doit", "init"],
        capture_output=True,
        text=True,
        cwd=temp_project_dir
    )

    assert result1.returncode == 0, f"First doit init failed: {result1.stderr}"

    # Run doit init second time
    result2 = subprocess.run(
        ["doit", "init"],
        capture_output=True,
        text=True,
        cwd=temp_project_dir
    )

    # Should succeed or gracefully handle existing .doit directory
    assert result2.returncode in (0, 1), f"Second doit init had unexpected error: {result2.stderr}"

    # Check .doit directory still exists and is intact
    doit_dir = temp_project_dir / ".doit"
    assert doit_dir.exists(), ".doit directory was removed on second init"

    constitution_file = doit_dir / "memory" / "constitution.md"
    assert constitution_file.exists(), "constitution.md was removed on second init"
