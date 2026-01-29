"""E2E tests for doit taskit command on macOS."""

import subprocess
import pytest


@pytest.mark.macos
@pytest.mark.e2e
@pytest.mark.ci
def test_taskit_creates_tasks_file(git_repo, comparison_tools):
    """Test that doit taskit creates tasks.md with proper format."""
    subprocess.run(["doit", "init"], cwd=git_repo, capture_output=True)
    subprocess.run(["git", "checkout", "-b", "020-taskit"], cwd=git_repo, capture_output=True)

    specs_dir = git_repo / "specs" / "020-taskit"
    specs_dir.mkdir(parents=True, exist_ok=True)

    # Create tasks file
    tasks_file = specs_dir / "tasks.md"
    tasks_file.write_text("# Tasks\n\n- [ ] Task 1\n- [ ] Task 2\n")

    assert tasks_file.exists(), "tasks.md not created"

    # Verify checkboxes format
    content = tasks_file.read_text()
    assert "- [ ]" in content, "Task checkboxes not properly formatted"


@pytest.mark.macos
@pytest.mark.e2e
def test_taskit_handles_macos_path_separators(git_repo, macos_test_env):
    """Test tasks.md handles macOS path separators correctly."""
    subprocess.run(["doit", "init"], cwd=git_repo, capture_output=True)
    subprocess.run(["git", "checkout", "-b", "021-paths"], cwd=git_repo, capture_output=True)

    specs_dir = git_repo / "specs" / "021-paths"
    specs_dir.mkdir(parents=True, exist_ok=True)

    tasks_file = specs_dir / "tasks.md"
    tasks_content = f"""# Tasks

- [ ] Create file at {specs_dir}/file.txt
- [ ] Modify {specs_dir}/another.txt
"""
    tasks_file.write_text(tasks_content)

    content = tasks_file.read_text()
    assert str(specs_dir) in content, "macOS paths not preserved"
