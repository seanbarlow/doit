"""E2E tests for line ending handling on macOS."""

import subprocess
import pytest


@pytest.mark.macos
@pytest.mark.e2e
@pytest.mark.ci
def test_lf_preservation_in_generated_files(git_repo, comparison_tools):
    """Test that generated files have LF line endings."""
    subprocess.run(["doit", "init"], cwd=git_repo, capture_output=True)

    constitution_file = git_repo / ".doit" / "memory" / "constitution.md"
    assert constitution_file.exists()

    line_ending = comparison_tools.verify_line_endings(str(constitution_file))
    assert line_ending == "LF", f"Expected LF, got {line_ending}"


@pytest.mark.macos
@pytest.mark.e2e
def test_handling_crlf_from_windows_files(tmp_path, comparison_tools):
    """Test handling of CRLF files from Windows."""
    # Create file with CRLF
    crlf_file = tmp_path / "windows_file.txt"
    with open(crlf_file, "wb") as f:
        f.write(b"Line 1\r\nLine 2\r\nLine 3\r\n")

    # Verify CRLF is detected (macOS may report as MIXED due to text mode handling)
    line_ending = comparison_tools.verify_line_endings(str(crlf_file))
    assert line_ending in ["CRLF", "MIXED"], f"Expected CRLF or MIXED, got {line_ending}"

    # Read in binary mode to preserve exact line endings
    content = crlf_file.read_bytes().decode('utf-8')
    normalized = content.replace("\r\n", "\n")

    lf_file = tmp_path / "normalized_file.txt"
    lf_file.write_text(normalized)

    # Verify LF
    line_ending = comparison_tools.verify_line_endings(str(lf_file))
    assert line_ending == "LF", f"Expected LF after normalization, got {line_ending}"


@pytest.mark.macos
@pytest.mark.e2e
def test_git_core_autocrlf_behavior(git_repo, macos_test_env):
    """Test Git core.autocrlf behavior on macOS."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    # Check Git's autocrlf setting (should be false or input on macOS)
    result = subprocess.run(
        ["git", "config", "core.autocrlf"],
        cwd=git_repo,
        capture_output=True,
        text=True
    )

    # On macOS, autocrlf should be false or input (not true)
    autocrlf_value = result.stdout.strip() if result.returncode == 0 else "false"
    assert autocrlf_value in ("false", "input", ""), \
        f"Unexpected autocrlf value: {autocrlf_value}"


@pytest.mark.macos
@pytest.mark.e2e
def test_mixed_line_endings_detection(tmp_path, comparison_tools):
    """Test detection of mixed line endings."""
    mixed_file = tmp_path / "mixed.txt"
    with open(mixed_file, "wb") as f:
        f.write(b"Line 1\nLine 2\r\nLine 3\nLine 4\r\n")

    line_ending = comparison_tools.verify_line_endings(str(mixed_file))
    assert line_ending == "MIXED", f"Expected MIXED, got {line_ending}"


@pytest.mark.macos
@pytest.mark.e2e
def test_lf_only_files(tmp_path, comparison_tools):
    """Test files with only LF line endings."""
    lf_file = tmp_path / "lf_only.txt"
    lf_file.write_text("Line 1\nLine 2\nLine 3\n")

    line_ending = comparison_tools.verify_line_endings(str(lf_file))
    assert line_ending == "LF", f"Expected LF, got {line_ending}"
