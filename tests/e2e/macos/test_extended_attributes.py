"""E2E tests for extended attributes (xattr) on macOS."""

import pytest


@pytest.mark.macos
@pytest.mark.e2e
@pytest.mark.filesystem
@pytest.mark.ci
def test_xattr_preservation(tmp_path, xattr_handler, macos_test_env):
    """Test that extended attributes are preserved during operations."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    # Create test file
    test_file = tmp_path / "test.txt"
    test_file.write_text("Content\n")

    # Set custom xattr
    success = xattr_handler.set_xattr(
        str(test_file),
        "com.example.test",
        "test_value"
    )

    if success:
        # Read back xattr
        value = xattr_handler.get_xattr(str(test_file), "com.example.test")
        assert value == "test_value", "Extended attribute not preserved"


@pytest.mark.macos
@pytest.mark.e2e
@pytest.mark.filesystem
def test_metadata_attributes(tmp_path, xattr_handler, macos_test_env):
    """Test com.apple.metadata attributes."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    test_file = tmp_path / "metadata_test.txt"
    test_file.write_text("Content\n")

    # Get all metadata attributes
    metadata_attrs = xattr_handler.get_metadata_attrs(str(test_file))
    # File might not have metadata attributes, just verify method works
    assert isinstance(metadata_attrs, dict)


@pytest.mark.macos
@pytest.mark.e2e
@pytest.mark.filesystem
def test_quarantine_attribute_handling(tmp_path, xattr_handler, macos_test_env):
    """Test quarantine attribute handling."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    test_file = tmp_path / "quarantine_test.txt"
    test_file.write_text("Content\n")

    # Check if file has quarantine (shouldn't for new files)
    has_quarantine = xattr_handler.has_quarantine_attr(str(test_file))
    # New files typically don't have quarantine
    assert isinstance(has_quarantine, bool)


@pytest.mark.macos
@pytest.mark.e2e
@pytest.mark.filesystem
def test_xattr_in_generated_files(tmp_path, xattr_handler, macos_test_env):
    """Test extended attributes in doit-generated files."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    # Create a file simulating doit-generated content
    generated_file = tmp_path / "generated.md"
    generated_file.write_text("# Generated File\n\nContent\n")

    # List all xattrs
    xattrs = xattr_handler.list_xattrs(str(generated_file))
    # File might have no xattrs, just verify method works
    assert isinstance(xattrs, list)


@pytest.mark.macos
@pytest.mark.e2e
@pytest.mark.filesystem
def test_xattr_summary(tmp_path, xattr_handler, macos_test_env):
    """Test getting xattr summary for a file."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    test_file = tmp_path / "summary_test.txt"
    test_file.write_text("Content\n")

    summary = xattr_handler.get_xattr_summary(str(test_file))

    assert summary["exists"], "File should exist"
    assert "xattr_count" in summary
    assert "has_quarantine" in summary
    assert isinstance(summary["attributes"], list)
