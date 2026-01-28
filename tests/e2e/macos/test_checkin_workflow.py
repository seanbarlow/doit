"""E2E tests for doit checkin command on macOS."""

import subprocess
import pytest


@pytest.mark.macos
@pytest.mark.e2e
@pytest.mark.ci
def test_checkin_creates_commits(git_repo):
    """Test that doit checkin creates git commits on macOS."""
    subprocess.run(["doit", "init"], cwd=git_repo, capture_output=True)
    subprocess.run(["git", "checkout", "-b", "040-checkin"], cwd=git_repo, capture_output=True)

    # Create and stage a file
    test_file = git_repo / "test.txt"
    test_file.write_text("Test content\n")
    subprocess.run(["git", "add", "test.txt"], cwd=git_repo, capture_output=True)

    # Create commit
    result = subprocess.run(
        ["git", "commit", "-m", "Test commit"],
        cwd=git_repo,
        capture_output=True,
        text=True
    )

    assert result.returncode == 0, f"Commit failed: {result.stderr}"

    # Verify commit exists
    log_result = subprocess.run(
        ["git", "log", "--oneline"],
        cwd=git_repo,
        capture_output=True,
        text=True
    )

    assert "Test commit" in log_result.stdout, "Commit not found in git log"


@pytest.mark.macos
@pytest.mark.e2e
def test_checkin_git_operations_on_macos(git_repo, macos_test_env):
    """Test git operations work correctly on macOS."""
    subprocess.run(["doit", "init"], cwd=git_repo, capture_output=True)

    # Create feature branch
    result = subprocess.run(
        ["git", "checkout", "-b", "041-git-test"],
        cwd=git_repo,
        capture_output=True,
        text=True
    )

    assert result.returncode == 0, f"Branch creation failed: {result.stderr}"

    # Verify branch was created
    branch_result = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=git_repo,
        capture_output=True,
        text=True
    )

    assert "041-git-test" in branch_result.stdout, "Branch not created"


@pytest.mark.macos
@pytest.mark.e2e
def test_checkin_branch_management(git_repo):
    """Test branch management succeeds on macOS."""
    subprocess.run(["doit", "init"], cwd=git_repo, capture_output=True)

    # Create multiple branches
    branches = ["042-branch-1", "042-branch-2", "042-branch-3"]

    for branch in branches:
        subprocess.run(
            ["git", "checkout", "-b", branch],
            cwd=git_repo,
            capture_output=True
        )
        subprocess.run(
            ["git", "checkout", "main"],
            cwd=git_repo,
            capture_output=True
        )

    # List branches
    result = subprocess.run(
        ["git", "branch"],
        cwd=git_repo,
        capture_output=True,
        text=True
    )

    # Debug output if empty
    if not result.stdout:
        stderr_msg = result.stderr if result.stderr else "No stderr"
        pytest.fail(f"git branch returned empty output. stderr: {stderr_msg}, returncode: {result.returncode}")

    for branch in branches:
        assert branch in result.stdout, f"Branch {branch} not found in output: {result.stdout}"
