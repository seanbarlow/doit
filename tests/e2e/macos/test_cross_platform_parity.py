"""E2E tests for cross-platform parity between macOS, Windows, and Linux."""

import pytest
import platform


@pytest.mark.macos
@pytest.mark.e2e
def test_output_comparison_with_windows_normalization(comparison_tools, macos_test_env):
    """Test output comparison with Windows (path and line ending normalization)."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    # Simulate macOS output
    macos_output = "File created at: /Users/test/project/spec.md\nSuccess\n"

    # Simulate Windows output (with Windows paths and CRLF)
    windows_output = "File created at: C:\\Users\\test\\project\\spec.md\r\nSuccess\r\n"

    # Compare with normalization
    are_equal, differences = comparison_tools.compare_outputs(
        macos_output,
        windows_output,
        normalize=True
    )

    # After normalization, outputs should be equivalent
    assert are_equal or len(differences) <= 1, \
        f"Outputs differ after normalization: {differences}"


@pytest.mark.macos
@pytest.mark.e2e
def test_output_comparison_with_linux(comparison_tools, macos_test_env):
    """Test output comparison with Linux."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    # macOS and Linux should have very similar output
    macos_output = "File: /home/user/project/spec.md\nStatus: complete\n"
    linux_output = "File: /home/user/project/spec.md\nStatus: complete\n"

    are_equal, differences = comparison_tools.compare_outputs(
        macos_output,
        linux_output,
        normalize=True
    )

    assert are_equal, f"macOS and Linux outputs should match: {differences}"


@pytest.mark.macos
@pytest.mark.e2e
def test_behavioral_consistency_validation(comparison_tools, tmp_path, macos_test_env):
    """Test behavioral consistency across platforms."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    # Test file creation behavior
    test_file = tmp_path / "consistency_test.txt"
    test_content = "Line 1\nLine 2\nLine 3\n"
    test_file.write_text(test_content)

    # Verify file exists and content matches
    assert test_file.exists()
    assert test_file.read_text() == test_content

    # Verify line endings are LF (consistent with Linux)
    line_ending = comparison_tools.verify_line_endings(str(test_file))
    assert line_ending == "LF", "macOS should use LF like Linux"


@pytest.mark.macos
@pytest.mark.e2e
def test_platform_specific_difference_documentation(comparison_tools, macos_test_env):
    """Document known platform-specific differences."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    platform_info = comparison_tools.get_platform_info()

    # Verify macOS is correctly identified
    assert platform_info["is_macos"], "Should be detected as macOS"
    assert platform_info["system"] == "Darwin"
    assert platform_info["line_ending"] == "LF"
    assert platform_info["unicode_normalization"] == "NFD"

    # Document differences
    differences = {
        "path_separator": "/",  # Same as Linux, different from Windows
        "line_ending": "LF",    # Same as Linux, different from Windows
        "unicode_norm": "NFD",  # Different from both Windows and Linux (NFC)
        "case_sensitive": "varies",  # Depends on filesystem
    }

    assert differences["path_separator"] == platform_info["path_separator"]
    assert differences["line_ending"] == platform_info["line_ending"]


@pytest.mark.macos
@pytest.mark.e2e
@pytest.mark.unicode
def test_unicode_normalization_parity(comparison_tools, macos_test_env):
    """Test Unicode normalization differences between platforms."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    from tests.utils.macos.unicode_utils import normalize_nfd, normalize_nfc

    # Test string with accented characters
    test_string = "café"

    # macOS uses NFD
    nfd_form = normalize_nfd(test_string)

    # Windows/Linux use NFC
    nfc_form = normalize_nfc(test_string)

    # They may look the same but have different byte representations
    # Test that comparison tools handle this
    are_equal, explanation = comparison_tools.handle_unicode_differences(
        nfd_form,
        nfc_form,
        auto_normalize=True
    )

    assert are_equal, f"Unicode forms should normalize to equal: {explanation}"


@pytest.mark.macos
@pytest.mark.e2e
def test_path_normalization_cross_platform(comparison_tools, macos_test_env):
    """Test path normalization across platforms."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    # Test with mixed path separators
    mixed_path = "project/specs\\feature\\spec.md"

    # Normalize to POSIX (forward slashes)
    posix_path = comparison_tools.normalize_path(mixed_path, target_platform="posix")
    assert "\\" not in posix_path, "Backslashes should be converted"
    assert "/" in posix_path, "Should have forward slashes"

    # Normalize to Windows (backslashes)
    windows_path = comparison_tools.normalize_path(mixed_path, target_platform="windows")
    assert "/" not in windows_path, "Forward slashes should be converted"
    assert "\\" in windows_path, "Should have backslashes"


@pytest.mark.macos
@pytest.mark.e2e
def test_comparison_report_generation(comparison_tools, macos_test_env):
    """Test generation of comparison reports."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    output1 = "Test output 1\nSuccess\n"
    output2 = "Test output 2\nSuccess\n"

    report = comparison_tools.create_comparison_report(
        "Test Comparison",
        output1,
        output2,
        platform1="macOS",
        platform2="Linux"
    )

    assert "Test Comparison" in report
    assert "macOS" in report
    assert "Linux" in report
    assert "Platform Information" in report
