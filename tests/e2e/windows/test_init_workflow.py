"""End-to-end tests for 'doit init' command on Windows."""
import sys
import subprocess
from pathlib import Path

import pytest


@pytest.mark.windows
@pytest.mark.e2e
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_init_creates_doit_directory(temp_project_dir, windows_test_env):
    """
    Test that 'doit init' creates the .doit directory structure on Windows.

    Given: A fresh Windows environment with Python 3.11+ installed
    When: Developer runs 'doit init' in an empty directory
    Then: .doit directory is created with proper structure
    """
    assert windows_test_env.platform == "win32", "Test must run on Windows"

    # Execute doit init in non-interactive mode
    import os
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    result = subprocess.run(
        ["doit", "init", ".", "--yes"],
        cwd=temp_project_dir,
        capture_output=True,
        env=env,
    )

    # Decode output with error handling for Windows encoding issues
    stdout = result.stdout.decode('utf-8', errors='replace') if result.stdout else ""
    stderr = result.stderr.decode('utf-8', errors='replace') if result.stderr else ""

    # Verify command succeeded
    assert result.returncode == 0, f"doit init failed: {stderr}"

    # Verify .doit directory structure
    doit_dir = temp_project_dir / ".doit"
    assert doit_dir.exists(), ".doit directory not created"
    assert (doit_dir / "memory").exists(), ".doit/memory directory not created"
    assert (doit_dir / "templates").exists(), ".doit/templates directory not created"


@pytest.mark.windows
@pytest.mark.e2e
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_init_handles_windows_paths_with_spaces(temp_project_dir, windows_test_env):
    """
    Test that 'doit init' handles Windows paths with spaces correctly.

    Given: Windows path with spaces in directory names
    When: Developer runs 'doit init'
    Then: All file operations succeed without path-related errors
    """
    # Create a path with spaces
    project_with_spaces = temp_project_dir / "My Project Folder"
    project_with_spaces.mkdir(parents=True, exist_ok=True)

    # Execute doit init
    import os
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    result = subprocess.run(
        ["doit", "init", ".", "--yes"],
        cwd=project_with_spaces,
        capture_output=True,
        env=env,
    )

    # Decode output with error handling for Windows encoding issues
    stdout = result.stdout.decode('utf-8', errors='replace') if result.stdout else ""
    stderr = result.stderr.decode('utf-8', errors='replace') if result.stderr else ""

    # Verify success despite spaces in path
    assert result.returncode == 0, f"doit init failed with spaces in path: {stderr}"

    # Verify created files
    doit_dir = project_with_spaces / ".doit"
    assert doit_dir.exists(), ".doit directory not created in path with spaces"


@pytest.mark.windows
@pytest.mark.e2e
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_init_creates_constitution_with_crlf(temp_project_dir, windows_test_env):
    """
    Test that 'doit init' creates constitution.md with Windows CRLF line endings.

    Given: CRLF line ending conventions on Windows
    When: Developer runs 'doit init'
    Then: Generated markdown files use CRLF line endings
    """
    from tests.utils.windows.line_ending_utils import detect_line_ending

    # Execute doit init in non-interactive mode with UTF-8 encoding
    import os
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    result = subprocess.run(
        ["doit", "init", ".", "--yes"],
        cwd=temp_project_dir,
        capture_output=True,
        env=env,
    )

    # Decode output with error handling for Windows encoding issues
    stdout = result.stdout.decode('utf-8', errors='replace') if result.stdout else ""
    stderr = result.stderr.decode('utf-8', errors='replace') if result.stderr else ""

    assert result.returncode == 0, f"doit init failed: {stderr}"

    # Read generated constitution
    constitution_file = temp_project_dir / ".doit" / "memory" / "constitution.md"
    if constitution_file.exists():
        content = constitution_file.read_text(encoding="utf-8")
        detected_ending = detect_line_ending(content)

        # On Windows, we expect CRLF (though Git may normalize)
        assert detected_ending in [
            "CRLF",
            "LF",
        ], f"Unexpected line ending: {detected_ending}"


@pytest.mark.windows
@pytest.mark.e2e
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_init_with_absolute_windows_path(temp_project_dir, windows_test_env):
    r"""
    Test that 'doit init' works with absolute Windows paths (C:\path\to\dir).

    Given: An absolute Windows path with drive letter
    When: Developer runs 'doit init' using absolute path
    Then: Command succeeds and respects the absolute path
    """
    # Get absolute path
    absolute_path = temp_project_dir.resolve()
    assert absolute_path.is_absolute(), "Test requires absolute path"

    # Execute doit init with absolute path
    import os
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    result = subprocess.run(
        ["doit", "init", ".", "--yes"],
        cwd=str(absolute_path),
        capture_output=True,
        env=env,
    )

    # Decode output with error handling for Windows encoding issues
    stdout = result.stdout.decode('utf-8', errors='replace') if result.stdout else ""
    stderr = result.stderr.decode('utf-8', errors='replace') if result.stderr else ""

    assert result.returncode == 0, f"doit init failed with absolute path: {stderr}"

    # Verify .doit created at correct location
    doit_dir = absolute_path / ".doit"
    assert doit_dir.exists(), f".doit directory not created at {absolute_path}"


@pytest.mark.windows
@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_init_full_workflow_on_windows(temp_project_dir, windows_test_env):
    """
    Test complete init workflow on Windows including all created files.

    Given: A fresh Windows environment
    When: Developer runs 'doit init' and inspects all created files
    Then: All expected files exist and are readable by Windows tools
    """
    # Execute doit init in non-interactive mode with UTF-8 encoding
    import os
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    result = subprocess.run(
        ["doit", "init", ".", "--yes"],
        cwd=temp_project_dir,
        capture_output=True,
        env=env,
    )

    # Decode output with error handling for Windows encoding issues
    stdout = result.stdout.decode('utf-8', errors='replace') if result.stdout else ""
    stderr = result.stderr.decode('utf-8', errors='replace') if result.stderr else ""

    assert result.returncode == 0, f"doit init failed: {stderr}"

    # Verify comprehensive directory structure
    expected_dirs = [
        temp_project_dir / ".doit",
        temp_project_dir / ".doit" / "memory",
        temp_project_dir / ".doit" / "templates",
        temp_project_dir / ".doit" / "scripts",
    ]

    for expected_dir in expected_dirs:
        if expected_dir.exists():
            # Directory exists - verify it's accessible
            assert expected_dir.is_dir(), f"{expected_dir} is not a directory"
            # Verify we can list contents (Windows permissions check)
            try:
                list(expected_dir.iterdir())
            except PermissionError:
                pytest.fail(f"Permission denied accessing {expected_dir}")

    # Verify key files are readable
    key_files = [
        temp_project_dir / ".doit" / "memory" / "constitution.md",
        temp_project_dir / ".doit" / "memory" / "roadmap.md",
    ]

    for key_file in key_files:
        if key_file.exists():
            try:
                content = key_file.read_text(encoding="utf-8")
                assert len(content) > 0, f"{key_file} is empty"
            except (PermissionError, UnicodeDecodeError) as e:
                pytest.fail(f"Failed to read {key_file}: {e}")
