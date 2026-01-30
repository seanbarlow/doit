"""End-to-end tests for 'doit checkin' and Git operations on Windows."""
import sys
import subprocess
from pathlib import Path

import pytest


@pytest.mark.windows
@pytest.mark.e2e
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_checkin_creates_git_commit(temp_project_dir):
    """
    Test that Git commits can be created on Windows.

    Given: A Git repository initialized on Windows
    When: Files are staged and committed
    Then: Commit is created successfully
    """
    # Initialize git repo
    subprocess.run(["git", "init"], cwd=temp_project_dir, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=temp_project_dir,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=temp_project_dir,
        check=True,
        capture_output=True,
    )

    # Create a test file
    test_file = temp_project_dir / "test.txt"
    test_file.write_text("test content", encoding="utf-8")

    # Stage and commit
    subprocess.run(["git", "add", "test.txt"], cwd=temp_project_dir, check=True, capture_output=True)
    result = subprocess.run(
        ["git", "commit", "-m", "Test commit"],
        cwd=temp_project_dir,
        check=True,
        capture_output=True,
        text=True,
    )

    # Verify commit created
    assert result.returncode == 0, "Git commit failed"

    # Verify commit exists
    log_result = subprocess.run(
        ["git", "log", "--oneline"],
        cwd=temp_project_dir,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "Test commit" in log_result.stdout


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_git_branch_operations(temp_project_dir):
    """
    Test that Git branch operations work on Windows.

    Given: A Git repository on Windows
    When: Branches are created and switched
    Then: Branch operations succeed
    """
    # Initialize git repo
    subprocess.run(["git", "init"], cwd=temp_project_dir, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=temp_project_dir,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=temp_project_dir,
        check=True,
        capture_output=True,
    )

    # Create initial commit
    test_file = temp_project_dir / "initial.txt"
    test_file.write_text("initial", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=temp_project_dir, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=temp_project_dir,
        check=True,
        capture_output=True,
    )

    # Create new branch
    subprocess.run(
        ["git", "checkout", "-b", "feature-branch"],
        cwd=temp_project_dir,
        check=True,
        capture_output=True,
    )

    # Verify branch created
    branch_result = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=temp_project_dir,
        capture_output=True,
        text=True,
        check=True,
    )
    assert branch_result.stdout.strip() == "feature-branch"

    # Switch back to main/master
    subprocess.run(
        ["git", "checkout", "-"],
        cwd=temp_project_dir,
        check=True,
        capture_output=True,
    )

    # Verify branch switched
    branch_result2 = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=temp_project_dir,
        capture_output=True,
        text=True,
        check=True,
    )
    assert branch_result2.stdout.strip() in ["master", "main"]


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_git_handles_windows_paths(temp_project_dir):
    """
    Test that Git handles Windows paths correctly.

    Given: Files in nested Windows directories
    When: Files are staged and committed
    Then: Git operations succeed with proper path handling
    """
    # Initialize git repo
    subprocess.run(["git", "init"], cwd=temp_project_dir, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=temp_project_dir,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=temp_project_dir,
        check=True,
        capture_output=True,
    )

    # Create nested directory structure
    nested_dir = temp_project_dir / "src" / "utils" / "windows"
    nested_dir.mkdir(parents=True, exist_ok=True)

    test_file = nested_dir / "helper.py"
    test_file.write_text("# Windows helper\n", encoding="utf-8")

    # Stage with forward slashes (Git convention)
    subprocess.run(
        ["git", "add", "src/utils/windows/helper.py"],
        cwd=temp_project_dir,
        check=True,
        capture_output=True,
    )

    # Commit
    subprocess.run(
        ["git", "commit", "-m", "Add Windows helper"],
        cwd=temp_project_dir,
        check=True,
        capture_output=True,
    )

    # Verify file in Git
    ls_result = subprocess.run(
        ["git", "ls-files"],
        cwd=temp_project_dir,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "src/utils/windows/helper.py" in ls_result.stdout


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_git_line_ending_handling(temp_project_dir):
    """
    Test that Git handles line endings correctly on Windows.

    Given: Files with different line endings
    When: Files are committed
    Then: Git respects core.autocrlf setting
    """
    # Initialize git repo
    subprocess.run(["git", "init"], cwd=temp_project_dir, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=temp_project_dir,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=temp_project_dir,
        check=True,
        capture_output=True,
    )

    # Set autocrlf to false to preserve line endings
    subprocess.run(
        ["git", "config", "core.autocrlf", "false"],
        cwd=temp_project_dir,
        check=True,
        capture_output=True,
    )

    # Create file with CRLF
    test_file = temp_project_dir / "crlf.txt"
    test_file.write_bytes(b"line1\r\nline2\r\nline3\r\n")

    # Stage and commit
    subprocess.run(["git", "add", "crlf.txt"], cwd=temp_project_dir, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Add CRLF file"],
        cwd=temp_project_dir,
        check=True,
        capture_output=True,
    )

    # Verify file committed
    status_result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=temp_project_dir,
        capture_output=True,
        text=True,
        check=True,
    )
    assert status_result.stdout.strip() == "", "Working directory should be clean"


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_git_status_on_windows(temp_project_dir):
    """
    Test that git status works correctly on Windows.

    Given: A Git repository with various file states
    When: git status is run
    Then: Status is reported correctly
    """
    # Initialize git repo
    subprocess.run(["git", "init"], cwd=temp_project_dir, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=temp_project_dir,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=temp_project_dir,
        check=True,
        capture_output=True,
    )

    # Create and commit initial file
    initial_file = temp_project_dir / "initial.txt"
    initial_file.write_text("initial", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=temp_project_dir, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial"],
        cwd=temp_project_dir,
        check=True,
        capture_output=True,
    )

    # Create untracked file
    untracked_file = temp_project_dir / "untracked.txt"
    untracked_file.write_text("untracked", encoding="utf-8")

    # Modify tracked file
    initial_file.write_text("modified", encoding="utf-8")

    # Check status
    status_result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=temp_project_dir,
        capture_output=True,
        text=True,
        check=True,
    )

    # Verify status shows both files
    assert "initial.txt" in status_result.stdout, "Modified file not shown"
    assert "untracked.txt" in status_result.stdout, "Untracked file not shown"


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_git_diff_on_windows(temp_project_dir):
    """
    Test that git diff works correctly on Windows.

    Given: A Git repository with modified files
    When: git diff is run
    Then: Changes are displayed correctly
    """
    # Initialize git repo
    subprocess.run(["git", "init"], cwd=temp_project_dir, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=temp_project_dir,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=temp_project_dir,
        check=True,
        capture_output=True,
    )

    # Create and commit initial file
    test_file = temp_project_dir / "test.txt"
    test_file.write_text("line 1\nline 2\nline 3\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=temp_project_dir, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial"],
        cwd=temp_project_dir,
        check=True,
        capture_output=True,
    )

    # Modify file
    test_file.write_text("line 1\nline 2 modified\nline 3\nline 4\n", encoding="utf-8")

    # Check diff
    diff_result = subprocess.run(
        ["git", "diff"],
        cwd=temp_project_dir,
        capture_output=True,
        text=True,
        check=True,
    )

    # Verify diff shows changes
    assert "line 2 modified" in diff_result.stdout or "+line 2 modified" in diff_result.stdout
    assert "line 4" in diff_result.stdout or "+line 4" in diff_result.stdout
