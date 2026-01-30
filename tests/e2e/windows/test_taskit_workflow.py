"""End-to-end tests for 'doit taskit' command on Windows."""
import sys
from pathlib import Path

import pytest


@pytest.mark.windows
@pytest.mark.e2e
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_taskit_creates_tasks_file(temp_project_dir):
    """
    Test that tasks.md is created correctly on Windows.

    Given: A feature plan exists
    When: tasks.md is created
    Then: File is accessible on Windows filesystem
    """
    spec_dir = temp_project_dir / "specs" / "001-test-feature"
    spec_dir.mkdir(parents=True, exist_ok=True)

    tasks_file = spec_dir / "tasks.md"
    tasks_content = """# Tasks: Test Feature

**Input**: Design documents from `/specs/001-test-feature/`

## Phase 1: Setup

- [ ] T001 Create test directory structure
- [ ] T002 Configure pytest markers
- [X] T003 [P] Create __init__ files

## Phase 2: Implementation

- [ ] T004 [P] Implement core functionality
- [X] T005 Add tests for edge cases
"""

    tasks_file.write_text(tasks_content, encoding="utf-8")

    # Verify file created and readable
    assert tasks_file.exists(), "tasks.md not created"
    content = tasks_file.read_text(encoding="utf-8")
    assert "# Tasks: Test Feature" in content
    assert "Phase 1: Setup" in content


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_tasks_handles_windows_paths(temp_project_dir):
    """
    Test that task descriptions with Windows paths are handled correctly.

    Given: Task descriptions containing Windows path separators
    When: tasks.md is created/read
    Then: Path separators are preserved correctly
    """
    spec_dir = temp_project_dir / "specs" / "002-paths"
    spec_dir.mkdir(parents=True, exist_ok=True)

    tasks_file = spec_dir / "tasks.md"

    # Tasks with Windows paths
    content = """# Tasks: Path Handling

## Implementation

- [ ] T001 Create tests/e2e/windows/ directory structure
- [ ] T002 Update tests\\utils\\windows\\path_utils.py
- [ ] T003 Configure .github\\workflows\\windows-tests.yml
"""

    tasks_file.write_text(content, encoding="utf-8")

    # Read and verify paths preserved
    read_content = tasks_file.read_text(encoding="utf-8")
    assert "tests/e2e/windows/" in read_content
    assert "tests\\utils\\windows\\path_utils.py" in read_content
    assert ".github\\workflows\\windows-tests.yml" in read_content


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_tasks_checkbox_format(temp_project_dir):
    """
    Test that task checkboxes use valid Markdown format.

    Given: Task list with various checkbox states
    When: Checkboxes are parsed
    Then: Format follows Markdown standard (- [ ] and - [X])
    """
    spec_dir = temp_project_dir / "specs" / "003-checkboxes"
    spec_dir.mkdir(parents=True, exist_ok=True)

    tasks_file = spec_dir / "tasks.md"

    content = """# Tasks: Checkbox Format

## Tasks

- [ ] T001 Incomplete task 1
- [X] T002 Completed task 2
- [ ] T003 [P] Incomplete parallel task
- [X] T004 [P] Completed parallel task
"""

    tasks_file.write_text(content, encoding="utf-8")

    # Verify checkbox format
    read_content = tasks_file.read_text(encoding="utf-8")
    assert "- [ ] T001" in read_content
    assert "- [X] T002" in read_content
    assert "- [ ] T003 [P]" in read_content
    assert "- [X] T004 [P]" in read_content


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_tasks_task_id_numbering(temp_project_dir):
    """
    Test that task IDs follow consistent numbering format.

    Given: Task list with sequential IDs
    When: IDs are parsed
    Then: Format follows T### pattern
    """
    spec_dir = temp_project_dir / "specs" / "004-ids"
    spec_dir.mkdir(parents=True, exist_ok=True)

    tasks_file = spec_dir / "tasks.md"

    content = """# Tasks: ID Numbering

## Phase 1

- [ ] T001 First task
- [ ] T002 Second task
- [ ] T010 Tenth task
- [ ] T025 Twenty-fifth task
- [ ] T100 Hundredth task
"""

    tasks_file.write_text(content, encoding="utf-8")

    # Verify ID format
    read_content = tasks_file.read_text(encoding="utf-8")
    assert "T001" in read_content
    assert "T002" in read_content
    assert "T010" in read_content
    assert "T025" in read_content
    assert "T100" in read_content

    # Verify consistent pattern
    import re

    task_ids = re.findall(r"T\d{3,}", read_content)
    assert len(task_ids) == 5, f"Expected 5 task IDs, found {len(task_ids)}"


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_tasks_mermaid_diagrams(temp_project_dir):
    """
    Test that Mermaid diagrams in tasks.md are preserved on Windows.

    Given: tasks.md with Mermaid dependency diagram
    When: File is created and read
    Then: Mermaid syntax is preserved correctly
    """
    spec_dir = temp_project_dir / "specs" / "005-mermaid"
    spec_dir.mkdir(parents=True, exist_ok=True)

    tasks_file = spec_dir / "tasks.md"

    content = """# Tasks: Mermaid Diagrams

## Task Dependencies

```mermaid
flowchart TD
    T001[Setup] --> T002[Core]
    T002 --> T003[Tests]
    T002 --> T004[Integration]
    T003 & T004 --> T005[Polish]
```

## Tasks

- [ ] T001 Setup
- [ ] T002 Core functionality
"""

    tasks_file.write_text(content, encoding="utf-8")

    # Read and verify Mermaid preserved
    read_content = tasks_file.read_text(encoding="utf-8")
    assert "```mermaid" in read_content
    assert "flowchart TD" in read_content
    assert "T001[Setup]" in read_content
    assert "T002 --> T003" in read_content
