"""E2E tests for case-sensitivity on macOS filesystems."""

import pytest
from pathlib import Path


@pytest.mark.macos
@pytest.mark.e2e
@pytest.mark.filesystem
@pytest.mark.ci
def test_filesystem_type_detection(case_sensitive_volume):
    """Test detection of filesystem type."""
    assert "filesystem_type" in case_sensitive_volume
    fs_type = case_sensitive_volume["filesystem_type"]
    assert fs_type in ("apfs", "hfs", "exfat", "unknown"), f"Unexpected filesystem: {fs_type}"


@pytest.mark.macos
@pytest.mark.e2e
@pytest.mark.filesystem
def test_case_insensitive_apfs_behavior(tmp_path, case_sensitive_volume):
    """Test behavior on case-insensitive APFS (default macOS)."""
    if case_sensitive_volume["is_case_sensitive"]:
        pytest.skip("Test requires case-insensitive filesystem")

    # Create lowercase file
    lower_file = tmp_path / "testfile.txt"
    lower_file.write_text("lowercase\n")

    # Try to access with uppercase
    upper_file = tmp_path / "TESTFILE.txt"

    # On case-insensitive, both should refer to same file
    assert upper_file.exists(), "Uppercase path doesn't resolve on case-insensitive FS"
    assert lower_file.read_text() == upper_file.read_text()


@pytest.mark.macos
@pytest.mark.e2e
@pytest.mark.filesystem
@pytest.mark.case_sensitive
def test_case_sensitive_apfs_behavior(tmp_path, case_sensitive_volume):
    """Test behavior on case-sensitive APFS."""
    if not case_sensitive_volume["is_case_sensitive"]:
        pytest.skip("Test requires case-sensitive filesystem")

    # Create lowercase file
    lower_file = tmp_path / "testfile.txt"
    lower_file.write_text("lowercase\n")

    # Create uppercase file (should be separate)
    upper_file = tmp_path / "TESTFILE.txt"
    upper_file.write_text("uppercase\n")

    # Both should exist as separate files
    assert lower_file.exists()
    assert upper_file.exists()
    assert lower_file.read_text() != upper_file.read_text()


@pytest.mark.macos
@pytest.mark.e2e
@pytest.mark.filesystem
@pytest.mark.apfs
def test_apfs_features_detection(case_sensitive_volume):
    """Test APFS feature detection."""
    if case_sensitive_volume["filesystem_type"] != "apfs":
        pytest.skip("Test requires APFS")

    apfs_features = case_sensitive_volume.get("apfs_features", {})
    assert apfs_features.get("is_apfs"), "Should be detected as APFS"
    assert apfs_features.get("supports_cloning"), "APFS should support cloning"
    assert apfs_features.get("supports_snapshots"), "APFS should support snapshots"


@pytest.mark.macos
@pytest.mark.e2e
@pytest.mark.filesystem
def test_volume_property_queries(case_sensitive_volume, macos_test_env):
    """Test querying volume properties."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    from tests.utils.macos.filesystem_utils import FilesystemValidator

    validator = FilesystemValidator()
    volume_info = validator.get_volume_info()

    assert "path" in volume_info
    assert "filesystem" in volume_info
    assert "case_sensitive" in volume_info
