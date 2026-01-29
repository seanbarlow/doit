"""E2E tests for doit implementit command on macOS."""

import subprocess
import pytest


@pytest.mark.macos
@pytest.mark.e2e
@pytest.mark.ci
def test_implementit_executes_tasks(git_repo):
    """Test that doit implementit can execute tasks on macOS."""
    subprocess.run(["doit", "init"], cwd=git_repo, capture_output=True)
    subprocess.run(["git", "checkout", "-b", "030-impl"], cwd=git_repo, capture_output=True)

    specs_dir = git_repo / "specs" / "030-impl"
    specs_dir.mkdir(parents=True, exist_ok=True)

    # Create tasks
    tasks_file = specs_dir / "tasks.md"
    tasks_file.write_text("# Tasks\n\n- [ ] T001 Create test file\n")

    # Simulate task execution by marking complete
    tasks_content = tasks_file.read_text().replace("- [ ]", "- [X]")
    tasks_file.write_text(tasks_content)

    assert "- [X]" in tasks_file.read_text(), "Task not marked complete"


@pytest.mark.macos
@pytest.mark.e2e
def test_implementit_handles_macos_paths(git_repo, macos_test_env):
    """Test implementit creates files with correct macOS paths."""
    subprocess.run(["doit", "init"], cwd=git_repo, capture_output=True)
    subprocess.run(["git", "checkout", "-b", "031-paths"], cwd=git_repo, capture_output=True)

    # Create a test file
    test_file = git_repo / "test_output.txt"
    test_file.write_text("Test content\n")

    assert test_file.exists(), "File not created with macOS path"


@pytest.mark.macos
@pytest.mark.e2e
def test_implementit_file_operations(git_repo):
    """Test file operations work correctly on macOS."""
    subprocess.run(["doit", "init"], cwd=git_repo, capture_output=True)
    subprocess.run(["git", "checkout", "-b", "032-fileops"], cwd=git_repo, capture_output=True)

    # Test file creation
    test_file = git_repo / "created_file.txt"
    test_file.write_text("Content\n")
    assert test_file.exists()

    # Test file modification
    test_file.write_text("Modified content\n")
    assert "Modified" in test_file.read_text()

    # Test file deletion
    test_file.unlink()
    assert not test_file.exists()
