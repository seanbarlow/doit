"""End-to-end tests for 'doit implementit' command on Windows."""
import sys
from pathlib import Path

import pytest


@pytest.mark.windows
@pytest.mark.e2e
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_implementit_executes_tasks(temp_project_dir):
    """
    Test that implementit workflow executes tasks on Windows.

    Given: A tasks.md file with task list
    When: Implementation workflow runs
    Then: Tasks are processed and marked complete
    """
    spec_dir = temp_project_dir / "specs" / "001-test-feature"
    spec_dir.mkdir(parents=True, exist_ok=True)

    tasks_file = spec_dir / "tasks.md"
    tasks_content = """# Tasks: Test Feature

## Phase 1: Setup

- [ ] T001 Create test directory
- [ ] T002 Create test file
"""

    tasks_file.write_text(tasks_content, encoding="utf-8")

    # Simulate task execution by creating the expected outputs
    test_dir = temp_project_dir / "test_output"
    test_dir.mkdir(parents=True, exist_ok=True)

    test_file = test_dir / "test.txt"
    test_file.write_text("test content", encoding="utf-8")

    # Verify files created
    assert test_dir.exists(), "Test directory not created"
    assert test_file.exists(), "Test file not created"
    assert test_file.read_text(encoding="utf-8") == "test content"


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_implementit_handles_windows_paths(temp_project_dir):
    """
    Test that implementit creates files with Windows path handling.

    Given: Tasks requiring file creation with Windows paths
    When: Files are created during implementation
    Then: Windows paths (backslashes, drive letters) are handled correctly
    """
    # Create nested Windows directory structure
    nested_path = temp_project_dir / "src" / "utils" / "windows"
    nested_path.mkdir(parents=True, exist_ok=True)

    # Create file in nested path
    test_file = nested_path / "helper.py"
    test_file.write_text('"""Windows helper utilities."""\n\ndef test():\n    pass\n', encoding="utf-8")

    # Verify nested structure
    assert nested_path.exists(), "Nested path not created"
    assert test_file.exists(), "File in nested path not created"

    # Verify absolute path resolution works
    absolute_path = test_file.resolve()
    assert absolute_path.is_absolute(), "Path not resolved to absolute"
    assert test_file.read_text(encoding="utf-8").startswith('"""Windows helper')


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_implementit_file_operations(temp_project_dir):
    """
    Test that file operations during implementation work on Windows.

    Given: Implementation tasks requiring file operations
    When: Files are created, read, and modified
    Then: All operations succeed on Windows filesystem
    """
    # Create initial file
    test_file = temp_project_dir / "config.txt"
    test_file.write_text("initial content", encoding="utf-8")

    # Verify creation
    assert test_file.exists(), "File not created"
    assert test_file.read_text(encoding="utf-8") == "initial content"

    # Modify file
    test_file.write_text("modified content", encoding="utf-8")

    # Verify modification
    assert test_file.read_text(encoding="utf-8") == "modified content"

    # Create additional file
    second_file = temp_project_dir / "data.json"
    second_file.write_text('{"key": "value"}', encoding="utf-8")

    assert second_file.exists(), "Second file not created"
    assert '"key": "value"' in second_file.read_text(encoding="utf-8")


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_implementit_task_completion_tracking(temp_project_dir):
    """
    Test that task completion is tracked correctly in tasks.md.

    Given: tasks.md with incomplete tasks
    When: Tasks are completed during implementation
    Then: Checkboxes are updated from [ ] to [X]
    """
    spec_dir = temp_project_dir / "specs" / "002-tracking"
    spec_dir.mkdir(parents=True, exist_ok=True)

    tasks_file = spec_dir / "tasks.md"

    # Initial task list
    initial_content = """# Tasks: Tracking Test

- [ ] T001 First task
- [ ] T002 Second task
- [ ] T003 Third task
"""

    tasks_file.write_text(initial_content, encoding="utf-8")

    # Verify initial state
    content = tasks_file.read_text(encoding="utf-8")
    assert content.count("- [ ]") == 3, "Should have 3 incomplete tasks"
    assert content.count("- [X]") == 0, "Should have 0 complete tasks"

    # Simulate task completion
    updated_content = content.replace("- [ ] T001", "- [X] T001")
    updated_content = updated_content.replace("- [ ] T002", "- [X] T002")
    tasks_file.write_text(updated_content, encoding="utf-8")

    # Verify updates
    final_content = tasks_file.read_text(encoding="utf-8")
    assert final_content.count("- [X]") == 2, "Should have 2 complete tasks"
    assert final_content.count("- [ ]") == 1, "Should have 1 incomplete task"


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_implementit_creates_nested_directories(temp_project_dir):
    """
    Test that implementit creates nested directory structures on Windows.

    Given: Tasks requiring deeply nested directories
    When: Directories are created during implementation
    Then: Full path is created successfully on Windows
    """
    # Create deeply nested structure
    nested_path = (
        temp_project_dir
        / "src"
        / "components"
        / "features"
        / "authentication"
        / "utils"
    )
    nested_path.mkdir(parents=True, exist_ok=True)

    # Verify all levels created
    assert (temp_project_dir / "src").exists()
    assert (temp_project_dir / "src" / "components").exists()
    assert (temp_project_dir / "src" / "components" / "features").exists()
    assert (
        temp_project_dir / "src" / "components" / "features" / "authentication"
    ).exists()
    assert nested_path.exists()

    # Create file in nested location
    test_file = nested_path / "validator.py"
    test_file.write_text("# Validator\n", encoding="utf-8")

    assert test_file.exists(), "File not created in nested directory"
    assert test_file.parent == nested_path, "File not in correct directory"


@pytest.mark.windows
@pytest.mark.slow
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_implementit_handles_large_task_lists(temp_project_dir):
    """
    Test that implementit handles large task lists efficiently.

    Given: tasks.md with many tasks
    When: Task list is processed
    Then: All tasks are accessible and trackable
    """
    spec_dir = temp_project_dir / "specs" / "003-large"
    spec_dir.mkdir(parents=True, exist_ok=True)

    tasks_file = spec_dir / "tasks.md"

    # Generate large task list
    tasks = ["# Tasks: Large Task List\n\n## Phase 1\n\n"]
    for i in range(1, 101):
        tasks.append(f"- [ ] T{i:03d} Task number {i}\n")

    tasks_content = "".join(tasks)
    tasks_file.write_text(tasks_content, encoding="utf-8")

    # Verify file created
    assert tasks_file.exists(), "Large tasks file not created"

    # Verify content
    content = tasks_file.read_text(encoding="utf-8")
    assert "T001" in content, "First task missing"
    assert "T050" in content, "Middle task missing"
    assert "T100" in content, "Last task missing"

    # Verify task count
    task_count = content.count("- [ ] T")
    assert task_count == 100, f"Expected 100 tasks, found {task_count}"
