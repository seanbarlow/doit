"""E2E tests for BSD command compatibility on macOS."""

import pytest
import subprocess


@pytest.mark.macos
@pytest.mark.e2e
@pytest.mark.bsd
@pytest.mark.ci
def test_bsd_sed_requires_extension(tmp_path, bsd_command_wrapper, macos_test_env):
    """Test that BSD sed -i requires extension argument."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    test_file = tmp_path / "test.txt"
    test_file.write_text("old_value\n")

    # Test BSD sed in-place editing
    success, message = bsd_command_wrapper.sed_inplace(
        "old_value",
        "new_value",
        str(test_file)
    )

    assert success, f"BSD sed failed: {message}"
    assert "new_value" in test_file.read_text()


@pytest.mark.macos
@pytest.mark.e2e
@pytest.mark.bsd
def test_bsd_grep_differences(tmp_path, bsd_command_wrapper, macos_test_env):
    """Test BSD grep differences from GNU grep."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    test_file = tmp_path / "test.txt"
    test_file.write_text("Line 1\nLine 2\nTest line\nLine 4\n")

    # Test extended regex with grep
    success, lines = bsd_command_wrapper.grep_extended(
        "^Test",
        str(test_file)
    )

    assert success, f"BSD grep failed"
    assert len(lines) == 1
    assert "Test line" in lines[0]


@pytest.mark.macos
@pytest.mark.e2e
@pytest.mark.bsd
def test_bsd_awk_posix_mode(tmp_path, bsd_command_wrapper, macos_test_env):
    """Test BSD awk POSIX mode."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    test_file = tmp_path / "data.txt"
    test_file.write_text("field1 field2 field3\n")

    # Test awk field extraction
    success, output = bsd_command_wrapper.awk_posix(
        "{print $2}",
        str(test_file)
    )

    assert success, f"BSD awk failed"
    assert "field2" in output


@pytest.mark.macos
@pytest.mark.e2e
@pytest.mark.bsd
def test_bsd_find_syntax(tmp_path, bsd_command_wrapper, macos_test_env):
    """Test BSD find syntax variations."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    # Create test files
    (tmp_path / "file1.txt").touch()
    (tmp_path / "file2.md").touch()
    (tmp_path / "file3.txt").touch()

    # Test find with name pattern
    success, files = bsd_command_wrapper.find_bsd(
        str(tmp_path),
        name_pattern="*.txt"
    )

    assert success, "BSD find failed"
    assert len(files) >= 2  # Should find file1.txt and file3.txt


@pytest.mark.macos
@pytest.mark.e2e
@pytest.mark.bsd
def test_detect_homebrew_gnu_utilities(bsd_command_wrapper, macos_test_env):
    """Test detection of Homebrew GNU utilities."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    has_gnu = bsd_command_wrapper.has_gnu_utils()
    # Just verify the detection works (may or may not have GNU utils)
    assert isinstance(has_gnu, bool)

    if has_gnu:
        command_info = bsd_command_wrapper.get_command_info()
        assert "gsed" in command_info or "ggrep" in command_info


@pytest.mark.macos
@pytest.mark.e2e
@pytest.mark.bsd
def test_bsd_command_version_detection(bsd_command_wrapper, macos_test_env):
    """Test BSD command version detection."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    # Detect sed version
    sed_version = bsd_command_wrapper.detect_command_version("sed")
    assert sed_version in ("BSD", "GNU", "UNKNOWN")

    # On macOS, sed should be BSD
    assert sed_version == "BSD", "macOS should have BSD sed"
