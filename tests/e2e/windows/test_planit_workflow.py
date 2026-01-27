"""End-to-end tests for 'doit planit' command on Windows."""
import sys
from pathlib import Path

import pytest


@pytest.mark.windows
@pytest.mark.e2e
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_planit_creates_plan_file(temp_project_dir):
    """
    Test that plan.md is created correctly on Windows.

    Given: A feature spec exists
    When: plan.md is created
    Then: File is accessible on Windows filesystem
    """
    spec_dir = temp_project_dir / "specs" / "001-test-feature"
    spec_dir.mkdir(parents=True, exist_ok=True)

    plan_file = spec_dir / "plan.md"
    plan_content = """# Implementation Plan: Test Feature

**Branch**: 001-test-feature

## Summary
Test implementation plan on Windows.

## Technical Context
**Language/Version**: Python 3.11+
**Primary Dependencies**: pytest
"""

    plan_file.write_text(plan_content, encoding="utf-8")

    # Verify file created and readable
    assert plan_file.exists(), "plan.md not created"
    content = plan_file.read_text(encoding="utf-8")
    assert "Implementation Plan" in content
    assert "Python 3.11+" in content


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_plan_handles_nested_windows_directories(temp_project_dir):
    """
    Test plan file creation in nested Windows directory structure.

    Given: Deeply nested Windows directory path
    When: Plan file is created
    Then: All parent directories are created correctly
    """
    # Create nested structure
    nested_path = temp_project_dir / "specs" / "002-nested" / "plans" / "v1"
    nested_path.mkdir(parents=True, exist_ok=True)

    plan_file = nested_path / "plan.md"
    plan_file.write_text("# Nested Plan", encoding="utf-8")

    # Verify accessibility
    assert plan_file.exists(), "Nested plan file not created"
    assert nested_path.is_dir(), "Nested directory not recognized"

    # Verify all parent directories exist
    assert (temp_project_dir / "specs").exists()
    assert (temp_project_dir / "specs" / "002-nested").exists()
    assert (temp_project_dir / "specs" / "002-nested" / "plans").exists()


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_plan_preserves_line_endings(temp_project_dir):
    """
    Test that plan.md preserves line endings correctly on Windows.

    Given: Plan file with specific line endings
    When: File is written and read
    Then: Line endings are preserved
    """
    from tests.utils.windows.line_ending_utils import detect_line_ending

    spec_dir = temp_project_dir / "specs" / "003-line-test"
    spec_dir.mkdir(parents=True, exist_ok=True)

    plan_file = spec_dir / "plan.md"

    # Write with CRLF
    content = "# Plan\r\n\r\n## Section\r\nContent here.\r\n"
    plan_file.write_bytes(content.encode("utf-8"))

    # Read and detect
    read_content = plan_file.read_text(encoding="utf-8")
    detected = detect_line_ending(read_content)

    assert detected in ["CRLF", "LF"], f"Unexpected line ending: {detected}"
    assert "# Plan" in read_content


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_plan_with_mermaid_diagrams(temp_project_dir):
    """
    Test that Mermaid diagrams in plan files are preserved on Windows.

    Given: Plan file with Mermaid syntax
    When: File is created and read
    Then: Mermaid syntax is preserved correctly
    """
    spec_dir = temp_project_dir / "specs" / "004-mermaid"
    spec_dir.mkdir(parents=True, exist_ok=True)

    plan_file = spec_dir / "plan.md"

    content = """# Implementation Plan

## Architecture

```mermaid
flowchart TD
    A[Start] --> B[Process]
    B --> C[End]
```

## Components
Test content
"""

    plan_file.write_text(content, encoding="utf-8")

    # Read and verify
    read_content = plan_file.read_text(encoding="utf-8")
    assert "```mermaid" in read_content
    assert "flowchart TD" in read_content
    assert "A[Start]" in read_content


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_plan_file_structure_paths(temp_project_dir):
    """
    Test that plan files handle Windows path separators in structure definitions.

    Given: Plan with project structure using paths
    When: Plan is created
    Then: Path separators are handled correctly
    """
    spec_dir = temp_project_dir / "specs" / "005-structure"
    spec_dir.mkdir(parents=True, exist_ok=True)

    plan_file = spec_dir / "plan.md"

    content = """# Implementation Plan

## Project Structure

```
tests/
├── e2e/
│   └── windows/
│       ├── test_init.py
│       └── test_specit.py
└── utils/
    └── windows/
        └── helpers.py
```
"""

    plan_file.write_text(content, encoding="utf-8")

    # Read and verify
    read_content = plan_file.read_text(encoding="utf-8")
    assert "tests/" in read_content
    assert "windows/" in read_content
    assert "test_init.py" in read_content
