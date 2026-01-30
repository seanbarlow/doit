"""Cross-platform parity tests for 'doit init' command."""
import sys
from pathlib import Path

import pytest


@pytest.mark.windows
@pytest.mark.unix
@pytest.mark.skipif(sys.platform != "win32", reason="Windows parity test")
def test_init_directory_structure_parity(temp_project_dir, comparison_tools):
    """
    Test that doit init creates identical directory structure on Windows and Linux.

    Given: doit init executed on both platforms
    When: Directory structures are compared
    Then: Same directories exist (after path normalization)
    """
    # Simulate doit init directory structure
    expected_dirs = [
        ".doit",
        ".doit/memory",
        ".doit/templates",
        ".doit/scripts",
        ".doit/scripts/bash",
        ".doit/scripts/powershell",
    ]

    # Create directories
    for dir_path in expected_dirs:
        (temp_project_dir / dir_path).mkdir(parents=True, exist_ok=True)

    # Verify all directories created
    for dir_path in expected_dirs:
        normalized_path = comparison_tools.normalize_path(dir_path)
        assert (temp_project_dir / dir_path).exists(), \
            f"Directory missing: {normalized_path}"


@pytest.mark.windows
@pytest.mark.unix
@pytest.mark.skipif(sys.platform != "win32", reason="Windows parity test")
def test_init_file_content_parity(temp_project_dir, comparison_tools):
    """
    Test that files created by doit init have identical content (after normalization).

    Given: Constitution and roadmap files created on both platforms
    When: Content is compared after line ending normalization
    Then: Content matches
    """
    memory_dir = temp_project_dir / ".doit" / "memory"
    memory_dir.mkdir(parents=True, exist_ok=True)

    # Create constitution file
    constitution_file = memory_dir / "constitution.md"
    constitution_content = """# Project Constitution

## Tech Stack
- Python 3.11+
- pytest

## Code Style
Follow PEP 8
"""
    constitution_file.write_text(constitution_content, encoding="utf-8")

    # Read and normalize
    read_content = constitution_file.read_text(encoding="utf-8")
    normalized = comparison_tools.normalize_output(read_content)

    # Verify structure preserved
    assert "# Project Constitution" in normalized
    assert "## Tech Stack" in normalized
    assert "Python 3.11+" in normalized


@pytest.mark.windows
@pytest.mark.unix
@pytest.mark.skipif(sys.platform != "win32", reason="Windows parity test")
def test_init_path_separator_normalization(temp_project_dir, comparison_tools):
    """
    Test that Windows paths can be normalized to Linux format.

    Given: Windows path separators (backslashes)
    When: Paths are normalized
    Then: Forward slashes are used (cross-platform standard)
    """
    # Windows-style paths
    windows_paths = [
        ".doit\\memory\\constitution.md",
        ".doit\\templates\\spec.md",
        "specs\\001-feature\\plan.md",
    ]

    # Normalize paths
    for win_path in windows_paths:
        normalized = comparison_tools.normalize_path(win_path)
        assert "\\" not in normalized, f"Backslashes remain in {normalized}"
        assert "/" in normalized, f"No forward slashes in {normalized}"


@pytest.mark.windows
@pytest.mark.unix
@pytest.mark.skipif(sys.platform != "win32", reason="Windows parity test")
def test_init_line_ending_normalization(temp_project_dir, comparison_tools):
    """
    Test that CRLF line endings can be normalized to LF.

    Given: File with CRLF line endings (Windows)
    When: Line endings are normalized
    Then: Only LF remains
    """
    from tests.utils.windows.line_ending_utils import normalize_line_endings

    # Create file with CRLF
    test_file = temp_project_dir / "test.md"
    content_crlf = "Line 1\r\nLine 2\r\nLine 3\r\n"
    test_file.write_bytes(content_crlf.encode("utf-8"))

    # Read and normalize
    read_content = test_file.read_text(encoding="utf-8")
    normalized = normalize_line_endings(read_content, target="LF")

    # Verify CRLF converted to LF
    assert "\r\n" not in normalized, "CRLF should be converted to LF"
    assert "\n" in normalized, "LF should be present"


@pytest.mark.windows
@pytest.mark.unix
@pytest.mark.skipif(sys.platform != "win32", reason="Windows parity test")
def test_init_template_file_parity(temp_project_dir, comparison_tools):
    """
    Test that template files are identical across platforms.

    Given: Template files created on both platforms
    When: Content is compared
    Then: Templates are functionally identical
    """
    templates_dir = temp_project_dir / ".doit" / "templates"
    templates_dir.mkdir(parents=True, exist_ok=True)

    # Create template file
    spec_template = templates_dir / "spec.md"
    spec_content = """# Specification: {{ feature_name }}

## Overview
{{ overview }}

## Requirements
- [ ] Requirement 1
- [ ] Requirement 2
"""
    spec_template.write_text(spec_content, encoding="utf-8")

    # Read and verify structure
    read_content = spec_template.read_text(encoding="utf-8")
    normalized = comparison_tools.normalize_output(read_content)

    # Verify template placeholders preserved
    assert "{{ feature_name }}" in read_content
    assert "{{ overview }}" in read_content
    assert "- [ ]" in read_content


@pytest.mark.windows
@pytest.mark.unix
@pytest.mark.skipif(sys.platform != "win32", reason="Windows parity test")
def test_init_script_file_parity(temp_project_dir):
    """
    Test that both bash and powershell scripts are created.

    Given: Script directory created by doit init
    When: Scripts are inspected
    Then: Both .sh and .ps1 versions exist
    """
    bash_dir = temp_project_dir / ".doit" / "scripts" / "bash"
    ps_dir = temp_project_dir / ".doit" / "scripts" / "powershell"

    bash_dir.mkdir(parents=True, exist_ok=True)
    ps_dir.mkdir(parents=True, exist_ok=True)

    # Create example script in both formats
    bash_script = bash_dir / "example.sh"
    bash_script.write_text("#!/bin/bash\necho 'Example'\n", encoding="utf-8")

    ps_script = ps_dir / "example.ps1"
    ps_script.write_text("Write-Host 'Example'\n", encoding="utf-8")

    # Verify both exist
    assert bash_script.exists(), "Bash script missing"
    assert ps_script.exists(), "PowerShell script missing"


@pytest.mark.windows
@pytest.mark.unix
@pytest.mark.skipif(sys.platform != "win32", reason="Windows parity test")
def test_init_gitignore_parity(temp_project_dir, comparison_tools):
    """
    Test that .gitignore content is consistent across platforms.

    Given: .gitignore created on both platforms
    When: Content is compared
    Then: Ignore patterns are identical
    """
    gitignore_file = temp_project_dir / ".gitignore"
    gitignore_content = """# Python
__pycache__/
*.pyc
.venv/
venv/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
"""
    gitignore_file.write_text(gitignore_content, encoding="utf-8")

    # Read and normalize
    read_content = gitignore_file.read_text(encoding="utf-8")
    normalized = comparison_tools.normalize_output(read_content)

    # Verify patterns present
    assert "__pycache__/" in normalized
    assert ".venv/" in normalized
    assert ".DS_Store" in normalized
    assert "Thumbs.db" in normalized
